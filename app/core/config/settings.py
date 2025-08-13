# app/core/config/settings.py
"""Configuration management using Pydantic models."""

from pathlib import Path
import json
import os
from typing import Tuple, Optional

from pydantic import BaseModel, Field, field_validator, ConfigDict


DEFAULTS = {
    'ausgabeBasisPfad': 'output',
    'missedPath': 'Verpasste_Termine.xlsx',
    'bild': {
        'breite': 1200,
        'hoehe': 1600,
        'qualitaet': 90,
        'seitenverhaeltnis': '3:4',
    },
    'overlay': {
        'drittellinien': True,
        'horizonte': False,
        'deckkraft': 0.3,
        'image': '',
    },
    'kamera': {
        'backend': 'opencv',
        'liveviewFpsZiel': 20,
        'format': 'JPEG',
        'timeoutMs': 5000,
    },
    'zip': {'maxAnzahl': None, 'maxGroesseMB': None},
    'copyright': {'artist': '', 'copyright': ''},
    'excelMapping': {
        'klasse': 'A',
        'nachname': 'B',
        'vorname': 'C',
        'schuelerId': 'D',
        'fotografiert': 'E',
        'aufnahmedatum': 'F',
        'grund': 'G',
    },
}

CONFIG_DIR = Path(os.getenv("APPDATA", Path.home())) / "LegicCardCreator"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_PATH = CONFIG_DIR / "settings.json"


class BildSettings(BaseModel):
    breite: int
    hoehe: int
    qualitaet: int
    seitenverhaeltnis: Tuple[int, int] = (3, 4)

    @field_validator('seitenverhaeltnis', mode='before')
    @classmethod
    def parse_ratio(cls, v):
        if isinstance(v, str) and ':' in v:
            a, b = v.split(':', 1)
            if a.isdigit() and b.isdigit():
                return int(a), int(b)
        if isinstance(v, (list, tuple)) and len(v) == 2:
            return int(v[0]), int(v[1])
        raise ValueError('Invalid ratio format')


class OverlaySettings(BaseModel):
    drittellinien: bool = True
    horizonte: bool = False
    deckkraft: float = 0.3
    image: Optional[Path] = Field(default=None)

    @field_validator('image', mode='before')
    @classmethod
    def check_image(cls, v):
        if not v:
            return None
        p = Path(v)
        if not p.exists():
            raise ValueError(f'Overlay image not found: {v}')
        return p


class KameraSettings(BaseModel):
    backend: str = 'opencv'
    liveviewFpsZiel: int = 20
    format: str = 'JPEG'
    timeoutMs: int = 5000


class ZipSettings(BaseModel):
    maxAnzahl: Optional[int] = None
    maxGroesseMB: Optional[int] = None


class CopyrightSettings(BaseModel):
    artist: str = ''
    copyright: str = ''


class ExcelMapping(BaseModel):
    klasse: str = 'A'
    nachname: str = 'B'
    vorname: str = 'C'
    schuelerId: str = 'D'
    fotografiert: str = 'E'
    aufnahmedatum: str = 'F'
    grund: str = 'G'


class Settings(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    ausgabeBasisPfad: Path = Field(default_factory=lambda: Path('output'))
    missedPath: Path = Field(default_factory=lambda: Path('Verpasste_Termine.xlsx'))
    bild: BildSettings = Field(default_factory=BildSettings)
    overlay: OverlaySettings = Field(default_factory=OverlaySettings)
    kamera: KameraSettings = Field(default_factory=KameraSettings)
    zip: ZipSettings = Field(default_factory=ZipSettings)
    copyright: CopyrightSettings = Field(default_factory=CopyrightSettings)
    excelMapping: ExcelMapping = Field(default_factory=ExcelMapping)

    @classmethod
    def load(cls, path: Path = CONFIG_PATH) -> 'Settings':
        if path.exists():
            data = json.loads(path.read_text(encoding='utf-8'))
        else:
            data = DEFAULTS
            path.write_text(json.dumps(data, indent=2), encoding='utf-8')
        return cls.model_validate(data)

    def save(self, path: Path = CONFIG_PATH) -> None:
        data = self.model_dump()
        data['ausgabeBasisPfad'] = str(data['ausgabeBasisPfad'])
        data['missedPath'] = str(data['missedPath'])
        ratio = data['bild']['seitenverhaeltnis']
        data['bild']['seitenverhaeltnis'] = f"{ratio[0]}:{ratio[1]}"
        img = data['overlay'].get('image')
        data['overlay']['image'] = str(img) if img else ''
        path.write_text(json.dumps(data, indent=2), encoding='utf-8')
