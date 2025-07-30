# app/ui/main_window.py
from PySide6 import QtWidgets, QtGui, QtCore
from pathlib import Path
from ..core.config.settings import Settings
from ..core.camera import SimulatorCamera, GPhoto2Camera, OpenCVCamera
from .settings_dialog import SettingsDialog
from ..core.imaging.processor import process_image
from ..core.util.paths import class_output_dir, new_learner_dir
from ..core.excel.reader import ExcelReader, Learner
from ..core.excel.missed_writer import MissedWriter, MissedEntry
from datetime import datetime

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, settings: Settings):
        super().__init__()
        self.settings = settings
        self.camera = self._init_camera()
        self.reader = None
        self.learners = []
        self.current = 0
        self._setup_ui()
        if hasattr(self.camera, 'start_liveview'):
            self.camera.start_liveview()

    def _init_camera(self):
        backend = self.settings.kamera.get('backend', 'opencv')
        cam = None
        if backend == 'gphoto2' and QtCore.QStandardPaths.findExecutable('gphoto2'):
            cam = GPhoto2Camera()
        elif backend == 'canon':
            try:
                from ..core.camera.canon_sdk import CanonSDKCamera
                cam = CanonSDKCamera()
            except Exception:
                cam = None
        elif backend == 'simulator':
            cam = SimulatorCamera()
        else:
            try:
                cam = OpenCVCamera()
            except Exception:
                cam = None
        if cam is None:
            cam = SimulatorCamera()
        return cam

    def _setup_ui(self):
        self.setWindowTitle('LegicCard-Creator')
        self.setFixedSize(1000, 700)
        central = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(central)
        layout.setContentsMargins(20, 20, 20, 20)
        self.setCentralWidget(central)

        # left controls
        control = QtWidgets.QVBoxLayout()
        control.setSpacing(10)
        self.btn_excel = QtWidgets.QPushButton('Excel verbinden...')
        self.cmb_location = QtWidgets.QComboBox()
        self.cmb_location.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
        self.cmb_class = QtWidgets.QComboBox()
        self.cmb_class.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
        self.cmb_class.setMaxVisibleItems(25)
        self.btn_capture = QtWidgets.QPushButton('Foto aufnehmen')
        self.btn_skip = QtWidgets.QPushButton('Überspringen')
        self.btn_add_person = QtWidgets.QPushButton('Person hinzufügen')
        self.btn_finish = QtWidgets.QPushButton('Fertig')
        self.btn_settings = QtWidgets.QPushButton('')
        icon = self.style().standardIcon(QtWidgets.QStyle.SP_FileDialogDetailedView)
        self.btn_settings.setIcon(icon)
        self.btn_settings.setToolTip('Einstellungen')
        for w in [self.btn_excel, self.cmb_location, self.cmb_class,
                  self.btn_capture, self.btn_skip, self.btn_add_person,
                  self.btn_finish, self.btn_settings]:
            control.addWidget(w)
        control.addStretch()
        layout.addLayout(control)

        # right preview
        from .widgets.live_view_widget import LiveViewWidget
        fps = self.settings.kamera.get('liveviewFpsZiel', 20)
        self.preview = LiveViewWidget(self.camera, fps)
        self.preview.set_overlay_image(self.settings.overlay.get('image'))
        preview_layout = QtWidgets.QVBoxLayout()
        preview_layout.setSpacing(10)
        name_layout = QtWidgets.QHBoxLayout()
        self.label_current = QtWidgets.QLabel('')
        self.label_current.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.label_current.setStyleSheet('font-size:16px;')
        self.label_upcoming = QtWidgets.QLabel('')
        self.label_upcoming.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.label_upcoming.setStyleSheet('font-size:12px; color: gray;')
        name_layout.addWidget(self.label_current)
        name_layout.addStretch()
        name_layout.addWidget(self.label_upcoming)
        preview_layout.addLayout(name_layout)
        preview_layout.addWidget(self.preview)
        self.btn_switch_camera = QtWidgets.QPushButton('Kamera wechseln')
        self.btn_switch_camera.setFixedWidth(120)
        preview_layout.addWidget(self.btn_switch_camera)
        layout.addLayout(preview_layout)

        self.setStyleSheet(
            "* {font-family: 'Segoe UI';} QPushButton {padding:6px 12px;}\nQLabel{font-size:14px;}"
        )

        self.btn_excel.clicked.connect(self.load_excel)
        self.cmb_location.currentTextChanged.connect(self.update_classes)
        self.cmb_class.currentTextChanged.connect(self.load_learners)
        self.btn_capture.clicked.connect(self.capture_photo)
        self.btn_skip.clicked.connect(self.skip_learner)
        self.btn_add_person.clicked.connect(self.add_person)
        self.btn_finish.clicked.connect(self.finish_class)
        self.btn_switch_camera.clicked.connect(self.switch_camera)
        self.btn_settings.clicked.connect(self.open_settings)

        self._update_buttons()

    def load_excel(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Excel auswählen', filter='Excel (*.xlsx)')
        if not path:
            return
        self.reader = ExcelReader(Path(path), self.settings.excelMapping)
        self.cmb_location.clear()
        self.cmb_location.addItems(self.reader.locations())
        self._update_buttons()

    def update_classes(self, location: str):
        if not self.reader or not location:
            return
        self.cmb_class.clear()
        self.cmb_class.addItems(self.reader.classes_for_location(location))
        self._update_buttons()

    def load_learners(self, class_name: str):
        location = self.cmb_location.currentText()
        if not self.reader or not class_name:
            return
        self.learners = self.reader.learners(location, class_name)
        self.current = 0
        self.show_next()
        self._update_buttons()

    def show_next(self):
        if self.current >= len(self.learners):
            self.label_current.setText('Klasse abgeschlossen')
            self.label_upcoming.setText('')
            self._update_buttons()
            return
        l = self.learners[self.current]
        self.label_current.setText(f"{l.vorname} {l.nachname}")
        if self.current + 1 < len(self.learners):
            n = self.learners[self.current + 1]
            self.label_upcoming.setText(f"{n.vorname} {n.nachname}")
        else:
            self.label_upcoming.setText('')
        self._update_buttons()

    def capture_photo(self):
        if self.current >= len(self.learners):
            return
        learner = self.learners[self.current]
        location = self.cmb_location.currentText()
        if learner.is_new:
            out_dir = new_learner_dir(self.settings.ausgabeBasisPfad, location, learner.klasse)
            filename = f"{learner.vorname}_{learner.nachname}.jpg"
        else:
            out_dir = class_output_dir(self.settings.ausgabeBasisPfad, location, learner.klasse)
            filename = f"{learner.schueler_id}.jpg"
        raw_path = out_dir / filename
        try:
            self.camera.capture(raw_path)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, 'Aufnahme fehlgeschlagen', str(e))
            return
        aspect = self.settings.bild.get('seitenverhaeltnis', (3, 4))
        try:
            process_image(
                raw_path,
                raw_path,
                self.settings.bild['breite'],
                self.settings.bild['hoehe'],
                self.settings.bild['qualitaet'],
                aspect,
            )
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, 'Bildverarbeitung', str(e))
            raw_path.unlink(missing_ok=True)
            return
        if self._show_review(raw_path):
            self.current += 1
        else:
            raw_path.unlink(missing_ok=True)
        self.show_next()
        self._update_buttons()

    def skip_learner(self):
        if self.current >= len(self.learners):
            return
        reason, ok = QtWidgets.QInputDialog.getText(
            self,
            'Grund',
            'Grund für das Überspringen eingeben:',
        )
        if not ok:
            return
        learner = self.learners[self.current]
        missed = MissedWriter(Path('Verpasste_Termine.xlsx'))
        entry = MissedEntry(
            self.cmb_location.currentText(),
            learner.klasse,
            learner.nachname,
            learner.vorname,
            learner.schueler_id,
            datetime.now().isoformat(),
            reason,
        )
        missed.append(entry)
        self.current += 1
        self.show_next()
        self._update_buttons()

    def finish_class(self):
        location = self.cmb_location.currentText()
        klasse = self.cmb_class.currentText()
        out_dir = class_output_dir(self.settings.ausgabeBasisPfad, location, klasse)
        files = sorted(out_dir.glob('*.jpg'))
        if files:
            from ..core.archiver.chunk_zip import chunk_by_count
            zip_base = out_dir / f"{klasse}.zip"
            max_count = self.settings.zip.get('maxAnzahl') or len(files)
            zip_paths = chunk_by_count(files, zip_base, max_count)
        else:
            zip_paths = []

        msg = QtWidgets.QMessageBox(self)
        msg.setWindowTitle('Klasse abgeschlossen')
        if zip_paths:
            msg.setText(f'ZIP-Archiv {zip_paths[0].name} wurde erstellt.')
            open_btn = msg.addButton('Ordner öffnen', QtWidgets.QMessageBox.ActionRole)
        else:
            msg.setText('Klasse abgeschlossen')
            open_btn = None
        msg.addButton('OK', QtWidgets.QMessageBox.AcceptRole)
        msg.exec()
        if open_btn and msg.clickedButton() == open_btn:
            QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(str(out_dir)))
        self._update_buttons()

    def add_person(self):
        dlg = QtWidgets.QDialog(self)
        dlg.setWindowTitle('Neue Person')
        form = QtWidgets.QFormLayout(dlg)
        first = QtWidgets.QLineEdit()
        last = QtWidgets.QLineEdit()
        form.addRow('Vorname', first)
        form.addRow('Nachname', last)
        buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        form.addRow(buttons)
        buttons.accepted.connect(dlg.accept)
        buttons.rejected.connect(dlg.reject)
        if dlg.exec() == QtWidgets.QDialog.Accepted:
            vor = first.text().strip()
            nach = last.text().strip()
            if vor and nach:
                learner = Learner(self.cmb_class.currentText(), nach, vor, '', True)
                self.learners.insert(self.current, learner)
                self.show_next()
                self._update_buttons()

    def _show_review(self, path: Path) -> bool:
        dlg = QtWidgets.QDialog(self)
        dlg.setWindowTitle('Aufnahme ansehen')
        vbox = QtWidgets.QVBoxLayout(dlg)
        lbl = QtWidgets.QLabel()
        pix = QtGui.QPixmap(str(path))
        lbl.setPixmap(pix.scaled(self.preview.size(), QtCore.Qt.KeepAspectRatio))
        vbox.addWidget(lbl)
        h = QtWidgets.QHBoxLayout()
        retry = QtWidgets.QPushButton('Erneut fotografieren')
        ok_btn = QtWidgets.QPushButton('OK')
        h.addWidget(retry)
        h.addWidget(ok_btn)
        vbox.addLayout(h)
        result = {'ok': True}
        retry.clicked.connect(lambda: (result.update(ok=False), dlg.accept()))
        ok_btn.clicked.connect(dlg.accept)
        dlg.exec()
        return result['ok']

    def switch_camera(self):
        if hasattr(self.camera, 'switch_camera'):
            self.current_cam_id = getattr(self, 'current_cam_id', 0) + 1
            try:
                self.camera.switch_camera(self.current_cam_id)
                self.preview.set_camera(self.camera)
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, 'Kamera', str(e))
                self.current_cam_id = 0
                try:
                    self.camera.switch_camera(self.current_cam_id)
                    self.preview.set_camera(self.camera)
                except Exception:
                    pass

    def closeEvent(self, event):
        self.camera.stop_liveview()
        super().closeEvent(event)

    def open_settings(self):
        dlg = SettingsDialog(self.settings, self)
        before_backend = self.settings.kamera.get('backend')
        before_overlay = self.settings.overlay.get('image')
        if dlg.exec() == QtWidgets.QDialog.Accepted:
            if self.settings.kamera.get('backend') != before_backend:
                self.camera.stop_liveview()
                self.camera = self._init_camera()
                if hasattr(self.camera, 'start_liveview'):
                    self.camera.start_liveview()
                self.preview.set_camera(self.camera)
            if self.settings.overlay.get('image') != before_overlay:
                self.preview.set_overlay_image(self.settings.overlay.get('image'))
        self._update_buttons()

    def _update_buttons(self):
        ready = bool(self.reader) and bool(self.cmb_class.currentText())
        more = ready and self.current < len(self.learners)
        self.btn_capture.setEnabled(more)
        self.btn_skip.setEnabled(more)
        self.btn_add_person.setEnabled(ready)
        self.btn_finish.setEnabled(ready)
