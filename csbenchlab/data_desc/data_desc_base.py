from abc import ABC, abstractmethod
import os, shutil
from pathlib import Path
from csb_qt.qt_utils import open_file_in_editor


class DataDescBase(ABC):

    def __init__(self, path):
        self.path = path


    @property
    @abstractmethod
    def files(self):
        pass


    def remove_file(self, filename):
        import os
        file_path = os.path.join(self.path, filename)
        if os.path.exists(file_path):
            os.remove(file_path)

    def evaluate_file(self, filename):
        pass

    def open_file(self, filename):
        file_path = os.path.join(self.path, filename)
        if os.path.exists(file_path):
            open_file_in_editor(file_path)

    def duplicate(self, new_id):
        if not new_id:
            raise ValueError("New ID must be provided")
        full_path = Path(self.path) / new_id
        if not full_path.exists():
            full_path.mkdir(parents=True, exist_ok=True)

        for f in self.files:
            src_file = Path(self.path) / f
            dest_file = full_path / f
            if src_file.exists():
                shutil.copy(src_file, dest_file)

    def remove(self):
        for f in self.files:
            file_path = Path(self.path) / f
            if file_path.exists():
                os.remove(file_path)




def get_default_callbacks_txt_file(comp):
        return f"""
from csbenchlab.common_types import *
import numpy as np

# Override callback functions for component {comp.get('Id', '')}
# Called once on simulation loading
def on_load():
    pass

# Called once when simulation is ready to start
def on_start():
    pass

# Called once when simulation ends
def on_end():
    pass
"""


