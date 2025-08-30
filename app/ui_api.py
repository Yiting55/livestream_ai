# app/ui_api.py
"""
UI-facing helpers for language analysis.

- run_language_analysis(video_path) -> dict (bundle)
- get_topline_scores(bundle)        -> {accuracy, clarity, persuasion}
- get_aux_signals(bundle)           -> {wpm, filler_rate, (optional *_raw)}
- get_interaction_signals(bundle)   -> {question_ratio, cta_hits, reply_rate, comments_per_min, interaction_score}
- get_timeline(bundle)              -> [ {t, comments, cta, questions}, ... ]
- get_highlights(bundle)            -> [ {start, end, reason}, ... ]
- get_compliance_score(bundle)      -> float
- get_flags(bundle)                 -> {hits, terms, highlights}
- get_debug_info(bundle)            -> debug dict
- make_mock_bundle()                -> a realistic fake bundle for UI prototyping
- save_bundle_json / load_bundle_json
"""

from __future__ import annotations
from functools import lru_cache
from typing import Dict, Any, List
import json

# 依赖你的核心分析（已在 text_language.py 中实现）
from text_language import analyze_language


# --------------------------- 主入口 ---------------------------

@lru_cache(maxsize=8)
def run_language_analysis(video_path: str) -> Dict[str, Any]:
    """执行分析并返回完整 bundle。带简单缓存，避免同一路径重复计算。"""
    res = analyze_language(video_path)
    return _normalize_bundle(res)


# --------------------------- Getter：UI直接可用 ---------------------------

def get_topline_scores(bundle: Dict[str, Any]) -> Dict[str, float]:
    """三大主分（雷达图/大卡片）"""
    ls = bundle.get("lang_scores", {}) or {}
    return {
        "accuracy":   float(ls.get("accuracy", 0.0)),
        "clarity":    float(ls.get("clarity", 0.0)),
        "persuasion": float(ls.get("persuasion", 0.0)),
    }

def get_aux_signals(bundle: Dict[str, Any]) -> Dict[str, float]:
    """辅助指标（小卡片/提示）：语速、口头禅；若有 *_raw 也一起返回（UI可忽略）"""
    ls = bundle.get("lang_scores", {}) or {}
    out = {
        "wpm":         float(ls.get("wpm", 0.0)),
        "filler_rate": float(ls.get("filler_rate", 0.0)),
    }
    for k in ("accuracy_raw", "clarity_raw", "persuasion_raw"):
        if k in ls:
            out[k] = float(ls[k])
    return out

def get_interaction_signals(bundle: Dict[str, Any]) -> Dict[str, float]:
    """互动模块的小指标 + 互动分"""
    li  = bundle.get("lang_interaction", {}) or {}
    sig = li.get("signals", {}) or {}
    return {
        "question_ratio":   float(sig.get("question_ratio", 0.0)),
        "cta_hits":         float(sig.get("cta_hits", 0.0)),
        "reply_rate":       float(sig.get("reply_rate", 0.0)),
        "comments_per_min": float(sig.get("comments_per_min", 0.0)),
        "interaction_score": float(li.get("score", 0.0)),
    }

def get_timeline(bundle: Dict[str, Any]) -> List[Dict[str, float]]:
    """时间线（每 10 秒）：画柱状/折线/热力图"""
    li = bundle.get("lang_interaction", {}) or {}
    return list(li.get("timeline", []) or [])

def get_highlights(bundle: Dict[str, Any]) -> List[Dict[str, float]]:
    """互动高峰片段，用于时间轴标记"""
    li = bundle.get("lang_interaction", {}) or {}
    return list(li.get("highlights", []) or [])

def get_compliance_score(bundle: Dict[str, Any]) -> float:
    """合规分（越高越合规）"""
    le = bundle.get("lang_exaggeration", {}) or {}
    return float(le.get("score", 0.0))

def get_flags(bundle: Dict[str, Any]) -> Dict[str, Any]:
    """合规模块：命中次数/词条/高亮片段"""
    le  = bundle.get("lang_exaggeration", {}) or {}
    sig = le.get("signals", {}) or {}
    return {
        "hits":       int(sig.get("exaggeration_hits", 0)),
        "terms":      list(sig.get("terms", []) or []),
        "highlights": list(le.get("highlights", []) or []),
    }

def get_debug_info(bundle: Dict[str, Any]) -> Dict[str, Any]:
    """调试信息（可放到折叠面板）"""
    return bundle.get("debug", {}) or {}


# --------------------------- Mock & 持久化 ---------------------------

def make_mock_bundle() -> Dict[str, Any]:
    """给 UI 同学用的模拟结果，无须跑ASR/视频"""
    return _normalize_bundle({
        "lang_interaction": {
            "score": 74.2,
            "signals": {"comments_per_min": 0.0, "question_ratio": 0.18, "cta_hits": 6, "reply_rate": 0.42},
            "timeline": [
                {"t": 10.0, "comments": 0, "cta": 1, "questions": 0},
                {"t": 20.0, "comments": 0, "cta": 2, "questions": 1},
                {"t": 30.0, "comments": 0, "cta": 1, "questions": 1},
                {"t": 40.0, "comments": 0, "cta": 2, "questions": 0},
            ],
            "highlights": [{"start": 20.0, "end": 30.0, "reason": "CTA and questions peak"}],
        },
        "lang_exaggeration": {
            "score": 91.0,
            "signals": {
                "exaggeration_hits": 1,
                "terms": ["cheapest ever"],
                "negation_exempted": 0,
                "category_overrides": 0,
            },
            "highlights": [{"start": 120.0, "end": 125.0, "term": "cheapest ever"}],
        },
        "lang_scores": {
            "accuracy": 82.3, "clarity": 67.9, "persuasion": 85.1,
            "wpm": 142.0, "filler_rate": 0.11,
            "accuracy_raw": 60.0, "clarity_raw": 50.0, "persuasion_raw": 62.0,
        },
        "debug": {"backend": "faster", "ffmpeg_available": True, "segments_count": 58, "used_fallback_audio": False, "error": ""},
    })

def save_bundle_json(bundle: Dict[str, Any], path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(bundle, f, ensure_ascii=False, indent=2)

def load_bundle_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return _normalize_bundle(json.load(f))


# --------------------------- 内部：结果补全 ---------------------------

def _normalize_bundle(res: Dict[str, Any]) -> Dict[str, Any]:
    """补全所有预期字段，避免 UI 写大量空值判断。"""
    li = res.get("lang_interaction", {}) or {}
    le = res.get("lang_exaggeration", {}) or {}
    ls = res.get("lang_scores", {}) or {}
    dbg = res.get("debug", {}) or {}

    li.setdefault("score", 0.0)
    li.setdefault("signals", {})
    li.setdefault("timeline", [])
    li.setdefault("highlights", [])
    sig_i = li["signals"]
    sig_i.setdefault("comments_per_min", 0.0)
    sig_i.setdefault("question_ratio", 0.0)
    sig_i.setdefault("cta_hits", 0)
    sig_i.setdefault("reply_rate", 0.0)

    le.setdefault("score", 0.0)
    le.setdefault("signals", {})
    le.setdefault("highlights", [])
    sig_e = le["signals"]
    sig_e.setdefault("exaggeration_hits", 0)
    sig_e.setdefault("terms", [])
    sig_e.setdefault("negation_exempted", 0)
    sig_e.setdefault("category_overrides", 0)

    ls.setdefault("accuracy", 0.0)
    ls.setdefault("clarity", 0.0)
    ls.setdefault("persuasion", 0.0)
    ls.setdefault("wpm", 0.0)
    ls.setdefault("filler_rate", 0.0)

    out = {
        "lang_interaction": li,
        "lang_exaggeration": le,
        "lang_scores": ls,
        "debug": dbg,
    }
    return out
