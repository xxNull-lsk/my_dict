import json

from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtWidgets import QWidget, QLabel, QTextEdit, QPushButton, QHBoxLayout, QVBoxLayout, QMessageBox

from src.events import events
from src.util import load_icon
from src.backend.youdao import YouDaoFanYi


class ResultWindow(QWidget):
    src = ""
    css = '<style type="text/css">\n' \
          'div.title {\n' \
          ' color: rgb(120, 120, 120);\n' \
          ' font-size: 12px;\n' \
          '}\n' \
          '</style>'

    def __init__(self, parent, translucent=False):
        super().__init__(parent)
        events.signal_translate_finish.connect(self.on_translate_finish)

        self.edit_res = QTextEdit()
        self.edit_res.setReadOnly(True)

        self.label_ussm = QLabel("")
        self.label_ussm.hide()
        self.label_uksm = QLabel("")
        self.label_uksm.hide()

        self.media_player_us = QMediaPlayer()
        self.btn_us = QPushButton("  美音  ")
        self.btn_us.setParent(self)
        self.btn_us.setIcon(load_icon("voice"))
        self.btn_us.hide()
        self.btn_us.setFlat(True)
        self.btn_us.clicked.connect(lambda: self.on_play(self.media_player_us))
        self.media_player_uk = QMediaPlayer()
        self.btn_uk = QPushButton("  英音  ")
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
        if translucent:
            self.label_uksm.setAttribute(Qt.WA_TranslucentBackground)
            self.label_ussm.setAttribute(Qt.WA_TranslucentBackground)
            self.btn_uk.setAttribute(Qt.WA_TranslucentBackground)
            self.edit_res.setAttribute(Qt.WA_TranslucentBackground)
            for i in range(0, hbox.count()):
                w = hbox.itemAt(i)
                if isinstance(w, QWidget):
                    print(i, "Qt.WA_TranslucentBackground")
                    w.setAttribute(Qt.WA_TranslucentBackground)
        self.setLayout(vbox)

    @staticmethod
    def on_play(media_player: QMediaPlayer):
        try:
            media_player.stop()
            media_player.play()
        except Exception as ex:
            print("Exception", ex)

    def reset(self, src):
        self.src = src
        self.btn_uk.hide()
        self.label_uksm.hide()
        self.btn_us.hide()
        self.label_ussm.hide()
        self.edit_res.clear()

    def on_translate_finish(self, src, result):
        if self.src != src:
            return
        if result["is_word"]:
            self._add_online_word_result(result)
        else:
            self._add_online_text_result(result)

    def _add_online_text_result(self, result):
        if "error_code" in result and result["error_code"] != 0:
            print("错误", json.dumps(result, indent=4))
            events.signal_pop_message.emit("查询失败")
            return False
        res = ''
        for target in result["target"]:
            if res != '':
                res += "<br>"
            res += "&nbsp;&nbsp;&nbsp;&nbsp;{}".format(
                self.plan2html(target)
            )
        res = self.css + "<div class=\"title\">{}</div><p>".format(result["server"]) + res + "</p>"
        html = self.edit_res.toHtml()
        self.edit_res.setHtml("{}{}".format(res, html))
        return True

    def _add_online_word_result(self, result):
        if result['error_code'] != 0:
            return False
        res = ''
        for item in result["target"]:
            if res != '':
                res += "<br>"
            res += "&nbsp;&nbsp;&nbsp;&nbsp;{}".format(
                self.plan2html(item)
            )
        res = self.css + "<div class=\"title\">{}</div><p>".format(result["server"]) + res + "</p>"

        if 'uk' in result:
            uk = result['uk']
            if uk['speach'] != '':
                self.media_player_uk.setMedia(
                    QMediaContent(QUrl(YouDaoFanYi.voice_addr(uk['speach'])))
                )
                self.media_player_uk.play()
                self.btn_uk.show()
            if uk['sm'] != '':
                self.label_uksm.setText("[{}]".format(uk['sm']))
                self.label_uksm.show()

        if 'us' in result:
            us = result['us']
            if us['speach'] != '':
                self.media_player_us.setMedia(
                    QMediaContent(QUrl(YouDaoFanYi.voice_addr(us['speach'])))
                )
                self.media_player_us.play()
                self.btn_us.show()
            if us['sm'] != '':
                self.label_ussm.setText("[{}]".format(us['sm']))
                self.label_ussm.show()
                
        html = self.edit_res.toHtml()
        self.edit_res.setHtml("{}{}".format(res, html))
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
