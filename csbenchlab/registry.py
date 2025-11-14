import os, sys
from pathlib import Path
from csbenchlab.plugin_helpers import parse_plugin_type, get_plugin_class


def is_casadi_component(plugin_class: type) -> bool:
    """
    Checks if the given plugin class is a Casadi-based component.

    Args:
        plugin_class (type): The class of the plugin to check.
    Returns:
        bool: True if the plugin is a Casadi-based component, False otherwise.
    """

    return hasattr(plugin_class, 'casadi_plugin__') \
        and getattr(plugin_class, 'casadi_plugin__') is True


def get_plugin_info_from_file(plugin_path: str) -> dict:
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
    sys.path.append(str(Path(plugin_path).parent.parent))
    plugin_class = get_plugin_class(plugin_path)


    plugin_name = plugin_class.__name__
    plugin_bases = [base for base in plugin_class.__mro__ \
            if str(base) == "<class 'csbenchlab.plugin.PluginBase.PluginBase'>"]
    if not plugin_bases:
        raise ValueError(f"Plugin '{plugin_name}' does not implement the abstract class 'PluginBase'.")
    plugin_info = {
        'Name': plugin_name,
        'T': parse_plugin_type(plugin_class),
        'HasParameters': hasattr(plugin_class, 'param_description') and plugin_class.param_description is not None,
        'Description': getattr(plugin_class, 'description', 'No description provided.'),
        'Parameters': getattr(plugin_class, 'param_description', None),
        'IsCasadi': is_casadi_component(plugin_class)
    }

    # check if plugin has abstract class 'Plugin' implemented
    return plugin_info


def parse_plugin(obj):
    from types import SimpleNamespace
    ret = SimpleNamespace()
    for attr in dir(obj):
        if attr.startswith('_'):
            continue
        setattr(ret, attr, getattr(obj, attr))

    return ret

def instantiate_plugin(plugin_path: str) -> dict:
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
    plugin_class = get_plugin_class(plugin_path)
    instance = parse_plugin(plugin_class('is_simulink', 1, 'Params', {}, 'Data', {}))

    # check if plugin has abstract class 'Plugin' implemented
    return instance