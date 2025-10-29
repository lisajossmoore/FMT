import sys
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from fmt_tool import config  # noqa: E402
from fmt_tool import errors  # noqa: E402


def clear_env(monkeypatch):
    monkeypatch.delenv("FMT_CONFIG_PATH", raising=False)


def test_load_matching_config_defaults(monkeypatch, tmp_path):
    clear_env(monkeypatch)

    cfg = config.load_matching_config()

    assert cfg.similarity_threshold == pytest.approx(0.6)
    assert cfg.use_weights is False
    assert cfg.keyword_weight == pytest.approx(0.6)
    assert cfg.grant_weight == pytest.approx(0.2)
    assert cfg.stage_weight == pytest.approx(0.2)
    assert cfg.synonyms == {}
    assert "neonatal" in cfg.ignored_tokens


def test_load_matching_config_from_custom_file(monkeypatch, tmp_path):
    custom_config = tmp_path / "custom_settings.toml"
    custom_config.write_text(
        "[matching]\n"
        "similarity_threshold = 0.75\n"
        "use_weights = true\n"
        "keyword_weight = 0.5\n"
        "grant_weight = 0.3\n"
        "stage_weight = 0.2\n"
        'ignored_tokens = ["foo", "bar"]\n'
        'synonyms = { BPD = ["bronchopulmonary dysplasia"] }\n',
        encoding="utf-8",
    )
    monkeypatch.setenv("FMT_CONFIG_PATH", str(custom_config))

    matching_config = config.load_matching_config()

    assert matching_config.similarity_threshold == pytest.approx(0.75)
    assert matching_config.use_weights is True
    assert matching_config.keyword_weight == pytest.approx(0.5)
    assert matching_config.grant_weight == pytest.approx(0.3)
    assert matching_config.stage_weight == pytest.approx(0.2)
    assert matching_config.synonyms["bpd"] == ["bronchopulmonary dysplasia"]
    assert matching_config.ignored_tokens.issuperset({"foo", "bar"})


def test_invalid_threshold_raises(monkeypatch, tmp_path):
    bad_config = tmp_path / "bad_settings.toml"
    bad_config.write_text(
        '[matching]\nsimilarity_threshold = 1.5\nignored_tokens = ["foo"]\n',
        encoding="utf-8",
    )
    monkeypatch.setenv("FMT_CONFIG_PATH", str(bad_config))

    with pytest.raises(errors.FMTValidationError):
        config.load_matching_config()
