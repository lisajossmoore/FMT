"""Foundation Matching Tool package."""

from .errors import FMTError, FMTValidationError
from .models import FacultyRecord, FoundationRecord, IngestionResult, RunContext

__all__ = [
    "FMTError",
    "FMTValidationError",
    "FacultyRecord",
    "FoundationRecord",
    "IngestionResult",
    "RunContext",
]
