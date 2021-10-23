import base64
import json

from PyQt5.QtCore import QRect
from PyQt5.QtGui import QScreen, QCursor, QPixmap
from PyQt5.QtWidgets import QApplication
import zmq
import cv2
import numpy as np

from src.setting import setting


class OcrServer:
    def __init__(self):
        self.context = zmq.Context()
        self.socket: zmq.Socket = self.context.socket(zmq.REQ)
        self.socket.connect(setting.ocr_server)

    def get_english(self, mat):
        img = cv2.imencode('.jpg', mat)[1]
        data = {
            "function": "/ocr/get_english",
            "image": base64.b64encode(img).decode('utf8')
        }
        self.socket.send_string(json.dumps(data))
        response = self.socket.recv_string()
        return json.loads(response)


class OCR:
    def __init__(self, app: QApplication):
        self.app = app
        self.server = OcrServer()

    @staticmethod
    def pixmap_to_mat(pixmap):
        img = pixmap.toImage()
        temp_shape = (img.height(), img.bytesPerLine() * 8 // img.depth())
        temp_shape += (4,)
        ptr = img.bits()
        ptr.setsize(img.byteCount())
        result = np.array(ptr, dtype=np.uint8).reshape(temp_shape)
        result = result[..., :3]
        return result

    def get_text(self):
        # print("OCR: get_text")
        screen: QScreen = self.app.primaryScreen()
        screen_rect: QRect = screen.geometry()
        pos = QCursor().pos()
        # x = max(0, pos.x() - 200)
        x = 0
        y = max(0, pos.y() - 20)
        # width = min(400, screen_rect.width() - x)
        width = screen_rect.width()
        height = min(40, screen_rect.height() - y)
        # print("pos: ", pos.x(), pos.y(), width, height)
        shot: QPixmap = screen.grabWindow(
            self.app.desktop().winId(),
            x,
            y,
            width=width,
            height=height,
        )
        # shot.save('1.bmp')
        mat = self.pixmap_to_mat(shot)
        result = self.server.get_english(mat)
        if result["code"] != 0:
            return ''
        # print('result', result)
        for item in result["data"]:
            rect = item['rect']
            if x + rect[0] < pos.x() <= x + rect[0] + rect[2] and rect[1] + y < pos.y() <= rect[1] + rect[3] + y:
                return item['text']
        return ''
