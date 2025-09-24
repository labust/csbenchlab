import json5
from pathlib import Path
from types import SimpleNamespace

class EnvFileManager:




    class ComponentDataManager:
        def __init__(self, rel_path, enlist=False, as_folder=False):
            self.enlist = enlist
            self.as_folder = as_folder
            self.rel_path = rel_path
            if as_folder:
                self.enlist = False

        def load(self, path):
            path = Path(path) / self.rel_path
            if not self.as_folder:
                return self._load_json5_file(path)
            all_data = []
            if path.exists() and path.is_dir():
                for file in path.glob("*.json"):
                    data = self._load_json5_file(file)
                    if isinstance(data, list):
                        all_data.extend(data)
                    else:
                        all_data.append(data)
            return all_data

        def save(self, path, data):
            path = Path(path) / self.rel_path
            if not self.as_folder:
                self._save_json5_file(path, data)
            else:
                if not path.exists():
                    path.mkdir(parents=True, exist_ok=True)
                existing_files = {f.name for f in path.glob("*.json")}
                data_files = set()
                if isinstance(data, list):
                    for item in data:
                        file_name = f"{item.get('Name')}.json"
                        file_path = path / file_name
                        self._save_json5_file(file_path, item)
                        data_files.add(file_name)
                else:
                    file_name = f"{data.get('Name')}.json"
                    file_path = path / file_name
                    self._save_json5_file(file_path, data)
                    data_files.add(file_name)
                # Remove files that are no longer present in the data
                for file_name in existing_files - data_files:
                    (path / file_name).unlink()

        def add_component(self, component, env_path):
            if not self.enlist and not self.as_folder:
                self.save(env_path, component)
                return
            comps = self.load(env_path)
            # delete if exists
            comps = [c for c in comps if c['Id'] != component.Id]
            comps.append(component)
            self.save(env_path, comps)


        def remove_component(self, component_id, env_path):
            comps = self.load(env_path)
            comps = [c for c in comps if c['Id'] != component_id]
            self.save(env_path, comps)

        def _load_json5_file(self, file_path):
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            with open(file_path, 'r') as f:
                r = json5.load(f)
                if self.enlist and not isinstance(r, list):
                    r = [r]
                return r

        def _save_json5_file(self, file_path, data):
            with open(file_path, 'w') as f:
                if self.enlist and not isinstance(data, list):
                    data = [data]
                json5.dump(data, f, indent=4)

    COMPONENT_MANAGERS = {
        'system': ComponentDataManager(Path('parts') / 'system.json', enlist=True),
        'controller': ComponentDataManager(Path('parts') / 'controllers', enlist=True, as_folder=True),
        'scenario': ComponentDataManager(Path('parts') / 'scenarios.json', enlist=True),
        'metric': ComponentDataManager(Path('parts') / 'metrics.json', enlist=True),
        'metadata': ComponentDataManager(Path('config.json'), enlist=False),
    }

    def __init__(self, env_path):

        if not self.is_valid_env_path(env_path):
            raise ValueError(f"Invalid environment path: {env_path}")
        self.env_path = Path(env_path)


    def add_component(self, component_type, component):
        if component_type in self.COMPONENT_MANAGERS:
            self.COMPONENT_MANAGERS[component_type].add_component(component, self.env_path)
        else:
            raise ValueError(f"Unknown component type: {component_type}")

    def remove_component(self, component_type, component):
        if component_type in self.COMPONENT_MANAGERS:
            self.COMPONENT_MANAGERS[component_type].remove_component(component["Id"], self.env_path)
        else:
            raise ValueError(f"Unknown component type: {component_type}")

    def load_environment_data(self):
        data = SimpleNamespace()
        data.metadata = self.COMPONENT_MANAGERS['metadata'].load(self.env_path)
        data.systems = self.COMPONENT_MANAGERS['system'].load(self.env_path)
        data.controllers = self.COMPONENT_MANAGERS['controller'].load(self.env_path)
        data.scenarios = self.COMPONENT_MANAGERS['scenario'].load(self.env_path)
        data.metrics = self.COMPONENT_MANAGERS['metric'].load(self.env_path)
        return data

    def save_environment_data(self, data):
        self.COMPONENT_MANAGERS['metadata'].save(self.env_path, data.metadata)
        self.COMPONENT_MANAGERS['system'].save(self.env_path, data.systems)
        self.COMPONENT_MANAGERS['controller'].save(self.env_path, data.controllers)
        self.COMPONENT_MANAGERS['scenario'].save(self.env_path, data.scenarios)
        self.COMPONENT_MANAGERS['metric'].save(self.env_path, data.metrics)


    @staticmethod
    def is_valid_env_path(path):
        p = Path(path)
        name = p.name
        return p.exists() and p.is_dir() and (p / f"{name}.cse").exists()

    def export_environment(self, export_path, data):
        pass