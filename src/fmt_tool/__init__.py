"""Foundation Matching Tool package."""

from .errors import FMTError, FMTValidationError
from .models import (
    FacultyRecord,
    FoundationRecord,
    IngestionResult,
    MatchResult,
    RunContext,
)

__all__ = [
    "FMTError",
    "FMTValidationError",
    "FacultyRecord",
    "FoundationRecord",
    "IngestionResult",
    "MatchResult",
    "RunContext",
]
