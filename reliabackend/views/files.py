"""
This module handles all the endpoints related to uploading, downloading files
and the user (e.g., uploading files, downloading the list of files, etc.).

The file structure is the following:
/uploads/<user-unique-id>/<test_rx.grc>
/uploads/<user-unique-id>/<test_tx.grc>
/uploads/<user-unique-id>/<library.grc>
/uploads/<user-unique-id>/metadata/files.json

Where files.json has the following structure:
{
    "receiver": [
        "text_rx.grc",
        "library.grc"
    ],
    "transmitter": [
        "test_tx.grc",
        "library.grc"
    ]
}

"""
import json
import os
import glob
from typing import Dict, List

from werkzeug.utils import secure_filename
from flask import Blueprint, jsonify, request, g, current_app

from reliabackend.auth import get_current_user

files_blueprint = Blueprint('files', __name__)



@files_blueprint.before_request
def check_authentication():
    user = get_current_user()
    if user['anonymous']:
        return jsonify(success=False)

    # The folder configured in the config file where the files will be stored
    upload_folder = os.path.abspath(current_app.config['UPLOAD_FOLDER'])

    # The user folder where the files will be located
    g.user_folder = os.path.join(upload_folder, secure_filename(user['username_unique']))
    if request.method not in ('GET', 'HEAD'):
        os.makedirs(g.user_folder, exist_ok=True)
        os.makedirs(os.path.join(g.user_folder, 'metadata'), exist_ok=True)

@files_blueprint.route('/', methods=['GET', 'POST'])
def manage_files():
    """
    If GET, list all the files that are in the d
    """
    if request.method == 'POST':
        for file_form_name in request.files:
            for file_object in request.files.getlist(file_form_name):
                file_object.save(os.path.join(g.user_folder, secure_filename(file_object.filename)))

    list_of_files = _get_list_of_files()
    metadata = _get_metadata(list_of_files)
    return jsonify(success=True, files=list_of_files, metadata=metadata)

@files_blueprint.route('/<filename>', methods=['GET', 'DELETE'])
def manage_file(filename):
    """
    Given a filename, either GET or DELETE the file.
    """
    list_of_files = _get_list_of_files()
    sec_filename = secure_filename(filename)

    if filename not in list_of_files:
        return jsonify(success=False, message="File not found"), 404

    if request.method == 'DELETE':
        if filename in list_of_files:
            full_filename = os.path.join(g.user_folder, sec_filename)
            if os.path.exists(full_filename):
                os.remove(full_filename)
            return jsonify(success=True)
        else:
            return jsonify(success=False, message="File not found"), 404

    # If GET, provide the metadata information
    full_metadata = _get_metadata(list_of_files)
    file_metadata = {
        'receiver': False,
        'transmitter': False,
        # We could add in the future date or whatever
    }

    if sec_filename in full_metadata['receiver']:
        file_metadata['receiver'] = True

    if sec_filename in full_metadata['transmitter']:
        file_metadata['transmitter'] = True

    return jsonify(success=True, **file_metadata)

@files_blueprint.route('/metadata/', methods=['GET', 'POST'])
def metadata():
    """
    If GET, list all the files selected (e.g., which ones are for receiver and
    which ones are for transmitter)
    """
    list_of_files = _get_list_of_files()

    if request.method == 'POST':
        provided_metadata = request.get_json(silent=True, force=True) or {}
        provided_receiver_files = provided_metadata.get('receiver')
        provided_transmitter_files = provided_metadata.get('transmitter')

        metadata = {
            'receiver': [],
            'transmitter': []
        }

        for receiver_file in provided_receiver_files:
            if receiver_file in list_of_files:
                metadata['receiver'].append(receiver_file)

        for transmitter_file in provided_transmitter_files:
            if transmitter_file in list_of_files:
                metadata['transmitter'].append(transmitter_file)

        _set_metadata(metadata)
    else:
        metadata = _get_metadata(list_of_files)

    return jsonify(success=True, metadata=metadata)


def _get_list_of_files():
    """
    Take all the files (not folders) in the user folder and return the filename
    """
    return [
        os.path.basename(filename) for filename in glob.glob(f"{g.user_folder}/*")
        if os.path.isfile(filename)
    ]

def _get_metadata(list_of_files: List[str]):
    """
    Read the metadata file and return the content
    """
    metadata_filename = os.path.join(g.user_folder, 'metadata', 'files.json')
    if os.path.exists(metadata_filename):
        with open(metadata_filename, 'r') as f:
            stored_metadata = json.load(f)
    else:
        stored_metadata = {
            'receiver': [],
            'transmitter': []
        }

    # Curated list only showing those that exist
    metadata = {
        'receiver': [fname for fname in stored_metadata.get('receiver', []) if fname in list_of_files],
        'transmitter': [fname for fname in stored_metadata.get('transmitter', []) if fname in list_of_files]
    }
    return metadata

def _set_metadata(metadata: Dict[str, List[str]]):
    """
    Write the metadata file
    """
    metadata_filename = os.path.join(g.user_folder, 'metadata', 'files.json')
    with open(metadata_filename, 'w') as f:
        json.dump(metadata, f)

