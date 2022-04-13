import datetime

from PyQt5.QtCore import QRect, QTimer, Qt, QSize, pyqtSignal, QPoint
from PyQt5.QtGui import QCursor, QFont, QColor, QMouseEvent
from PyQt5.QtMultimedia import QMediaPlayer
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QApplication, QPushButton
from system_hotkey import SystemHotkey

from src.UI.BaseWidget import BaseWidget
from src.backend.ocr import OCR
from src.UI.result import ResultWindow
from src.UI.util import create_line, create_multi_line
from src.backend.online import OnLine
from src.backend.stardict import StartDict
from src.events import events
from src.setting import setting
from src.util import load_icon


class TipWindow(BaseWidget):
    last_text_datetime = datetime.datetime.now()
    last_text_count = 0
    last_text = ''
    signal_hotkey = pyqtSignal()
    clipboard = None
    ocr = None
    is_in_hotkey = False
    _startPos = None
    _endPos = None
    _isTracking = False
    curr_hotkey = []

    def __init__(self, online: OnLine, star_dict: StartDict, app):
        super().__init__()
        self.src = ""
        self.app = app
        self.signal_hotkey.connect(self.on_hotkey)
        events.signal_setting_changed.connect(self.on_setting_changed)
        events.signal_translate_finish.connect(self.on_translate_finish)

        self.star_dict = star_dict
        self.setMinimumSize(QSize(360, 280))
        self.setMaximumWidth(360)

        self.online = online
        # 窗口置顶，无边框，在任务栏不显示图标
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.BypassWindowManagerHint | Qt.FramelessWindowHint | Qt.Tool)

        self.font_word = QFont()
        self.font_word.setFamily("Mono")
        self.font_word.setPointSize(16)
        self.font_word.setWeight(75)
        self.font_word.setBold(True)

        self.font_text = QFont()
        self.font_text.setFamily("Mono")
        self.font_text.setPointSize(11)
        self.font_text.setBold(False)

        self.label_src = QLabel()
        self.label_src.setWordWrap(True)
        self.label_src.setFont(self.font_text)
        self.label_src.setAttribute(Qt.WA_TranslucentBackground)

        self.btn_close = QPushButton(load_icon("close"), '')
        self.btn_close.clicked.connect(self.hide)

        self.color_background = QColor(128, 128, 128, 0.8 * 255)
        self.result = ResultWindow(self, True)
        self.result.setAttribute(Qt.WA_TranslucentBackground)

        vbox = QVBoxLayout()
        vbox.addItem(create_line([self.label_src, 1, create_multi_line([self.btn_close, 1])]))
        vbox.addWidget(self.result)
        self.setLayout(vbox)
        self.timer_hide = QTimer()
        self.timer_hide.timeout.connect(self.on_auto_hide)

        self.hotkey = SystemHotkey(check_queue_interval=0.01)
        self.on_setting_changed()

    def mouseMoveEvent(self, e: QMouseEvent):  # 重写移动事件
        self._endPos = e.pos() - self._startPos
        self.move(self.pos() + self._endPos)

    def mousePressEvent(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            self._isTracking = True
            self._startPos = QPoint(e.x(), e.y())

    def mouseReleaseEvent(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            self._isTracking = False
            self._startPos = None
            self._endPos = None

    def on_setting_changed(self):
        if setting.support_clipboard:
            if self.clipboard is None:
                self.clipboard = QApplication.clipboard()
                self.clipboard.dataChanged.connect(lambda: self.on_clipboard(self.clipboard.text()))
        else:
            if self.clipboard is not None:
                del self.clipboard

        if setting.support_ocr:
            if self.ocr is None:
                self.ocr = OCR(self.app)
            if '-'.join(setting.ocr_hotkey) != '-'.join(self.curr_hotkey):
                if len(self.curr_hotkey) > 0:
                    self.hotkey.unregister(self.curr_hotkey)
                    self.curr_hotkey = []
                if len(setting.ocr_hotkey) > 0:
                    self.hotkey.register(setting.ocr_hotkey, callback=lambda x: self.signal_hotkey.emit())
                    self.curr_hotkey = setting.ocr_hotkey
        else:
            if self.ocr:
                self.hotkey.unregister(self.curr_hotkey)
                self.curr_hotkey = []
                del self.ocr

    def on_hotkey(self):
        if self.is_in_hotkey:
            return
        self.is_in_hotkey = True
        res, txt, pos = self.ocr.get_text()
        self.is_in_hotkey = False
        if not res:
            if txt:
                events.signal_pop_message.emit("OCR取词：{}".format(txt))
            return
        self.query(txt, QPoint(pos[0], pos[1]))

    def on_clipboard(self, txt):
        if not self.check_last_text(txt):
            return False
        return self.query(txt, QCursor.pos())

    @staticmethod
    def on_play(media_player: QMediaPlayer):
        try:
            media_player.stop()
            media_player.play()
        except Exception as ex:
            print("Exception", ex)

    def check_last_text(self, txt):
        now = datetime.datetime.now()
        if self.last_text != txt:
            self.last_text = txt
            self.last_text_count = 1
            self.last_text_datetime = now
        else:
            if (now - self.last_text_datetime).total_seconds() > setting.clipboard_second:
                self.last_text_count = 1
                self.last_text_datetime = now
                return False
            self.last_text_count += 1
            self.last_text_datetime = now
        if self.last_text_count >= setting.clipboard_count:
            self.last_text = ''
            return True
        return False

    def query(self, txt, pos):
        if txt is None or txt == '':
            return False
        self.src = txt
        self.result.reset(txt)
        self.label_src.setText(txt)
        self.online.translate(txt, setting.dicts_for_clipboard, pos)
        res = self.star_dict.translate_word(txt)
        succeed = False
        for k in res.keys():
            if res[k] == '':
                continue
            count = len(setting.dicts_for_clipboard)
            if count < 1:
                continue
            if k in setting.dicts_for_clipboard\
                    or (count == 1 and setting.dicts_for_clipboard[0] == "*"):
                self.result.add_word_result(k, res[k])
                succeed = True
        if succeed:
            self.show(pos)
        return succeed

    def on_auto_hide(self):
        pos = QCursor.pos()
        geometry = self.geometry()
        geometry: QRect
        geometry.adjust(-5, -5, 5, 5)
        if geometry.contains(pos):
            self.timer_hide.start(1000)
            return
        self.timer_hide.stop()
        self.hide()

    def show(self, pos=None):
        if self.isVisible():
            return
        if setting.use_dark_skin:
            self.color_background = QColor(50, 50, 50, 0.8*255)
        else:
            self.color_background = QColor(200, 200, 200, 0.8*255)
        if pos is None:
            pos = QCursor.pos()
        self.move(pos)
        self.timer_hide.start(3000)
        super().show()

    def on_translate_finish(self, src, result, pos):
        if src == self.src:
            self.show(pos)
