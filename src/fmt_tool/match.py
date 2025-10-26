"""Matching engine for connecting faculty with foundations."""

from __future__ import annotations

from typing import Iterable, List, Optional

from .models import FacultyRecord, FoundationRecord, MatchResult


def calculate_score(
    faculty_keywords: Iterable[str],
    foundation_keywords: Iterable[str],
) -> tuple[int, set[str]]:
    """Calculate match score and overlapping keywords.

    Returns a score between 0 and 100 (inclusive) along with the set of matched keywords.
    """

    faculty_set = set(faculty_keywords)
    foundation_set = set(foundation_keywords)

    if not faculty_set or not foundation_set:
        return 0, set()

    matched = faculty_set & foundation_set
    if not matched:
        return 0, set()

    score = int((len(matched) / len(faculty_set)) * 100)
    if score > 100:
        score = 100

    return score, matched


def generate_matches(
    faculty_records: Iterable[FacultyRecord],
    foundation_records: Iterable[FoundationRecord],
    *,
    warnings: Optional[List[str]] = None,
    profile: str = "standard",
) -> List[MatchResult]:
    """Generate match results for the provided faculty and foundation lists."""

    if profile != "standard":
        raise ValueError(f"Unsupported matching profile '{profile}'")

    warning_list = warnings if warnings is not None else []
    matches: List[MatchResult] = []
    foundation_warning_emitted: set[int] = set()

    for faculty in faculty_records:
        if not faculty.keywords:
            warning_list.append(
                f"Faculty '{faculty.name}' has no keywords available for matching (row {faculty.raw_row_index})."
            )
            continue

        for foundation in foundation_records:
            if not foundation.keywords:
                if foundation.raw_row_index not in foundation_warning_emitted:
                    warning_list.append(
                        f"Foundation '{foundation.name}' has no keywords available for matching (row {foundation.raw_row_index})."
                    )
                    foundation_warning_emitted.add(foundation.raw_row_index)
                continue

            score, matched_keywords = calculate_score(
                faculty.keywords, foundation.keywords
            )
            if not matched_keywords:
                continue

            result = MatchResult(
                faculty=faculty,
                foundation=foundation,
                score=score,
                matched_keywords=sorted(matched_keywords),
                faculty_keyword_count=len(faculty.keywords),
                foundation_keyword_count=len(foundation.keywords),
            )
            matches.append(result)

    matches.sort(
        key=lambda m: (m.faculty.name.lower(), -m.score, m.foundation.name.lower())
    )

    return matches


def group_matches_by_faculty(
    matches: Iterable[MatchResult],
) -> dict[str, List[MatchResult]]:
    """Group matches by faculty name while preserving encounter order."""

    grouped: dict[str, List[MatchResult]] = {}
    for match in matches:
        grouped.setdefault(match.faculty.name, []).append(match)
    return grouped
