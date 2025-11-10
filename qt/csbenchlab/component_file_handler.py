from pathlib import Path
from qt.csbenchlab.file_handler import ComponentFileHandler
from csbenchlab.data_desc import DataDescBase, COMPONENT_DATA_DESC
from qt.qt_utils import open_file_in_editor
import shutil, os

class ComponentFileHandler:

    def __init__(self, folder_path, data_desc_class:DataDescBase=None):
        self.folder_path = folder_path
        self.data_desc_class = data_desc_class

        if data_desc_class:
            self.desc = data_desc_class(folder_path)
        else:
            self.desc = None


    def open_file(self, component, file_name):

        file_path = self.resolve_file_path(self.folder_path, component, file_name)
        if not Path(file_path).exists():
            with open(file_path, 'w') as f:
                f.write(self.desc.files[file_name](component))

        open_file_in_editor(file_path)


    def resolve_file_path(self, folder_path, component, file_name):
        ctype = component["ComponentType"]
        if self.desc == None:
            raise Exception(f"Cannot open file '{file_name}'. Component '{ctype}' has no files")
        if file_name not in self.desc.files:
            raise Exception(f"Cannot open file '{file_name}'. File does not exist for component '{ctype}'" )
        is_standalone = COMPONENT_DATA_DESC[component["ComponentType"]]["standalone"]
        if is_standalone:
            file_path = Path(folder_path) / component["Id"] / file_name
        else:
            dest_path = COMPONENT_DATA_DESC[component["ComponentType"]]["destination_path"]
            file_path = Path(folder_path) / dest_path / component["Id"] / file_name
        return file_path

    def has_files(self, component):
        if self.desc is None or not self.desc.files:
            return False
        for f in self.desc.files:
            f = self.resolve_file_path(self.folder_path, component, f)
            if Path(f).exists():
                return True
        return False

    def duplicate_files(self, component, new_component, new_folder_path):
        if 'Id' not in new_component:
            raise ValueError("Component must have 'Id' field")

        for f in self.desc.files:
            full_file : Path = self.resolve_file_path(self.folder_path, component, f)
            dest_file : Path = self.resolve_file_path(new_folder_path, new_component, f)
            if full_file.exists():
                if not dest_file.parent.exists():
                    os.makedirs(dest_file.parent, exist_ok=True)

                # replace ids in files
                with open(full_file, 'r') as f:
                    src = f.read()
                src = src.replace(component["Id"], new_component["Id"])
                with open(dest_file, 'w') as f:
                    f.write(src)
