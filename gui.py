
from csb_qt.csb_pyqt import CSBenchlabGUI
from PyQt6.QtWidgets import QApplication


def main():
    import sys, argparse

    app = QApplication(sys.argv)

    parser = argparse.ArgumentParser(description='CSB Environment GUI')
    parser.add_argument('--daemon-restart', action="store_true", default=False, help="Force restart daemon.")
    parser.add_argument('--debug', action="store_true", default=False, help="Enable debug mode.")
    args = parser.parse_args()

    w = CSBenchlabGUI(debug=args.debug, daemon_restart=args.daemon_restart)
    w.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()