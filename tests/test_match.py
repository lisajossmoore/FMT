import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from fmt_tool import config as config_module, match, models  # noqa: E402


def make_faculty(
    *,
    name: str,
    phrases: list[str],
    row: int = 2,
) -> models.FacultyRecord:
    ignored = {
        "and",
        "in",
        "career",
        "development",
        "prevention",
        "care",
        "early",
        "neonatal",
    }
    keywords = {
        token for phrase in phrases for token in phrase.split() if token not in ignored
    }
    return models.FacultyRecord(
        name=name,
        degree="MD",
        rank="Professor",
        division="Neonatology",
        career_stage="Mid",
        keywords=keywords,
        keywords_phrases=phrases,
        raw_row_index=row,
    )


def make_foundation(
    *,
    name: str,
    phrases: list[str],
    row: int = 2,
) -> models.FoundationRecord:
    ignored = {
        "and",
        "in",
        "career",
        "development",
        "prevention",
        "care",
        "early",
        "neonatal",
    }
    keywords = {
        token for phrase in phrases for token in phrase.split() if token not in ignored
    }
    return models.FoundationRecord(
        name=name,
        areas_of_funding="Area",
        average_grant_amount="High",
        career_stage_targeted="Mid",
        deadlines="June",
        institution_preferences="",
        website="https://example.com",
        keywords=keywords,
        keywords_phrases=phrases,
        raw_row_index=row,
    )


def make_config(
    threshold: float = 0.6,
    *,
    use_weights: bool = False,
    keyword_weight: float = 0.6,
    grant_weight: float = 0.2,
    stage_weight: float = 0.2,
):
    return config_module.MatchingConfig(
        similarity_threshold=threshold,
        use_weights=use_weights,
        keyword_weight=keyword_weight,
        grant_weight=grant_weight,
        stage_weight=stage_weight,
        synonyms={},
        ignored_tokens={
            "and",
            "in",
            "career",
            "development",
            "prevention",
            "care",
            "early",
            "neonatal",
        },
    )


def test_generate_matches_sorted_and_includes_rationale():
    faculty = [
        make_faculty(name="Dr. A", phrases=["neonatal lung", "bpd"]),
        make_faculty(name="Dr. B", phrases=["cardiology"], row=3),
    ]
    foundations = [
        make_foundation(name="Pulmonary Fund", phrases=["lung", "neonatology"]),
        make_foundation(name="Newborn Trust", phrases=["neonatal research"]),
        make_foundation(name="Heart Fund", phrases=["cardiology"]),
    ]

    matches = match.generate_matches(
        faculty,
        foundations,
        matching_config=make_config(threshold=0.3),
    )

    assert len(matches) == 3

    first = matches[0]
    assert first.faculty.name == "Dr. A"
    assert first.foundation.name == "Pulmonary Fund"
    assert 0 <= first.score <= 100
    assert first.matched_keywords == ["neonatal lung"]
    assert "Pulmonary Fund" in first.match_reason
    assert first.keyword_match_count >= 1
    assert first.keyword_score == first.score
    assert first.weighted_score is None

    second = matches[1]
    assert second.foundation.name == "Newborn Trust"
    assert second.score >= 60

    third = matches[2]
    assert third.faculty.name == "Dr. B"
    assert third.foundation.name == "Heart Fund"
    assert third.score >= 60


def test_generate_matches_skips_empty_keywords_and_warns():
    faculty = [
        make_faculty(name="Dr. A", phrases=[]),
    ]
    foundations = [
        make_foundation(name="Pulmonary Fund", phrases=["pulmonary"]),
    ]

    warnings: list[str] = []
    matches = match.generate_matches(
        faculty,
        foundations,
        warnings=warnings,
        matching_config=make_config(threshold=0.5),
    )

    assert matches == []


def test_generate_matches_with_weights():
    faculty = [make_faculty(name="Dr. Weighted", phrases=["pulmonary hypertension"])]
    foundations = [
        make_foundation(name="High Grant", phrases=["pulmonary hypertension"], row=2),
        make_foundation(name="Low Grant", phrases=["pulmonary hypertension"], row=3),
    ]

    config = make_config(threshold=0.6, use_weights=True)

    matches = match.generate_matches(
        faculty,
        foundations,
        matching_config=config,
    )

    assert matches[0].foundation.name == "High Grant"
    assert matches[0].score >= matches[1].score
    assert matches[0].weighted_score is not None
    assert matches[0].keyword_score <= matches[0].score


def test_generate_matches_warns_on_foundation_missing_keywords():
    faculty = [
        make_faculty(name="Dr. A", phrases=["pulmonary"]),
    ]
    foundations = [
        make_foundation(name="Pulmonary Fund", phrases=[]),
    ]

    warnings: list[str] = []
    matches = match.generate_matches(
        faculty,
        foundations,
        warnings=warnings,
        matching_config=make_config(threshold=0.5),
    )

    assert matches == []
    assert any("Pulmonary Fund" in warning for warning in warnings)
    assert len(warnings) == 1


def test_group_matches_by_faculty_preserves_order():
    faculty = [
        make_faculty(name="Dr. A", phrases=["neonatal lung"]),
        make_faculty(name="Dr. B", phrases=["cardiology"]),
    ]
    foundations = [
        make_foundation(name="Pulmonary Fund", phrases=["neonatal lung"]),
        make_foundation(name="Heart Fund", phrases=["cardiology"]),
    ]
    matches = match.generate_matches(
        faculty,
        foundations,
        matching_config=make_config(threshold=0.5),
    )

    grouped = match.group_matches_by_faculty(matches)

    assert list(grouped.keys()) == ["Dr. A", "Dr. B"]
    assert [m.foundation.name for m in grouped["Dr. A"]] == ["Pulmonary Fund"]
    assert [m.foundation.name for m in grouped["Dr. B"]] == ["Heart Fund"]


def test_generate_matches_respects_threshold():
    faculty = [make_faculty(name="Dr. C", phrases=["pulmonary hypertension", "lung"])]
    foundations = [
        make_foundation(name="Pulmonary Fund", phrases=["pulmonary hypertension"]),
        make_foundation(name="Cardio Fund", phrases=["hypertension support"]),
    ]

    low_threshold_matches = match.generate_matches(
        faculty,
        foundations,
        matching_config=make_config(threshold=0.2),
    )
    assert len(low_threshold_matches) == 2

    high_threshold_matches = match.generate_matches(
        faculty,
        foundations,
        matching_config=make_config(threshold=0.95),
    )
    assert len(high_threshold_matches) == 1


def test_generate_matches_requires_non_stopword_keywords():
    faculty = [make_faculty(name="Dr. Generic", phrases=["career development"])]
    foundations = [
        make_foundation(name="Generic Fund", phrases=["career early"]),
        make_foundation(name="Specific Fund", phrases=["pulmonary"]),
    ]

    matches = match.generate_matches(
        faculty,
        foundations,
        matching_config=make_config(threshold=0.3),
    )

    assert matches == []
