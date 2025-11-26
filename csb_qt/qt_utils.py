import sys, os, subprocess
from pathlib import Path
from csb_qt.worker_thread import WorkerThread

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


def open_file_in_editor(path):
    if path:
        if sys.platform == 'win32':
            os.startfile(path)
        elif sys.platform == 'darwin':  # macOS
            subprocess.call(['open', path])
        else:  # Linux, Unix
            # subprocess.call(['xdg-open', path])
            if Path(path).is_file():
                subprocess.call(['code', path])
            else:
                subprocess.call(['xdg-open', path])


def do_in_thread(parent, func, on_finish):
    parent.t = WorkerThread(parent, func)
    def on_finish_wrapper(*args):
        parent.setEnabled(True)
        on_finish(*args)
    parent.t.finished.connect(on_finish_wrapper)
    parent.t.start()
    parent.setEnabled(False)