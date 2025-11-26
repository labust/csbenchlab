from pathlib import Path
from PyQt6.QtWidgets import *
from PyQt6 import uic, QtCore
import sys, os

from csb_qt.csbenchlab.parameter_handler import ParameterHandler
from csb_qt.csb_pyqt_env_manager import CSBEnvGui
from csb_qt.csb_pyqt_plugin_manager import CSBPluginManager
from csb_qt.qt_utils import do_in_thread
from csbenchlab.csb_utils import load_app_config, save_app_config, instantiate_backend


class CSBenchlabGUI(QMainWindow):
    def __init__(self, ui_path, debug=False, daemon_restart=False, parent=None):
        QMainWindow.__init__(self, parent=parent)
        self.ui_path = ui_path
        uic.loadUi(os.path.join(self.ui_path, 'main.ui'), self)
        self.pluginManagerBtn.clicked.connect(self.open_plugin_manager)
        self.openEnvironmentBtn.clicked.connect(self.open_environment)
        self.newEnvironmentBtn.clicked.connect(self.new_environment)
        self.removeEnvironmentBtn.clicked.connect(self.remove_environment)
        self.backendCb.currentTextChanged.connect(self.set_backend)
        self.debug = debug
        self._fill = False
        self.daemon_restart = daemon_restart
        self.init()

    def init(self):
        self.cfg = load_app_config()
        self.setWindowTitle("CSBenchlab GUI")
        self._fill = True
        self.backendCb.addItems(['python', 'matlab'])
        self.backendCb.setCurrentText(self.cfg.get('active_backend', 'python'))
        self._fill = False
        self.set_backend(self.backendCb.currentText())
        self.resize(300, 200)
        # on double click, open environment
        self.envListWidget.itemDoubleClicked.connect(self.on_env_double_clicked)
        self.envListWidget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.envListWidget.addItems([x["Name"] for x in self.cfg['envs']])

    def remove_environment(self):
        selected_items = self.envListWidget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "No environment selected.")
            return
        for item in selected_items:
            index = self.envListWidget.row(item)
            self.cfg['envs'].pop(index)
            self.envListWidget.takeItem(index)
        save_app_config(self.cfg)

    def new_environment(self):

        # select folder to create new environment
        path = QFileDialog.getExistingDirectory(self, "Select Directory to Create New Environment", "")
        if path:
            env_name, ok = QInputDialog.getText(self, "Environment Name", "Enter Environment Name:")
            if ok and env_name:
                env_path = os.path.join(path, f"{env_name}")
                if os.path.exists(env_path):
                    QMessageBox.warning(self, "Error", f"Environment file already exists: {env_path}")
                    return
                self.backend.create_environment(path, env_name)
                data = self.load_environment(Path(env_path))
                self.cfg['envs'].append({
                    'Path': env_path,
                    'Name': data.metadata.get('Name', env_name)
                })
                save_app_config(self.cfg)
                self.envListWidget.addItem(data.metadata.get('Name', env_name))


    def load_environment(self, path):
        if not os.path.isdir(path):
            path = Path(path).parent
        w = CSBEnvGui(path, self.backend, parent=self, debug=self.debug)
        w.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
        w.show()
        return w.env_data

    def on_env_double_clicked(self, item):
        index = self.envListWidget.row(item)
        env = self.cfg['envs'][index]
        self.load_environment(env['Path'])

    def open_plugin_manager(self):
        from .csb_pyqt_plugin_manager import CSBPluginManager
        w = CSBPluginManager(self.backend, self)
        w.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
        w.show()

    def open_environment(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Environment", "", "Environment Files (*.cse )")
        if path:
            data = self.load_environment(path)
            self.cfg['envs'].append({
                'Path': path,
                'Name': data.metadata.get('Name', os.path.basename(path))
            })
            save_app_config(self.cfg)
            self.envListWidget.addItem(data.metadata.get('Name', Path(path).name.replace('.cse', '')))

    def set_backend(self, backend_name):
        if self._fill:
            return

        def run():
            return instantiate_backend(backend_name, self.daemon_restart)

        def finish(result, error):
            if error:
                QMessageBox.critical(self, "Error", f"Error instantiating backend '{backend_name}':\n{error}")
                self.backendCb.setCurrentText('python')
                return
            (self.backend, msg) = result
            print(f"Using {backend_name} backend with csb path:", self.backend.csb_path)
            self.cfg['active_backend'] = backend_name
            save_app_config(self.cfg)
        # do_in_thread(self, run, finish)
        run()
        finish(run(), None)

