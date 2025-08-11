from pathlib import Path
import openpyxl
from app.core.excel.missed_writer import MissedWriter, MissedEntry


def test_missed_reason(tmp_path):
    file = tmp_path / 'miss.xlsx'
    writer = MissedWriter(file)
    entry = MissedEntry('Loc','Class','Nach','Vor','001','2024-01-01','Krank')
    writer.append(entry)
    wb = openpyxl.load_workbook(file)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    assert rows[1] == ('Loc','Class','Nach','Vor','001','2024-01-01','Krank')
