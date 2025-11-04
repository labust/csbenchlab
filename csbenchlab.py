
from qt.csb_pyqt import CSBenchlabGUI
from PyQt6.QtWidgets import QApplication
import os


if __name__ == '__main__':
    import sys, argparse

    app = QApplication(sys.argv)

    parser = argparse.ArgumentParser(description='CSB Environment GUI')
    parser.add_argument('-backend', type=str, default='matlab', choices=['matlab', 'py'], help='Backend to use (default: matlab)')
    parser.add_argument('--daemon-restart', action="store_true", default=False, help="Force restart daemon.")
    parser.add_argument('--debug', action="store_true", default=False, help="Enable debug mode.")
    args = parser.parse_args()

    if args.backend == 'matlab':
        from matlab.matlab_backend import MatlabBackend
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

    w = CSBenchlabGUI(backend, debug=args.debug)
    w.show()
    sys.exit(app.exec())