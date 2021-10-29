from PyQt5.QtCore import QRect, QTimer, Qt, QSize, pyqtSignal
from PyQt5.QtGui import QCursor, QFont, QColor
from PyQt5.QtMultimedia import QMediaPlayer
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QApplication, QWidget, QPushButton
from system_hotkey import SystemHotkey

from src.UI.BaseWidget import BaseWidget
from src.UI.OCR import OCR
from src.UI.result import ResultWindow
from src.UI.util import create_line
from src.backend.stardict import StartDict
from src.backend.youdao import YouDaoFanYi
from src.events import events
from src.setting import setting
from src.util import load_icon


class TipWindow(BaseWidget):
    last_text = []
    signal_hotkey = pyqtSignal()
    clipboard = None
    ocr = None
    is_in_hotkey = False

    def __init__(self, youdao: YouDaoFanYi, star_dict: StartDict, app):
        super().__init__()

        self.app = app
        self.signal_hotkey.connect(self.on_hotkey)
        events.signal_setting_changed.connect(self.on_setting_changed)

        self.star_dict = star_dict
        self.setMinimumSize(QSize(360, 280))

        self.youdao = youdao
        # 窗口置顶，无边框，在任务栏不显示图标
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.BypassWindowManagerHint | Qt.FramelessWindowHint | Qt.Tool)
        font = QFont()
        font.setFamily("Mono")
        font.setPointSize(16)
        font.setWeight(75)
        font.setBold(True)
        self.label_src = QLabel()
        self.label_src.setFont(font)
        self.label_src.setAttribute(Qt.WA_TranslucentBackground)
        self.btn_close = QPushButton(load_icon("close"), '')
        self.btn_close.clicked.connect(self.hide)
        self.color_background = QColor(128, 128, 128, 0.8 * 255)
        self.result = ResultWindow(self, True)
        self.result.setAttribute(Qt.WA_TranslucentBackground)
        vbox = QVBoxLayout()
        vbox.addItem(create_line([self.label_src, 1, self.btn_close]))
        vbox.addWidget(self.result)
        self.setLayout(vbox)
        self.timer_hide = QTimer()
        self.timer_hide.timeout.connect(self.on_auto_hide)

        self.curr_hotkey = []
        self.hotkey = SystemHotkey()
        self.on_setting_changed()

    def on_setting_changed(self):
        if setting.support_clipboard:
            if self.clipboard is None:
                self.clipboard = QApplication.clipboard()
                self.clipboard.dataChanged.connect(lambda: self.on_clipboard(self.clipboard.text()))
        else:
            if self.clipboard is None:
                del self.clipboard

        if self.ocr:
            self.hotkey.unregister(self.curr_hotkey)
            del self.ocr

        if setting.support_ocr and len(setting.ocr_hotkey) > 0:
            self.ocr = OCR(self.app)
            self.hotkey.register(setting.ocr_hotkey, callback=lambda x: self.signal_hotkey.emit())
            self.curr_hotkey = setting.ocr_hotkey

    def on_hotkey(self):
        if self.is_in_hotkey:
            return
        self.is_in_hotkey = True
        txt = self.ocr.get_text()
        self.is_in_hotkey = False
        if txt == '':
            events.signal_pop_message.emit("OCR取词失败。")
            return
        if not self.query(txt):
            print("query failed!")
            return

    def on_clipboard(self, txt):
        if not self.last_three_is_same(txt):
            return False
        return self.query(txt)

    @staticmethod
    def on_play(media_player: QMediaPlayer):
        try:
            media_player.stop()
            media_player.play()
        except Exception as ex:
            print("Exception", ex)

    def last_three_is_same(self, txt):
        count = len(self.last_text)
        if count == 0:
            self.last_text.append(txt)
            return False

        if txt in self.last_text:
            self.last_text.append(txt)

            # 之前连续复制了三次，就认为命中
            # 注意：count：是不包含当前这一次
            if count >= 2:
                self.last_text = []
                return True
            return False

        # 如果不存在就删除历史记录，重新记录
        self.last_text = [txt]
        return False

    def query(self, txt):
        if txt is None or txt == '':
            return False
        is_word, result = self.youdao.translate(txt)
        # print("youdao: ", is_word, result)
        if is_word:
            succeed = self.result.show_word_result(result)
            self.label_src.setText(txt)
            self.label_src.show()
        else:
            succeed = self.result.show_text_result(result)
            self.label_src.hide()
        res = self.star_dict.translate_word(txt)
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
            self.show()
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

    def show(self):
        if setting.use_dark_skin:
            self.color_background = QColor(50, 50, 50, 0.8*255)
        else:
            self.color_background = QColor(200, 200, 200, 0.8*255)
        self.move(QCursor.pos())
        self.timer_hide.start(3000)
        super().show()
