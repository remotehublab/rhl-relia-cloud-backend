import json

from flask import Blueprint, jsonify, render_template

from reliaweb import redis_store


main_blueprint = Blueprint('main', __name__)

@main_blueprint.route('/')
def index():
    return render_template("index.html")

api_blueprint = Blueprint('api', __name__)

@api_blueprint.route('/')
def index():
    return "Welcome to the API"

@api_blueprint.route('/data/current/<device_identifier>/blocks/<block_identifier>')
def get_data(device_identifier, block_identifier):

    session_identifier = 'my-session-id' # TODO

    block_key = f'relia:data-uploader:sessions:{session_identifier}:devices:{device_identifier}:blocks:{block_identifier}'
    
    empty = False
    data = None
    while not empty:
        newest_data = redis_store.lpop(block_key)
        if newest_data is None:
            empty = True
        else:
            data = newest_data

    if data is None:
        return jsonify(success=True, data=None)

    decoded_data = json.loads(data)

    return jsonify(success=True, data=decoded_data)
