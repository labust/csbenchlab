from csbenchlab.csb_app_setup import get_app_registry_path
import os, json5, json, warnings, shutil


def get_available_plugins(cls):
    reg = get_app_registry_path()
    fs = os.listdir(reg)
    plugins = {}
    for n in fs:
        # Skip '.' '..' 'slprj'
        if n in ['.', '..', 'slprj']:
            continue
        full_path = os.path.join(reg, n)
        if os.path.isdir(full_path):
            manifest_file = os.path.join(full_path, 'autogen', 'manifest.json')
        elif n.endswith('.json'):
            with open(full_path, 'r') as f:
                s = json5.load(f)
                lib = s['Path']
                manifest_file = os.path.join(lib, 'autogen', 'manifest.json')
        if os.path.isfile(manifest_file):
            with open(manifest_file, 'r') as f:
                data = json5.load(f)
                plugins[data["Library"]] = data["Registry"]
    return plugins


def get_library_path(cls, lib_name):
    reg = get_app_registry_path()
    fs = os.listdir(reg)

    for n in fs:
        # Skip '.' '..' 'slprj' or non-matching names
        if n in ['.', '..', 'slprj']:
            continue
        if not (n == lib_name or n == f"{lib_name}.json"):
            continue

        full_path = os.path.join(reg, n)
        if os.path.isdir(full_path):
            return full_path
        elif n.endswith('.json'):
            with open(full_path, 'r') as f:
                s = json5.load(f)
                lib = s['Path']
                return lib
    raise FileNotFoundError(f"Library '{lib_name}' not found")


def get_plugin_info(cls, lib_name_or_path, component_name):
    if os.path.isdir(lib_name_or_path):
        lib_path = lib_name_or_path
    else:
        lib_path = cls.get_library_path(lib_name_or_path)

    manifest_file = os.path.join(lib_path, 'autogen', 'manifest.json')
    if not os.path.isfile(manifest_file):
        raise ValueError(f"Library at '{lib_path}' does not contain a valid manifest.json file")

    with open(manifest_file, 'r') as f:
        plugins = json5.load(f)
    registry = plugins.get('Registry', {})
    for comp_type, comps in registry.items():
        for comp in comps:
            if comp['Name'] == component_name:
                return comp

def get_library_info(cls, lib_name_or_path, only_registered=True):
    if only_registered:
        if cls.is_valid_component_library(lib_name_or_path):
            path = lib_name_or_path
        else:
            path = get_library_path(lib_name_or_path)  # You need to define this function accordingly
        if not os.path.isdir(lib_name_or_path) and not os.path.isdir(path):
            raise ValueError(f"Library '{lib_name_or_path}' is not a valid library")
        with open(os.path.join(path, 'package.json'), 'r') as f:
            info = json5.load(f)
    else:
        if cls.is_valid_component_library(lib_name_or_path):  # You need to define this function accordingly
            with open(os.path.join(lib_name_or_path, 'package.json'), 'r') as f:
                info = json5.load(f)
        else:
            raise ValueError(f"Path '{lib_name_or_path}' is not a valid library")
    return info


def is_valid_component_library(cls, path):
    return os.path.isfile(os.path.join(path, 'package.json')) and \
           os.path.isfile(os.path.join(path, 'plugins.json'))


def list_component_libraries(cls, ignore_csbenchlab=True):
    libs = []
    reg = get_app_registry_path()
    fs = os.listdir(reg)

    for n in fs:
        # Skip '.' '..' 'slprj'
        if n in ['.', '..', 'slprj']:
            continue
        full_path = os.path.join(reg, n)
        if os.path.isdir(full_path):
            if cls.is_valid_component_library(full_path):
                libs.append(full_path)
        elif n.endswith('.json'):
            with open(full_path, 'r') as f:
                s = json.load(f)
                lib = s['Path']
                if os.path.isdir(lib) and cls.is_valid_component_library(lib):
                    libs.append(lib)
    return libs

def refresh_component_library(cls, lib_name):
    path = get_library_path(lib_name)
    if not is_valid_component_library(path):
        raise ValueError(f"Library '{lib_name}' is not a valid library")
    raise NotImplementedError("Function refresh_component_library is not yet implemented")

def register_component_library(cls, path, link_register=False, ask_dialog=True):
    raise NotImplementedError("Function register_component_library is not yet implemented")


def get_or_create_component_library(cls, lib_name, close_after_creation=False):
    raise NotImplementedError("Function get_or_create_component_library is not yet implemented")
    def create_component_library(path, link_register):
        if path is None:
            dest_path = os.getcwd()
            name = os.path.basename(dest_path)
        else:
            path = path.rstrip(os.sep)
            dest_path = path
            name = os.path.basename(dest_path)

        if not os.path.exists(dest_path):
            os.makedirs(dest_path)
        autogen_folder = os.path.join(dest_path, 'autogen')
        if not os.path.exists(autogen_folder):
            os.makedirs(autogen_folder)

        syspath = f"{name}_sys"
        contpath = f"{name}_ctl"
        estpath = f"{name}_est"
        distpath = f"{name}_dist"

        handle = {}
        handle['path'] = dest_path
        handle['name'] = name

        # These functions need to be implemented or adapted to Python environment
        handle['sh'] = new_system(syspath, 'Library')
        save_system(handle['sh'], os.path.join(autogen_folder, syspath))
        handle['ch'] = new_system(contpath, 'Library')
        save_system(handle['ch'], os.path.join(autogen_folder, contpath))
        handle['eh'] = new_system(estpath, 'Library')
        save_system(handle['eh'], os.path.join(autogen_folder, estpath))
        handle['dh'] = new_system(distpath, 'Library')
        save_system(handle['dh'], os.path.join(autogen_folder, distpath))

        # Create src and library folders
        os.makedirs(os.path.join(dest_path, 'src'), exist_ok=True)
        os.makedirs(os.path.join(dest_path, name), exist_ok=True)

        comp_types = get_component_types()  # Implement accordingly
        registry = {ctype: [] for ctype in comp_types}

        lib_meta = {
            'Name': name,
            'Id': new_uuid(),  # Implement new_uuid() to generate unique IDs
            'Version': "0.0.1",
            'Dependencies': [],
            'Install': []
        }

        # Add paths to sys.path or equivalent if required

        # Save registry (adapt to Python format, here using JSON as placeholder)
        with open(os.path.join(handle['path'], 'autogen', 'manifest.json'), 'w') as f:
            json.dump(registry, f)

        # Save lib_meta to package.json
        with open(os.path.join(handle['path'], 'package.json'), 'w') as f:
            json.dump(lib_meta, f, indent=4)

        plugins_path = os.path.join(handle['path'], 'plugins.json')
        if not os.path.isfile(plugins_path):
            template_path = os.path.join(CSPath.get_app_template_path(), 'plugins_template.json')
            try:
                with open(template_path, 'r') as f:
                    content = f.read()
                replaced = content.replace('{{library_name}}', name)
                with open(plugins_path, 'w') as f:
                    f.write(replaced)
            except Exception as e:
                warnings.warn(f"Failed to create plugins.json: {e}")

        return handle


    try:
        path = get_library_path(lib_name)  # Define or import accordingly
    except Exception:
        path = os.path.join(get_app_registry_path(), lib_name)

    if not os.path.exists(path):
        os.makedirs(path)

    autogen_folder = os.path.join(path, 'autogen')
    autogen_created = False
    if not os.path.exists(autogen_folder):
        os.makedirs(autogen_folder)
        autogen_created = True

    handle = {}
    handle['path'] = path
    handle['name'] = lib_name

    if autogen_created:
        handle = create_component_library(path, 0)  # Define accordingly
    else:
        handle['sh'] = load_and_unlock_system(os.path.join(autogen_folder, lib_name + '_sys'))  # Define accordingly
        handle['ch'] = load_and_unlock_system(os.path.join(autogen_folder, lib_name + '_ctl'))
        handle['eh'] = load_and_unlock_system(os.path.join(autogen_folder, lib_name + '_est'))
        handle['dh'] = load_and_unlock_system(os.path.join(autogen_folder, lib_name + '_dist'))

    return handle




__all__ = ['get_library_path', 'get_library_info', 'is_valid_component_library', 'list_component_libraries', 'get_plugin_info', 'get_available_plugins', 'register_component_library', 'get_or_create_component_library']