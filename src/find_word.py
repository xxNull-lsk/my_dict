from PyQt5.QtWidgets import QWidget, QLineEdit, QPushButton, QTextEdit, QHBoxLayout, QVBoxLayout


class FindWord(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.edit_word = QLineEdit()
        self.btn_find = QPushButton("查询")
        self.btn_find.clicked.connect(self.on_find)

        self.edit_result = QTextEdit()

        hbox = QHBoxLayout()
        hbox.setSpacing(5)
        hbox.addWidget(self.edit_word)
        hbox.addWidget(self.btn_find)

        vbox = QVBoxLayout()
        vbox.addItem(hbox)
        vbox.addWidget(self.edit_result)

        self.setLayout(vbox)

    def on_find(self):
        pass
