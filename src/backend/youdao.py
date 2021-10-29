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
            return self.last_result
        for i in txt:
            if not i.isalpha():
                return self.translate_text(txt)
        result = self.translate_word(txt)
        if result:
            return result
        return self.translate_text(txt)

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
        response = requests.get(url=url, params=params).json()
        if "basic" not in response.keys():
            params["len"] = "chs"
            response = requests.get(url=url, params=params).json()
        if "basic" not in response.keys():
            return None
        result = {
            "is_word": True,
            "error_code": -1,
            "target": [],
            "target_language": "",
            "source_language": "",
            "uk": {
                "speach": "",
                "sm": ""
            },
            "us": {
                "speach": "",
                "sm": ""
            }
        }
        result["uk"]["speach"] = response['ukspeach'] if "ukspeach" in response else ''
        result["uk"]["sm"] = response['uksm'] if "uksm" in response else ''
        result["us"]["speach"] = response['usspeach'] if "usspeach" in response else ''
        result["us"]["sm"] = response['ussm'] if "ussm" in response else ''
        for item in response["basic"]:
            result["target"].append(item)
            result["error_code"] = 0
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
        response = requests.get(url=url, params=params).json()

        result = {
            "is_word": False,
            "error_code": -1,
            "target": [],
            "target_language": "",
            "source_language": "",
            "uk": {
                "speach": "",
                "sm": ""
            },
            "us": {
                "speach": "",
                "sm": ""
            }
        }
        for groups in response["translateResult"]:
            for i in groups:
                result["target"].append(i['tgt'])
                result["error_code"] = 0
        self.last_word = text
        self.last_result = result

        return result
