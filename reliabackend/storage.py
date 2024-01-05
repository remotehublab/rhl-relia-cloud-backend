import os
import glob
import json

from flask import current_app
from werkzeug.utils import secure_filename

from typing import Optional, List, Dict

from reliabackend.auth import get_current_user

def _get_user_folder():
    user = get_current_user()
    upload_folder = os.path.abspath(current_app.config['UPLOAD_FOLDER'])
    return os.path.join(upload_folder, secure_filename(user['username_unique']))

def get_list_of_files():
    """
    Take all the files (not folders) in the user folder and return the filename
    """
    user_folder = _get_user_folder()
    return [
        os.path.basename(filename) for filename in glob.glob(f"{user_folder}/*")
        if os.path.isfile(filename)
    ]

def get_stored_file(filename) -> Optional[bytes]:
    """
    Return the file content or None if it does not exist
    """
    user = get_current_user()
    upload_folder = os.path.abspath(current_app.config['UPLOAD_FOLDER'])
    user_folder = os.path.join(upload_folder, secure_filename(user['username_unique']))
    full_filename = os.path.join(user_folder, filename)
    if os.path.exists(full_filename):
        return open(full_filename, 'rb').read()
    return None


def get_metadata(list_of_files: List[str]):
    """
    Read the metadata file and return the content
    """
    user_folder = _get_user_folder()
    metadata_filename = os.path.join(user_folder, 'metadata', 'files.json')
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

def set_metadata(metadata: Dict[str, List[str]]):
    """
    Write the metadata file
    """
    user_folder = _get_user_folder()
    metadata_filename = os.path.join(user_folder, 'metadata', 'files.json')
    with open(metadata_filename, 'w') as f:
        json.dump(metadata, f)

