import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from fmt_tool import verification  # noqa: E402


@pytest.fixture()
def config_override(monkeypatch, tmp_path):
    config_path = tmp_path / "settings.toml"
    config_path.write_text(
        "[matching]\n"
        "similarity_threshold = 0.6\n"
        "use_weights = false\n"
        "keyword_weight = 0.6\n"
        "grant_weight = 0.2\n"
        "stage_weight = 0.2\n"
        'ignored_tokens = ["career", "development", "prevention", "and", "in", "neonatal"]\n',
        encoding="utf-8",
    )
    monkeypatch.setenv("FMT_CONFIG_PATH", str(config_path))
    yield
    monkeypatch.delenv("FMT_CONFIG_PATH", raising=False)


def write_excel(tmp_path: Path, filename: str, rows: list[dict]) -> Path:
    path = tmp_path / filename
    pd.DataFrame(rows).to_excel(path, index=False)
    return path


def test_get_top_matches_returns_results(tmp_path, config_override):
    faculty_path = write_excel(
        tmp_path,
        "faculty.xlsx",
        [
            {
                "Name": "Dr. Pulmonary",
                "Degree": "MD",
                "Rank": "Professor",
                "Division ": "Neonatology",
                "Career Stage": "Mid",
                "Keywords": "Pulmonary, Neonatology",
            }
        ],
    )
    foundation_path = write_excel(
        tmp_path,
        "foundations.xlsx",
        [
            {
                "Foundation name": "Pulmonary Fund",
                "area(s) of funding": "Pulmonary research",
                "average grant amount": "High",
                "career stage targeted": "Mid",
                "Deadlines, restrictions": "July",
                "institution specific preferences": "",
                "Website link": "https://example.com",
                "Keywords": "Pulmonary",
            }
        ],
    )

    result = verification.get_top_matches(
        "Dr. Pulmonary",
        faculty_path,
        foundation_path,
        top=3,
    )

    assert result.faculty_name == "Dr. Pulmonary"
    assert len(result.matches) == 1
    assert result.matches[0].foundation.name == "Pulmonary Fund"
    assert "pulmonary" in result.matches[0].match_reason
