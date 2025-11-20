import os
from PyQt6.QtWidgets import *
from PyQt6 import uic
from .plugin_selector_widget import PluginSelectorWidget
from csbenchlab.env_model import Disturbance

class DisturbanceWidget(QWidget):

    model = Disturbance
    # container_name = "disturbances"

    def __init__(self, data, parent=None):
        QWidget.__init__(self, parent=parent)
        ui_path = parent.app.ui_path if parent is not None else ''
        uic.loadUi(os.path.join(ui_path, 'disturbance.ui'), self)
        self.app = parent.app
        self.data = data
        self.p = parent
        self.init_disturbance(data)
        self._fill = False

    def init_disturbance(self, disturbance_data):

        self.saveBtn.clicked.connect(self.on_save)
        self.removeBtn.clicked.connect(self.on_remove)
        self.importBtn.clicked.connect(self.on_import_system)
        self.exportBtn.clicked.connect(self.on_export_system)
        self.editParametersBtn.clicked.connect(self.on_edit_parameters)
        self.searchOnlineBtn.clicked.connect(self.on_search_online)
        self.editCallbacksBtn.clicked.connect(self.on_edit_callbacks)
        self.importParametersBtn.clicked.connect(self.on_import_parameters)
        self.selectPluginBtn.clicked.connect(self.on_select_plugin)
        self.openContextBtn.clicked.connect(self.open_context)

        self.idTxt.setText(disturbance_data.get('Id', ''))
        self.idTxt.setEnabled(False)
        self.fill_disturbance_data(disturbance_data)

    def open_context(self):
        self.app.open_component_context(self.p)

    def fill_disturbance_data(self, disturbance):
        self._fill = True
        self.libTypeLbl.setText(disturbance.get('PluginName', '-'))
        self.libLibraryLbl.setText(disturbance.get('Lib', '-'))
        if disturbance.get('Lib', '') == '':
            self.editParametersBtn.setEnabled(False)
            self.importParametersBtn.setEnabled(False)
        else:
            self.editParametersBtn.setEnabled(True)
            self.importParametersBtn.setEnabled(True)
        self._fill = False

    def clear_disturbance_data(self):
        self._fill = True
        self.nameTxt.setText('')
        self.descriptionTxt.setPlainText('')
        self.libTypeLbl.setText('-')
        self.libLibraryLbl.setText('-')
        self.editParametersBtn.setEnabled(False)
        self.importParametersBtn.setEnabled(False)
        self._fill = False


    def on_edit_parameters(self):
        self.app.env_manager.open_parameter_file(self.data)

    def on_import_parameters(self):
        print("Import parameters")

    def on_select_plugin(self):
        def on_select(plugin):
            self.data["PluginName"] = plugin["Name"]
            self.data["PluginImplementation"] = plugin["Type"]
            self.data["PluginType"] = 'dist'
            self.data["Lib"] = plugin["Lib"]
            self.data["LibVersion"] = plugin["LibVersion"]
            self.data["ParentComponentId"] = self.p.data['Id']
            self.data["ParentComponentType"] = self.p.data['ComponentType']
            self.app.set_component_params(self.data)
            self.fill_disturbance_data(self.data)
            self.record_change()
            self.app.log(f"Selected plugin: {plugin}")
        dlg = PluginSelectorWidget('dist', on_select, self)
        dlg.show()


    def on_save(self):
        self.app.save_component(self.p)
        self.app.set_widget(self.p, copy=True)

    def on_remove(self):
        self.app.remove_subcomponent(Disturbance, self.p, 'Disturbance', ask_confirmation=False)


    def record_change(self):
        self.app.record_widget_change(self.p)

    def on_import_system(self):
        # path, _ = QFileDialog.getOpenFileName(self, "Import System", "", "System Files (*.json )")
        # if path:
        #     self.app.import_component(self.p, path)
        print("Importing system...")

    def on_export_system(self):
        # export_folder = QFileDialog.getExistingDirectory(self, "Select Export Directory", "")
        # if export_folder:
        #     full_path = Path(export_folder) / 'export'
        #     if not full_path.exists():
        #         full_path.mkdir(parents=True, exist_ok=True)
        #     self.app.export_component(self, full_path)
        print("Exporting system...")

    def on_search_online(self):
        print("Search online")

    def on_edit_callbacks(self):
        self.app.env_manager.open_callbacks(self.data)