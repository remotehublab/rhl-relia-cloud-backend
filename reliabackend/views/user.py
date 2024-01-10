import os
import requests

from werkzeug.utils import secure_filename
from flask import Blueprint, jsonify, current_app, request

from weblablib import poll as wl_poll

from reliabackend.auth import get_current_user
from reliabackend.device_data import delete_existing_session_data
from reliabackend.storage import get_list_of_files, get_metadata, get_stored_file
from reliabackend import weblab

user_blueprint = Blueprint('user', __name__)

@user_blueprint.before_request
def before_request():
    current_user = get_current_user()
    if current_user['anonymous']:
        return _corsify_actual_response(jsonify(success=False))

@weblab.initial_url
def initial_url():
    return f"{current_app.config['CDN_URL']}/"

@user_blueprint.route('/tasks/', methods = ['POST'])
def add_task_to_scheduler():
    """
    This method will call the scheduler creating a new task in the scheduler.
    It does not expect any data (we rely on the existing metadata), and it will
    call the scheduler server.

    It will return information such as:
    {
        "taskIdentifier": "asdfadsfadfafadsfadfadfafd",
        "status": "queued", 
        "message": "Loading successful",
        "success": true
    }

    where the frontend is expected to retrieve "success" to know if it worked or not
    (and report what is the error if it did not work), and then the taskIdentifier
    so that the rest of the calls of the frontend related to the scheduler go directly
    to the scheduler.
    """
    current_user = get_current_user()
    if current_user['anonymous']:
        return _corsify_actual_response(jsonify(success=False))
    
    request_data = request.get_json(silent=True, force=True)

    list_of_files = get_list_of_files()
    metadata = get_metadata(list_of_files)
    list_of_receiver_files = metadata.get('receiver', [])
    list_of_transmitter_files = metadata.get('transmitter', [])

    if list_of_receiver_files:
        receiver_filename: str = list_of_receiver_files[0]
        receiver_file_content: bytes = get_stored_file(receiver_filename)
    else:
        # Temporarily
        return jsonify(success=False, message="At least one receiver is needed"), 400

    if list_of_transmitter_files:
        transmitter_filename: str = list_of_transmitter_files[0]
        transmitter_file_content: bytes = get_stored_file(transmitter_filename)
    else:
        # Temporarily
        return jsonify(success=False, message="At least one transmitter is needed"), 400
    
    delete_existing_session_data(current_user['session_id'])

    # Temporarily, assume all files (grc) are text (which they are)
    transmitter_file_content: str = transmitter_file_content.decode()
    receiver_file_content: str = receiver_file_content.decode()

    # TODO: in the future add priority
    priority = None

    user_id = current_user['username_unique']

    object = {
        "grc_files": {
            "receiver": {
                "filename": receiver_filename,
                "content": receiver_file_content
            },
            "transmitter": {
                "filename": transmitter_filename,
                "content": transmitter_file_content
            },
        },
        "priority": priority,
        "session_id": current_user['session_id'],
        "user_id": user_id,
    }

    scheduler_token = current_app.config['SCHEDULER_TOKEN']
    response_json = requests.post(f"{current_app.config['SCHEDULER_BASE_URL']}/scheduler/user/tasks/", json=object, headers={'relia-secret': scheduler_token}, timeout=(30, 30)).json()
    return _corsify_actual_response(jsonify(response_json))

@user_blueprint.route('/poll')
def poll():
    wl_poll()
    current_user = get_current_user()
    if current_user['anonymous'] or current_user['time_left'] <= 0:
        return _corsify_actual_response(jsonify(success=False, redirect_to=current_app.config['REDIRECT_URL'], user_id=None, session_id=None, locale=None))

    return _corsify_actual_response(jsonify(success=True, redirect_to=current_user['redirect_to'], user_id=current_user['username_unique'], session_id=current_user['session_id'], locale=current_user['locale']))

@user_blueprint.route('/upload/<target_device>', methods=['POST'])
def file_upload(target_device):
    if target_device not in ('transmitter', 'receiver'):
        return "Target not found", 404

    current_user = get_current_user()
    if current_user['anonymous']:
       return _corsify_actual_response(jsonify(success=False, message="Unauthenticated user"))
    upload_folder = 'uploads'
    subtarget=os.path.join(upload_folder, secure_filename(current_user['username_unique']))
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
        return _corsify_actual_response(jsonify(success=False, message="Unsupported extension"))
    return _corsify_actual_response(jsonify(success=True))

def _corsify_actual_response(response):
    response.headers['Access-Control-Allow-Origin'] = '*';
    response.headers['Access-Control-Allow-Credentials'] = 'true';
    response.headers['Access-Control-Allow-Methods'] = 'OPTIONS, GET, POST';
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Depth, User-Agent, X-File-Size, X-Requested-With, If-Modified-Since, X-File-Name, Cache-Control';
    return response
