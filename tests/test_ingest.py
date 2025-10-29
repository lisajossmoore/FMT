import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from fmt_tool import errors, ingest, models  # noqa: E402


def write_excel(tmp_path, filename, dataframe):
    path = tmp_path / filename
    dataframe.to_excel(path, index=False)
    return path


def test_load_faculty_success(tmp_path):
    df = pd.DataFrame(
        [
            {
                "Name": "Jane Doe ",
                "Degree": "MD",
                "Rank": "Associate Professor",
                "Division ": "Neonatology ",
                "Career Stage": "Mid",
                "Keywords": "Neonatology, Lung, Pulmonary ",
            },
            {
                "Name": "John Smith",
                "Degree": "PhD",
                "Rank": "Assistant Professor",
                "Division ": "Neonatology",
                "Career Stage": "Early",
                "Keywords": " Neonatal Intensive Care , BPD ",
            },
        ]
    )
    path = write_excel(tmp_path, "faculty.xlsx", df)

    result = ingest.load_faculty(path)

    assert isinstance(result, models.IngestionResult)
    assert result.warnings == []
    assert len(result.records) == 2

    first = result.records[0]
    assert first.name == "Jane Doe"
    assert first.division == "Neonatology"
    assert {"neonatology", "lung", "pulmonary"} <= first.keywords
    assert first.keywords_phrases == ["lung", "neonatology", "pulmonary"]
    assert first.raw_row_index == 2

    second = result.records[1]
    assert second.name == "John Smith"
    assert second.keywords_phrases == ["bpd", "neonatal intensive care"]
    assert "intensive" in second.keywords
    assert second.raw_row_index == 3


def test_load_faculty_missing_required_column(tmp_path):
    df = pd.DataFrame(
        [
            {
                "Name": "Jane Doe",
                "Degree": "MD",
                "Rank": "Associate Professor",
                "Division ": "Neonatology",
                "Keywords": "Neonatology",
            }
        ]
    )
    path = write_excel(tmp_path, "faculty.xlsx", df)

    with pytest.raises(errors.FMTValidationError) as excinfo:
        ingest.load_faculty(path)

    assert "Career Stage" in str(excinfo.value)


def test_load_faculty_warns_on_missing_keywords(tmp_path):
    df = pd.DataFrame(
        [
            {
                "Name": "Jane Doe",
                "Degree": "MD",
                "Rank": "Associate Professor",
                "Division ": "Neonatology",
                "Career Stage": "Mid",
                "Keywords": "",
            }
        ]
    )
    path = write_excel(tmp_path, "faculty.xlsx", df)

    result = ingest.load_faculty(path)

    assert len(result.records) == 1
    assert result.records[0].keywords == set()
    assert any("missing keywords" in warning.lower() for warning in result.warnings)


def test_load_faculty_duplicate_warning(tmp_path):
    df = pd.DataFrame(
        [
            {
                "Name": "Jane Doe",
                "Degree": "MD",
                "Rank": "Associate Professor",
                "Division ": "Neonatology",
                "Career Stage": "Mid",
                "Keywords": "Neonatology",
            },
            {
                "Name": " JANE DOE ",
                "Degree": "MD",
                "Rank": "Professor",
                "Division ": "Neonatology",
                "Career Stage": "Late",
                "Keywords": "Pulmonary",
            },
        ]
    )
    path = write_excel(tmp_path, "faculty.xlsx", df)

    result = ingest.load_faculty(path)

    assert len(result.records) == 2
    assert any("duplicate faculty" in warning.lower() for warning in result.warnings)


def test_load_foundations_success(tmp_path):
    df = pd.DataFrame(
        [
            {
                "Foundation name": "Pulmonary Fund",
                "area(s) of funding": "Pulmonary research ",
                "average grant amount": "High",
                "career stage targeted": "Mid",
                "Deadlines, restrictions": "July 15",
                "institution specific preferences": "Utah institutions preferred",
                "Website link": "https://example.com",
                "Keywords": "Pulmonary, Neonatology",
            },
            {
                "Foundation name": "Neonate Foundation",
                "area(s) of funding": "Neonatal care",
                "average grant amount": "Medium",
                "career stage targeted": "Early",
                "Deadlines, restrictions": "March 1",
                "institution specific preferences": "",
                "Website link": "https://example.org",
                "Keywords": " Neonate ",
            },
        ]
    )
    path = write_excel(tmp_path, "foundations.xlsx", df)

    result = ingest.load_foundations(path)

    assert isinstance(result, models.IngestionResult)
    assert result.warnings == []
    assert len(result.records) == 2

    record = result.records[0]
    assert record.name == "Pulmonary Fund"
    assert {"pulmonary", "neonatology"} <= record.keywords
    assert record.keywords_phrases == ["neonatology", "pulmonary"]
    assert record.raw_row_index == 2


def test_load_foundations_missing_required_column(tmp_path):
    df = pd.DataFrame(
        [
            {
                "Foundation name": "Pulmonary Fund",
                "area(s) of funding": "Pulmonary research",
                "average grant amount": "High",
                "career stage targeted": "Mid",
                "Deadlines, restrictions": "July 15",
                "institution specific preferences": "Utah preferred",
            }
        ]
    )
    path = write_excel(tmp_path, "foundations.xlsx", df)

    with pytest.raises(errors.FMTValidationError) as excinfo:
        ingest.load_foundations(path)

    assert "Website link" in str(excinfo.value)


def test_load_foundations_warns_on_missing_keywords(tmp_path):
    df = pd.DataFrame(
        [
            {
                "Foundation name": "Pulmonary Fund",
                "area(s) of funding": "Pulmonary research",
                "average grant amount": "High",
                "career stage targeted": "Mid",
                "Deadlines, restrictions": "July 15",
                "institution specific preferences": "Utah preferred",
                "Website link": "https://example.com",
                "Keywords": "",
            }
        ]
    )
    path = write_excel(tmp_path, "foundations.xlsx", df)

    result = ingest.load_foundations(path)

    assert len(result.records) == 1
    assert result.records[0].keywords == set()
    assert any("missing keywords" in warning.lower() for warning in result.warnings)


def test_load_faculty_filters_stopwords(tmp_path):
    df = pd.DataFrame(
        [
            {
                "Name": "Dr. Generic",
                "Degree": "MD",
                "Rank": "Professor",
                "Division ": "Neonatology",
                "Career Stage": "Mid",
                "Keywords": "Career, Development, Pulmonary",
            }
        ]
    )
    path = write_excel(tmp_path, "faculty.xlsx", df)

    result = ingest.load_faculty(
        path,
        ignored_tokens={"career", "development"},
    )

    assert len(result.records) == 1
    assert result.records[0].keywords == {"pulmonary"}
