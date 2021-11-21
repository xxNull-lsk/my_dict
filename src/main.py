#!/bin/python3
import fcntl
import json
import os
import sys

from PyQt5.QtWidgets import QApplication
from src.util import version

flock = None


def is_running():
    global flock
    lock_folder = '/tmp'
    flock = open(os.path.join(lock_folder, "my_dict.lock"), 'w+')
    try:
        fcntl.flock(flock, fcntl.LOCK_NB | fcntl.LOCK_EX)
        return False
    except:
        return True


def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == '-v':
            print(version["curr"])
            return
        elif sys.argv[1] == '-i':
            print(json.dumps(version, ensure_ascii=False))
            return
    if is_running():
        print("The application is running...")
        return
    from src.setting import setting
    # os.environ['QT_DEBUG_PLUGINS'] = '1'
    # QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    app.setApplicationName("MyDict")
    app.setQuitOnLastWindowClosed(False)
    from src.main_window import MainWindow
    main_window = MainWindow(app)
    if setting.show_main_window_when_startup:
        main_window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
