from PyQt5.QtWidgets import QWidget, QComboBox, QPushButton, QCheckBox, QTableWidget

from src.UI.util import create_line, create_multi_line
from src.backend.word_book import work_book


class WordBook(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.combo_groups = QComboBox()
        self.button_add_group = QPushButton("  添加分类  ")
        self.button_delete_group = QPushButton("  删除分类  ")

        self.button_add_word = QPushButton("  添加生词  ")
        self.button_edit_word = QPushButton("  编辑生词  ")
        self.button_delete_word = QPushButton("  删除生词  ")

        self.checkbox_select_all = QCheckBox()

        self.table = QTableWidget()

        tools = create_line([
            self.checkbox_select_all,
            self.button_add_word,
            self.button_edit_word,
            self.button_delete_word,
            1,
            self.combo_groups,
            self.button_add_group,
            self.button_delete_group,
        ])

        self.setLayout(
            create_multi_line([
                tools,
                self.table
            ])
        )
        work_book.get_groups(self.init_groups)

    def init_groups(self, group):
        self.combo_groups.addItem(group[1], group[0])
