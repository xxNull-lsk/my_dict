from src.backend.google import Google
from src.backend.youdao import YouDaoFanYi
from src.events import events
from src.setting import setting
import threading


class OnLine(object):
    def __init__(self):
        super().__init__()
        self.servers = {
            "google": Google(),
            "youdao": YouDaoFanYi(),
        }

    def translate(self, txt: str, dicts=None, pos=None):
        if dicts is None:
            dicts = setting.dicts_for_query
        count = len(dicts)
        for server in self.servers.keys():
            if server in dicts \
                    or (count == 1 and dicts[0] == "*"):
                t = threading.Thread(target=self.do_translate, args=(server, txt, pos))
                t.start()

    def do_translate(self, server, txt, pos):
        result = self.servers[server].translate(txt)
        if result is None:
            return
        # print(server, result)
        result["server"] = setting.online[server]["name"]
        events.signal_translate_finish.emit(txt, result, pos)
