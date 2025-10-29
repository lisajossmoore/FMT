import sys
from datetime import datetime
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from fmt_tool import models, render  # noqa: E402


def sample_run_context(tmp_path: Path) -> models.RunContext:
    return models.RunContext(
        timestamp=datetime(2025, 1, 15, 10, 30),
        operator="Alex Operator",
        run_label="Spring 2025",
        faculty_source=tmp_path / "faculty.xlsx",
        foundation_source=tmp_path / "foundations.xlsx",
        output_path=tmp_path / "output.xlsx",
        weighted_mode=False,
        warnings=["Faculty 'Dr. B' missing keywords (row 4)."],
    )


def make_match(
    faculty_name: str,
    foundation_name: str,
    score: int,
    matched_keywords: list[str],
) -> models.MatchResult:
    faculty = models.FacultyRecord(
        name=faculty_name,
        degree="MD",
        rank="Professor",
        division="Neonatology",
        career_stage="Mid",
        keywords=set(word for phrase in matched_keywords for word in phrase.split()),
        keywords_phrases=matched_keywords,
        raw_row_index=2,
    )
    foundation = models.FoundationRecord(
        name=foundation_name,
        areas_of_funding="Pulmonary research",
        average_grant_amount="High",
        career_stage_targeted="Mid",
        deadlines="July 15",
        institution_preferences="Utah preferred",
        website="https://example.com",
        keywords=set(word for phrase in matched_keywords for word in phrase.split()),
        keywords_phrases=matched_keywords,
        raw_row_index=5,
    )
    return models.MatchResult(
        faculty=faculty,
        foundation=foundation,
        score=score,
        raw_score=score / 100,
        keyword_score=score,
        weighted_score=None,
        matched_keywords=matched_keywords,
        faculty_keyword_count=len(faculty.keywords_phrases),
        foundation_keyword_count=len(foundation.keywords_phrases),
        keyword_match_count=len(matched_keywords),
        match_reason="; ".join(f"{kw} ~ {kw} ({score})" for kw in matched_keywords),
    )


def test_build_workbook_creates_summary_and_neonatology(tmp_path):
    matches = [
        make_match("Dr. A", "Pulmonary Fund", 80, ["lung", "bpd"]),
        make_match("Dr. A", "Neonate Trust", 60, ["neonatology"]),
        make_match("Dr. C", "Respiratory Alliance", 40, ["respiratory"]),
    ]
    grouped = render.group_matches_by_division(matches)
    context = sample_run_context(tmp_path)

    workbook = render.build_workbook(grouped, context)

    assert "Summary" in workbook.sheetnames
    assert "Neonatology" in workbook.sheetnames
    assert "Meta" not in workbook.sheetnames

    summary_sheet = workbook["Summary"]
    assert summary_sheet["B2"].value == "Alex Operator"
    assert summary_sheet["B1"].value == "2025-01-15T10:30:00"
    assert "Faculty 'Dr. B' missing keywords" in summary_sheet["B7"].value

    data_sheet = workbook["Neonatology"]
    headers = [cell.value for cell in data_sheet[1]]
    assert headers[:7] == [
        "Faculty Name",
        "Faculty Career Stage",
        "Foundation Name",
        "Match Score (0-100)",
        "Matched Keywords",
        "Matched Keyword Count",
        "Why Matched",
    ]
    rows = list(data_sheet.iter_rows(min_row=2, max_col=len(headers), values_only=True))
    assert rows[0][0] == "Dr. A"
    assert rows[0][2] == "Pulmonary Fund"
    assert rows[0][3] == 80
    assert rows[0][4] == "bpd, lung"
    assert rows[0][5] == 2
    assert "lung" in rows[0][6]

    assert rows[1][0] == "Dr. A"
    assert rows[1][2] == "Neonate Trust"
    assert rows[1][3] == 60

    assert rows[2][0] == "Dr. C"
    assert rows[2][2] == "Respiratory Alliance"
    assert rows[2][3] == 40


def test_write_workbook_creates_directories(tmp_path):
    matches = []
    grouped = render.group_matches_by_division(matches)
    context = sample_run_context(tmp_path)
    workbook = render.build_workbook(grouped, context)

    output_path = tmp_path / "output" / "digest.xlsx"
    render.write_workbook(workbook, output_path)

    assert output_path.exists()


def test_build_workbook_handles_no_matches(tmp_path):
    grouped = {"Neonatology": []}
    context = sample_run_context(tmp_path)

    workbook = render.build_workbook(grouped, context)

    data_sheet = workbook["Neonatology"]
    assert data_sheet.max_row == 1  # only headers


def test_build_workbook_weighted_includes_meta_and_column(tmp_path):
    matches = [
        models.MatchResult(
            faculty=models.FacultyRecord(
                name="Dr. Weighted",
                degree="MD",
                rank="Professor",
                division="Neonatology",
                career_stage="Mid",
                keywords={"pulmonary"},
                keywords_phrases=["pulmonary"],
                raw_row_index=4,
            ),
            foundation=models.FoundationRecord(
                name="Pulmonary Fund",
                areas_of_funding="Pulmonary research",
                average_grant_amount="High",
                career_stage_targeted="Mid",
                deadlines="July",
                institution_preferences="",
                website="https://example.com",
                keywords={"pulmonary"},
                keywords_phrases=["pulmonary"],
                raw_row_index=10,
            ),
            score=90,
            raw_score=0.9,
            keyword_score=70,
            weighted_score=90,
            matched_keywords=["pulmonary"],
            faculty_keyword_count=1,
            foundation_keyword_count=1,
            keyword_match_count=1,
            match_reason="Pulmonary Fund: pulmonary ~ pulmonary (100)",
        )
    ]
    grouped = {"Neonatology": matches}
    context = models.RunContext(
        timestamp=datetime(2025, 1, 15, 10, 30),
        operator="Casey",
        run_label=None,
        faculty_source=tmp_path / "faculty.xlsx",
        foundation_source=tmp_path / "foundations.xlsx",
        output_path=tmp_path / "digest.xlsx",
        weighted_mode=True,
        warnings=[],
    )

    workbook = render.build_workbook(grouped, context)

    assert "Meta" in workbook.sheetnames
    data_sheet = workbook["Neonatology"]
    headers = [cell.value for cell in data_sheet[1]]
    assert "Weighted Score (0-100)" in headers
    row = next(data_sheet.iter_rows(min_row=2, max_row=2, values_only=True))
    assert row[3] == 70
    assert row[4] == 90
