# app/core/excel/reader.py
from dataclasses import dataclass
from typing import List
from pathlib import Path
import openpyxl
from .missed_writer import MissedEntry

@dataclass
class Learner:
    klasse: str
    nachname: str
    vorname: str
    schueler_id: str = ''
    is_new: bool = False

class ExcelReader:
    def __init__(self, path: Path, mapping: dict):
        self.path = path
        self.mapping = mapping
        self.wb = openpyxl.load_workbook(path)

    def locations(self) -> List[str]:
        return self.wb.sheetnames

    def classes_for_location(self, location: str) -> List[str]:
        sheet = self.wb[location]
        col = self.mapping['klasse']
        values = {str(cell.value) for cell in sheet[col][1:] if cell.value}
        return sorted(values)

    def learners(self, location: str, class_name: str) -> List[Learner]:
        sheet = self.wb[location]
        m = self.mapping
        learners = []
        for row in sheet.iter_rows(min_row=2):
            if str(row[openpyxl.utils.column_index_from_string(m['klasse'])-1].value) == class_name:
                nachname = row[openpyxl.utils.column_index_from_string(m['nachname'])-1].value
                vorname = row[openpyxl.utils.column_index_from_string(m['vorname'])-1].value
                sid = row[openpyxl.utils.column_index_from_string(m['schuelerId'])-1].value
                if nachname and vorname and sid:
                    learners.append(Learner(str(class_name), str(nachname), str(vorname), str(sid)))
        learners.sort(key=lambda l: (l.nachname, l.vorname))
        return learners
