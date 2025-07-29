# app/ui/widgets/live_view_widget.py
from pathlib import Path
from PySide6 import QtWidgets, QtGui, QtCore
from .overlay import Overlay

class LiveViewWidget(QtWidgets.QWidget):
    """Widget zur Anzeige des Live-Streams mit einblendbarem Overlay."""

    def __init__(self, camera, fps: int = 20, parent=None):
        super().__init__(parent)
        self.camera = camera
        self.label = QtWidgets.QLabel()
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setStyleSheet("background-color: black;")
        self.label.setMinimumSize(320, 240)
        self.overlay = Overlay()
        layout = QtWidgets.QStackedLayout(self)
        layout.setStackingMode(QtWidgets.QStackedLayout.StackAll)
        layout.addWidget(self.label)
        layout.addWidget(self.overlay)
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(max(30, int(1000 / max(1, fps))))

    def set_camera(self, camera):
        self.camera = camera

    def set_overlay_mode(self, mode: str):
        self.overlay.set_mode(mode)
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
                self.label.setPixmap(pix.scaled(self.size(), QtCore.Qt.KeepAspectRatio))
        except Exception as e:
            self.label.setText(str(e))
