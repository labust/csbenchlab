import json, warnings
from csbenchlab.environment_data_manager import EnvironmentDataManager
from csbenchlab.eval_parameters import eval_environment_params

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






__all__ = ['generate_control_environment']