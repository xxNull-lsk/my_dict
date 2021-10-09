import os

from pystardict import Dictionary


class StartDict(object):
    dists = []

    def __init__(self, folder, in_memory=False):
        if not os.path.exists(folder):
            return
        for f in os.listdir(folder):
            self.load(os.path.join(folder, f), in_memory)

    def list(self):
        return [d.ifo for d in self.dists]

    def load(self, folder, in_memory):
        if not os.path.isdir(folder):
            return
        for f in os.listdir(folder):
            if os.path.isdir(os.path.join(folder, f)):
                self.load(os.path.join(folder, f), in_memory)
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
            print("load", d.ifo.bookname, "succeed")
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
