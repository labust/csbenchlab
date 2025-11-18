from csbenchlab.csb_app_setup import get_appdata_dir
import os
class PythonBackend:
    def __init__(self):
        self.csb_path = get_appdata_dir()

        if not os.path.exists(self.csb_path):
            os.makedirs(self.csb_path)

        if not os.path.exists(os.path.join(self.csb_path, 'registry')):
            os.makedirs(os.path.join(self.csb_path, 'registry'))

    @property
    def is_long_generation(self):
        return False

    def start(self):
        pass

import backend.library_helpers as lib_helpers
for f in lib_helpers.__all__:
    if hasattr(PythonBackend, f):
        raise ValueError(f"Function '{f}' already exists in PythonBackend")
    setattr(PythonBackend, f, classmethod(getattr(lib_helpers, f)))

import backend.environment_helpers as env_helpers
for f in env_helpers.__all__:
    if hasattr(PythonBackend, f):
        raise ValueError(f"Function '{f}' already exists in PythonBackend")
    setattr(PythonBackend, f, classmethod(getattr(env_helpers, f)))
