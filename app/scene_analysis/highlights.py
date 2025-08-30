from __future__ import annotations
from typing import List, Tuple, Optional

def compress_runs(times: List[float], mask: List[bool], min_s: float) -> List[Tuple[float, float]]:
    out: List[Tuple[float, float]] = []
    if not times:
        return out
    start_t: Optional[float] = None
    prev_t: Optional[float] = None
    for t, flag in zip(times, mask):
        if flag and start_t is None:
            start_t = t
        if not flag and start_t is not None:
            if prev_t is not None and (prev_t - start_t) >= min_s:
                out.append((start_t, prev_t))
            start_t = None
        prev_t = t
    if start_t is not None and prev_t is not None and (prev_t - start_t) >= min_s:
        out.append((start_t, prev_t))
    return out

