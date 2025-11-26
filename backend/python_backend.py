from csbenchlab.csb_app_setup import get_appdata_dir, get_app_registry_path, get_app_root_path
import os
class PythonBackend:
    def __init__(self):
        self.csb_path = get_appdata_dir()

        if not os.path.exists(self.csb_path):
            os.makedirs(self.csb_path)

        registry_path = get_app_registry_path()
        if not os.path.exists(registry_path):
            os.makedirs(registry_path)


    @property
    def is_long_generation(self):
        return False

    @property
    def is_long_library_management(self):
        return False

    def start(self):
        registry_path = get_app_registry_path()
        init_f = os.path.join(registry_path, 'init_f')
        if os.path.exists(init_f):
            return
        self.init_csbenchlab()
        with open(init_f, 'w') as f:
            f.write("# Initialization file for CSB Python Backend\n")
        pass


    def init_csbenchlab(self):
        root = get_app_root_path()
        plugin_path = os.path.join(root, "plugins")
        registry_path = get_app_registry_path()
        handle = self.get_or_create_component_library('csbenchlab')
        registry = self.make_component_registry_from_plugin_description(plugin_path, \
            'csbenchlab', os.path.join(registry_path, 'csbenchlab', 'autogen'))

        types = self.get_supported_component_types()
        for name in registry:
            if name not in types:
                print(f"Warning: Found unknown component type '{name}'.")
                continue
            plugin_list = registry[name]
            for plugin in plugin_list:
                self.register_component(plugin, handle["name"], 1, 0)




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
