from __future__ import annotations
from typing import Dict, Tuple, Optional
import cv2, numpy as np

try:
    import mediapipe as mp
except Exception:
    mp = None  # 环境无 mediapipe 时兜底

from .emotion_config import EmotionConfig

# —— 工具：按高度等比缩放 ——
def resize_by_height(img: np.ndarray, target_h: int) -> np.ndarray:
    h, w = img.shape[:2]
    if h <= target_h:
        return img
    scale = target_h / float(h)
    new_w = int(w * scale)
    return cv2.resize(img, (new_w, target_h), interpolation=cv2.INTER_AREA)

# —— 计算 2D 点距离 ——
def _dist(a: Tuple[float,float], b: Tuple[float,float]) -> float:
    return float(np.hypot(a[0]-b[0], a[1]-b[1]))

# —— FaceMesh 用到的稳定 landmark 索引 ——
LEFT_EYE_OUTER = 33
RIGHT_EYE_OUTER = 263
LEFT_EYE_TOP, LEFT_EYE_BOTTOM = 159, 145
RIGHT_EYE_TOP, RIGHT_EYE_BOTTOM = 386, 374
MOUTH_LEFT, MOUTH_RIGHT = 61, 291
LIP_TOP, LIP_BOTTOM = 13, 14

def _select_best_face(dets, w: int, h: int):
    """选面积×置信度最大的检测框，返回 (x,y,w,h, score)；没有检测返回 None"""
    if not dets:
        return None
    best = None; best_score = 0.0
    for d in dets:
        bb = d.location_data.relative_bounding_box
        x = max(0, int(bb.xmin * w)); y = max(0, int(bb.ymin * h))
        ww = max(1, int(bb.width * w)); hh = max(1, int(bb.height * h))
        score = float(ww * hh) * float(d.score[0] if d.score else 1.0)
        if score > best_score:
            best_score = score
            best = (x, y, ww, hh, score)
    return best

def _detect_face_roi(frame_bgr: np.ndarray, cfg: EmotionConfig):
    """
    用 MediaPipe FaceDetection 检测整帧，返回裁剪后的 ROI 及中心/宽度：
      (roi_bgr, (cx, cy), face_width)；检测不到返回 None
    - 支持从 cfg 读取可选参数：
        fd_min_conf (默认 0.5), fd_model_selection (默认 0), fd_margin (默认 0.35)
      若 0 检不到，会回退尝试 model_selection=1（远景）。
    """
    if mp is None:
        return None
    h, w = frame_bgr.shape[:2]
    min_conf = float(getattr(cfg, "fd_min_conf", 0.5))
    margin   = float(getattr(cfg, "fd_margin", 0.35))

    rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)

    # 先用近景模型，失败再用远景模型
    det = None
    for ms in (int(getattr(cfg, "fd_model_selection", 0)), 1):
        with mp.solutions.face_detection.FaceDetection(
            model_selection=ms, min_detection_confidence=min_conf
        ) as fd:
            res = fd.process(rgb)
        if res and res.detections:
            best = _select_best_face(res.detections, w, h)
            if best:
                x, y, ww, hh, _ = best
                # 扩边 margin
                cx, cy = x + ww/2.0, y + hh/2.0
                W2, H2 = int(ww * (1 + margin)), int(hh * (1 + margin))
                x2 = max(0, int(cx - W2/2)); y2 = max(0, int(cy - H2/2))
                x2e = min(w, x2 + W2); y2e = min(h, y2 + H2)
                roi = frame_bgr[y2:y2e, x2:x2e]
                face_width = float(max(ww, hh))
                det = (roi, (float(cx), float(cy)), face_width)
                break
    return det

def extract_face_metrics(
    frame_bgr: np.ndarray,
    prev_center: Optional[Tuple[float, float]],
    cfg: EmotionConfig,
    face_mesh=None,   # 外层传进来的实例（推荐）；None 时会临时创建
):
    """
    返回单帧原始几何指标（未归一化）：
      {"smile","eye_open","mouth_open","head_motion"}
    逻辑：
      1) 先在人脸全图上做检测，锁定 ROI；
      2) 在 ROI 上跑 FaceMesh 提嘴/眼几何；
      3) head_motion = 检测框中心位移 / 人脸宽度（对远近/位置更稳）。
    无人脸/抓不到 landmark 时返回 (None, prev_center)，由上层跳过该帧。
    """
    if mp is None:
        return None, prev_center

    det = _detect_face_roi(frame_bgr, cfg)
    if det is None:
        return None, prev_center
    roi_bgr, det_center, face_w = det  # det_center 是“全图坐标”的检测框中心

    # 在 ROI 上跑 FaceMesh（优先复用外部实例）
    small = resize_by_height(roi_bgr, cfg.downscale_h)
    rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)

    if face_mesh is None:
        with mp.solutions.face_mesh.FaceMesh(
            static_image_mode=cfg.static_image_mode,
            max_num_faces=1,
            refine_landmarks=cfg.refine_landmarks,
            min_detection_confidence=cfg.min_detection_confidence,
            min_tracking_confidence=cfg.min_tracking_confidence,
        ) as fm:
            res = fm.process(rgb)
    else:
        res = face_mesh.process(rgb)

    if not res.multi_face_landmarks:
        return None, prev_center

    # —— 在 ROI 上计算几何（用眼距归一化） ——
    h, w = small.shape[:2]
    pts = res.multi_face_landmarks[0].landmark
    def p(idx):
        lm = pts[idx]
        return (lm.x * w, lm.y * h)

    eye_L = p(LEFT_EYE_OUTER)
    eye_R = p(RIGHT_EYE_OUTER)
    eye_dist = _dist(eye_L, eye_R) + 1e-6

    eye_open_L = _dist(p(LEFT_EYE_TOP),  p(LEFT_EYE_BOTTOM))  / eye_dist
    eye_open_R = _dist(p(RIGHT_EYE_TOP), p(RIGHT_EYE_BOTTOM)) / eye_dist
    eye_open   = float((eye_open_L + eye_open_R) / 2.0)
    smile      = _dist(p(MOUTH_LEFT),  p(MOUTH_RIGHT)) / eye_dist
    mouth_open = _dist(p(LIP_TOP),     p(LIP_BOTTOM))  / eye_dist

    # —— 头部位移：用“检测框中心”在全图的位移 / 人脸宽度 —— 更鲁棒
    if prev_center is None:
        head_motion = 0.0
    else:
        dx = det_center[0] - prev_center[0]
        dy = det_center[1] - prev_center[1]
        head_motion = float(np.hypot(dx, dy)) / max(face_w, 1e-6)

    metrics = {
        "eye_open":   float(eye_open),
        "smile":      float(smile),
        "mouth_open": float(mouth_open),
        "head_motion":float(head_motion),
    }
    # 返回新的 center（全图坐标）
    return metrics, det_center

# —— 归一化到 0~1（经验线性映射；如你已用“自适应归一化”，这些可忽略） ——
def normalize_smile(x: float) -> float:
    # 嘴角宽度/眼距：远景ROI后通常 0.30~0.65
    return float(np.clip((x - 0.30) / (0.65 - 0.30), 0.0, 1.0))

def normalize_eye_open(x: float) -> float:
    # 眼睛垂直/眼距：0.12~0.28
    return float(np.clip((x - 0.12) / (0.28 - 0.12), 0.0, 1.0))

def normalize_mouth_open(x: float) -> float:
    # 唇间距/眼距：0.02~0.12
    return float(np.clip((x - 0.02) / (0.12 - 0.02), 0.0, 1.0))

def normalize_head_motion(x: float) -> float:
    # 检测框中心位移 / 人脸宽度：0.005~0.05
    return float(np.clip((x - 0.005) / (0.05 - 0.005), 0.0, 1.0))
