from PyQt6.QtWidgets import *
from PyQt6 import uic
import sys, os

from csbenchlab.environment_data_manager import EnvironmentDataManager
from uuid import uuid4
from copy import deepcopy
from pathlib import Path

from widgets import SystemWidget, ControllerWidget, ScenarioWidget, MetricWidget, EnvironmentWidget
from csb_qt.qt_utils import clear_form_layout, open_file_in_editor
from csbenchlab.data_desc import COMPONENT_DATA_DESC

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

class CSBEnvGui(QMainWindow):
    def __init__(self, env_path, backend, parent=None, readonly=False, debug=False):
        QMainWindow.__init__(self, parent=parent)
        self.ui_path = parent.ui_path if parent is not None else ''
        uic.loadUi(os.path.join(self.ui_path, 'env_manager.ui'), self)
        self.backend = backend
        self.env_path = env_path
        self.env_manager = EnvironmentDataManager(env_path)
        self.env_data = self.env_manager.load_environment_data()
        # set title
        self.setWindowTitle(f"CSB Environment - {self.env_data.metadata.get('Name', '')}")
        self._readonly = readonly
        self.debug = debug

        self.treeWidget.itemClicked.connect(self.on_item_clicked)
        self.fill_tree_view()


        # capture all clicks on the app
        self.on_app_click = self.on_app_click
        self.centralwidget.mousePressEvent = self.on_app_click
        self.widgetBox.mousePressEvent = self.on_app_click
        self.widget_changed = dict()
        self.active_editable_labels = []
        self.selected_labels = []

        # click on first item
        self.treeWidget.setCurrentItem(self.treeWidget.topLevelItem(0).child(0))

    def on_app_click(self, event):
        # check if any editable label is in edit mode
        for lbl in self.active_editable_labels:
            if lbl.line_edit.isVisible():
                lbl.finish_edit()
        for lbl in self.selected_labels:
            lbl.finish_edit()
        self.selected_labels = []
        self.active_editable_labels = []
        event.ignore()


    def export_component(self, widget, export_folder):
        component = widget.data
        if component is None:
            self.log("Cannot export component: invalid component")
            return

        rel_path = COMPONENT_DATA_DESC.get(component.get('ComponentType', ''), None)
        comp_path = self.env_path / rel_path[0] / component['Id']
        self.env_manager.export_component(comp_path, export_folder)
        self.log(f"Exported component '{component.get('Name', '')}' to '{export_folder}'")

    def import_component(self, widget, import_path):
        import_path = Path(import_path)
        if not import_path.exists():
            self.log(f"Import path does not exist: {import_path}")
            return

        component = self.env_manager.import_component(import_path)
        component_type = component.get("ComponentType", None)
        if component_type is None:
            self.log("Invalid component file: missing ComponentType")
            return

        # add component to env data
        idx = widget.index
        container = self.get_container(widget)
        self.remove_component(widget, False)  # remove current component
        self.on_widget_save(widget)
        if idx >= len(container):
            container.append(component)
        else:
            container.insert(idx, component)
        self.fill_tree_view()
        self.set_widget(widget.__class__(widget.index, component, self))
        self.record_widget_change(widget)
        self.log(f"Imported component '{component.get('Name', '')}' from '{import_path}'")

    def add_subcomponent(self, dcls, parent_widget, field_name):
        container = self.get_container(parent_widget.__class__)
        d = dcls.as_dict()
        container = parent_widget.data[field_name]
        d["Name"] = self.make_name_unique(f"New {dcls.__name__}", container)
        d["ParentComponentId"] = parent_widget.data['Id']
        d["ParentComponentType"] = parent_widget.data['ComponentType']

        if field_name not in parent_widget.data:
            raise Exception(f"Field name {field_name} does not exist")

        if isinstance(parent_widget.data[field_name], list):
            parent_widget.data[field_name].append(d)
        else:
            parent_widget.data[field_name] = d

        self.record_widget_change(parent_widget)
        self.log(f"Added new {dcls.__name__.lower()}: {d['Name']}")
        return d

    def add_component(self, widget_cls):
        container = self.get_container(widget_cls)
        dcls = self.get_dataclass(widget_cls)
        d = dcls.as_dict()
        d["Name"] = self.make_name_unique(f"New {dcls.__name__}", container)
        container.append(d)
        w = widget_cls(len(container)-1, d, self)
        self.fill_tree_view()
        self.set_widget(w)

        self.record_widget_change(w)
        self.log(f"Added new {dcls.__name__.lower()}: {d['Name']}")
        return d


    def duplicate_subcomponent(self, original_data, parent_widget, field_name, modified_data=None):
        subc = original_data[field_name]
        if not subc:
            return modified_data
        if modified_data is None:
            modified_data = deepcopy(original_data)

        def duplicate_item(original, new):
            new["Id"] = str(uuid4())
            new["ParentComponentId"] = modified_data["Id"]
            if self.env_manager.has_component_params(original):
                self.env_manager.duplicate_component_params(original, new)
            if self.env_manager.has_files(original):
                self.env_manager.duplicate_files(original_data, new)

        modified = modified_data[field_name]
        if isinstance(subc, list):
            for i, it in enumerate(subc):
                duplicate_item(subc[i], modified[i])
        else:
            duplicate_item(subc, modified)
        return modified_data

    def duplicate_component(self, widget):
        widget_cls = type(widget)
        dcls = self.get_dataclass(widget)
        container = self.get_container(widget_cls)
        original_data = container[widget.index]
        d = deepcopy(original_data)
        d["Id"] = str(uuid4())
        d["Name"] = self.make_name_unique(f"{d['Name']} (copy)", container)

        for n in d["Subcomponents"]:
            d = self.duplicate_subcomponent(original_data, widget, n, d)

        container.append(d)
        self.fill_tree_view()
        w = widget_cls(len(container)-1, d, self)
        if self.env_manager.has_component_params(original_data):
            self.env_manager.duplicate_component_params(original_data, d)
        if self.env_manager.has_files(original_data):
            self.env_manager.duplicate_files(original_data, d)
        self.set_widget(w)
        self.record_widget_change(w)
        self.log(f"Duplicated {dcls.__name__.lower()}: {d['Name']}")
        return d

    def remove_subcomponent(self, component, parent_widget, field_name, idx=-1, ask_confirmation=True):
        # prompt for confirmation
        comp_name = component["Name"]
        if ask_confirmation:
            widget_name = parent_widget.data[field_name]["Name"]
            reply = QMessageBox.question(self, 'Remove Confirmation',
                                        f"Are you sure you want to remove {comp_name} '{widget_name}'?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                        QMessageBox.StandardButton.No)
            if reply != QMessageBox.StandardButton.Yes:
                return

        obj = parent_widget.data[field_name]
        if isinstance(obj, list):
            if idx < 0:
                raise Exception("Index should be positive integer")
            obj = obj[idx]
            del parent_widget.data[field_name][idx]
        else:
            parent_widget.data[field_name] = {}

        name = obj['Name']
        self.fill_tree_view()

        new_p = parent_widget.__class__(parent_widget.index, parent_widget.data, self)
        self.set_widget(new_p)
        self.env_manager.remove_component(obj)
        self.log(f"Removed {comp_name}: {name}")
        return obj

    def remove_component(self, widget, ask_confirmation=True):
        widget_cls = type(widget)
        dcls = self.get_dataclass(widget)
        # prompt for confirmation
        container = self.get_container(widget.__class__)
        widget_name = widget.data['Name']
        if ask_confirmation:
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
        if len(container) == 0:
            w = EnvironmentWidget(self)
        else:
            idx = max(0, widget.index-1)
            if idx < len(container):
                w = widget_cls(idx, container[idx], self)
            else:
                w = EnvironmentWidget(self)
        self.set_widget(w)
        self.env_manager.remove_component(obj)
        self.log(f"Removed {dcls.__name__.lower()}: {name}")
        return obj

    def save_component(self, widget):
        if isinstance(widget, EnvironmentWidget):
            self.env_data.metadata['ComponentType'] = 'metadata'
        dcls = self.get_dataclass(widget)
        container = self.get_container(widget.__class__)
        if hasattr(widget, 'index'):
            obj = container[widget.index]
        else:
            obj = container
        name = obj['Name']
        self.env_manager.add_component(obj)
        self.on_widget_save(widget)
        self.log(f"Saved {dcls.__name__.lower()}: {name}")

    def make_name_unique(self, name, objects):
        if not isinstance(objects, list):
            objects = [objects]
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
        cursor = self.logText.textCursor()
        if self.logText.document().blockCount() > max_lines:
            # clear last 100 lines
            cursor.movePosition(cursor.End)
            for _ in range(100):
                cursor.select(cursor.LineUnderCursor)
                cursor.removeSelectedText()
                cursor.deleteChar()
            self.logText.setTextCursor(cursor)
        cursor.setPosition(0)
        self.logText.setTextCursor(cursor)
        self.logText.insertPlainText(f"[{t_now}] {msg}\n")

    def show_environment(self, index=-1):
        w = EnvironmentWidget(self.env_data.metadata, self)
        self.set_widget(w)

    def show_system(self, index):
        w = SystemWidget(index, self.env_data.systems[index], self)
        self.set_widget(w)

    def show_controller(self, index):
        w = ControllerWidget(index, self.env_data.controllers[index], self)
        self.set_widget(w)

    def show_scenario(self, index):
        w = ScenarioWidget(index, self.env_data.scenarios[index], self)
        self.set_widget(w)

    def show_metric(self, index):
        w = MetricWidget(index, self.env_data.metrics[index], self)
        self.set_widget(w)

    def select_widget(self, w):
        if isinstance(w, SystemWidget):
            self.treeWidget.setCurrentItem(self.roots[0].child(w.index))
        elif isinstance(w, ControllerWidget):
            self.treeWidget.setCurrentItem(self.roots[1].child(w.index))
        elif isinstance(w, ScenarioWidget):
            self.treeWidget.setCurrentItem(self.roots[2].child(w.index))
        elif isinstance(w, MetricWidget):
            self.treeWidget.setCurrentItem(self.roots[3].child(w.index))
        else:
            pass

    def set_widget(self, w, copy=False):
        if copy:
            w = w.__class__(w.index, w.data, self)
        clear_form_layout(self.widgetBox)
        self.widgetBox.addWidget(w)
        self.select_widget(w)

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

    def set_widget_title(self, widget, title):
        tree = self.treeWidget
        item = tree.currentItem()
        id = self.make_widget_id(widget)
        has_changes = self.widget_changed.get(id, False)
        if has_changes:
            title += '*'
        if item is not None:
            if env_has_to_be_changed(item):
                root = tree.topLevelItem(0)
                root.setText(0, title)
                return
            else:
                item.setText(0, title)

    def on_widget_save(self, widget, save_fn=None):

        id = self.make_widget_id(widget)
        changed = self.widget_changed.get(id, False)
        if not changed:
            return

        if save_fn is not None:
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

    def has_unsaved_changes(self):
        for k, v in self.widget_changed.items():
            if v:
                return True
        return False

    def set_component_params(self, component):
        # load component parameters from backend
        if 'PluginImplementation' not in component or \
           'PluginName' not in component or \
           'Lib' not in component:
            return

        if component['PluginImplementation'] == 'py':
            info = self.backend.get_plugin_info_from_lib(
                component['PluginName'],
                component['Lib']
            )
            params = self.env_manager.load_py_component_params(component, info["ComponentPath"])
        else:
            params = self.backend.get_component_params(
                component['PluginImplementation'],
                component['PluginName'],
                component['Lib'],
            )
        if params is None:
            params = {}
        self.env_manager.set_component_params(component, params)


    def open_component_context(self, widget):
        component = widget.data
        desc = COMPONENT_DATA_DESC.get(component.get('ComponentType', ''), None)
        if desc is None:
            self.log("Cannot open context. Invalid component")
            return
        path = Path(self.env_path) / desc["destination_path"] / component['Id']
        open_file_in_editor(path)


    def make_widget_id(self, widget):
        id = str(widget.__class__)
        if hasattr(widget, 'index'):
            id += str(widget.index)
        return id

    def get_container(self, widget_cls):
        if issubclass(widget_cls, SystemWidget):
            return self.env_data.systems
        elif issubclass(widget_cls, ControllerWidget):
            return self.env_data.controllers
        elif issubclass(widget_cls, ScenarioWidget):
            return self.env_data.scenarios
        elif issubclass(widget_cls, MetricWidget):
            return self.env_data.metrics
        elif issubclass(widget_cls, EnvironmentWidget):
            return self.env_data.metadata
        return None

    def get_dataclass(self, widget_cls):
        if hasattr(widget_cls, 'model'):
            return widget_cls.model
        raise ValueError("Unknown widget type")

if __name__ == '__main__':
    import sys, argparse

    app = QApplication(sys.argv)

    parser = argparse.ArgumentParser(description='CSB Environment GUI')
    parser.add_argument('env_path', type=str, help='Path to environment folder')
    parser.add_argument('--readonly', action='store_true', default=False, help='Open in read-only mode')
    parser.add_argument('-backend', type=str, default='matlab', choices=['matlab', 'py'], help='Backend to use (default: matlab)')
    parser.add_argument('--daemon-restart', action="store_true", default=False, help="Force restart daemon.")
    args = parser.parse_args()

    if args.backend == 'matlab':
        from ..csb_matlab.matlab_backend import MatlabBackend
        backend = MatlabBackend(restart_daemon=args.daemon_restart)
        backend.start()
        print("Using matlab backend with csb path:", backend.csb_path)
    elif args.backend == 'py':
        from backend.python_backend import PythonBackend
        backend = PythonBackend()
        backend.start()
        print("Using python backend with csb path:", backend.csb_path)
    else:
        raise ValueError("Unknown backend")

    w = CSBEnvGui(args.env_path, backend, readonly=False, debug=True)
    w.show()
    sys.exit(app.exec())

