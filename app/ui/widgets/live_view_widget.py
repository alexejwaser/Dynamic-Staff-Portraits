# app/ui/widgets/live_view_widget.py
from PySide6 import QtWidgets, QtGui, QtCore

class LiveViewWidget(QtWidgets.QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(640, 480)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setText('LiveView')
