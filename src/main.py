#!/bin/python3
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

from src.main_window import MainWindow
from src.setting import setting


def main():
    # os.environ['QT_DEBUG_PLUGINS'] = '1'
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    if setting.use_dark_skin:
        import qdarkstyle
        dark_stylesheet = qdarkstyle.load_stylesheet_pyqt5()
        app.setStyleSheet(dark_stylesheet)
    app.setApplicationName("MyDict")
    app.setQuitOnLastWindowClosed(False)
    main_window = MainWindow()
    if setting.show_main_window_when_startup:
        main_window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
