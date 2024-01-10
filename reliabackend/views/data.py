import json
import time
import zlib

from collections import OrderedDict

from flask import Blueprint, jsonify, request, g, current_app, make_response
from reliabackend import redis_store
from reliabackend.auth import get_current_user

data_blueprint = Blueprint('data', __name__)

@data_blueprint.before_request
def check_authentication():
    """
    Here we should check the authentication of the user
    (typically with weblablib) and store the session
    identifier.
    """
    current_user_data = get_current_user()

    g.session_id = current_user_data['session_id']
    if g.session_id is None:
        return jsonify(success=False, message="Not authenticated")

@data_blueprint.route('/')
def index():
    return "Welcome to the Data API"

@data_blueprint.route('/tasks/<task_id>/devices')
def get_devices(task_id):
    devices_key = f'relia:data-uploader:sessions:{g.session_id}:tasks:{task_id}:devices'
    devices_set = redis_store.smembers(devices_key)
    current_app.logger.info(devices_set)
    device_names = [ device_name.decode() for device_name in (devices_set or ()) ]

    return _corsify_actual_response(jsonify({
        "devices": sorted(device_names),
        "success": True
    }))

@data_blueprint.route('/tasks/<task_id>/devices/<device_identifier>/blocks')
def get_device_blocks(task_id, device_identifier):
    blocks_key = f'relia:data-uploader:sessions:{g.session_id}:tasks:{task_id}:devices:{device_identifier}:blocks'
    blocks_set = redis_store.smembers(blocks_key)
    block_names = [ block_name.decode() for block_name in (blocks_set or ()) ]

    for block_identifier in block_names:
        block_alive_key = f'relia:data-uploader:sessions:{g.session_id}:tasks:{task_id}:devices:{device_identifier}:blocks:{block_identifier}:alive'
        if redis_store.get(block_alive_key) != b'1':
            block_names.remove(block_identifier)

    return _corsify_actual_response(jsonify({
        "blocks": sorted(block_names),
        "success": True
    }))

@data_blueprint.route('/tasks/<task_id>/devices/<device_identifier>/all-blocks')
def get_device_blocks_data(task_id, device_identifier):
    last_version = request.args.get('last-version') or 'none'
    current_version = last_version
    initial_time = time.time()
    max_seconds = 10

    while last_version == current_version and (time.time() - initial_time) < max_seconds:
        blocks_key = f'relia:data-uploader:sessions:{g.session_id}:tasks:{task_id}:devices:{device_identifier}:blocks'
        blocks_set = redis_store.smembers(blocks_key)
        block_names = [ block_name.decode() for block_name in (blocks_set or ()) ]
        block_data = {
            # block_identifier: data
        }

        for block_identifier in block_names:
            block_alive_key = f'relia:data-uploader:sessions:{g.session_id}:tasks:{task_id}:devices:{device_identifier}:blocks:{block_identifier}:alive'
            if redis_store.get(block_alive_key) != b'1':
                block_names.remove(block_identifier)
                continue

            gnuradio2web_block_key = f'relia:data-uploader:sessions:{g.session_id}:tasks:{task_id}:devices:{device_identifier}:blocks:{block_identifier}:from-gnuradio'

            empty = False
            while not empty:
                newest_data = redis_store.lpop(gnuradio2web_block_key)
                if newest_data is None:
                    empty = True
                else:
                    data = newest_data
            block_data[block_identifier] = data

        response_dict = OrderedDict()
        response_dict['success'] = True
        response_dict['blocks'] = []
        response_dict['blocksData'] = OrderedDict()
        for block in sorted(block_names):
            response_dict['blocks'].append(block)
            response_dict['blocksData'][block] = block_data[block]

        response_json = json.dumps(response_dict, indent=4)
        current_version = str(zlib.crc32(response_json.encode()))
        if current_version == last_version:
            time.sleep(0.1)

    response = make_response(response_json)
    response.headers['Content-Type'] = 'application/json'

    return _corsify_actual_response(response)


@data_blueprint.route('/tasks/<task_id>/devices/<device_identifier>/blocks/<block_identifier>', methods=['GET', 'POST'])
def manage_data(task_id, device_identifier, block_identifier):

    if request.method == 'GET':
        gnuradio2web_block_key = f'relia:data-uploader:sessions:{g.session_id}:tasks:{task_id}:devices:{device_identifier}:blocks:{block_identifier}:from-gnuradio'
        

        initial_time = time.time()
        data = None
        while True:

            empty = False
            while not empty:
                newest_data = redis_store.lpop(gnuradio2web_block_key)
                if newest_data is None:
                    empty = True
                else:
                    data = newest_data

            if data:
                # If there is data, we exit immediately
                break

            if time.time() - initial_time > 5:
                # If we have been waiting for more than 5 seconds
                # then exit (even without data)
                break

            time.sleep(0.05)        

        if data is None:
            return _corsify_actual_response(jsonify(success=True, data=None))

        decoded_data = json.loads(data)

        return _corsify_actual_response(jsonify(success=True, data=decoded_data))
    elif request.method == 'POST':

        block_alive_key = f'relia:data-uploader:sessions:{g.session_id}:tasks:{task_id}:devices:{device_identifier}:blocks:{block_identifier}:alive'
        if redis_store.get(block_alive_key) != b'1':
            return _corsify_actual_response(jsonify(success=False, message="Block does not exist"), 404)

        web2gnuradio_block_key = f'relia:data-uploader:sessions:{g.session_id}:tasks:{task_id}:devices:{device_identifier}:blocks:{block_identifier}:to-gnuradio'

        request_data = request.get_json(silent=True, force=True)

        pipeline = redis_store.pipeline()
        pipeline.rpush(web2gnuradio_block_key, json.dumps(request_data))
        pipeline.expire(web2gnuradio_block_key, 60)
        pipeline.execute()

        return _corsify_actual_response(jsonify(success=True))
    else:
        return "Method not allowed", 400

def _corsify_actual_response(response):
    response.headers['Access-Control-Allow-Origin'] = '*';
    response.headers['Access-Control-Allow-Credentials'] = 'true';
    response.headers['Access-Control-Allow-Methods'] = 'OPTIONS, GET, POST';
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Depth, User-Agent, X-File-Size, X-Requested-With, If-Modified-Since, X-File-Name, Cache-Control';
    return response
