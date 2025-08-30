from __future__ import annotations
import io, os, tempfile
from typing import IO, Iterable, Optional, Set
from .scene_analysis import analyze_video
from .scene_config import SceneConfig

def analyze_scene_from_upload(
    file: IO[bytes] | bytes,
    filename: str = "upload.mp4",
    *,
    brand_keywords: Optional[Set[str]] = None,
    config: SceneConfig = SceneConfig(),
) -> dict:
    if hasattr(file, "read"):
        content = file.read()
    elif isinstance(file, (bytes, bytearray)):
        content = bytes(file)
    else:
        raise TypeError("file must be a bytes-like object or an IO[bytes]")

    suffix = os.path.splitext(filename)[-1] or ".mp4"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        return analyze_video(tmp_path, brand_keywords=brand_keywords, config=config)
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
