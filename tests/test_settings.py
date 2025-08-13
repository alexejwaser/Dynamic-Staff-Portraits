"""Tests for configuration settings management."""

from pathlib import Path
import json
import pytest
from pydantic import ValidationError

from app.core.config.settings import (
    Settings,
    DEFAULTS,
    BildSettings,
    OverlaySettings,
    KameraSettings,
    ZipSettings,
    CopyrightSettings,
    ExcelMapping,
)


def test_load_creates_file_with_defaults(tmp_path):
    cfg = tmp_path / "settings.json"
    settings = Settings.load(cfg)
    assert cfg.exists()
    assert settings.bild.seitenverhaeltnis == (3, 4)
    assert settings.overlay.image is None


def test_save_and_load_roundtrip(tmp_path):
    cfg = tmp_path / "settings.json"
    s = Settings(
        ausgabeBasisPfad=tmp_path,
        missedPath=tmp_path / "missed.xlsx",
        bild=BildSettings(breite=800, hoehe=600, qualitaet=80, seitenverhaeltnis=(4, 3)),
        overlay=OverlaySettings(drittellinien=True, horizonte=False, deckkraft=0.3, image=None),
        kamera=KameraSettings(backend="opencv", liveviewFpsZiel=20, format="JPEG", timeoutMs=5000),
        zip=ZipSettings(maxAnzahl=None, maxGroesseMB=None),
        copyright=CopyrightSettings(artist="", copyright=""),
        excelMapping=ExcelMapping(**DEFAULTS["excelMapping"]),
    )
    s.save(cfg)
    loaded = Settings.load(cfg)
    assert loaded.bild.seitenverhaeltnis == (4, 3)
    assert loaded.ausgabeBasisPfad == tmp_path


def test_overlay_path_validation(tmp_path):
    cfg = tmp_path / "settings.json"
    data = DEFAULTS.copy()
    data["overlay"] = data["overlay"].copy()
    data["overlay"]["image"] = str(tmp_path / "missing.png")
    cfg.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValidationError):
        Settings.load(cfg)
