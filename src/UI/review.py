import random

from PyQt5.QtCore import QSize
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QDialog, QCheckBox, QPushButton, QLabel, QMessageBox, QTextEdit

from src.UI.util import create_line, create_multi_line
from src.backend.word_book import word_book


class UiReview(QDialog):
    words = []
    current = -1
    right_index = -1

    def __init__(self, parent, group_id):
        super().__init__(parent)
        self.setWindowTitle("复习生词")
        for word in word_book.get_words(group_id, for_review=True):
            self.words.append({
                "id": word[0],
                "word": word[1],
                "translate": word[2],
                "review_count": word[4]
            })
        self.font_word = QFont()
        self.font_word.setFamily("Mono")
        self.font_word.setPointSize(16)
        self.font_word.setWeight(75)
        self.font_word.setBold(True)

        self.setFixedSize(QSize(800, 600))
        self.label_text = QTextEdit()
        self.label_text.setReadOnly(True)
        self.label_text.setFont(self.font_word)
        self.label_text.setAcceptRichText(False)
        self.checkbox = []
        for i in range(4):
            chk = QCheckBox()
            chk.setFont(self.font_word)
            self.checkbox.append(chk)

        self.btn_next = QPushButton("  下一个  ")
        self.btn_next.setFont(self.font_word)
        self.btn_next.clicked.connect(self.on_next)

        items = [
            self.label_text,
            create_line([1, create_multi_line(self.checkbox), 1]),
            create_line([1, self.btn_next, 1])
        ]
        self.setLayout(create_multi_line(items))
        self.on_next()

    def get_error_word(self, exclude):
        while True:
            r = random.Random()
            index = r.randint(0, len(self.words) - 1)
            if index in exclude:
                continue

            return index, self.words[index]

    def on_next(self):
        if len(self.words) < len(self.checkbox):
            return
        if self.current >= 0:
            curr = self.words[self.current]
            for i in range(len(self.checkbox)):
                if self.checkbox[i].isChecked() and i != self.right_index:
                    QMessageBox.information(self, "错误", "选错了。")
                    # 如果做错了，需要加强复习一次
                    if self.words[-1] != curr:
                        self.words.append(curr)
                    return
            word_book.review_word(curr["id"], curr["review_count"] + 1)

        self.current += 1
        if self.current == len(self.words) - 1:
            self.btn_next.setText("  完成  ")
        elif self.current >= len(self.words):
            self.accept()
            return

        curr = self.words[self.current]
        r = random.Random()
        self.right_index = r.randint(0, len(self.checkbox) - 1)
        self.label_text.setText(curr["translate"])
        self.checkbox[self.right_index].setText(curr["word"])
        self.checkbox[self.right_index].setChecked(False)

        exclude = [self.current]
        for i in range(len(self.checkbox)):
            if i == self.right_index:
                continue
            index, word = self.get_error_word(exclude)
            self.checkbox[i].setText(word["word"])
            self.checkbox[i].setChecked(False)
            exclude.append(index)
