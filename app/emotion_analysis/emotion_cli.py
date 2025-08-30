from __future__ import annotations
import argparse, json
from .emotion_analysis import analyze_emotion
from .emotion_config import EmotionConfig

parser = argparse.ArgumentParser(description="Emotion & Energy Analysis CLI")
parser.add_argument("video", help="Path to video file")
parser.add_argument("--sample-fps", type=float, default=None, help="Override sample fps")
parser.add_argument("--smooth", type=float, default=None, help="Smooth window seconds")

if __name__ == "__main__":
    args = parser.parse_args()
    cfg = EmotionConfig()
    if args.sample_fps is not None: cfg.sample_fps = args.sample_fps
    if args.smooth is not None: cfg.smooth_window_s = args.smooth

    out = analyze_emotion(args.video, config=cfg)

    perf = out.get("perf", {})
    video = perf.get("video", {})
    samp  = perf.get("sampling", {})
    time  = perf.get("timing", {})

    print("\n== Performance Summary ==")
    print(f"Duration: {video.get('duration_s','?')}s  | FPS: {video.get('fps','?')}  | Frames: {video.get('frames','?')}")
    print(f"Sampling: {samp.get('sample_fps','?')} Hz -> {samp.get('frames_sampled','?')} frames")
    print(f"Timing: total {time.get('total_s','?')} s\n")

    print(json.dumps({"emotion": out.get("emotion", {})}, ensure_ascii=False, indent=2))
