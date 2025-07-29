# app/core/config/settings.py
from dataclasses import dataclass, field
from pathlib import Path
import json

DEFAULTS = {
    'ausgabeBasisPfad': 'output',
    'bild': {'breite': 1200, 'hoehe': 1600, 'qualitaet': 90, 'seitenverhaeltnis': '3:4'},
    'overlay': {'drittellinien': True, 'horizonte': False, 'deckkraft': 0.3},
    'kamera': {'liveviewFpsZiel': 20, 'format': 'JPEG', 'timeoutMs': 5000},
    'zip': {'maxAnzahl': None, 'maxGroesseMB': None},
    'copyright': {'artist': '', 'copyright': ''},
    'excelMapping': {'klasse': 'A', 'nachname': 'B', 'vorname': 'C', 'schuelerId': 'D'},
}

CONFIG_PATH = Path('settings.json')

@dataclass
class Settings:
    ausgabeBasisPfad: Path
    bild: dict
    overlay: dict
    kamera: dict
    zip: dict
    copyright: dict
    excelMapping: dict

    @staticmethod
    def load(path: Path = CONFIG_PATH) -> 'Settings':
        if path.exists():
            data = json.loads(path.read_text(encoding='utf-8'))
        else:
            data = DEFAULTS
            path.write_text(json.dumps(data, indent=2), encoding='utf-8')
        data['ausgabeBasisPfad'] = Path(data['ausgabeBasisPfad'])
        return Settings(**data)

    def save(self, path: Path = CONFIG_PATH) -> None:
        data = self.__dict__.copy()
        data['ausgabeBasisPfad'] = str(data['ausgabeBasisPfad'])
        path.write_text(json.dumps(data, indent=2), encoding='utf-8')
