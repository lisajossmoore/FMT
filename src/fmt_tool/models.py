"""Data models used by the Foundation Matching Tool."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Sequence, Set


@dataclass(slots=True)
class FacultyRecord:
    """Normalized representation of a faculty member."""

    name: str
    degree: str
    rank: str
    division: str
    career_stage: str
    keywords: Set[str]
    keywords_phrases: List[str]
    raw_row_index: int


@dataclass(slots=True)
class FoundationRecord:
    """Normalized representation of a foundation opportunity."""

    name: str
    areas_of_funding: str
    average_grant_amount: str
    career_stage_targeted: str
    deadlines: str
    institution_preferences: str
    website: str
    keywords: Set[str]
    keywords_phrases: List[str]
    raw_row_index: int


@dataclass(slots=True)
class IngestionResult:
    """Container for ingested records and associated warnings."""

    records: List[object]
    warnings: List[str] = field(default_factory=list)


@dataclass(slots=True)
class RunContext:
    """Metadata about a pipeline run (populated later in the pipeline)."""

    timestamp: datetime
    operator: str
    run_label: str | None
    faculty_source: Path
    foundation_source: Path
    output_path: Path
    weighted_mode: bool
    warnings: Sequence[str] = field(default_factory=list)


@dataclass(slots=True)
class MatchResult:
    """Represents a scored match between a faculty member and a foundation."""

    faculty: FacultyRecord
    foundation: FoundationRecord
    score: int
    raw_score: float
    keyword_score: int
    weighted_score: int | None
    matched_keywords: List[str]
    faculty_keyword_count: int
    foundation_keyword_count: int
    keyword_match_count: int
    match_reason: str


@dataclass(slots=True)
class PipelineSummary:
    """Aggregate information about a completed pipeline run."""

    total_faculty: int
    total_foundations: int
    total_matches: int
    weighted_mode: bool
    warnings: List[str] = field(default_factory=list)
