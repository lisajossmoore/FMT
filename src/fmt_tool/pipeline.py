"""Pipeline orchestration for the Foundation Matching Tool."""

from __future__ import annotations

from argparse import Namespace
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Tuple

from .errors import FMTValidationError
from . import ingest, match, render
from .models import PipelineSummary, RunContext


def run(args: Namespace) -> Tuple[Path, PipelineSummary]:
    """Execute the end-to-end Foundation Matching Tool pipeline."""

    warnings: List[str] = []

    faculty_result = ingest.load_faculty(Path(args.faculty_xlsx))
    foundation_result = ingest.load_foundations(Path(args.foundations_xlsx))

    warnings.extend(faculty_result.warnings)
    warnings.extend(foundation_result.warnings)

    matches = match.generate_matches(
        faculty_result.records,
        foundation_result.records,
        warnings=warnings,
        profile="standard",
    )

    matches_by_division = render.group_matches_by_division(matches)

    run_timestamp = _resolve_run_timestamp(args.run_date)
    deduped_warnings = _dedupe_warnings(warnings)

    run_context = RunContext(
        timestamp=run_timestamp,
        operator=args.operator,
        run_label=args.run_label,
        faculty_source=Path(args.faculty_xlsx),
        foundation_source=Path(args.foundations_xlsx),
        warnings=deduped_warnings,
    )

    workbook = render.build_workbook(matches_by_division, run_context)
    output_path = Path(args.output_xlsx)
    render.write_workbook(workbook, output_path)

    summary = PipelineSummary(
        total_faculty=len(faculty_result.records),
        total_foundations=len(foundation_result.records),
        total_matches=len(matches),
        warnings=deduped_warnings,
    )

    return output_path, summary


def _resolve_run_timestamp(run_date: str | None) -> datetime:
    if not run_date:
        return datetime.now()

    try:
        return datetime.fromisoformat(run_date)
    except ValueError as exc:  # pragma: no cover - defensive
        raise FMTValidationError(
            f"Invalid run date '{run_date}'. Expected ISO format (YYYY-MM-DD)."
        ) from exc


def _dedupe_warnings(warnings: Iterable[str]) -> List[str]:
    seen = {}
    for warning in warnings:
        if warning not in seen:
            seen[warning] = None
    return list(seen.keys())
