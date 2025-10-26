"""Command-line interface for the Foundation Matching Tool."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from . import errors, pipeline


def build_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the CLI."""

    parser = argparse.ArgumentParser(
        prog="fmt",
        description=(
            "Foundation Matching Tool – generates faculty-specific foundation "
            "opportunity digests from keyword spreadsheets."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--faculty-xlsx",
        required=True,
        type=Path,
        help="Path to the faculty keyword Excel workbook.",
    )
    parser.add_argument(
        "--foundations-xlsx",
        required=True,
        type=Path,
        help="Path to the foundation opportunity Excel workbook.",
    )
    parser.add_argument(
        "--output-xlsx",
        required=True,
        type=Path,
        help="Destination path for the generated digest workbook.",
    )
    parser.add_argument(
        "--operator",
        default="Unknown",
        help="Name of the person running the tool.",
    )
    parser.add_argument(
        "--run-label",
        default=None,
        help="Optional descriptive label for this run (e.g., 'Spring 2025 cycle').",
    )
    parser.add_argument(
        "--run-date",
        default=None,
        help="ISO-formatted date string to override the run timestamp (YYYY-MM-DD).",
    )

    return parser


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments."""

    parser = build_parser()
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry point."""

    args = parse_args(argv)

    try:
        output_path = pipeline.run(args)
    except errors.FMTError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:  # pragma: no cover - defensive
        print(f"Unexpected error: {exc}", file=sys.stderr)
        return 1

    print(f"Digest created at {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
