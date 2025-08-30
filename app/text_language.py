from __future__ import annotations
import math, re, os, tempfile, shutil
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from pathlib import Path

# ===================== Tunable Parameters =====================
# ---- Baseline remap for headline scores (start from 60) ----
BASELINE     = 60.0   # baseline score
MAX_BONUS    = 40.0   # max above baseline -> 100
MAX_PENALTY  = 20.0   # max below baseline -> 40

# ---- Accuracy (independent positive-evidence score) ----
ACC_POS_SCALE = 6.0     # larger -> slower saturation for positive signals

# ---- Compliance (exaggeration) exponential decay ----
ACC_EXP_K     = 0.35    # compliance = 100 * exp(-k * hits)

# ---- Clarity ----
CL_FILLER_COEF = 40.0   # penalty slope for filler_rate (per 1.0 rate)
CL_WPM_TARGET  = 150.0  # target speaking rate (wpm)
CL_WPM_TOL     = 60.0   # tolerance; larger -> wider bell
CL_WEIGHTS     = (0.6, 0.4)  # (wpm_weight, filler_weight)

# ---- Persuasion (friendlier curve) ----
P_MODE      = "saturating"  # "saturating" or "piecewise"
P_CTA_SCALE = 2.5           # smaller -> faster saturation

# Weighted hits bonuses (convert extra signals to CTA-equivalents)
BONUS_DEAL     = 0.5  # each deal word counts as +0.5 CTA
BONUS_URGENCY  = 0.5  # each urgency word counts as +0.5 CTA
BONUS_STRUCTURE= 1.0  # CTA + pain/benefit co-occurrence
BONUS_EVIDENCE = 1.0  # CTA + price/units/numbers co-occurrence

# ---- Interaction (timeline window & Q->A window) ----
WINDOW_SECONDS   = 10.0
QA_PAIR_MAX_GAP  = 15.0

# Debug diagnostics
DEBUG_DIAG = True
# ===============================================================

# ---------- Optional ASR backends ----------
_BACKEND = None
try:
    from faster_whisper import WhisperModel
    _BACKEND = "faster"
except Exception:
    try:
        import whisper  # openai-whisper
        _BACKEND = "openai"
    except Exception:
        _BACKEND = None  # no ASR available; return zeros

# ---------- Lexicons (extend freely) ----------
# CTA core + platform actions + urgency + deals
CTA_TERMS = [
    # direct CTA
    "buy now", "shop now", "order now", "get yours now", "grab it now", "grab yours",
    "add to cart", "add it to your cart",
    "tap the link", "click the link", "hit the link",
    "check out", "checkout now",
    "use the coupon", "apply coupon", "redeem", "claim offer",
    "follow us", "like and share", "subscribe", "turn on notifications",
]

# Deals / incentives (counted as weighted bonus)
DEAL_TERMS = [
    "flash sale", "bundle deal", "bundle", "special offer", "exclusive deal",
    "free shipping", "buy one get one", "bogo", "gift with purchase",
    "discount", "coupon", "promo code", "use code", "save", "save up to",
]

# Urgency / scarcity (counted as weighted bonus)
URGENCY_TERMS = [
    "limited time", "last chance", "only today", "today only", "act fast",
    "while supplies last", "limited stock", "low stock", "now or never",
    "don’t miss out", "dont miss out",
]

# Regex variants for common spoken CTAs
CTA_REGEX = [
    r"add\s+(?:it\s+to\s+)?(?:your\s+)?cart",
    r"(?:tap|click|hit)\s+(?:the\s+)?link",
    r"(?:go|head)\s+to\s+checkout",
    r"(?:use|apply)\s+(?:the\s+)?(?:coupon|promo\s*code|code)",
    r"(?:buy|grab|get)\s+(?:it|yours)\s+now",
    r"(?:check)\s*out\s+now",
]

# Exaggeration / compliance
SENSITIVE_TERMS = [
    # absolute guarantees / exaggeration
    "guaranteed", "100% effective", "works every time", "permanent", "forever",
    "instant result", "immediate effect", "miracle", "magic", "secret formula",
    # medical/health claims (generic; adjust for your policy)
    "cure", "heals", "no side effects", "risk-free", "zero risk", "completely safe",
    "clinically proven", "doctor recommended", "fda approved", "no approval needed",
    # price / exclusivity
    "cheapest ever", "lowest price ever", "unbeatable price", "only available here",
    "now or never", "once in a lifetime",
]

# Fillers (clarity negative)
FILLERS_EN = [
    "um", "uh", "erm", "hmm",
    "like", "you know", "i mean", "sort of", "kind of",
    "basically", "literally", "actually", "so yeah", "well", "ok so",
    "whatever", "stuff like that", "things like that",
]

QUESTION_HEADS = {
    "what","why","how","when","where","which","who","whom","whose",
    "does","do","did","is","are","can","could","would","should",
}

# Accuracy positive-evidence lexicons (independent of compliance)
PRECISION_TERMS = [
    # specs / objective descriptions
    "size", "weight", "dimensions", "material", "ingredients",
    "specification", "specs", "warranty", "return policy",
    "expires on", "manufactured on", "shelf life",
    "includes", "what’s in the box", "whats in the box", "package contains",
    # price / discount / logistics
    "price", "original price", "discount", "coupon", "tax", "shipping",
    "msrp", "unit price", "per pack", "per unit",
]
DISCLAIMER_TERMS = [
    "results may vary", "not medical advice", "consult your doctor",
    "consult a professional", "for educational purposes",
    "for demonstration only", "subject to availability", "terms apply",
]

# Evidence pattern (numbers, units, money)
NUMERIC_UNIT_RE = re.compile(
    r"(\$?\d+(\.\d+)?\s?(ml|l|g|kg|oz|lb|inch|in|cm|mm|years?|year|months?|day|days|pack|pcs|%)|\$\d+)",
    re.IGNORECASE,
)

# Pain/benefit list (for structure bonus with CTA)
PAIN_BENEFIT = [
    "problem", "pain point", "struggle",
    "save time", "save money", "faster", "easier",
    "convenient", "comfortable", "durable",
]

_word_re = re.compile(r"[a-z0-9]+")

# ---------- Data model ----------
@dataclass
class Segment:
    start: float
    end: float
    text: str

# ---------- ASR helpers & diagnostics ----------
_asr_cache = None

def _load_asr():
    global _asr_cache
    if _asr_cache is not None:
        return _asr_cache
    if _BACKEND == "faster":
        _asr_cache = WhisperModel("base", device="cpu", compute_type="int8")
    elif _BACKEND == "openai":
        _asr_cache = whisper.load_model("base")  # type: ignore
    else:
        _asr_cache = None
    return _asr_cache

def _has_ffmpeg() -> bool:
    from shutil import which
    return which("ffmpeg") is not None

def _extract_audio_wav(video_path: str) -> Optional[str]:
    """Fallback: extract audio to wav for transcription."""
    try:
        from moviepy.editor import VideoFileClip
        tmpd = tempfile.mkdtemp(prefix="asr_audio_")
        out_wav = os.path.join(tmpd, "audio.wav")
        clip = VideoFileClip(video_path)
        if clip.audio is None:
            return None
        clip.audio.write_audiofile(out_wav, verbose=False, logger=None)
        clip.close()
        return out_wav
    except Exception:
        return None

def transcribe_to_segments(path: str, language: Optional[str] = None) -> List[Segment]:
    """
    Try direct transcription on the video; if no segments, fallback to:
      extract WAV -> transcribe.
    """
    model = _load_asr()
    segs: List[Segment] = []
    used_fallback, err_msg = False, ""

    try:
        if _BACKEND == "faster":
            gen, _info = model.transcribe(path, language=language, word_timestamps=False)  # type: ignore
            for s in gen:
                segs.append(Segment(float(s.start), float(s.end), (s.text or "").strip().lower()))
        elif _BACKEND == "openai":
            res = model.transcribe(path, language=language)  # type: ignore
            for s in res.get("segments", []):
                segs.append(Segment(float(s["start"]), float(s["end"]), str(s.get("text","")).strip().lower()))
        else:
            err_msg = "No ASR backend available."
    except Exception as e:
        err_msg = f"Direct transcribe error: {e}"

    if len(segs) == 0:
        wav = _extract_audio_wav(path)
        if wav:
            try:
                used_fallback = True
                if _BACKEND == "faster":
                    gen, _info = model.transcribe(wav, language=language, word_timestamps=False)  # type: ignore
                    for s in gen:
                        segs.append(Segment(float(s.start), float(s.end), (s.text or "").strip().lower()))
                elif _BACKEND == "openai":
                    res = model.transcribe(wav, language=language)  # type: ignore
                    for s in res.get("segments", []):
                        segs.append(Segment(float(s["start"]), float(s["end"]), str(s.get("text","")).strip().lower()))
            except Exception as e2:
                err_msg = (err_msg + " | " if err_msg else "") + f"Fallback transcribe error: {e2}"
            finally:
                try:
                    shutil.rmtree(Path(wav).parent, ignore_errors=True)
                except Exception:
                    pass

    transcribe_to_segments._last_debug = {
        "backend": _BACKEND or "none",
        "ffmpeg_available": _has_ffmpeg(),
        "segments_count": len(segs),
        "used_fallback_audio": used_fallback,
        "error": err_msg,
    }
    return segs

# ---------- Text utils ----------
def contains_any(text: str, phrases: List[str]) -> int:
    t = text.lower()
    c = 0
    for ph in phrases:
        ph = ph.lower().strip()
        if not ph:
            continue
        i = 0
        while True:
            i = t.find(ph, i)
            if i == -1:
                break
            c += 1
            i += len(ph)
    return c

def contains_any_regex(text: str, patterns: List[str]) -> int:
    c = 0
    low = text.lower()
    for pat in patterns:
        try:
            c += len(re.findall(pat, low))
        except re.error:
            pass
    return c

def is_question_like(text: str) -> bool:
    if "?" in text:
        return True
    toks = _word_re.findall(text.lower())
    return bool(toks and (toks[0] in QUESTION_HEADS))

def detect_q_and_answers(segments: List[Segment], max_gap: float = QA_PAIR_MAX_GAP) -> Tuple[int,int]:
    q_idx = [i for i,s in enumerate(segments) if is_question_like(s.text)]
    answered = 0
    for qi in q_idx:
        end_t = segments[qi].end
        j = qi + 1
        while j < len(segments) and (segments[j].start - end_t) <= max_gap:
            t = segments[j].text.lower()
            if re.search(r"\b(\d+(\.\d+)?|\$\d+)\b", t) or re.search(r"\b(yes|yeah|yep|no|nope|sure)\b", t):
                answered += 1
                break
            j += 1
    return len(q_idx), answered

def count_cta_hits_rich(text: str) -> Tuple[int, int, int]:
    """
    Returns (cta_hits, deal_hits, urg_hits) using phrases + regex variants.
    """
    low = text.lower()
    cta_hits = contains_any(low, CTA_TERMS) + contains_any_regex(low, CTA_REGEX)
    deal_hits = contains_any(low, DEAL_TERMS)
    urg_hits  = contains_any(low, URGENCY_TERMS)
    return cta_hits, deal_hits, urg_hits

def build_timeline(segments: List[Segment], window: float = WINDOW_SECONDS) -> Tuple[List[Dict], float, int]:
    if not segments:
        return [], 0.0, 0
    max_t = segments[-1].end
    bins = [{"t": (i+1)*window, "comments": 0, "cta": 0, "questions": 0} for i in range(int(math.ceil(max_t/window)))]
    q_total = 0
    cta_total = 0
    for s in segments:
        bi = min(int(s.end // window), len(bins)-1)
        if is_question_like(s.text):
            bins[bi]["questions"] += 1
            q_total += 1
        cta, _deal, _urg = count_cta_hits_rich(s.text)
        if cta:
            bins[bi]["cta"] += cta          # timeline shows pure CTA hits
            cta_total += cta
        else:
            # still count 0 increments for transparency
            cta_total += 0
    question_ratio = q_total / max(1, len(segments))
    return bins, question_ratio, cta_total

def extract_highlights(timeline: List[Dict]) -> List[Dict]:
    if not timeline:
        return []
    ctas = [x["cta"] for x in timeline]
    qs = [x["questions"] for x in timeline]
    thr_cta = max(1, int(round(sorted(ctas)[int(0.75*(len(ctas)-1))]))) if ctas else 1
    thr_q   = max(1, int(round(sorted(qs)[int(0.75*(len(qs)-1))])))   if qs   else 1
    hi = []
    for i,w in enumerate(timeline):
        if w["cta"] >= thr_cta and w["questions"] >= thr_q:
            start, end = i*WINDOW_SECONDS, (i+1)*WINDOW_SECONDS
            hi.append({"start": start, "end": end, "reason": "CTA and questions peak"})
    return hi

def count_exaggerations(segments: List[Segment]) -> Tuple[int,List[str],List[Dict]]:
    hits, terms, hl = 0, [], []
    for s in segments:
        txt = s.text.lower()
        for term in SENSITIVE_TERMS:
            cnt = contains_any(txt, [term])
            if cnt > 0:
                hits += cnt
                terms += [term]*cnt
                hl.append({"start": s.start, "end": s.end, "term": term})
    return hits, terms, hl

# ---------- Scoring helpers ----------
def remap_with_baseline(raw_score: float) -> float:
    """
    Map a 0..100 raw score to a baseline-centered range:
      raw=0   -> BASELINE - MAX_PENALTY
      raw=100 -> BASELINE + MAX_BONUS
    """
    r = max(0.0, min(100.0, float(raw_score))) / 100.0
    mapped = (BASELINE - MAX_PENALTY) + (MAX_PENALTY + MAX_BONUS) * r
    return max(0.0, min(100.0, mapped))

def score_accuracy_independent(text_all: str, segments: List[Segment]) -> float:
    """
    Accuracy (independent of compliance): more precise info -> higher score (saturating).
    score = 100 * (1 - exp(- pos / ACC_POS_SCALE))
    """
    low = text_all.lower()
    pos = 0
    for term in PRECISION_TERMS:
        pos += low.count(term.lower())
    for term in DISCLAIMER_TERMS:
        pos += low.count(term.lower())
    pos += len(NUMERIC_UNIT_RE.findall(text_all))
    score = 100.0 * (1.0 - math.exp(- float(pos) / max(1e-6, ACC_POS_SCALE)))
    return max(0.0, min(100.0, score))

def score_compliance_from_hits_exp(hits: int) -> float:
    return max(0.0, min(100.0, 100.0 * math.exp(-ACC_EXP_K * max(0, hits))))

def score_clarity_from_signals(filler_rate: float, wpm: float) -> float:
    clarity_fillers = max(0.0, min(100.0, 100.0 - CL_FILLER_COEF * max(0.0, filler_rate)))
    clarity_wpm = 100.0 * math.exp(- ((wpm - CL_WPM_TARGET) / max(1e-6, CL_WPM_TOL)) ** 2)
    w_wpm, w_fill = CL_WEIGHTS
    score = w_wpm * clarity_wpm + w_fill * clarity_fillers
    return max(0.0, min(100.0, score))

def score_persuasion_from_cta(cta_hits: int) -> float:
    h = max(0, cta_hits)
    if P_MODE == "saturating":
        return max(0.0, min(100.0, 100.0 * (1.0 - math.exp(- h / max(1e-6, P_CTA_SCALE)))))
    elif P_MODE == "piecewise":
        if h == 0:
            return 60.0
        if 1 <= h <= 3:
            return 60.0 + (88.0 - 60.0) * (h / 3.0)
        if 4 <= h <= 8:
            return 88.0 + (96.0 - 88.0) * ((h - 3) / 5.0)
        return 100.0
    else:
        return max(0.0, min(100.0, 100.0 * (1.0 - math.exp(- h / max(1e-6, P_CTA_SCALE)))))

# ---------- Public API ----------
def analyze_language(video_path: str) -> Dict:
    """
    Returns:
      - lang_interaction: {score, signals, timeline, highlights}
      - lang_exaggeration: {score, signals, highlights}   # compliance
      - lang_scores: {accuracy, clarity, persuasion, wpm, filler_rate, *_raw}
    """
    segments = transcribe_to_segments(video_path, language=None)

    # Interaction & pacing
    timeline, question_ratio, cta_hits_pure = build_timeline(segments)
    q_total, q_answered = detect_q_and_answers(segments)
    reply_rate = (q_answered / max(1, q_total)) if q_total else 0.0

    inter_base = (
        min(1.0, question_ratio * 4.0) * 0.4 +
        min(1.0, cta_hits_pure / 15.0) * 0.3 +
        min(1.0, reply_rate * 2.0) * 0.3
    )
    inter_score = max(0.0, min(100.0, 100.0 * inter_base))
    inter_json = {
        "score": round(inter_score, 1),
        "signals": {
            "comments_per_min": 0.0,                 # no comments available
            "question_ratio": float(round(question_ratio, 3)),
            "cta_hits": int(cta_hits_pure),          # pure CTA only (timeline consistency)
            "reply_rate": float(round(reply_rate, 3)),
        },
        "timeline": timeline,
        "highlights": extract_highlights(timeline),
    }

    # Compliance (exaggeration)
    ex_hits, ex_terms, ex_hi = count_exaggerations(segments)
    compliance_raw = score_compliance_from_hits_exp(ex_hits)
    ex_json = {
        "score": round(compliance_raw, 1),
        "signals": {
            "exaggeration_hits": int(ex_hits),
            "terms": ex_terms,
            "negation_exempted": 0,  # TODO: implement negation window
            "category_overrides": 0  # TODO: category allowlist
        },
        "highlights": ex_hi
    }

    # Headline scores (independent)
    text_all = " ".join(s.text for s in segments)
    words = _word_re.findall(text_all.lower())
    minutes = (segments[-1].end - segments[0].start)/60.0 if len(segments) >= 2 else 1.0
    wpm = len(words) / max(1e-6, minutes)
    filler_cnt = sum(text_all.lower().count(f) for f in FILLERS_EN)
    sent_cnt = max(1, text_all.count(".") + text_all.count("?") + text_all.count("!"))
    filler_rate = filler_cnt / sent_cnt

    # Weighted persuasion hits: CTA + bonuses (deal/urgency/structure/evidence)
    weighted_hits = 0.0
    for s in segments:
        cta, deal, urg = count_cta_hits_rich(s.text)
        weighted_hits += cta + BONUS_DEAL * deal + BONUS_URGENCY * urg
        if cta > 0:
            if any(term in s.text.lower() for term in PAIN_BENEFIT):
                weighted_hits += BONUS_STRUCTURE
            if NUMERIC_UNIT_RE.search(s.text):
                weighted_hits += BONUS_EVIDENCE

    accuracy_raw   = score_accuracy_independent(text_all, segments)
    clarity_raw    = score_clarity_from_signals(filler_rate=filler_rate, wpm=wpm)
    persuasion_raw = score_persuasion_from_cta(int(round(weighted_hits)))

    # Baseline remap
    accuracy   = remap_with_baseline(accuracy_raw)
    clarity    = remap_with_baseline(clarity_raw)
    persuasion = remap_with_baseline(persuasion_raw)

    result = {
        "lang_interaction": inter_json,
        "lang_exaggeration": ex_json,  # compliance result (independent)
        "lang_scores": {
            "accuracy": round(accuracy, 1),
            "clarity": round(clarity, 1),
            "persuasion": round(persuasion, 1),
            "wpm": round(wpm, 1),
            "filler_rate": round(filler_rate, 3),
            # raw scores for debugging/tuning (remove if you don't want to expose)
            "accuracy_raw": round(accuracy_raw, 1),
            "clarity_raw": round(clarity_raw, 1),
            "persuasion_raw": round(persuasion_raw, 1),
        },
    }
    if DEBUG_DIAG:
        dbg = getattr(transcribe_to_segments, "_last_debug", {})
        result["debug"] = dbg
    return result
