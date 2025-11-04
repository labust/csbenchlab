import os

LIB_PATH_OVERRIDE = None

def get_appdata_dir():
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
    path = '/home/luka/matlab/csbenchlab'  # Debug override
    return path

def get_app_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_app_registry_path():
    if LIB_PATH_OVERRIDE is not None:
        return LIB_PATH_OVERRIDE
    return os.path.join(get_appdata_dir(), 'registry')

