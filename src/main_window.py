from PyQt5.QtCore import QRect, QTimer
from PyQt5.QtWidgets import QWidget, QDesktopWidget, QTabWidget

from src.UI.util import create_line
from src.UI.word_book import UiWordBook
from src.backend.online import OnLine
from src.backend.stardict import StartDict
from src.backend.stat import check_newest
from src.events import events
from src.setting import setting
from src.UI.find_text import FindText
from src.UI.find_word import FindWord
from src.UI.tip_window import TipWindow
from src.UI.setting import SettingWindow
from src.tray_icon import TrayIcon
from src.util import load_icon, get_version


class MainWindow(QWidget):
    btn_action = []

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.on_setting_changed()
        events.signal_setting_changed.connect(self.on_setting_changed)
        events.signal_check_newest.connect(self.on_check_newest)

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
        self.tab.addTab(FindWord(self.online, self.star_dict, self), '  词典  ')
        self.tab.addTab(FindText(self.online, self), '  翻译  ')
        self.tab.addTab(UiWordBook(self), '  生词本  ')
        self.tab.addTab(SettingWindow(self, self.star_dict), '  设置  ')
        self.tab.tabBar().setMinimumWidth(200)
        self.tab.tabBar().setTabIcon(0, load_icon("word"))
        self.tab.tabBar().setTabIcon(1, load_icon("text"))
        self.tab.tabBar().setTabIcon(2, load_icon("wordbook"))
        self.tab.tabBar().setTabIcon(3, load_icon("setting"))

        self.setLayout(create_line([self.tab]))

        self.center()
        check_newest()

    def on_setting_changed(self):
        import qdarkstyle
        if setting.use_dark_skin:
            dark_stylesheet = qdarkstyle.load_stylesheet_pyqt5()
            dark_stylesheet = dark_stylesheet.replace('QComboBox::item:checked', "XQComboBox::item:checked")
            dark_stylesheet = dark_stylesheet.replace('QComboBox::indicator', "XQComboBox::indicator")
            self.app.setStyleSheet(dark_stylesheet)
        else:
            # style = qdarkstyle.load_stylesheet(palette=LightPalette)
            # self.app.setStyleSheet(style)
            self.app.setStyleSheet("")

    def center(self):
        rect = self.frameGeometry()
        pt = QDesktopWidget().availableGeometry().center()
        rect.moveCenter(pt)
        self.move(rect.topLeft())

    def show(self) -> None:
        super(MainWindow, self).show()
        self.center()

    @staticmethod
    def on_check_newest(new_version):
        events.signal_pop_message("检测到新版本：\n{}: {}".format(
            new_version['curr'],
            new_version['history'][new_version['curr']])
        )
        # TODO：执行升级
