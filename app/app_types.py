from typing import TypedDict

class AnalyzeResult(TypedDict, total=False):
    avg_brightness: float
    brightness_score: float
    # lqi: float
    # dimensions: dict
    # tips: list[str]
