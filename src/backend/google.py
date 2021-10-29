from googletrans import Translator


class Google(object):
    def __init__(self):
        super().__init__()
        self.translator = Translator(service_urls=[
            'translate.google.cn',
        ])

    def translate(self, txt: str):
        try:
            self.translator.detect(txt)
            response = self.translator.translate(txt, dest="zh-cn")
            if response.src == "zh-CN":
                response = self.translator.translate(txt, dest="en")
        except Exception as ex:
            print("Google translate: ", ex)
            return None
        # print(response.src, response.parts, response.extra_data)
        result = {
            "is_word": True,
            "error_code": 0,
            "target": [response.text],
            "target_language": response.src,
            "source_language": response.dest,
            "uk": {
                "speach": "",
                "sm": ""
            },
            "us": {
                "speach": "",
                "sm": ""
            }
        }
        return result