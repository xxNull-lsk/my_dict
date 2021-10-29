from PyQt5.QtCore import QObject, pyqtSignal


class Events(QObject):
    signal_pop_message = pyqtSignal(str)
    signal_setting_changed = pyqtSignal()

    # 在线翻译结束：源字符串，翻译结果
    signal_translate_finish = pyqtSignal(str, dict)


events = Events()
