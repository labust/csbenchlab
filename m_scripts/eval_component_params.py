import sys, os
file_name = sys.argv[0]
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(file_name))))
import json5, json
from argparse import ArgumentParser
from pathlib import Path
from csbenchlab.eval_parameters import eval_environment_params, eval_plugin_params_from_file
from csbenchlab.source_libraries import source_libraries
from csbenchlab.env_iterators import iterate_environment_components_with_subcomponents
from csbenchlab.common_types import LoadFromFile, MatEval, CompositeParams, CSPath
from csbenchlab.data_desc import get_component_param_file_path, get_component_context_path
import numpy as np


def parse_value_(value, comp_context_path):
    if isinstance(value, LoadFromFile):
        return value.as_string()  # Return the file path as is
    elif isinstance(value, MatEval):
        return value.as_string()
    elif isinstance(value, np.ndarray):
        return value.tolist()
    elif isinstance(value, CSPath):
        return str(comp_context_path / str(value))
    elif isinstance(value, CompositeParams):
        return {k: parse_value_(v, comp_context_path) for k, v in value.__dict__.items()}
    elif hasattr(value, "load_from_file__"):
        return value.as_string()
    return value

if __name__ == "__main__":

    parser = ArgumentParser(description="Get information about a specific plugin.")
    parser.add_argument("--env-path", type=str, default="", help="Path to the environment directory.")
    parser.add_argument("--lib-path", type=str, default="", help="Path to the library directory.")
    parser.add_argument("--component-info-path", type=str, default="", help="Path to the parameter description file.")
    parser.add_argument("--py-as-py", action="store_true", default=False, help="Output as Python.")
    args = parser.parse_args()

    os.environ['CSB_LIB_PATH'] = args.lib_path
    source_libraries()

    if not os.path.exists(args.env_path):
        raise ValueError(f"Environment path '{args.env_path}' does not exist.")

    if not os.path.exists(args.component_info_path):
        raise ValueError(f"Component information file '{args.component_info_path}' does not exist.")

    with open(args.component_info_path, 'r') as f:
        component_infos = json5.load(f)

    if isinstance(component_infos, dict):
        component_infos = [component_infos]

    res_params = {"py": [], "json": []}
    for info in component_infos:
        c = info["Comp"]
        comp_context_path = Path(args.env_path) / get_component_context_path(c)
        params_file = Path(args.env_path) / get_component_param_file_path(c)
        params = eval_plugin_params_from_file(params_file, info["Desc"], plugin_path=info.get("ComponentPath", None))
        if c["PluginImplementation"] == "py":
            res_params["py"].append({"Id": c["Id"], "Params": params})
        else:
            c_params = params.__dict__
            for k, v in c_params.items():
                c_params[k] = parse_value_(v, comp_context_path)
            res_params["json"].append({"Id": c["Id"], "Params": c_params})

    res_params["json"] = json.dumps(res_params["json"])
    params = res_params