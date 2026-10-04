"""Legacy-compatible behavior preserved for this callable."""
from __future__ import annotations

import functools
import io
from typing import BinaryIO, Literal, Tuple

from PIL import Image, ImageOps

__all__ = ["watermark_image"]

# Internal implementation note: legacy behavior is preserved during modernization.
# Internal implementation note: legacy behavior is preserved during modernization.
# Internal implementation note: legacy behavior is preserved during modernization.
@functools.lru_cache(maxsize=4)
def _load_mark(path: str) -> Image.Image:
    """Load watermark as RGBA (cached)."""
    return Image.open(path).convert("RGBA")


# Internal implementation note: legacy behavior is preserved during modernization.
def _scale_and_crop(
    mark: Image.Image,
    target_sz: Tuple[int, int],
    anchor: Literal["center", "top", "bottom", "left", "right"] = "center",
) -> Image.Image:
    """
    Resize *mark* so that it fully covers *target_sz* while keeping aspect
    ratio, then crop to exactly *target_sz* around the given *anchor*.

    anchor:
        Where to keep the *un-cropped* area when mark is bigger than target.
        Only `'center'`, `'top'`, `'bottom'`, `'left'`, `'right'` accepted.
    """
    tw, th = target_sz
    mw, mh = mark.size

    # ---- 1) scale so both dims >= target ----
    scale = max(tw / mw, th / mh)
    new_w, new_h = int(mw * scale + 0.5), int(mh * scale + 0.5)
    mark = mark.resize((new_w, new_h), Image.LANCZOS)

    # ---- 2) crop extra parts ----
    if anchor == "center":
        left   = (new_w - tw) // 2
        upper  = (new_h - th) // 2
    elif anchor == "top":
        left, upper = (new_w - tw) // 2, 0
    elif anchor == "bottom":
        left, upper = (new_w - tw) // 2, new_h - th
    elif anchor == "left":
        left, upper = 0, (new_h - th) // 2
    elif anchor == "right":
        left, upper = new_w - tw, (new_h - th) // 2
    else:
        raise ValueError(f"Invalid anchor: {anchor}")

    return mark.crop((left, upper, left + tw, upper + th))


# Internal implementation note: legacy behavior is preserved during modernization.
def watermark_image(
    photo_bytes: bytes | BinaryIO,
    watermark_path: str,
    *,
    opacity: float = 1.0,
    jpeg_quality: int = 90,
    anchor: Literal["center", "top", "bottom", "left", "right"] = "center",
) -> io.BytesIO:
    """Legacy-compatible behavior preserved for this callable."""
    # 1) Load base image (RGBA guarantees alpha layer for composite)
    if isinstance(photo_bytes, bytes):
        photo_bytes = io.BytesIO(photo_bytes)
    base = Image.open(photo_bytes)
    base = ImageOps.exif_transpose(base)  # honour EXIF orientation
    base = base.convert("RGBA")

    # 2) Prepare watermark: load (cached), scale, crop, adjust opacity
    mark = _load_mark(watermark_path)
    mark = _scale_and_crop(mark, base.size, anchor=anchor)

    if opacity < 1.0:
        # Multiply existing alpha by opacity
        r, g, b, a = mark.split()
        a = a.point(lambda p: int(p * max(0, min(opacity, 1))))
        mark.putalpha(a)

    # 3) Composite & export
    combined = Image.alpha_composite(base, mark)

    buf = io.BytesIO()
    combined.convert("RGB").save(buf, format="JPEG", quality=jpeg_quality)
    buf.seek(0)
    return buf
