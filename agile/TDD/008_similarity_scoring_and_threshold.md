## TDD 008 – Similarity Scoring & Threshold

### Objective
Introduce a composite similarity score that blends token overlap with spaCy vector similarity, enforce a configurable threshold, and output normalized 0–100 scores for reporting.

### Scope
- Implement new functions in `fmt_tool/match.py` (or dedicated module) to calculate similarity using normalized keywords produced by TDD 007.  
- Blend two components:  
  1. Token overlap percentage (matched tokens / faculty tokens).  
  2. spaCy vector similarity between faculty and foundation keyword docs.  
- Apply weighted average (default: 70% overlap, 30% vector similarity) configurable via TOML.  
- Enforce numeric threshold from config to filter matches; retain ability to sort and report scores.  
- Update match warnings to reflect situations where vector similarity cannot be computed (e.g., empty vectors).

### Dependencies & Constraints
- Relies on TDD 006 config loader for `similarity_threshold` and optional weights `overlap_weight`, `vector_weight`.  
- Uses normalization from TDD 007 to supply tokens and spaCy docs.  
- Strict TDD required; tests before implementation.  
- Keep deterministic scores for testing (careful with float rounding).

### Implementation Notes
1. **Config Values**  
   - Defaults: `similarity_threshold = 0.6`, `overlap_weight = 0.7`, `vector_weight = 0.3`.  
   - Validate that weights sum to 1.0 (within epsilon); otherwise raise `FMTValidationError`.  
   - Allow optional override via `config/settings.toml`.
2. **Scoring Function**  
   - Inputs: faculty tokens/doc, foundation tokens/doc, config weights.  
   - Calculate:  
     - `overlap_score = matched_token_count / len(faculty_tokens)` (0 if faculty tokens empty).  
     - `vector_score = doc1.similarity(doc2)`; if vectors missing, fallback to 0 and log warning.  
   - Weighted average: `composite = overlap_weight * overlap_score + vector_weight * vector_score`.  
   - Clamp composite to [0, 1]; convert to integer 0–100 for reporting.
3. **Threshold Filtering**  
   - Compare composite score (0–1) against `similarity_threshold`.  
   - Only create `MatchResult` when score >= threshold.  
   - Store both integer score and raw composite for debugging (maybe via `additional_context`).
4. **Sorting & Reporting**  
   - Continue ordering matches by descending score, then name.  
   - Update narrative (match rationale) to include key matched tokens even when vector similarity drives the match.
5. **Warnings**  
   - Append warning if either party has no tokens (should be handled earlier but double-check).  
   - Warn if spaCy similarity falls back due to zero vectors (rare for empty docs).

### Acceptance Criteria
1. Weight validation: config with weights summing to 1 passes; invalid sums raise descriptive error.  
2. Faculty with tokens {“pulmonary hypertension”} and foundation tokens {“neonatal and pediatric pulmonary hypertension”} produce composite score >= threshold (expected >0.6).  
3. Cases with token overlap but low vector similarity (e.g., shared generic terms) produce lower composite scores, demonstrating tunability.  
4. Scores output as integers 0–100; internal composite stored (if needed) without rounding errors in tests.  
5. Threshold filters out low-scoring matches; tests assert matches below threshold are excluded.  
6. CLI summary still reports match counts correctly.

### Testing Strategy
- Add `tests/test_similarity.py` focusing on:  
  - Weighted average calculation with fixtures for spaCy docs (use normalization helpers).  
  - Threshold filtering behavior (under/over boundary).  
  - Weight validation errors.  
  - Handling of missing tokens or vector similarity fallback.  
- Update `tests/test_match.py` to use new scoring function (TDD-first: adjust tests so they fail prior to implementation).  
- Use pytest fixtures to reuse spaCy pipeline introduced earlier.  
- Run `script/test.sh` to ensure lint/tests pass.
