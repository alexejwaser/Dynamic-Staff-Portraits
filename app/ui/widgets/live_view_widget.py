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
        self.label.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding,
        )
        self.frame_ratio = 3 / 4
        self.overlay = Overlay()
        layout = QtWidgets.QStackedLayout(self)
        layout.setStackingMode(QtWidgets.QStackedLayout.StackAll)
        layout.addWidget(self.label)
        layout.addWidget(self.overlay)
        # Sicherstellen, dass das Overlay ueber dem Bild liegt
        self.overlay.raise_()
        self.overlay.show()
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(max(30, int(1000 / max(1, fps))))

    def _update_label_geometry(self):
        if self.frame_ratio <= 0:
            return
        w, h = self.width(), self.height()
        if w / h > self.frame_ratio:
            new_w = int(h * self.frame_ratio)
            new_h = h
        else:
            new_w = w
            new_h = int(w / self.frame_ratio)
        x = (w - new_w) // 2
        y = (h - new_h) // 2
        self.label.setGeometry(x, y, new_w, new_h)
        self.overlay.setGeometry(self.label.geometry())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_label_geometry()

    def sizeHint(self):
        if self.frame_ratio >= 1:
            return QtCore.QSize(480, int(480 / self.frame_ratio))
        else:
            return QtCore.QSize(int(640 * self.frame_ratio), 640)

    def set_camera(self, camera):
        self.camera = camera

    def set_overlay_image(self, path: str | Path | None):
        self.overlay.set_image(path)

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
                self.frame_ratio = img.width() / img.height()
                self._update_label_geometry()
                pix = QtGui.QPixmap.fromImage(img).scaled(
                    self.label.size(),
                    QtCore.Qt.KeepAspectRatio,
                    QtCore.Qt.SmoothTransformation,
                )
                self.label.setPixmap(pix)
        except Exception as e:
            self.label.setText(str(e))
