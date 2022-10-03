import sys

from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction, QDialog, QLabel

from src.UI.util import create_form, create_multi_line, create_line
from src.events import events
from src.util import resource_path, version, run_app


class About(QDialog):
    def __init__(self):
        super().__init__()
        url_project = QLabel(
            u'<a href="https://github.com/xxNull-lsk/my_dict">https://github.com/xxNull-lsk/my_dict</a>'
        )
        url_project.setOpenExternalLinks(True)
        url_email = QLabel(u'<a href="mailto:xxNull@163.com">联系我</a>')
        url_email.setOpenExternalLinks(True)
        layout = create_form([
            ["版本号：", QLabel(version["curr"])],
            ["项目地址：", url_project]
        ], space=16)
        self.setLayout(create_multi_line([layout, create_line([1, url_email, 1])], space=16))


class TrayIcon(QSystemTrayIcon):

    def __init__(self, parent=None):
        super(TrayIcon, self).__init__(parent)
        self.menu = QMenu()
        self.menu.addAction(QAction("关于", parent, triggered=self.on_about))
        self.menu.addAction(QAction("主窗口", parent, triggered=self.on_show))
        self.menu.addSeparator()
        self.menu.addAction(QAction("退出", parent, triggered=self.on_quit))
        self.setContextMenu(self.menu)
        self.ico_dict = QIcon(QPixmap(resource_path("./res/dict_64x64.png")))
        self.setIcon(self.ico_dict)
        self.activated.connect(self.on_activated)
        self.setToolTip("我的词典 {}".format(version["curr"]))

        events.signal_pop_message.connect(self.pop_message)

    @staticmethod
    def on_quit():
        events.signal_exit_app.emit()

    @staticmethod
    def on_about():
        About().exec()

    def on_show(self):
        self.on_activated()

    @staticmethod
    def on_activated():
        events.signal_show_main_window.emit()

    def pop_message(self, msg):
        self.showMessage("我的词典", msg, self.ico_dict)
