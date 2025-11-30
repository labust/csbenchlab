import os
from pathlib import Path

CSB_PATH_OVERRIDE = None

_BACKEND = None
def get_backend():
    global _BACKEND
    if _BACKEND is None:
        from csbenchlab.backend.python_backend import PythonBackend
        _BACKEND = PythonBackend()
    return _BACKEND

csb_path = os.getenv('CSB_PATH', None)
if csb_path is not None:
    CSB_PATH_OVERRIDE = csb_path


def get_app_root_path():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_appdata_dir():
    if CSB_PATH_OVERRIDE is not None:
        return CSB_PATH_OVERRIDE
    home = os.path.expanduser('~')
    path = os.path.join(home, '.csbenchlab')
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
    return path

def get_app_registry_path():
    return os.path.join(get_appdata_dir(), 'registry', 'python')

