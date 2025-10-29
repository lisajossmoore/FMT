"""Data ingestion and validation utilities."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable, List, Tuple

import pandas as pd

from .errors import FMTValidationError
from .models import FacultyRecord, FoundationRecord, IngestionResult

FACULTY_REQUIRED_COLUMNS = [
    "Name",
    "Degree",
    "Rank",
    "Division",
    "Career Stage",
    "Keywords",
]

FOUNDATION_REQUIRED_COLUMNS = [
    "Foundation name",
    "area(s) of funding",
    "average grant amount",
    "career stage targeted",
    "Deadlines, restrictions",
    "institution specific preferences",
    "Website link",
    "Keywords",
]


def load_faculty(
    path: Path,
    *,
    synonyms: dict[str, list[str]] | None = None,
    ignored_tokens: Iterable[str] | None = None,
) -> IngestionResult:
    """Load and validate faculty spreadsheet."""

    dataframe = _read_excel(path)
    dataframe = _normalize_columns(dataframe)
    _ensure_required_columns(dataframe, FACULTY_REQUIRED_COLUMNS, "faculty", path)
    dataframe = _drop_blank_rows(dataframe)

    records: List[FacultyRecord] = []
    warnings: List[str] = []
    synonyms = _normalize_synonyms(synonyms)
    ignored_set = {token.lower() for token in (ignored_tokens or [])}

    for _, row in dataframe.iterrows():
        name = _clean_str(row["Name"])
        phrases, token_set = _prepare_keywords(
            row["Keywords"],
            synonyms,
            ignored_set,
        )
        if not token_set:
            warnings.append(
                f"Faculty '{name}' has missing keywords (row {int(row['__rownum__'])})."
            )

        record = FacultyRecord(
            name=name,
            degree=_clean_str(row["Degree"]),
            rank=_clean_str(row["Rank"]),
            division=_clean_str(row["Division"]),
            career_stage=_clean_str(row["Career Stage"]),
            keywords=token_set,
            keywords_phrases=phrases,
            raw_row_index=int(row["__rownum__"]),
        )
        records.append(record)

    warnings.extend(_detect_duplicate_faculty(records))

    return IngestionResult(records=records, warnings=warnings)


def load_foundations(
    path: Path,
    *,
    synonyms: dict[str, list[str]] | None = None,
    ignored_tokens: Iterable[str] | None = None,
) -> IngestionResult:
    """Load and validate foundation spreadsheet."""

    dataframe = _read_excel(path)
    dataframe = _normalize_columns(dataframe)
    _ensure_required_columns(dataframe, FOUNDATION_REQUIRED_COLUMNS, "foundation", path)
    dataframe = _drop_blank_rows(dataframe)

    records: List[FoundationRecord] = []
    warnings: List[str] = []
    synonyms = _normalize_synonyms(synonyms)
    ignored_set = {token.lower() for token in (ignored_tokens or [])}

    for _, row in dataframe.iterrows():
        name = _clean_str(row["Foundation name"])
        phrases, token_set = _prepare_keywords(
            row["Keywords"],
            synonyms,
            ignored_set,
        )
        if not token_set:
            warnings.append(
                f"Foundation '{name}' has missing keywords (row {int(row['__rownum__'])})."
            )

        record = FoundationRecord(
            name=name,
            areas_of_funding=_clean_str(row["area(s) of funding"]),
            average_grant_amount=_clean_str(row["average grant amount"]),
            career_stage_targeted=_clean_str(row["career stage targeted"]),
            deadlines=_clean_str(row["Deadlines, restrictions"]),
            institution_preferences=_clean_str(row["institution specific preferences"]),
            website=_clean_str(row["Website link"]),
            keywords=token_set,
            keywords_phrases=phrases,
            raw_row_index=int(row["__rownum__"]),
        )
        records.append(record)

    return IngestionResult(records=records, warnings=warnings)


def _read_excel(path: Path) -> pd.DataFrame:
    try:
        dataframe = pd.read_excel(path, engine="openpyxl")
    except FileNotFoundError as exc:
        raise FMTValidationError(f"Input file not found: {path}") from exc
    except ValueError as exc:  # invalid format or empty file
        raise FMTValidationError(f"Unable to read Excel file '{path}': {exc}") from exc

    dataframe["__rownum__"] = dataframe.index + 2
    return dataframe


def _normalize_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    dataframe = dataframe.rename(
        columns=lambda col: col.strip() if isinstance(col, str) else col
    )
    dataframe = dataframe.fillna("")
    return dataframe


def _ensure_required_columns(
    dataframe: pd.DataFrame,
    required_columns: Iterable[str],
    label: str,
    path: Path,
) -> None:
    missing = [column for column in required_columns if column not in dataframe.columns]
    if missing:
        missing_list = ", ".join(sorted(missing))
        raise FMTValidationError(
            f"The {label} file '{path}' is missing required column(s): {missing_list}"
        )


def _drop_blank_rows(dataframe: pd.DataFrame) -> pd.DataFrame:
    def row_is_blank(row: pd.Series) -> bool:
        return all(
            str(value).strip() == ""
            for key, value in row.items()
            if key != "__rownum__"
        )

    mask = dataframe.apply(row_is_blank, axis=1)
    return dataframe.loc[~mask].reset_index(drop=True)


def _clean_str(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _normalize_synonyms(synonyms: dict[str, list[str]] | None) -> dict[str, list[str]]:
    if not synonyms:
        return {}
    normalized: dict[str, list[str]] = {}
    for key, values in synonyms.items():
        base = _normalize_phrase(key)
        if not base:
            continue
        cleaned_values = []
        for value in values:
            norm_value = _normalize_phrase(value)
            if norm_value:
                cleaned_values.append(norm_value)
        normalized[base] = cleaned_values
    return normalized


def _prepare_keywords(
    raw_keywords: object,
    synonyms: dict[str, list[str]],
    ignored_tokens: set[str],
) -> tuple[List[str], set[str]]:
    cleaned = _clean_str(raw_keywords)
    if not cleaned:
        return [], set()

    phrases: set[str] = set()
    for part in re.split(r"[;,\n]+", cleaned):
        phrase = _normalize_phrase(part)
        if not phrase:
            continue
        if _phrase_should_ignore(phrase, ignored_tokens):
            continue
        phrases.add(phrase)
        for syn in synonyms.get(phrase, []):
            if syn and not _phrase_should_ignore(syn, ignored_tokens):
                phrases.add(syn)

    sorted_phrases = sorted(phrases)
    token_set = {
        token
        for phrase in sorted_phrases
        for token in phrase.split()
        if token not in ignored_tokens
    }
    return sorted_phrases, token_set


def _normalize_phrase(value: str) -> str:
    value = value.strip().lower()
    value = value.replace("\u00a0", " ")
    value = re.sub(r"[\s_/|,-]+", " ", value)
    value = re.sub(r"[^a-z0-9 ]+", "", value)
    return " ".join(value.split())


def _phrase_should_ignore(phrase: str, ignored_tokens: set[str]) -> bool:
    if not phrase:
        return True
    words = [part for part in phrase.split() if part]
    if not words:
        return True
    return all(word in ignored_tokens for word in words)


def _detect_duplicate_faculty(records: List[FacultyRecord]) -> List[str]:
    seen: dict[Tuple[str, str], List[int]] = {}
    display: dict[Tuple[str, str], Tuple[str, str]] = {}
    for record in records:
        key = (record.name.lower(), record.division.lower())
        seen.setdefault(key, []).append(record.raw_row_index)
        display.setdefault(key, (record.name, record.division))

    warnings = []
    for key, rows in seen.items():
        if len(rows) > 1:
            name, division = display[key]
            row_list = ", ".join(str(row) for row in sorted(rows))
            warnings.append(
                f"Duplicate faculty '{name}' in division '{division}' at rows {row_list}."
            )
    return warnings
