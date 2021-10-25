from PyQt5 import QtCore
from PyQt5.QtWidgets import QGridLayout, QFormLayout, QLabel, QHBoxLayout, QLayout, QVBoxLayout, QWidget


def create_line(items, space=5):
    hbox = QHBoxLayout()
    hbox.setSpacing(space)
    for item in items:
        if isinstance(item, int):
            hbox.addStretch(item)
        elif isinstance(item, str):
            hbox.addWidget(QLabel(item))
        elif isinstance(item, QLayout):
            hbox.addItem(item)
        else:
            hbox.addWidget(item)
    return hbox


def create_widget_with_layout(layout):
    widget = QWidget()
    widget.setLayout(layout)
    return widget


def create_multi_line(items, space=8):
    vbox = QVBoxLayout()
    vbox.setSpacing(space)
    for item in items:
        if isinstance(item, int):
            vbox.addStretch(item)
        elif isinstance(item, str):
            vbox.addWidget(QLabel(item))
        elif isinstance(item, QLayout):
            vbox.addItem(item)
        else:
            vbox.addWidget(item)
    return vbox


def create_grid(items, space=5):
    col_count = 0
    for line in items:
        col_count = max(col_count, len(line))

    gl = QGridLayout()
    gl.setSpacing(space)
    for row, line_items in enumerate(items):
        n = len(line_items)
        for col, item in enumerate(line_items):
            if isinstance(item, str):
                item = QLabel(item)
            if isinstance(item, QLayout):
                gl.addItem(item, row, col, rowSpan=1, columnSpan=int(col_count/n))
            else:
                gl.addWidget(item, row, col, 1, int(col_count/n), QtCore.Qt.AlignLeft)

    return gl


def create_form(items, space=5):
    col_count = 0
    for line in items:
        col_count = max(col_count, len(line))

    qfl = QFormLayout()
    qfl.setSpacing(space)
    for line in items:
        if len(line) == 0:
            qfl.addWidget(QLabel(""))
        elif len(line) == 1:
            qfl.addWidget(line[0])
        elif isinstance(line[0], str):
            hbox = QHBoxLayout()
            hbox.setSpacing(5)
            for i in line[1:]:
                hbox.addWidget(i)
            qfl.addRow(line[0], hbox)
        else:
            hbox = QHBoxLayout()
            hbox.setSpacing(5)
            for i in line:
                hbox.addWidget(i)
            qfl.addItem(hbox)
    return qfl

