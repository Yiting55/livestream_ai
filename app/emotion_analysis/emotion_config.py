# scene_analysis/emotion_config.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Literal

@dataclass
class EmotionConfig:
    """
    全局配置（表情/能量分析）
    - 采样/平滑：控制帧采样与时间平滑
    - 人脸检测：MediaPipe FaceDetection 的阈值/模型/裁剪边距
    - 多人：最多跟踪的人脸数与聚合方式
    - FaceMesh：在 ROI 上跑 landmarks 的选项
    - 评分：各项权重与高亮阈值
    """

    # ------- 采样与平滑 -------
    sample_fps: float = 1.0          # 每秒采样帧数（1Hz 足够稳定）
    downscale_h: int = 480           # ROI 统一高度（越小越快）
    smooth_window_s: float = 1.2     # 移动平均窗口（秒）
    autoscale_enabled: bool = True   # 长视频自动降采样

    # ------- 人脸检测（FaceDetection）-------
    fd_min_conf: float = 0.5         # 置信度阈值
    fd_model_selection: int = 0      # 0近景 / 1远景（主播远、脸很小用 1）
    fd_margin: float = 0.40          # ROI 裁剪扩边比例（0.3~0.5 之间调）

    # ------- 多人支持 -------
    max_faces: int = 2               # 每帧最多跟踪的人脸数（1~4）
    aggregate_mode: Literal["primary", "mean", "max"] = "primary"
    # primary: 以“出现帧数最多”的人作为主结果
    # mean   : 对所有人脸的分数取平均（作为 group_score）
    # max    : 取最高分（作为 group_score）

    # ------- FaceMesh（在 ROI 上跑）-------
    static_image_mode: bool = False
    max_num_faces: int = 1           # 每个 ROI 内只取 1 张脸
    refine_landmarks: bool = True    # 精细嘴唇/眼部（更准、稍慢）
    min_detection_confidence: float = 0.5
    min_tracking_confidence: float = 0.5

    # ------- 评分权重 -------
    w_valence: float = 0.55
    w_energy: float = 0.45
    w_smile: float = 0.6             # valence = 0.6*smile + 0.4*eye_open
    w_eye_open: float = 0.4
    w_mouth_dyn: float = 0.6         # energy = 0.6*mouth + 0.25*head + 0.15*eye_var
    w_head_motion: float = 0.25
    w_eye_var: float = 0.15

    # ------- 高亮阈值 -------
    low_valence_thresh: float = 0.4
    high_valence_thresh: float = 0.7
    low_energy_thresh: float = 0.4
    high_energy_thresh: float = 0.7
    min_span_s: float = 4.0          # 高亮片段最短持续秒数
