from PyQt5.QtCore import QSize, QRect
from PyQt5.QtGui import QPalette, QBrush, QColor
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QDesktopWidget, QTabWidget, QMainWindow
from qdarkstyle import LightPalette

from src.backend.google import Google
from src.backend.online import OnLine
from src.backend.stardict import StartDict
from src.events import events
from src.setting import setting
from src.UI.find_text import FindText
from src.UI.find_word import FindWord
from src.UI.tip_window import TipWindow
from src.UI.setting import SettingWindow
from src.tray_icon import TrayIcon
from src.util import load_icon, get_version
from src.backend.youdao import YouDaoFanYi


class MainWindow(QWidget):
    btn_action = []

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.on_setting_changed()
        events.signal_setting_changed.connect(self.on_setting_changed)

        self.setGeometry(QRect(0, 0, 800, 600))
        self.tray = TrayIcon(self)
        self.tray.show()

        self.setWindowIcon(load_icon("dict"))
        self.setWindowTitle("我的词典 {}".format(get_version()))

        self.online = OnLine()
        self.star_dict = StartDict(setting.star_dict_folder, True)
        self.tip_window = TipWindow(self.online, self.star_dict, app)
        self.tip_window.hide()

        self.tab = QTabWidget()
        self.tab.addTab(FindWord(self.online, self.star_dict, self), '词典')
        self.tab.addTab(FindText(self.online, self), '翻译')
        self.tab.addTab(SettingWindow(self, self.star_dict), '设置')
        self.tab.tabBar().setMinimumWidth(200)
        self.tab.tabBar().setTabIcon(0, load_icon("word"))
        self.tab.tabBar().setTabIcon(1, load_icon("text"))
        self.tab.tabBar().setTabIcon(2, load_icon("setting"))

        hbox = QHBoxLayout()
        hbox.addWidget(self.tab)
        self.setLayout(hbox)

        self.center()

    def on_setting_changed(self):
        import qdarkstyle
        if setting.use_dark_skin:
            dark_stylesheet = qdarkstyle.load_stylesheet_pyqt5()
            self.app.setStyleSheet(dark_stylesheet)
        else:
            style = qdarkstyle.load_stylesheet(palette=LightPalette)
            self.app.setStyleSheet(style)
            # self.app.setStyleSheet("")

    def center(self):
        rect = self.frameGeometry()
        pt = QDesktopWidget().availableGeometry().center()
        rect.moveCenter(pt)
        self.move(rect.topLeft())

    def show(self) -> None:
        super(MainWindow, self).show()
        self.center()
