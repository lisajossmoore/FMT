## TDD 009 – Pipeline Integration & Verification Upgrade

### Objective
Wire the new NLP normalization and similarity scoring into the existing pipeline, update outputs/documentation, and provide a helper script for quick match verification.

### Scope
- Update `fmt_tool/pipeline.py` to use the new config loader (TDD 006), normalization (TDD 007), and scoring (TDD 008).  
- Ensure warnings and run context include info relevant to NLP failures (e.g., model missing, zero vectors).  
- Adjust output summary (if needed) to reflect new scoring behavior while keeping format stable.  
- Add `script/verify_match.py` that loads the pipeline components to display top matches for a specified faculty (e.g., Matthew Douglass) using current spreadsheets.  
- Update README with instructions for configuring threshold and running the verification script.  
- Maintain strict TDD: tests before code changes.

### Dependencies & Constraints
- Depends on completed TDDs 006–008.  
- CLI interface remains unchanged.  
- Verification script should reuse pipeline logic; avoid duplicating matching code.  
- Tests must remain reliable even when spaCy model is required (reuse fixtures).  
- Keep runtime reasonable; verification script should execute quickly on sample data.

### Implementation Notes
1. **Pipeline Wiring**  
   - Retrieve matching config via `fmt_tool.config.load_matching_config()`.  
   - Pass config into normalization and scoring steps (through `match.generate_matches`).  
   - Combine ingestion warnings with NLP/scoring warnings; dedupe as before.  
2. **Logging/Warnings**  
   - If spaCy model missing, propagate meaningful `FMTError`.  
   - When fallback behavior occurs (e.g., zero vector similarity), include message in warnings list.  
3. **Output Adjustments**  
   - Ensure Summary sheet still reports counts; optionally add threshold info if helpful for QA (but not mandatory).  
   - Confirm match scores reflect new composite metric (0–100).  
   - Add mention in README that scores now blend overlap + semantic similarity.  
4. **Verification Script (`script/verify_match.py`)**  
   - Usage: `python script/verify_match.py --faculty "Matthew Douglass" --top 5`.  
   - Loads config, ingestion, normalization, scoring, prints top matches with scores and matched phrases.  
   - Provide default file paths (data/faculty.xlsx, data/foundations.xlsx) with overrides if desired.  
5. **Documentation**  
   - README: configuration guidance, example threshold tuning, and verification script usage.  
   - Mention that the script helps QA teams confirm known matches.

### Acceptance Criteria
1. Pipeline uses new normalization/scoring, producing non-zero matches on current spreadsheets at default threshold.  
2. Warnings list includes any NLP-related issues when encountered.  
3. `script/verify_match.py --faculty "Matthew Douglass"` prints at least one relevant foundation with score ≥ threshold.  
4. README updated with NLP setup, config instructions, threshold explanation, and verification script example.  
5. All tests (existing + new) pass via `script/test.sh`.

### Testing Strategy
- Update `tests/test_pipeline.py` to expect matches after integration (TDD-first: adjust assertions before touching code).  
- Add tests for verification script (e.g., using `subprocess` or invoking helper function) ensuring it returns expected output for known cases (can mock small datasets).  
- Integration test ensuring pipeline run raises clear error when spaCy model missing (simulate via env var).  
- Ensure existing tests (ingest, match, render) still pass with new behavior.  
- Follow red→green workflow: failing tests first, then implementation, then refactor.
