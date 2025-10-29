"""Pipeline orchestration for the Foundation Matching Tool."""

from __future__ import annotations

from argparse import Namespace
from dataclasses import replace
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Tuple

from .errors import FMTValidationError
from . import config as config_module
from . import ingest, match, render
from .models import PipelineSummary, RunContext


def run(args: Namespace) -> Tuple[Path, PipelineSummary]:
    """Execute the end-to-end Foundation Matching Tool pipeline."""

    warnings: List[str] = []

    matching_config = config_module.load_matching_config()
    cli_use_weights = getattr(args, "use_weights", None)
    if cli_use_weights is not None:
        matching_config = replace(matching_config, use_weights=cli_use_weights)

    faculty_path = Path(args.faculty_xlsx)
    foundation_path = Path(args.foundations_xlsx)
    output_path = Path(args.output_xlsx)

    faculty_result = ingest.load_faculty(
        faculty_path,
        synonyms=matching_config.synonyms,
        ignored_tokens=matching_config.ignored_tokens,
    )
    foundation_result = ingest.load_foundations(
        foundation_path,
        synonyms=matching_config.synonyms,
        ignored_tokens=matching_config.ignored_tokens,
    )

    warnings.extend(faculty_result.warnings)
    warnings.extend(foundation_result.warnings)

    matches = match.generate_matches(
        faculty_result.records,
        foundation_result.records,
        warnings=warnings,
        profile="standard",
        matching_config=matching_config,
    )

    matches_by_division = render.group_matches_by_division(matches)

    run_timestamp = _resolve_run_timestamp(args.run_date)
    deduped_warnings = _dedupe_warnings(warnings)

    run_context = RunContext(
        timestamp=run_timestamp,
        operator=args.operator,
        run_label=args.run_label,
        faculty_source=faculty_path,
        foundation_source=foundation_path,
        output_path=output_path,
        weighted_mode=matching_config.use_weights,
        warnings=deduped_warnings,
    )

    workbook = render.build_workbook(matches_by_division, run_context)
    render.write_workbook(workbook, output_path)

    summary = PipelineSummary(
        total_faculty=len(faculty_result.records),
        total_foundations=len(foundation_result.records),
        total_matches=len(matches),
        weighted_mode=matching_config.use_weights,
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
