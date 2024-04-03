import json
import os
import sys
import glob
import time
import tempfile
import subprocess

from typing import List

from flask import current_app

from reliabackend.grc_manager import GrcManager


def compile_grc_file(grc_filename: str):
    print(f"[{time.asctime()}] Starting compilation for file {grc_filename}", file=sys.stderr, flush=True)
    print(f"[{time.asctime()}] Starting compilation for file {grc_filename}", file=sys.stdout, flush=True)

    grc_manager = GrcManager(grc_serialized_content=open(grc_filename).read(), target_filename='target_file')
    with tempfile.TemporaryDirectory() as tempdir:
        full_grc_filename = os.path.join(tempdir, 'user_file.grc')
        grc_manager.save(tempdir, 'user_file.grc')

        open(os.path.join(tempdir, 'relia.json'), 'w').write(json.dumps({
                "uploader_base_url": "http://localhost:6001",
                "session_id": "my-session-id",
                "task_id": "my-task-id",
                "device_id": "my-device-id"
            }, indent=4))

        command = ['grcc', full_grc_filename, '-o', tempdir]

        p: subprocess.Popen = run_in_sandbox(command, tempdir)
        try:
            p.wait(timeout=10)
        except subprocess.TimeoutExpired:
            p.terminate()
            p.wait()
            return False
        
        stdout, stderr = p.communicate()
        print("STDOUT:", stdout)
        print("STDERR:", stderr)
        
        tmp_py_filename = os.path.join(tempdir, 'target_file.py')
        if os.path.exists(tmp_py_filename):
            uploads_py_filename = grc_filename[:-4] + '.py'
            py_content = open(tmp_py_filename, 'r').read()
            open(uploads_py_filename, 'w').write(py_content)
            print(f"[{time.asctime()}] File {tmp_py_filename} found, length={len(py_content)}")
        else:
            print(f"[{time.asctime()}] File {tmp_py_filename} not found")
        
        print(f"[{time.asctime()}] Compilation process finished", file=sys.stderr, flush=True)
        print(f"[{time.asctime()}] Compilation process finished", file=sys.stdout, flush=True)
            
def run_in_sandbox(command: List[str], directory: str) -> subprocess.Popen:
    """
    Run the command in a firejail sandbox
    """
    use_firejail = current_app.config['USE_FIREJAIL']
    if use_firejail:
        user = os.getenv('USER') or 'relia'
        profile = '\n'.join([
                    f"net none",
                    f"whitelist /home/{user}/.gr_fftw_wisdom",
                    f"whitelist /home/{user}/relia-blocks",
                    f"read-only /home/{user}/relia-blocks",
                    f"whitelist /home/{user}/.gnuradio/prefs",
                    f"read-only /home/{user}/.gnuradio/prefs",
                    f"read-only /home/{user}/.bashrc",
                    f"read-only /home/{user}/.profile",
                    f"whitelist /home/{user}/.grc_gnuradio",
                    f"read-only /home/{user}/.grc_gnuradio",
                    f"whitelist /home/{user}/.cache/grc_gnuradio",
                    f"whitelist {directory}",
                ])

        open(os.path.join(directory, 'firejail.profile'), 'w').write(profile)

        print(f"[{time.asctime()}] firejail.profile generated at {os.path.join(directory, 'firejail.profile')}")
        print(f"[{time.asctime()}] The content:")
        print(profile)

        print(f"[{time.asctime()}] The contents of the folder now are:")
        print(glob.glob(f"{directory}/*"))

        firejail_command = ['firejail', '--profile=firejail.profile']
        firejail_command.extend(command)
        print(f"[{time.asctime()}] Running command inside the firejail sandbox: {' '.join(command)}")
        print(f"[{time.asctime()}] So in reality it looks like: {' '.join(firejail_command)}")
        print(f"[{time.asctime()}] Running command inside the firejail sandbox: {' '.join(command)}", file=sys.stderr)
        print(f"[{time.asctime()}] So in reality it looks like: {' '.join(firejail_command)}", file=sys.stderr, flush=True)
        command_to_run = firejail_command
    else:
        print(f"[{time.asctime()}] Running command outside any sandbox: {' '.join(command)}")
        print(f"[{time.asctime()}] Running command outside any sandbox: {' '.join(command)}", file=sys.stderr, flush=True)
        command_to_run = command

    return subprocess.Popen(command_to_run, cwd=directory, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)