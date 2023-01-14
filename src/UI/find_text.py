from PyQt5.QtWidgets import QWidget, QPushButton, QTextEdit, QVBoxLayout, QHBoxLayout

from src.UI.result import ResultWindow
from src.backend.online import OnLine
from src.util import load_icon


class FindText(QWidget):
    def __init__(self, online: OnLine, parent=None):
        super().__init__(parent)

        self.online = online
        self.btn_clear = QPushButton("清空")
        self.btn_clear.setMinimumWidth(120)
        self.btn_clear.clicked.connect(lambda: self.edit_text.clear())
        self.btn_find = QPushButton("翻译")
        self.btn_find.setIcon(load_icon("find"))
        self.btn_find.setMinimumWidth(120)
        self.btn_find.clicked.connect(self.on_find)

        self.edit_text = QTextEdit()
        self.edit_text.setPlaceholderText("在此处输入或者“粘贴”要翻译的文本")

        self.result = ResultWindow(self)

        hbox = QHBoxLayout()
        hbox.setSpacing(8)
        hbox.addStretch(1)
        hbox.addWidget(self.btn_clear)
        hbox.addWidget(self.btn_find)

        vbox = QVBoxLayout()
        vbox.addWidget(self.edit_text)
        vbox.addItem(hbox)
        vbox.addWidget(self.result)

        self.setLayout(vbox)

    def on_find(self):
        if self.edit_text.toPlainText() == '':
            return
        txt = self.edit_text.toPlainText()
        self.result.reset(txt)
        self.online.translate(txt)

    def showEvent(self, e) -> None:
        super().showEvent(e)
        self.edit_text.setFocus()
