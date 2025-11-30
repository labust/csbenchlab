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
from csbenchlab.common_types import ScenarioOptions



def parse_scenario(sc:ScenarioOptions, scenario_id, env_path, ref_to_file) -> dict:

    data = sc.data
    if ref_to_file:
        ref_path = save_reference(env_path, scenario_id, data["Reference"])
        data["Reference"] = ref_path
    if isinstance(data["SystemIc"], np.ndarray):
        data["SystemIc"] = list(data["SystemIc"])

    return data


def eval_function(func, *args):
    if hasattr(func, 'external_function__'):
        return {
            "external_function__": True,
            "function": func.external_function__,
            "backend": func.external_backend__,
            "kwargs": getattr(func, 'external_kwargs__', { }),
        }
    else:
        return func(*args)


def eval_scenario_description(env_path, scenario, env_data, ref_to_file):
    scenario_path = Path(env_path) / 'parts' / 'scenarios' / scenario['Id']
    if not scenario_path.exists():
        raise ValueError(f"Scenario path '{scenario_path}' does not exist for scenario '{scenario['Id']}'")
    scenario_file = scenario_path / 'scenario.py'

    scenario_module = import_module_from_path(scenario_file) if scenario_file.exists() else None
    if scenario_module is None or not hasattr(scenario_module, 'scenario'):
        raise ValueError(f"'scenario' function not defined in '{scenario_file}' for scenario '{scenario['Id']}'")

    try:
        scenario_eval = eval_function(scenario_module.scenario, scenario, env_data['dt'], env_data['system_dims'])
    except Exception as e:
        raise ValueError(f"Error evaluating 'scenario'" + \
                         f" function in '{scenario_file}' for scenario '{scenario['Id']}'" + f": {e}")

    return parse_scenario(scenario_eval, scenario["Id"], env_path, ref_to_file)


def save_reference(env_path, scenario_id, reference):
    ref_path = Path(env_path) / 'data' / 'references' / f"{scenario_id}_ref.mat"
    if not ref_path.exists():
        os.makedirs(ref_path.parent, exist_ok=True)
    sio.savemat(ref_path, {'data': reference.T})
    return str(ref_path)


def eval_scenario_descriptions(env_path, env_data_or_path, ref_to_file=False):

    env_manager = EnvironmentDataManager(env_path)
    scenarios = env_manager.get_components('scenario')

    if isinstance(env_data_or_path, str):
        with open(env_data_path, 'r') as f:
            env_data = json5.load(f)
    else:
        env_data = env_data_or_path

    data = []
    for scenario in scenarios:
        options = eval_scenario_description(env_path, scenario, env_data, ref_to_file)
        data.append(options)

    return data



if __name__ == "__main__":


    parser = ArgumentParser(description="Get information about a specific plugin.")
    parser.add_argument("--env-path", type=str, default="", help="Path to the environment directory.")
    parser.add_argument("--env-data-path", type=str, default="", help="Path to the environment data json file.")
    args = parser.parse_args()
    env_path = args.env_path
    if not env_path or not os.path.exists(env_path):
        raise ValueError(f"Environment path '{env_path}' does not exist.")

    env_data_path = args.env_data_path
    if not env_data_path or not os.path.exists(env_data_path):
        raise ValueError(f"Environment data path '{env_data_path}' does not exist.")

    result = json.dumps(eval_scenario_descriptions(env_path, env_data_path, ref_to_file=True))

    eval