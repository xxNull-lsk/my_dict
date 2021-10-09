import requests


class YouDaoFanYi(object):
    is_word = None
    last_word = None
    last_result = None

    @staticmethod
    def voice_addr(param):
        return "http://dict.youdao.com/dictvoice?type=2&audio=" + param

    def translate(self, txt: str):
        if self.last_word == txt:
            return self.is_word, self.last_result
        for i in txt:
            if not i.isalpha():
                return False, self.translate_text(txt)
        return True, self.translate_word(txt)

    def translate_word(self, word):
        url = 'http://dict.youdao.com/jsonresult'
        params = {
            'q': word,
            'type': '1',
            "client": "deskdict",
            "keyfrom": "deskdict_deepin",
            "pos": "-1",
            "len": "eng"
        }
        result = requests.get(url=url, params=params).json()
        self.is_word = True
        self.last_word = word
        self.last_result = result
        return result

    def translate_text(self, text):
        url = 'http://fanyi.youdao.com/translate'
        params = {
            'dogVersion': '1.0',
            'ue': 'utf8',
            'doctype': 'json',
            'xmlVersion': '1.6',
            'client': 'deskdict_deepin',
            'id': '92dc50aa4970fb72d',
            'vendor': 'YoudaoDict',
            'appVer': '1.0.3',
            'appZengqiang': '0',
            'abTest': '5',
            'smartresult': "rule",
            'keyfrom': "deskdict",
            'smartresult': "deskdict.main",
            'i': text,
            "type": "AUTO"
        }
        result = requests.get(url=url, params=params).json()
        self.is_word = False
        self.last_word = text
        self.last_result = result
        return result
