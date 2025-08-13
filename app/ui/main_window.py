"""Main application window."""

from __future__ import annotations

from PySide6 import QtWidgets, QtGui, QtCore, QtConcurrent
from pathlib import Path
from datetime import datetime
import logging
import psutil

from ..core.config.settings import Settings
from ..core.controller import MainController
from ..core.camera import SimulatorCamera, GPhoto2Camera, OpenCVCamera
from ..core.excel.reader import ExcelReader, Learner
from ..core.excel.missed_writer import MissedWriter, MissedEntry
from ..core.imaging.processor import process_image
from ..core.util.paths import (
    class_output_dir,
    new_learner_dir,
    unique_file_path,
)
from .settings_dialog import SettingsDialog
from .class_search_dialog import ClassSearchDialog
from .widgets import ControlPanel


class MainWindow(QtWidgets.QMainWindow):
    """Main GUI window for the application."""

    def __init__(
        self,
        settings: Settings,
        controller: MainController | None = None,
        logger: logging.Logger | None = None,
    ):
        super().__init__()
        self.logger = logger or logging.getLogger(type(self).__name__)
        self.settings = settings
        self.controller = controller or MainController(settings)
        self.camera = self._init_camera()
        self._reader = None
        self.busy = False
        self._setup_ui()
        if hasattr(self.camera, "start_liveview"):
            self.camera.start_liveview()

    @property
    def reader(self):
        return self._reader

    @reader.setter
    def reader(self, value):
        self._reader = value
        if self.controller is not None:
            self.controller.reader = value

    def _init_camera(self):
        backend = self.settings.kamera.backend
        cam = None
        if backend == 'gphoto2' and QtCore.QStandardPaths.findExecutable('gphoto2'):
            cam = GPhoto2Camera()
        elif backend == 'simulator':
            cam = SimulatorCamera()
        else:
            try:
                # In Webcam-Modus standardmaessig die zweite Kamera verwenden
                cam = OpenCVCamera(1)
                self.current_cam_id = 1
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
        self.controls = ControlPanel(self)
        self.cmb_location = self.controls.cmb_location
        self.cmb_class = self.controls.cmb_class
        self.btn_search_class = self.controls.btn_search_class
        self.btn_excel = self.controls.btn_excel
        self.btn_capture = self.controls.btn_capture
        self.btn_skip = self.controls.btn_skip
        self.btn_add_person = self.controls.btn_add_person
        self.btn_finish = self.controls.btn_finish
        self.btn_settings = self.controls.btn_settings
        self.cmb_location.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
        self.cmb_class.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
        self.cmb_class.setMaxVisibleItems(25)
        search_icon = self.style().standardIcon(QtWidgets.QStyle.SP_FileDialogContentsView)
        self.btn_search_class.setIcon(search_icon)
        self.btn_search_class.setToolTip('Klasse suchen')
        icon = self.style().standardIcon(QtWidgets.QStyle.SP_FileDialogDetailedView)
        self.btn_settings.setIcon(icon)
        self.btn_settings.setToolTip('Einstellungen')
        layout.addWidget(self.controls)

        # right preview
        from .widgets.live_view_widget import LiveViewWidget
        fps = self.settings.kamera.liveviewFpsZiel
        self.preview = LiveViewWidget(self.camera, fps)
        self.preview.set_overlay_image(self.settings.overlay.image)
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
        self.btn_search_class.clicked.connect(self.search_class)

        self._update_buttons()

        # Keyboard shortcuts
        QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Space), self, self.capture_photo)
        QtGui.QShortcut(QtGui.QKeySequence('S'), self, self.skip_learner)
        QtGui.QShortcut(QtGui.QKeySequence('F'), self, self.finish_class)
        QtGui.QShortcut(QtGui.QKeySequence('A'), self, self.add_person)
        QtGui.QShortcut(QtGui.QKeySequence('C'), self, self.switch_camera)

    # ------------------------------------------------------------------
    def _notify(
        self,
        title: str,
        message: str,
        level: str = "info",
        show: bool = True,
    ) -> None:
        """Log *message* with *level* and optionally show a QMessageBox."""

        log_fn = getattr(self.logger, level, self.logger.info)
        log_fn(f"{title}: {message}")
        if not show:
            return
        mapping = {
            "error": QtWidgets.QMessageBox.critical,
            "warning": QtWidgets.QMessageBox.warning,
            "info": QtWidgets.QMessageBox.information,
        }
        msg_fn = mapping.get(level, QtWidgets.QMessageBox.information)
        msg_fn(self, title, message)

    def load_excel(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Excel auswählen', filter='Excel (*.xlsx)')
        if not path:
            return
        try:
            self.reader = ExcelReader(Path(path), self.settings.excelMapping.model_dump())
            locations = self.reader.locations()
        except Exception as e:
            self._notify('Excel', str(e), level='error')
            return
        self.controls.cmb_location.clear()
        self.controls.cmb_location.addItems(locations)
        self._update_buttons()

    def update_classes(self, location: str):
        classes = self.controller.classes_for_location(location)
        self.controls.cmb_class.clear()
        self.controls.cmb_class.addItems(classes)
        self._update_buttons()

    def search_class(self):
        if not getattr(self.controller, 'current_classes', None):
            return
        dlg = ClassSearchDialog(
            self.controller.current_classes, self, logger=self.logger.getChild('ClassSearchDialog')
        )
        if dlg.exec() == QtWidgets.QDialog.Accepted:
            selected = dlg.selected_class()
            if selected:
                idx = self.controls.cmb_class.findText(selected, QtCore.Qt.MatchExactly)
                if idx >= 0:
                    self.controls.cmb_class.setCurrentIndex(idx)

    def load_learners(self, class_name: str):
        location = self.controls.cmb_location.currentText()
        self.controller.learners_for_class(location, class_name)
        self.show_next()
        self._update_buttons()

    def show_next(self):
        learner = self.controller.current_learner()
        if learner is None:
            self.label_current.setText('Klasse abgeschlossen')
            self.label_upcoming.setText('')
            self._update_buttons()
            return
        self.label_current.setText(
            f"{learner.vorname} {learner.nachname} ({self.controller.current + 1}/{len(self.controller.learners)})"
        )
        next_l = self.controller.next_learner()
        if next_l:
            self.label_upcoming.setText(f"{next_l.vorname} {next_l.nachname}")
        else:
            self.label_upcoming.setText('')
        self._update_buttons()

    def _excel_running(self) -> bool:
        for proc in psutil.process_iter(['name']):
            try:
                name = proc.info['name'] or ''
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
            if 'excel' in name.lower():
                return True
        return False

    def _set_busy(self, busy: bool):
        self.busy = busy
        for btn in [self.btn_excel, self.btn_settings, self.btn_switch_camera]:
            btn.setEnabled(not busy)
        self._update_buttons()

    def capture_photo(self):
        if self.controller.current >= len(self.controller.learners):
            return
        if self.controller.excel_running():
            self._notify(
                'Excel geöffnet',
                'Schliesse Excel um die App zu benutzen!',
                level='warning',
            )
            return
        self._set_busy(True)
        learner = self.controller.learners[self.controller.current]
        location = self.cmb_location.currentText()
        if learner.is_new:
            out_dir = new_learner_dir(self.settings.ausgabeBasisPfad, location, learner.klasse)
            raw_path = unique_file_path(out_dir, f"{learner.vorname}_{learner.nachname}.jpg")
        else:
            out_dir = class_output_dir(self.settings.ausgabeBasisPfad, location, learner.klasse)
            raw_path = unique_file_path(out_dir, f"{learner.schueler_id}.jpg")

        def task():
            self.camera.capture(raw_path)
            aspect = getattr(self.settings.bild, 'seitenverhaeltnis', (3, 4))
            process_image(
                raw_path,
                raw_path,
                self.settings.bild.breite,
                self.settings.bild.hoehe,
                self.settings.bild.qualitaet,
                aspect,
            )

        if hasattr(QtConcurrent, 'run'):
            future = QtConcurrent.run(task)
            watcher = QtCore.QFutureWatcher()
            watcher.setFuture(future)
            watcher.finished.connect(
                lambda: self._capture_finished(watcher, learner, location, raw_path)
            )
            self._capture_watcher = watcher
        else:
            task()
            self._capture_finished(None, learner, location, raw_path)

    def _capture_finished(self, watcher: QtCore.QFutureWatcher | None, learner: Learner, location: str, raw_path: Path):
        try:
            if watcher is not None:
                watcher.result()
        except Exception as e:
            self._notify('Aufnahme fehlgeschlagen', str(e), level='error')
            raw_path.unlink(missing_ok=True)
            self._set_busy(False)
            return
        if self._show_review(raw_path):
            if not learner.is_new:
                date_str = datetime.now().strftime('%d.%m.%Y')

                def excel_task():
                    self.reader.mark_photographed(location, learner.row, True, date_str)

                if hasattr(QtConcurrent, 'run'):
                    future = QtConcurrent.run(excel_task)
                    watcher2 = QtCore.QFutureWatcher()
                    watcher2.setFuture(future)
                    watcher2.finished.connect(lambda: self._mark_finished(watcher2))
                    self._excel_watcher = watcher2
                else:
                    excel_task()
                    self._mark_finished(None)
            else:
                self.controller.advance()
                self.show_next()
                self._set_busy(False)
        else:
            raw_path.unlink(missing_ok=True)
            self._set_busy(False)

    def _mark_finished(self, watcher: QtCore.QFutureWatcher | None):
        try:
            if watcher is not None:
                watcher.result()
        except Exception as e:
            self._notify('Excel', str(e), level='warning')
        self.controller.advance()
        self.show_next()
        self._set_busy(False)

    def skip_learner(self):
        if self.controller.current >= len(self.controller.learners):
            return
        if self.controller.excel_running():
            self._notify(
                'Excel geöffnet',
                'Schliesse Excel um die App zu benutzen!',
                level='warning',
            )
            return
        reasons = ['Krank', 'Verweigert', 'Anderer Grund...']
        reason, ok = QtWidgets.QInputDialog.getItem(
            self,
            'Grund',
            'Grund für das Überspringen wählen:',
            reasons,
            0,
            False,
        )
        if not ok:
            return
        if reason == 'Anderer Grund...':
            reason, ok = QtWidgets.QInputDialog.getText(
                self,
                'Grund',
                'Grund für das Überspringen eingeben:',
            )
            if not ok:
                return
        learner = self.controller.learners[self.controller.current]
        missed = MissedWriter(self.settings.missedPath)
        entry = MissedEntry(
            self.cmb_location.currentText(),
            learner.klasse,
            learner.nachname,
            learner.vorname,
            learner.schueler_id,
            datetime.now().isoformat(),
            reason,
        )
        self._set_busy(True)

        def task():
            errors = []
            try:
                missed.append(entry)
            except Exception as e:
                errors.append(str(e))
            if not learner.is_new:
                try:
                    self.reader.mark_photographed(
                        self.cmb_location.currentText(),
                        learner.row,
                        False,
                        reason=reason,
                    )
                except Exception as e:
                    errors.append(str(e))
            return errors

        if hasattr(QtConcurrent, 'run'):
            future = QtConcurrent.run(task)
            watcher = QtCore.QFutureWatcher()
            watcher.setFuture(future)
            watcher.finished.connect(lambda: self._skip_finished(watcher))
            self._skip_watcher = watcher
        else:
            errors = task()
            for err in errors:
                self._notify('Excel', err, level='warning')
            self.controller.advance()
            self.show_next()
            self._set_busy(False)

    def _skip_finished(self, watcher: QtCore.QFutureWatcher):
        errors = watcher.result()
        for err in errors:
            self._notify('Excel', err, level='warning')
        self.controller.advance()
        self.show_next()
        self._set_busy(False)

    def finish_class(self):
        location = self.controls.cmb_location.currentText()
        klasse = self.controls.cmb_class.currentText()
        zip_paths, out_dir = self.controller.finish(location, klasse)
        if zip_paths:
            text = f'ZIP-Archiv {zip_paths[0].name} wurde erstellt.'
        else:
            text = 'Klasse abgeschlossen'
        self.logger.info(text)

        msg = QtWidgets.QMessageBox(self)
        msg.setWindowTitle('Klasse abgeschlossen')
        msg.setText(text)
        open_btn = None
        if zip_paths:
            open_btn = msg.addButton('Ordner öffnen', QtWidgets.QMessageBox.ActionRole)
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
                self.controller.add_learner(self.controls.cmb_class.currentText(), vor, nach)
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
        retry = QtWidgets.QPushButton('Erneut fotografieren\n[Esc]')
        ok_btn = QtWidgets.QPushButton('OK\n[Leertaste]')
        h.addWidget(retry)
        h.addWidget(ok_btn)
        vbox.addLayout(h)
        result = {'ok': True}
        retry.clicked.connect(lambda: (result.update(ok=False), dlg.accept()))
        ok_btn.clicked.connect(dlg.accept)
        QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Space), dlg, ok_btn.click)
        QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Escape), dlg, retry.click)
        dlg.exec()
        return result['ok']

    def switch_camera(self):
        if hasattr(self.controller.camera, 'switch_camera'):
            try:
                self.controller.switch_camera()
                self.preview.set_camera(self.controller.camera)
            except Exception as e:
                self._notify('Kamera', str(e), level='warning')

    def closeEvent(self, event):
        self.controller.camera.stop_liveview()
        super().closeEvent(event)

    def open_settings(self):
        dlg = SettingsDialog(
            self.settings, self, logger=self.logger.getChild('SettingsDialog')
        )
        before_backend = self.settings.kamera.backend
        before_overlay = self.settings.overlay.image
        if dlg.exec() == QtWidgets.QDialog.Accepted:
            if self.settings.kamera.backend != before_backend:
                self.camera.stop_liveview()
                self.camera = self._init_camera()
                if hasattr(self.camera, 'start_liveview'):
                    self.camera.start_liveview()
                self.preview.set_camera(self.camera)
            if self.settings.overlay.image != before_overlay:
                self.preview.set_overlay_image(self.settings.overlay.image)
        self._update_buttons()

    def _update_buttons(self):
        ready = bool(self.reader) and bool(self.cmb_class.currentText())
        more = ready and self.controller.current < len(self.controller.learners)
        busy = getattr(self, 'busy', False)
        self.btn_capture.setEnabled(more and not busy)
        self.btn_skip.setEnabled(more and not busy)
        self.btn_add_person.setEnabled(ready and not busy)
        self.btn_finish.setEnabled(ready and not busy)
        self.btn_search_class.setEnabled(bool(getattr(self, 'current_classes', [])) and not busy)
