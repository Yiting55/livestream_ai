from typing import Dict
from text_language import analyze_language  

def analyze_video(video_path: str) -> Dict:
    lang = analyze_language(video_path)
    result: Dict = {
        "lang_interaction": lang.get("lang_interaction"),
        "lang_exaggeration": lang.get("lang_exaggeration"),
        "lang_scores": lang.get("lang_scores"),
    }
    return result
