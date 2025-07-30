# app/core/config/settings.py
from dataclasses import dataclass
from pathlib import Path
import json


def _parse_ratio(value):
    if isinstance(value, str) and ':' in value:
        a, b = value.split(':', 1)
        if a.isdigit() and b.isdigit():
            return int(a), int(b)
    if isinstance(value, (list, tuple)) and len(value) == 2:
        return int(value[0]), int(value[1])
    return (3, 4)

DEFAULTS = {
    'ausgabeBasisPfad': 'output',
    'missedPath': 'Verpasste_Termine.xlsx',
    'bild': {'breite': 1200, 'hoehe': 1600, 'qualitaet': 90, 'seitenverhaeltnis': '3:4'},
    'overlay': {
        'drittellinien': True,
        'horizonte': False,
        'deckkraft': 0.3,
        'image': ''
    },
    'kamera': {
        'backend': 'opencv',
        'liveviewFpsZiel': 20,
        'format': 'JPEG',
        'timeoutMs': 5000,
    },
    'zip': {'maxAnzahl': None, 'maxGroesseMB': None},
    'copyright': {'artist': '', 'copyright': ''},
    'excelMapping': {'klasse': 'A', 'nachname': 'B', 'vorname': 'C', 'schuelerId': 'D'},
}

CONFIG_PATH = Path('settings.json')

@dataclass
class Settings:
    ausgabeBasisPfad: Path
    missedPath: Path
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
        data['missedPath'] = Path(data.get('missedPath', 'Verpasste_Termine.xlsx'))
        data['bild']['seitenverhaeltnis'] = _parse_ratio(data['bild'].get('seitenverhaeltnis', '3:4'))
        if data.get('overlay') and 'image' in data['overlay']:
            img = data['overlay']['image']
            data['overlay']['image'] = str(img) if img else ''
        else:
            data.setdefault('overlay', {}).setdefault('image', '')
        return Settings(**data)

    def save(self, path: Path = CONFIG_PATH) -> None:
        data = self.__dict__.copy()
        data['ausgabeBasisPfad'] = str(data['ausgabeBasisPfad'])
        data['missedPath'] = str(data['missedPath'])
        ratio = data['bild'].get('seitenverhaeltnis', (3, 4))
        if isinstance(ratio, tuple):
            data['bild']['seitenverhaeltnis'] = f"{ratio[0]}:{ratio[1]}"
        data['overlay']['image'] = data['overlay'].get('image', '')
        path.write_text(json.dumps(data, indent=2), encoding='utf-8')
