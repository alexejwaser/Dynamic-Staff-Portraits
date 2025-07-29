# app/core/camera/gphoto2_backend.py
from pathlib import Path
import subprocess
import tempfile
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
