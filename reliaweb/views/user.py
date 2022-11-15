import os
import logging

from werkzeug.utils import secure_filename
from flask import Blueprint, jsonify, current_app, request, make_response

from reliaweb.auth import get_current_user
from reliaweb import weblab

logger = logging.getLogger(__name__)

user_blueprint = Blueprint('user', __name__)

@weblab.initial_url
def initial_url():
    return "http://localhost:3000"

@user_blueprint.route('/auth')
def auth():
    current_user = get_current_user()
    if current_user['anonymous']:
        return _corsify_actual_response(jsonify(success=True, auth=False))

    return _corsify_actual_response(jsonify(success=True, auth=True, user_id=current_user['username_unique'], session_id=current_user['session_id']))

def _corsify_actual_response(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

@user_blueprint.route('/uploads/<file_id>', methods=['POST'])
def file_upload(file_id):
    upload_folder = current_app.config['UPLOAD_FOLDER']
    target=os.path.join(upload_folder,'test_docs')
    if not os.path.isdir(target):
        os.mkdir(target)
    logger.info("welcome to upload`")
    file = request.files['file'] 
    filename = secure_filename(file.filename)
    destinatio = os.path.join(target, filename)
    file.save(destination)
    session['uploadFilePath']=destination
    response="Something"
    return response

