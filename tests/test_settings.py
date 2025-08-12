"""Tests for configuration settings management."""

from pathlib import Path

from app.core.config.settings import Settings, DEFAULTS


def test_load_creates_file_with_defaults(tmp_path):
    cfg = tmp_path / "settings.json"
    settings = Settings.load(cfg)
    assert cfg.exists()
    assert settings.bild["seitenverhaeltnis"] == (3, 4)
    assert settings.overlay.get("image") == ""


def test_save_and_load_roundtrip(tmp_path):
    cfg = tmp_path / "settings.json"
    s = Settings(
        ausgabeBasisPfad=tmp_path,
        missedPath=tmp_path / "missed.xlsx",
        bild={"breite": 800, "hoehe": 600, "qualitaet": 80, "seitenverhaeltnis": (4, 3)},
        overlay={"drittellinien": True, "horizonte": False, "deckkraft": 0.3, "image": ""},
        kamera={"backend": "opencv", "liveviewFpsZiel": 20, "format": "JPEG", "timeoutMs": 5000},
        zip={"maxAnzahl": None, "maxGroesseMB": None},
        copyright={"artist": "", "copyright": ""},
        excelMapping=DEFAULTS["excelMapping"],
    )
    s.save(cfg)
    loaded = Settings.load(cfg)
    assert loaded.bild["seitenverhaeltnis"] == (4, 3)
    assert loaded.ausgabeBasisPfad == tmp_path
