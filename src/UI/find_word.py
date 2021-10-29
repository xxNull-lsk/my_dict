from PyQt5.QtWidgets import QWidget, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout

from src.backend.online import OnLine
from src.setting import setting
from src.UI.result import ResultWindow
from src.backend.stardict import StartDict
from src.util import load_icon


class FindWord(QWidget):
    def __init__(self, online: OnLine, star_dict: StartDict, parent=None):
        super().__init__(parent)
        self.star_dict = star_dict
        self.online = online
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
        word = self.edit_word.text().strip()
        self.result.reset(word)
        self.online.translate(word)
        res = self.star_dict.translate_word(word)
        for k in res.keys():
            if res[k] == '':
                continue
            count = len(setting.dicts_for_query)
            if count < 1:
                continue
            if k in setting.dicts_for_query\
                    or (count == 1 and setting.dicts_for_query[0] == "*"):
                self.result.add_word_result(k, res[k])
