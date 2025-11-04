import sys, os
file_name = sys.argv[0]
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(file_name))))
from pathlib import Path
from argparse import ArgumentParser
from csbenchlab.plugin_helpers import get_plugin_class

def get_plugin_class_attr(plugin_path: str, attr_name, callable_args=None) -> dict:

    sys.path.append(str(Path(plugin_path).parent.parent))

    plugin_class = get_plugin_class(plugin_path)
    # check if plugin has abstract class 'Plugin' implemented
    attr = getattr(plugin_class, attr_name, None)
    if callable(attr):
        return attr(*callable_args) if callable_args else attr()
    return attr

if __name__ == "__main__":

    parser = ArgumentParser(description="Get information about a specific plugin.")
    parser.add_argument("--plugin_path", type=str, default="", help="Path to the plugin directory or module.")
    parser.add_argument("--attr_name", type=str, default="", help="Path to the plugin directory or module.")
    args = parser.parse_args()
    plugin_path = args.plugin_path
    attr_name = args.attr_name
    if not plugin_path.endswith('.py'):
        plugin_path = plugin_path + '.py'

    # Check if the plugin path is valid
    if not os.path.exists(plugin_path):
        raise ValueError(f"Plugin path '{plugin_path}' does not exist.")

    if not attr_name:
        raise ValueError(f"Attribute name not provided")

    try:
        attr = get_plugin_class_attr(plugin_path, attr_name)
        a = 5
    except ValueError as e:
        print(e)


