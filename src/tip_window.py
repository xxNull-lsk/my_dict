from PyQt5.QtCore import QRect, QUrl, QTimer, Qt
from PyQt5.QtGui import QCursor, QIcon, QPixmap
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtWidgets import QMessageBox, QHBoxLayout, QVBoxLayout, QPushButton, QTextEdit, QLabel, QApplication, QWidget

from src.util import resource_path
from src.youdao import YouDaoFanYi


class TipWindow(QWidget):
    last_text = ""

    def __init__(self):
        super().__init__()
        self.clipboard = QApplication.clipboard()
        self.clipboard.dataChanged.connect(self.on_data_changed)
        self.youdao = YouDaoFanYi()
        # self.setAttribute(Qt.WA_TranslucentBackground)            # 窗体背景透明
        # 窗口置顶，无边框，在任务栏不显示图标
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.BypassWindowManagerHint | Qt.FramelessWindowHint | Qt.Tool)
        self.label_src = QLabel()
        self.edit_res = QTextEdit()
        self.edit_res.setReadOnly(True)
        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        self.media_player_us = QMediaPlayer()
        self.btn_us = QPushButton("美音")
        ico_voice = QIcon(QPixmap(resource_path("./res/voice.png")))
        self.btn_us.setIcon(ico_voice)
        self.btn_us.hide()
        self.btn_us.setFlat(True)
        self.btn_us.clicked.connect(lambda: self.on_play(self.media_player_us))
        self.media_player_uk = QMediaPlayer()
        self.btn_uk = QPushButton("英音")
        self.btn_uk.setIcon(ico_voice)
        self.btn_uk.hide()
        self.btn_uk.setFlat(True)
        self.btn_uk.clicked.connect(lambda: self.on_play(self.media_player_uk))
        hbox.addWidget(self.label_src)
        hbox.addWidget(self.btn_uk)
        hbox.addWidget(self.btn_us)
        vbox.addItem(hbox)
        vbox.addWidget(self.edit_res)
        self.setLayout(vbox)
        self.timer_hide = QTimer()
        self.timer_hide.timeout.connect(self.on_auto_hide)

    @staticmethod
    def on_play(media_player: QMediaPlayer):
        try:
            media_player.stop()
            media_player.play()
        except Exception as ex:
            print("Exception", ex)

    def on_data_changed(self):
        data = self.clipboard.text()
        if self.last_text != data:
            self.last_text = data
            return
        self.last_text = ""
        is_word, result = self.youdao.translate(data)
        # print(json.dumps(result, indent=4, ensure_ascii=False))
        if is_word:
            self.show_word_result(result)
        else:
            if "errorCode" not in result or result["errorCode"] != 0:
                QMessageBox.critical(self, "错误", result)
                return
            res = ''
            for groups in result["translateResult"]:
                for i in groups:
                    if res != '':
                        res += "\n"
                    res += "{}\n    {}".format(
                        i['src'],
                        i['tgt']
                    )

            self.label_src.hide()
            self.btn_uk.hide()
            self.btn_us.hide()
            self.edit_res.clear()
            self.edit_res.setText(res)
            self.show()

    def show_word_result(self, result):
        if 'basic' not in result:
            return
        res = ''
        for item in result["basic"]:
            if res != '':
                res += "\n"
            res += "    {}".format(item)

        self.label_src.setText(result['oq'])
        self.label_src.show()
        if 'ukspeach' in result and result['ukspeach'] != '':
            self.media_player_uk.setMedia(
                QMediaContent(QUrl(self.youdao.voice_addr(result['ukspeach'])))
            )
            self.media_player_uk.play()
            self.btn_uk.show()
        else:
            self.btn_uk.hide()
        if 'usspeach' in result and result['usspeach'] != '':
            self.media_player_us.setMedia(
                QMediaContent(QUrl(self.youdao.voice_addr(result['usspeach'])))
            )
            self.btn_us.show()
        else:
            self.btn_us.hide()
        self.edit_res.clear()
        self.edit_res.setText(res)
        self.show()

    def on_auto_hide(self):
        pos = QCursor.pos()
        geometry = self.geometry()
        geometry: QRect
        if geometry.contains(pos):
            self.timer_hide.start(1000)
            return
        self.timer_hide.stop()
        self.hide()

    def show(self):
        self.move(QCursor.pos())
        self.timer_hide.start(3000)
        super().show()