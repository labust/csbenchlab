import os
from pathlib import Path

LIB_PATH_OVERRIDE = None
CSB_PATH_OVERRIDE = None

_BACKEND = None
def get_backend():
    global _BACKEND
    if _BACKEND is None:
        from backend.python_backend import PythonBackend
        _BACKEND = PythonBackend()
    return _BACKEND

csb_path = os.getenv('CSB_PATH', None)
if csb_path is not None:
    CSB_PATH_OVERRIDE = csb_path

lib_path = os.getenv('CSB_LIB_PATH', None)
if lib_path is not None:
    LIB_PATH_OVERRIDE = lib_path

def get_appdata_dir():
    if CSB_PATH_OVERRIDE is not None:
        return CSB_PATH_OVERRIDE
    if os.name == 'nt':
        appdata = os.getenv('APPDATA')
        if appdata is None:
            appdata = os.path.expanduser('~\\AppData\\Roaming')
        path =  os.path.join(appdata, 'CSBenchLab')
    else:
        home = os.path.expanduser('~')
        path = os.path.join(home, '.csbenchlab')

    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
    return path

def get_app_registry_path():
    if LIB_PATH_OVERRIDE is not None:
        return LIB_PATH_OVERRIDE
    return os.path.join(get_appdata_dir(), 'registry')

