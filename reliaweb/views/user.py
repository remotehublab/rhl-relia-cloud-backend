import os
import logging

from werkzeug.utils import secure_filename
from flask import Blueprint, jsonify, current_app, request, make_response
#from flask_cors import CORS, cross_origin

from reliaweb.auth import get_current_user
from reliaweb import weblab

user_blueprint = Blueprint('user', __name__)
# CORS(user_blueprint, expose_headers='Authorization', resources={r"/upload": {"origins": "http://localhost:3000/"}})

@weblab.initial_url
def initial_url():
    return "http://localhost:3000/"

@user_blueprint.route('/auth')
def auth():
    current_user = get_current_user()
    if current_user['anonymous']:
        return _corsify_actual_response(jsonify(success=True, auth=False))

    return _corsify_actual_response(jsonify(success=True, auth=True, user_id=current_user['username_unique'], session_id=current_user['session_id']))

@user_blueprint.route('/upload', methods=['POST'])
#@cross_origin(origin='localhost', headers=['Content-Type','Authorization'])
def file_upload():
    upload_folder = 'uploads'
    target=os.path.join(upload_folder,'test_docs')
    if not os.path.isdir(target):
        os.mkdir(target)
    file = request.files['file'] 
    filename = secure_filename(file.filename)
    destination="/".join([target, filename])
    file.save(destination)
    return _corsify_actual_response(jsonify(success=True))

def _corsify_actual_response(response):
    response.headers['Access-Control-Allow-Origin'] = '*';
    response.headers['Access-Control-Allow-Credentials'] = 'true';
    response.headers['Access-Control-Allow-Methods'] = 'OPTIONS, GET, POST';
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Depth, User-Agent, X-File-Size, X-Requested-With, If-Modified-Since, X-File-Name, Cache-Control';
    return response
