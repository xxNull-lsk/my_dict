from PyQt5.QtWidgets import QWidget, QLineEdit, QPushButton, QTextEdit, QHBoxLayout, QVBoxLayout


class FindText(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.btn_find = QPushButton("查询")
        self.btn_find.clicked.connect(self.on_find)

        self.edit_text = QTextEdit()
        self.edit_result = QTextEdit()

        vbox = QVBoxLayout()
        vbox.addWidget(self.edit_text)
        vbox.addWidget(self.btn_find)
        vbox.addWidget(self.edit_result)

        self.setLayout(vbox)

    def on_find(self):
        pass
