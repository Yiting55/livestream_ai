from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple

@dataclass
class SceneConfig:
    """可调参数集中在这里，方便一处改动全局生效。"""
    # 采样频率（抽帧）
    sample_fps: float = 1.0                 # 每秒取几帧做质量度量
    ocr_every_s: float = 5.0                # 每隔N秒做一次OCR（减少开销）

    # 下采样尺寸（加速处理用）
    downscale_for_metrics_h: int = 480      # 计算亮度/清晰度等时缩放到该高度
    downscale_for_ocr_h: int = 640          # 做OCR时缩放到该高度

    # 打分区间（8-bit 图像）
    brightness_band: Tuple[float, float] = (120.0, 180.0)  # HSV.V 理想带
    saturation_band: Tuple[float, float] = (60.0, 160.0)   # HSV.S 理想带
    contrast_band: Tuple[float, float] = (40.0, 160.0)     # P95-P5 的带宽
    sharpness_band: Tuple[float, float] = (100.0, 300.0)   # Laplacian 方差
    color_cast_good: float = 10.0                          # |R-G| 与 |B-G| 越小越好
    color_cast_bad: float = 40.0

    # 高亮区段判定
    dark_v_thresh: float = 110.0            # V < 110 判为偏暗
    blur_varlap_thresh: float = 120.0       # varlap < 120 判为偏虚
    no_logo_min_s: float = 8.0              # 连续≥8s 才作为高亮问题片段

    # OCR 设置
    tesseract_lang: str = "eng"            # 可设 "chi_sim+eng"
    tesseract_psm: str = "6"               # 假设均匀文本块
    ocr_only_if_sharp: bool = True          # 仅在清晰帧上做 OCR
    ocr_min_varlap: float = 140.0           # 清晰阈值（低于此值跳过 OCR）

    # 自动降采样
    autoscale_enabled: bool = True          # 根据时长自动调低采样与提高 OCR 周期

    # 最终评分权重（可依据业务调整）
    w_exposure: float = 0.30
    w_sharpness: float = 0.25
    w_contrast: float = 0.15
    w_saturation: float = 0.10
    w_colorcast: float = 0.10
    w_logo: float = 0.10

