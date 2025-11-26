from csbenchlab.csb_app_setup import get_app_registry_path
import os, json5, json, warnings, shutil
from pathlib import Path
from uuid import uuid4
from csbenchlab.plugin_helpers import import_module_from_path


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
                plugins[data["Library"]]["LibVersion"] = data["Version"]
    return plugins


def get_library_path(cls, lib_name):

    if cls.is_valid_component_library(lib_name):
        return lib_name

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
    return None


def is_supported_component_file(cls, component_file):
    supported_extensions = ['.py']
    ext = os.path.splitext(component_file)[1].lower()
    return ext in supported_extensions


def get_plugin_info_from_file(cls, component_file):
    import csbenchlab.registry as reg_plugins
    return reg_plugins.get_plugin_info_from_file(component_file)


def get_supported_component_types(cls):
    return ['ctl', 'sys', 'est', 'dist']

def get_plugin_info(cls, lib_name_or_path, component_name):
    if cls.is_valid_component_library(lib_name_or_path):
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
            path = cls.get_library_path(lib_name_or_path)  # You need to define this function accordingly
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
                info = cls.get_library_info(full_path, only_registered=True)
                libs.append({
                    "Name": info['Library'],
                    "Type": "install",
                    "Path": full_path,
                    "Version": info['Version']
                })
        elif n.endswith('.json'):
            with open(full_path, 'r') as f:
                s = json.load(f)
                lib = s['Path']
                if os.path.isdir(lib) and cls.is_valid_component_library(lib):
                    info = cls.get_library_info(lib, only_registered=True)
                    libs.append({
                        "Name": info['Library'],
                        "Type": "link",
                        "Path": lib,
                        "Version": info['Version']
                    })
    return libs

def refresh_component_library(cls, lib_name):
    path = cls.get_library_path(lib_name)
    if not cls.is_valid_component_library(path):
        raise ValueError(f"Library '{lib_name}' is not a valid library")

    with open(os.path.join(path, 'package.json'), 'r') as f:
        info = json5.load(f)
    with open(os.path.join(path, 'plugins.json'), 'r') as f:
        plugins = json5.load(f)

    manifest = {
        'Library': info['Library'],
        'Registry': {},
        'Version': info['Version']
    }

    for plugin in plugins.get('Plugins', []):
        comp_path = os.path.join(path, plugin['Path'])
        if not os.path.isfile(comp_path):
            warnings.warn(f"Component file '{comp_path}' not found. Skipping.")
            continue
        if not cls.is_supported_component_file(comp_path):
            warnings.warn(f"Component file '{comp_path}' is not a supported component file. Skipping.")
            continue
        comp_info = cls.get_plugin_info_from_file(comp_path)
        comp_type = comp_info.get('T', 'unknown')
        if comp_type not in manifest['Registry']:
            manifest['Registry'][comp_type] = []
        manifest['Registry'][comp_type].append(comp_info)
    manifest_file = os.path.join(path, 'autogen', 'manifest.json')
    with open(manifest_file, 'w') as f:
        json.dump(manifest, f, indent=4)

def register_component_library(cls, path, link_register=False, ask_dialog=True):
    # copy files if not link register
    reg_path = get_app_registry_path()
    lib_path = Path(path).resolve()
    dest_path = Path(reg_path) / lib_path.name

    if not link_register:
        if dest_path.exists():
            raise FileExistsError(f"Library '{lib_path.name}' already exists in registry")
        shutil.copytree(lib_path, dest_path)
        lib_path = dest_path
    else:
        # Just create a JSON file pointing to the library path
        json_path = dest_path.with_suffix('.json')
        info = cls.get_library_info(lib_path, only_registered=False)
        if json_path.exists():
            raise FileExistsError(f"Library '{lib_path.name}' already exists in registry")
        with open(json_path, 'w') as f:
            json.dump({
                'Path': str(lib_path),
                'Version': info.get('Version', '0.0.1')
            }, f, indent=4)

    autogen_path = lib_path / 'autogen'
    if autogen_path.exists():
        shutil.rmtree(autogen_path)
    os.makedirs(autogen_path)

    cls.refresh_component_library(lib_path.name)

    return str(lib_path)

def get_or_create_component_library(cls, lib_name, close_after_creation=False):
    path = cls.get_library_path(lib_name)  # Define or import accordingly
    if path is not None:
        return {
            'path': path,
            'name': lib_name
        }

    # create new library
    path = os.path.join(get_app_registry_path(), lib_name)
    if not os.path.exists(path):
        os.makedirs(path)

    autogen_folder = os.path.join(path, 'autogen')
    if not os.path.exists(autogen_folder):
        os.makedirs(autogen_folder)

    # Create src and library folders
    os.makedirs(os.path.join(path, 'src'), exist_ok=True)
    os.makedirs(os.path.join(path, lib_name), exist_ok=True)

    lib_meta = {
        'Library': lib_name,
        'Id': str(uuid4()),
        'Version': "0.0.1",
        'Dependencies': [],
        'Install': []
    }


    manifest = {
        'Library': lib_name,
        'Registry': {},  # Initially empty
        'Version': "0.0.1"
    }

    plugins_txt = plugins_template__.replace('{{library_name}}', lib_name)
    with open(os.path.join(path, 'plugins.json'), 'w') as f:
        f.write(plugins_txt)

    # Save registry (adapt to Python format, here using JSON as placeholder)
    with open(os.path.join(path, 'autogen', 'manifest.json'), 'w') as f:
        json.dump(manifest, f)

    # Save lib_meta to package.json
    with open(os.path.join(path, 'package.json'), 'w') as f:
        json.dump(lib_meta, f, indent=4)

    handle = {}
    handle['path'] = path
    handle['name'] = lib_name

    return handle


def remove_component_library(cls, lib_name):
    reg = get_app_registry_path()
    lib_folder = os.path.join(reg, lib_name)
    lib_json = os.path.join(reg, f"{lib_name}.json")
    if os.path.isdir(lib_folder):
        shutil.rmtree(lib_folder)
        return lib_folder
    elif os.path.isfile(lib_json):
        os.remove(lib_json)
        return lib_json
    else:
        raise FileNotFoundError(f"Library '{lib_name}' not found in registry")

def register_component_from_file(cls, component_file, lib_name):
    info = cls.get_plugin_info_from_file(component_file)
    cls.register_component(info, lib_name)

def register_component(cls, info, lib_name, append_to_json=True, append_to_manifest=True):

    lib_path = cls.get_library_path(lib_name)
    if not cls.is_valid_component_library(lib_path):
        raise ValueError(f"Library '{lib_name}' is not a valid library")

    if append_to_json:
        plugins_file = os.path.join(lib_path, 'plugins.json')
        with open(plugins_file, 'r') as f:
            plugins_data = json5.load(f)
        if 'Plugins' not in plugins_data:
            plugins_data['Plugins'] = []

        # Check for existing component with same name
        for comp in plugins_data['Plugins']:
            if comp['Name'] == info['Name']:
                warnings.warn(f"Component '{info['Name']}' already exists in library '{lib_name}'. Overwriting.")
                plugins_data['Plugins'].remove(comp)
                break

        rel_path = os.path.relpath(info['ComponentPath'], lib_path)
        if rel_path.startswith('/'):
            rel_path = rel_path[1:]
        plugins_data['Plugins'].append({
            "Name": info['Name'],
            "Path": rel_path,
            "Type": "file"
        })
        info["Lib"] = lib_name
        with open(plugins_file, 'w') as f:
            json.dump(plugins_data, f, indent=4)


    if append_to_manifest:
        manifest_file = os.path.join(lib_path, 'autogen', 'manifest.json')
        with open(manifest_file, 'r') as f:
            manifest_data = json5.load(f)

        comp_type = info.get('T', 'unknown')
        if comp_type not in manifest_data['Registry']:
            manifest_data['Registry'][comp_type] = []

        # Check for existing component with same name
        for comp in manifest_data['Registry'][comp_type]:
            if comp['Name'] == info['Name']:
                warnings.warn(f"Component '{info['Name']}' already exists in library '{lib_name}'. Overwriting.")
                manifest_data['Registry'][comp_type].remove(comp)
                break

        manifest_data['Registry'][comp_type].append(info)

        with open(manifest_file, 'w') as f:
            json.dump(manifest_data, f, indent=4)


def unregister_component(cls, component_name, lib_name):

    lib_path = cls.get_library_path(lib_name)
    if not cls.is_valid_component_library(lib_path):
        raise ValueError(f"Library '{lib_name}' is not a valid library")
    manifest_file = os.path.join(lib_path, 'autogen', 'manifest.json')
    with open(manifest_file, 'r') as f:
        manifest_data = json5.load(f)
    found = False
    for comp_type, comps in manifest_data['Registry'].items():
        for comp in comps:
            if comp['Name'] == component_name:
                comps.remove(comp)
                found = True
                break
        if found:
            break
    if not found:
        raise ValueError(f"Component '{component_name}' not found in library '{lib_name}'")
    with open(manifest_file, 'w') as f:
        json.dump(manifest_data, f, indent=4)

    plugins_file = os.path.join(lib_path, 'plugins.json')
    with open(plugins_file, 'r') as f:
        plugins_data = json5.load(f)
    found = False
    for comp in plugins_data['Plugins']:
        if comp['Name'] == component_name:
            plugins_data['Plugins'].remove(comp)
            found = True
            break
    if not found:
        raise ValueError(f"Component '{component_name}' not found in library '{lib_name}'")
    with open(plugins_file, 'w') as f:
        json.dump(plugins_data, f, indent=4)


def make_component_registry_from_plugin_description(cls, plugin_path, lib_name, save_manifest_library_path=None):


    plugin_desc_path = os.path.join(plugin_path, "plugins.json")
    if not plugin_desc_path.endswith(".json"):
        raise ValueError(f"Error parsing json. {plugin_desc_path} is not a json file.")
    try:
        with open(plugin_desc_path, 'r') as f:
            pd = json5.load(f)
    except Exception as e:
        print("Error parsing library package.json")
        raise e

    plugin_package_path = os.path.join(plugin_path, "package.json")
    if not plugin_package_path.endswith(".json"):
        raise ValueError(f"Error parsing json. '{plugin_package_path}' is not a json file.")
    try:
        with open(plugin_package_path, 'r') as f:
            pkg = json5.load(f)
    except Exception as e:
        print("Error parsing library package.json")
        raise e

    lib_path = os.path.dirname(plugin_desc_path)
    registry = {z : [] for z in cls.get_supported_component_types()}
    for p in pd.get('Plugins', []):
        if p['Type'] == 'folder_scan':
            scan_folder = os.path.join(lib_path, p['Path'])
            if not os.path.isdir(scan_folder):
                warnings.warn(f"Plugin folder '{scan_folder} does not exist. Skipping...")
                continue
            registry = cls.detect_components_from_path(scan_folder, registry)
        elif p['Type'] == 'file':
            comp_path = os.path.join(lib_path, p['Path'])
            registry = cls.detect_component(comp_path, registry)

    def append_lib_name_to_registry(registry, lib_name, version):
        for comps in registry.values():
            for comp in comps:
                comp['Lib'] = lib_name
                comp['LibVersion'] = version
        return registry

    append_lib_name_to_registry(registry, lib_name, pkg['Version'])

    if save_manifest_library_path is not None:
        manifest = {
            'Registry': registry,
            'Library': pkg['Library'],
            'Version': pkg['Version']
        }
        dir_name = os.path.dirname(save_manifest_library_path)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name, exist_ok=True)
        with open(os.path.join(save_manifest_library_path, 'manifest.json'), 'w') as f:
            json.dump(manifest, f, indent=4)

    return registry

def detect_components_from_path(cls, path, registry=None):
    if registry is None:
        registry = {z : [] for z in cls.get_supported_component_types()}
    for root, dirs, files in os.walk(path):
        for file in files:
            comp_path = os.path.join(root, file)
            registry = cls.detect_component(comp_path, registry)
    return registry

def detect_component(cls, component_file, registry=None):
    if registry is None:
        registry = {z : [] for z in cls.get_supported_component_types()}
    if not os.path.isfile(component_file):
        raise FileNotFoundError(f"Component file '{component_file}' not found.")
    if not cls.is_supported_component_file(component_file):
        warnings.warn(f"Component file '{component_file}' is not a supported component file. Skipping.")
        return registry
    comp_info = cls.get_plugin_info_from_file(component_file)
    comp_type = comp_info.get('T', 'unknown')
    if comp_type not in registry:
        registry[comp_type] = []
    registry[comp_type].append(comp_info)
    return registry


def get_plugin_info_from_lib(cls, component_name, lib_name_or_path):
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

def setup_library(cls, lib_name_or_path):
    pass

plugins_template__ = """
{
    "Library": "{{library_name}}",
    "Plugins": [
        // list your plugins here as json objects
	    // specify the type of each to eather 'folder_scan' or 'file'
    ]
}
"""

__all__ = ['get_library_path',
           'get_library_info',
           'is_valid_component_library',
           'list_component_libraries',
           'get_plugin_info',
           'get_plugin_info_from_file',
           'get_plugin_info_from_lib',
           'is_supported_component_file',
           'get_available_plugins',
           'get_supported_component_types',
           'register_component_library',
           'get_or_create_component_library',
           'remove_component_library',
           'refresh_component_library',
           'register_component_from_file',
           'register_component',
           'unregister_component',
           'make_component_registry_from_plugin_description',
           'detect_components_from_path',
           'detect_component',
           'setup_library'
]