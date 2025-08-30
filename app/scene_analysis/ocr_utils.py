from __future__ import annotations
from typing import List, Tuple, Optional, Set
import cv2, numpy as np
try:
    import pytesseract
    from PIL import Image
except Exception:  # 环境无OCR库时，降级为空实现
    pytesseract = None
    Image = None

from .scene_config import SceneConfig
from .metrics_frame import resize_by_height

# —— 在一帧上做OCR，返回(词列表, 文本面积占比) ——
def ocr_on_frame(frame_bgr: np.ndarray, cfg: SceneConfig) -> Tuple[List[str], float]:
    if pytesseract is None or Image is None:
        return [], 0.0
    small = resize_by_height(frame_bgr, cfg.downscale_for_ocr_h)
    rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(rgb)
    config = f"--oem 3 --psm {cfg.tesseract_psm}"
    try:
        data = pytesseract.image_to_data(img, lang=cfg.tesseract_lang, config=config, output_type=pytesseract.Output.DICT)
    except Exception:
        return [], 0.0
    words: List[str] = []
    total_area = 0.0
    img_area = float(small.shape[0] * small.shape[1])
    n = len(data.get("text", []))
    for i in range(n):
        text = (data["text"][i] or "").strip()
        conf = float(data.get("conf", [0]*n)[i])
        if text and conf > 60:
            words.append(text)
            bw = int(data.get("width", [0]*n)[i])
            bh = int(data.get("height", [0]*n)[i])
            total_area += float(bw * bh)
    area_ratio = float(total_area / img_area) if img_area > 0 else 0.0
    return words, area_ratio

# —— 根据品牌关键字判断是否“露出” ——
def logo_hit_by_keywords(words: List[str], brand_keywords: Optional[Set[str]]) -> bool:
    if not brand_keywords:
        return False
    lower_words = {w.lower() for w in words}
    for kw in brand_keywords:
        if kw.lower() in lower_words:
            return True
    return False

