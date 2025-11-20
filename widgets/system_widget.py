import os
from PyQt6.QtWidgets import *
from PyQt6 import uic, QtCore
from .plugin_selector_widget import PluginSelectorWidget
from csbenchlab.env_model import System
from pathlib import Path

class SystemWidget(QWidget):

    model = System

    def __init__(self, index, data, parent=None):
        QWidget.__init__(self, parent=parent)
        ui_path = parent.ui_path if parent is not None else ''
        uic.loadUi(os.path.join(ui_path, 'system.ui'), self)
        self.index = index
        self.app = parent
        self.data = data
        self.init_system(data)
        self._fill = False

    def init_system(self, system_data):

        self.nameTxt.textChanged.connect(self.on_name_changed)
        self.descriptionTxt.textChanged.connect(self.on_description_changed)
        self.saveBtn.clicked.connect(self.on_save)
        self.removeBtn.clicked.connect(self.on_remove)
        self.duplicateBtn.clicked.connect(self.on_duplicate_system)
        self.importBtn.clicked.connect(self.on_import_system)
        self.exportBtn.clicked.connect(self.on_export_system)
        self.editParametersBtn.clicked.connect(self.on_edit_parameters)
        self.searchOnlineBtn.clicked.connect(self.on_search_online)
        self.editCallbacksBtn.clicked.connect(self.on_edit_callbacks)
        self.importParametersBtn.clicked.connect(self.on_import_parameters)
        self.selectPluginBtn.clicked.connect(self.on_select_plugin)
        self.openContextBtn.clicked.connect(self.open_context)

        self.idTxt.setText(system_data.get('Id', ''))
        self.idTxt.setEnabled(False)
        self.fill_system_data(system_data)

    def open_context(self):
        self.app.open_component_context(self)

    def fill_system_data(self, system):
        self._fill = True
        self.nameTxt.setText(system.get('Name', ''))
        self.descriptionTxt.setPlainText(system.get('Description', ''))
        self.libTypeLbl.setText(system.get('PluginName', '-'))
        self.libLibraryLbl.setText(system.get('Lib', '-'))
        if system.get('Lib', '') == '':
            self.editParametersBtn.setEnabled(False)
            self.importParametersBtn.setEnabled(False)
        else:
            self.editParametersBtn.setEnabled(True)
            self.importParametersBtn.setEnabled(True)
        self._fill = False

    def clear_system_data(self):
        self._fill = True
        self.nameTxt.setText('')
        self.descriptionTxt.setPlainText('')
        self.libTypeLbl.setText('-')
        self.libLibraryLbl.setText('-')
        self.editParametersBtn.setEnabled(False)
        self.importParametersBtn.setEnabled(False)
        self._fill = False

    def on_name_changed(self, text):
        name_without_star = text
        self.data["Name"] = name_without_star
        self.app.set_widget_title(self, name_without_star)

        if not self._fill:
            self.record_change()

    def on_edit_parameters(self):
        self.app.env_manager.open_parameter_file(self.data)

    def on_import_parameters(self):
        print("Import parameters")

    def on_select_plugin(self):
        def on_select(plugin):
            self.data["PluginName"] = plugin["Name"]
            self.data["PluginImplementation"] = plugin["Type"]
            self.data["PluginType"] = 'sys'
            self.data["Lib"] = plugin["Lib"]
            self.data["LibVersion"] = plugin["LibVersion"]
            self.app.set_component_params(self.data)
            self.fill_system_data(self.data)
            self.record_change()
            self.app.log(f"Selected plugin: {plugin}")
        dlg = PluginSelectorWidget('sys', on_select, self)
        dlg.show()


    def on_description_changed(self):
        text = self.descriptionTxt.toPlainText()
        self.data["Description"] = text
        if not self._fill:
            self.record_change()

    def on_save(self):
        self.app.save_component(self)

    def on_remove(self):
        self.app.remove_component(self)

    def record_change(self):
        self.app.record_widget_change(self)

    def on_duplicate_system(self):
        self.app.duplicate_component(self)

    def on_import_system(self):
        path, _ = QFileDialog.getOpenFileName(self, "Import System", "", "System Files (*.json )")
        if path:
            self.app.import_component(self, path)

    def on_export_system(self):
        export_folder = QFileDialog.getExistingDirectory(self, "Select Export Directory", "")
        if export_folder:
            full_path = Path(export_folder) / 'export'
            if not full_path.exists():
                full_path.mkdir(parents=True, exist_ok=True)
            self.app.export_component(self, full_path)

    def on_search_online(self):
        print("Search online")

    def on_edit_callbacks(self):
        self.app.env_manager.open_file(self.data, 'callbacks.py')