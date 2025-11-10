from PyQt6.QtWidgets import *
from PyQt6 import uic, QtCore

from csbenchlab.env_model import ControllerComponent, Controller
from widgets.plugin_selector_widget import PluginSelectorWidget
from uuid import uuid4
import numpy as np

class ControllerWidget(QWidget):
    model = Controller
    # container_name = "controllers"

    def __init__(self, index, data, parent=None):
        QWidget.__init__(self, parent=parent)
        uic.loadUi('ui/controller.ui', self)
        self.index = index
        self.app = parent
        self.data = data
        self._fill = True
        self.init_controller(self.data)
        self._fill = False

    def init_controller(self, controller_data):
        self.nameTxt.textChanged.connect(self.on_name_changed)
        self.isComposableCb.stateChanged.connect(self.on_is_composable_changed)

        self.descriptionTxt.textChanged.connect(self.on_description_changed)
        self.inputMuxTxt.textChanged.connect(self.on_input_mux_changed)
        self.outputMuxTxt.textChanged.connect(self.on_output_mux_changed)
        self.refHorizonTxt.textChanged.connect(self.on_ref_horizon_changed)
        self.subctlNameTxt.textChanged.connect(self.on_subctl_name_changed)
        self.selectPluginBtn.clicked.connect(self.on_select_plugin)
        self.editParametersBtn.clicked.connect(self.on_edit_parameters)
        self.idTxt.setEnabled(False)

        self.fill_active_data()

        self.addComponentBtn.clicked.connect(self.on_add_subcontroller)
        self.removeComponentBtn.clicked.connect(self.on_remove_subcontroller)
        self.subcontrollerList.clicked.connect(self.on_subcontroller_selected)
        self.duplicateBtn.clicked.connect(self.on_duplicate_controller)
        self.saveBtn.clicked.connect(self.on_save)
        self.removeBtn.clicked.connect(self.on_remove)
        self.exportBtn.clicked.connect(self.on_export_controller)
        self.importBtn.clicked.connect(self.on_import_controller)
        self.editCallbacksBtn.clicked.connect(self.on_edit_callbacks)
        self.openContextBtn.clicked.connect(self.open_context)

    def fill_active_data(self):
        controller_data = self.data
        if self.has_valid_subcontrollers(controller_data):
            self.fill_subcontroller_list()

            idx = self.subcontrollerList.currentRow()
            idx = max(idx, 0)
            item = self.subcontrollerList.item(idx)
            item.setSelected(True)
            self.nameTxt.setText(controller_data.get('Name', ''))
            self.fill_controller_data(controller_data["Subcontrollers"][idx], True)
        else:
            self.fill_controller_data(controller_data)

    def open_context(self):
        self.app.open_component_context(self)

    def on_edit_callbacks(self):
        self.app.env_manager.open_file(self.data, 'callbacks.py')

    def on_edit_parameters(self):
        idx = self.subcontrollerList.currentRow()
        idx = max(idx, 0)
        if idx < 0 or not self.has_valid_subcontrollers(self.data):
            self.app.env_manager.open_parameter_file(self.data)
        else:
            self.app.env_manager.open_parameter_file(self.data["Subcontrollers"][idx])

    def on_duplicate_controller(self):
        new_comp = self.app.duplicate_component(self)

    def on_subctl_name_changed(self, text):
        idx = self.subcontrollerList.currentRow()
        if idx < 0:
            return
        name_without_star = text.rstrip('*')
        item = self.subcontrollerList.item(idx)
        item.setText(name_without_star)
        self.data["Subcontrollers"][idx]["Name"] = name_without_star
        if not self._fill:
            self.record_change()

    def on_name_changed(self, text):
        name_without_star = text
        self.data["Name"] = name_without_star
        self.app.set_widget_title(self, name_without_star)
        if not self._fill:
            self.record_change()

    def on_description_changed(self):
        idx = self.subcontrollerList.currentRow()
        text = self.descriptionTxt.toPlainText()
        if idx < 0:
            self.data["Description"] = text
        else:
            self.data["Subcontrollers"][idx]["Description"] = text
        if not self._fill:
            self.record_change()

    def check_io_mux_value_(self, text):
        err_return = (False, [])
        try:
            if text.strip() == "":
                return (True, '')
            # evaluate the text
            v = eval(text)
            if isinstance(v, int):
                return (True, v)
            # if list, check that all are ints
            if isinstance(v, (list, tuple, np.ndarray)):
                for vi in v:
                    if not isinstance(vi, int):
                        return err_return
                return (True, v)
            return err_return
        except Exception:
            return err_return

    def on_input_mux_changed(self, text):
        idx = self.subcontrollerList.currentRow()

        ok, v = self.check_io_mux_value_(text)
        if not ok:
            return

        if idx < 0:
            self.data.setdefault("Mux", {})
            self.data["Mux"]["Inputs"] = v
        else:
            self.data["Subcontrollers"][idx].setdefault("Mux", {})
            self.data["Subcontrollers"][idx]["Mux"]["Inputs"] = v
        if not self._fill:
            self.record_change()

    def on_output_mux_changed(self, text):

        ok, v = self.check_io_mux_value_(text)
        if not ok:
            return

        idx = self.subcontrollerList.currentRow()
        if idx < 0:
            self.data.setdefault("Mux", {})
            self.data["Mux"]["Outputs"] = v
        else:
            self.data["Subcontrollers"][idx].setdefault("Mux", {})
            self.data["Subcontrollers"][idx]["Mux"]["Outputs"] = v
        if not self._fill:
            self.record_change()

    def on_ref_horizon_changed(self, text):
        try:
            val = int(text)
            self.data['RefHorizon'] = val
            idx = self.subcontrollerList.currentRow()
            if idx >= 0:
                self.data["Subcontrollers"][idx]["RefHorizon"] = val
            else:
                self.data['RefHorizon'] = val
            if not self._fill:
                self.record_change()
        except ValueError:
            pass

    def fill_controller_data(self, ctl, is_subcontroller=False):
        self._fill = True
        self.idTxt.setText(ctl.get('Id', ''))
        if is_subcontroller:
            self.subctlNameTxt.setText(ctl.get('Name', ''))
            checked = True
        else:
            self.nameTxt.setText(ctl.get('Name', ''))
            checked = bool(ctl.get("IsComposable", False))

        self.isComposableCb.setChecked(checked)
        if not checked:
            self.subcontrollerList.setVisible(False)
            self.addComponentBtn.setVisible(False)
            self.removeComponentBtn.setVisible(False)
            self.subctlNameTxt.setVisible(False)
            self.subctlLabel.setVisible(False)
        else:
            self.subcontrollerList.setVisible(True)
            self.addComponentBtn.setVisible(True)
            self.removeComponentBtn.setVisible(True)
            self.subctlNameTxt.setVisible(True)
            self.subctlLabel.setVisible(True)

        if is_subcontroller or not checked:
            self.selectPluginBtn.setEnabled(True)
            self.inputMuxTxt.setEnabled(True)
            self.outputMuxTxt.setEnabled(True)
            self.refHorizonTxt.setEnabled(True)
            self.editCallbacksBtn.setEnabled(True)
        else:
            self.selectPluginBtn.setEnabled(False)
            self.inputMuxTxt.setEnabled(False)
            self.outputMuxTxt.setEnabled(False)
            self.refHorizonTxt.setEnabled(False)
            self.editCallbacksBtn.setEnabled(False)


        mux = ctl.get("Mux", {})
        if mux is not None:
            self.inputMuxTxt.setText(str(mux.get('Inputs', '')))
            self.outputMuxTxt.setText(str(mux.get('Outputs', '')))
        self.descriptionTxt.setPlainText(ctl.get('Description', ''))
        self.refHorizonTxt.setText(str(ctl.get('RefHorizon', '')))
        self.libTypeLbl.setText(ctl.get('Lib', '-'))
        self.libLibraryLbl.setText(ctl.get('PluginName', '-'))


        if ctl.get('Lib', '') == '':
            self.editParametersBtn.setEnabled(False)
            self.importParametersBtn.setEnabled(False)
        else:
            self.editParametersBtn.setEnabled(True)
            self.importParametersBtn.setEnabled(True)

        self._fill = False

    def clear_controller_data(self):
        self._fill = True
        self.subctlNameTxt.setText('')
        self.descriptionTxt.setPlainText('')
        self.inputMuxTxt.setText('')
        self.outputMuxTxt.setText('')
        self.refHorizonTxt.setText('')
        self.libTypeLbl.setText('-')
        self.libLibraryLbl.setText('-')
        self.editParametersBtn.setEnabled(False)
        self.importParametersBtn.setEnabled(False)

        # clear all except name and isComposable
        self.isComposableCb.setChecked(self.data.get("IsComposable", False))
        self._fill = False

    def on_add_subcontroller(self):

        if not self.has_valid_subcontrollers(self.data):
            self.data["Subcontrollers"] = []
        self.app.add_subcomponent(ControllerComponent, self, 'Subcontrollers')

        self.fill_subcontroller_list()
        self.subcontrollerList.setCurrentRow(len(self.data["Subcontrollers"])-1)
        self.on_subcontroller_selected()


    def on_remove_subcontroller(self):
        item = self.subcontrollerList.currentRow()
        comp = self.data["Subcontrollers"][item]
        self.app.remove_subcomponent(comp, self, 'Subcontrollers', item, ask_confirmation=False)

        self.fill_subcontroller_list()
        self.fill_active_data()
        self.record_change()

    def on_export_controller(self):
        print("Export controller")

    def on_import_controller(self):
        print("Import controller")

    def on_save(self):
        self.app.save_component(self)

    def on_close(self):
        self.app.set_widget(QWidget())

    def on_remove(self):
        ctl = self.app.remove_component(self)
        if ctl is not None:
            self._remove_controller_subcontrollers(ctl)

    def on_subcontroller_selected(self):
        idx = self.subcontrollerList.currentRow()
        self.fill_controller_data(self.data["Subcontrollers"][idx], True)

    def on_select_plugin(self):
        def on_select(plugin):
            idx = self.subcontrollerList.currentRow()
            if idx < 0:
                idx = 0
            is_composable = self.data.get("IsComposable", False)
            if is_composable == False:
                self.data["Lib"] = plugin["Lib"]
                self.data["LibVersion"] = plugin["LibVersion"]
                self.data["PluginType"] = 'ctl'
                self.data["PluginName"] = plugin["Name"]
                self.data["PluginImplementation"] = plugin["Type"]
            else:
                self.data["Subcontrollers"][idx]["Lib"] = plugin["Lib"]
                self.data["Subcontrollers"][idx]["LibVersion"] = plugin["LibVersion"]
                self.data["Subcontrollers"][idx]["PluginType"] = 'ctl'
                self.data["Subcontrollers"][idx]["PluginName"] = plugin["Name"]
                self.data["Subcontrollers"][idx]["PluginImplementation"] = plugin["Type"]
            self.app.set_component_params(
                self.data if not is_composable else
                self.data["Subcontrollers"][idx])


            ctl = self.data if not is_composable else \
                self.data["Subcontrollers"][idx]

            self.fill_controller_data(ctl, is_composable)

            self.app.log(f"Selected plugin: {plugin}")
            self.record_change()
        dlg = PluginSelectorWidget('ctl', on_select, self)
        dlg.show()



    def has_valid_subcontrollers(self, controller):
        if not controller.get("IsComposable", False):
            return False
        comp = controller.get("Subcontrollers", None)

        if comp is None or len(comp) == 0:
            return False
        name = comp[0].get("Name", None)
        if name is None or name == "":
            return False
        return True


    def fill_subcontroller_list(self):
        self.subcontrollerList.clear()
        if not self.data.get("IsComposable", False):
            return
        if self.has_valid_subcontrollers(self.data):
            subcontrollers = self.data.get("Subcontrollers", [])
            for sc in subcontrollers:
                self.subcontrollerList.addItem(sc.get("Name", ""))

    def clear_subcontroller_list(self):
        self.subcontrollerList.clear()
        self._remove_controller_subcontrollers(self.data)
        self.data["Subcontrollers"] = []

    def on_is_composable_changed(self, state, record=True):

        if self._fill:
            return

        # ask user to confirm clearing components if state is 0
        curr = self.data["IsComposable"]
        if state == 0 and bool(curr) == True and \
                len(self.data.get("Subcontrollers", [])) > 0:
            reply = QMessageBox.question(self, 'Clear Subcontrollers',
                                         "Are you sure you want to clear all Subcontrollers?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                         QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.No:
                self.data["IsComposable"] = True
                self.isComposableCb.setChecked(True)
                return
            self.clear_subcontroller_list()
        self.data["IsComposable"] = bool(state)
        self.fill_controller_data(self.data)
        if state != 0:
            self.fill_subcontroller_list()
            self.subcontrollerList.setCurrentRow(0)
            self.clear_controller_data()
        if record:
            self.record_change()

    def record_change(self):
        self.app.record_widget_change(self)