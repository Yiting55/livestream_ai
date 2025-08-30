## Public API (same-process)

### analyze_scene_from_upload(file, filename, *, brand_keywords=None, config=SceneConfig()) -> dict
### analyze_video(video_path, *, brand_keywords=None, config=SceneConfig()) -> dict

**Return JSON**
{
  "scene": {
    "score": 0..100,
    "signals": {
      "brightness_mean": float,
      "contrast_bw": float,
      "sharpness_varlap": float,
      "saturation_mean": float,
      "color_cast": float,
      "logo_visible_ratio": float,
      "logo_area_mean": float
    },
    "timeline": [ {"t": 秒, "v": V亮度, "s": S饱和度, "varlap": 清晰度, "logo": bool, "text_area": 文本面积占比} ],
    "highlights": [ {"start": 秒, "end": 秒, "reason": "画面偏暗/偏虚/无露出"} ]
  },
  "perf": {  # optional diagnostics
    "video": {"fps": float, "frames": int, "duration_s": float},
    "sampling": {"sample_fps": float, "frames_sampled": int, "ocr_every_s": float, "ocr_attempts": int, "ocr_hits": int},
    "timing": {"total_s": float, "avg_per_frame_ms": float, "avg_ocr_ms": float}
  }
}

**Errors**
- Raises RuntimeError if video cannot be opened/decoded.
- Raises TypeError if `file` is neither bytes nor file-like.
