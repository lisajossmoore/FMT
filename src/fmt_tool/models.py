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
    warnings: Sequence[str] = field(default_factory=list)
