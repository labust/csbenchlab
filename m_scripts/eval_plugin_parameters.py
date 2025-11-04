import sys, os
file_name = sys.argv[0]
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(file_name))))
import json5, json
from argparse import ArgumentParser
from csbenchlab.plugin_helpers import import_module_from_path
from csbenchlab.param_typing import LoadFromFile, PyEval, MatEval
import numpy as np
from pathlib import Path
from types import SimpleNamespace

plugin_class = None

def handle_value(value, info, plugin_path, params):
    global plugin_class
    if isinstance(value, LoadFromFile):
        return value.as_string()  # Return the file path as is
    elif isinstance(value, PyEval):
        return value.eval()
    elif isinstance(value, MatEval):
        return value.as_string()
    elif value is None:
        if info["DefaultValue"] == "csb_py_fh":
            set_plugin_class_if_none(plugin_path=plugin_path)
            f = next((x for x in plugin_class.param_description if x['Name'] == info["Name"]), None)
            if f is None:
                raise ValueError(f"Plugin class in '{plugin_path}' does not define parameter '{info['Name']}'.")
            return f['DefaultValue'](params)
        elif info["DefaultValue"] == "csb_m_fh":
            return "csb_m_eval_default"
    elif isinstance(value, np.ndarray):
        return value.tolist()
    return value



def set_plugin_class_if_none(plugin_path: str):
    global plugin_class
    if plugin_class is not None:
        return plugin_class

    if not plugin_path or not os.path.exists(plugin_path):
        raise ValueError(f"Plugin path '{plugin_path}' does not exist.")

    if plugin_path.endswith('.py'):
        name = os.path.splitext(os.path.basename(plugin_path))[0]
        sys.path.append(str(Path(plugin_path).parent.parent))
        plugin_py_class = import_module_from_path(plugin_path)
        if not hasattr(plugin_py_class, name):
            raise ValueError(f"Plugin '{name}' does not have a '{name}' class.")
        plugin_class = getattr(plugin_py_class, name)
    else:
        plugin_class = None
    return plugin_class

def eval_plugin_params(param_file: str, plugin_path: str, plugin_desc_path: str=None, for_json=False) -> dict:

    global plugin_class

    result_params = SimpleNamespace()

    if plugin_desc_path is None:
        if not plugin_path.endswith('.py'):
            raise ValueError(f"Plugin path '{plugin_path}' is not a valid .py file.")
        set_plugin_class_if_none(plugin_path=plugin_path)
        if not hasattr(plugin_class, 'param_description'):
            raise ValueError(f"Plugin class in '{plugin_path}' does not define 'param_description'.")
        param_desc = getattr(plugin_class, 'param_description')
    else:
        with open(plugin_desc_path, 'r') as f:
            param_desc = json5.load(f)

    params_m = import_module_from_path(param_file)
    if not hasattr(params_m, 'ComponentParams'):
        raise ValueError(f"Plugin parameter file '{param_file}' does not define 'ComponentParams' class.")
    params_cls = getattr(params_m, 'ComponentParams')

    if hasattr(params_cls, 'load_from_file__') and params_cls.load_from_file__:
        v = params_cls.as_string()
        result_params.csb_params_file__ = v
        return result_params

    if isinstance(param_desc, dict):
        param_desc = [param_desc]

    for info in param_desc:
        if hasattr(params_cls, info['Name']):
            value = getattr(params_cls, info['Name'])
            if for_json:
                value = handle_value(value, info, plugin_path, result_params)
        else:
            raise ValueError(f"Parameter '{info['Name']}' not found in 'ComponentParams' class.")
        setattr(result_params, info['Name'], value)

    return result_params

if __name__ == "__main__":

    parser = ArgumentParser(description="Get information about a specific plugin.")
    parser.add_argument("--param-file", type=str, default="", help="Path to the plugin parameter file.")
    parser.add_argument("--plugin-path", type=str, default="", help="Path to the plugin implementation.")
    parser.add_argument("--plugin-desc-path", type=str, default="", help="Path to the plugin description file.")
    args = parser.parse_args()
    param_file = args.param_file
    plugin_desc_path = args.plugin_desc_path
    plugin_path = args.plugin_path
    if not param_file.endswith('.py'):
        param_file = param_file + '.py'

    for_json = True
    if Path(plugin_path).suffix == '':
        plugin_path = plugin_path + '.py'
        for_json = False

    # Check if the plugin path is valid
    if not os.path.exists(param_file):
        raise ValueError(f"Param path '{param_file}' does not exist.")

    if not plugin_desc_path or not os.path.exists(plugin_desc_path):
        raise ValueError(f"Plugin description path not provided")

    params = eval_plugin_params(param_file, plugin_path, plugin_desc_path=plugin_desc_path, for_json=for_json)
    if for_json:
        params = json.dumps(params.__dict__)


