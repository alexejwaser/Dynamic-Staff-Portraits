# app/core/imaging/processor.py
from pathlib import Path
from PIL import Image
from typing import Tuple, Union


def _parse_ratio(val: Union[Tuple[int, int], str, None]) -> Tuple[int, int] | None:
    """Return a tuple ratio from a ``"w:h"`` string or tuple."""
    if val is None:
        return None
    if isinstance(val, tuple) and len(val) == 2:
        try:
            return int(val[0]), int(val[1])
        except (TypeError, ValueError):
            return None
    if isinstance(val, str):
        if ':' in val:
            a, b = val.split(':', 1)
            if a.isdigit() and b.isdigit():
                return int(a), int(b)
    return None


def crop_center(img: Image.Image, aspect: Tuple[int, int]) -> Image.Image:
    w, h = img.size
    target_w = w
    target_h = int(w * aspect[1] / aspect[0])
    if target_h > h:
        target_h = h
        target_w = int(h * aspect[0] / aspect[1])
    left = (w - target_w) // 2
    top = (h - target_h) // 2
    right = left + target_w
    bottom = top + target_h
    return img.crop((left, top, right, bottom))


def process_image(
    src: Path,
    dest: Path,
    width: int,
    height: int,
    quality: int,
    aspect: Union[Tuple[int, int], str, None] = None,
) -> None:
    aspect_tuple = _parse_ratio(aspect)
    with Image.open(src) as im:
        if aspect_tuple:
            im = crop_center(im, aspect_tuple)
        im = im.resize((width, height), Image.LANCZOS)
        dest_temp = dest.with_suffix('.tmp')
        im.save(dest_temp, 'JPEG', quality=quality)
        dest_temp.replace(dest)
