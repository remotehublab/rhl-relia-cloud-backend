import os
import logging

from werkzeug.utils import secure_filename
from flask import Blueprint, jsonify, current_app, request, make_response

from reliaweb.auth import get_current_user
from reliaweb import weblab

user_blueprint = Blueprint('user', __name__)

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
def file_upload():
    current_user = get_current_user()
    if current_user['anonymous']:
       return _corsify_actual_response(jsonify(success=False))
    upload_folder = 'reliaweb/views/uploads'
    subtarget=os.path.join(upload_folder,current_user['username_unique'])
    if not os.path.isdir(subtarget):
        os.mkdir(subtarget)
    target=os.path.join(subtarget,'transmitter')
    if not os.path.isdir(target):
        os.mkdir(target)
    target2=os.path.join(subtarget,'receiver')
    if not os.path.isdir(target2):
        os.mkdir(target2)
    file = request.files['file'] 
    filename = secure_filename(file.filename)
    file2 = request.files['file2']
    filename2 = secure_filename(file2.filename)
    if filename.endswith('.grc'):
        destination="/".join([target, filename])
        file.save(destination)
    if filename2.endswith('.grc'):
        destination2="/".join([target2, filename2])
        file2.save(destination2)
    return _corsify_actual_response(jsonify(success=True))

def _corsify_actual_response(response):
    response.headers['Access-Control-Allow-Origin'] = '*';
    response.headers['Access-Control-Allow-Credentials'] = 'true';
    response.headers['Access-Control-Allow-Methods'] = 'OPTIONS, GET, POST';
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Depth, User-Agent, X-File-Size, X-Requested-With, If-Modified-Since, X-File-Name, Cache-Control';
    return response
