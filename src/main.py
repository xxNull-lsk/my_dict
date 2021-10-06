#!/bin/python3
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

from src.MainWindow import MainWindow


def main():
    # os.environ['QT_DEBUG_PLUGINS'] = '1'
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    app.setApplicationName("我的词典")
    app.setQuitOnLastWindowClosed(False)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
