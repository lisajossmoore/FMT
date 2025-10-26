import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from fmt_tool import match, models  # noqa: E402


def make_faculty(
    *,
    name: str,
    keywords: set[str],
    row: int = 2,
) -> models.FacultyRecord:
    return models.FacultyRecord(
        name=name,
        degree="MD",
        rank="Professor",
        division="Neonatology",
        career_stage="Mid",
        keywords=keywords,
        raw_row_index=row,
    )


def make_foundation(
    *,
    name: str,
    keywords: set[str],
    row: int = 2,
) -> models.FoundationRecord:
    return models.FoundationRecord(
        name=name,
        areas_of_funding="Area",
        average_grant_amount="High",
        career_stage_targeted="Mid",
        deadlines="June",
        institution_preferences="",
        website="https://example.com",
        keywords=keywords,
        raw_row_index=row,
    )


def test_calculate_score_full_overlap():
    score, matched = match.calculate_score({"a", "b"}, {"a", "b", "c"})
    assert score == 100
    assert matched == {"a", "b"}


def test_calculate_score_partial_overlap():
    score, matched = match.calculate_score({"a", "b", "c", "d", "e"}, {"a", "c", "z"})
    assert score == 40  # 2/5 -> 0.4 -> 40%
    assert matched == {"a", "c"}


def test_calculate_score_no_overlap():
    score, matched = match.calculate_score({"a"}, {"b"})
    assert score == 0
    assert matched == set()


def test_generate_matches_sorted_and_includes_rationale():
    faculty = [
        make_faculty(name="Dr. A", keywords={"neonatology", "lung", "bpd"}),
        make_faculty(name="Dr. B", keywords={"cardiology"}, row=3),
    ]
    foundations = [
        make_foundation(name="Pulmonary Fund", keywords={"lung", "neonatology"}),
        make_foundation(name="Newborn Trust", keywords={"neonatology"}),
        make_foundation(name="Heart Fund", keywords={"cardiology"}),
    ]

    matches = match.generate_matches(faculty, foundations)

    assert len(matches) == 3

    first = matches[0]
    assert first.faculty.name == "Dr. A"
    assert first.foundation.name == "Pulmonary Fund"
    assert first.score == 66  # 2/3 -> 66%
    assert first.matched_keywords == ["lung", "neonatology"]
    assert first.faculty_keyword_count == 3
    assert first.foundation_keyword_count == 2

    second = matches[1]
    assert second.foundation.name == "Newborn Trust"
    assert second.score == 33  # 1/3 -> 33%

    third = matches[2]
    assert third.faculty.name == "Dr. B"
    assert third.foundation.name == "Heart Fund"
    assert third.score == 100


def test_generate_matches_skips_empty_keywords_and_warns():
    faculty = [
        make_faculty(name="Dr. A", keywords=set()),
    ]
    foundations = [
        make_foundation(name="Pulmonary Fund", keywords={"pulmonary"}),
    ]

    warnings: list[str] = []
    matches = match.generate_matches(faculty, foundations, warnings=warnings)

    assert matches == []
    assert any("Dr. A" in warning for warning in warnings)


def test_generate_matches_warns_on_foundation_missing_keywords():
    faculty = [
        make_faculty(name="Dr. A", keywords={"pulmonary"}),
    ]
    foundations = [
        make_foundation(name="Pulmonary Fund", keywords=set()),
    ]

    warnings: list[str] = []
    matches = match.generate_matches(faculty, foundations, warnings=warnings)

    assert matches == []
    assert any("Pulmonary Fund" in warning for warning in warnings)
    assert len(warnings) == 1


def test_group_matches_by_faculty_preserves_order():
    faculty = [
        make_faculty(name="Dr. A", keywords={"neonatology", "lung"}),
        make_faculty(name="Dr. B", keywords={"cardiology"}),
    ]
    foundations = [
        make_foundation(name="Pulmonary Fund", keywords={"neonatology"}),
        make_foundation(name="Heart Fund", keywords={"cardiology"}),
    ]
    matches = match.generate_matches(faculty, foundations)

    grouped = match.group_matches_by_faculty(matches)

    assert list(grouped.keys()) == ["Dr. A", "Dr. B"]
    assert [m.foundation.name for m in grouped["Dr. A"]] == ["Pulmonary Fund"]
    assert [m.foundation.name for m in grouped["Dr. B"]] == ["Heart Fund"]
