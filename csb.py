#! /usr/bin/env python3

from argparse import ArgumentParser
from http.client import HTTPConnection
import json
import requests
import os, sys
import tempfile
import zipfile

from csbenchlab.csb_utils import load_app_config, get_active_backend
from csbenchlab.csb_app_setup import get_appdata_dir
from backend.python_backend import PythonBackend
from pathlib import Path

URI = "http://127.0.0.1:8000"

def _csb_complete(*args):
    if args and args[0] == "--setup-bash-completion":
        print("complete -C 'csb --complete-bash' csb")
    elif args and args[0] == "--complete-bash":
        print("")
    else:
        return False
    return True

def main():

    if _csb_complete(*sys.argv[1:]):
        return


    parser = ArgumentParser(description="CSBenchlab Command-Line Interface")
    parser.add_argument("first", choices=["login", 'register-user', "env", 'lib'], type=str, help="Object to interact with.")
    parser.add_argument("second", type=str, help="Sub-command for the specified object.")
    # capture all remaining arguments after the first two positional arguments. Caputre as a list of strings.

    (args, unknown) = parser.parse_known_args()


    if args.first == "login":
        login([args.second, *unknown])

    if args.first == "register-user":
        register_user([args.second, *unknown])

    if args.first == "env":
        if hasattr(EnvCommands, args.second):
            EnvCommands.__dict__[args.second](unknown)
        else:
            raise ValueError(f"Unknown sub-command '{args.second}' for 'env'.")
    elif args.first == "lib":
        if hasattr(LibCommands, args.second):
            LibCommands.__dict__[args.second](unknown)
        else:
            raise ValueError(f"Unknown sub-command '{args.second}' for 'lib'.")
    elif args.first == "login":
        pass
    pass


def register_user(args):
    if not args or len(args) < 2:
        print("Usage: csb register-user <username> <password>")
        return
    username = args[0]
    password = args[1]
    email = args[2] if len(args) > 2 else ""
    is_admin = args[3].lower() == 'true' if len(args) > 3 else False
    response = requests.post(
        URI + "/register_user",
        data=json.dumps({'username': username, 'password': password, 'email': email, 'is_admin': is_admin}),
        headers={'Content-Type': 'application/json'}
    )
    if response.status_code == 200:
        print("Registration successful.")
    else:
        msg = response.json().get('detail', 'Unknown error')
        print(f"Registration failed: {msg}")


def login(args):
    if not args or len(args) < 2:
        print("Usage: csb login <username> <password>")
        return
    username = args[0]
    password = args[1]
    response = requests.post(
        URI + "/login",
        data={'username': username, 'password': password}
    )

    access_token = response.json().get('access_token', None)
    # save the response cookies to a file named 'csb_cookies.txt' in the user's home directory
    token_file = os.path.join(get_appdata_dir(), 'token.txt')
    with open(token_file, 'w') as f:
        f.write(f"access_token={access_token}\n")

    if response.status_code == 200:
        print("Login successful.")
    else:
        print("Login failed. Please check your credentials.")


def get_access_token():
    token_file = os.path.join(get_appdata_dir(), 'token.txt')
    token = ""
    if os.path.exists(token_file):
        with open(token_file, 'r') as f:
            for line in f:
                if line.startswith("access_token="):
                    token = line.strip().split('=', 1)[1]
                    break
    return token


def zip_directory_as_tmp(path):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
    tmp.close()
    full_path = tmp.name
    with zipfile.ZipFile(full_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(path):
            for f in files:
                full_path_in_zip = os.path.join(root, f)
                arcname = os.path.relpath(full_path_in_zip, start=path)
                zf.write(full_path_in_zip, arcname)
    return full_path


class LibCommands():

    @staticmethod
    def pull(args):
        lib_name = args[0]
        access_token = get_access_token()
        headers = {'Authorization': f'Bearer {access_token}'} if access_token else {}
        response = requests.get(URI + "/lib/download", params={'lib': lib_name}, headers=headers)
        if response.status_code != 200:
            msg = response.json().get('detail', 'Unknown error')
            print(f"Failed to pull library '{lib_name}': {msg}")
            return

        file_name = response.headers.get('X-Filename', '')
        if not file_name:
            raise ValueError("Response does not contain 'X-Filename' header.")

        save_path = os.path.join(get_appdata_dir(), 'libs', file_name)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        # extract zip file from response content
        import io
        with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
            zf.extractall(save_path)

        backend = get_active_backend()
        backend.setup_library(save_path)
        print(f"Library '{lib_name}' pulled and set up at '{save_path}'.")
        pass

    @staticmethod
    def push(args):
        if not args:
            print("Usage: csb lib push <path> [--override] [--public]")
            return

        path = args[0]
        override = '--override' in args
        public = '--public' in args

        backend = get_active_backend()

        if not backend.is_valid_component_library(path):
            path_n = backend.get_library_path(path)
            if path_n is None or not backend.is_valid_component_library(path_n):
                libraries = backend.list_component_libraries()
                library_names = [lib['Name'] for lib in libraries]
                raise ValueError(f"Path '{path}' is not a valid library or registered library." +
                                 f" Available libraries: {library_names}")
            path = path_n

        # if path is a directory, zip it into a temporary file
        if os.path.isdir(path):
            full_path = zip_directory_as_tmp(path)
        elif not os.path.isfile(path):
            raise ValueError(f"Path '{path}' is not a valid file or directory.")

        access_token = get_access_token()
        headers = {'Authorization': f'Bearer {access_token}'} if access_token else {}
        # set content_type to file
        name = os.path.basename(path)
        response = requests.post(
            URI + "/lib/add",
            files={'lib_file': (name, open(full_path, 'rb'), 'application/octet-stream')},
            data={'override_existing': str(override).lower(), 'is_public': str(public).lower()},
            headers=headers
        )

        if response.status_code == 200:
            print(f"Library '{name}' pushed successfully.")
        else:
            msg = response.json().get('detail', 'Unknown error')
            print(f"Failed to push library '{name}': {msg}")

    @staticmethod
    def install(args):
        pass

    @staticmethod
    def remove(args):
        if not args:
            print("Usage: csb lib remove <lib_name>")
            return
        lib_name = args[0]
        access_token = get_access_token()
        headers = {'Authorization': f'Bearer {access_token}'} if access_token else {}
        response = requests.delete(
            URI + "/lib/remove",
            params={'lib': lib_name},
            headers=headers
        )
        if response.status_code == 200:
            print(f"Library '{lib_name}' removed successfully.")
        else:
            msg = response.json().get('detail', 'Unknown error')
            print(f"Failed to remove library '{lib_name}': {msg}")
        pass

    @staticmethod
    def list(args):
        public = '--public' in args
        verbose = '--verbose' in args or '-v' in args
        if public:
            url = URI + "/lib/list_public"
        else:
            url = URI + "/lib/list"
        access_token = get_access_token()
        headers = {'Authorization': f'Bearer {access_token}'} if access_token else {}
        response = requests.get(url,
            headers=headers
            )
        data = response.content
        if verbose:
            print(data.decode("utf-8"))
        else:
            libs = response.json()
            names = [lib['name'] for lib in libs]
            print("\n".join(names))

class EnvCommands():

    @staticmethod
    def push(args):
        if not args:
            print("Usage: csb env push <path> [--override] [--public]")
            return

        path = args[0]
        override = '--override' in args
        public = '--public' in args

        cfg = load_app_config()

        if not PythonBackend.is_valid_environment_path(path):
            item = next((k for k in cfg['envs'] if k["Name"] == path), None)
            if item is None:
                raise ValueError(f"Path '{path}' is not a valid environment or registered environment.")
            path = Path(item['Path']).parent

        if not PythonBackend.is_valid_environment_path(path):
            raise ValueError(f"Path '{path}' is not a valid environment.")

        # if path is a directory, zip it into a temporary file
        if os.path.isdir(path):
            full_path = zip_directory_as_tmp(path)
        elif not os.path.isfile(path):
            raise ValueError(f"Path '{path}' is not a valid file or directory.")

        access_token = get_access_token()
        headers = {'Authorization': f'Bearer {access_token}'} if access_token else {}
        # set content_type to file
        name = os.path.basename(path)
        response = requests.post(
            URI + "/env/add",
            files={'env_file': (name, open(full_path, 'rb'), 'application/octet-stream')},
            data={'override_existing': str(override).lower(), 'is_public': str(public).lower()},
            headers=headers
        )

        if response.status_code == 200:
            print(f"Environment '{name}' pushed successfully.")
        else:
            msg = response.json().get('detail', 'Unknown error')
            print(f"Failed to push environment '{name}': {msg}")


    @staticmethod
    def pull(args):

        env_name = args[0]
        access_token = get_access_token()
        headers = {'Authorization': f'Bearer {access_token}'} if access_token else {}
        response = requests.get(URI + "/env/download", params={'env': env_name}, headers=headers)
        if response.status_code != 200:
            msg = response.json().get('detail', 'Unknown error')
            print(f"Failed to pull environment '{env_name}': {msg}")
            return

        file_name = response.headers.get('X-Filename', '')
        if not file_name:
            raise ValueError("Response does not contain 'X-Filename' header.")

        save_path = os.path.join(get_appdata_dir(), 'envs', file_name)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        # extract zip file from response content
        import io
        with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
            zf.extractall(save_path)

        backend = get_active_backend()
        backend.setup_environment(save_path)
        print(f"Environment '{env_name}' pulled and set up at '{save_path}'.")

    @staticmethod
    def make(args):

        name = args[0]
        public = 'public' in args
        private = 'private' in args
        access_token = get_access_token()
        headers = {'Authorization': f'Bearer {access_token}'} if access_token else {}
        if public:
            response = requests.get(
                URI + "/env/make_public",
                params={'env': name},
                headers=headers
            )
        elif private:
            response = requests.get(
                URI + "/env/make_private",
                params={'env': name},
                headers=headers
            )
        else:
            raise ValueError("Specify either 'public' or 'private'.")
        if response.status_code == 200:
            status = "public" if public else "private"
            print(f"Environment '{name}' is now {status}.")
        else:
            msg = response.json().get('detail', 'Unknown error')
            print(f"Failed to change visibility of environment '{name}': {msg}")

    @staticmethod
    def list(args):
        public = '--public' in args
        verbose = '--verbose' in args or '-v' in args

        if public:
            url = URI + "/env/list_public"
        else:
            url = URI + "/env/list"
        access_token = get_access_token()
        headers = {'Authorization': f'Bearer {access_token}'} if access_token else {}
        response = requests.get(url,
            headers=headers
            )
        data = response.content
        if verbose:
            print(data.decode("utf-8"))
        else:
            envs = response.json()
            names = [env['name'] for env in envs]
            print("\n".join(names))

    @staticmethod
    def remove(args):
        if not args:
            print("Usage: csb env remove <env_name>")
            return
        env_name = args[0]
        access_token = get_access_token()
        headers = {'Authorization': f'Bearer {access_token}'} if access_token else {}
        response = requests.delete(
            URI + "/env/remove",
            params={'env': env_name},
            headers=headers
        )
        if response.status_code == 200:
            print(f"Environment '{env_name}' removed successfully.")
        else:
            msg = response.json().get('detail', 'Unknown error')
            print(f"Failed to remove environment '{env_name}': {msg}")

if __name__ == "__main__":
    main()



