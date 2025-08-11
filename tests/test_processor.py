"""Tests for image processing helpers."""

from pathlib import Path
from PIL import Image

from app.core.imaging.processor import process_image, _parse_ratio


def test_process(tmp_path):
    src = tmp_path / 'src.jpg'
    img = Image.new('RGB', (400, 400), (255, 0, 0))
    img.save(src)
    dest = tmp_path / 'out.jpg'
    process_image(src, dest, 200, 200, 80, (1, 1))
    with Image.open(dest) as im:
        assert im.size == (200, 200)


def test_process_crop(tmp_path):
    src = tmp_path / 'src.jpg'
    img = Image.new('RGB', (400, 300), (255, 0, 0))
    img.save(src)
    dest = tmp_path / 'out.jpg'
    process_image(src, dest, 200, 200, 80, (3, 4))
    with Image.open(dest) as im:
        assert im.size == (200, 200)


def test_parse_ratio():
    """Ensure the internal ratio parser handles various inputs."""
    assert _parse_ratio("16:9") == (16, 9)
    assert _parse_ratio((4, 3)) == (4, 3)
    assert _parse_ratio("bad") is None
    assert _parse_ratio((1, 2, 3)) is None
    assert _parse_ratio(None) is None
