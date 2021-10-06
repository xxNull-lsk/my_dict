from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QMainWindow, QWidget, QStackedLayout, QHBoxLayout, QVBoxLayout, QPushButton, QDesktopWidget

from src.find_text import FindText
from src.find_word import FindWord
from src.tip_window import TipWindow
from src.tray_icon import TrayIcon


class QPageButton(QPushButton):
    index = 0
    page = None

    def __int__(self, title):
        super().__init__(title)


class MainWindow(QWidget):
    btn_action = []

    def __init__(self):
        super().__init__()
        self.setFixedSize(QSize(640, 480))
        self.tray = TrayIcon(self)
        self.tray.show()

        self.tip_window = TipWindow()
        self.tip_window.hide()

        right = QWidget(self)
        self.mainLayout = QStackedLayout(right)
        self.add_page('单词', FindWord(self))
        self.add_page('文章', FindText(self))
        right.setLayout(self.mainLayout)

        vbox = QVBoxLayout()
        vbox.setSpacing(5)
        for btn in self.btn_action:
            vbox.addWidget(btn)
        vbox.addStretch(1)
        hbox = QHBoxLayout()
        hbox.addItem(vbox)
        hbox.addWidget(right)

        self.setLayout(hbox)

        self.center()

    def add_page(self, text, page):
        self.mainLayout.addWidget(page)
        btn = QPageButton(text)
        btn.page = page
        btn.index = text
        self.btn_action.append(btn)

    def center(self):
        rect = self.frameGeometry()
        pt = QDesktopWidget().availableGeometry().center()
        rect.moveCenter(pt)
        self.move(rect.topLeft())
