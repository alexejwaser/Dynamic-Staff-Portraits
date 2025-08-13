from PySide6 import QtWidgets
from .live_view_widget import LiveViewWidget


class PreviewPane(QtWidgets.QWidget):
    """Widget containing the live preview and camera switch button."""

    def __init__(self, camera, fps: int, overlay: str | None = None, parent=None):
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(10)
        self.preview = LiveViewWidget(camera, fps)
        if overlay:
            self.preview.set_overlay_image(overlay)
        layout.addWidget(self.preview)
        self.btn_switch_camera = QtWidgets.QPushButton('Kamera wechseln')
        self.btn_switch_camera.setFixedWidth(120)
        layout.addWidget(self.btn_switch_camera)

    def set_camera(self, camera):
        self.preview.set_camera(camera)

    def set_overlay_image(self, image: str | None):
        self.preview.set_overlay_image(image)
