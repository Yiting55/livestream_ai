from __future__ import annotations
from typing import Dict
import cv2, numpy as np
from .scene_config import SceneConfig

# —— 图像缩放：按目标高度等比缩放 ——
def resize_by_height(img: np.ndarray, target_h: int) -> np.ndarray:
    h, w = img.shape[:2]
    if h <= target_h:
        return img
    scale = target_h / float(h)
    new_w = int(w * scale)
    return cv2.resize(img, (new_w, target_h), interpolation=cv2.INTER_AREA)

# —— 单帧指标：亮度、饱和度、对比度带宽、清晰度、色偏 ——
def frame_metrics(frame_bgr: np.ndarray, cfg: SceneConfig) -> Dict[str, float]:
    """对单帧计算基础指标。
    返回：{"v_mean","s_mean","contrast_bw","varlap","color_cast"}
    """
    small = resize_by_height(frame_bgr, cfg.downscale_for_metrics_h)

    hsv = cv2.cvtColor(small, cv2.COLOR_BGR2HSV)
    hch, sch, vch = cv2.split(hsv)
    v_mean = float(np.mean(vch))            # 亮度（V通道均值）
    s_mean = float(np.mean(sch))            # 饱和度（S通道均值）

    gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
    p5, p95 = np.percentile(gray, [5, 95]) # 5分位与95分位
    contrast_bw = float(p95 - p5)           # 有效动态范围（带宽）

    varlap = float(cv2.Laplacian(gray, cv2.CV_64F).var())  # 清晰度（拉普拉斯方差）

    # 色偏：R/G/B 三通道均值差（越小越佳）
    b_mean = float(np.mean(small[:, :, 0]))
    g_mean = float(np.mean(small[:, :, 1]))
    r_mean = float(np.mean(small[:, :, 2]))
    color_cast = float((abs(r_mean - g_mean) + abs(b_mean - g_mean)) / 2.0)

    return {
        "v_mean": v_mean,
        "s_mean": s_mean,
        "contrast_bw": contrast_bw,
        "varlap": varlap,
        "color_cast": color_cast,
    }

# —— 简单评分函数 ——
def band_score(x: float, lo: float, hi: float) -> float:
    """目标区间内 80~100；区外线性衰减到 0。"""
    if x <= lo:
        return max(0.0, 100.0 * (x / max(lo, 1e-6)))
    if x >= hi:
        return max(0.0, 100.0 * ((255.0 - x) / max(255.0 - hi, 1e-6)))
    return 80.0 + 20.0 * (x - lo) / max((hi - lo), 1e-6)

def linear_score(x: float, lo: float, hi: float) -> float:
    x = max(lo, min(hi, x))
    return 100.0 * (x - lo) / max((hi - lo), 1e-6)

def inverse_score(x: float, good: float, bad: float) -> float:
    if x <= good:
        return 100.0
    if x >= bad:
        return 0.0
    return 100.0 * (bad - x) / max((bad - good), 1e-6)
