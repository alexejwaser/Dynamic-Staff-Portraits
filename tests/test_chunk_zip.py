# tests/test_chunk_zip.py
from pathlib import Path
from app.core.archiver.chunk_zip import chunk_by_count


def test_chunk(tmp_path):
    files = []
    for i in range(5):
        p = tmp_path / f"f{i}.txt"
        p.write_text('x')
        files.append(p)
    out_base = tmp_path / 'archive.zip'
    zips = chunk_by_count(files, out_base, 2)
    assert len(zips) == 3
    for zp in zips:
        assert zp.exists()


def test_single_chunk(tmp_path):
    files = []
    for i in range(2):
        p = tmp_path / f"f{i}.txt"
        p.write_text('x')
        files.append(p)
    out_base = tmp_path / 'archive.zip'
    zips = chunk_by_count(files, out_base, 10)
    assert zips == [out_base]
    assert out_base.exists()
