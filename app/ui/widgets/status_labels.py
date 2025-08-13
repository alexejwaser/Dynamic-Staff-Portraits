from PySide6 import QtWidgets, QtCore


class StatusLabels(QtWidgets.QWidget):
    """Widget showing current and upcoming learner labels."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QtWidgets.QHBoxLayout(self)
        self.label_current = QtWidgets.QLabel('')
        self.label_current.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.label_current.setStyleSheet('font-size:16px;')
        self.label_upcoming = QtWidgets.QLabel('')
        self.label_upcoming.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.label_upcoming.setStyleSheet('font-size:12px; color: gray;')
        layout.addWidget(self.label_current)
        layout.addStretch()
        layout.addWidget(self.label_upcoming)

    def set_current(self, text: str):
        self.label_current.setText(text)

    def set_upcoming(self, text: str):
        self.label_upcoming.setText(text)
