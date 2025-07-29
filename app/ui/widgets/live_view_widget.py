# app/ui/widgets/live_view_widget.py

from pathlib import Path
from PySide6 import QtWidgets, QtGui, QtCore

class LiveViewWidget(QtWidgets.QLabel):
    def __init__(self, camera, parent=None):
        super().__init__(parent)
        self.camera = camera
        self.setFixedSize(640, 480)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setText('LiveView')
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(500)

    def update_frame(self):
        from tempfile import NamedTemporaryFile
        with NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
            path = Path(tmp.name)
        try:
            self.camera.capture_preview(path)
            pix = QtGui.QPixmap(str(path))
            if not pix.isNull():
                self.setPixmap(pix.scaled(self.size(), QtCore.Qt.KeepAspectRatio))
        finally:
            path.unlink(missing_ok=True)

from PySide6 import QtWidgets, QtGui, QtCore

class LiveViewWidget(QtWidgets.QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(640, 480)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setText('LiveView')

