import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from fmt_tool import errors, pipeline  # noqa: E402


def write_faculty(tmp_path: Path, rows: list[dict]) -> Path:
    path = tmp_path / "faculty.xlsx"
    df = pd.DataFrame(rows)
    df.to_excel(path, index=False)
    return path


def write_foundations(tmp_path: Path, rows: list[dict]) -> Path:
    path = tmp_path / "foundations.xlsx"
    df = pd.DataFrame(rows)
    df.to_excel(path, index=False)
    return path


def test_pipeline_success(tmp_path):
    faculty_path = write_faculty(
        tmp_path,
        [
            {
                "Name": "Dr. A",
                "Degree": "MD",
                "Rank": "Professor",
                "Division ": "Neonatology",
                "Career Stage": "Mid",
                "Keywords": "Pulmonary, Neonatology",
            },
            {
                "Name": "Dr. B",
                "Degree": "PhD",
                "Rank": "Assistant Professor",
                "Division ": "Neonatology",
                "Career Stage": "Early",
                "Keywords": "",
            },
        ],
    )
    foundation_path = write_foundations(
        tmp_path,
        [
            {
                "Foundation name": "Pulmonary Fund",
                "area(s) of funding": "Pulmonary research",
                "average grant amount": "High",
                "career stage targeted": "Mid",
                "Deadlines, restrictions": "July 15",
                "institution specific preferences": "Utah preferred",
                "Website link": "https://pulmonary.example.com",
                "Keywords": "Pulmonary, Neonatal",
            }
        ],
    )

    output_path = tmp_path / "output" / "digest.xlsx"
    args = type(
        "Args",
        (),
        {
            "faculty_xlsx": faculty_path,
            "foundations_xlsx": foundation_path,
            "output_xlsx": output_path,
            "operator": "Alex Operator",
            "run_label": "Spring 2025",
            "run_date": "2025-03-01",
        },
    )()

    final_path, summary = pipeline.run(args)

    assert final_path == output_path
    assert output_path.exists()
    assert summary.total_faculty == 2
    assert summary.total_matches == 1
    assert any("missing keywords" in warning for warning in summary.warnings)


def test_pipeline_raises_validation_error(tmp_path):
    faculty_path = write_faculty(
        tmp_path,
        [
            {
                "Name": "Dr. A",
                "Degree": "MD",
                "Rank": "Professor",
                "Division ": "Neonatology",
                "Keywords": "Pulmonary",
            }
        ],
    )
    foundation_path = write_foundations(
        tmp_path,
        [
            {
                "Foundation name": "Pulmonary Fund",
                "area(s) of funding": "Pulmonary research",
                "average grant amount": "High",
                "career stage targeted": "Mid",
                "Deadlines, restrictions": "July 15",
                "institution specific preferences": "Utah preferred",
                "Website link": "https://pulmonary.example.com",
                "Keywords": "Pulmonary",
            }
        ],
    )

    output_path = tmp_path / "output" / "digest.xlsx"
    args = type(
        "Args",
        (),
        {
            "faculty_xlsx": faculty_path,
            "foundations_xlsx": foundation_path,
            "output_xlsx": output_path,
            "operator": "Alex Operator",
            "run_label": None,
            "run_date": None,
        },
    )()

    with pytest.raises(errors.FMTValidationError):
        pipeline.run(args)
