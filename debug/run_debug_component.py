
from argparse import ArgumentParser
from csbenchlab.plugin_helpers import import_module_from_path
from pathlib import Path
import sys, os
from m_scripts.get_plugin_info import get_plugin_info_from_file
from csbenchlab.eval_parameters import eval_plugin_params
from types import SimpleNamespace
from csbenchlab.environment_data_manager import EnvironmentDataManager
from csbenchlab.backend.python_backend import PythonBackend

def debug_component(env_path, controller_name, mux):

    env_manager = EnvironmentDataManager(env_path)
    controllers = env_manager.load_environment_data().controllers

    controller = next((c for c in controllers if c['Name'] == controller_name), None)
    lib_name = controller['Lib']
    class_name = controller['PluginName']


    backend = PythonBackend()

    component_info = backend.get_plugin_info(lib_name, class_name)


    sys.path.append(str(Path(component_info['ComponentPath']).parent.parent))
    m = import_module_from_path(component_info['ComponentPath'])
    component_class = getattr(m, class_name)
    params = eval_plugin_params(env_path, controller)
    if hasattr(component_class, 'create_data_model'):
        # check if it is class method
        if hasattr(component_class.create_data_model, '__self__') \
            and component_class.create_data_model.__self__ == component_class:
            data = component_class.create_data_model(params, mux)
        else:
            raise ValueError("create_data_model must be a class method.")
    component_instance = component_class('Params', params, 'Data', data)
    component_instance.configure()
    if hasattr(component_instance, 'is_pure__') \
        and component_instance.is_pure__:
        for i in range(5000):
            print(f"Step {i}")
            [u, new_data] = component_instance.step(1, 0, 0.05, data)
            data = component_instance.update_data(new_data)
        print(u)
        pass
    else:
        for i in range(5000):
            print(f"Step {i}")
            u = component_instance.step(1, 0, 0.05)
    # component_instance.restart()


def main():

    parser = ArgumentParser(description="Component Debugger")
    parser.add_argument('--env-path', type=str, required=True, help="Path to the component to debug.")
    parser.add_argument('--name', type=str, required=True, help="Path to the component to debug.")
    parser.add_argument('--mux-inputs', type=int, required=True)
    parser.add_argument('--mux-outputs', type=int, required=True)



    args = parser.parse_args()

    mux = dict()
    mux["Inputs"] = args.mux_inputs
    mux["Outputs"] = args.mux_outputs
    debug_component(args.env_path, args.name, mux)




if __name__ == "__main__":
    main()