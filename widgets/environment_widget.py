from PyQt6.QtWidgets import *
from PyQt6 import uic, QtCore

from .system_widget import SystemWidget
from .controller_widget import ControllerWidget
from .scenario_widget import ScenarioWidget
from .metric_widget import MetricWidget
from .gen_options_widget import GenOptionsWidget
from qt.qt_utils import clear_form_layout

from csbenchlab.env_model import Metadata
from qt.worker_thread import WorkerThread
from csbenchlab.check_environment import check_environment




class EnvironmentWidget(QWidget):

    model = Metadata

    def __init__(self, data, parent=None):
        QWidget.__init__(self, parent=parent)
        uic.loadUi('ui/environment.ui', self)
        self.app = parent
        self.backend = self.app.backend
        self.env_data = parent.env_data
        self.data = data
        self._fill = False
        self.init_environment(self.env_data)

    def init_environment(self, env_data):
        data = env_data.metadata

        self.fill_data()
        self.nameTxt.textChanged.connect(self.on_name_changed)
        self.descriptionTxt.textChanged.connect(self.on_description_changed)
        self.stepTimeTxt.textChanged.connect(self.on_step_time_changed)
        self.coderExtrinsicCb.stateChanged.connect(self.on_coder_extrinsic_changed)

        self.saveBtn.clicked.connect(self.on_save)
        self.closeBtn.clicked.connect(self.on_close)
        self.exportBtn.clicked.connect(self.on_export_environment)
        self.generateEnvironmentBtn.clicked.connect(self.on_generate_environment)
        self.generatorOptionsBtn.clicked.connect(self.on_generator_options)
        self.addSystemInstanceBtn.clicked.connect(self.on_add_system_instance)
        self.addControllerBtn.clicked.connect(self.on_add_controller)
        self.addScenarioBtn.clicked.connect(self.on_add_scenario)
        self.addMetricBtn.clicked.connect(self.on_add_metric)
        self.editReferencesBtn.clicked.connect(self.on_edit_references)


        self.display_meta_data(data.get('Metadata', {}))

    def on_coder_extrinsic_changed(self, state):
        self.env_data.metadata['CoderExtrinsic'] = bool(state)
        if not self._fill:
            self.record_change()

    def display_meta_data(self, meta_data):
        clear_form_layout(self.metadataFormLayout)
        for k, v in meta_data.items():
            key_lbl = QLabel(k)
            val_txt = QLineEdit(str(v))
            # set clicked callback to update metadata
            val_txt.textChanged.connect(lambda text, key=k: self.on_metadata_changed(key, text))
            self.metadataFormLayout.addRow(key_lbl, val_txt)

    def on_metadata_changed(self, key, value):
        self.env_data.metadata["Metadata"][key] = value
        if not self._fill:
            self.record_change()

    def on_save(self):
        self.app.save_component(self)

    def record_change(self):
        self.app.record_widget_change(self)

    def on_name_changed(self, text):
        name_without_star = text.rstrip('*')
        self.env_data.metadata["Name"] = name_without_star
        if not self._fill:
            self.record_change()

    def on_step_time_changed(self, text):
        try:
            val = float(text)
            self.env_data.metadata['Ts'] = val
            if not self._fill:
                self.record_change()
        except ValueError:
            pass

    def on_description_changed(self, text):
        self.env_data.metadata["Metadata"]["Description"] = text
        if not self._fill:
            self.record_change()

    def on_close(self):
        self.app.set_widget(QWidget())

    def on_export_environment(self):

        # prompt for folder
        export_path = QFileDialog.getExistingDirectory(self, "Select Export Directory")
        self.app.env_manager.export_environment(self.env_data, export_path)
        self.app.log(f"Exported environment to {export_path}")

    def fill_data(self):
        data = self.env_data.metadata
        self._fill = True
        checked = bool(data.get("CoderExtrinsic", False))
        self.descriptionTxt.setPlainText(data.get('Description', ''))
        self.stepTimeTxt.setText(str(data.get('Ts', '')))
        self.coderExtrinsicCb.setChecked(checked)
        self.nameTxt.setText(data.get('Name', ''))
        self._fill = False

    def on_generate_environment(self):

        # if has changes, save first
        if self.app.has_unsaved_changes():
            self.app.log("Unsaved changes detected. Please save your changes before generating the environment.")
            return

        (ok, msgs) = check_environment(self.app.env_path, self.env_data)
        if not ok:
            self.app.log("Environment check failed. Please fix the issues before generating the environment.")
            for msg in msgs:
                self.app.log(f"- {msg}")
            return

        def finish(result, error):
            self.app.setEnabled(True)
            if error is not None:
                self.app.log("Environment generation failed.")
                self.app.log(str(error))
                raise Exception(error)
            else:
                self.app.log("Environment generation completed successfully.")

        def generate(gen_options):
            self.app.log("Generating environment...")
            ids = gen_options.get("SelectedControllers", [])
            instance = gen_options.get("SystemInstance", "")


            ids_str = f"{ids}".replace("'", '"')
            if self.app.debug:
                self.app.log(f"COMMAND: generate_control_environment('{self.app.env_path}', '{instance}', {ids_str})")
            def func():
                self.backend.generate_control_environment(self.app.env_path, instance, ids_str)
            self.t = WorkerThread(self.app, func)
            self.t.finished.connect(finish)
            self.t.start()
            self.app.setEnabled(False)

        if not GenOptionsWidget.has_gen_options(self.app.env_path):
            self.app.set_widget(GenOptionsWidget(self, on_save_callback=generate))
        else:
            generate(GenOptionsWidget.load_gen_options(self.app.env_path))

    def on_generator_options(self):
        self.app.set_widget(GenOptionsWidget(self))

    def on_add_system_instance(self):
        self.app.add_component(SystemWidget)

    def on_add_controller(self):
        self.app.add_component(ControllerWidget)

    def on_add_scenario(self):
        self.app.add_component(ScenarioWidget)

    def on_add_metric(self):
        self.app.add_component(MetricWidget)

    def on_edit_references(self):
        pass
