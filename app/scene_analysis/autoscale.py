from __future__ import annotations
from dataclasses import replace
from .scene_config import SceneConfig

def autoscale_config(cfg: SceneConfig, duration_s: float) -> SceneConfig:
    if not cfg.autoscale_enabled:
        return cfg
    # 阈值区间：<10min 保持；10–30min 降到0.5Hz/8s；30–60min 降到0.33Hz/12s；>=60min 降到0.2Hz/20s
    mins = duration_s / 60.0
    sample_fps, ocr_every = cfg.sample_fps, cfg.ocr_every_s
    if mins < 10:
        pass
    elif mins < 30:
        sample_fps = min(sample_fps, 0.5)
        ocr_every = max(ocr_every, 8.0)
    elif mins < 60:
        sample_fps = min(sample_fps, 0.33)
        ocr_every = max(ocr_every, 12.0)
    else:
        sample_fps = min(sample_fps, 0.2)
        ocr_every = max(ocr_every, 20.0)
    return replace(cfg, sample_fps=sample_fps, ocr_every_s=ocr_every)

