# app/ui/main_window.py
from PySide6 import QtWidgets, QtGui, QtCore
from pathlib import Path

from ..core.config.settings import Settings
from ..core.controller import MainController
from .settings_dialog import SettingsDialog
from .class_search_dialog import ClassSearchDialog
from .widgets import ControlPanel, PreviewPane, StatusLabels

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, settings: Settings, controller: MainController | None = None):
        super().__init__()
        self.settings = settings
        self.controller = controller or MainController(settings)
        self.camera = self.controller.camera
        self._setup_ui()
        if hasattr(self.camera, "start_liveview"):
            self.camera.start_liveview()

    def _setup_ui(self):
        self.setWindowTitle('LegicCard-Creator')
        self.setFixedSize(1000, 700)
        central = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(central)
        layout.setContentsMargins(20, 20, 20, 20)
        self.setCentralWidget(central)

        # left controls
        self.controls = ControlPanel(self)
        self.controls.cmb_location.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
        self.controls.cmb_class.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
        self.controls.cmb_class.setMaxVisibleItems(25)
        search_icon = self.style().standardIcon(QtWidgets.QStyle.SP_FileDialogContentsView)
        self.controls.btn_search_class.setIcon(search_icon)
        self.controls.btn_search_class.setToolTip('Klasse suchen')
        icon = self.style().standardIcon(QtWidgets.QStyle.SP_FileDialogDetailedView)
        self.controls.btn_settings.setIcon(icon)
        self.controls.btn_settings.setToolTip('Einstellungen')
        layout.addWidget(self.controls)

        # right preview
        fps = self.settings.kamera.get('liveviewFpsZiel', 20)
        self.preview_pane = PreviewPane(self.camera, fps, self.settings.overlay.get('image'), self)
        self.status_labels = StatusLabels(self)
        right_layout = QtWidgets.QVBoxLayout()
        right_layout.setSpacing(10)
        right_layout.addWidget(self.status_labels)
        right_layout.addWidget(self.preview_pane)
        layout.addLayout(right_layout)

        self.setStyleSheet(
            "* {font-family: 'Segoe UI';} QPushButton {padding:6px 12px;}\nQLabel{font-size:14px;}"
        )

        self.controls.btn_excel.clicked.connect(self.load_excel)
        self.controls.cmb_location.currentTextChanged.connect(self.update_classes)
        self.controls.cmb_class.currentTextChanged.connect(self.load_learners)
        self.controls.btn_capture.clicked.connect(self.capture_photo)
        self.controls.btn_skip.clicked.connect(self.skip_learner)
        self.controls.btn_add_person.clicked.connect(self.add_person)
        self.controls.btn_finish.clicked.connect(self.finish_class)
        self.preview_pane.btn_switch_camera.clicked.connect(self.switch_camera)
        self.controls.btn_settings.clicked.connect(self.open_settings)
        self.controls.btn_search_class.clicked.connect(self.search_class)

        self._update_buttons()

        # Keyboard shortcuts
        QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Space), self, self.capture_photo)
        QtGui.QShortcut(QtGui.QKeySequence('S'), self, self.skip_learner)
        QtGui.QShortcut(QtGui.QKeySequence('F'), self, self.finish_class)
        QtGui.QShortcut(QtGui.QKeySequence('A'), self, self.add_person)
        QtGui.QShortcut(QtGui.QKeySequence('C'), self, self.switch_camera)

    def load_excel(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Excel auswählen', filter='Excel (*.xlsx)')
        if not path:
            return
        try:
            locations = self.controller.load_excel(Path(path))
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, 'Excel', str(e))
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
        dlg = ClassSearchDialog(self.controller.current_classes, self)
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
            self.status_labels.set_current('Klasse abgeschlossen')
            self.status_labels.set_upcoming('')
            self._update_buttons()
            return
        self.status_labels.set_current(
            f"{learner.vorname} {learner.nachname} ({self.controller.current + 1}/{len(self.controller.learners)})"
        )
        next_l = self.controller.next_learner()
        if next_l:
            self.status_labels.set_upcoming(f"{next_l.vorname} {next_l.nachname}")
        else:
            self.status_labels.set_upcoming('')
        self._update_buttons()

    def capture_photo(self):
        if self.controller.current >= len(self.controller.learners):
            return
        if self.controller.excel_running():
            QtWidgets.QMessageBox.warning(
                self,
                'Excel geöffnet',
                'Schliesse Excel um die App zu benutzen!'
            )
            return
        learner = self.controller.current_learner()
        location = self.controls.cmb_location.currentText()
        try:
            raw_path = self.controller.capture(learner, location)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, 'Aufnahme fehlgeschlagen', str(e))
            return
        if self._show_review(raw_path):
            try:
                self.controller.mark_photographed(learner, location)
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, 'Excel', str(e))
            self.controller.advance()
        else:
            raw_path.unlink(missing_ok=True)
        self.show_next()
        self._update_buttons()

    def skip_learner(self):
        if self.controller.current >= len(self.controller.learners):
            return
        if self.controller.excel_running():
            QtWidgets.QMessageBox.warning(
                self,
                'Excel geöffnet',
                'Schliesse Excel um die App zu benutzen!'
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
        learner = self.controller.current_learner()
        location = self.controls.cmb_location.currentText()
        try:
            self.controller.skip(learner, location, reason)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, 'Excel', str(e))
        self.controller.advance()
        self.show_next()
        self._update_buttons()

    def finish_class(self):
        location = self.controls.cmb_location.currentText()
        klasse = self.controls.cmb_class.currentText()
        zip_paths, out_dir = self.controller.finish(location, klasse)

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
                self.controller.add_learner(self.controls.cmb_class.currentText(), vor, nach)
                self.show_next()
                self._update_buttons()

    def _show_review(self, path: Path) -> bool:
        dlg = QtWidgets.QDialog(self)
        dlg.setWindowTitle('Aufnahme ansehen')
        vbox = QtWidgets.QVBoxLayout(dlg)
        lbl = QtWidgets.QLabel()
        pix = QtGui.QPixmap(str(path))
        lbl.setPixmap(pix.scaled(self.preview_pane.preview.size(), QtCore.Qt.KeepAspectRatio))
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
                self.preview_pane.set_camera(self.controller.camera)
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, 'Kamera', str(e))

    def closeEvent(self, event):
        self.controller.camera.stop_liveview()
        super().closeEvent(event)

    def open_settings(self):
        dlg = SettingsDialog(self.settings, self)
        before_backend = self.settings.kamera.get('backend')
        before_overlay = self.settings.overlay.get('image')
        if dlg.exec() == QtWidgets.QDialog.Accepted:
            if self.settings.kamera.get('backend') != before_backend:
                self.camera = self.controller.restart_camera()
                self.preview_pane.set_camera(self.camera)
            if self.settings.overlay.get('image') != before_overlay:
                self.preview_pane.set_overlay_image(self.settings.overlay.get('image'))
        self._update_buttons()

    def _update_buttons(self):
        ready = bool(self.controller.reader) and bool(self.controls.cmb_class.currentText())
        more = ready and self.controller.current < len(self.controller.learners)
        self.controls.btn_capture.setEnabled(more)
        self.controls.btn_skip.setEnabled(more)
        self.controls.btn_add_person.setEnabled(ready)
        self.controls.btn_finish.setEnabled(ready)
        self.controls.btn_search_class.setEnabled(bool(getattr(self.controller, 'current_classes', [])))
