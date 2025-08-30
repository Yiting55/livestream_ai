# app/analyzer.py
from typing import Dict
from text_language import analyze_language  # 语言分析模块

def analyze_video(video_path: str) -> Dict:
    """
    分析汇总入口：仅语言分析（英文）。
    输出字段：
      - lang_interaction
      - lang_exaggeration
      - lang_scores {accuracy, clarity, persuasion, wpm, filler_rate}
    """
    lang = analyze_language(video_path)
    result: Dict = {
        "lang_interaction": lang.get("lang_interaction"),
        "lang_exaggeration": lang.get("lang_exaggeration"),
        "lang_scores": lang.get("lang_scores"),
    }
    return result
