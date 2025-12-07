import os
from PyQt6.QtWidgets import *
from PyQt6 import uic
from csbenchlab.env_model import Scenario
import numpy as np
from pathlib import Path
import shutil
from widgets.disturbance_widget import DisturbanceWidget, Disturbance

class ScenarioWidget(QWidget):
    model = Scenario
    # container_name = "scenarios"

    def __init__(self, index, data, parent=None):
        QWidget.__init__(self, parent=parent)
        ui_path = parent.ui_path if parent is not None else ''
        uic.loadUi(os.path.join(ui_path, 'scenario.ui'), self)
        self.index = index
        self.app = parent
        self.data = data
        self.init_scenario(self.data)
        self._fill = False


    def init_scenario(self, scenario_data):
        self.nameTxt.textChanged.connect(self.on_name_changed)
        self.descriptionTxt.textChanged.connect(self.on_description_changed)
        self.simulationTimeTxt.textChanged.connect(self.on_simulation_time_changed)

        self.saveBtn.clicked.connect(self.on_save)
        self.removeBtn.clicked.connect(self.on_remove)
        self.duplicateBtn.clicked.connect(self.on_duplicate_scenario)
        self.exportBtn.clicked.connect(self.on_export_scenario)
        self.importBtn.clicked.connect(self.on_import_scenario)
        self.editScenarioBtn.clicked.connect(self.on_edit_scenario)
        self.addDisturbanceBtn.clicked.connect(self.on_add_disturbance)
        self.removeDisturbanceBtn.clicked.connect(self.on_remove_disturbance)
        self.idTxt.setText(scenario_data.get('Id', ''))
        self.idTxt.setEnabled(False)
        self.removeDisturbanceBtn.setVisible(False)

        self.fill_scenario(scenario_data)

    def on_description_changed(self):
        self.data["Description"] = self.descriptionTxt.toPlainText()
        if not self._fill:
            self.record_change()

    def fill_scenario(self, scenario_data):
        self._fill = True
        dist = scenario_data.get("Disturbance", {})
        if dist:
            self.addDisturbanceBtn.setText("Edit Disturbance")
            self.removeDisturbanceBtn.setVisible(True)
        else:
            self.addDisturbanceBtn.setText("Add Disturbance")
            self.removeDisturbanceBtn.setVisible(False)
        self.nameTxt.setText(scenario_data.get('Name', ''))
        self.descriptionTxt.setPlainText(scenario_data.get('Description', ''))
        self.simulationTimeTxt.setText(str(scenario_data.get('SimulationTime', 0.0)))
        self._fill = False

    def on_add_disturbance(self):
        dist = self.data.get("Disturbance", {})
        if not dist:
            self.record_change()
            dist = self.app.add_subcomponent(Disturbance, self, 'Disturbance')
        self.app.set_widget(DisturbanceWidget(dist, self))


    def on_remove_disturbance(self):
        dist = self.data.get("Disturbance", {})
        if dist:
            self.app.remove_subcomponent(dist, self, 'Disturbance', False)
            self.addDisturbanceBtn.setText("Add Disturbance")
            self.removeDisturbanceBtn.setVisible(False)
        self.record_change()

    def on_simulation_time_changed(self):
        try:
            val = float(self.simulationTimeTxt.text())
            self.data["SimulationTime"] = val
            if not self._fill:
                self.record_change()
        except ValueError:
            pass

    def on_name_changed(self, text):
        name_without_star = text
        self.data["Name"] = name_without_star
        self.app.set_widget_title(self, name_without_star)
        if not self._fill:
            self.record_change()


    def on_edit_scenario(self):
        self.app.env_manager.open_file(self.data, 'scenario.py')


    def on_save(self):
        self.app.save_component(self)

    def record_change(self):
        self.app.record_widget_change(self)

    def on_duplicate_scenario(self):
         self.app.duplicate_component(self)

    def on_import_scenario(self):
        print("Import scenario")

    def on_export_scenario(self):
        print("Export scenario")

    def on_edit_references(self):
        print("Edit references")

    def on_remove(self):
        self.app.remove_component(self)
