# app/ui/main_window.py
from PySide6 import QtWidgets, QtGui, QtCore
from pathlib import Path
from ..core.config.settings import Settings
from ..core.camera.simulator import SimulatorCamera
from ..core.imaging.processor import process_image
from ..core.util.paths import class_output_dir
from ..core.excel.reader import ExcelReader, Learner
from ..core.excel.missed_writer import MissedWriter, MissedEntry
from datetime import datetime

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, settings: Settings):
        super().__init__()
        self.settings = settings
        self.camera = SimulatorCamera()
        self.reader = None
        self.learners = []
        self.current = 0
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle('Porträt-Fotografie')
        central = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(central)
        self.setCentralWidget(central)

        # left controls
        control = QtWidgets.QVBoxLayout()
        self.btn_excel = QtWidgets.QPushButton('Excel verbinden...')
        self.cmb_location = QtWidgets.QComboBox()
        self.cmb_class = QtWidgets.QComboBox()
        self.label_next = QtWidgets.QLabel('')
        self.btn_capture = QtWidgets.QPushButton('Foto aufnehmen')
        self.btn_skip = QtWidgets.QPushButton('Überspringen')
        self.btn_finish = QtWidgets.QPushButton('Fertig')
        for w in [self.btn_excel, self.cmb_location, self.cmb_class, self.label_next,
                  self.btn_capture, self.btn_skip, self.btn_finish]:
            control.addWidget(w)
        control.addStretch()
        layout.addLayout(control)

        # right preview
        self.preview = QtWidgets.QLabel('LiveView')
        self.preview.setFixedSize(640, 480)
        layout.addWidget(self.preview)

        self.btn_excel.clicked.connect(self.load_excel)
        self.cmb_location.currentTextChanged.connect(self.update_classes)
        self.cmb_class.currentTextChanged.connect(self.load_learners)
        self.btn_capture.clicked.connect(self.capture_photo)
        self.btn_skip.clicked.connect(self.skip_learner)
        self.btn_finish.clicked.connect(self.finish_class)

    def load_excel(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Excel auswählen', filter='Excel (*.xlsx)')
        if not path:
            return
        self.reader = ExcelReader(Path(path), self.settings.excelMapping)
        self.cmb_location.clear()
        self.cmb_location.addItems(self.reader.locations())

    def update_classes(self, location: str):
        if not self.reader or not location:
            return
        self.cmb_class.clear()
        self.cmb_class.addItems(self.reader.classes_for_location(location))

    def load_learners(self, class_name: str):
        location = self.cmb_location.currentText()
        if not self.reader or not class_name:
            return
        self.learners = self.reader.learners(location, class_name)
        self.current = 0
        self.show_next()

    def show_next(self):
        if self.current >= len(self.learners):
            self.label_next.setText('Klasse abgeschlossen')
            return
        l = self.learners[self.current]
        self.label_next.setText(f"{l.vorname} {l.nachname} ({l.schueler_id})")

    def capture_photo(self):
        if self.current >= len(self.learners):
            return
        learner = self.learners[self.current]
        out_dir = class_output_dir(self.settings.ausgabeBasisPfad, self.cmb_location.currentText(), learner.klasse)
        raw_path = out_dir / f"{learner.schueler_id}.jpg"
        self.camera.capture(raw_path)
        process_image(raw_path, raw_path, self.settings.bild['breite'], self.settings.bild['hoehe'], self.settings.bild['qualitaet'])
        self.current += 1
        self.show_next()

    def skip_learner(self):
        if self.current >= len(self.learners):
            return
        learner = self.learners[self.current]
        missed = MissedWriter(Path('Verpasste_Termine.xlsx'))
        entry = MissedEntry(self.cmb_location.currentText(), learner.klasse, learner.nachname, learner.vorname, learner.schueler_id, datetime.now().isoformat())
        missed.append(entry)
        self.current += 1
        self.show_next()

    def finish_class(self):
        QtWidgets.QMessageBox.information(self, 'Info', 'Klasse abgeschlossen')
