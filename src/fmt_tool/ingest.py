"""Data ingestion and validation utilities."""

from __future__ import annotations

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


def load_faculty(path: Path) -> IngestionResult:
    """Load and validate faculty spreadsheet."""

    dataframe = _read_excel(path)
    dataframe = _normalize_columns(dataframe)
    _ensure_required_columns(dataframe, FACULTY_REQUIRED_COLUMNS, "faculty", path)
    dataframe = _drop_blank_rows(dataframe)

    records: List[FacultyRecord] = []
    warnings: List[str] = []

    for _, row in dataframe.iterrows():
        record = FacultyRecord(
            name=_clean_str(row["Name"]),
            degree=_clean_str(row["Degree"]),
            rank=_clean_str(row["Rank"]),
            division=_clean_str(row["Division"]),
            career_stage=_clean_str(row["Career Stage"]),
            keywords=_parse_keywords(
                row["Keywords"],
                warnings,
                entity="Faculty",
                name=_clean_str(row["Name"]),
                row_num=int(row["__rownum__"]),
            ),
            raw_row_index=int(row["__rownum__"]),
        )
        records.append(record)

    warnings.extend(_detect_duplicate_faculty(records))

    return IngestionResult(records=records, warnings=warnings)


def load_foundations(path: Path) -> IngestionResult:
    """Load and validate foundation spreadsheet."""

    dataframe = _read_excel(path)
    dataframe = _normalize_columns(dataframe)
    _ensure_required_columns(dataframe, FOUNDATION_REQUIRED_COLUMNS, "foundation", path)
    dataframe = _drop_blank_rows(dataframe)

    records: List[FoundationRecord] = []
    warnings: List[str] = []

    for _, row in dataframe.iterrows():
        record = FoundationRecord(
            name=_clean_str(row["Foundation name"]),
            areas_of_funding=_clean_str(row["area(s) of funding"]),
            average_grant_amount=_clean_str(row["average grant amount"]),
            career_stage_targeted=_clean_str(row["career stage targeted"]),
            deadlines=_clean_str(row["Deadlines, restrictions"]),
            institution_preferences=_clean_str(row["institution specific preferences"]),
            website=_clean_str(row["Website link"]),
            keywords=_parse_keywords(
                row["Keywords"],
                warnings,
                entity="Foundation",
                name=_clean_str(row["Foundation name"]),
                row_num=int(row["__rownum__"]),
            ),
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


def _parse_keywords(
    raw_keywords: object,
    warnings: List[str],
    *,
    entity: str,
    name: str,
    row_num: int,
) -> set[str]:
    cleaned = _clean_str(raw_keywords)
    if not cleaned:
        warnings.append(f"{entity} '{name}' has missing keywords (row {row_num}).")
        return set()
    tokens = {token.strip().lower() for token in cleaned.split(",") if token.strip()}
    if not tokens:
        warnings.append(f"{entity} '{name}' has missing keywords (row {row_num}).")
    return tokens


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
