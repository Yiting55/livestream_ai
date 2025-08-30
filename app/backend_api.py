# app/backend_api.py
"""
后端调用封装：语言分析 + 视觉分析 + 场景分析
"""

from io_utils import save_upload_to_tempfile, remove_path

# ---- Language (A) ----
from ui_api import run_language_analysis

# ---- Visual (B) ----
from analyzer import analyze_video

# ---- Scene (C) ----
try:
    from scene_analysis import analyze_scene_from_upload, SceneConfig
    HAS_SCENE = True
except Exception:
    HAS_SCENE = False


def run_full_analysis(uploaded_file):
    """
    保存上传文件到临时目录 → 调用语言+视觉 → 清理 → 返回结果
    """
    tmp_path, tmp_dir = save_upload_to_tempfile(uploaded_file, show_progress=True)

    try:
        lang_bundle = run_language_analysis(tmp_path)
        visual_result = analyze_video(tmp_path)
    finally:
        remove_path(tmp_dir)

    return {
        "language": lang_bundle,
        "visual": visual_result,
        "file_meta": {
            "name": uploaded_file.name,
            "size_mb": round(len(uploaded_file.getbuffer()) / 1024 / 1024, 2),
        }
    }


def run_scene_analysis(uploaded_file, tess_lang="chi_sim+eng", brand_keywords=None):
    """
    单独调用场景分析（OCR/品牌识别）
    """
    if not HAS_SCENE:
        return {"error": "scene_analysis module not available"}

    brand_keywords = brand_keywords or set()
    cfg = SceneConfig(tesseract_lang=tess_lang)
    out = analyze_scene_from_upload(uploaded_file, uploaded_file.name, config=cfg, brand_keywords=brand_keywords)
    return out
