"""Custom exceptions for the Foundation Matching Tool."""


class FMTError(Exception):
    """Base class for expected application errors."""


class FMTValidationError(FMTError):
    """Indicates validation errors in user-supplied input files."""
