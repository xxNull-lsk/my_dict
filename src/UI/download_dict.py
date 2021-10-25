import os
import threading

import requests
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QDialog, QVBoxLayout, \
    QTableWidget, QHeaderView, QAbstractItemView, QTableView, QTableWidgetItem, QPushButton, QProgressBar
from pystardict import Dictionary

from src import setting
from src.UI.util import create_line, create_widget_with_layout
from src.backend.stardict import StartDict


class MyPushButton(QPushButton):
    d: Dictionary = None


class DownloadDialog(QDialog):
    signal_reload_dict = pyqtSignal()
    signal_change_progress = pyqtSignal(int, int)
    dicts = {
        "朗道英汉字典5.0": {
            "url": "http://download.huzheng.org/zh_CN/stardict-langdao-ec-gb-2.4.2.tar.bz2",
            "count": 435468,
            "size": "9.1M"
        },
        "朗道汉英字典5.0": {
            "url": "http://download.huzheng.org/zh_CN/stardict-langdao-ce-gb-2.4.2.tar.bz2",
            "count": 405719,
            "size": "7.8M"
        },
        "懒虫简明英汉词典": {
            "url": "http://download.huzheng.org/zh_CN/stardict-lazyworm-ec-2.4.2.tar.bz2",
            "count": 452185,
            "size": "10M"
        },
        "懒虫简明汉英词典": {
            "url": "http://download.huzheng.org/zh_CN/stardict-lazyworm-ce-2.4.2.tar.bz2",
            "count": 119592,
            "size": "1.7M"
        },
        "新世纪英汉科技大词典": {
            "url": "http://download.huzheng.org/zh_CN/stardict-ncce-ec-2.4.2.tar.bz2",
            "count": 626953,
            "size": "10.4M"
        },
        "新世纪汉英科技大词典": {
            "url": "http://download.huzheng.org/zh_CN/stardict-ncce-ce-2.4.2.tar.bz2",
            "count": 621241,
            "size": "10.6M"
        },
        "计算机词汇": {
            "url": "http://download.huzheng.org/zh_CN/stardict-kdic-computer-gb-2.4.2.tar.bz2",
            "count": 6131,
            "size": "683K"
        },
        "新华字典": {
            "url": "http://download.huzheng.org/zh_CN/stardict-xhzd-2.4.2.tar.bz2",
            "count": 74025,
            "size": "8.9M"
        },
        "汉语成语词典": {
            "url": "http://download.huzheng.org/zh_CN/stardict-hanyuchengyucidian_fix-2.4.2.tar.bz2",
            "count": 13305,
            "size": "2.8M"
        },
    }
    t = None

    def __init__(self, parent, star_dict: StartDict):
        super().__init__(parent)
        self.setWindowTitle("下载离线词典")
        self.star_dict = star_dict
        self.star_dict.signal_load_dict_finish.connect(self.init_dict)
        self.signal_reload_dict.connect(self.init_dict)
        self.signal_change_progress.connect(self.on_progress)

        self.setMinimumHeight(520)
        self.setMinimumWidth(760)
        self.list_dicts = QTableWidget()
        self.list_dicts.setRowCount(len(self.dicts.keys()))
        self.list_dicts.setColumnCount(4)
        self.list_dicts.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.list_dicts.setEditTriggers(QTableView.NoEditTriggers)
        self.list_dicts.setSelectionMode(QAbstractItemView.SingleSelection)
        self.list_dicts.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.can_download = True
        self.btn_cancel_download = QPushButton("取消")
        self.btn_cancel_download.clicked.connect(self.on_cancel_download)
        self.btn_cancel_download.hide()

        self.progress = QProgressBar()
        self.progress.hide()
        vbox = QVBoxLayout()
        vbox.addWidget(self.list_dicts)
        vbox.addItem(create_line([self.progress, self.btn_cancel_download]))
        self.setLayout(vbox)

        self.init_dict()

    def init_dict(self):
        self.list_dicts.clear()
        self.list_dicts.setHorizontalHeaderLabels(['名称', '词汇数量', '大小', '管理'])
        for i, k in enumerate(self.dicts.keys()):
            self.list_dicts.setRowHeight(i, 64)
            info = self.dicts[k]
            self.list_dicts.setItem(i, 0, QTableWidgetItem(k))
            self.list_dicts.setItem(i, 1, QTableWidgetItem(str(info["count"])))
            self.list_dicts.setItem(i, 2, QTableWidgetItem(info["size"]))
            if not self.star_dict.exist(k):
                btn_add = MyPushButton("下载")
                btn_add.d = self.dicts[k]
                btn_add.clicked.connect(self.on_download)
                self.list_dicts.setCellWidget(i, 3, create_widget_with_layout(create_line([btn_add])))

        for d in self.star_dict.dists:
            d: Dictionary
            if d.ifo.bookname in self.dicts.keys():
                continue
            i = self.list_dicts.rowCount()
            self.list_dicts.setRowHeight(i, 64)
            self.list_dicts.setItem(i, 0, QTableWidgetItem(d.ifo.bookname))
            self.list_dicts.setItem(i, 1, QTableWidgetItem(str(d.ifo.wordcount)))
            self.list_dicts.setItem(i, 2, QTableWidgetItem(str(d.ifo.idxfilesize)))
        if self.progress:
            self.progress.hide()
        if self.btn_cancel_download:
            self.btn_cancel_download.hide()

    def on_download(self):
        sender = self.sender()
        sender: MyPushButton
        self.can_download = True
        self.progress.setValue(0)
        self.progress.show()
        self.btn_cancel_download.show()
        self.btn_cancel_download.setEnabled(not self.can_download)
        # download dict may be use very long time, so do it in a thread
        self.t = threading.Thread(target=self.do_download, args=(sender.d["url"], ))
        self.t.start()

    def on_progress(self, curr, total):
        self.progress.setMaximum(total)
        self.progress.setValue(curr)

    def do_download(self, url):
        path = "{}/tmp".format(setting.setting_folder)
        if not os.path.exists(path):
            os.makedirs(path)
        filename = os.path.split(url)[-1]
        f = open(os.path.join(path, filename), "w+b")
        with requests.get(url, stream=True) as r:
            filesize = r.headers["Content-Length"]
            chunk_size = 128
            total = int(filesize) // chunk_size
            self.signal_change_progress.emit(0, total)
            curr = 1
            for chunk in r.iter_content(chunk_size):
                if not self.can_download:
                    break
                f.write(chunk)
                if curr <= total:
                    self.signal_change_progress.emit(curr, total)
                    curr += 1
        f.close()
        if self.can_download:
            os.system("tar -xf {} -C {}".format(os.path.join(path, filename), setting.setting.star_dict_folder))
            self.star_dict.load()
        self.signal_reload_dict.emit()
        os.remove(os.path.join(path, filename))

    def on_cancel_download(self):
        self.can_download = False
