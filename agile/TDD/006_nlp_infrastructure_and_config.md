## TDD 006 – NLP Infrastructure & Configuration

### Objective
Introduce configurable fuzzy-matching support (RapidFuzz) and similarity thresholds without altering the existing CLI surface, laying the groundwork for richer matching.

### Scope
- Add RapidFuzz as a runtime dependency; document installation in README.  
- Load optional configuration from `config/settings.toml`; if absent, fall back to default threshold (0.6).  
- Expose normalized settings via a new `fmt_tool.config` module for downstream components.  
- Ensure strict TDD: tests written before implementation.

### Dependencies & Constraints
- Python 3.11 runtime (per ADR 001).  
- RapidFuzz library.  
- Existing toolchain (`pytest`, `ruff`).  
- No new CLI flags; configuration file path is fixed (`config/settings.toml`) with optional overrides available via environment variable `FMT_CONFIG_PATH`.

### Implementation Notes
1. **Dependencies**  
   - Update `requirements.txt` with `rapidfuzz`.  
   - README: note dependency installation.  
2. **Config Module** (`src/fmt_tool/config.py`)  
   - Functions to load TOML (use `tomllib` in Python 3.11).  
   - Default values stored in `config/defaults.toml` (shipped with repo). Include weights, stopwords, and optional `use_weights`.  
   - Environment variable `FMT_CONFIG_PATH` overrides default path.  
3. **Data Model**  
   - Define `MatchingConfig` dataclass with threshold, weighting flags, stopword list, and synonyms.  
   - Validate ranges and weight sums; raise `FMTValidationError` on invalid values.  
4. **Testing**  
   - Pytest module `tests/test_config.py` covering:  
     - Loading defaults when no file present.  
     - Reading threshold/weights from custom TOML (using temp files).  
     - Handling invalid values and error messaging.  
     - Environment variable override precedence.

### Acceptance Criteria
1. `fmt_tool.config.load_matching_config()` returns default threshold/weights when no config file exists.  
2. Custom `config/settings.toml` with overrides (threshold, weights, ignored tokens) is honoured.  
3. Invalid threshold or weight sums raise `FMTValidationError` with descriptive message.  
4. README instructions updated; CI/local lint/tests pass.

### Testing Strategy
- TDD-first: write failing tests in `tests/test_config.py` before implementing `fmt_tool.config`.  
- Use temporary directories/files in tests to simulate presence/absence of configuration.  
- Run `script/test.sh` after implementation to ensure formatting, linting, and tests pass.
