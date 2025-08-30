# app/ui_api.py
"""
UI-facing helpers for language (A) plus optional scene/emotion modules.

Language (A)
- run_language_analysis(video_path) -> dict
- get_topline_scores(bundle)        -> {accuracy, clarity, persuasion}
- get_aux_signals(bundle)           -> {wpm, filler_rate, ...}
- get_interaction_signals(bundle)   -> {..., interaction_score}
- get_timeline(bundle)              -> [ {t, comments, cta, questions}, ... ]
- get_highlights(bundle)            -> [ {start, end, reason}, ... ]
- get_compliance_score(bundle)      -> float
- get_flags(bundle)                 -> {hits, terms, highlights}
- get_debug_info(bundle)            -> dict
- save_bundle_json / load_bundle_json

Scene (OCR / Brand)
- run_scene_analysis(uploaded_file, tesseract_lang="chi_sim+eng", brand_keywords=None) -> dict
- summarize_scene(scene_dict) -> (summary_markdown, moments)

Emotion
- run_emotion_from_upload(uploaded_file, config=None) -> dict
"""

from __future__ import annotations
from functools import lru_cache
from typing import Dict, Any, List, Tuple
import json
import tempfile
import os
import plotly.graph_objects as go

from text_language import analyze_language


# --------------------------- Language ---------------------------

@lru_cache(maxsize=8)
def run_language_analysis(video_path: str) -> Dict[str, Any]:
    res = analyze_language(video_path)
    return _normalize_bundle(res)

def get_topline_scores(bundle: Dict[str, Any]) -> Dict[str, float]:
    ls = bundle.get("lang_scores", {}) or {}
    return {
        "accuracy":   float(ls.get("accuracy", 0.0)),
        "clarity":    float(ls.get("clarity", 0.0)),
        "persuasion": float(ls.get("persuasion", 0.0)),
    }

def get_aux_signals(bundle: Dict[str, Any]) -> Dict[str, float]:
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
    li  = bundle.get("lang_interaction", {}) or {}
    sig = li.get("signals", {}) or {}
    return {
        "question_ratio":    float(sig.get("question_ratio", 0.0)),
        "cta_hits":          float(sig.get("cta_hits", 0.0)),
        "reply_rate":        float(sig.get("reply_rate", 0.0)),
        "comments_per_min":  float(sig.get("comments_per_min", 0.0)),
        "interaction_score": float(li.get("score", 0.0)),
    }

def get_timeline(bundle: Dict[str, Any]) -> List[Dict[str, float]]:
    li = bundle.get("lang_interaction", {}) or {}
    return list(li.get("timeline", []) or [])

def get_highlights(bundle: Dict[str, Any]) -> List[Dict[str, float]]:
    li = bundle.get("lang_interaction", {}) or {}
    return list(li.get("highlights", []) or [])

def get_compliance_score(bundle: Dict[str, Any]) -> float:
    le = bundle.get("lang_exaggeration", {}) or {}
    return float(le.get("score", 0.0))

def get_flags(bundle: Dict[str, Any]) -> Dict[str, Any]:
    le  = bundle.get("lang_exaggeration", {}) or {}
    sig = le.get("signals", {}) or {}
    return {
        "hits":       int(sig.get("exaggeration_hits", 0)),
        "terms":      list(sig.get("terms", []) or []),
        "highlights": list(le.get("highlights", []) or []),
    }

def get_debug_info(bundle: Dict[str, Any]) -> Dict[str, Any]:
    return bundle.get("debug", {}) or {}

def save_bundle_json(bundle: Dict[str, Any], path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(bundle, f, ensure_ascii=False, indent=2)

def load_bundle_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return _normalize_bundle(json.load(f))

def _normalize_bundle(res: Dict[str, Any]) -> Dict[str, Any]:
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

    return {
        "lang_interaction": li,
        "lang_exaggeration": le,
        "lang_scores": ls,
        "debug": dbg,
    }


# --------------------------- Scene (OCR / Brand) ---------------------------

def _compress_seconds_to_ranges(seconds: List[int]) -> List[Tuple[int, int]]:
    if not seconds:
        return []
    seconds = sorted(set(int(s) for s in seconds))
    ranges: List[Tuple[int, int]] = []
    start = prev = seconds[0]
    for s in seconds[1:]:
        if s == prev + 1:
            prev = s
        else:
            ranges.append((start, prev))
            start = prev = s
    ranges.append((start, prev))
    return ranges

def run_scene_analysis(uploaded_file, tesseract_lang: str = "chi_sim+eng", brand_keywords: set | None = None) -> Dict[str, Any]:
    from scene_analysis import analyze_scene_from_upload, SceneConfig
    cfg = SceneConfig(tesseract_lang=tesseract_lang)

    '''if hasattr(uploaded_file, "seek"):
        try:
            uploaded_file.seek(0)
        except Exception:
            pass'''

    out = analyze_scene_from_upload(
        uploaded_file,
        getattr(uploaded_file, "name", "upload.mp4"),
        config=cfg,
        brand_keywords=brand_keywords or set()
    )
    return out

def summarize_scene(scene_dict: Dict[str, Any]) -> Tuple[str, List[Dict[str, Any]]]:
    score = float(scene_dict.get("score", 0))
    sig   = scene_dict.get("signals", {}) or {}

    summary_md: List[str] = []
    summary_md.append("### ✅ Scene Summary")
    summary_md.append(f"- **Visual Score:** **{score:.1f}** / 100")
    if "brightness_mean" in sig:    summary_md.append(f"- Brightness (mean): **{sig['brightness_mean']:.1f}**")
    if "contrast_bw" in sig:        summary_md.append(f"- Contrast (B/W): **{sig['contrast_bw']:.1f}**")
    if "sharpness_varlap" in sig:   summary_md.append(f"- Sharpness (VarLap): **{sig['sharpness_varlap']:.1f}**")
    if "saturation_mean" in sig:    summary_md.append(f"- Saturation (mean): **{sig['saturation_mean']:.1f}**")
    if "color_cast" in sig:         summary_md.append(f"- Color Cast: **{sig['color_cast']:.1f}**")
    if "logo_visible_ratio" in sig: summary_md.append(f"- Logo Visible Ratio: **{sig['logo_visible_ratio']:.3f}**")
    if "logo_area_mean" in sig:     summary_md.append(f"- Avg Logo Area: **{sig['logo_area_mean']:.1f}**")

    tl = scene_dict.get("timeline", []) or []
    ocr_seconds  = [int(row.get("t", 0)) for row in tl if float(row.get("text_area", 0) or 0) > 0]
    logo_seconds = [int(row.get("t", 0)) for row in tl if bool(row.get("logo", False))]

    ocr_ranges  = _compress_seconds_to_ranges(ocr_seconds)
    logo_ranges = _compress_seconds_to_ranges(logo_seconds)

    moments: List[Dict[str, Any]] = []
    for a, b in ocr_ranges:
        moments.append({"type": "OCR text", "start_s": a, "end_s": b})
    for a, b in logo_ranges:
        moments.append({"type": "Brand/Logo", "start_s": a, "end_s": b})

    if not moments:
        summary_md.append("> No OCR text or brand/logo detected in the timeline.")

    return "\n".join(summary_md), moments


# --------------------------- Emotion ---------------------------

def run_emotion_from_upload(uploaded_file, config=None) -> Dict[str, Any]:
    from emotion_analysis import analyze_emotion, EmotionConfig
    cfg = EmotionConfig()

    if hasattr(uploaded_file, "seek"):
        try:
            uploaded_file.seek(0)
        except Exception:
            pass

    with tempfile.TemporaryDirectory(prefix="emo_") as tmpd:
        tmp_path = os.path.join(tmpd, "video_for_emotion.mp4")
        with open(tmp_path, "wb") as f:
            f.write(uploaded_file.read())

        result = analyze_emotion(tmp_path, cfg)

    return result

def summarize_emotion(emotion_result: Dict[str, Any]) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Summarize emotion analysis output into a short Markdown report and key moments.
    Expects either:
      { "emotion": { "score": ..., "signals": {...}, "timeline": [...], "highlights": [...] }, "perf": {...} }
    or just the inner emotion dict itself.

    Returns:
      summary_md (str), moments (List[{"label": str, "start_s": int, "end_s": int}])
    """
    # Root: allow both {"emotion": {...}} or {...}
    root = emotion_result.get("emotion", emotion_result) or {}

    score    = root.get("score", None)
    signals  = root.get("signals", {}) or {}
    timeline = root.get("timeline", []) or []
    hi_input = root.get("highlights", []) or []

    # Safe casts
    val_mean = float(signals.get("valence_mean", 0.0))
    eng_mean = float(signals.get("energy_mean", 0.0))

    # --- Heuristics for "emotional seconds"
    # Thresholds are relative to means but also clamp to sensible bounds.
    # High = clearly positive/excited; Smile is a strong visible cue.
    VALENCE_HI = max(0.75, val_mean + 0.20)
    ENERGY_HI  = max(0.75, eng_mean + 0.20)
    SMILE_HI   = 0.90

    # Optional "low" band (useful for contrast)
    VALENCE_LO = min(0.35, val_mean - 0.25)

    # Collect seconds by category
    hi_valence_secs: List[int] = []
    hi_energy_secs:  List[int] = []
    big_smile_secs:  List[int] = []
    low_valence_secs: List[int] = []

    # Keep top-3 peaks for quick callouts
    top_valence: List[Tuple[int, float]] = []
    top_energy:  List[Tuple[int, float]] = []

    for row in timeline:
        t = int(row.get("t", 0))
        v = float(row.get("valence", row.get("emotions", {}).get("valence", 0.0) if isinstance(row.get("emotions"), dict) else row.get("valence", 0.0)))
        e = float(row.get("energy", 0.0))
        s = float(row.get("smile", 0.0))

        if v >= VALENCE_HI:
            hi_valence_secs.append(t)
        if e >= ENERGY_HI:
            hi_energy_secs.append(t)
        if s >= SMILE_HI:
            big_smile_secs.append(t)
        if v <= VALENCE_LO:
            low_valence_secs.append(t)

        top_valence.append((t, v))
        top_energy.append((t, e))

    # Sort peaks by magnitude and keep top 3 unique seconds
    top_valence = [t for (t, _v) in sorted(top_valence, key=lambda kv: kv[1], reverse=True)[:3]]
    top_energy  = [t for (t, _e) in sorted(top_energy,  key=lambda kv: kv[1], reverse=True)[:3]]

    # Compress contiguous seconds into ranges
    def _compress_seconds_to_ranges(seconds: List[int]) -> List[Tuple[int, int]]:
        if not seconds:
            return []
        seconds = sorted(set(int(s) for s in seconds))
        ranges: List[Tuple[int, int]] = []
        start = prev = seconds[0]
        for s in seconds[1:]:
            if s == prev + 1:
                prev = s
            else:
                ranges.append((start, prev))
                start = prev = s
        ranges.append((start, prev))
        return ranges

    v_ranges = _compress_seconds_to_ranges(hi_valence_secs)
    e_ranges = _compress_seconds_to_ranges(hi_energy_secs)
    s_ranges = _compress_seconds_to_ranges(big_smile_secs)
    lo_ranges = _compress_seconds_to_ranges(low_valence_secs)

    # Build summary markdown
    summary_md: List[str] = []
    summary_md.append("### ✅ Emotion Summary")

    if score is not None:
        try:
            summary_md.append(f"- **Emotion Score:** **{float(score):.1f}** / 100")
        except Exception:
            summary_md.append(f"- **Emotion Score:** **{score}**")

    summary_md.append(f"- Valence mean: **{val_mean:.3f}**  |  Energy mean: **{eng_mean:.3f}**")
    summary_md.append(f"- High thresholds → Valence ≥ **{VALENCE_HI:.2f}**, Energy ≥ **{ENERGY_HI:.2f}**, Smile ≥ **{SMILE_HI:.2f}**")

    def _fmt_ranges(tag: str, rs: List[Tuple[int, int]]) -> None:
        if not rs:
            return
        parts = []
        for a, b in rs:
            parts.append(f"{a}s" if a == b else f"{a}–{b}s")
        summary_md.append(f"- {tag}: " + ", ".join(parts))

    _fmt_ranges("High valence", v_ranges)
    _fmt_ranges("High energy", e_ranges)
    _fmt_ranges("Big smiles", s_ranges)

    if lo_ranges:
        _fmt_ranges("Low-valence dips", lo_ranges)

    # Quick peak callouts
    if top_valence:
        summary_md.append(f"- 📈 Top valence seconds: {', '.join(str(x)+'s' for x in top_valence)}")
    if top_energy:
        summary_md.append(f"- ⚡ Top energy seconds: {', '.join(str(x)+'s' for x in top_energy)}")

    # If nothing really stood out:
    if not (v_ranges or e_ranges or s_ranges or hi_input):
        summary_md.append("> No standout emotional peaks detected — performance looks steady.")

    # Build moments list (unified, labeled)
    moments: List[Dict[str, Any]] = []

    for a, b in v_ranges:
        moments.append({"label": "High valence", "start_s": a, "end_s": b})
    for a, b in e_ranges:
        moments.append({"label": "High energy", "start_s": a, "end_s": b})
    for a, b in s_ranges:
        moments.append({"label": "Big smiles", "start_s": a, "end_s": b})

    # Include model-provided highlights (keep their label/reason if present)
    for h in hi_input:
        start_s = int(h.get("start") or h.get("start_s") or h.get("t") or 0)
        end_s   = int(h.get("end")   or h.get("end_s")   or start_s)
        label   = str(h.get("label") or h.get("reason") or h.get("emotion") or "highlight")
        moments.append({"label": label, "start_s": start_s, "end_s": end_s})

    return "\n".join(summary_md), moments

def build_emotion_chart(emotion_result: Dict[str, Any]) -> go.Figure:
    """Return a Plotly figure visualizing valence/energy timeline with means & thresholds."""
    root = emotion_result.get("emotion", emotion_result) or {}
    signals  = root.get("signals", {}) or {}
    timeline = root.get("timeline", []) or []

    # Means and adaptive thresholds
    val_mean = float(signals.get("valence_mean", 0.0))
    eng_mean = float(signals.get("energy_mean", 0.0))
    VALENCE_HI = max(0.75, val_mean + 0.20)
    ENERGY_HI  = max(0.75, eng_mean + 0.20)

    # Extract series
    t: List[int] = []
    val: List[float] = []
    eng: List[float] = []

    for row in timeline:
        t.append(int(row.get("t", 0)))
        val.append(float(row.get("valence", 0.0)))
        eng.append(float(row.get("energy", 0.0)))

    fig = go.Figure()
    if t:
        fig.add_trace(go.Scatter(x=t, y=val, name="Valence", mode="lines+markers"))
        fig.add_trace(go.Scatter(x=t, y=eng, name="Energy",  mode="lines+markers"))

    # Horizontal reference lines (means & thresholds)
    shapes = []
    annotations = []

    def _hline(y, text, dash="dot"):
        shapes.append(dict(
            type="line", xref="paper", x0=0, x1=1,
            yref="y", y0=y, y1=y,
            line=dict(dash=dash, width=1)
        ))
        annotations.append(dict(
            x=1.005, y=y, xref="paper", yref="y",
            text=text, showarrow=False,
            xanchor="left", font=dict(size=11)
        ))

    _hline(val_mean,   f"Valence mean {val_mean:.2f}", dash="dot")
    _hline(eng_mean,   f"Energy mean {eng_mean:.2f}",  dash="dot")
    _hline(VALENCE_HI, f"Valence high {VALENCE_HI:.2f}", dash="dash")
    _hline(ENERGY_HI,  f"Energy high {ENERGY_HI:.2f}",   dash="dash")

    score = root.get("score")
    title = "Emotion Timeline"
    if score is not None:
        try:
            title = f"Emotion Timeline — Score: {float(score):.1f}/100"
        except Exception:
            title = f"Emotion Timeline — Score: {score}/100"

    fig.update_layout(
        title=title,
        xaxis_title="Time (s)",
        yaxis_title="Intensity (0–1)",
        yaxis=dict(range=[0, 1], tick0=0, dtick=0.1),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=60, r=120, l=50, b=50),
        shapes=shapes,
        annotations=annotations,
    )
    return fig