"""Lightweight fuzzy string matching helpers with optional RapidFuzz support."""

from __future__ import annotations

import difflib

try:  # pragma: no cover - prefer RapidFuzz when available
    from rapidfuzz import fuzz as _rf_fuzz  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - fallback used in constrained envs
    _rf_fuzz = None  # type: ignore[assignment]


def partial_ratio(a: str, b: str) -> int:
    """Return the partial ratio between two strings (0-100)."""

    if _rf_fuzz is not None:
        return int(_rf_fuzz.partial_ratio(a, b))
    return _sequence_ratio(_normalize(a), _normalize(b), partial=True)


def token_set_ratio(a: str, b: str) -> int:
    """Return the token set ratio between two strings (0-100)."""

    if _rf_fuzz is not None:
        return int(_rf_fuzz.token_set_ratio(a, b))

    normalized_a = " ".join(sorted(set(_normalize(a).split())))
    normalized_b = " ".join(sorted(set(_normalize(b).split())))
    return _sequence_ratio(normalized_a, normalized_b)


def _sequence_ratio(a: str, b: str, *, partial: bool = False) -> int:
    if not a or not b:
        return 0

    if not partial:
        ratio = difflib.SequenceMatcher(None, a, b).ratio()
        best = max(ratio, _lcs_ratio(a, b))
        return int(round(best * 100))

    shorter, longer = (a, b) if len(a) <= len(b) else (b, a)
    best = 0.0
    len_short = len(shorter)

    for start in range(len(longer) - len_short + 1):
        window = longer[start : start + len_short]
        ratio = difflib.SequenceMatcher(None, shorter, window).ratio()
        if ratio > best:
            best = ratio
        if best == 1.0:
            break

    best = max(best, _lcs_ratio(shorter, longer))
    return int(round(best * 100))


def _normalize(value: str) -> str:
    return " ".join(value.strip().lower().split())


def _lcs_ratio(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    matcher = difflib.SequenceMatcher(None, a, b)
    matches = sum(block.size for block in matcher.get_matching_blocks())
    shortest = min(len(a), len(b))
    if shortest == 0:
        return 0.0
    if matches >= shortest:
        return 1.0
    longest = max(len(a), len(b))
    if longest == 0:
        return 0.0
    return matches / longest
