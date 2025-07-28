# app/ui/widgets/overlay.py
from PySide6 import QtWidgets, QtGui, QtCore

class Overlay(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground)
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        pen = QtGui.QPen(QtGui.QColor(255, 255, 255, 128))
        painter.setPen(pen)
        w, h = self.width(), self.height()
        painter.drawLine(w//3, 0, w//3, h)
        painter.drawLine(2*w//3, 0, 2*w//3, h)
        painter.drawLine(0, h//3, w, h//3)
        painter.drawLine(0, 2*h//3, w, 2*h//3)
