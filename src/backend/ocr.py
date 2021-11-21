import base64
import json

from PyQt5.QtWidgets import QApplication
import zmq
import cv2
import numpy as np

from src.UI.ocr_mask import UiOcrMask
from src.setting import setting
from src.util import run_app, resource_path
import threading


class OcrServer:
    def __init__(self):
        self.context = zmq.Context()
        self.socket: zmq.Socket = self.context.socket(zmq.REQ)
        self.socket.connect(setting.ocr_server)
        self.socket.setsockopt(zmq.RCVTIMEO, 1000)
        self.socket.setsockopt(zmq.SNDTIMEO, 1000)
        self.t = threading.Thread(target=self.start_local_server)
        self.t.start()

    def __del__(self):
        cmd = "bash {} stop".format(resource_path("./res/ocr.sh"))
        run_app(cmd, print)

    @staticmethod
    def start_local_server():
        cmd = "bash {} start".format(resource_path("./res/ocr.sh"))
        run_app(cmd, print)

    def get_english(self, mat):
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
            return ''
        mat = self.img_to_mat(mask.select_image)
        result = self.server.get_english(mat)
        print("result", result)
        if result["code"] != 0:
            return ''
        if len(result["data"]) > 0:
            return result["data"][0]["text"]
        return ''
