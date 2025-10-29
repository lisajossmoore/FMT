"""Configuration loading utilities for the Foundation Matching Tool."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import tomllib

from .errors import FMTValidationError

_ENV_CONFIG_PATH = "FMT_CONFIG_PATH"
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_DEFAULTS_PATH = _PROJECT_ROOT / "config" / "defaults.toml"
_DEFAULT_CONFIG_PATH = _PROJECT_ROOT / "config" / "settings.toml"


@dataclass(slots=True)
class MatchingConfig:
    """Configuration values influencing matching behavior."""

    similarity_threshold: float = 0.6
    use_weights: bool = False
    keyword_weight: float = 0.6
    grant_weight: float = 0.2
    stage_weight: float = 0.2
    synonyms: dict[str, list[str]] = field(default_factory=dict)
    ignored_tokens: set[str] = field(default_factory=set)


def load_matching_config() -> MatchingConfig:
    """Load matching configuration, applying defaults and validation."""

    defaults = _load_toml(_DEFAULTS_PATH)
    user_values = _load_user_config()

    default_threshold = _extract_threshold(defaults)
    override_threshold = _extract_threshold(user_values, required=False)

    threshold = (
        float(override_threshold)
        if override_threshold is not None
        else float(default_threshold)
    )

    _validate_threshold(threshold, source="configuration")

    keyword_weight, grant_weight, stage_weight = _extract_scoring_weights(defaults)
    override_weights = _extract_scoring_weights(user_values, required=False)
    if override_weights is not None:
        keyword_weight, grant_weight, stage_weight = override_weights

    _validate_scoring_weights(keyword_weight, grant_weight, stage_weight)

    use_weights = _extract_bool(user_values, "matching", "use_weights", default=False)

    synonyms = _extract_synonyms(defaults)
    user_synonyms = _extract_synonyms(user_values, required=False)
    if user_synonyms:
        synonyms.update(user_synonyms)

    ignored_tokens = set(_extract_ignored_tokens(defaults))
    override_ignored = _extract_ignored_tokens(user_values, required=False)
    if override_ignored is not None:
        ignored_tokens.update(override_ignored)

    return MatchingConfig(
        similarity_threshold=threshold,
        use_weights=use_weights,
        keyword_weight=keyword_weight,
        grant_weight=grant_weight,
        stage_weight=stage_weight,
        synonyms=synonyms,
        ignored_tokens=ignored_tokens,
    )


def _load_user_config() -> dict[str, Any]:
    env_value = os.environ.get(_ENV_CONFIG_PATH)
    if env_value:
        user_path = Path(env_value)
        if not user_path.exists():
            raise FMTValidationError(
                f"Configuration file specified by {_ENV_CONFIG_PATH} not found: {user_path}"
            )
        if not user_path.is_file():
            raise FMTValidationError(
                f"Configuration path specified by {_ENV_CONFIG_PATH} is not a file: {user_path}"
            )
        return _load_toml(user_path)

    if _DEFAULT_CONFIG_PATH.is_file():
        return _load_toml(_DEFAULT_CONFIG_PATH)

    return {}


def _load_toml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FMTValidationError(f"Required configuration file missing: {path}")
    with path.open("rb") as handle:
        return tomllib.load(handle)


def _extract_threshold(
    data: dict[str, Any],
    *,
    required: bool = True,
) -> float | None:
    matching_section = data.get("matching", {})
    value = matching_section.get("similarity_threshold")
    if value is None:
        if required:
            raise FMTValidationError(
                "Default configuration missing 'matching.similarity_threshold'."
            )
        return None
    if not isinstance(value, (int, float)):
        raise FMTValidationError(
            "Configuration value 'matching.similarity_threshold' must be numeric."
        )
    return float(value)


def _extract_synonyms(
    data: dict[str, Any],
    *,
    required: bool = False,
) -> dict[str, list[str]]:
    matching_section = data.get("matching", {})
    raw_synonyms = matching_section.get("synonyms")
    if raw_synonyms is None:
        if required:
            raise FMTValidationError(
                "Default configuration missing 'matching.synonyms'."
            )
        return {}

    if not isinstance(raw_synonyms, dict):
        raise FMTValidationError("Configuration 'matching.synonyms' must be a mapping.")

    normalized: dict[str, list[str]] = {}
    for key, values in raw_synonyms.items():
        if not isinstance(key, str):
            raise FMTValidationError("Synonym keys must be strings.")
        if isinstance(values, str):
            normalized[key.lower()] = [values.lower()]
        elif isinstance(values, list):
            normalized[key.lower()] = [
                str(item).lower() for item in values if str(item).strip()
            ]
        else:
            raise FMTValidationError(
                "Synonym values must be a string or list of strings."
            )
    return normalized


def _validate_threshold(value: float, *, source: str) -> None:
    if not 0.0 <= value <= 1.0:
        raise FMTValidationError(
            f"{source.capitalize()} similarity_threshold must be between 0 and 1; got {value}."
        )


def _extract_scoring_weights(
    data: dict[str, Any],
    *,
    required: bool = True,
) -> tuple[float, float, float] | None:
    matching_section = data.get("matching", {})
    keyword = matching_section.get("keyword_weight")
    grant = matching_section.get("grant_weight")
    stage = matching_section.get("stage_weight")
    if keyword is None or grant is None or stage is None:
        if required:
            raise FMTValidationError(
                "Configuration missing keyword, grant, or stage weights."
            )
        return None
    if not all(isinstance(value, (int, float)) for value in (keyword, grant, stage)):
        raise FMTValidationError("Scoring weights must be numeric values.")
    return float(keyword), float(grant), float(stage)


def _validate_scoring_weights(keyword: float, grant: float, stage: float) -> None:
    total = keyword + grant + stage
    for value in (keyword, grant, stage):
        if not 0.0 <= value <= 1.0:
            raise FMTValidationError("Scoring weights must be between 0 and 1.")
    if abs(total - 1.0) > 1e-6:
        raise FMTValidationError(f"Scoring weights must sum to 1.0; got {total}.")


def _extract_bool(
    data: dict[str, Any],
    section: str,
    key: str,
    *,
    default: bool = False,
) -> bool:
    section_values = data.get(section, {})
    value = section_values.get(key)
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "yes", "1"}:
            return True
        if lowered in {"false", "no", "0"}:
            return False
    raise FMTValidationError(f"Configuration value '{section}.{key}' must be boolean.")


def _extract_ignored_tokens(
    data: dict[str, Any],
    *,
    required: bool = True,
) -> list[str] | None:
    matching_section = data.get("matching", {})
    tokens = matching_section.get("ignored_tokens")
    if tokens is None:
        if required:
            raise FMTValidationError("Configuration missing 'matching.ignored_tokens'.")
        return None
    if not isinstance(tokens, list):
        raise FMTValidationError("'matching.ignored_tokens' must be a list.")
    normalized: list[str] = []
    for value in tokens:
        if not isinstance(value, str):
            raise FMTValidationError("All ignored token entries must be strings.")
        token = value.strip().lower()
        if token:
            normalized.append(token)
    return normalized
