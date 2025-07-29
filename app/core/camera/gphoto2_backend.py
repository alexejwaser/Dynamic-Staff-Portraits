# app/core/camera/gphoto2_backend.py
from pathlib import Path
import subprocess
import tempfile
from PySide6 import QtGui
from .base import BaseCamera, CameraError

class GPhoto2Camera(BaseCamera):
    def __init__(self):
        self.running = False

    def start_liveview(self):
        self.running = True

    def stop_liveview(self):
        self.running = False

    def capture(self, dest: Path) -> None:
        cmd = [
            'gphoto2',
            '--capture-image-and-download',
            '--filename', str(dest)
        ]
        proc = subprocess.run(cmd, capture_output=True)
        if proc.returncode != 0:
            raise CameraError(proc.stderr.decode(errors='ignore'))

    def capture_preview(self, dest: Path) -> None:
        cmd = [
            'gphoto2',
            '--capture-preview',
            '--filename', str(dest)
        ]
        proc = subprocess.run(cmd, capture_output=True)
        if proc.returncode != 0:
            raise CameraError(proc.stderr.decode(errors='ignore'))

    def get_preview_qimage(self) -> QtGui.QImage:
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
            path = Path(tmp.name)
        try:
            self.capture_preview(path)
            img = QtGui.QImage(str(path))
            return img
        finally:
            path.unlink(missing_ok=True)