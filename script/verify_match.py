#!/usr/bin/env python
"""Helper script to print top foundation matches for a faculty member."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"


def _load_verification_module():
    if str(SRC_DIR) not in sys.path:
        sys.path.insert(0, str(SRC_DIR))
    from fmt_tool import verification  # imported lazily to avoid path issues

    return verification


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Show top foundation matches for a faculty member."
    )
    parser.add_argument("--faculty-name", required=True, help="Faculty member name.")
    parser.add_argument(
        "--faculty-xlsx",
        default="data/faculty.xlsx",
        type=Path,
        help="Path to faculty Excel file.",
    )
    parser.add_argument(
        "--foundations-xlsx",
        default="data/foundations.xlsx",
        type=Path,
        help="Path to foundation Excel file.",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=5,
        help="Number of top matches to display.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    verification = _load_verification_module()
    result = verification.get_top_matches(
        args.faculty_name,
        args.faculty_xlsx,
        args.foundations_xlsx,
        top=args.top,
    )

    if not result.matches:
        print(f"No matches found for {result.faculty_name}.")
        return 0

    print(f"Top {len(result.matches)} matches for {result.faculty_name}:")
    for match in result.matches:
        keywords = ", ".join(match.matched_keywords) or "(no overlapping keywords)"
        print(
            f"- {match.foundation.name} | score={match.score} | matches={match.keyword_match_count} | keywords={keywords}"
        )
        reason = match.match_reason or "(no details)"
        print(f"    Why: {reason}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
