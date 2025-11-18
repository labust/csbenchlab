from pathlib import Path
from PyQt6.QtWidgets import *
from PyQt6 import uic, QtCore
import sys, os

from qt.csbenchlab.parameter_handler import ParameterHandler
from qt.csb_pyqt_env_manager import CSBEnvGui
from qt.csb_pyqt_plugin_manager import CSBPluginManager
from csbenchlab.csb_app_setup import get_appdata_dir


class CSBenchlabGUI(QMainWindow):
    def __init__(self, debug=False, daemon_restart=False, parent=None):
        QMainWindow.__init__(self, parent=parent)
        uic.loadUi('ui/main.ui', self)
        self.pluginManagerBtn.clicked.connect(self.open_plugin_manager)
        self.openEnvironmentBtn.clicked.connect(self.open_environment)
        self.newEnvironmentBtn.clicked.connect(self.new_environment)
        self.removeEnvironmentBtn.clicked.connect(self.remove_environment)
        self.backendCb.currentTextChanged.connect(self.set_backend)
        self.appdata_dir = get_appdata_dir()
        self.debug = debug
        self.daemon_restart = daemon_restart
        self.init()

    def init(self):
        self.cfg = self.load_app_config()
        self.setWindowTitle("CSBenchlab GUI")
        self.backendCb.addItems(['python', 'matlab'])
        self.backendCb.setCurrentText(self.cfg.get('active_backend', 'python'))
        self.resize(300, 200)
        # on double click, open environment
        self.envListWidget.itemDoubleClicked.connect(self.on_env_double_clicked)
        self.envListWidget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.envListWidget.addItems([x["Name"] for x in self.cfg['prev_envs']])

    def remove_environment(self):
        selected_items = self.envListWidget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "No environment selected.")
            return
        for item in selected_items:
            index = self.envListWidget.row(item)
            self.cfg['prev_envs'].pop(index)
            self.envListWidget.takeItem(index)
        self.save_app_config(self.cfg)

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
                self.cfg['prev_envs'].append({
                    'Path': env_path,
                    'Name': data.metadata.get('Name', env_name)
                })
                self.save_app_config(self.cfg)
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
        env = self.cfg['prev_envs'][index]
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
            self.cfg['prev_envs'].append({
                'Path': path,
                'Name': data.metadata.get('Name', os.path.basename(path))
            })
            self.save_app_config(self.cfg)
            self.envListWidget.addItem(data.metadata.get('Name', Path(path).name.replace('.cse', '')))

    def set_backend(self, backend_name):
        if backend_name == 'matlab':
            from csb_matlab.matlab_backend import MatlabBackend
            if not MatlabBackend.is_available():
                QMessageBox.critical(self, "Error", "Matlab Engine for Python is not available or not configured properly.")
                self.backendCb.setCurrentText('python')
                return
            backend = MatlabBackend(restart_daemon=self.daemon_restart)
            backend.start()
        elif backend_name == 'python':
            from backend.python_backend import PythonBackend
            backend = PythonBackend()
            backend.start()
        else:
            raise ValueError("Unknown backend")
        print(f"Using {backend_name} backend with csb path:", backend.csb_path)
        self.backend = backend
        self.cfg['active_backend'] = backend_name
        self.save_app_config(self.cfg)

    def load_app_config(self):
        path = os.path.join(self.appdata_dir, 'app_config.json')
        cfg = {
            'prev_envs': [],
            'active_backend': 'python'
        }
        if os.path.exists(path):
            import json
            with open(path, 'r') as f:
                try:
                    cfg = json.load(f)
                except:
                    pass
        return cfg

    def save_app_config(self, cfg):
        path = os.path.join(self.appdata_dir, 'app_config.json')
        if not os.path.exists(self.appdata_dir):
            os.makedirs(self.appdata_dir)
        import json
        with open(path, 'w') as f:
            json.dump(cfg, f)