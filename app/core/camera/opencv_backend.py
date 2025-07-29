# app/core/camera/opencv_backend.py
from pathlib import Path
import cv2
from PySide6 import QtGui
from .base import BaseCamera, CameraError


class OpenCVCamera(BaseCamera):
    def __init__(self, camera_id: int = 0):
        self.camera_id = camera_id
        self.cap = None

    def start_liveview(self):
        if self.cap is None:
            self.cap = cv2.VideoCapture(self.camera_id, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            raise CameraError(f"Kamera {self.camera_id} kann nicht geoeffnet werden")

    def stop_liveview(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None

    def _ensure_open(self):
        if self.cap is None:
            self.start_liveview()

    def capture(self, dest: Path) -> None:
        self._ensure_open()
        ret, frame = self.cap.read()
        if not ret:
            raise CameraError("Kein Bild von Kamera erhalten")
        frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
        cv2.imwrite(str(dest), frame)

    def capture_preview(self, dest: Path) -> None:
        self.capture(dest)

    def get_preview_qimage(self) -> QtGui.QImage:
        self._ensure_open()
        ret, frame = self.cap.read()
        if not ret:
            raise CameraError("Kein Bild von Kamera erhalten")
        frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bytes_per_line = ch * w
        img = QtGui.QImage(rgb.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        return img.copy()

    def switch_camera(self, camera_id: int):
        self.stop_liveview()
        self.camera_id = camera_id
        self.start_liveview()
