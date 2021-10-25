import json
import os

from src.events import events

setting_folder = "{}/.config/my_dict".format(os.environ["HOME"])
setting_filename = "{}/setting.json".format(setting_folder)


class Setting:
    star_dict_folder = "{}/star_dict".format(setting_folder)
    support_clipboard = True
    support_ocr = True
    ocr_hotkey = ['control', 'alt', 'd']
    ocr_server = "tcp://127.0.0.1:12126"
    show_main_window_when_startup = True
    use_dark_skin = True
    dicts_for_query = ["*"]
    dicts_for_clipboard = []

    def __init__(self):
        self.load()

    def load(self):
        if not os.path.exists(setting_folder):
            os.makedirs(setting_folder)
        if not os.path.exists(self.star_dict_folder):
            os.makedirs(self.star_dict_folder)
        txt = ""
        if os.path.exists(setting_filename):
            with open(setting_filename, 'r') as f:
                txt = f.read()
        try:
            if len(txt) <= 2:
                return
            json_setting = json.loads(txt)
            for i in json_setting.keys():
                self.__setattr__(i, json_setting[i])
        except Exception as err:
            print(err)

    def dump(self):
        obj = {}
        for i in self.__dir__():
            if i.startswith("__") or i.startswith("signal_"):
                continue
            attr = self.__getattribute__(i)
            if callable(attr):
                continue
            obj[i] = attr
        return obj

    def save(self):
        if not os.path.exists(setting_folder):
            os.makedirs(setting_folder)
        with open(setting_filename, 'w+') as f:
            obj = json.dumps(self.dump(), indent=4, ensure_ascii=False)
            f.write(obj)
        events.signal_setting_changed.emit()


setting = Setting()
