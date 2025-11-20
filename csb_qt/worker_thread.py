from PyQt6 import QtCore
import time



class WorkerThread(QtCore.QThread):
    finished = QtCore.pyqtSignal(object, object)  # result, error

    def __init__(self, app, func, *args, **kwargs):
        super().__init__()
        self.app = app
        self.args = args
        self.func = func
        self.kwargs = kwargs
        self.result = None
        self.error = None

    def run(self):
        error = None
        result = None
        try:
            result = self.func(*self.args, **self.kwargs)
        except Exception as e:
            error = e
        self.finished.emit(result, error)
