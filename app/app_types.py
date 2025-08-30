from typing import TypedDict
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class Utterance:
    start: float
    end: float
    text: str

@dataclass
class TextMetrics:
    wpm: float
    filler_rate: float
    cta_hits: int
    hyperbole_hits: int
    sentence_len_mean: float
    sentence_len_std: float
    utterances: List[Utterance]

@dataclass
class VideoMetrics:
    cuts: int
    shake_var: float
    brightness_mean: float
    brightness_std: float
    over_exposure_ratio: float
    product_visibility: float

@dataclass
class AnalysisBundle:
    text: TextMetrics
    video: VideoMetrics
    meta: Dict[str, Any]


class AnalyzeResult(TypedDict, total=False):
    avg_brightness: float
    brightness_score: float
