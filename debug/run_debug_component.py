
from argparse import ArgumentParser
from csbenchlab.plugin_helpers import import_module_from_path
from pathlib import Path
import sys, os
from m_scripts.get_plugin_info import get_plugin_info
from m_scripts.eval_plugin_parameters import eval_plugin_params
from csbenchlab.environment_data import load_env_controllers
from types import SimpleNamespace
from backend.python_backend import PythonBackend

def debug_component(env_path, controller_name, mux):

    contorllers = load_env_controllers(env_path)

    controller = next((c for c in contorllers if c['Name'] == controller_name), None)
    params_file = Path(env_path) / 'parts' / 'controllers' / controller["Id"] / 'params' / f"{controller['Id']}.py"
    lib_name = controller['Lib']
    class_name = controller['PluginName']


    backend = PythonBackend()

    component_info = backend.get_component_info(lib_name, class_name)


    sys.path.append(str(Path(component_info['ComponentPath']).parent.parent))
    m = import_module_from_path(component_info['ComponentPath'])
    component_class = getattr(m, class_name)
    params = eval_plugin_params(
        param_file=params_file,
        plugin_path=component_info['ComponentPath'],
        for_json=False
    )
    if hasattr(component_class, 'create_data_model'):
        # check if it is class method
        if hasattr(component_class.create_data_model, '__self__') \
            and component_class.create_data_model.__self__ == component_class:
            data = component_class.create_data_model(params, mux)
        else:
            raise ValueError("create_data_model must be a class method.")
    component_instance = component_class('Params', params, 'Data', data)

    component_instance.configure()
    for i in range(5000):
        print(f"Step {i}")
        u = component_instance.step(1, 0, 0.05)
    print(u)
    a = 5
    # component_instance.restart()


def main():

    parser = ArgumentParser(description="Component Debugger")
    parser.add_argument('--env-path', type=str, required=True, help="Path to the component to debug.")
    parser.add_argument('--name', type=str, required=True, help="Path to the component to debug.")
    parser.add_argument('--mux-inputs', type=int, required=True)
    parser.add_argument('--mux-outputs', type=int, required=True)

    lib_path = os.getenv('CSB_LIB_PATH', None)
    if lib_path is not None:
        import csbenchlab.csb_paths
        csbenchlab.csb_paths.LIB_PATH_OVERRIDE = lib_path



    args = parser.parse_args()

    mux = dict()
    mux["Inputs"] = args.mux_inputs
    mux["Outputs"] = args.mux_outputs
    debug_component(args.env_path, args.name, mux)




if __name__ == "__main__":
    main()