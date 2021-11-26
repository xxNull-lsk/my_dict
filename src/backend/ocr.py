import base64
import json

from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtWidgets import QApplication
import zmq
import cv2
import numpy as np

from src.UI.ocr_mask import UiOcrMask
from src.setting import setting
from src.util import run_app, resource_path
import threading


class OcrServer(QObject):
    socket = None
    signal_start_finish = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.context = zmq.Context()
        self.signal_start_finish.connect(self.on_start_finish)
        self.t = threading.Thread(target=self.start_local_server)
        self.t.start()

    def __del__(self):
        cmd = "bash {} stop".format(resource_path("res/ocr.sh"))
        run_app(cmd, print)

    def start_local_server(self):
        cmd = "bash {} start".format(resource_path("res/ocr.sh"))
        ret = run_app(cmd, print)
        self.signal_start_finish.emit(ret)

    def on_start_finish(self, ret):
        if ret != 0:
            return
        self.socket: zmq.Socket = self.context.socket(zmq.REQ)
        self.socket.connect(setting.ocr_server)
        self.socket.setsockopt(zmq.RCVTIMEO, 500)
        self.socket.setsockopt(zmq.SNDTIMEO, 500)

    def get_english(self, mat):
        if self.socket is None:
            return {
                "code": -1,
                "message": str("OCR服务器尚未启动。")
            }
        img = cv2.imencode('.jpg', mat)[1]
        data = {
            "function": "/ocr/get_english",
            "image": base64.b64encode(img).decode('utf8')
        }
        try:
            self.socket.send_string(json.dumps(data))
            response = self.socket.recv_string()
            return json.loads(response)
        except Exception as ex:
            print("Exception: ", ex)
            self.on_start_finish(0)
            return {
                "code": -1,
                "message": str(ex)
            }


class OCR:
    def __init__(self, app: QApplication):
        self.app = app
        self.server = OcrServer()

    @staticmethod
    def img_to_mat(img):
        temp_shape = (img.height(), img.bytesPerLine() * 8 // img.depth())
        temp_shape += (4,)
        ptr = img.bits()
        ptr.setsize(img.byteCount())
        result = np.array(ptr, dtype=np.uint8).reshape(temp_shape)
        result = result[..., :3]
        return result

    def get_text(self):
        mask = UiOcrMask(self.app.desktop().winId(), self.app.primaryScreen())
        if mask.exec_() == 0 or mask.select_image.isNull():
            return False, ''
        mat = self.img_to_mat(mask.select_image)
        result = self.server.get_english(mat)
        if result["code"] != 0:
            return False, result["message"]
        if len(result["data"]) > 0:
            return True, result["data"][0]["text"]
        return False, "无法识别。"
