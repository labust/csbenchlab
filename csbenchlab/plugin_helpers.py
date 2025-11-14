import os

def parse_plugin_type(plugin_class):
    """
    Parses the type of a plugin class to determine if it is a 'Controller', 'System', or else.

    Args:
        plugin_class (type): The class of the plugin to parse.
    """
    if any([base for base in plugin_class.__mro__ \
            if str(base) ==  "<class 'csbenchlab.plugin.DynSystem.DynSystem'>"]):
        return 'sys'
    if any([base for base in plugin_class.__mro__ \
            if str(base) ==  "<class 'csbenchlab.plugin.Controller.Controller'>"]):
        return 'ctl'
    if any([base for base in plugin_class.__mro__ \
            if str(base) ==  "<class 'csbenchlab.plugin.Estimator.Estimator'>"]):
        return 'est'
    if any([base for base in plugin_class.__mro__ \
            if str(base) ==  "<class 'csbenchlab.plugin.DisturbanceGenerator.DisturbanceGenerator'>"]):
        return 'dist'
    return ''

def import_module_from_path(module_path: str):
    """
    Imports a Python module from a given file path.

    Args:
        module_path (str): The file path to the Python module.

    Returns:
        module: The imported Python module.

    Raises:
        ValueError: If the module cannot be found or loaded.
    """
    import importlib.util
    import os
    if not os.path.exists(module_path):
        raise ValueError(f"Module path '{module_path}' does not exist.")
    module_name = os.path.splitext(os.path.basename(module_path))[0]
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None:
        raise ValueError(f"Could not find module '{module_name}' at path '{module_path}'.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def get_plugin_class(plugin_path: str) -> dict:
    """
    Retrieves information about a plugin by its name.

    Args:
        plugin_path (str): The name of the plugin to retrieve information for.

    Returns:
        dict: A dictionary containing the plugin's information, including its name,
              description, and parameters.

    Raises:
        ValueError: If the plugin does not exist or if the plugin name is invalid.
    """
    if not os.path.exists(plugin_path):
        raise ValueError(f"Plugin path '{plugin_path}' does not exist.")

    plugin_name = os.path.splitext(os.path.basename(plugin_path))[0]
    plugin_module = import_module_from_path(plugin_path)
    if not hasattr(plugin_module, plugin_name):
        raise ValueError(f"Plugin '{plugin_name}' does not have a 'Plugin' class.")
    return getattr(plugin_module, plugin_name)