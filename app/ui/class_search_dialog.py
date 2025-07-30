from PySide6 import QtWidgets, QtCore

class ClassSearchDialog(QtWidgets.QDialog):
    def __init__(self, classes, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Klasse suchen')
        self.classes = list(classes)
        layout = QtWidgets.QVBoxLayout(self)
        self.edit = QtWidgets.QLineEdit()
        self.edit.setPlaceholderText('Klasse eingeben...')
        completer = QtWidgets.QCompleter(self.classes, self)
        completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        completer.setFilterMode(QtCore.Qt.MatchContains)
        self.edit.setCompleter(completer)
        layout.addWidget(self.edit)
        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        layout.addWidget(buttons)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

    def selected_class(self):
        text = self.edit.text().strip()
        for c in self.classes:
            if c.lower() == text.lower():
                return c
        return None
