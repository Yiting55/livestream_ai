from typing import Dict
from vision import average_brightness
from app_types import AnalyzeResult  # 仅作类型提示；不想用可删

def analyze_video(video_path: str) -> Dict:
    """
    分析汇总入口：当前仅做亮度示例。
    后续可在这里串联：饱和度/ASR/NLP/互动/5维打分/雷达图数据等。
    """
    avg_bri = average_brightness(video_path)
    bri_score = _score_brightness(avg_bri)

    result: AnalyzeResult = {
        "avg_brightness": avg_bri,
        "brightness_score": bri_score,
        # 预留结构位，方便后续扩展
        # "dimensions": {...}, "lqi": ..., "tips": [...]
    }
    return result

def _score_brightness(avg_bri: float) -> float:
    """
    简易亮度评分：假设 60~200 属于较佳区间，线性映射到 50~100，出界衰减。
    """
    def clamp(x, lo, hi): return max(lo, min(hi, x))
    def map_linear(x, a, b, A, B):
        if b == a: return A
        t = (x - a) / (b - a)
        return A + t * (B - A)

    base = map_linear(avg_bri, 60, 200, 50, 100)
    return clamp(base, 0, 100)
