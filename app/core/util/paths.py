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
