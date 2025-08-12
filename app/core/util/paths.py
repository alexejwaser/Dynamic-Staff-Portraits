# app/core/util/paths.py
from pathlib import Path
from typing import Union


def sanitize_name(name: str) -> str:
    return ''.join(c for c in name if c.isalnum() or c in ('-', '_')).strip()

def class_output_dir(base: Union[str, Path], location: str, class_name: str) -> Path:
    """Return the directory for a class, creating it if necessary."""
    base_path = Path(base)
    safe_loc = sanitize_name(location)
    safe_class = sanitize_name(class_name)
    path = base_path / safe_loc / safe_class
    path.mkdir(parents=True, exist_ok=True)
    return path


def new_learner_dir(base: Union[str, Path], location: str, class_name: str) -> Path:
    """Return folder for additional learners."""
    base_path = Path(base) / 'Neue Lernende'
    return class_output_dir(base_path, location, class_name)


def unique_file_path(directory: Union[str, Path], filename: str) -> Path:
    """Return a unique, sanitized file path inside *directory*.

    If *filename* already exists it will be suffixed with ``_1``, ``_2`` …
    """
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    stem = sanitize_name(Path(filename).stem)
    suffix = Path(filename).suffix
    candidate = directory / f"{stem}{suffix}"
    index = 1
    while candidate.exists():
        candidate = directory / f"{stem}_{index}{suffix}"
        index += 1
    return candidate
