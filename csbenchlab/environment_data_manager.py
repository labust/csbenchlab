import json5, json
from pathlib import Path
from types import SimpleNamespace
import shutil, os
from csbenchlab.data_desc import COMPONENT_DATA_DESC

from csbenchlab.parameter_handler import ParameterHandler
from csbenchlab.component_file_handler import ComponentFileHandler
from copy import deepcopy


class ComponentDataManager:

    def __init__(self, dest_folder_path, file_name=None, data_desc_class=None):
        self.path = dest_folder_path
        self.file_name = file_name
        self.is_file = Path(dest_folder_path).is_file()
        if self.is_file and not (file_name is None or file_name == ''):
            raise ValueError("If rel_path is a file, file_name must be None")
        if not self.is_file and file_name is None:
            self.file_name = "component.json"

        self.param_handler = ParameterHandler(self.path)
        self.file_handler = ComponentFileHandler(self.path, data_desc_class=data_desc_class)

    def load_all(self):
        all_data = []
        if not self.path.exists():
            return all_data
        if self.is_file:
            return self._fill_subcomponents(self._load_json_file(self.path))
        if self.path.exists() and self.path.is_dir():
            for item in self.path.iterdir():
                if not item.is_dir():
                    continue
                json_file = item / self.file_name
                if not json_file.exists():
                    continue
                data = self._fill_subcomponents(self._load_json_file(json_file))
                if isinstance(data, list):
                    all_data.extend(data)
                else:
                    all_data.append(data)
        return all_data

    def save_all(self, data):
        if self.is_file:
            self._save_subcomponents(data)
            self._save_json_file(self.path, data)
            return
        if not self.path.exists():
            self.path.mkdir(parents=True, exist_ok=True)

        # clear existing files
        for item in self.path.iterdir():
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()
        # save new data
        for comp in data:
            self.save_component(comp)

    def save_component(self, component):
        if self.is_file:
            self.save_all(component)
            return

        # create folder if not exists
        if not self.path.exists():
            self.path.mkdir(parents=True, exist_ok=True)
        if 'Id' not in component:
            raise ValueError("Component must have 'Id' field")
        comp_id = component['Id']
        comp_path = self.path / comp_id
        if not comp_path.exists():
            comp_path.mkdir(parents=True, exist_ok=True)
        component = self._save_subcomponents(component)
        self._save_json_file(comp_path / self.file_name, component)

    def remove_component(self, component_id):
        if self.is_file:
            path = self.path
            if path.exists():
                path.unlink()
            return
        path = self.path / component_id
        if path.exists() and path.is_dir():
            shutil.rmtree(path)

    def _load_json_file(self, file_path):
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        with open(file_path, 'r') as f:
            r = json5.load(f)
            return r

    def _save_json_file(self, file_path, data):
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)

    def _fill_subcomponents(self, component):
        if not isinstance(component, dict):
            return component
        subc_names = component.get("Subcomponents", [])
        for subc_name in subc_names:
            if subc_name not in component:
                component[subc_name] = {}
            else:
                comp_info = component[subc_name]
                if not comp_info:
                    continue

                if isinstance(comp_info, list):
                    res_list = []
                    for i, item in enumerate(comp_info):
                        res_list.append(self._load_value(component["Id"], item, subc_name))
                    component[subc_name] = res_list
                else:
                    component[subc_name] = self._load_value(component["Id"], comp_info, subc_name)
        return component

    def _save_subcomponents(self, component):
        component = deepcopy(component)
        if not isinstance(component, dict):
            return component
        subc_names = component.get("Subcomponents", [])
        for subc_name in subc_names:
            if subc_name in component:
                subc = component[subc_name]
                if not subc:
                    continue
                if isinstance(subc, list):
                    for i, item in enumerate(subc):
                        substitute_value = self._store_value(component["Id"], item, subc_name)
                        component[subc_name][i] = substitute_value
                else:
                    substitute_value = self._store_value(component["Id"], subc, subc_name)
                    component[subc_name] = substitute_value
        return component

    def _load_value(self, comp_id, item, subc_name):
        id = item.get("Id", None)
        component_type = item.get("ComponentType", None)
        if id is None or id == "" or component_type is None or component_type == "":
            raise Exception(f"Component should have 'ComponentType' field")
        ctype = COMPONENT_DATA_DESC[component_type]["destination_path"]
        return self._load_json_file(Path(self.path)
                / comp_id / 'subcomponents' / ctype / id / f"{subc_name}.json")

    def _store_value(self, comp_id, item, subc_name):

        id = item.get("Id", None)
        if id is None:
            raise ValueError(f"Subcomponent '{subc_name}' must have 'Id' field")
        component_type = item.get("ComponentType", "")
        if component_type == "":
            raise Exception(f"Component should have 'ComponentType' field")
        if COMPONENT_DATA_DESC[component_type]["standalone"]:
            raise ValueError(f"Cannot save subcomponent as it is standalone.")
        ctype = COMPONENT_DATA_DESC[component_type]["destination_path"]

        substutute_value = {"Id": id, "ComponentType": component_type, "DestinationPath": ctype}
        path = Path(self.path) / comp_id / 'subcomponents' / ctype / id
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
        self._save_json_file(path / f"{subc_name}.json", item)
        return substutute_value



class EnvironmentDataManager:

    def __init__(self, env_path):

        if not self.is_valid_env_path(env_path):
            raise ValueError(f"Invalid environment path: {env_path}")

        full_env_path = Path(env_path)
        self.standalone_comp_managers = {
            k: ComponentDataManager(full_env_path / v["destination_path"], v["data_file"], v.get("data_desc_class", None)) \
                for k, v in COMPONENT_DATA_DESC.items() if v.get("standalone", False)
        }
        self.subcomponent_managers = {}


    def get_or_create_component_data_manager(self, component):
        component_type = component.get("ComponentType", None)
        if component_type not in COMPONENT_DATA_DESC:
            raise ValueError(f"Unknown component type: {component_type}")
        if component_type in self.standalone_comp_managers:
            return self.standalone_comp_managers[component_type]
        else:
            parent_type = component.get("ParentComponentType", None)
            if parent_type not in self.standalone_comp_managers:
                raise ValueError(f"Unknown parent component type: {parent_type}")
            parent_id = component.get("ParentComponentId", None)
            if parent_id is None or parent_id == "":
                raise ValueError(f"Subcomponent must have 'ParentComponentId' field")
            subctl_path = Path(self.standalone_comp_managers[parent_type].path) / parent_id / 'subcomponents'
            if parent_id not in self.subcomponent_managers:
                desc = COMPONENT_DATA_DESC[component_type]
                rel_path = desc.get("destination_path", "")
                subctl_path = subctl_path / rel_path
                file_name = desc["data_file"]
                data_desc_class = desc.get("data_desc_class", None)
                self.subcomponent_managers[parent_id] = ComponentDataManager(subctl_path, file_name, data_desc_class)
            return self.subcomponent_managers[parent_id]


    def add_component(self, component):
        mgr = self.get_or_create_component_data_manager(component)
        mgr.save_component(component)

    def remove_component(self, component):
        mgr = self.get_or_create_component_data_manager(component)
        id = component.get("Id", None)
        mgr.remove_component(id)

    def get_components(self, component_type):
        if component_type in self.standalone_comp_managers:
            return self.standalone_comp_managers[component_type].load_all()
        else:
            raise ValueError(f"Unknown component type: {component_type}")


    def load_environment_data(self):
        data = SimpleNamespace()
        data.metadata = self.standalone_comp_managers['metadata'].load_all()
        data.controllers = self.standalone_comp_managers['controller'].load_all()
        data.systems = self.standalone_comp_managers['system'].load_all()
        data.metrics = self.standalone_comp_managers['metric'].load_all()
        data.scenarios = self.standalone_comp_managers['scenario'].load_all()
        self._create_subcomponent_data_managers(data)
        return data

    def save_environment_data(self, data):
        data = deepcopy(data)
        data = self._save_subcomponent_data(data)

        self.standalone_comp_managers['metadata'].save_all(data.metadata)
        self.standalone_comp_managers['system'].save_all(data.systems)
        self.standalone_comp_managers['controller'].save_all(data.controllers)
        self.standalone_comp_managers['scenario'].save_all(data.scenarios)
        self.standalone_comp_managers['metric'].save_all(data.metrics)


    def has_component_params(self, component):
        mgr = self.get_or_create_component_data_manager(component)
        return mgr.param_handler.has_component_params(component)

    def duplicate_component_params(self, original_component, new_component):
        mgr_orig = self.get_or_create_component_data_manager(original_component)
        mgr_new = self.get_or_create_component_data_manager(new_component)
        new_path = mgr_new.param_handler.get_component_param_file_path(new_component)
        mgr_orig.param_handler.duplicate_component_params(original_component, new_component["Id"], new_path)

    def has_files(self, component):
        mgr = self.get_or_create_component_data_manager(component)
        return mgr.file_handler.has_files(component)

    def duplicate_files(self, original_component, new_component):
        mgr = self.get_or_create_component_data_manager(original_component)
        mgr_new = self.get_or_create_component_data_manager(new_component)
        mgr.file_handler.duplicate_files(original_component, new_component, mgr_new.file_handler.folder_path)

    def open_parameter_file(self, component):
        mgr = self.get_or_create_component_data_manager(component)
        return mgr.param_handler.open_parameter_file(component)

    def open_file(self, component, file_name):
        mgr = self.get_or_create_component_data_manager(component)
        return mgr.file_handler.open_file(component, file_name)

    def remove_parameter_file(self, component):
        mgr = self.get_or_create_component_data_manager(component)
        mgr.param_handler.remove_component_params(component)

    def remove_file(self, component, file_name):
        mgr = self.get_or_create_component_data_manager(component)
        mgr.file_handler.remove(component, file_name)

    def set_component_params(self, component, params):
        mgr = self.get_or_create_component_data_manager(component)
        return mgr.param_handler.set_component_params(component, params)

    def load_py_component_params(self, component, component_path):
        mgr = self.get_or_create_component_data_manager(component)
        return mgr.param_handler.load_py_component_params(component, component_path)


    @staticmethod
    def is_valid_env_path(path):
        p = Path(path)
        name = p.name
        return p.exists() and p.is_dir() and (p / f"{name}.cse").exists()


    def export_component(self, export_path):
        if not Path(export_path).exists():
            Path(export_path).mkdir(parents=True, exist_ok=True)
        shutil.copytree(self.comp_path, export_path / self.comp_path.name)

    def import_component(self, import_path):
        if not Path(import_path).exists():
            raise FileNotFoundError(f"Import path not found: {import_path}")
        shutil.copytree(import_path, self.comp_path)


    def export_component(self, component_path, export_path):
        if not Path(component_path).exists():
            raise FileNotFoundError(f"Component path not found: {component_path}")
        if not Path(export_path).exists():
            Path(export_path).mkdir(parents=True, exist_ok=True)
        shutil.copytree(component_path, export_path / Path(component_path).name)

    def import_component(self, import_path):
        if not Path(import_path).exists():
            raise FileNotFoundError(f"Import path not found: {import_path}")
        # read component json to get component type
        comp_json_path = Path(import_path)
        with open(comp_json_path, 'r') as f:
            component = json5.load(f)
        component_type = component.get("ComponentType", None)
        if component_type not in self.standalone_comp_managers:
            raise ValueError(f"Unknown component type: {component_type}")
        dest_folder = self.env_path / STANDALONE_COMPONENT_PATHS[component_type][0] / component["Id"]
        if dest_folder.exists():
            raise FileExistsError(f"Component with Id '{component['Id']}' already exists.")

        if not os.path.isdir(import_path):
            import_path = comp_json_path.parent
        shutil.copytree(import_path, dest_folder)
        return component


    def _create_subcomponent_data_managers(self, data):

        def get_or_create(item_or_list):
            if not item_or_list:
                return
            if isinstance(item_or_list, list):
                for it in item_or_list:
                    self.get_or_create_component_data_manager(it)
            else:
                self.get_or_create_component_data_manager(item_or_list)

        for s in data.systems:
            for subc in s.get('Subcomponents', []):
                get_or_create(s[subc])
        for c in data.controllers:
            for subc in c.get('Subcomponents', []):
                get_or_create(c[subc])
        for s in data.scenarios:
            for subc in s.get('Subcomponents', []):
                get_or_create(s[subc])

