from __future__ import annotations
from typing import Dict, List, Optional, Set
import time
import cv2, numpy as np

from .scene_config import SceneConfig
from .metrics_frame import frame_metrics, band_score, linear_score, inverse_score
from .ocr_utils import ocr_on_frame, logo_hit_by_keywords
from .highlights import compress_runs
from .autoscale import autoscale_config

# —— 主函数：analyze_video ——
def analyze_video(video_path: str, *, brand_keywords: Optional[Set[str]] = None, config: SceneConfig = SceneConfig()) -> Dict[str, dict]:
    t0 = time.perf_counter()

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    duration = float(total_frames / max(fps, 1e-6)) if total_frames > 0 else 0.0

    eff_cfg = autoscale_config(config, duration)

    step = max(int(round(fps / max(eff_cfg.sample_fps, 1e-6))), 1)
    next_ocr_t = 0.0

    times: List[float] = []
    v_list: List[float] = []
    s_list: List[float] = []
    bw_list: List[float] = []
    varlap_list: List[float] = []
    cast_list: List[float] = []

    ocr_frames = 0
    ocr_logo_frames = 0
    ocr_area_sum = 0.0
    ocr_time_sum = 0.0

    timeline: List[Dict[str, float | bool]] = []

    i = 0
    sampled = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if i % step != 0:
            i += 1; continue
        t = i / max(fps, 1e-6)

        m = frame_metrics(frame, eff_cfg)
        times.append(t)
        v_list.append(m["v_mean"])
        s_list.append(m["s_mean"])
        bw_list.append(m["contrast_bw"])
        varlap_list.append(m["varlap"])
        cast_list.append(m["color_cast"])
        sampled += 1

        logo_hit, text_area = False, 0.0
        do_ocr = (t >= next_ocr_t)
        if eff_cfg.ocr_only_if_sharp:
            do_ocr = do_ocr and (m["varlap"] >= eff_cfg.ocr_min_varlap)
        if do_ocr:
            t_ocr0 = time.perf_counter()
            words, text_area = ocr_on_frame(frame, eff_cfg)
            ocr_time_sum += (time.perf_counter() - t_ocr0)
            ocr_frames += 1
            if brand_keywords:
                logo_hit = logo_hit_by_keywords(words, brand_keywords)
            else:
                logo_hit = text_area > 0.01
            if logo_hit:
                ocr_logo_frames += 1
            ocr_area_sum += text_area
            next_ocr_t = t + max(eff_cfg.ocr_every_s, 1.0)

        timeline.append({
            "t": float(t),
            "v": float(m["v_mean"]),
            "s": float(m["s_mean"]),
            "varlap": float(m["varlap"]),
            "logo": bool(logo_hit),
            "text_area": float(text_area),
        })
        i += 1

    cap.release()

    if not times:
        perf = {
            "video": {"fps": fps, "frames": total_frames, "duration_s": duration},
            "sampling": {"sample_fps": eff_cfg.sample_fps, "frames_sampled": 0, "ocr_every_s": eff_cfg.ocr_every_s, "ocr_attempts": 0, "ocr_hits": 0},
            "timing": {"total_s": round(time.perf_counter() - t0, 3), "avg_per_frame_ms": 0.0, "avg_ocr_ms": 0.0},
        }
        return {"scene": {"score": 0.0, "signals": {"brightness_mean":0.0,"contrast_bw":0.0,"sharpness_varlap":0.0,"saturation_mean":0.0,"color_cast":0.0,"logo_visible_ratio":0.0,"logo_area_mean":0.0}, "timeline": [], "highlights": [{"start":0.0,"end":0.0,"reason":"无法抽帧/解码失败"}]}, "perf": perf}

    v_mean = float(np.mean(v_list))
    s_mean = float(np.mean(s_list))
    bw_mean = float(np.mean(bw_list))
    varlap_mean = float(np.mean(varlap_list))
    cast_mean = float(np.mean(cast_list))

    logo_visible_ratio = float(ocr_logo_frames / max(ocr_frames, 1)) if ocr_frames else 0.0
    logo_area_mean = float(ocr_area_sum / max(ocr_frames, 1)) if ocr_frames else 0.0

    s_exposure   = band_score(v_mean, *eff_cfg.brightness_band)
    s_saturation = band_score(s_mean, *eff_cfg.saturation_band)
    s_contrast   = linear_score(bw_mean, *eff_cfg.contrast_band)
    s_sharp      = linear_score(max(min(varlap_mean, eff_cfg.sharpness_band[1]), eff_cfg.sharpness_band[0]), *eff_cfg.sharpness_band)
    s_color      = inverse_score(cast_mean, eff_cfg.color_cast_good, eff_cfg.color_cast_bad)

    logo_score_ratio = min(1.0, logo_visible_ratio / 0.30)
    logo_score_area  = min(1.0, logo_area_mean / 0.05)
    s_logo = 100.0 * (0.6 * logo_score_ratio + 0.4 * logo_score_area)

    final_score = (
        eff_cfg.w_exposure  * s_exposure +
        eff_cfg.w_sharpness * s_sharp    +
        eff_cfg.w_contrast  * s_contrast +
        eff_cfg.w_saturation* s_saturation+
        eff_cfg.w_colorcast * s_color    +
        eff_cfg.w_logo      * s_logo
    )

    dark_mask   = [v < eff_cfg.dark_v_thresh for v in v_list]
    blur_mask   = [vl < eff_cfg.blur_varlap_thresh for vl in varlap_list]
    nologo_mask = [not item.get("logo", False) for item in timeline] if any(d.get("logo") for d in timeline) else [True]*len(timeline)

    dark_spans   = compress_runs(times, dark_mask,   eff_cfg.no_logo_min_s)
    blur_spans   = compress_runs(times, blur_mask,   eff_cfg.no_logo_min_s)
    nologo_spans = compress_runs(times, nologo_mask, eff_cfg.no_logo_min_s)

    highlights = []
    for a,b in dark_spans:   highlights.append({"start": float(a), "end": float(b), "reason": "画面偏暗"})
    for a,b in blur_spans:   highlights.append({"start": float(a), "end": float(b), "reason": "画面偏虚"})
    for a,b in nologo_spans: highlights.append({"start": float(a), "end": float(b), "reason": "无商品/Logo露出"})

    scene_block = {
        "score": round(float(final_score), 1),
        "signals": {
            "brightness_mean": round(v_mean, 1),
            "contrast_bw": round(bw_mean, 1),
            "sharpness_varlap": round(varlap_mean, 1),
            "saturation_mean": round(s_mean, 1),
            "color_cast": round(cast_mean, 1),
            "logo_visible_ratio": round(logo_visible_ratio, 3),
            "logo_area_mean": round(logo_area_mean, 4),
        },
        "timeline": timeline,
        "highlights": highlights,
    }

    total_s = time.perf_counter() - t0
    perf = {
        "video": {"fps": fps, "frames": total_frames, "duration_s": round(duration,3)},
        "sampling": {"sample_fps": eff_cfg.sample_fps, "frames_sampled": sampled, "ocr_every_s": eff_cfg.ocr_every_s, "ocr_attempts": ocr_frames, "ocr_hits": ocr_logo_frames},
        "timing": {"total_s": round(total_s, 3), "avg_per_frame_ms": round((total_s / max(sampled,1))*1000, 2), "avg_ocr_ms": round((ocr_time_sum / max(ocr_frames,1))*1000, 2)}
    }

    return {"scene": scene_block, "perf": perf}
