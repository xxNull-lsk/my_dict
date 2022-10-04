import os
import platform
import subprocess
import sys
import threading

import pystardict
from PyQt5.QtCore import QSize, pyqtSignal, Qt, QTimer, QUrl
from PyQt5.QtGui import QKeyEvent, QDesktopServices
from PyQt5.QtWidgets import QWidget, QCheckBox, QPushButton, QLineEdit, QFileDialog, \
    QListWidget, QListWidgetItem, QMessageBox, QDialog, QTextEdit, QLabel, QInputDialog, QSlider

from src.UI.download_dict import DownloadDialog
from src.UI.util import create_grid, create_line, create_multi_line
from src.backend.stardict import StartDict
from src.setting import setting
from src.util import run_app, resource_path, load_icon


class GetHotkey(QDialog):
    hotkey = []

    def __init__(self, parent, hotkey):
        super().__init__(parent)
        self.label_disc = QLabel("热键可以是shift、control、alt中的一个或多个，外加一个字母键。请留意，为防止冲突，热键必须存在字母键。\nESC：禁止热键")
        self.label_disc.setWordWrap(True)
        self.label = QLabel(hotkey)
        self.btn = QPushButton("OK")
        self.btn.setFixedWidth(80)
        self.btn.clicked.connect(self.accept)
        layout = create_multi_line([
            create_line([1, self.label_disc, 1]),
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

    def __init__(self, parent, passwd):
        super().__init__(parent)
        self.setWindowTitle("安装OCR服务")
        self.setFixedSize(QSize(640, 480))
        self.edit = QTextEdit()
        self.edit.setAcceptRichText(False)
        self.edit.setReadOnly(True)

        self.flag = '.'
        self.label = QLabel("请耐心等待，正在安装中" + self.flag)
        self.setLayout(create_multi_line([self.edit, self.label]))

        self.timer = QTimer()
        self.timer.timeout.connect(self.on_timeout)
        self.timer.start(1000)

        self.signal_log.connect(self.on_log)
        self.signal_finish.connect(self.on_finish)
        self.t = threading.Thread(target=self.do_install, args=(passwd, ))
        self.t.start()

    def on_timeout(self):
        self.flag += '.'
        if len(self.flag) > 3:
            self.flag = ''
        self.label.setText("请耐心等待，正在安装中" + self.flag)

    def on_log(self, txt):
        self.edit.append(txt)

    def on_finish(self, ret):
        self.timer.stop()
        if ret != 0:
            self.label.setText("安装失败")
            QMessageBox.warning(self, "错误", "安装失败。您可以手动安装Ocr服务，或者到项目主页报告问题。")
            return
        self.label.setText("安装成功，需重启系统或注销重新登录方能生效。")
        QMessageBox.information(self, "提示", "安装成功，需重启系统或注销重新登录方能生效。")

    def do_install(self, passwd):
        cmd = "bash {} install".format(resource_path("res/ocr.sh"))
        ret = run_app(cmd, lambda x: self.signal_log.emit(x), passwd=passwd)
        self.signal_finish.emit(ret)


class SettingWindow(QWidget):
    signal_check_install = pyqtSignal(int)
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

        self.checkbox_hide_when_close = QCheckBox("关闭主窗口时自动隐藏而不退出")

        self.edit_main_hotkey = QPushButton()
        self.edit_main_hotkey.setFlat(True)

        self.checkbox_use_dark_skin = QCheckBox("使用灰色主题")

        self.checkbox_support_clipboard = QCheckBox("支持剪贴板取词")
        self.slider_clipboard_count_label = QLabel("    复制相同内容{}次触发".format(setting.clipboard_count))
        self.slider_clipboard_second_label = QLabel("    同一内容{:.1f}秒后失效".format(setting.clipboard_second))
        self.slider_clipboard_count = QSlider(Qt.Horizontal)
        self.slider_clipboard_count.setRange(1, 9)
        self.slider_clipboard_count.setSingleStep(1)
        self.slider_clipboard_count.setTickInterval(1)
        self.slider_clipboard_count.setTickPosition(QSlider.TicksAbove)
        self.slider_clipboard_second = QSlider(Qt.Horizontal)
        self.slider_clipboard_second.setRange(500, 5000)
        self.slider_clipboard_second.setSingleStep(100)
        self.slider_clipboard_second.setTickInterval(100)
        self.slider_clipboard_second.setTickPosition(QSlider.TicksAbove)

        self.checkbox_support_ocr = QCheckBox("OCR取词")

        self.edit_ocr_hotkey = QPushButton()
        self.edit_ocr_hotkey.setFlat(True)

        self.edit_ocr_server = QLineEdit()
        self.edit_ocr_server.setReadOnly(True)
        self.edit_ocr_server.setPlaceholderText("取词服务器")

        self.button_ocr_server = QPushButton("安装")
        self.button_ocr_server.setMinimumWidth(120)
        self.button_ocr_server_help = QPushButton()
        self.button_ocr_server_help.setFlat(True)
        self.button_ocr_server_help.clicked.connect(self.on_ocr_server_help)
        self.button_ocr_server_help.setIcon(load_icon('help_32x32'))

        self.checkbox_show_main_window_when_startup = QCheckBox("启动时显示主窗口")

        self.checkbox_auto_startup = QCheckBox("开机时启动")

        self.btn_create_desktop = QPushButton("创建快捷方式")

        self.btn_download_dict = QPushButton("下载离线词典")

        self.btn_reset = QPushButton("重置所有设置")
        url_project = QLabel(
            u'<a href="https://github.com/xxNull-lsk/my_dict">'
            u'https://github.com/xxNull-lsk/my_dict'
            u'</a>'
        )
        url_project.setOpenExternalLinks(True)
        url_doc = QLabel(
            u'<a href="https://blog.mydata.top/index.php/category/mydict/">'
            u'https://blog.mydata.top/index.php/category/mydict/'
            u'</a>'
        )
        url_doc.setOpenExternalLinks(True)
        url_email = QLabel(u'<a href="mailto:xxNull@163.com">联系我</a>')
        url_email.setOpenExternalLinks(True)

        self.edit_dict_folder = QLineEdit()
        self.btn_select_dict_folder = QPushButton("...")
        self.btn_select_dict_folder.setMinimumWidth(80)
        self.btn_open_dict_folder = QPushButton("浏览")
        self.btn_open_dict_folder.setMinimumWidth(80)

        self.list_query_dicts = QListWidget()
        self.list_clipboard_dicts = QListWidget()
        self.init_dict()
        line_dicts = create_line([
            create_multi_line(["查询词典:", self.list_query_dicts]),
            create_multi_line(["取词词典:", self.list_clipboard_dicts])
        ])
        items = [
            [self.checkbox_auto_startup],
            [self.checkbox_show_main_window_when_startup],
            [self.checkbox_hide_when_close],
            ["    显示主窗口热键:", create_line([self.edit_main_hotkey])],
            [self.checkbox_use_dark_skin],
            [self.checkbox_support_clipboard],
            [self.slider_clipboard_count_label, create_line([self.slider_clipboard_count]), ],
            [self.slider_clipboard_second_label, create_line([self.slider_clipboard_second]), ],
            [self.checkbox_support_ocr],
            ["    取词热键:", create_line([self.edit_ocr_hotkey])],
            ["    取词服务器:", create_line([self.edit_ocr_server, self.button_ocr_server, self.button_ocr_server_help])],
            [create_line(["离线词典目录:", self.edit_dict_folder, self.btn_select_dict_folder, self.btn_open_dict_folder])],
            [line_dicts],
            [create_line([self.btn_create_desktop, self.btn_download_dict, self.btn_reset])],
            [create_line(["项目地址：", url_project, "文档地址：", url_doc, "", url_email])]
        ]

        self.init_data()
        self.checkbox_use_dark_skin.clicked.connect(self.on_save)
        self.checkbox_support_clipboard.clicked.connect(self.on_save)
        self.slider_clipboard_count.valueChanged.connect(self.on_clipboard_count_changed)
        self.slider_clipboard_second.valueChanged.connect(self.on_clipboard_second_changed)
        self.checkbox_hide_when_close.clicked.connect(self.on_save)
        self.checkbox_support_ocr.clicked.connect(self.on_save)
        self.edit_ocr_hotkey.clicked.connect(self.on_change_ocr_hotkey)
        self.edit_main_hotkey.clicked.connect(self.on_change_main_hotkey)
        self.edit_ocr_server.textChanged.connect(self.on_save)
        self.button_ocr_server.clicked.connect(self.on_install_ocr_server)
        self.checkbox_show_main_window_when_startup.clicked.connect(self.on_save)
        self.checkbox_auto_startup.clicked.connect(self.on_auto_startup)
        self.btn_create_desktop.clicked.connect(self.on_create_desktop)
        self.btn_download_dict.clicked.connect(self.on_download_dict)
        self.btn_reset.clicked.connect(self.on_reset)
        self.btn_open_dict_folder.clicked.connect(self.on_open_dict_folder)
        self.btn_select_dict_folder.clicked.connect(self.on_select_dict_folder)

        self.setLayout(create_multi_line([create_grid(items)]))

        self.signal_check_install.connect(self.on_check_install)
        self.t = threading.Thread(target=self.do_check_install_ocr)
        self.t.start()

    def init_data(self):
        self.checkbox_hide_when_close.setChecked(setting.hide_when_close)
        self.edit_main_hotkey.setText(
            " - ".join(setting.main_hotkey).upper() if len(setting.main_hotkey) > 0 else '禁用'
        )
        self.edit_ocr_server.setText(setting.ocr_server)
        self.checkbox_use_dark_skin.setChecked(setting.use_dark_skin)
        self.edit_ocr_hotkey.setText(
            " - ".join(setting.ocr_hotkey).upper() if len(setting.ocr_hotkey) > 0 else '禁用'
        )
        self.edit_dict_folder.setText(setting.star_dict_folder)

        self.checkbox_support_clipboard.setChecked(setting.support_clipboard)
        self.slider_clipboard_count.setValue(setting.clipboard_count)
        self.slider_clipboard_second.setValue(int(setting.clipboard_second * 1000))
        self.slider_clipboard_count_label.setText("    复制相同内容{}次触发".format(setting.clipboard_count))
        self.slider_clipboard_second_label.setText("    同一内容{:.1f}秒后失效".format(setting.clipboard_second))
        self.checkbox_support_ocr.setChecked(setting.support_ocr)
        self.checkbox_show_main_window_when_startup.setChecked(setting.show_main_window_when_startup)
        self.checkbox_auto_startup.setChecked(setting.auto_start)
        if setting.auto_start:
            self.on_auto_startup()

    def on_check_install(self, ret):
        if ret == 0:
            self.button_ocr_server.setText("更新/重装")
            self.button_ocr_server.setToolTip("已经安装，点击更新OCR服务器")
        else:
            self.button_ocr_server.setText("安装")
            self.button_ocr_server.setToolTip("点击安装OCR服务器")

    def do_check_install_ocr(self):
        cmd = "bash {} check_install".format(resource_path("res/ocr.sh"))
        ret = run_app(cmd)
        self.signal_check_install.emit(ret)

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

    def on_clipboard_count_changed(self, val):
        setting.clipboard_count = val
        setting.save()
        self.slider_clipboard_count_label.setText("    复制相同内容{}次触发".format(setting.clipboard_count))

    def on_clipboard_second_changed(self, val):
        setting.clipboard_second = val / 1000
        setting.save()
        self.slider_clipboard_second_label.setText("    同一内容{:.1f}秒后失效".format(setting.clipboard_second))

    def on_save(self):
        setting.hide_when_close = self.checkbox_hide_when_close.isChecked()
        setting.use_dark_skin = self.checkbox_use_dark_skin.isChecked()
        setting.support_clipboard = self.checkbox_support_clipboard.isChecked()
        setting.support_ocr = self.checkbox_support_ocr.isChecked()
        setting.show_main_window_when_startup = self.checkbox_show_main_window_when_startup.isChecked()
        setting.star_dict_folder = self.edit_dict_folder.text()
        setting.save()
        self.slider_clipboard_count.setEnabled(setting.support_clipboard)
        self.slider_clipboard_second.setEnabled(setting.support_clipboard)

    def on_auto_startup(self):
        if os.path.exists(self.auto_startup_filename):
            os.remove(self.auto_startup_filename)
        folder = os.path.split(self.auto_startup_filename)[0]
        if not os.path.exists(folder):
            os.makedirs(folder)
        if self.checkbox_auto_startup.isChecked():
            with open(self.auto_startup_filename, "w+") as f:
                f.write(self.cfg_desktop)

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
        passwd, succeed = QInputDialog.getText(
            self,
            "请输入密码",
            "安装OCR服务需要管理员权限，\n请输入当前用户密码以提升权限：",
            QLineEdit.Password)
        if not succeed or passwd is None or passwd == '':
            return
        dd = InstallOcrWindow(self, passwd)
        dd.exec_()

    def on_change_ocr_hotkey(self):
        dd = GetHotkey(self, self.edit_ocr_hotkey.text())
        ret = dd.exec_()
        if ret == 1:
            self.edit_ocr_hotkey.setText(' - '.join(dd.hotkey).upper() if len(dd.hotkey) > 0 else '禁用')
            setting.ocr_hotkey = dd.hotkey
            setting.save()

    def on_change_main_hotkey(self):
        dd = GetHotkey(self, self.edit_main_hotkey.text())
        ret = dd.exec_()
        if ret == 1:
            self.edit_main_hotkey.setText(' - '.join(dd.hotkey).upper() if len(dd.hotkey) > 0 else '禁用')
            setting.main_hotkey = dd.hotkey
            setting.save()

    def on_reset(self):
        setting.reset()
        self.init_data()
        self.on_save()

    @staticmethod
    def on_ocr_server_help():
        QDesktopServices.openUrl(QUrl("https://blog.mydata.top/index.php/mydict999900.html"))
