# tests/test_excel_reader.py
from pathlib import Path
from app.core.excel.reader import ExcelReader
import openpyxl

def create_sample(path: Path):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Standort1'
    ws['A1'] = 'Klasse'
    ws['B1'] = 'Nachname'
    ws['C1'] = 'Vorname'
    ws['D1'] = 'SchuelerID'
    ws.append(['INF', 'Meier', 'Hans', '001'])
    ws.append(['INF', 'Muster', 'Eva', '002'])
    wb.save(path)

def test_read(tmp_path):
    xl = tmp_path / 'test.xlsx'
    create_sample(xl)
    reader = ExcelReader(xl, {'klasse':'A', 'nachname':'B', 'vorname':'C', 'schuelerId':'D'})
    classes = reader.classes_for_location('Standort1')
    assert classes == ['INF']
    learners = reader.learners('Standort1', 'INF')
    assert len(learners) == 2
    assert learners[0].nachname == 'Meier'
