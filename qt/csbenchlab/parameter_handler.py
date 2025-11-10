from pathlib import Path
import os
import importlib.util
import numpy as np
from types import FunctionType
from qt.qt_utils import open_file_in_editor
from csbenchlab.data_desc import COMPONENT_DATA_DESC, get_component_relative_param_file_path
import sys

class ParameterHandler:

    def __init__(self, comp_path):
        self.component_destination_path = comp_path

    def open_parameter_file(self, component):
        # open parameter file in default editor
        path = self.get_component_param_file_path(component)
        if path is not None and path.exists():
            open_file_in_editor(path)

    def duplicate_component_params(self, component, new_id, new_path):
        if 'Id' not in component:
            raise ValueError("Component must have 'Id' fields")
        path = self.get_component_param_file_path(component)
        if path is None:
            return None

        if path.exists():
            with open(path, 'r') as f:
                src = f.read()
                src = src.replace(component["Id"], new_id)
            if not new_path.parent.exists():
                new_path.parent.mkdir(parents=True, exist_ok=True)
            with open(new_path, 'w') as f:
                f.write(src)
            return str(new_path)
        return None

    def load_py_component_params(self, component, path):
        if 'Id' not in component:
            raise ValueError("Component must have 'Id' fields")

        class_name = component['PluginName']
        if not path.endswith('.py'):
            path = f"{path}.py"
        sys.path.append(str(Path(path).parent.parent))
        spec = importlib.util.spec_from_file_location(class_name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if hasattr(module, class_name):
            cls = getattr(module, class_name)
            return cls.param_description
        return []

    def has_component_params(self, component):
        path = self.get_component_param_file_path(component)
        return path is not None and path.exists()

    def remove_component_params(self, component):
        path = self.get_component_param_file_path(component)
        if path is not None and path.exists():
            os.remove(path)

    def get_component_param_file_path(self, component) -> Path:
        full_file = Path(self.component_destination_path) / component["Id"] / get_component_relative_param_file_path(component)
        return full_file

    def set_component_params(self, component, params):
        if 'Id' not in component:
            raise ValueError("Component must have 'Id' fields")

        path = self.get_component_param_file_path(component)

        if Path(path).parent is None or not Path(path).parent.exists():
            Path(path).parent.mkdir(parents=True, exist_ok=True)

        src = self.make_python_params_file_src(params, component)
        with open(path, 'w') as f:
            f.write(src)
        return str(path)

    def make_python_params_file_src(self, params, component):
        src = """
from dataclasses import dataclass, field
from typing import List, Dict, Any
from csbenchlab.common_types import *
import numpy as np

# Parameter file for component with id {}


@dataclass
class ComponentParams:
{}
"""

        def is_special_string(value):
            return isinstance(value, str) and (value.startswith('csb_m_fh') or value.startswith('csb_path:'))

        if isinstance(params, list):
            params = {value["Name"]: value["DefaultValue"] for value in params}

        fields = []
        rest_keys = []
        for key, value in params.items():

            if isinstance(value, bool):
                fields.append(f"{key}: bool = {value}")
            elif isinstance(value, int):
                fields.append(f"{key}: int = {value}")
            elif isinstance(value, float):
                fields.append(f"{key}: float = {value}")
            elif isinstance(value, str) and not is_special_string(value):
                fields.append(f"{key}: str = '{value}'")
            elif value is None:
                fields.append(f"{key}: Any = None")
            elif isinstance(value, np.ndarray):
                fields.append(f"{key}: np.ndarray = np.array({value.tolist()})")
            elif isinstance(value, list):
                if len(value) == 0:
                    fields.append(f"{key}: List[Any] = field(default_factory=list)")
                else:
                    elem_type = type(value[0]).__name__
                    fields.append(f"{key}: List[{elem_type}] = field(default_factory=lambda: {value})")
            elif isinstance(value, dict):
                fields.append(f"{key}: Dict[str, Any] = field(default_factory=lambda: {value})")
            else:
                rest_keys.append(key)
        for key, value in params.items():
            if isinstance(value, FunctionType):
                fields.append(f"{key}: PyFunctionHandle = None  ### EVALUATED FROM DEFAULT FUNCTION IF NONE")
            elif is_special_string(value):
                if value.startswith('csb_m_fh'):
                    fields.append(f"{key}: MatFunctionHandle = None  ### EVALUATED FROM DEFAULT FUNCTION IF NONE")
                elif value.startswith('csb_path:'):
                    fields.append(f"{key}: FilePath = '{value[len('csb_path:'):]}'  # Path")
            else:
                if key in rest_keys:
                    fields.append(f"# {key}: {type(value).__name__} = {repr(value)}  ### UNSUPPORTED TYPE, PLEASE EDIT MANUALLY")

        fields_str = "    " + "\n    ".join(fields)
        full_src = src.format(component.get('Id', ''), fields_str)
        return full_src
