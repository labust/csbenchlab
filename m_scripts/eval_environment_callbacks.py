import sys, os
file_name = sys.argv[0]
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(file_name))))

from argparse import ArgumentParser
from pathlib import Path
import json5, json
import numpy as np
from csbenchlab.environment_data_manager import EnvironmentDataManager
from csbenchlab.plugin_helpers import import_module_from_path
import scipy.io as sio
from csbenchlab.param_typing import MultiScenario


CALLBACKS = {
    'on_load': None,
    'on_start': None,
    'on_end': None,
}


def parse_callback(func):
    if hasattr(func, 'external_function__'):
        return json.dumps({
            "external_function__": True,
            "function": func.external_function__,
            "backend": func.external_backend__,
            "kwargs": getattr(func, 'external_kwargs__', { }),
        })
    else:
        return func


def eval_environment_callbacks(env_path):
    # iterate over env_path parts

    path = Path(env_path) / 'parts'
    callbacks = {}
    for part_dir in path.iterdir():
        if not part_dir.is_dir():
            continue
        component_dir = part_dir
        for id_dir in component_dir.iterdir():
            if not id_dir.is_dir():
                continue
            callbacks_file = id_dir / 'callbacks.py'
            if not callbacks_file.exists():
                continue
            callbacks_module = import_module_from_path(callbacks_file)
            id = id_dir.name
            for cb_name in CALLBACKS.keys():
                if hasattr(callbacks_module, cb_name):
                    callbacks[f"{cb_name}:{id}"] = parse_callback(getattr(callbacks_module, cb_name))
    return callbacks





if __name__ == "__main__":


    parser = ArgumentParser(description="Get information about a specific plugin.")
    parser.add_argument("--env-path", type=str, default="", help="Path to the environment directory.")
    args = parser.parse_args()
    env_path = args.env_path
    if not env_path or not os.path.exists(env_path):
        raise ValueError(f"Environment path '{env_path}' does not exist.")

    callbacks = eval_environment_callbacks(env_path)