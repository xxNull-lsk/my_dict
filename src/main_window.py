import sys

from PyQt5 import QtGui
from PyQt5.QtCore import QRect
from PyQt5.QtWidgets import QWidget, QDesktopWidget, QTabWidget, QDialog, QCheckBox

from src.UI.util import create_line, create_multi_line, create_grid
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
from src.util import load_icon, get_version, resource_path, run_app


class WarnClose(QDialog):
    def __init__(self):
        super().__init__()
        if setting.main_hotkey:
            main_hotkey = "提示： 隐藏后请通过热键（" + " - ".join(setting.main_hotkey).upper() + "）显示主窗口"
        else:
            main_hotkey = ""
        self.setWindowTitle("询问")
        self.checkbox_close = QCheckBox("立即退出(不再询问)")
        self.checkbox_close.clicked.connect(self.on_close)
        self.checkbox_hide = QCheckBox("隐藏而不退出(不再询问) ")
        self.checkbox_hide.clicked.connect(self.on_close)
        self.checkbox_close_keep_ask = QCheckBox("本次退出，保持询问")
        self.checkbox_close_keep_ask.clicked.connect(self.on_close)
        self.checkbox_hide_keep_ask = QCheckBox("本次隐藏，保持询问 ")
        self.checkbox_hide_keep_ask.clicked.connect(self.on_close)
        items = [
            [self.checkbox_close],
            [self.checkbox_hide],
            [self.checkbox_close_keep_ask],
            [self.checkbox_hide_keep_ask],
            [main_hotkey],
        ]
        self.setLayout(create_multi_line([create_grid(items)]))

    def on_close(self):
        if self.checkbox_close.isChecked():
            setting.hide_when_close = False
            setting.ask_when_close = False
            setting.save()
        elif self.checkbox_hide.isChecked():
            setting.hide_when_close = True
            setting.ask_when_close = False
            setting.save()
        elif self.checkbox_close_keep_ask.isChecked():
            setting.hide_when_close = False
        elif self.checkbox_hide_keep_ask.isChecked():
            setting.hide_when_close = True
        else:
            self.done(0)
        self.done(1)


class MainWindow(QWidget):
    btn_action = []

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.on_setting_changed()
        events.signal_setting_changed.connect(self.on_setting_changed)
        events.signal_check_newest.connect(self.on_check_newest)
        events.signal_show_main_window.connect(self.on_show)
        events.signal_exit_app.connect(self.on_exit_app)

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
        super().show()
        self.center()

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        if setting.ask_when_close:
            a = WarnClose()
            if a.exec_() == 0:
                a0.setAccepted(False)
                return

        if not setting.hide_when_close:
            self.on_exit_app()
        super().closeEvent(a0)

    def on_exit_app(self):
        cmd = "bash {} stop".format(resource_path("./res/ocr.sh"))
        run_app(cmd, print)
        self.setVisible(False)
        sys.exit(0)

    def on_show(self):
        self.activateWindow()
        self.showNormal()

    @staticmethod
    def on_check_newest(new_version):
        events.signal_pop_message("检测到新版本：\n{}: {}".format(
            new_version['curr'],
            new_version['history'][new_version['curr']])
        )
        # TODO：执行升级
