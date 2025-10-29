"""Utilities for verifying faculty matches without writing workbooks."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from . import config as config_module
from . import ingest, match
from .models import MatchResult


@dataclass(slots=True)
class FacultyMatches:
    faculty_name: str
    matches: list[MatchResult]


def get_top_matches(
    faculty_name: str,
    faculty_path: Path,
    foundations_path: Path,
    *,
    top: int = 5,
) -> FacultyMatches:
    """Return top matches for the specified faculty member."""

    config = config_module.load_matching_config()

    faculty_records = ingest.load_faculty(
        faculty_path,
        synonyms=config.synonyms,
        ignored_tokens=config.ignored_tokens,
    ).records
    foundation_records = ingest.load_foundations(
        foundations_path,
        synonyms=config.synonyms,
        ignored_tokens=config.ignored_tokens,
    ).records

    matches = match.generate_matches(
        faculty_records,
        foundation_records,
        matching_config=config,
    )

    filtered = [m for m in matches if m.faculty.name.lower() == faculty_name.lower()]
    filtered.sort(key=lambda m: (-m.score, m.foundation.name.lower()))

    return FacultyMatches(faculty_name=faculty_name, matches=filtered[:top])
