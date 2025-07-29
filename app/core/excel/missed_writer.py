# app/core/excel/missed_writer.py
from dataclasses import dataclass
from pathlib import Path
import openpyxl
from datetime import datetime

@dataclass
class MissedEntry:
    standort: str
    klasse: str
    nachname: str
    vorname: str
    schueler_id: str
    datum: str
    grund: str = ''

class MissedWriter:
    HEADER = ['Standort', 'Klasse', 'Nachname', 'Vorname', 'SchuelerID', 'Datum', 'Grund']

    def __init__(self, path: Path):
        self.path = path
        if path.exists():
            self.wb = openpyxl.load_workbook(path)
            self.ws = self.wb.active
        else:
            self.wb = openpyxl.Workbook()
            self.ws = self.wb.active
            self.ws.append(self.HEADER)
            self.wb.save(path)

    def append(self, entry: MissedEntry) -> None:
        self.ws.append([
            entry.standort,
            entry.klasse,
            entry.nachname,
            entry.vorname,
            entry.schueler_id,
            entry.datum,
            entry.grund,
        ])
        self.wb.save(self.path)
