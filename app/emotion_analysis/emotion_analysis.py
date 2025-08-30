from __future__ import annotations
from typing import Dict, List, Optional, Tuple
import time
from collections import deque
import cv2, numpy as np
import mediapipe as mp

from .emotion_config import EmotionConfig
from .emotion_features import extract_face_metrics  

def moving_avg(arr: List[float], k: int) -> List[float]:
    """Simple moving average of a list with window k (k>=1)."""
    if k <= 1 or len(arr) == 0:
        return list(arr)
    out: List[float] = []
    s = 0.0
    q = deque()
    for x in arr:
        x = float(x)
        q.append(x)
        s += x
        if len(q) > k:
            s -= q.popleft()
        out.append(s / len(q))
    return out

def adapt_norm(x: np.ndarray, p_lo: float = 5, p_hi: float = 85,
               floor: float = 0.20, ceil: float = 0.98, gamma: float = 0.85) -> np.ndarray:
    if len(x) == 0:
        return x
    lo = float(np.percentile(x, p_lo))
    hi = float(np.percentile(x, p_hi))
    if not np.isfinite(lo) or not np.isfinite(hi) or hi <= lo + 1e-6:
        return np.full_like(x, (floor + ceil) * 0.5, dtype=np.float32)
    z = np.clip((x - lo) / (hi - lo), 0.0, 1.0).astype(np.float32)
    z = z ** float(gamma)
    return np.clip(floor + (ceil - floor) * z, 0.0, 1.0)

def topk_mean_rowwise(M: np.ndarray, k: int) -> np.ndarray:
    if M.ndim != 2:
        M = np.atleast_2d(M)
    k = max(1, min(k, M.shape[1]))
    Ms = np.sort(M, axis=1)
    return Ms[:, -k:].mean(axis=1)

def peak_hold(series: np.ndarray, tau_s: float, fps: float) -> np.ndarray:
    out = np.zeros_like(series, dtype=np.float32)
    if len(series) == 0:
        return out
    decay = np.exp(-1.0 / max(tau_s * max(fps, 1e-6), 1e-6))
    peak = 0.0
    for i, x in enumerate(series.astype(np.float32)):
        peak = max(float(x), float(peak * decay))
        out[i] = peak
    return out

def calibrate_score(base_mean: float, cfg: EmotionConfig) -> float:
    mode = getattr(cfg, "calibration_mode", "none")  
    floor = float(getattr(cfg, "score_floor", 0.0)) / 100.0
    ceil  = float(getattr(cfg, "score_ceiling", 100.0)) / 100.0
    base = float(np.clip(base_mean, 0.0, 1.0))

    if mode == "affine":
        gain = float(getattr(cfg, "calib_gain", 1.0))
        bias = float(getattr(cfg, "calib_bias", 0.0))
        y = gain * base + bias
    elif mode == "target_mean":
        target = float(getattr(cfg, "target_mean", 0.80))
        alpha  = float(getattr(cfg, "target_strength", 0.65))
        y = (1.0 - alpha) * base + alpha * target
    else:
        y = base

    y = float(np.clip(y, floor, ceil))
    return 100.0 * y

def analyze_emotion(video_path: str, config: EmotionConfig = EmotionConfig()) -> Dict[str, dict]:
    t0 = time.perf_counter()

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    duration = float(total_frames / max(fps, 1e-6)) if total_frames > 0 else 0.0

    sample_fps = float(getattr(config, "sample_fps", 1.0))
    if getattr(config, "autoscale_enabled", True):
        mins = duration / 60.0
        if mins >= 60:
            sample_fps = min(sample_fps, 0.5)
        elif mins >= 30:
            sample_fps = min(sample_fps, 1.0)
    step = max(int(round(fps / max(sample_fps, 1e-6))), 1)

    raw_t: List[float] = []
    raw_smile: List[float] = []
    raw_eye: List[float] = []
    raw_mouth: List[float] = []
    raw_head: List[float] = []

    sampled_frames = 0
    valid_frames = 0

    with mp.solutions.face_mesh.FaceMesh(
        static_image_mode=getattr(config, "static_image_mode", False),
        max_num_faces=getattr(config, "max_num_faces", 1),  
        refine_landmarks=getattr(config, "refine_landmarks", True),
        min_detection_confidence=getattr(config, "min_detection_confidence", 0.5),
        min_tracking_confidence=getattr(config, "min_tracking_confidence", 0.5),
    ) as face_mesh:

        prev_center: Optional[Tuple[float, float]] = None  
        i = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            if i % step != 0:
                i += 1
                continue
            t = i / max(fps, 1e-6)
            sampled_frames += 1

            m, prev_center = extract_face_metrics(frame, prev_center, config, face_mesh)
            if m is None:
                i += 1
                continue  

            raw_t.append(float(t))
            raw_smile.append(float(m.get("smile", 0.0)))
            raw_eye.append(float(m.get("eye_open", 0.0)))
            raw_mouth.append(float(m.get("mouth_open", 0.0)))
            raw_head.append(float(m.get("head_motion", 0.0)))
            valid_frames += 1
            i += 1

    cap.release()

    if valid_frames == 0:
        total_s = time.perf_counter() - t0
        perf = {
            "video": {"fps": fps, "frames": total_frames, "duration_s": round(duration, 3)},
            "sampling": {"sample_fps": sample_fps, "frames_sampled": sampled_frames, "valid_frames": 0, "detection_rate": 0.0},
            "timing": {"total_s": round(total_s, 3)},
        }
        return {
            "emotion": {
                "score": 0.0,
                "signals": {"valence_mean": 0.0, "energy_mean": 0.0},
                "timeline": [],
                "highlights": [{"start": 0.0, "end": 0.0, "reason": "未检测到人脸或人脸覆盖过低"}],
            },
            "perf": perf,
        }

    smile_n = adapt_norm(np.array(raw_smile, dtype=np.float32))
    eye_n   = adapt_norm(np.array(raw_eye,   dtype=np.float32))
    mouth_n = adapt_norm(np.array(raw_mouth, dtype=np.float32))
    head_n  = adapt_norm(np.array(raw_head,  dtype=np.float32))

    eye_var   = np.abs(np.diff(eye_n,   prepend=eye_n[:1]))
    mouth_var = np.abs(np.diff(mouth_n, prepend=mouth_n[:1]))

    w_smile    = getattr(config, "w_smile", 0.6)
    w_eye_open = getattr(config, "w_eye_open", 0.4)
    valence = w_smile * smile_n + w_eye_open * eye_n

    c_mouth = np.maximum(mouth_n, 1.30 * mouth_var)   
    c_head  = head_n
    c_eye   = eye_var

    C = np.stack([c_mouth, c_head, c_eye], axis=1)    
    energy_core = topk_mean_rowwise(C, k=2)           
    hold = peak_hold(energy_core, tau_s=1.0, fps=sample_fps)
    energy = np.clip(0.6 * energy_core + 0.4 * hold, 0.0, 1.0)

    k = max(1, int(round(getattr(config, "smooth_window_s", 1.5) * sample_fps)))
    valence_s = moving_avg(list(valence), k)
    energy_s  = moving_avg(list(energy),  k)

    valence_s = [float(np.clip(v, 0.0, 1.0)) for v in valence_s]
    energy_s  = [float(np.clip(e, 0.0, 1.0)) for e in energy_s]

    w_valence = getattr(config, "w_valence", 0.6)
    w_energy  = getattr(config, "w_energy",  0.4)
    base_mean = (w_valence * float(np.mean(valence_s)) + w_energy * float(np.mean(energy_s)))
    score = calibrate_score(base_mean, config)  

    def compress_runs(times: List[float], mask: List[bool], min_s: float) -> List[Tuple[float, float]]:
        out: List[Tuple[float, float]] = []
        start = None
        prev = None
        for t, f in zip(times, mask):
            if f and start is None:
                start = t
            if (not f) and start is not None:
                if prev is not None and (prev - start) >= min_s:
                    out.append((start, prev))
                start = None
            prev = t
        if start is not None and prev is not None and (prev - start) >= min_s:
            out.append((start, prev))
        return out

    low_val  = getattr(config, "low_valence_thresh", 0.35)
    high_val = getattr(config, "high_valence_thresh", 0.65)
    low_en   = getattr(config, "low_energy_thresh", 0.35)
    high_en  = getattr(config, "high_energy_thresh", 0.65)
    min_span = getattr(config, "min_span_s", 4.0)

    low_val_mask  = [v < low_val  for v in valence_s]
    high_val_mask = [v > high_val for v in valence_s]
    low_en_mask   = [e < low_en   for e in energy_s]
    high_en_mask  = [e > high_en  for e in energy_s]

    highlights = []
    for a, b in compress_runs(raw_t, high_en_mask,  min_span):
        highlights.append({"start": float(a), "end": float(b), "reason": "高能量片段"})
    for a, b in compress_runs(raw_t, low_en_mask,   min_span):
        highlights.append({"start": float(a), "end": float(b), "reason": "能量偏低"})
    for a, b in compress_runs(raw_t, low_val_mask,  min_span):
        highlights.append({"start": float(a), "end": float(b), "reason": "积极度偏低"})

    timeline = [
        {
            "t": float(t),
            "valence": float(valence_s[i]),
            "energy":  float(energy_s[i]),
            "smile":   float(smile_n[i]),
            "eye":     float(eye_n[i]),
            "mouth":   float(mouth_n[i]),
            "head":    float(head_n[i]),
        }
        for i, t in enumerate(raw_t)
    ]

    detection_rate = valid_frames / max(sampled_frames, 1)
    if detection_rate < 0.2:
        highlights.append({"start": 0.0, "end": 0.0, "reason": "人脸检测覆盖低(<20%)，结果可能不稳定"})

    emotion_block = {
        "score": round(float(score), 1),
        "signals": {
            "valence_mean": round(float(np.mean(valence_s)), 3),
            "energy_mean":  round(float(np.mean(energy_s)), 3),
        },
        "timeline": timeline,
        "highlights": highlights,
    }

    total_s = time.perf_counter() - t0
    perf = {
        "video": {"fps": fps, "frames": total_frames, "duration_s": round(duration, 3)},
        "sampling": {
            "sample_fps": sample_fps,
            "frames_sampled": sampled_frames,
            "valid_frames": valid_frames,
            "detection_rate": round(detection_rate, 3),
        },
        "timing": {"total_s": round(total_s, 3)},
    }

    return {"emotion": emotion_block, "perf": perf}
