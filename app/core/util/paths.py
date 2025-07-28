# app/core/util/paths.py
from pathlib import Path


def sanitize_name(name: str) -> str:
    return ''.join(c for c in name if c.isalnum() or c in ('-', '_')).strip()

def class_output_dir(base: Path, location: str, class_name: str) -> Path:
    safe_loc = sanitize_name(location)
    safe_class = sanitize_name(class_name)
    path = base / safe_loc / safe_class
    path.mkdir(parents=True, exist_ok=True)
    return path
