# app/core/imaging/processor.py
from pathlib import Path
from PIL import Image
from typing import Tuple


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


def process_image(src: Path, dest: Path, width: int, height: int, quality: int, aspect: Tuple[int, int] = None) -> None:
    with Image.open(src) as im:
        if aspect:
            im = crop_center(im, aspect)
        im = im.resize((width, height), Image.LANCZOS)
        dest_temp = dest.with_suffix('.tmp')
        im.save(dest_temp, 'JPEG', quality=quality)
        dest_temp.replace(dest)
