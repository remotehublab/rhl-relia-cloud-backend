import os
import glob
import logging
import requests
import json
import jsonpickle

from werkzeug.utils import secure_filename
from flask import Blueprint, jsonify, current_app, request, make_response, send_file, redirect

from reliabackend.auth import get_current_user
from reliabackend import weblab

user_blueprint = Blueprint('user', __name__)

@weblab.initial_url
def initial_url():
    return current_app['CDN_URL']

@user_blueprint.route('/auth')
def auth():
    current_user = get_current_user()
    if current_user['anonymous']:
        return _corsify_actual_response(jsonify(success=True, auth=False))

    return _corsify_actual_response(jsonify(success=True, auth=True, user_id=current_user['username_unique'], session_id=current_user['session_id']))

@user_blueprint.route('/route/<user_id>', methods = ['POST'])
def route(user_id):
    current_user = get_current_user()
    if current_user['anonymous']:
       return _corsify_actual_response(jsonify(success=False))
    
    request_data = request.json
    current_app.logger.info(request_data)
    requests.post(f"{current_app.config['SCHEDULER_BASE_URL']}scheduler/user/tasks/{user_id}", json=json.dumps(request_data), headers={'relia-secret': 'password'}, timeout=(30, 30))
    return _corsify_actual_response(jsonify(success=True))

@user_blueprint.route('/transactions')
def transact():
    current_user = get_current_user()
    if current_user['anonymous']:
       return _corsify_actual_response(jsonify(success=False))
    upload_folder = 'uploads'
    subtarget = os.path.join(upload_folder,current_user['username_unique'])
    if not os.path.isdir(subtarget):
        os.mkdir(subtarget)
    transmitter_target = os.path.join(subtarget,'transmitter')
    if not os.path.isdir(transmitter_target):
        os.mkdir(transmitter_target)
    receiver_target = os.path.join(subtarget,'receiver')
    if not os.path.isdir(receiver_target):
        os.mkdir(receiver_target)
    transmitter_files_path = os.path.join(transmitter_target, '*')
    receiver_files_path = os.path.join(receiver_target, '*')
    transmitter_file_names = sorted(glob.iglob(transmitter_files_path), key=os.path.getctime, reverse=True) 
    receiver_file_names = sorted(glob.iglob(receiver_files_path), key=os.path.getctime, reverse=True) 

    transmitter_files = []
    receiver_files = []
    for transmitter_filename in transmitter_file_names[:5]:
        filename = os.path.basename(transmitter_filename).split('/')[-1]
        transmitter_files.append(filename)
        transact_helper(filename, current_user['username_unique'], 'transmitter')

    for receiver_filename in receiver_file_names[:5]:
        filename = os.path.basename(receiver_filename).split('/')[-1]
        receiver_files.append(filename)
        transact_helper(filename, current_user['username_unique'], 'receiver')

    return _corsify_actual_response(jsonify(success=True, 
                receiver_files=receiver_files, transmitter_files=transmitter_files, 
                username=current_user['username_unique']))

@user_blueprint.route('/transactions/<username>/<side>/<filename>', methods=['GET', 'POST'])
def transact_helper(filename, username, side):
    if side not in ('transmitter', 'receiver'):
        return "Target not found", 404
    current_user = get_current_user()
    upload_folder = os.path.join(os.path.abspath('.'), 'uploads')
    subtarget = os.path.join(upload_folder,current_user['username_unique'])
    target = os.path.join(subtarget, side)
    file = os.path.join(target, filename)
    response = make_response(send_file(file))
    return _corsify_actual_response(response)

@user_blueprint.route('/upload/<target_device>', methods=['POST'])
def file_upload(target_device):
    if target_device not in ('transmitter', 'receiver'):
        return "Target not found", 404

    current_user = get_current_user()
    if current_user['anonymous']:
       return _corsify_actual_response(jsonify(success=False))
    upload_folder = 'uploads'
    subtarget=os.path.join(upload_folder,current_user['username_unique'])
    if not os.path.isdir(subtarget):
        os.mkdir(subtarget)
    target=os.path.join(subtarget, target_device)
    if not os.path.isdir(target):
        os.mkdir(target)
    file = request.files['file'] 
    filename = secure_filename(file.filename)
    if filename.endswith('.grc'):
        destination="/".join([target, filename])
        file.save(destination)
    return _corsify_actual_response(jsonify(success=True))

def _corsify_actual_response(response):
    response.headers['Access-Control-Allow-Origin'] = '*';
    response.headers['Access-Control-Allow-Credentials'] = 'true';
    response.headers['Access-Control-Allow-Methods'] = 'OPTIONS, GET, POST';
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Depth, User-Agent, X-File-Size, X-Requested-With, If-Modified-Since, X-File-Name, Cache-Control';
    return response
