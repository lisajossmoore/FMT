"""Fuzzy matching engine for connecting faculty with foundations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional

from . import config as config_module
from . import fuzzy
from .models import FacultyRecord, FoundationRecord, MatchResult


@dataclass(slots=True)
class KeywordPair:
    faculty_phrase: str
    foundation_phrase: str
    score: int


def generate_matches(
    faculty_records: Iterable[FacultyRecord],
    foundation_records: Iterable[FoundationRecord],
    *,
    warnings: Optional[List[str]] = None,
    profile: str = "standard",
    matching_config: config_module.MatchingConfig | None = None,
) -> List[MatchResult]:
    if profile != "standard":
        raise ValueError(f"Unsupported matching profile '{profile}'")

    config = matching_config or config_module.load_matching_config()

    warning_list = warnings if warnings is not None else []
    matches: List[MatchResult] = []

    threshold_percent = int(round(config.similarity_threshold * 100))
    ignored_tokens = config.ignored_tokens

    for faculty in faculty_records:
        faculty_phrases = _filter_phrases(faculty.keywords_phrases, ignored_tokens)
        if not faculty_phrases:
            warning_list.append(
                f"Faculty '{faculty.name}' has no keywords available for matching (row {faculty.raw_row_index})."
            )
            continue

        for foundation in foundation_records:
            foundation_phrases = _filter_phrases(
                foundation.keywords_phrases, ignored_tokens
            )
            if not foundation_phrases:
                warning_list.append(
                    f"Foundation '{foundation.name}' has no keywords available for matching (row {foundation.raw_row_index})."
                )
                continue

            keyword_score, pairs = _pairwise_best_scores(
                faculty_phrases, foundation_phrases
            )
            if not pairs:
                continue

            final_score = keyword_score
            keyword_component = keyword_score
            grant_score = 0
            stage_score = 0
            weighted_score_value: int | None = None

            if config.use_weights:
                grant_mult = _grant_multiplier(foundation.average_grant_amount)
                grant_score = int(round(grant_mult * 100))
                stage_score = (
                    100
                    if _stage_matches(
                        faculty.career_stage, foundation.career_stage_targeted
                    )
                    else 0
                )
                final_score = int(
                    round(
                        config.keyword_weight * keyword_component
                        + config.grant_weight * grant_score
                        + config.stage_weight * stage_score
                    )
                )
                final_score = max(0, min(100, final_score))
                weighted_score_value = final_score

            if final_score < threshold_percent:
                continue

            match_reason = _build_match_reason(pairs, foundation.name)
            match_count = sum(1 for pair in pairs if pair.score >= threshold_percent)

            matches.append(
                MatchResult(
                    faculty=faculty,
                    foundation=foundation,
                    score=final_score,
                    raw_score=final_score / 100,
                    keyword_score=keyword_score,
                    weighted_score=weighted_score_value,
                    matched_keywords=sorted({pair.faculty_phrase for pair in pairs}),
                    faculty_keyword_count=len(faculty_phrases),
                    foundation_keyword_count=len(foundation_phrases),
                    keyword_match_count=match_count,
                    match_reason=match_reason,
                )
            )

    matches.sort(
        key=lambda m: (m.faculty.name.lower(), -m.score, m.foundation.name.lower())
    )
    return matches


def group_matches_by_faculty(
    matches: Iterable[MatchResult],
) -> dict[str, List[MatchResult]]:
    grouped: dict[str, List[MatchResult]] = {}
    for match in matches:
        grouped.setdefault(match.faculty.name, []).append(match)
    return grouped


def _pairwise_best_scores(
    faculty_keywords: List[str],
    foundation_keywords: List[str],
) -> tuple[int, List[KeywordPair]]:
    pairs: List[KeywordPair] = []
    best_overall = 0

    for faculty_kw in faculty_keywords:
        best_match: Optional[str] = None
        best_score = -1
        for foundation_kw in foundation_keywords:
            faculty_tokens = set(faculty_kw.split())
            foundation_tokens = set(foundation_kw.split())
            shared_tokens = faculty_tokens & foundation_tokens
            abbreviation = False
            if not shared_tokens:
                abbreviation = (
                    len(faculty_kw) <= 5 and _is_subsequence(faculty_kw, foundation_kw)
                ) or (
                    len(foundation_kw) <= 5
                    and _is_subsequence(foundation_kw, faculty_kw)
                )
                if not abbreviation:
                    continue

            score = max(
                fuzzy.partial_ratio(faculty_kw, foundation_kw),
                fuzzy.token_set_ratio(faculty_kw, foundation_kw),
            )
            if score > best_score:
                best_score = int(score)
                best_match = foundation_kw

        if best_match is not None and best_score > 0:
            pairs.append(KeywordPair(faculty_kw, best_match, best_score))
            if best_score > best_overall:
                best_overall = best_score

    pairs.sort(
        key=lambda pair: (-pair.score, pair.faculty_phrase, pair.foundation_phrase)
    )
    return best_overall, pairs


def _grant_multiplier(value: str) -> float:
    v = (value or "").strip().lower()
    if v.startswith("h"):
        return 1.0
    if v.startswith("m"):
        return 0.6
    if v.startswith("l"):
        return 0.3
    return 0.6


def _stage_matches(faculty_stage: str, foundation_stage: str) -> bool:
    return (faculty_stage or "").strip().lower() == (
        foundation_stage or ""
    ).strip().lower()


def _build_match_reason(
    pairs: List[KeywordPair],
    foundation_name: str,
    limit: int = 5,
) -> str:
    snippets = [
        f"{foundation_name}: {pair.faculty_phrase} ~ {pair.foundation_phrase} ({pair.score})"
        for pair in pairs[:limit]
    ]
    return "; ".join(snippets)


def _filter_phrases(phrases: Iterable[str], ignored_tokens: set[str]) -> List[str]:
    filtered: List[str] = []
    for phrase in phrases:
        if not phrase:
            continue
        tokens = [token for token in phrase.split() if token]
        if not tokens:
            continue
        if all(token in ignored_tokens for token in tokens):
            continue
        filtered.append(phrase)
    return filtered


def _is_subsequence(candidate: str, target: str) -> bool:
    if not candidate:
        return True
    it = iter(target)
    return all(char in it for char in candidate)
