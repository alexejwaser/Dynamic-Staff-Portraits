# app/ui/widgets/live_view_widget.py
from pathlib import Path
from PySide6 import QtWidgets, QtGui, QtCore

class LiveViewWidget(QtWidgets.QLabel):
    def __init__(self, camera, fps: int = 20, parent=None):
        super().__init__(parent)
        self.camera = camera
        self.setMinimumSize(320, 240)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setStyleSheet('background-color: black;')
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(max(30, int(1000 / max(1, fps))))

    def set_camera(self, camera):
        self.camera = camera

    def update_frame(self):
        try:
            if hasattr(self.camera, 'get_preview_qimage'):
                img = self.camera.get_preview_qimage()
            else:
                from tempfile import NamedTemporaryFile
                with NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
                    path = Path(tmp.name)
                try:
                    self.camera.capture_preview(path)
                    img = QtGui.QImage(str(path))
                finally:
                    path.unlink(missing_ok=True)
            if not img.isNull():
                pix = QtGui.QPixmap.fromImage(img)
                self.setPixmap(pix.scaled(self.size(), QtCore.Qt.KeepAspectRatio))
        except Exception as e:
            self.setText(str(e))