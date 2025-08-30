from __future__ import annotations
from typing import Optional, Tuple
import cv2
import numpy as np
import mediapipe as mp

class FaceLocator:
    def __init__(self, min_conf: float = 0.5, model_selection: int = 0, margin: float = 0.35):
        self.detector = mp.solutions.face_detection.FaceDetection(
            model_selection=model_selection, min_detection_confidence=min_conf
        )
        self.margin = margin

    def locate(self, frame_bgr) -> Optional[Tuple[Tuple[int,int,int,int], Tuple[float,float], float]]:
        h, w = frame_bgr.shape[:2]
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        res = self.detector.process(rgb)
        if not res.detections:
            return None

        best = None; best_score = 0.0
        for d in res.detections:
            bb = d.location_data.relative_bounding_box
            x = max(0, int(bb.xmin * w)); y = max(0, int(bb.ymin * h))
            ww = max(1, int(bb.width * w)); hh = max(1, int(bb.height * h))
            score = float(ww * hh) * float(d.score[0] if d.score else 1.0)
            if score > best_score:
                best_score = score; best = (x, y, ww, hh)

        if best is None:
            return None

        x, y, ww, hh = best
        cx, cy = x + ww / 2.0, y + hh / 2.0
        m = self.margin
        W2, H2 = int(ww * (1 + m)), int(hh * (1 + m))
        x2 = max(0, int(cx - W2 / 2)); y2 = max(0, int(cy - H2 / 2))
        x2e = min(w, x2 + W2); y2e = min(h, y2 + H2)
        roi = (x2, y2, x2e - x2, y2e - y2)
        center = (float(cx), float(cy))
        face_size = float(max(ww, hh))
        return roi, center, face_size