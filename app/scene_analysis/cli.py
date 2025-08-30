from __future__ import annotations
import json, sys, argparse
from .scene_analysis import analyze_video
from .scene_config import SceneConfig

parser = argparse.ArgumentParser(description="Scene Analysis CLI (OpenCV + Tesseract OCR)")
parser.add_argument("video", help="Path to video file")
parser.add_argument("keywords", nargs="*", help="Brand keywords (optional)")
parser.add_argument("--no-autoscale", action="store_true", help="Disable duration-based autoscaling")
parser.add_argument("--sample-fps", type=float, default=None, help="Override sample_fps (Hz)")
parser.add_argument("--ocr-every", type=float, default=None, help="Override OCR interval (seconds)")
parser.add_argument("--lang", type=str, default=None, help="Tesseract language, e.g. eng or chi_sim+eng")
parser.add_argument("--json-out", type=str, default=None, help="Write full JSON result to a file")

if __name__ == "__main__":
    args = parser.parse_args()
    cfg = SceneConfig()
    if args.lang: cfg.tesseract_lang = args.lang
    if args.sample_fps is not None: cfg.sample_fps = args.sample_fps
    if args.ocr_every is not None: cfg.ocr_every_s = args.ocr_every
    if args.no_autoscale: cfg.autoscale_enabled = False

    out = analyze_video(args.video, brand_keywords=set(args.keywords) if args.keywords else None, config=cfg)

    # —— 性能概要打印 ——
    perf = out.get("perf", {})
    video = perf.get("video", {})
    samp  = perf.get("sampling", {})
    time  = perf.get("timing", {})

    print("== Performance Summary ==")
    print(f"Duration: {video.get('duration_s','?')}s  | FPS: {video.get('fps','?')}  | Frames: {video.get('frames','?')}")
    print(f"Sampling: {samp.get('sample_fps','?')} Hz -> {samp.get('frames_sampled','?')} frames")
    print(f"OCR: every {samp.get('ocr_every_s','?')} s  | attempts: {samp.get('ocr_attempts','?')}  | hits: {samp.get('ocr_hits','?')}")
    print(f"Timing: total {time.get('total_s','?')} s  | avg/frame {time.get('avg_per_frame_ms','?')} ms  | avg OCR {time.get('avg_ocr_ms','?')} ms")

    # —— 结果输出：默认打印 scene JSON；可选写入文件 ——
    scene_only = {"scene": out.get("scene", {})}
    print(json.dumps(scene_only, ensure_ascii=False, indent=2))

    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)
        print(f"Saved full JSON (with perf) to: {args.json_out}")
