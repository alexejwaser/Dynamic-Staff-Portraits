# app/ui/widgets/overlay.py
from pathlib import Path
from PySide6 import QtWidgets, QtGui, QtCore


class Overlay(QtWidgets.QWidget):
    """Zeigt ein optionales PNG-Bild ueber dem LiveView."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.pixmap = None
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground)
        # Unter Windows sorgt diese Flag-Kombination fuer korrekte Transparenz
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding,
        )

    def set_image(self, path: str | Path | None):
        if path and Path(path).exists():
            self.pixmap = QtGui.QPixmap(str(path))
        else:
            self.pixmap = None
        self.update()

    def paintEvent(self, event):
        if not self.pixmap:
            return
        painter = QtGui.QPainter(self)
        pix = self.pixmap.scaled(
            self.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation
        )
        x = (self.width() - pix.width()) // 2
        y = (self.height() - pix.height()) // 2
        painter.drawPixmap(x, y, pix)
