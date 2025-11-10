from pathlib import Path
import os
from qt.qt_utils import open_file_in_editor

class ComponentFileHandler:

    def __init__(self, dir_path, file_name, default_txt=""):
        self.dir_path = dir_path
        self.file_name = file_name
        self.name = file_name.split('.')[0]
        self.default_txt = default_txt
        self.file_path = Path(dir_path) / self.file_name
        if not self.file_path.parent.exists():
            self.file_path.parent.mkdir(parents=True, exist_ok=True)

        self.make_file_if_not_exists()


    def make_file_if_not_exists(self):
        if self.file_path.exists():
            return
        with open(self.file_path, 'w') as f:
            f.write(self.default_txt)

    def import_as_module(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(f"{self.name}", self.file_path)
        module = importlib.util.module_from_spec(spec)
        m = spec.loader.exec_module(module)
        return m

    def delete_file(self):
        if self.file_path.exists():
            os.remove(self.file_path)

    def open_file(self):
        if self.file_path.exists():
            open_file_in_editor(self.file_path)

    def duplicate_file(self, new_comp_path):
        new_file_path = Path(new_comp_path) / self.file_name
        if self.file_path.exists():
            with open(self.file_path, 'r') as f:
                src = f.read()
            with open(new_file_path, 'w') as f:
                f.write(src)
            return str(new_file_path)
        return None

