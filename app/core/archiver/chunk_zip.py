# app/core/archiver/chunk_zip.py
from pathlib import Path
import zipfile
from typing import List


def chunk_by_count(files: List[Path], out_base: Path, max_count: int) -> List[Path]:
    zips = []
    part = 1
    for i in range(0, len(files), max_count):
        zip_path = out_base.with_name(f"{out_base.stem}_part{part:02d}.zip")
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for f in files[i:i+max_count]:
                zf.write(f, arcname=f.name)
        zips.append(zip_path)
        part += 1
    return zips
