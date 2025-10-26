## TDD 003 – Matching Engine & Scoring

### Objective
Transform normalized faculty and foundation datasets into ranked opportunity matches, capturing match scores and keyword rationale for downstream reporting.

### Scope
- Implement `src/fmt_tool/match.py` with a `generate_matches(faculty_records, foundation_records) -> list[MatchResult]`.  
- Include helper functions for keyword normalization reuse, score calculation, and filtering.  
- Support a single matching profile for v0.1.0 (no strict/broad differentiation), but architect functions to accommodate future profiles.

### Matching Model
- **Keyword Comparison**: Treat both faculty and foundation keywords as lowercase token sets.  
- **Score Definition**:  
  - Base score = `(matched_keyword_count / faculty_keyword_count) * 100`.  
  - If faculty has zero keywords, skip match generation and surface warning (handled in ingestion).  
  - Cap score at 100; round to nearest integer for reporting.  
- **Match Inclusion Rule**:  
  - Only include pairs with at least one overlapping keyword.  
  - If foundation has no keywords, skip and record warning.  
- **Rationale Capture**: store sorted list of matched keywords to provide traceability.

### Data Structures
- `MatchResult` dataclass fields:  
  - `faculty` (FacultyRecord reference)  
  - `foundation` (FoundationRecord reference)  
  - `score` (int)  
  - `matched_keywords` (list[str])  
  - `additional_context` (dict for future use; include `faculty_keyword_count`, `foundation_keyword_count`)

### Implementation Notes
1. **Reusability**  
   - Provide `calculate_score(faculty_keywords: set[str], foundation_keywords: set[str]) -> tuple[int, set[str]]`.  
   - Keep pure functions to ease unit testing.  
2. **Performance**  
   - Data scale is small; nested loops acceptable.  
   - Still, consider caching foundation keyword sets if extended metadata added later.  
3. **Warning Propagation**  
   - Accept optional `warnings` list parameter to append contextual warnings (e.g., foundation missing keywords).  
4. **Future Flexibility**  
   - Stub optional `profile` parameter defaulting to `"standard"` to allow later strict/broad profiles without refactoring CLI.  
5. **Sort Order**  
   - Downstream expects results grouped by faculty with descending score; provide helper `group_matches_by_faculty(matches)` returning dict keyed by faculty.
6. **TDD Requirements**  
   - Introduce failing pytest tests in `tests/test_match.py` specifying score calculations, filtering rules, and ordering before coding the implementation.  
   - Execute `ruff check` alongside tests to ensure stylistic consistency.

### Acceptance Criteria
- Faculty without keyword overlap do not produce match entries.  
- Score computation matches specification (e.g., 3 overlaps out of 5 faculty keywords → 60).  
- Matched keyword rationale retained for rendering.  
- Function handles empty foundation keyword sets by skipping and emitting warning.

### Testing Strategy
- Pytest-first development: create tests that fail prior to implementing the matching logic.  
- Unit tests for `calculate_score` covering edge cases (no overlap, full overlap, empty keyword sets).  
- Unit test verifying `generate_matches` returns expected matches for small synthetic datasets.  
- Ensure deterministic output ordering (sorted descending by score, then foundation name) to simplify testing and reporting.  
- Run `ruff check`/`ruff format` as part of completion criteria.
