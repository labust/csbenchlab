from pathlib import Path
import os
import json
# commands = {
#     'get_library_info': ("get_library_info('{}, {}')", 1),
#     'list_component_libraries': ("list_component_libraries()", 1),
#     'refresh_component_library': ("refresh_component_library('{}')", 0),
#     'register_component_library': ("register_component_library('{}', {})", 0),
#     'get_or_create_component_library': ("get_or_create_component_library('{}', 1)", 0),
#     'remove_component_library': ("remove_component_library('{}')", 0),
#     'register_component': ("register_component({})", 0),
#     'unregister_component': ("unregister_component('{}')", 0),
#     'get_component_info': ("get_component_info('{}')", 1),
#     'get_available_plugins': ("get_available_plugins(); ", 'dict'),
#     'get_component_params': ("jsonify_component_param_description(ComponentManager.get('{}').get_component_params('{}', '{}'))", 1),
#     'get_plugin_info_from_lib': ("get_plugin_info_from_lib('{}', '{}')", 1),
#     "generate_environment": ("generate_control_environment('{}', '{}', {})", 0),
#     "create_environment": ("create_environment('{}', '{}')", 0),
# }


class PythonBackend:
    def __init__(self):
        self.csb_path = None

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
