import os
import sys

from PyQt5.QtWidgets import QVBoxLayout, QWidget, QCheckBox, QPushButton, QHBoxLayout

from src.setting import setting


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

    def __init__(self, parent):
        super().__init__(parent)
        self.support_clipboard = QCheckBox("剪贴板取词（复制两次触发取词）")
        self.support_clipboard.setToolTip("复制两次触发取词")
        self.support_clipboard.clicked.connect(self.on_save)
        self.show_main_window_when_startup = QCheckBox("启动时显示主窗口")
        self.show_main_window_when_startup.clicked.connect(self.on_save)
        self.auto_startup = QCheckBox("开机时启动")
        self.auto_startup.clicked.connect(self.on_auto_startup)
        self.create_desktop = QPushButton("创建快捷方式")
        self.create_desktop.setMinimumWidth(180)
        self.create_desktop.clicked.connect(self.on_create_desktop)

        self.support_clipboard.setChecked(setting.support_clipboard)
        self.show_main_window_when_startup.setChecked(setting.show_main_window_when_startup)
        self.auto_startup.setChecked(self.is_auto_startup())

        vbox = QVBoxLayout()
        vbox.setSpacing(8)
        vbox.addWidget(self.support_clipboard)
        vbox.addWidget(self.show_main_window_when_startup)
        vbox.addWidget(self.auto_startup)
        hbox = QHBoxLayout()
        hbox.addWidget(self.create_desktop)
        hbox.addStretch(1)
        vbox.addItem(hbox)
        vbox.addStretch(1)

        self.setLayout(vbox)

    def on_save(self):
        setting.support_clipboard = self.support_clipboard.isChecked()
        setting.show_main_window_when_startup = self.show_main_window_when_startup.isChecked()
        setting.save()

    def is_auto_startup(self):
        return os.path.exists(self.auto_startup_filename)

    def on_auto_startup(self):
        if self.auto_startup.isChecked():
            with open(self.auto_startup_filename, "w+") as f:
                f.write(self.cfg_desktop)
        else:
            if os.path.exists(self.auto_startup_filename):
                os.remove(self.auto_startup_filename)

    def on_create_desktop(self):
        with open("{}/.local/share/applications/my_dict.desktop".format(os.environ["HOME"]), "w+") as f:
            f.write(self.cfg_desktop)

