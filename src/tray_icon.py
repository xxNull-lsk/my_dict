import sys

from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction, QMessageBox

from src.util import resource_path


class TrayIcon(QSystemTrayIcon):
    def __init__(self, parent=None):
        super(TrayIcon, self).__init__(parent)
        self.menu = QMenu()
        self.menu.addAction(QAction("关于", parent, triggered=self.on_about))
        self.menu.addAction(QAction("主窗口", parent, triggered=self.on_show))
        self.menu.addSeparator()
        self.menu.addAction(QAction("退出", parent, triggered=self.on_quit))
        self.setContextMenu(self.menu)
        ico_dict = QIcon(QPixmap(resource_path("./res/dict.png")))
        self.setIcon(ico_dict)

    def on_quit(self):
        self.setVisible(False)
        sys.exit()

    @staticmethod
    def on_about():
        QMessageBox.about(None, "关于", "我的字典")

    def on_show(self):
        self.parent().show()
