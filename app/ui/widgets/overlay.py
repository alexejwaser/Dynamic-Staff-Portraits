# app/ui/widgets/overlay.py
from PySide6 import QtWidgets, QtGui, QtCore

class Overlay(QtWidgets.QWidget):

    """Draw various overlay helpers above der LiveView."""

    def __init__(self, parent=None, mode: str = "thirds"):
        super().__init__(parent)
        self.mode = mode

        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground)
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)


    def set_mode(self, mode: str):
        self.mode = mode
        self.update()


    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        pen = QtGui.QPen(QtGui.QColor(255, 255, 255, 128))
        painter.setPen(pen)
        w, h = self.width(), self.height()

        if self.mode == "thirds":
            painter.drawLine(w // 3, 0, w // 3, h)
            painter.drawLine(2 * w // 3, 0, 2 * w // 3, h)
            painter.drawLine(0, h // 3, w, h // 3)
            painter.drawLine(0, 2 * h // 3, w, 2 * h // 3)
        elif self.mode == "crosshair":
            painter.drawLine(w // 2, 0, w // 2, h)
            painter.drawLine(0, h // 2, w, h // 2)

