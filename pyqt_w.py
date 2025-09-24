from PyQt6.QtWidgets import *
from PyQt6 import uic

from env_file_manager import EnvFileManager
from uuid import uuid4
from env_model import System, Controller, Metric, Scenario, Disturbance, Estimator, Metadata
from copy import deepcopy


def clear_form_layout(form_layout):
    while form_layout.count():
        item = form_layout.takeAt(0)
        if item is not None:
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                sublayout = item.layout()
                if sublayout is not None:
                    clear_form_layout(sublayout)

def env_has_to_be_changed(item):
    # check if env is changing
    if item is None:
        return False
    parent = item.parent()
    name_without_star = item.text(0).rstrip('*')
    if name_without_star == "Environment" and parent is None:
        return True
    if parent is None:
        return False
    par_name_without_star = parent.text(0).rstrip('*')
    if name_without_star in ["Systems", "Controllers", "Scenarios", "Metrics"]\
        and par_name_without_star == "Environment":
        return True
    return False


class SystemWidget(QWidget):
    def __init__(self, index, parent=None):
        QWidget.__init__(self, parent=parent)
        uic.loadUi('system.ui', self)
        self.index = index
        self.app = parent
        self.env_data = self.app.env_data
        self.init_system(self.env_data.systems[index])

    def init_system(self, system_data):
        self.nameTxt.setText(system_data.get('Name', ''))
        self.nameTxt.textChanged.connect(self.on_name_changed)
        self.descriptionTxt.setPlainText(system_data.get('Description', ''))
        self.descriptionTxt.textChanged.connect(self.on_description_changed)

        self.saveBtn.clicked.connect(self.on_save)
        self.removeBtn.clicked.connect(self.on_remove)
        self.duplicateBtn.clicked.connect(self.on_duplicate_system)
        self.importBtn.clicked.connect(self.on_import_system)
        self.exportBtn.clicked.connect(self.on_export_system)
        self.searchOnlineBtn.clicked.connect(self.on_search_online)
        self.editCallbacksBtn.clicked.connect(self.on_edit_callbacks)

    def on_name_changed(self, text):
        name_without_star = text.rstrip('*')
        self.env_data.systems[self.index]["Name"] = name_without_star
        self.record_change()

    def on_description_changed(self):
        text = self.descriptionTxt.toPlainText()
        self.env_data.systems[self.index]["Description"] = text
        self.record_change()

    def on_save(self):
        self.app.save_component(self)

    def on_remove(self):
        self.app.remove_component(self)

    def record_change(self):
        self.app.record_widget_change(self)

    def on_duplicate_system(self):
        self.app.duplicate_component(self)
        print("Duplicate system")

    def on_import_system(self):
        print("Import system")

    def on_export_system(self):
        print("Export system")

    def on_search_online(self):
        print("Search online")

    def on_edit_callbacks(self):
        print("Edit callbacks")


class EnvironmentWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        uic.loadUi('environment.ui', self)
        self.app : CSBEnvGui = parent
        self.env_data = parent.env_data
        self.init_environment(self.env_data)

    def init_environment(self, env_data):
        data = env_data.metadata
        self.nameTxt.setText(data.get('Name', ''))
        self.nameTxt.textChanged.connect(self.on_name_changed)
        self.descriptionTxt.setPlainText(data.get('Description', ''))
        self.descriptionTxt.textChanged.connect(self.on_description_changed)
        self.stepTimeTxt.setText(str(data.get('StepTime', '')))
        self.stepTimeTxt.textChanged.connect(self.on_step_time_changed)
        self.coderExtrinsicCb.stateChanged.connect(self.on_coder_extrinsic_changed)
        checked = bool(data.get("CoderExtrinsic", False))
        self.coderExtrinsicCb.setChecked(checked)

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

        system_names = [s['Name'] for s in self.env_data.systems]
        self.systemInstanceCbox.addItems(system_names)
        self.systemInstanceCbox.currentIndexChanged.connect(self.on_system_instance_changed)

        self.display_meta_data(data.get('Metadata', {}))

    def on_system_instance_changed(self, index):
        self.env_data['SystemInstance'] = self.env_data.systems[index]["Id"]

    def on_coder_extrinsic_changed(self, state):
        self.env_data['CoderExtrinsic'] = bool(state)
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
        self.record_change()

    def on_save(self):
        self.app.save_component(self)

    def record_change(self):
        self.app.record_widget_change(self)


    def on_name_changed(self, text):
        name_without_star = text.rstrip('*')
        self.env_data.metadata["Name"] = name_without_star
        self.record_change()

    def on_step_time_changed(self, text):
        try:
            val = float(text)
            self.env_data['StepTime'] = val
            self.record_change()
        except ValueError:
            pass

    def on_description_changed(self, text):
        self.env_data.metadata["Metadata"]["Description"] = text
        self.record_change()

    def on_close(self):
        self.app.set_widget(QWidget())

    def on_export_environment(self):

        # prompt for folder
        export_path = QFileDialog.getExistingDirectory(self, "Select Export Directory")
        self.app.env_manager.export_environment(self.env_data, export_path)
        self.app.log(f"Exported environment to {export_path}")

    def on_generate_environment(self):
        print("Generate environment")

    def on_generator_options(self):
        print("Generator options")

    def on_add_system_instance(self):
        self.app.add_component(SystemWidget)

    def on_add_controller(self):
        self.app.add_component(ControllerWidget)

    def on_add_scenario(self):
        self.app.add_scenario()

    def on_add_metric(self):
        self.app.add_metric()

    def on_edit_references(self):
        pass

class ControllerWidget(QWidget):
    def __init__(self, index, parent=None):
        QWidget.__init__(self, parent=parent)
        uic.loadUi('controller.ui', self)
        self.index = index
        self.app = parent
        self.env_data = self.app.env_data
        self.init_controller(self.env_data.controllers[index])

    def init_controller(self, controller_data):
        self.nameTxt.setText(controller_data.get('Name', ''))
        self.nameTxt.textChanged.connect(self.on_name_changed)
        self.isComposableCb.stateChanged.connect(self.on_is_composable_changed)
        checked = bool(controller_data.get("IsComposable", False))
        self.isComposableCb.setChecked(checked)
        self.descriptionTxt.setPlainText(controller_data.get('Description', ''))
        self.descriptionTxt.textChanged.connect(self.on_description_changed)
        self.inputMuxTxt.setText(controller_data.get('InputMux', ''))
        self.inputMuxTxt.textChanged.connect(self.on_input_mux_changed)
        self.outputMuxTxt.setText(controller_data.get('OutputMux', ''))
        self.outputMuxTxt.textChanged.connect(self.on_output_mux_changed)
        self.refHorizonTxt.setText(str(controller_data.get('RefHorizon', '')))
        self.refHorizonTxt.textChanged.connect(self.on_ref_horizon_changed)

        self.addComponentBtn.clicked.connect(self.on_add_subcontroller)
        self.removeComponentBtn.clicked.connect(self.on_remove_subcontroller)
        self.subcontrollerList.clicked.connect(self.on_subcontroller_selected)
        self.duplicateBtn.clicked.connect(self.on_duplicate_controller)
        self.saveBtn.clicked.connect(self.on_save)
        self.removeBtn.clicked.connect(self.on_remove)
        self.exportBtn.clicked.connect(self.on_export_controller)
        self.importBtn.clicked.connect(self.on_import_controller)

    def on_duplicate_controller(self):
        print("Duplicate controller")

    def on_name_changed(self, text):
        name_without_star = text.rstrip('*')
        self.env_data.controllers[self.index]["Name"] = name_without_star
        self.record_change()

    def on_description_changed(self):
        text = self.descriptionTxt.toPlainText()
        self.env_data.controllers[self.index]["Description"] = text
        self.record_change()

    def on_input_mux_changed(self, text):
        self.env_data.controllers[self.index]["InputMux"] = text
        self.record_change()

    def on_output_mux_changed(self, text):
        self.env_data.controllers[self.index]["OutputMux"] = text
        self.record_change()

    def on_ref_horizon_changed(self, text):
        try:
            val = int(text)
            self.env_data.controllers[self.index]['RefHorizon'] = val
            self.record_change()
        except ValueError:
            pass

    def on_add_subcontroller(self):
        print("Add subcontroller")

    def on_remove_subcontroller(self):
        print("Remove subcontroller")

    def on_subcontroller_selected(self):
        print("Subcontroller selected")

    def on_export_controller(self):
        print("Export controller")

    def on_import_controller(self):
        print("Import controller")

    def on_duplicate_controller(self):
        self.app.duplicate_component(self)

    def on_save(self):
        self.app.save_component(self)

    def on_close(self):
        self.app.set_widget(QWidget())

    def on_remove(self):
        self.app.remove_component(self)

    def on_is_composable_changed(self, state):
        if state == 0:
            self.addComponentBtn.setVisible(False)
            self.subcontrollerList.setVisible(False)
        else:
            self.addComponentBtn.setVisible(True)
            self.subcontrollerList.setVisible(True)

        self.record_change()

    def record_change(self):
        self.app.record_widget_change(self)


class CSBEnvGui(QMainWindow):
    def __init__(self, env_path, parent=None, readonly=False):
        QMainWindow.__init__(self, parent=parent)
        uic.loadUi('main.ui', self)
        self.env_manager = EnvFileManager(env_path)
        self.env_data = self.env_manager.load_environment_data()
        # set title
        self.setWindowTitle(f"CSB Environment - {self.env_data.metadata.get('Name', '')}")
        self._readonly = readonly
        self.fill_tree_view()

        self.widget_changed = dict()


    def add_component(self, widget_cls):
        dcls = self.get_dataclass(widget_cls)
        d = dcls.as_dict()
        container = self.get_container(widget_cls)
        d["Name"] = self.make_name_unique(f"New {dcls.__name__}", container)
        container.append(d)
        self.fill_tree_view()

        w = widget_cls(len(container)-1, self)
        self.set_widget(w)
        self.record_widget_change(w)
        self.log(f"Added new {dcls.__name__.lower()}: {d['Name']}")


    def duplicate_component(self, widget):
        widget_cls = type(widget)
        dcls = self.get_dataclass(widget_cls)
        container = self.get_container(widget_cls)
        original_data = container[widget.index]
        d = deepcopy(original_data)
        d["Id"] = str(uuid4())
        d["Name"] = self.make_name_unique(f"{d['Name']} (copy)", container)
        container.append(d)
        self.fill_tree_view()
        w = widget_cls(len(container)-1, self)
        self.set_widget(w)
        self.record_widget_change(w)
        self.log(f"Duplicated {dcls.__name__.lower()}: {d['Name']}")

    def remove_component(self, widget):

        widget_cls = type(widget)
        dcls = self.get_dataclass(widget_cls)
        container = self.get_container(widget_cls)
        widget_name = container[widget.index]['Name']
        # prompt for confirmation
        reply = QMessageBox.question(self, 'Remove Confirmation',
                                     f"Are you sure you want to remove {dcls.__name__.lower()} '{widget_name}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes:
            return
        obj = container[widget.index]
        name = obj['Name']
        del container[widget.index]
        self.fill_tree_view()
        self.set_widget(QWidget())
        self.env_manager.remove_component(dcls.__name__.lower(), obj)
        self.log(f"Removed {dcls.__name__.lower()}: {name}")

    def save_component(self, widget):
        widget_cls = type(widget)
        dcls = self.get_dataclass(widget_cls)
        container = self.get_container(widget_cls)
        if hasattr(widget, 'index'):
            obj = container[widget.index]
        else:
            obj = container
        name = obj['Name']
        self.env_manager.add_component(dcls.__name__.lower(), obj)
        self.log(f"Saved {dcls.__name__.lower()}: {name}")


    def make_name_unique(self, name, objects):

        existing_names = [o['Name'] for o in objects]
        if name not in existing_names:
            return name
        i = 1
        new_name = f"{name} ({i})"
        while new_name in existing_names:
            i += 1
            new_name = f"{name} ({i})"
        return new_name

    def fill_tree_view(self):

        self.treeWidget.clear()

        root = QTreeWidgetItem(self.treeWidget)
        root.setText(0, "Environment")

        env_values = ["Systems", "Controllers", "Scenarios", "Metrics"]
        self.roots = []
        for i, r in enumerate(env_values):
            env_v = QTreeWidgetItem(root)
            env_v.setText(0, r)
            self.roots.append(env_v)

        for s in self.env_data.systems:
            item = QTreeWidgetItem(self.roots[0])
            item.setText(0, s['Name'])
            item.setText(1, s.get('Description', ''))
        for c in self.env_data.controllers:
            item = QTreeWidgetItem(self.roots[1])
            item.setText(0, c['Name'])
            item.setText(1, c.get('Description', ''))
        for sc in self.env_data.scenarios:
            item = QTreeWidgetItem(self.roots[2])
            item.setText(0, sc['Name'])
            item.setText(1, sc.get('Description', ''))
        for m in self.env_data.metrics:
            item = QTreeWidgetItem(self.roots[3])
            item.setText(0, m['Name'])
            item.setText(1, m.get('Description', ''))

        self.treeWidget.itemClicked.connect(self.on_item_clicked)

        # click on first item
        self.treeWidget.setCurrentItem(self.treeWidget.topLevelItem(0).child(0))
        self.on_item_clicked(self.treeWidget.currentItem())

    def on_item_clicked(self, item):
        parent = item.parent()
        index = -1
        if parent is not None:
            index = parent.indexOfChild(item)
        if parent is None or parent.parent() is None \
            or parent.text(0) == "Environment":
            self.show_environment(index)
        elif parent.text(0) == "Systems":
            self.show_system(index)
        elif parent.text(0) == "Controllers":
            self.show_controller(index)
        elif parent.text(0) == "Scenarios":
            self.show_scenario(index)
        elif parent.text(0) == "Metrics":
            self.show_metric(index)


    def log(self, msg):
        from datetime import datetime
        t_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        max_lines = 1000
        if self.logText.document().blockCount() > max_lines:
            # clear last 100 lines
            cursor = self.logText.textCursor()
            cursor.movePosition(cursor.Start)
            for _ in range(100):
                cursor.select(cursor.LineUnderCursor)
                cursor.removeSelectedText()
                cursor.deleteChar()
            self.logText.setTextCursor(cursor)
        self.logText.append(f"[{t_now}]: {msg}")

    def show_environment(self, index):
        w = EnvironmentWidget(self)
        self.set_widget(w)
    def show_system(self, index):
        w = SystemWidget(index, self)
        self.set_widget(w)
    def show_controller(self, index):
        w = ControllerWidget(index, self)
        self.set_widget(w)
    def show_scenario(self, index):
        print("Show scenario", index)

    def show_metric(self, index):
        print("Show metric", index)

    def set_widget(self, w):

        if isinstance(w, SystemWidget):
            self.treeWidget.setCurrentItem(self.roots[0].child(w.index))
        elif isinstance(w, ControllerWidget):
            self.treeWidget.setCurrentItem(self.roots[1].child(w.index))
        elif isinstance(w, EnvironmentWidget):
            pass
        clear_form_layout(self.widgetBox)
        self.widgetBox.addWidget(w)

    def record_widget_change(self, widget):
        id = str(widget.__class__)
        if hasattr(widget, 'index'):
            id += str(widget.index)
        changed = self.widget_changed.get(id, None)
        if changed is None or changed is False:
            # set * to tree name
            tree = self.treeWidget
            item = tree.currentItem()
            if item is not None:
                if env_has_to_be_changed(item):
                    tree.topLevelItem(0).setText(0, tree.topLevelItem(0).text(0) + '*')
                else:
                    item.setText(0, item.text(0) + '*')
        self.widget_changed[id] = True

    def on_widget_save(self, widget, save_fn):

        id = self.make_widget_id(widget)
        changed = self.widget_changed.get(id, None)
        if changed is None or changed is False:
            return

        save_fn()
        self.widget_changed[id] = False
        # remove * from tree name
        tree = self.treeWidget
        item = tree.currentItem()
        if item is not None:
            if env_has_to_be_changed(item):
                root = tree.topLevelItem(0)
                name = root.text(0)
                if name.endswith('*'):
                    root.setText(0, name[:-1])
                return
            else:
                name = item.text(0)
                if name.endswith('*'):
                    item.setText(0, name[:-1])

    def make_widget_id(self, widget):
        id = str(widget.__class__)
        if hasattr(widget, 'ctl_idx'):
            id += str(widget.ctl_idx)
        return id

    def get_container(self, widget_cls):
        if widget_cls == SystemWidget:
            return self.env_data.systems
        elif widget_cls == ControllerWidget:
            return self.env_data.controllers
        elif widget_cls == EnvironmentWidget:
            return self.env_data.metadata
        raise ValueError("Unknown widget class")

    def get_dataclass(self, widget_cls):
        if widget_cls == SystemWidget:
            return System
        elif widget_cls == ControllerWidget:
            return Controller
        elif widget_cls == EnvironmentWidget:
            return Metadata
        raise ValueError("Unknown widget type")

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)

    env_path = "demo_env"
    w = CSBEnvGui(env_path, readonly=False)
    w.show()
    sys.exit(app.exec())

