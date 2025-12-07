import json, warnings
from csbenchlab.environment_data_manager import EnvironmentDataManager
from csbenchlab.eval_parameters import eval_environment_params
import os
from pathlib import Path
from csbenchlab.scenario_templates.control_environment import ControlEnvironment
from uuid import uuid4

def load_control_environment_params_and_data(cls, env_path, system_instance:str=None, controller_ids:str=None):

    mgr = EnvironmentDataManager(env_path)
    data = mgr.load_environment_data()

    if system_instance is not None and system_instance != '':
        system = next((s for s in data.systems if s["Id"] == system_instance), None)
        if system is None:
            raise ValueError(f"System instance '{system_instance}' not found in environment.")
        data.systems = [system]
    elif len(data.systems) > 1:
        raise ValueError("Multiple system instances found. Please specify one to use.")

    if controller_ids is None or controller_ids == '':
        controller_ids = [c["Id"] for c in data.controllers]
    data.controllers = [c for c in data.controllers if c["Id"] in controller_ids]
    filtered = [c for c in data.controllers if c["PluginImplementation"] == "py"]

    if len(filtered) != len(data.controllers):
        warnings.warn("Some controllers are not implemented in Python and will be ignored.")
    data.controllers = filtered
    data.env_path = env_path

    if data.metadata["Ts"] <= 0:
        raise ValueError("Invalid sampling time 'Ts' in environment metadata.")

    env_params = eval_environment_params(env_path, data)

    return env_params, data

def generate_control_environment(cls, env_path, system_instance:str=None, controller_ids:str=None):
    from csb_qt.qt_utils import open_file_in_editor
    source = env_eval_file.format(env_path=env_path,
        system_instance=system_instance or "None",
        controller_ids=controller_ids or '"None"')
    name = cls.get_env_name(env_path)
    file_path = Path(env_path) / f"{name}.py"
    with open(file_path, 'w') as f:
        f.write(source)
    open_file_in_editor(file_path)

def create_environment(cls, base_path: str, env_name: str):
    """
    Creates a new control environment at the specified base path with the given environment name.

    Args:
        base_path (str): The base directory where the environment will be created.
        env_name (str): The name of the new environment.
    """
    env_path = os.path.join(base_path, env_name)
    if os.path.exists(env_path):
        raise ValueError(f"Environment path '{env_path}' already exists.")

    os.makedirs(env_path)
    name = env_name
    new_uuid = str(uuid4())
    os.makedirs(os.path.join(env_path, name))
    os.makedirs(os.path.join(env_path, 'parts'))
    with open(os.path.join(env_path, f"{name}.cse"), 'w') as f:
        f.write("")  # Create empty environment file

    cfg = {
        "Id": new_uuid,
        "Name": name,
        "Version": "0.1",
        "Ts": 0.0
    }
    with open(os.path.join(env_path, 'config.json'), 'w') as f:
        json.dump(cfg, f)

    cls.setup_environment(env_path)



def is_valid_environment_path(cls, path: str) -> bool:
    """
    Checks if the given path is a valid control environment.

    Args:
        path (str): The path to check.
    Returns:
        bool: True if the path is a valid control environment, False otherwise.
    """
    name = Path(path).stem
    return os.path.isdir(path) and \
        os.path.exists(os.path.join(path, f"{name}.cse"))



def setup_environment(cls, env_path: str):
    """
    Sets up the control environment located at the given path.

    Args:
        env_path (str): The path to the control environment.
    """

    pass


def get_env_name(cls, env_path: str):
    return Path(env_path).stem


def get_system_dims(cls, system_description: dict, params) -> dict:
    """
    Retrieves the input and output dimensions of the system described by the given description.

    Args:
        system_description (dict): The system description containing parameters.
    Returns:
        dict: A dictionary with 'Inputs' and 'Outputs' keys indicating the system dimensions.
    """
    from csbenchlab.plugin_helpers import import_module_from_path

    cls_name = system_description["PluginName"]
    info = cls.get_plugin_info_from_lib(system_description["PluginName"], system_description["Lib"])
    module_path = info["ComponentPath"]
    module = import_module_from_path(module_path)
    if not hasattr(module, cls_name):
        raise ValueError(f"Component class '{cls_name}' not found in module '{module_path}'.")
    comp_cls = getattr(module, cls_name)

    if not hasattr(comp_cls, 'get_dims_from_params'):
        raise ValueError(f"Component class '{cls_name}' does not implement 'get_dims_from_params' method.")

    dims = comp_cls.get_dims_from_params(params)
    return dims


__all__ = ['generate_control_environment',
           'create_environment',
           'is_valid_environment_path',
           'setup_environment',
           'get_system_dims',
           'get_env_name',
           'load_control_environment_params_and_data']




env_eval_file = """
from argparse import ArgumentParser
from csbenchlab.backend.python_backend import PythonBackend
from csbenchlab.scenario_templates.control_environment import ControlEnvironment
from m_scripts.eval_metrics import eval_metrics
from bdsim import BDSim
from matplotlib import pyplot as plt


def eval_control_environment(env_path, system_instance:str=None, controller_ids:str=None):
    backend = PythonBackend()
    env_params, data = backend.load_control_environment_params_and_data(env_path, system_instance, controller_ids)

    env = ControlEnvironment(env_path, data.metadata, backend=backend)

    env.generate({{
        "system": data.systems[0],
        "controllers": data.controllers
    }}, env_params=env_params, generate_scopes=False)

    scenario = env.select_scenario(0)
    env.compile()
    out = env.run(T=scenario["SimulationTime"])


    r = eval_metrics(data, out)
    plt.show()
    print(r)


def main():
    env_path = "{env_path}"
    system_instance = "{system_instance}"
    controller_ids = {controller_ids}
    eval_control_environment(env_path, system_instance, controller_ids)

if __name__ == "__main__":
    main()
"""