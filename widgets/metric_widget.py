import os
from PyQt6.QtWidgets import *
from PyQt6 import uic
from csbenchlab.env_model import Metric

class MetricWidget(QWidget):
    model = Metric
    # container_name = "metrics"

    def __init__(self, index, data, parent=None):
        QWidget.__init__(self, parent=parent)
        ui_path = parent.ui_path if parent is not None else ''
        uic.loadUi(os.path.join(ui_path, 'metric.ui'), self)
        self.index = index
        self.app = parent
        self.data = data
        self.init_metric(self.data)
        self._fill = False

    def init_metric(self, metric_data):
        self.nameTxt.textChanged.connect(self.on_name_changed)
        self.descriptionTxt.textChanged.connect(self.on_description_changed)

        self.saveBtn.clicked.connect(self.on_save)
        self.removeBtn.clicked.connect(self.on_remove)
        self.duplicateBtn.clicked.connect(self.on_duplicate_metric)
        self.exportBtn.clicked.connect(self.on_export_metric)
        self.editMetricBtn.clicked.connect(self.on_edit_metric)
        self.openContextBtn.clicked.connect(self.open_context)
        self.idTxt.setText(metric_data.get('Id', ''))
        self.idTxt.setEnabled(False)
        self.fill_metric(metric_data)

    def open_context(self):
        self.app.open_component_context(self)

    def fill_metric(self, metric_data):
        self._fill = True
        self.nameTxt.setText(metric_data.get('Name', ''))
        self.descriptionTxt.setPlainText(metric_data.get('Description', ''))
        self._fill = False

    def on_name_changed(self, text):
        name_without_star = text.rstrip('*')
        self.data["Name"] = name_without_star
        self.app.set_widget_title(self, name_without_star)
        if not self._fill:
            self.record_change()

    def on_description_changed(self):
        self.data["Description"] = self.descriptionTxt.toPlainText()
        if not self._fill:
            self.record_change()

    def on_edit_metric(self):
        self.app.env_manager.open_file(self.data, 'metric.py')

    def on_remove(self):
        self.app.remove_component(self)

    def on_save(self):
        self.app.save_component(self)

    def record_change(self):
        self.app.record_widget_change(self)

    def on_duplicate_metric(self):
        self.app.duplicate_component(self)

    def on_export_metric(self):
        print("Exporting metric...")

