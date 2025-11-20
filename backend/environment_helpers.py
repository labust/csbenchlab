import json, warnings
from csbenchlab.environment_data_manager import EnvironmentDataManager
from csbenchlab.eval_parameters import eval_environment_params
import os
from pathlib import Path
from csbenchlab.scenario_templates.control_environment import ControlEnvironment

def generate_control_environment(cls, env_path, system_instance:str=None, controller_ids:str=None):

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
        controller_ids = []
    else:
        controller_ids = json.loads(controller_ids)
    data.controllers = [c for c in data.controllers if c["Id"] in controller_ids]
    filtered = [c for c in data.controllers if c["PluginImplementation"] == "py"]

    if len(filtered) != len(data.controllers):
        warnings.warn("Some controllers are not implemented in Python and will be ignored.")
    data.controllers = filtered

    if data.metadata["Ts"] <= 0:
        raise ValueError("Invalid sampling time 'Ts' in environment metadata.")

    name = data.metadata.get("Name", "GeneratedEnvironment")
    env_params = eval_environment_params(env_path, data)

    env = ControlEnvironment(name)
    env.generate({
        "system": data.systems[0],
        "controllers": data.controllers
    })



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


__all__ = ['generate_control_environment',
           'is_valid_environment_path',
           'setup_environment']