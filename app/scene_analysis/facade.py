# scene_analysis/facade.py
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
    """前端把上传文件(字节或文件对象)直接丢进来；本函数负责落盘 -> 调用 analyze_video -> 返回结果。"""
    # 兼容 bytes / BytesIO / UploadedFile
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
        # 临时文件清理（根据业务需要，也可让前端决定是否保留）
        try:
            os.remove(tmp_path)
        except OSError:
            pass
