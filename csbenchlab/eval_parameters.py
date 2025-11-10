from csbenchlab.env_iterators import  iterate_environment_components_with_subcomponents
from csbenchlab.data_desc import get_component_param_file_path
from csbenchlab.plugin_helpers import import_module_from_path
from pathlib import Path
from types import SimpleNamespace
import warnings

__cache_results = {}

def clear_cache_():
    __cache_results.clear()


def handle_callable_value_(value, info, params, plugin_class=None):
    if value is None:
        if info["DefaultValue"] == "csb_py_fh":
            if plugin_class is None:
                raise ValueError("Plugin class must be provided to handle 'csb_py_fh' default value.")
            f = next((x for x in plugin_class.param_description if x['Name'] == info["Name"]), None)
            if f is None:
                raise ValueError(f"Plugin class in '{str(plugin_class)}' does not define parameter '{info['Name']}'.")
            return f['DefaultValue'](params)
        elif info["DefaultValue"] == "csb_m_fh":
            return "csb_m_eval_default"
        elif callable(info["DefaultValue"]):
            return info["DefaultValue"](params)
    return value

def load_param_description_class_from_file_(file_path, plugin_name):
    global __cache_results
    cache_key = file_path
    comp_class_module = import_module_from_path(file_path)
    if not hasattr(comp_class_module, plugin_name):
        raise ValueError(f"Plugin '{plugin_name}' does not have a '{plugin_name}' class.")
    comp_class = getattr(comp_class_module, plugin_name)
    if not hasattr(comp_class, 'param_description'):
        raise ValueError(f"Plugin class in '{file_path}' does not define 'param_description'.")
    __cache_results[cache_key] = comp_class
    return comp_class

def load_param_description_class_from_library_(plugin_name, lib_name):
    from csbenchlab.csb_app_setup import get_backend
    info = get_backend().get_plugin_info(lib_name, plugin_name)
    return load_param_description_class_from_file_(info["ComponentPath"], info["Name"])

def eval_plugin_params_from_file(param_file, param_desc, plugin_class=None, plugin_path=None) -> SimpleNamespace:
    """
    Evaluate plugin parameters from a parameter file based on the provided parameter description.
    Used for both Python and non-Python plugins.
    """
    result_params = SimpleNamespace()
    params_m = import_module_from_path(param_file)
    if not hasattr(params_m, 'ComponentParams'):
        raise ValueError(f"Plugin parameter file '{param_file}' does not define 'ComponentParams' class.")
    params_cls = getattr(params_m, 'ComponentParams')
    if hasattr(params_cls, 'load_from_file__') and params_cls.load_from_file__:
        result_params.csb_params_file__ = params_cls
        return result_params

    # if plugin path is provided, param_desc is ignored and overriden by the one from the plugin class
    if plugin_class is None:
        if plugin_path is None:
            raise ValueError("Either 'plugin_class' or 'plugin_path' must be provided.")
        if plugin_path.endswith('.py'):
            name = Path(plugin_path).stem
            plugin_class = load_param_description_class_from_file_(plugin_path, name)
            if plugin_class is None:
                raise ValueError("Failed to load plugin class from provided 'plugin_path'.")
            else:
                param_desc = getattr(plugin_class, 'param_description')

    if isinstance(param_desc, dict):
        param_desc = [param_desc]

    for info in param_desc:
        if hasattr(params_cls, info['Name']):
            value = getattr(params_cls, info['Name'])
            value = handle_callable_value_(value, info, result_params, plugin_class)
        else:
            raise ValueError(f"Parameter '{info['Name']}' not found in 'ComponentParams' class.")
        setattr(result_params, info['Name'], value)
    return result_params

def eval_plugin_params_(env_path, component):
    path = Path(env_path) / get_component_param_file_path(component)
    if not path.exists():
        return None
    plugin_class = load_param_description_class_from_library_(component["PluginName"], component["Lib"])
    param_desc = getattr(plugin_class, 'param_description')
    return eval_plugin_params_from_file(param_file=str(path), param_desc=param_desc, plugin_class=plugin_class)

def eval_environment_params(env_path, env_info=None):
    """
    Evaluate parameters for all components in the environment located at 'env_path'.
    Used only for Python plugins.
    """
    ret = {}
    clear_cache_()
    for comp in iterate_environment_components_with_subcomponents(env_info):
        p_type = comp.get("PluginImplementation", None)
        if p_type == "slx" or p_type == "mat":
            warnings.warn(f"Skipping parameter evaluation for component '{comp['Id']}' with unsupported type '{p_type}'.")
            continue
        ret[comp["Id"]] = eval_plugin_params_(env_path, comp)
    return ret