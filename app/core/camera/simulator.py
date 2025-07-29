# app/core/camera/simulator.py
from pathlib import Path
from PIL import Image, ImageDraw
from PySide6 import QtGui
import time
from .base import BaseCamera


class SimulatorCamera(BaseCamera):
    def start_liveview(self):
        pass

    def stop_liveview(self):
        pass

    def capture(self, dest: Path) -> None:
        img = Image.new('RGB', (1920, 1080), (128, 128, 128))
        d = ImageDraw.Draw(img)
        d.text((10, 10), time.strftime('%H:%M:%S'), fill=(255, 255, 255))
        img.save(dest)

    def capture_preview(self, dest: Path) -> None:
        self.capture(dest)

    def get_preview_qimage(self) -> QtGui.QImage:
        img = Image.new('RGB', (640, 480), (80, 80, 80))
        d = ImageDraw.Draw(img)
        d.text((10, 10), time.strftime('%H:%M:%S'), fill=(255, 255, 255))
        data = img.tobytes('raw', 'RGB')
        qimg = QtGui.QImage(data, img.width, img.height, QtGui.QImage.Format_RGB888)
        return qimg
