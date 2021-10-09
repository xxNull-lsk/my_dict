from PyQt5.QtCore import QSize, QRect
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QDesktopWidget, QTabWidget, QMainWindow

from src.setting import setting
from src.UI.find_text import FindText
from src.UI.find_word import FindWord
from src.UI.clipboard import TipWindow
from src.UI.setting import SettingWindow
from src.tray_icon import TrayIcon
from src.util import load_icon, get_version
from src.backend.youdao import YouDaoFanYi


class MainWindow(QWidget):
    btn_action = []

    def __init__(self):
        super().__init__()
        self.setGeometry(QRect(0, 0, 640, 480))
        self.tray = TrayIcon(self)
        self.tray.show()

        self.setWindowIcon(load_icon("dict"))
        self.setWindowTitle("我的词典 {}".format(get_version()))

        self.youdao = YouDaoFanYi()
        if setting.support_clipboard:
            self.tip_window = TipWindow(self.youdao)
            self.tip_window.hide()

        self.tab = QTabWidget()
        self.tab.addTab(FindWord(self.youdao, self), '词典')
        self.tab.addTab(FindText(self.youdao, self), '翻译')
        self.tab.addTab(SettingWindow(self), '设置')
        self.tab.tabBar().setMinimumWidth(200)
        self.tab.tabBar().setTabIcon(0, load_icon("word"))
        self.tab.tabBar().setTabIcon(1, load_icon("text"))
        self.tab.tabBar().setTabIcon(2, load_icon("setting"))

        hbox = QHBoxLayout()
        hbox.addWidget(self.tab)
        self.setLayout(hbox)

        self.center()

    def center(self):
        rect = self.frameGeometry()
        pt = QDesktopWidget().availableGeometry().center()
        rect.moveCenter(pt)
        self.move(rect.topLeft())

    def show(self) -> None:
        super(MainWindow, self).show()
        self.center()
