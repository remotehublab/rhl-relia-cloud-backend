import json
import time

from flask import Blueprint, jsonify, render_template, g

from reliaweb import redis_store


main_blueprint = Blueprint('main', __name__)

@main_blueprint.route('/')
def index():
    return render_template("index.html")

api_blueprint = Blueprint('api', __name__)

@api_blueprint.before_request
def check_authentication():
    """
    Here we should check the authentication of the user
    (typically with weblablib) and store the session
    identifier.
    """
    # TODO: actually check authentication
    g.session_id = "my-session-id"

@api_blueprint.route('/')
def index():
    return "Welcome to the API"

@api_blueprint.route('/data/current/devices')
def get_devices():
    devices_key = f'relia:data-uploader:sessions:{g.session_id}:devices'
    devices_set = redis_store.smembers(devices_key)
    device_names = [ device_name.decode() for device_name in (devices_set or ()) ]

    return jsonify({
        "devices": device_names,
        "success": True
    })

@api_blueprint.route('/data/current/devices/<device_identifier>/blocks')
def get_device_blocks(device_identifier):
    blocks_key = f'relia:data-uploader:sessions:{g.session_id}:devices:{device_identifier}:blocks'
    blocks_set = redis_store.smembers(blocks_key)
    block_names = [ block_name.decode() for block_name in (blocks_set or ()) ]

    for block_identifier in block_names:
        block_alive_key = f'relia:data-uploader:sessions:{g.session_id}:devices:{device_identifier}:blocks:{block_identifier}:alive'
        if redis_store.get(block_alive_key) != b'1':
            block_names.remove(block_identifier)

    return jsonify({
        "blocks": block_names,
        "success": True
    })

@api_blueprint.route('/data/current/devices/<device_identifier>/blocks/<block_identifier>')
def get_data(device_identifier, block_identifier):
    block_key = f'relia:data-uploader:sessions:{g.session_id}:devices:{device_identifier}:blocks:{block_identifier}'
    

    initial_time = time.time()
    data = None
    while True:

        empty = False
        while not empty:
            newest_data = redis_store.lpop(block_key)
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
        return jsonify(success=True, data=None)

    decoded_data = json.loads(data)

    return jsonify(success=True, data=decoded_data)
