import sys, os
file_name = sys.argv[0]
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(file_name))))

from argparse import ArgumentParser
from csbenchlab.registry import get_plugin_info

if __name__ == "__main__":


    parser = ArgumentParser(description="Get information about a specific plugin.")
    parser.add_argument("--plugin_path", type=str, default="", help="Path to the plugin directory or module.")
    args = parser.parse_args()
    plugin_path = args.plugin_path
    if not plugin_path.endswith('.py'):
        plugin_path = plugin_path + '.py'

    # Check if the plugin path is valid
    if not os.path.exists(plugin_path):
        raise ValueError(f"Plugin path '{plugin_path}' does not exist.")

    try:
        plugin_info = get_plugin_info(plugin_path)
    except ValueError as e:
        print(e)


