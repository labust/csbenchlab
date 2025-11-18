
from qt.csb_pyqt import CSBenchlabGUI
from PyQt6.QtWidgets import QApplication
import os
from csbenchlab.source_libraries import source_libraries
from csbenchlab.csb_app_setup import get_appdata_dir


if __name__ == '__main__':
    import sys, argparse

    app = QApplication(sys.argv)

    parser = argparse.ArgumentParser(description='CSB Environment GUI')
    parser.add_argument('--daemon-restart', action="store_true", default=False, help="Force restart daemon.")
    parser.add_argument('--debug', action="store_true", default=False, help="Enable debug mode.")
    args = parser.parse_args()

    w = CSBenchlabGUI(debug=args.debug, daemon_restart=args.daemon_restart)
    w.show()
    sys.exit(app.exec())
