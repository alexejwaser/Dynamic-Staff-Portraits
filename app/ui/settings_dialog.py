# app/ui/settings_dialog.py
from PySide6 import QtWidgets
from pathlib import Path
from ..core.config.settings import Settings


class SettingsDialog(QtWidgets.QDialog):
    def __init__(self, settings: Settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setWindowTitle('Einstellungen')

        form = QtWidgets.QFormLayout(self)

        self.cmb_camera = QtWidgets.QComboBox()
        self.cmb_camera.addItems(['Webcam', 'GPhoto2', 'Simulator'])
        backend = self.settings.kamera.get('backend', 'opencv')
        mapping = {'opencv': 0, 'gphoto2': 1, 'simulator': 2}
        self.cmb_camera.setCurrentIndex(mapping.get(backend, 0))
        form.addRow('Kamera', self.cmb_camera)

        emap = self.settings.excelMapping
        self.ed_class = QtWidgets.QLineEdit(emap.get('klasse', 'A'))
        self.ed_last = QtWidgets.QLineEdit(emap.get('nachname', 'B'))
        self.ed_first = QtWidgets.QLineEdit(emap.get('vorname', 'C'))
        self.ed_id = QtWidgets.QLineEdit(emap.get('schuelerId', 'D'))
        form.addRow('Spalte Klasse', self.ed_class)
        form.addRow('Spalte Nachname', self.ed_last)
        form.addRow('Spalte Vorname', self.ed_first)
        form.addRow('Spalte SchülerID', self.ed_id)

        self.buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        form.addRow(self.buttons)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

    def accept(self):
        backend_idx = self.cmb_camera.currentIndex()
        backend = ['opencv', 'gphoto2', 'simulator'][backend_idx]
        self.settings.kamera['backend'] = backend
        self.settings.excelMapping = {
            'klasse': self.ed_class.text() or 'A',
            'nachname': self.ed_last.text() or 'B',
            'vorname': self.ed_first.text() or 'C',
            'schuelerId': self.ed_id.text() or 'D',
        }
        self.settings.save()
        super().accept()
