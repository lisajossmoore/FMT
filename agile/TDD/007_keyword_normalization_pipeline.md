## TDD 007 – Keyword Normalization Pipeline

### Objective
Replace the current lowercase/comma-split keyword handling with an NLP-backed normalization pipeline that produces consistent lemmatized tokens and meaningful multi-word terms for matching.

### Scope
- Implement `fmt_tool/nlp.py` (or similar) providing functions to load/reuse a spaCy pipeline and normalize keyword strings.  
- Generate lemmatized unigrams for all tokens and multi-word noun chunks identified by spaCy (e.g., “pulmonary hypertension”).  
- Handle punctuation, case, and abbreviation cleanup (e.g., stripping trailing periods, harmonizing hyphenated terms).  
- Allow optional synonym substitutions via a simple configurable map (JSON/YAML) kept small and maintainable.  
- Ensure deterministic ordering for testing and downstream consumers.

### Dependencies & Constraints
- Depends on spaCy integration and config module from TDD 006.  
- Continue using strict TDD (tests written first).  
- No changes to CLI inputs; normalization happens within ingestion/matching pipeline.  
- Must keep processing performant given ~140 keyword records.

### Implementation Notes
1. **Module Design**  
   - `load_spacy_model()` returning a cached spaCy `Language` object (singleton).  
   - `normalize_keywords(raw: str, language) -> set[str]` performing:  
     - Early return for empty/whitespace strings.  
     - spaCy doc creation.  
     - Collect lemmatized unigrams (alphabetic tokens only).  
     - Collect lemmatized noun chunks (`chunk.lemma_`).  
     - Apply optional synonym map from config (`matching.synonyms`, map of source → replacements).  
     - Return lowercased tokens sorted alphabetically.
2. **Synonyms (Optional)**  
   - Config structure example:  
     ```toml
     [matching.synonyms]
     BPD = ["bronchopulmonary dysplasia"]
     ```
   - Expand synonyms after base normalization.
3. **Integration Touchpoints**  
   - `ingest.load_faculty` and `load_foundations` call normalization instead of `_parse_keywords`.  
   - Update ingestion warnings to reflect empty tokens post-normalization.
4. **Error Handling**  
   - If spaCy model fails to load, raise `FMTError` with guidance to run bootstrap script.  
   - Ensure tests mock spaCy where appropriate to avoid heavy model load per test (fixture to reuse pipeline).

### Acceptance Criteria
1. `normalize_keywords("Pulmonary Hypertension")` returns `{"hypertension", "pulmonary", "pulmonary hypertension"}`.  
2. `normalize_keywords("Inflammatory Responses")` returns `{"inflammatory response", "response"}` (lemma of “responses” is “response”).  
3. Empty or whitespace-only strings yield empty sets and trigger warnings in ingestion.  
4. Synonym entries expand tokens accordingly (e.g., “BPD” includes “bronchopulmonary dysplasia”).  
5. Performance: processing all keywords from sample spreadsheets completes well under 1 second (informal benchmark).  
6. Tests cover noun-chunk extraction, synonym expansion, and duplicate removal.

### Testing Strategy
- Create `tests/test_nlp.py` with fixtures to load spaCy once per session (use pytest `session` fixture).  
- Write tests before implementation covering:  
  - Basic lemmatization (singular/plural).  
  - Phrase extraction via noun chunks.  
  - Synonym expansion via mock config.  
  - Error when model missing (can simulate by mocking load function).  
- Update ingestion tests (`tests/test_ingest.py`) to assert normalized outputs once integration happens (may stub until pipeline updated).  
- Run `script/test.sh` to ensure lint and tests pass after implementation.
