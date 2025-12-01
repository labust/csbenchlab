from PyQt6.QtWidgets import *
from PyQt6 import uic, QtCore
import sys, os
import subprocess
from pathlib import Path
from csb_qt.qt_utils import do_in_thread

plugin_types = {
    'ctl': 'Controllers',
    'sys': 'Systems',
    'est': 'Estimators',
    'dist': 'Disturbances',
}

class CSBPluginManager(QMainWindow):
    def __init__(self, backend, parent=None):
        QMainWindow.__init__(self, parent=parent)

        self.ui_path = parent.ui_path if parent is not None else ''
        uic.loadUi(os.path.join(self.ui_path, 'plugin_manager.ui'), self)
        self.backend = backend
        self.load_plugins()
        self.init()
        self.active_plugins = []
        self.libraryListWidget.setCurrentRow(0)


    def init(self):
        self.libraryListWidget.itemSelectionChanged.connect(self.on_library_selected)
        self.libraryListWidget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        for t in plugin_types.values():
            tab = QWidget()
            layout = QVBoxLayout()
            tab.setLayout(layout)
            # add on tab select
            self.tabWidget.addTab(tab, t)
        self.tabWidget.currentChanged.connect(self.on_tab_selected)

        # on app click, remove active plugins
        self.centralwidget.mousePressEvent = self.on_app_clicked
        self.openContextBtn.clicked.connect(self.open_context)

        self.registerComponentBtn.clicked.connect(self.register_component)
        self.unregisterComponentBtn.clicked.connect(self.unregister_component)
        self.refreshLibraryBtn.clicked.connect(self.refresh_library)
        self.unregisterLibraryBtn.clicked.connect(self.unregister_library)
        self.createLibraryBtn.clicked.connect(self.create_library)

        self.exportLibraryBtn.clicked.connect(self.export_library)
        self.installLibraryBtn.clicked.connect(self.install_library)
        self.linkLibraryBtn.clicked.connect(self.link_library)

    def on_app_clicked(self, event):
        self.clear_selected_plugins()

    def ask_library_path(self):

        fileName, _ = QFileDialog.getOpenFileName(self, "Select Library File", "",
                                                  "Shared Library File (*.json)")
        # check that it is package.json
        if fileName and os.path.basename(fileName) == "package.json":
            return fileName
        return None


    def log(self, msg):
        from datetime import datetime
        t_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        max_lines = 1000
        cursor = self.logTxt.textCursor()
        if self.logTxt.document().blockCount() > max_lines:
            # clear last 100 lines
            cursor.movePosition(cursor.End)
            for _ in range(100):
                cursor.select(cursor.LineUnderCursor)
                cursor.removeSelectedText()
                cursor.deleteChar()
            self.logTxt.setTextCursor(cursor)
        cursor.setPosition(0)
        self.logTxt.setTextCursor(cursor)
        self.logTxt.insertPlainText(f"[{t_now}] {msg}\n")

    def register_component_library(self, link_install):
        path = self.ask_library_path()
        if path is None:
            self.log("Invalid library file selected.")
            return
        self.log(f"Registering library from '{path}'. This may take a few moments...")

        def on_finish(result, error):
            if error is not None:
                self.log(f"Failed to register library from '{path}': {error}")
                return
            self.log("Library registered.")
            self.load_plugins()

        def run():
            self.backend.register_component_library(Path(path).parent, int(link_install), 0)

        self._do_fn(run, on_finish)

    def create_library(self):

        name, ok = QInputDialog.getText(self, 'Create Library', 'Enter library name:')
        if not ok or not name:
            self.log("Invalid library name.")
            return
        self.log(f"Creating library '{name}'. This may take a few moments...")

        self.backend.get_or_create_component_library(name)
        self.load_plugins()
        self.fill_tab(self.tabWidget.currentIndex())
        self.log(f"Library '{name}' created.")

    def install_library(self):
        self.register_component_library(link_install=False)

    def link_library(self):
        self.register_component_library(link_install=True)


    def export_library(self):
        lib = self.get_active_library()
        if lib is None:
            QMessageBox.warning(self, "Warning", "No library selected.")
            return
        export_path = QFileDialog.getExistingDirectory(self, "Select Export Directory", "")
        if not export_path:
            self.log("Invalid export directory selected.")
            return
        pass
        self.backend.export_component_library(lib, export_path)
        self.log(f"Library '{lib}' exported to '{export_path}'.")

    def refresh_library(self):

        lib = self.get_active_library()
        if lib is None:
            QMessageBox.warning(self, "Warning", "No library selected.")
            return
        self.log(f"Refreshing library '{lib}'. This may take a few moments...")

        def on_finish(result, error):
            if error is not None:
                self.log(f"Failed to refresh library '{lib}': {error}")
                return
            self.log(f"Library '{lib}' refreshed.")
            self.load_plugins()
            self.fill_tab(self.tabWidget.currentIndex())
            self.setEnabled(True)

        def run():
            self.backend.refresh_component_library(lib)

        self._do_fn(run, on_finish)

    def register_component(self):
        lib = self.get_active_library()
        if lib is None:
            QMessageBox.warning(self, "Warning", "No library selected.")
            return
        # .m, .py or .slx files
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Component File", "",
                                                  "Component Files (*.m *.py *.slx)")
        if not file_path:
            self.log("No component file selected.")
            return

        if file_path.endswith('.slx'):
            block_path = QInputDialog.getText(self, 'Simulink Block Path',
                                              'Enter Simulink block path (e.g., subsystem/myblock):')[0]
            if not block_path:
                self.log("Invalid Simulink block path.")
                return
        l = next((l for l in self.libraries if l['Name'] == lib), None)
        # open folder in file explorer, for all os
        path = l.get('Path', None)
        if not file_path.startswith(path):
            # ask user to copy file to library path
            reply = QMessageBox.question(self, 'Copy Component File',
                                         f"The selected component file is not in the library path.\n"
                                         f"Do you want to copy it to the library '{lib}'?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                         QMessageBox.StandardButton.No)
            if reply != QMessageBox.StandardButton.Yes:
                return
            import shutil
            # copy file to library path
            dest_path = os.path.join(path, 'src', os.path.basename(file_path))
            shutil.copyfile(file_path, dest_path)
            file_path = dest_path
            self.log(f"Component file '{file_path}' copied to library '{lib}'.")

        full_component_path = file_path
        if file_path.endswith('.slx'):
            full_component_path = f"{file_path}:{block_path}"

        if not self.backend.is_supported_component_file(file_path):
            self.log(f"Unsupported component file type: '{file_path}'. Only '*.py' files are supported with python backend.")
            return

        def run():
            self.backend.register_component_from_file(full_component_path, lib)

        self.log(f"Registering component from '{file_path}' to library '{lib}'. This may take a few moments...")
        def on_finish(result, error):
            if error is not None:
                self.log(f"Failed to register component '{full_component_path}' in library '{lib}': {error}")
                return
            if result is False:
                self.log(f"Failed to register component '{full_component_path}' in library '{lib}'.")
            else:
                self.log(f"Component '{full_component_path}' registered in library '{lib}'.")
                self.load_plugins()

        self._do_fn(run, on_finish)

    def _do_fn(self, fn, on_finish):
        if self.backend.is_long_library_management:
            do_in_thread(self, fn, on_finish)
        else:
            try:
                result = fn()
                on_finish(result, None)
            except Exception as e:
                on_finish(None, e)

    def unregister_component(self):
        lib = self.get_active_library()
        if lib is None:
            QMessageBox.warning(self, "Warning", "No library selected.")
            return

        selected_plugins = self.active_plugins
        if not selected_plugins:
            QMessageBox.warning(self, "Warning", "No plugin selected.")
            return

        reply = QMessageBox.question(self, 'Unregister Component',
                                        f"Are you sure you want to unregister the selected component(s) from library '{lib}'?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                        QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes:
            return

        for p in selected_plugins:
            name = p.findChild(QLabel).text()
            self.backend.unregister_component(name, lib)
            self.log(f"Component '{name}' unregistered from library '{lib}'.")
        self.load_plugins()

    def unregister_library(self):
        # are you sure
        if self.get_active_library() is None:
            QMessageBox.warning(self, "Warning", "No library selected.")
            return
        reply = QMessageBox.question(self, 'Unregister Library',
                                     f"Are you sure you want to unregister library '{self.get_active_library()}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.backend.remove_component_library(self.get_active_library())
            self.load_plugins()
            self.fill_tab(self.tabWidget.currentIndex())

    def clear_selected_plugins(self):
        for p in self.active_plugins:
            # check if p is not deleted
            try:
                if p is not None and p.isVisible():
                    p.setStyleSheet("border: 1px solid transparent;")
            except:
                pass


        self.active_plugins = []

    def on_plugin_selected(self, widget):
        if widget:

            # if ctrl is pressed, allow multiple selection
            if not (QApplication.keyboardModifiers() & QtCore.Qt.KeyboardModifier.ControlModifier):
                self.clear_selected_plugins()
            # if already selected, deselect
            if widget in self.active_plugins:
                widget.setStyleSheet("border: 1px solid transparent;")
                self.active_plugins.remove(widget)
                return


            # set border only for this widget, not for its children
            widget.setStyleSheet("border: 1px solid #ff7e67;")
            for c in widget.children():
                if isinstance(c, QWidget):
                    c.setStyleSheet("border: 1px solid transparent;")
            self.active_plugins.append(widget)

    def get_active_library(self):
        selected_items = self.libraryListWidget.selectedItems()
        if selected_items:
            item = selected_items[0]
            return item.text()
        return None

    def on_tab_selected(self, index):
        self.fill_tab(index)


    def open_plugin_file(self, plugin):
        path = plugin.get('ComponentPath', "")
        if plugin["Type"] == 'slx':
            path = path.split(':')[0]
            self.log(f"Cannot open Simulink plugin file '{path}' from here. " \
            "Please open it from MATLAB.")
            return
        if path is not None and os.path.exists(path):
            if sys.platform == "win32":
                os.startfile(path)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", path])
            else:
                subprocess.Popen(["xdg-open", path])
        else:
            QMessageBox.warning(self, "Warning", "Plugin file path not found.")

    def open_context(self):

        lib = self.get_active_library()
        if lib is None:
            lib = self.libraryListWidget.item(0).text()

        l = next((l for l in self.libraries if l['Name'] == lib), None)
        # open folder in file explorer, for all os
        path = l.get('Path', None)
        if path is not None and os.path.exists(path):
            if sys.platform == "win32":
                os.startfile(path)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", path])
            else:
                subprocess.Popen(["xdg-open", path])
        else:
            QMessageBox.warning(self, "Warning", "Library path not found.")

    def on_plugin_double_clicked(self, plugin):
        # open plugin file
        self.open_plugin_file(plugin)


    def fill_tab(self, index):

        if self.libraryListWidget.count() == 0:
            return

        lib = self.get_active_library()
        if lib is None:
            lib = self.libraryListWidget.item(0).text()
        plugins = self.plugins.get(lib, {})
        plugin_type = list(plugin_types.keys())[index]
        plugin_list = plugins.get(plugin_type, [])
        if not isinstance(plugin_list, list):
            plugin_list = [plugin_list]
        lay = QVBoxLayout()
        w = QWidget()
        w.setLayout(lay)

        plugin_list.append({
            "Name": "LQR",
            "Type": "slx",
        })

        plugin_list.append({
            "Name": "Sliding Mode",
            "Type": "slx",
        })

        plugin_list.append({
            "Name": "H infinity",
            "Type": "slx",
        })


        for i, p in enumerate(plugin_list):
            item_lay = QHBoxLayout()
            label = QLabel(p['Name'])
            item_lay.addWidget(label)
            lib_label = QLabel(f"({lib})")
            item_lay.addWidget(lib_label)
            typ_label = QLabel(f"({p['Type']})")
            item_lay.addWidget(typ_label)
            item_lay.addStretch()
            # set border when active on click and callback
            item_lay_widget = QWidget()
            item_lay_widget.setLayout(item_lay)
            item_lay_widget.setObjectName("pluginItem")
            item_lay_widget.setStyleSheet("border: 1px solid transparent;")
            item_lay_widget.mousePressEvent = lambda event, w=item_lay_widget: self.on_plugin_selected(w)
            item_lay_widget.mouseDoubleClickEvent = lambda event, p=p: self.on_plugin_double_clicked(p)
            lay.addWidget(item_lay_widget)


        # if clicked, show details
        lay.addStretch()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(w)
        current_tab = self.tabWidget.widget(index)
        # clear current tab layout
        for i in reversed(range(current_tab.layout().count())):
            current_tab.layout().itemAt(i).widget().setParent(None)
        current_tab.layout().addWidget(scroll)


    def on_library_selected(self):
        self.fill_tab(self.tabWidget.currentIndex())

    def fill_data(self):
        self.libraryListWidget.clear()
        for lib, p in self.plugins.items():
            item = QListWidgetItem(lib)
            item.setData(QtCore.Qt.ItemDataRole.UserRole, p)
            self.libraryListWidget.addItem(item)

    def load_plugins(self):
        self.plugins = self.backend.get_available_plugins()
        self.libraries = self.backend.list_component_libraries()
        self.fill_data()

