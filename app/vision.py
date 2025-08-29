import cv2
import numpy as np

def average_brightness(video_path: str, sample_fps: int = 1) -> float:
    """
    采样读取视频帧（默认1fps），计算全视频平均亮度（0~255）。
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError("无法打开视频")

    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    step = int(max(fps // sample_fps, 1))

    frame_idx = 0
    vals = []
    while True:
        ret = cap.grab()
        if not ret:
            break
        if frame_idx % step == 0:
            ret, frame = cap.retrieve()
            if not ret:
                break
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            vals.append(float(np.mean(gray)))
        frame_idx += 1

    cap.release()
    return float(np.mean(vals)) if vals else 0.0
