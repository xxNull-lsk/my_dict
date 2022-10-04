from PyQt5.QtCore import Qt, QRect, QPoint, QSize
from PyQt5.QtGui import QScreen, QPainter, QPixmap, QColor, QImage, QCursor
from PyQt5.QtWidgets import QDialog, QPushButton

from src.UI.BaseWidget import BaseWidget
from src.UI.util import create_line
from src.util import load_icon


class UiOcrMask(QDialog):
    def __init__(self, win_id, screen: QScreen):
        super().__init__()
        self.select_rect = QRect()
        self.select_image = QImage()
        self.select_pt = QPoint(0, 0)
        self.is_draw = False
        self.pt1 = QPoint(0, 0)
        self.pt2 = QPoint(0, 0)
        self.setAttribute(Qt.WA_TranslucentBackground)  # 窗体背景透明
        # 窗口置顶，无边框，在任务栏不显示图标
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.BypassWindowManagerHint | Qt.FramelessWindowHint | Qt.Tool)
        screen_rect: QRect = screen.availableGeometry()
        self.screen_rect = screen_rect

        screen_rect.setWidth(screen_rect.width())
        screen_rect.setHeight(screen_rect.height())
        self.devicePixelRatio = screen.devicePixelRatio()
        self.setGeometry(screen_rect)
        shot: QPixmap = screen.grabWindow(
            win_id,
            screen_rect.x(),
            screen_rect.y(),
            width=screen_rect.width(),
            height=screen_rect.height(),
        )
        self.img: QImage = shot.toImage()
        self.tools = BaseWidget(self)
        self.tools.setHidden(True)
        self.tools.setFixedHeight(int(64 / self.devicePixelRatio))

        btn_ok = QPushButton("", self.tools)
        btn_ok.setIcon(load_icon("ok"))
        btn_ok.setIconSize(QSize(int(32 / self.devicePixelRatio), int(32 / self.devicePixelRatio)))
        btn_ok.clicked.connect(self.accept)
        btn_ok.setFlat(True)
        btn_cancel = QPushButton("", self.tools)
        btn_cancel.setIconSize(QSize(int(32 / self.devicePixelRatio), int(32 / self.devicePixelRatio)))
        btn_cancel.setIcon(load_icon("cancel"))
        btn_cancel.setFlat(True)
        btn_cancel.clicked.connect(self.reject)
        lay = create_line([btn_ok, btn_cancel])
        self.tools.setLayout(lay)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.save()
        painter.drawImage(0, 0, self.img)
        painter.fillRect(self.rect(), QColor(128, 128, 128, 125))
        painter.drawImage(self.select_pt, self.select_image)
        painter.restore()

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self.reject()
            return
        if self.is_draw or event.button() != Qt.LeftButton:
            return
        self.is_draw = True
        self.setCursor(Qt.CrossCursor)

        self.pt1 = self.pt2 = QCursor.pos() - self.screen_rect.topLeft()
        self.update()

    def mouseMoveEvent(self, event):
        if self.is_draw:
            self.pt2 = QCursor.pos() - self.screen_rect.topLeft()
            pt1 = QPoint(min(self.pt1.x(), self.pt2.x()), min(self.pt1.y(), self.pt2.y()))
            pt2 = QPoint(max(self.pt1.x(), self.pt2.x()), max(self.pt1.y(), self.pt2.y()))
            rect = QRect(pt1, pt2)
            if rect.width() > 3 and rect.height() > 3:
                self.select_rect = rect
                self.select_pt = pt1
                self.select_image = self.img.copy(
                    int(self.select_rect.x() * self.devicePixelRatio),
                    int(self.select_rect.y() * self.devicePixelRatio),
                    int(self.select_rect.width() * self.devicePixelRatio),
                    int(self.select_rect.height() * self.devicePixelRatio)
                )
                # 计算工具条位置
                # 最优先的是左下角，防止显示在屏幕外
                y = pt2.y() + 2
                if y > self.rect().height() - self.tools.height() - 2:
                    y = self.rect().height() - self.tools.height() - 2
                x = pt1.x()
                if x > self.rect().width() - self.tools.width() - 2:
                    x = self.rect().width() - self.tools.width() - 2
                self.tools.move(QPoint(x, y))
                self.tools.setVisible(True)
                self.update()

    def mouseReleaseEvent(self, event):
        self.is_draw = False
        self.setCursor(Qt.ArrowCursor)

    def mouseDoubleClickEvent(self, event):
        self.accept()
