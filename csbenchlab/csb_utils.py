import json, os
from csbenchlab.csb_app_setup import get_appdata_dir

def load_app_config():
    path = os.path.join(get_appdata_dir(), 'app_config.json')
    cfg = {
        'envs': [],
        'active_backend': 'python'
    }
    if os.path.exists(path):
        with open(path, 'r') as f:
            try:
                cfg = json.load(f)
            except:
                pass
    return cfg


def instantiate_backend(backend_name, restart_daemon=False):
    if backend_name == 'matlab':
        from csb_matlab.matlab_backend import MatlabBackend
        if not MatlabBackend.is_available():
            return (None, "Matlab Engine for Python is not available or not configured properly.")
        backend = MatlabBackend(restart_daemon=restart_daemon)
        backend.start()
    elif backend_name == 'python':
        from backend.python_backend import PythonBackend
        backend = PythonBackend()
        backend.start()
    else:
        raise ValueError("Unknown backend")
    return (backend, "Backend instantiated successfully.")

def save_app_config(cfg):
    appdata_dir = get_appdata_dir()
    path = os.path.join(appdata_dir, 'app_config.json')
    if not os.path.exists(appdata_dir):
        os.makedirs(appdata_dir, exist_ok=True)
    with open(path, 'w') as f:
        json.dump(cfg, f)


def get_active_backend():
    cfg = load_app_config()
    backend = cfg.get('active_backend', 'python')
    return instantiate_backend(backend, restart_daemon=False)[0]