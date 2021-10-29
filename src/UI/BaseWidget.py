from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtWidgets import QWidget


class BaseWidget(QWidget):
    """圆角边框类"""
    def __init__(self, parent=None):
        super().__init__(parent)
        # 设置 窗口无边框和背景透明 *必须
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.color_background = QColor(128, 128, 128, 0.7 * 255)

    def paintEvent(self, event):
        pat = QPainter(self)
        pat.setRenderHint(pat.Antialiasing)
        pat.setPen(self.color_background)
        pat.setBrush(self.color_background)
        rect = self.rect()
        rect.setLeft(5)
        rect.setTop(5)
        rect.setWidth(rect.width() - 5)
        rect.setHeight(rect.height() - 5)
        pat.drawRoundedRect(rect, 4, 4)
