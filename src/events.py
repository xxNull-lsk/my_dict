from PyQt5.QtCore import QObject, pyqtSignal


class Events(QObject):
    signal_pop_message = pyqtSignal(str)
    signal_setting_changed = pyqtSignal()


events = Events()
