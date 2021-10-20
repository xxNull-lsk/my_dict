import os
import sys

from PyQt5.QtGui import QIcon, QPixmap

version = {
    "curr": "0.1.2",
    "history": {
        "0.0.1": "实现基本功能:\n"
                 "  1、查词界面\n"
                 "  2、翻译界面\n"
                 "  3、剪贴板取词",
        "0.1.1": "支持本地词典",
        "0.1.2": "防止多次运行"
    }
}


def get_version():
    return version["curr"]


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception as err:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def load_icon(name):
    return QIcon(QPixmap(resource_path("./res/{}.png".format(name))))
