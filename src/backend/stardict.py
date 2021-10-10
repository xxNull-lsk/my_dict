import os
import threading

from PyQt5.QtCore import pyqtSignal, QObject
from pystardict import Dictionary


class StartDict(QObject):
    dists = []
    signal_load_dict_finish = pyqtSignal()

    def __init__(self, folder, in_memory=False):
        super().__init__()
        self.folder = folder
        self.in_memory = in_memory
        # load dict is very slowly, so do it in a thread
        t = threading.Thread(target=self.load)
        t.start()

    def load(self):
        if not os.path.exists(self.folder):
            return
        self.dists.clear()
        for f in os.listdir(self.folder):
            self._load(os.path.join(self.folder, f), self.in_memory)
        self.signal_load_dict_finish.emit()

    def exist(self, name):
        for k in self.dists:
            k: Dictionary
            if k.ifo.bookname == name:
                return True
        return False

    def get(self, name):
        for k in self.dists:
            k: Dictionary
            if k.ifo.bookname == name:
                return k
        return None

    def list(self) -> list:
        return self.dists

    def _load(self, folder, in_memory):
        if not os.path.isdir(folder):
            return
        for f in os.listdir(folder):
            if os.path.isdir(os.path.join(folder, f)):
                self._load(os.path.join(folder, f), in_memory)
                continue
            items = os.path.splitext(f)
            if items[-1] != '.ifo':
                continue
            filename_prefix = os.path.join(folder, items[0])
            try:
                d = Dictionary(filename_prefix, in_memory)
            except Exception as err:
                print(err)
                return
            print("load", d.ifo.bookname, "succeed", len(self.dists))
            self.dists.append(d)

    def translate_word(self, word):
        results = {}
        for d in self.dists:
            d: Dictionary
            try:
                results[d.ifo.bookname] = d.get(word)
            except Exception as err:
                print(err)
                continue
        return results
