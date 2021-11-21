import os
import platform
import subprocess
import sys
import threading

import pystardict
from PyQt5.QtCore import QSize, pyqtSignal, Qt
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import QWidget, QCheckBox, QPushButton, QLineEdit, QFileDialog, \
    QListWidget, QListWidgetItem, QMessageBox, QDialog, QTextEdit, QLabel

from src.UI.download_dict import DownloadDialog
from src.UI.util import create_grid, create_line, create_multi_line
from src.backend.stardict import StartDict
from src.setting import setting
from src.util import run_app, resource_path


class GetHotkey(QDialog):
    hotkey = []

    def __init__(self, parent, hotkey):
        super().__init__(parent)
        self.label = QLabel(hotkey)
        self.btn = QPushButton("OK")
        self.btn.setFixedWidth(80)
        self.btn.clicked.connect(self.accept)
        layout = create_multi_line([
            create_line([1, self.label, 1]),
            create_line([1, self.btn, 1])
        ])
        self.setWindowTitle("更改热键")
        self.setLayout(layout)

    def keyPressEvent(self, event: QKeyEvent):
        m = event.modifiers()
        hotkey = []
        if m & Qt.ShiftModifier:
            hotkey.append("shift")
        if m & Qt.ControlModifier:
            hotkey.append("control")
        if m & Qt.AltModifier:
            hotkey.append("alt")
        k = event.key()
        if 48 <= k <= 57 or 65 <= k <= 90 or 97 <= k <= 122:
            hotkey.append(chr(k).lower())

        if k == Qt.Key_Escape:
            hotkey = []

        self.label.setText(' - '.join(hotkey).upper() if len(hotkey) > 0 else '禁用')
        self.hotkey = hotkey


class InstallOcrWindow(QDialog):
    signal_log = pyqtSignal(str)
    signal_finish = pyqtSignal(int)

    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("安装OCR服务")
        self.setFixedSize(QSize(640, 480))
        self.edit = QTextEdit()
        self.edit.setAcceptRichText(False)
        self.edit.setReadOnly(True)
        self.setLayout(create_line([self.edit]))

        self.signal_log.connect(self.on_log)
        self.signal_finish.connect(self.on_finish)
        self.t = threading.Thread(target=self.do_install)
        self.t.start()

    def on_log(self, txt):
        self.edit.append(txt)

    def on_finish(self, ret):
        if ret != 0:
            QMessageBox.warning(self, "错误", "安装失败")
            return
        QMessageBox.information(self, "提示", "安装成功")
        self.accept()

    def do_install(self):
        cmd = "bash {} install".format(resource_path("./res/ocr.sh"))
        ret = run_app(cmd, lambda x: self.signal_log.emit(x))
        self.signal_finish.emit(ret)


class SettingWindow(QWidget):
    auto_startup_filename = "{}/.config/autostart/my_dict.desktop".format(os.environ["HOME"])
    cfg_desktop = "[Desktop Entry]\n" \
                  "Categories=Education;Translation\n" \
                  "Type=Application\n"\
                  "Icon=dictionary\n"\
                  "StartupNotify=false\n"\
                  "Terminal=false\n"\
                  "Name=MyDict\n"\
                  "GenericName=MyDict\n"\
                  "GenericName[zh_CN]=我的词典\n"\
                  "Name[zh_CN]=我的词典\n"\
                  "Exec={}\n".format(sys.argv[0])

    def __init__(self, parent, star_dict: StartDict):
        super().__init__(parent)
        self.star_dict = star_dict
        self.star_dict.signal_load_dict_finish.connect(self.init_dict)

        self.checkbox_use_dark_skin = QCheckBox("使用灰色主题")
        self.checkbox_use_dark_skin.setChecked(setting.use_dark_skin)
        self.checkbox_use_dark_skin.clicked.connect(self.on_save)

        self.checkbox_support_clipboard = QCheckBox("剪贴板取词（复制3次触发取词）")
        self.checkbox_support_clipboard.setToolTip("复制3次触发取词")
        self.checkbox_support_clipboard.clicked.connect(self.on_save)

        self.checkbox_support_ocr = QCheckBox("OCR取词")
        self.checkbox_support_ocr.clicked.connect(self.on_save)

        self.edit_ocr_hotkey = QPushButton(
            " - ".join(setting.ocr_hotkey).upper() if len(setting.ocr_hotkey) > 0 else '禁用'
        )
        self.edit_ocr_hotkey.clicked.connect(self.on_change_hotkey)
        self.edit_ocr_hotkey.setFlat(True)

        self.edit_ocr_server = QLineEdit()
        self.edit_ocr_server.setReadOnly(True)
        self.edit_ocr_server.setPlaceholderText("取词服务器")
        self.edit_ocr_server.setText(setting.ocr_server)
        self.edit_ocr_server.textChanged.connect(self.on_save)

        self.button_ocr_server = QPushButton("安装")
        self.button_ocr_server.setMinimumWidth(80)
        self.button_ocr_server.clicked.connect(self.on_install_ocr_server)

        self.checkbox_show_main_window_when_startup = QCheckBox("启动时显示主窗口")
        self.checkbox_show_main_window_when_startup.clicked.connect(self.on_save)

        self.checkbox_auto_startup = QCheckBox("开机时启动")
        self.checkbox_auto_startup.clicked.connect(self.on_auto_startup)

        self.btn_create_desktop = QPushButton("创建快捷方式")
        self.btn_create_desktop.setMinimumWidth(180)
        self.btn_create_desktop.clicked.connect(self.on_create_desktop)

        self.btn_download_dict = QPushButton("下载离线词典")
        self.btn_download_dict.setMinimumWidth(180)
        self.btn_download_dict.clicked.connect(self.on_download_dict)

        self.edit_dict_folder = QLineEdit(setting.star_dict_folder)
        self.btn_select_dict_folder = QPushButton("...")
        self.btn_select_dict_folder.setMinimumWidth(80)
        self.btn_select_dict_folder.clicked.connect(self.on_select_dict_folder)
        self.btn_open_dict_folder = QPushButton("浏览")
        self.btn_open_dict_folder.setMinimumWidth(80)
        self.btn_open_dict_folder.clicked.connect(self.on_open_dict_folder)

        self.checkbox_support_clipboard.setChecked(setting.support_clipboard)
        self.checkbox_support_ocr.setChecked(setting.support_ocr)
        self.checkbox_show_main_window_when_startup.setChecked(setting.show_main_window_when_startup)
        self.checkbox_auto_startup.setChecked(self.is_auto_startup())

        self.list_query_dicts = QListWidget()
        self.list_clipboard_dicts = QListWidget()
        self.init_dict()
        line_dicts = create_line([
            create_multi_line(["查询词典:", self.list_query_dicts]),
            create_multi_line(["取词词典:", self.list_clipboard_dicts])
        ])
        items = [
            [self.checkbox_use_dark_skin],
            [self.checkbox_support_clipboard],
            [self.checkbox_support_ocr],
            ["    取词热键:", create_line([self.edit_ocr_hotkey])],
            ["    取词服务器:", create_line([self.edit_ocr_server, self.button_ocr_server])],
            [self.checkbox_show_main_window_when_startup],
            [self.checkbox_auto_startup],
            ["词典目录:", create_line([self.edit_dict_folder, self.btn_select_dict_folder, self.btn_open_dict_folder])],
            [line_dicts],
            [create_line([self.btn_create_desktop, self.btn_download_dict])],
        ]

        self.setLayout(create_multi_line([create_grid(items), 1]))

    def init_dict(self):
        self.list_query_dicts.clear()
        self.list_clipboard_dicts.clear()

        for k in setting.online.keys():
            item = QListWidgetItem()
            item.setData(Qt.UserRole, k)
            self.list_query_dicts.addItem(item)
            checkbox1 = QCheckBox(setting.online[k]["name"])
            checkbox1.clicked.connect(self.on_clicked_list_query_dicts)
            if k in setting.dicts_for_query or\
                    (len(setting.dicts_for_query) == 1 and setting.dicts_for_query[0] == "*"):
                checkbox1.setChecked(True)
            self.list_query_dicts.setItemWidget(item, checkbox1)

            item2 = QListWidgetItem()
            item2.setData(Qt.UserRole, k)
            self.list_clipboard_dicts.addItem(item2)
            checkbox2 = QCheckBox(setting.online[k]["name"])
            checkbox2.clicked.connect(self.on_clicked_list_clipboard_dicts)
            if k in setting.dicts_for_clipboard or\
                    (len(setting.dicts_for_clipboard) == 1 and setting.dicts_for_clipboard[0] == "*"):
                checkbox2.setChecked(True)
            self.list_clipboard_dicts.setItemWidget(item2, checkbox2)

        for i in self.star_dict.list():
            i: pystardict.Dictionary
            item = QListWidgetItem()
            item.setData(Qt.UserRole, i.ifo.bookname)
            self.list_query_dicts.addItem(item)
            checkbox1 = QCheckBox(i.ifo.bookname)
            checkbox1.clicked.connect(self.on_clicked_list_query_dicts)
            if i.ifo.bookname in setting.dicts_for_query or\
                    (len(setting.dicts_for_query) == 1 and setting.dicts_for_query[0] == "*"):
                checkbox1.setChecked(True)
            self.list_query_dicts.setItemWidget(item, checkbox1)

            item2 = QListWidgetItem()
            item2.setData(Qt.UserRole, i.ifo.bookname)
            self.list_clipboard_dicts.addItem(item2)
            checkbox2 = QCheckBox(i.ifo.bookname)
            checkbox2.clicked.connect(self.on_clicked_list_clipboard_dicts)
            if i.ifo.bookname in setting.dicts_for_clipboard or\
                    (len(setting.dicts_for_clipboard) == 1 and setting.dicts_for_clipboard[0] == "*"):
                checkbox2.setChecked(True)
            self.list_clipboard_dicts.setItemWidget(item2, checkbox2)

    def on_clicked_list_query_dicts(self):
        count = self.list_query_dicts.count()
        chooses = []
        for i in range(count):
            item = self.list_query_dicts.item(i)
            cb = self.list_query_dicts.itemWidget(item)
            if cb.isChecked():
                chooses.append(item.data(Qt.UserRole))
        if len(chooses) == count:
            setting.dicts_for_query = ["*"]
        else:
            setting.dicts_for_query = chooses
        setting.save()

    def on_clicked_list_clipboard_dicts(self):
        count = self.list_clipboard_dicts.count()
        chooses = []
        for i in range(count):
            item = self.list_clipboard_dicts.item(i)
            cb = self.list_clipboard_dicts.itemWidget(item)
            if cb.isChecked():
                chooses.append(item.data(Qt.UserRole))
        if len(chooses) == count:
            setting.dicts_for_clipboard = ["*"]
        else:
            setting.dicts_for_clipboard = chooses
        setting.save()

    def on_save(self):
        setting.use_dark_skin = self.checkbox_use_dark_skin.isChecked()
        setting.support_clipboard = self.checkbox_support_clipboard.isChecked()
        setting.support_ocr = self.checkbox_support_ocr.isChecked()
        setting.show_main_window_when_startup = self.checkbox_show_main_window_when_startup.isChecked()
        setting.star_dict_folder = self.edit_dict_folder.text()
        setting.save()

    def is_auto_startup(self):
        return os.path.exists(self.auto_startup_filename)

    def on_auto_startup(self):
        if self.checkbox_auto_startup.isChecked():
            with open(self.auto_startup_filename, "w+") as f:
                f.write(self.cfg_desktop)
        else:
            if os.path.exists(self.auto_startup_filename):
                os.remove(self.auto_startup_filename)

    def on_create_desktop(self):
        with open("{}/.local/share/applications/my_dict.desktop".format(os.environ["HOME"]), "w+") as f:
            f.write(self.cfg_desktop)

    def on_select_dict_folder(self):
        dict_folder = QFileDialog.getExistingDirectory(self, "选择字典目录", self.edit_dict_folder.text())
        if dict_folder is None:
            return
        self.edit_dict_folder.setText(setting.star_dict_folder)

    def on_open_dict_folder(self):
        file_path = self.edit_dict_folder.text()
        if not os.path.exists(file_path):
            return

        system_name = platform.system()
        if system_name == 'Windows':
            os.startfile(file_path)
        elif system_name == 'Darwin':
            subprocess.call(["open", file_path])
        else:
            subprocess.call(["xdg-open", file_path])

    def on_download_dict(self):
        dd = DownloadDialog(self, self.star_dict)
        dd.exec_()
        self.init_dict()

    def on_install_ocr_server(self):
        dd = InstallOcrWindow(self)
        dd.exec_()

    def on_change_hotkey(self):
        dd = GetHotkey(self, self.edit_ocr_hotkey.text())
        ret = dd.exec_()
        if ret == 1:
            self.edit_ocr_hotkey.setText(' - '.join(dd.hotkey).upper() if len(dd.hotkey) > 0 else '禁用')
            setting.ocr_hotkey = dd.hotkey
            setting.save()
