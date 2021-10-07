from PyQt5.QtWidgets import QWidget, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout

from src.UI.result import ResultWindow
from src.util import load_icon
from src.youdao import YouDaoFanYi


class FindWord(QWidget):
    def __init__(self, youdao: YouDaoFanYi, parent=None):
        super().__init__(parent)

        self.youdao = youdao
        self.edit_word = QLineEdit()
        self.edit_word.setPlaceholderText("搜索单词")
        self.edit_word.setClearButtonEnabled(True)
        self.btn_find = QPushButton("查询")
        self.btn_find.setMinimumWidth(120)
        self.btn_find.clicked.connect(self.on_find)
        self.btn_find.setIcon(load_icon("find"))

        self.result = ResultWindow(self)

        hbox = QHBoxLayout()
        hbox.setSpacing(5)
        hbox.addWidget(self.edit_word)
        hbox.addWidget(self.btn_find)

        vbox = QVBoxLayout()
        vbox.addItem(hbox)
        vbox.addWidget(self.result)

        self.setLayout(vbox)

    def on_find(self):
        if self.edit_word.text() == '':
            return
        result = self.youdao.translate_word(self.edit_word.text())
        self.result.show_word_result(result)
