from PyQt6.QtWidgets import *
from PyQt6 import uic, QtCore
from pathlib import Path
import json5, json


class GenOptionsWidget(QWidget):

    @classmethod
    def has_gen_options(cls, env_path):
        gen_options_path = Path(env_path) / "gen_options.json"
        return gen_options_path.exists()

    @classmethod
    def load_gen_options(cls, env_path):
        gen_options_path = Path(env_path) / "gen_options.json"
        gen_options = {"SelectedControllers": []}
        if gen_options_path.exists():
            with open(gen_options_path, 'r') as f:
                try:
                    gen_options = json5.load(f)
                except Exception as e:
                    print(f"Error loading gen_options.json: {e}")
        return gen_options

    def __init__(self, parent=None, on_save_callback=None):
        QWidget.__init__(self, parent=parent)
        uic.loadUi('ui/gen_options.ui', self)
        self.app = parent.app
        self.env_path = self.app.env_path
        self.env_data = parent.env_data
        self.on_save_callback = on_save_callback
        self.init_ui()


    def init_ui(self):
        self.gen_options = self.load_gen_options(self.env_path)
        self.fill_data()

        # on list selection change
        self.saveBtn.clicked.connect(self.on_save)
        self.cancelBtn.clicked.connect(self.on_cancel)
        self.selectBtn.clicked.connect(self.on_select)
        self.unselectBtn.clicked.connect(self.on_unselect)
        self.bringUpBtn.clicked.connect(self.on_bring_up)
        self.pullDownBtn.clicked.connect(self.on_pull_down)

        system_names = [s['Name'] for s in self.env_data.systems]
        self.systemInstanceCbox.addItems(system_names)
        self.systemInstanceCbox.currentIndexChanged.connect(self.on_system_instance_changed)


    def on_system_instance_changed(self, index):
        self.gen_options['SystemInstance'] = self.env_data.systems[index]["Id"]


    def fill_data(self):
        # fill with controllers
        self.envControllersList.clear()
        self.genControllersList.clear()

        for ctl in self.env_data.controllers:
            item = QListWidgetItem(ctl["Name"])
            item.setData(QtCore.Qt.ItemDataRole.UserRole, ctl["Id"])
            if ctl["Id"] not in self.gen_options.get("SelectedControllers", []):
                self.envControllersList.addItem(item)

        for id in self.gen_options["SelectedControllers"]:
            ctl = next((c for c in self.env_data.controllers if c["Id"] == id), None)
            if ctl is None:
                raise ValueError(f"Controller with id {id} not found in environment data")
            item = QListWidgetItem(ctl["Name"])
            item.setData(QtCore.Qt.ItemDataRole.UserRole, ctl["Id"])
            self.genControllersList.addItem(item)

    def on_select(self):
        item = self.envControllersList.currentItem()
        if item is not None:
            id = item.data(QtCore.Qt.ItemDataRole.UserRole)
            controller = next((c for c in self.env_data.controllers if c["Id"] == id), None)
            if controller is not None and controller["Id"] not in self.gen_options["SelectedControllers"]:
                self.gen_options["SelectedControllers"].append(controller["Id"])
                self.fill_data()

    def on_unselect(self):
        item = self.genControllersList.currentItem()
        if item is not None:
            id = item.data(QtCore.Qt.ItemDataRole.UserRole)
            controller = next((c for c in self.env_data.controllers if c["Id"] == id), None)
            if controller["Id"] in self.gen_options["SelectedControllers"]:
                self.gen_options["SelectedControllers"].remove(controller["Id"])
                self.fill_data()

    def on_bring_up(self):

        item = self.genControllersList.currentItem()
        if item is not None:
            row = self.genControllersList.row(item)
            if row > 0:
                id = item.data(QtCore.Qt.ItemDataRole.UserRole)
                controller = next((c for c in self.env_data.controllers if c["Id"] == id), None)
                self.gen_options["SelectedControllers"].remove(controller["Id"])
                self.gen_options["SelectedControllers"].insert(row - 1, controller["Id"])
                self.fill_data()
                self.genControllersList.setCurrentRow(row - 1)

    def on_pull_down(self):
        item = self.genControllersList.currentItem()
        if item is not None:
            row = self.genControllersList.row(item)
            if row < self.genControllersList.count() - 1:
                id = item.data(QtCore.Qt.ItemDataRole.UserRole)
                controller = next((c for c in self.env_data.controllers if c["Id"] == id), None)
                self.gen_options["SelectedControllers"].remove(controller["Id"])
                self.gen_options["SelectedControllers"].insert(row + 1, controller["Id"])
                self.fill_data()
                self.genControllersList.setCurrentRow(row + 1)

    def on_save(self):
        gen_options_path = Path(self.env_path) / "gen_options.json"
        with open(gen_options_path, 'w') as f:
            json.dump(self.gen_options, f, indent=4)
        self.app.show_environment()
        if self.on_save_callback is not None:
            self.on_save_callback(self.gen_options)
        self.app.log(f"Generator options saved to {gen_options_path}")

    def on_cancel(self):
        self.app.show_environment()

    def on_env_controller_selected(self, item):
        pass

    def on_gen_controller_selected(self, item):
        pass

