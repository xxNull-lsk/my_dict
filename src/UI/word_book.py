from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QComboBox, QPushButton, QCheckBox, QTableWidget, QInputDialog, QAbstractItemView, \
    QHeaderView, QTableWidgetItem

from src.UI.util import create_line, create_multi_line
from src.backend.word_book import work_book
from src.events import events


class WordBook(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        events.signal_add_2_wordbook.connect(self.on_add_word)

        self.combo_groups = QComboBox()
        self.combo_groups.currentIndexChanged.connect(self.init_words)

        self.checkbox_select_all = QCheckBox("全选")
        self.checkbox_select_all.clicked.connect(self.on_select_all)
        self.button_add_group = QPushButton("  添加分类  ")
        self.button_add_group.clicked.connect(self.on_add_group)
        self.button_delete_group = QPushButton("  删除分类  ")
        self.button_delete_group.clicked.connect(self.on_delete_group)

        self.button_delete_word = QPushButton("  删除生词  ")
        self.button_delete_word.clicked.connect(self.on_delete_word)

        self.table = QTableWidget()
        header = ["单词", "翻译", "添加时间", "复习次数"]
        self.table.setColumnCount(len(header))
        self.table.setHorizontalHeaderLabels(header)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.horizontalHeader().setResizeContentsPrecision(QHeaderView.ResizeToContents)
        self.table.itemDoubleClicked.connect(self.on_double_clicked)

        tools = create_line([
            self.checkbox_select_all,
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
        self.init_groups()

    def init_groups(self):
        self.combo_groups.clear()
        for group in work_book.get_groups():
            self.combo_groups.addItem(group[1], group[0])

        self.update_ui()
        self.init_words()
        return True

    def update_ui(self):
        self.button_delete_group.setEnabled(self.combo_groups.currentIndex() > 0)

    def init_words(self):
        for i in range(self.table.rowCount()):
            self.table.removeRow(0)
        for word in work_book.get_words(self.combo_groups.currentData()):
            self.table.insertRow(0)
            for i in range(len(word) - 1):
                item = QTableWidgetItem(str(word[i + 1]))
                if i == 0:
                    item.setCheckState(Qt.Unchecked)
                    item.setData(Qt.UserRole, word[0])
                elif i == 1:
                    item.setToolTip(str(word[i + 1]))
                self.table.setItem(0, i, item)
        self.update_ui()
        return True

    def on_select_all(self, checked):
        checked = Qt.Checked if checked else Qt.Unchecked
        for i in range(self.table.rowCount()):
            self.table.item(i, 0).setCheckState(checked)

    def on_add_group(self):
        name, succeed = QInputDialog.getText(self, "新增分类", "分类名称")
        if name is None or not succeed:
            return
        work_book.create_group(name)
        self.init_groups()

    def on_delete_group(self):
        if self.combo_groups.currentIndex() < 0:
            return
        work_book.delete_group(self.combo_groups.currentData())
        self.init_groups()

    def on_add_word(self, word, translate):
        word_id = work_book.add_word(word, translate)
        work_book.add_word_to_group(word_id, 1)
        self.init_groups()

    def on_delete_word(self):
        # 注意：只能从后往前删除
        for i in range(self.table.rowCount() - 1, -1, -1):
            item = self.table.item(i, 0)
            if item.checkState() == Qt.Checked:
                work_book.delete_word(item.data(Qt.UserRole))
                self.table.removeRow(i)

    def on_double_clicked(self, item: QTableWidgetItem):
        item = self.table.item(item.row(), 0)
        item.setCheckState(Qt.Checked if item.checkState() != Qt.Checked else Qt.Unchecked)
