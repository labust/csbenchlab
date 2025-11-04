from PyQt6.QtWidgets import *
from PyQt6 import uic, QtCore

class PluginSelectorWidget(QMainWindow):
    def __init__(self, plugin_type, on_select, parent=None):
        QMainWindow.__init__(self, parent=parent)
        uic.loadUi('ui/tree_selector.ui', self)
        self.app = parent.app
        self.env_data = self.app.env_data
        self.on_select = on_select
        self.plugin_type = plugin_type
        self.init_plugins()

        self.selectBtn.clicked.connect(self.on_select_clicked)
        self.cancelBtn.clicked.connect(self.on_cancel_clicked)
        self.treeWidget.itemClicked.connect(self.on_item_clicked)

    def on_item_clicked(self, item, column):
        # hide select button if item has no parent
        if item.parent() is None:
            self.selectBtn.setEnabled(False)
        else:
            self.selectBtn.setEnabled(True)

    def on_select_clicked(self):
        item = self.treeWidget.currentItem()
        if item is not None:
            if item.parent() is None:
                return
            par = item.parent().text(0)
            plugins = self.plugins[par][self.plugin_type]
            if not isinstance(plugins, list):
                plugins = [plugins]
            plugin = [x for x in plugins if x['Name'] == item.text(0)]
            if len(plugin) == 0:
                return
            self.on_select(plugin[0])
            self.close()

    def on_cancel_clicked(self):
        self.close()

    def init_plugins(self):
        self.treeWidget.clear()
        self.plugins = self.app.backend.get_available_plugins()

        for lib_name, lib in self.plugins.items():
            lib_item = QTreeWidgetItem(self.treeWidget)
            lib_item.setText(0, lib_name)
            plugins = lib.get(self.plugin_type, None)
            if plugins is None:
                continue
            if not isinstance(plugins, list):
                plugins = [plugins]
            for comp in plugins:
                comp_item = QTreeWidgetItem(lib_item)
                comp_item.setText(0, comp['Name'])