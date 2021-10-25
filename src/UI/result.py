import json

from PyQt5.QtCore import QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtWidgets import QWidget, QLabel, QTextEdit, QPushButton, QHBoxLayout, QVBoxLayout, QMessageBox

from src.events import events
from src.util import load_icon
from src.backend.youdao import YouDaoFanYi


class ResultWindow(QWidget):
    last_text = ""
    css = '<style type="text/css">\n' \
          'div.title {\n' \
          ' color: rgb(120, 120, 120);\n' \
          ' font-size: 12px;\n' \
          '}\n' \
          '</style>'

    def __init__(self, parent):
        super().__init__(parent)

        self.edit_res = QTextEdit()
        self.edit_res.setReadOnly(True)

        self.label_ussm = QLabel("")
        self.label_ussm.hide()
        self.label_uksm = QLabel("")
        self.label_uksm.hide()

        self.media_player_us = QMediaPlayer()
        self.btn_us = QPushButton("美音")
        self.btn_us.setParent(self)
        self.btn_us.setIcon(load_icon("voice"))
        self.btn_us.hide()
        self.btn_us.setFlat(True)
        self.btn_us.clicked.connect(lambda: self.on_play(self.media_player_us))
        self.media_player_uk = QMediaPlayer()
        self.btn_uk = QPushButton("英音")
        self.btn_uk.setParent(self)
        self.btn_uk.setIcon(load_icon("voice"))
        self.btn_uk.hide()
        self.btn_uk.setFlat(True)
        self.btn_uk.clicked.connect(lambda: self.on_play(self.media_player_uk))

        hbox = QHBoxLayout()
        hbox.setSpacing(8)
        hbox.addWidget(self.label_uksm)
        hbox.addWidget(self.btn_uk)
        hbox.addWidget(self.label_ussm)
        hbox.addWidget(self.btn_us)
        hbox.addStretch(1)

        vbox = QVBoxLayout()
        vbox.addItem(hbox)
        vbox.addWidget(self.edit_res)
        self.setLayout(vbox)

    @staticmethod
    def on_play(media_player: QMediaPlayer):
        try:
            media_player.stop()
            media_player.play()
        except Exception as ex:
            print("Exception", ex)

    def set_result(self, is_word, result):
        if is_word:
            return self.show_word_result(result)
        else:
            return self.show_text_result(result)

    def show_text_result(self, result):
        if "errorCode" not in result or result["errorCode"] != 0:
            print("错误", json.dumps(result, indent=4))
            events.signal_pop_message.emit("查询失败")
            # QMessageBox.critical(self, "错误", json.dumps(result, indent=4), QMessageBox.Ok)
            return False
        res = ''
        for groups in result["translateResult"]:
            for i in groups:
                if res != '':
                    res += "\n"
                res += "{}\n    {}".format(
                    i['src'],
                    i['tgt']
                )

        self.btn_uk.hide()
        self.btn_us.hide()
        self.edit_res.clear()
        self.edit_res.setText(res)
        return True

    def show_word_result(self, result):
        if 'basic' not in result:
            return False
        res = ''
        for item in result["basic"]:
            if res != '':
                res += "<br>"
            res += "&nbsp;&nbsp;&nbsp;&nbsp;{}".format(self.plan2html(item))
        res = self.css + "<div class=\"title\">有道词典</div><p>" + res + "</p>"
        if 'ukspeach' in result and result['ukspeach'] != '':
            self.media_player_uk.setMedia(
                QMediaContent(QUrl(YouDaoFanYi.voice_addr(result['ukspeach'])))
            )
            self.media_player_uk.play()
            self.btn_uk.show()
        else:
            self.btn_uk.hide()
        if 'uksm' in result:
            self.label_uksm.setText("[{}]".format(result['uksm']))
            self.label_uksm.show()
        else:
            self.label_uksm.hide()

        if 'usspeach' in result and result['usspeach'] != '':
            self.media_player_us.setMedia(
                QMediaContent(QUrl(YouDaoFanYi.voice_addr(result['usspeach'])))
            )
            self.btn_us.show()
        else:
            self.btn_us.hide()
        if 'ussm' in result:
            self.label_ussm.setText("[{}]".format(result['ussm']))
            self.label_ussm.show()
        else:
            self.label_ussm.hide()
        self.edit_res.clear()
        self.edit_res.setHtml(res)
        return True

    @staticmethod
    def plan2html(v: str):
        if "<br>" not in v and '<br/>' not in v:
            v = v.replace('\n', '<br>')
            v = v.replace(' ', '&nbsp;')
            v = v.replace('\t', '&nbsp;&nbsp;&nbsp;&nbsp;')
        return v

    def add_word_result(self, k, v: str):
        html = self.edit_res.toHtml()
        if self.css not in html:
            html += self.css
        if "<br>" not in v and '<br/>' not in v:
            v = v.replace('\n', '<br>')
            v = v.replace(' ', '&nbsp;')
            v = v.replace('\t', '&nbsp;&nbsp;&nbsp;&nbsp;')
        self.edit_res.setHtml("{}"
                              "<div class=\"title\">{}</div>"
                              "<p>{}</p>".format(html, k, v))
