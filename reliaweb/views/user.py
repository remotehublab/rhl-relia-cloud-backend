import glob
import os
import logging

from werkzeug.utils import secure_filename
from flask import Blueprint, jsonify, current_app, request, make_response, send_file

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

@user_blueprint.route('/transactions')
def transact():
    current_user = get_current_user()
    if current_user['anonymous']:
       return _corsify_actual_response(jsonify(success=False))
    upload_folder = 'reliaweb/views/uploads'
    subtarget = os.path.join(upload_folder,current_user['username_unique'])
    if not os.path.isdir(subtarget):
        os.mkdir(subtarget)
    target = os.path.join(subtarget,'transmitter')
    if not os.path.isdir(target):
        os.mkdir(target)
    target2 = os.path.join(subtarget,'receiver')
    if not os.path.isdir(target2):
        os.mkdir(target2)
    files_path = os.path.join(target, '*')
    files_path2 = os.path.join(target2, '*')
    files = sorted(glob.iglob(files_path), key=os.path.getctime, reverse=True) 
    files2 = sorted(glob.iglob(files_path2), key=os.path.getctime, reverse=True) 
    r = []
    t = []
    for i in range(min(5, len(files))):
        if files[i]:
            filename = os.path.basename(files[i]).split('/')[-1]
            t.append(filename)
            transact_helper(filename, current_user['username_unique'], 't')
    for j in range(min(5, len(files2))):
        if files2[j]:
            filename = os.path.basename(files2[j]).split('/')[-1]
            r.append(filename)
            transact_helper(filename, current_user['username_unique'], 'r')
    return _corsify_actual_response(jsonify(success=True, receiver_files=r, transmitter_files=t, username=current_user['username_unique']))

@user_blueprint.route('/transactions/<username>/<side>/<filename>', methods=['GET', 'POST'])
def transact_helper(filename, username, side):
    current_user = get_current_user()
    upload_folder = 'reliaweb/views/uploads'
    subtarget = os.path.join(upload_folder,current_user['username_unique'])
    if side == 't':
       target = os.path.join(subtarget,'transmitter')
    if side == 'r':
       target = os.path.join(subtarget,'receiver')
    file = os.path.join(target, filename)
    file2 = os.path.join(*(file.split(os.path.sep)[1:]))
    response = make_response(send_file(file2))
    return _corsify_actual_response(response)

@user_blueprint.route('/upload_t', methods=['POST'])
def file_upload():
    print('Made it 1', flush=True)
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
    file = request.files['file'] 
    filename = secure_filename(file.filename)
    if filename.endswith('.grc'):
        destination="/".join([target, filename])
        file.save(destination)
        print('Made it 2', flush=True)
    return _corsify_actual_response(jsonify(success=True))

@user_blueprint.route('/upload_r', methods=['POST'])
def file_upload2():
    print('Made it 1', flush=True)
    current_user = get_current_user()
    if current_user['anonymous']:
       return _corsify_actual_response(jsonify(success=False))
    upload_folder = 'reliaweb/views/uploads'
    subtarget=os.path.join(upload_folder,current_user['username_unique'])
    if not os.path.isdir(subtarget):
        os.mkdir(subtarget)
    target=os.path.join(subtarget,'receiver')
    if not os.path.isdir(target):
        os.mkdir(target)
    file = request.files['file'] 
    filename = secure_filename(file.filename)
    if filename.endswith('.grc'):
        destination="/".join([target, filename])
        file.save(destination)
        print('Made it 2', flush=True)
    return _corsify_actual_response(jsonify(success=True))

def _corsify_actual_response(response):
    response.headers['Access-Control-Allow-Origin'] = '*';
    response.headers['Access-Control-Allow-Credentials'] = 'true';
    response.headers['Access-Control-Allow-Methods'] = 'OPTIONS, GET, POST';
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Depth, User-Agent, X-File-Size, X-Requested-With, If-Modified-Since, X-File-Name, Cache-Control';
    return response
