import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from fmt_tool import match  # noqa: E402


def test_pairwise_best_scores_prefers_closest_match():
    best, pairs = match._pairwise_best_scores(
        ["pulmonary hypertension", "lung"],
        ["pulmonary hypertension", "career development"],
    )

    assert best == 100
    assert pairs[0].faculty_phrase == "pulmonary hypertension"
    assert pairs[0].foundation_phrase == "pulmonary hypertension"


def test_pairwise_best_scores_returns_sorted_pairs():
    _, pairs = match._pairwise_best_scores(
        ["lung disease", "bronchopulmonary dysplasia"],
        ["lung disease", "bpd"],
    )

    assert [pair.faculty_phrase for pair in pairs] == [
        pair.faculty_phrase
        for pair in sorted(pairs, key=lambda p: (-p.score, p.faculty_phrase))
    ]
    phrases = {pair.faculty_phrase for pair in pairs}
    assert "bronchopulmonary dysplasia" in phrases
    assert "lung disease" in phrases
