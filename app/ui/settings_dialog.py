# app/ui/settings_dialog.py
from PySide6 import QtWidgets
import logging
from pathlib import Path
from ..core.config.settings import Settings


class SettingsDialog(QtWidgets.QDialog):
    def __init__(self, settings: Settings, parent=None, logger: logging.Logger | None = None):
        super().__init__(parent)
        self.logger = logger or logging.getLogger(__name__)
        self.settings = settings
        self.setWindowTitle('Einstellungen')

        form = QtWidgets.QFormLayout(self)

        self.cmb_camera = QtWidgets.QComboBox()
        self.cmb_camera.addItems(['Webcam', 'GPhoto2', 'Simulator'])
        backend = self.settings.kamera.get('backend', 'opencv')
        mapping = {'opencv': 0, 'gphoto2': 1, 'simulator': 2}
        self.cmb_camera.setCurrentIndex(mapping.get(backend, 0))
        form.addRow('Kamera', self.cmb_camera)

        # output directory
        self.output_dir = str(self.settings.ausgabeBasisPfad)
        self.lbl_output = QtWidgets.QLabel(self.output_dir)
        self.btn_output = QtWidgets.QPushButton('Ordner wählen...')
        h_out = QtWidgets.QHBoxLayout()
        h_out.addWidget(self.lbl_output)
        h_out.addWidget(self.btn_output)
        form.addRow('Ausgabeordner', h_out)
        self.btn_output.clicked.connect(self.choose_output)

        # missed file path
        self.missed_path = str(self.settings.missedPath)
        self.lbl_missed = QtWidgets.QLabel(Path(self.missed_path).as_posix())
        self.btn_missed = QtWidgets.QPushButton('Datei wählen...')
        h_miss = QtWidgets.QHBoxLayout()
        h_miss.addWidget(self.lbl_missed)
        h_miss.addWidget(self.btn_missed)
        form.addRow('Verpasste Termine', h_miss)
        self.btn_missed.clicked.connect(self.choose_missed)

        self.overlay_path = self.settings.overlay.get('image', '')
        self.lbl_overlay = QtWidgets.QLabel(Path(self.overlay_path).name if self.overlay_path else 'Kein Overlay')
        self.btn_overlay = QtWidgets.QPushButton('Overlay wählen...')
        h_overlay = QtWidgets.QHBoxLayout()
        h_overlay.addWidget(self.lbl_overlay)
        h_overlay.addWidget(self.btn_overlay)
        form.addRow('Overlay-Bild', h_overlay)
        self.btn_overlay.clicked.connect(self.choose_overlay)

        emap = self.settings.excelMapping
        self.ed_class = QtWidgets.QLineEdit(emap.get('klasse', 'A'))
        self.ed_last = QtWidgets.QLineEdit(emap.get('nachname', 'B'))
        self.ed_first = QtWidgets.QLineEdit(emap.get('vorname', 'C'))
        self.ed_id = QtWidgets.QLineEdit(emap.get('schuelerId', 'D'))
        self.ed_photo = QtWidgets.QLineEdit(emap.get('fotografiert', 'E'))
        self.ed_date = QtWidgets.QLineEdit(emap.get('aufnahmedatum', 'F'))
        self.ed_reason = QtWidgets.QLineEdit(emap.get('grund', 'G'))
        form.addRow('Spalte Klasse', self.ed_class)
        form.addRow('Spalte Nachname', self.ed_last)
        form.addRow('Spalte Vorname', self.ed_first)
        form.addRow('Spalte SchülerID', self.ed_id)
        form.addRow('Spalte Fotografiert', self.ed_photo)
        form.addRow('Spalte Aufnahmedatum', self.ed_date)
        form.addRow('Spalte Grund', self.ed_reason)

        self.buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        form.addRow(self.buttons)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

    def choose_overlay(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'PNG wählen', filter='PNG (*.png)')
        if path:
            self.overlay_path = path
            self.lbl_overlay.setText(Path(path).name)

    def choose_output(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, 'Ordner wählen', self.output_dir)
        if path:
            self.output_dir = path
            self.lbl_output.setText(path)

    def choose_missed(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'Datei wählen', self.missed_path, filter='Excel (*.xlsx)')
        if path:
            if not path.lower().endswith('.xlsx'):
                path += '.xlsx'
            self.missed_path = path
            self.lbl_missed.setText(Path(path).as_posix())

    def accept(self):
        backend_idx = self.cmb_camera.currentIndex()
        backend = ['opencv', 'gphoto2', 'simulator'][backend_idx]
        self.settings.kamera['backend'] = backend
        self.settings.excelMapping = {
            'klasse': self.ed_class.text() or 'A',
            'nachname': self.ed_last.text() or 'B',
            'vorname': self.ed_first.text() or 'C',
            'schuelerId': self.ed_id.text() or 'D',
            'fotografiert': self.ed_photo.text() or 'E',
            'aufnahmedatum': self.ed_date.text() or 'F',
            'grund': self.ed_reason.text() or 'G',
        }
        self.settings.overlay['image'] = self.overlay_path
        self.settings.ausgabeBasisPfad = Path(self.output_dir)
        self.settings.missedPath = Path(self.missed_path)
        self.settings.save()
        super().accept()
