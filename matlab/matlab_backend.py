import os, socket
import numpy as np
import json5
import time
from multiprocessing import Process
import subprocess
import sys
from matlab.matlab_daemon import start_daemon
from pathlib import Path

SOCKET_PATH = '/tmp/csbenchlab_matlab_daemon.sock'

class MatlabBackend:

    commands = {
        'get_library_info': ("get_library_info('{}, {}')", 1),
        'list_component_libraries': ("list_component_libraries()", 1),
        'refresh_component_library': ("refresh_component_library('{}')", 0),
        'register_component_library': ("register_component_library('{}', {})", 0),
        'get_or_create_component_library': ("get_or_create_component_library('{}', 1)", 0),
        'remove_component_library': ("remove_component_library('{}')", 0),
        'register_component_from_file': ("register_component_from_file('{}', '{}')", 1),
        'unregister_component': ("unregister_component('{}', '{}')", 0),
        'export_component_library': ("export_component_library('{}', '{}')", 0),
        'get_component_info': ("get_component_info('{}')", 1),
        'get_available_plugins': ("get_available_plugins(); ", 'dict'),
        'get_component_params': ("jsonify_component_param_description(ComponentManager.get('{}').get_component_params('{}', '{}'))", 1),
        'get_plugin_info_from_lib': ("get_plugin_info_from_lib('{}', '{}')", 1),
        "generate_control_environment": ("generate_control_environment('{}', '{}', {})", 0),
        "create_environment": ("create_environment('{}', '{}')", 0),
    }

    def __init__(self, restart_daemon):
        self._restart_daemon = restart_daemon
        self.csb_path = None

    @property
    def is_long_generation(self):
        return True

    def get_daemon_source_path(self):
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.connect(SOCKET_PATH)
        client.send('csb:path'.encode())
        csb_path = client.recv(1024).decode()
        client.close()
        return csb_path

    def is_daemon_running(self):
        exists = os.path.exists(SOCKET_PATH)
        if exists:
            try:
                client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                client.connect(SOCKET_PATH)
                client.send('csb:ping'.encode())
                response = client.recv(1024)
                client.close()
                if response.decode() == 'csb:pong':
                    return True
            except:
                pass
        return False

    def start_daemon(self):
        # start matlab_daemon.py as a standalone process
        path = Path(__file__).parent / "matlab_daemon.py"
        if sys.platform == 'win32':
            subprocess.Popen(['python', str(path)],
                         creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
                         stdin=subprocess.DEVNULL,
                         stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL,
                         close_fds=True)
        else:
            subprocess.Popen(['nohup', 'python3', str(path)],
                         stdin=subprocess.DEVNULL,
                         stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL,
                         close_fds=True,
                         start_new_session=True)
        time.sleep(1)
        # wait for daemon to start and socket to appear
        for i in range(20):
            if self.is_daemon_running():
                return True
            time.sleep(0.5)
        return False

    def parse_response(self, response, nargout, is_json, has_error=False):
        has_error = response.startswith("csb_err:")
        if has_error:
            raise Exception(response[len("csb_err:"):])
        has_error = response.startswith("err:")
        if has_error:
            raise Exception(response[len("err:"):])
        if not is_json:
            return response
        if response == "":
            return None
        if nargout == 'dict':
            temp = json5.loads(response)
            return dict(zip(temp["keys"], temp["values"]))
        else:
            return json5.loads(response)


    def eng_eval(self, command, nargout, is_json=True):
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.connect(SOCKET_PATH)
        client.send(command.encode())

        if not is_json:
            response = client.recv(1024)
        else:
            l = client.recv(5)
            has_err = l[0]
            if has_err:
                response = client.recv(1024)
            else:
                sz = int.from_bytes(l[1:], byteorder='little')
                response = client.recv(sz)


        client.close()
        return self.parse_response(response.decode(), nargout, is_json)

    def run_command(self, command, *args):

        is_json = False
        nargout = 0
        if not command.startswith("csb:"):
            is_json = True
            cmd = self.commands.get(command, None)
            if cmd is None:
                raise Exception(f"Unknown command '{command}'")
            command, nargout = cmd
            if command.count('{}') != len(args):
                raise Exception(f"Command '{command}' expects {command.count('{}')} arguments,"
                                f" but {len(args)} were given.")
            command = command.format(*args)


            if nargout == 'dict':
                command = """
                temp = {command};
                r.keys = temp.keys();
                r.values = temp.values();
                temp=jsonencode(r);
                """.format(command=command)
            elif nargout != 0:
                command = """
                temp = jsonencode({command});
                """.format(command=command)

        return self.eng_eval(command, nargout=nargout, is_json=is_json)

    def start(self):

        is_running = self.is_daemon_running()
        if is_running and not self._restart_daemon:
            self.csb_path = self.get_daemon_source_path()
            print("Matlab daemon already running.")
            return
        if is_running and self._restart_daemon:
            print("Stopping existing matlab daemon...")
            self.run_command("csb:exit")
            time.sleep(1)
            if self.is_daemon_running():
                raise Exception("Could not stop existing matlab daemon.")
        print("Starting matlab daemon...")
        if not self.start_daemon():
            raise Exception("Could not start matlab daemon.")
        print("Matlab daemon started.")
        self.csb_path = self.run_command("csb:path")


    def stop(self):
        pass


# set commands as functions to the class
for cmd in MatlabBackend.commands.keys():
    setattr(MatlabBackend, cmd, lambda self, *args, cmd=cmd: self.run_command(cmd, *args))