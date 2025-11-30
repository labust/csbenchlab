
from csb_qt.csb_pyqt import CSBenchlabGUI
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor

import os


def main():
    import sys, argparse

    app = QApplication(sys.argv)

    parser = argparse.ArgumentParser(description='CSB Environment GUI')
    parser.add_argument('--daemon-restart', action="store_true", default=False, help="Force restart daemon.")
    parser.add_argument('--debug', action="store_true", default=False, help="Enable debug mode.")
    args = parser.parse_args()

    root_path = os.path.dirname(os.path.abspath(__file__))
    ui_path = os.path.join(root_path, 'ui')

    w = CSBenchlabGUI(ui_path, debug=args.debug, daemon_restart=args.daemon_restart)
    w.show()
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#eeeeee"))

    palette.setColor(QPalette.ColorRole.Base, QColor("#FFFFFF"))

    palette.setColor(QPalette.ColorRole.WindowText, QColor("#2C2C2C"))
    palette.setColor(QPalette.ColorRole.Text, QColor("#2C2C2C"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#2C2C2C"))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#2C2C2C"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#ff7e67"))

    palette.setColor(QPalette.ColorRole.Dark, QColor("#BBBBBB"))

    app.setPalette(palette)   

    app.setStyleSheet("""
                      
* {
    font-family: 'Inter';
    font-size: 10pt;
}

QTreeView::item:selected {
    background-color: #ff7e67;  
    color: white; 
    border: none;
    outline: 0
}
                      
QListWidget::item:selected {
    background-color: #ff7e67;  
    color: white; 
    border: none;
    outline: 0;
}

QPushButton {
    border: 1px solid #6c757d;
    color: white;
    background-color: #6c757d;
    border-radius: 6px;
    padding: 3px 6px;
}

QPushButton:hover {
    background-color: #5a6268;
    border: 1px solid #5a6268;
    color: white;
}
                      
#newEnvironmentBtn, #openEnvironmentBtn, #removeEnvironmentBtn, #saveBtn, #closeBtn, #registerComponentBtn, #unregisterComponentBtn {
    border: 1px solid #6c757d;
    background-color: #eeeeee;
    color: #6c757d;                  
}

#newEnvironmentBtn:hover, #openEnvironmentBtn:hover, #removeEnvironmentBtn:hover, #saveBtn:hover, #closeBtn:hover, #registerComponentBtn:hover, #unregisterComponentBtn:hover {
    background-color: #6c757d;
    color: white;
}
                      
#pluginManagerBtn {
    background-color: #6c757d;
    border: 1px solid #6c757d;
    color: white;             
}
                      
#pluginManagerBtn:hover {
    background-color: #606970;
    border: 1px solid #606970;
    color: white;             
}

QComboBox QAbstractItemView {
    background-color: white; 
    color: black;
    selection-background-color: white;
    selection-color: white;
    outline: 0; 
    border: none; 
}
                      
QComboBox QAbstractItemView::item {
    border-left: 3px solid white;
    color: black;
}
                      
QComboBox QAbstractItemView::item:hover {
    border-left: 3px solid #ff7e67;
    color: black;
}

QComboBox QAbstractItemView::item:selected {
    color: black;
    border-left: 3px solid #ff7e67;
}
                      
QGroupBox {
    border: 1px solid #BBBBBB;
    border-radius: 5px;
    padding: 15px;
}
                      
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
}
                      
QLineEdit {
    border: none;
    border-bottom: 1px solid #ccc;
    outline: none;
    background: white;
}

QLineEdit:focus {
    border: none;
    border-bottom: 1px solid #ff7e67; 
    outline: none;
}

QCheckBox::indicator {
    width: 12px;    
    height: 12px;
    border: 1px solid #6c757d;
    background: white;
    border-radius: 6px;
}

QCheckBox::indicator:hover {
    border-color: #ff7e67;
}

QCheckBox::indicator:checked {
    background-color: #ff7e67;
    border-color: black;
}

""")

    sys.exit(app.exec())

if __name__ == '__main__':
    main()