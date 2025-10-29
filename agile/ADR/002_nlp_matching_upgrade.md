## ADR 002 – NLP-Powered Matching Upgrade

### Context
- Release v0.2.0 targets richer matching accuracy demanded by the Pre-Award Director (see agile/stories/005_pre_award_director_needs_richer_matching.md).  
- v0.1.0’s exact-overlap scoring yields zero matches with real spreadsheets because keywords differ by inflection, phrasing, or abbreviations.  
- Product requirements for v0.2.0 (agile/PRD/v.0.2.0_NLP_Matching_Upgrade.md) authorize adoption of heavier NLP tooling and introduce a per-run numeric similarity threshold, while keeping the CLI interface stable.  
- We must continue using strict TDD and preserve operability for staff running the existing CLI on WSL machines.

### Decision
1. **Matching Library**: Adopt RapidFuzz for fuzzy string comparison (token set ratios, partial ratios) instead of spaCy similarity. Document installation requirements in `README.md`.  
2. **Keyword Normalization Pipeline**: Split faculty and foundation keyword phrases on semicolons/commas, normalize punctuation/casing, expand optional synonyms, and drop phrases composed entirely of generic stopwords maintained in config.  
3. **Similarity Scoring**: For each faculty phrase, retain the best fuzzy score against foundation phrases and derive a 0–100 keyword score. Honour a configurable similarity threshold (default 0.6) expressed as a fraction.  
4. **Threshold Configuration**: Accept the threshold via a small TOML/INI config file passed with `--config` (optional). If omitted, use defaults defined in `config/defaults.toml`. CLI flags remain unchanged otherwise, meeting the “no UI changes” constraint.  
5. **Reporting**: Continue embedding scores and matched keyword rationale in the Excel output, surfacing a “Why matched” explanation and matched keyword count.  
6. **Optional Weighting**: Support an optional per-run weighting blend (keyword/grant/stage) controlled by config flags, maintaining defaults that rely solely on keyword similarity.  
7. **Quality Constraints**: Maintain TDD/ruff discipline—new functionality must be introduced via failing tests first; add integration tests covering known matched pairs from current spreadsheets.

### Consequences
- RapidFuzz keeps dependencies lightweight and avoids distributing large NLP models.  
- Token expansion and fuzzy comparisons increase runtime slightly but remain acceptable given dataset size.  
- Configuration file support introduces minimal complexity while avoiding breaking changes to the CLI.  
- Maintaining a small synonym map keeps control in our hands without committing to heavyweight knowledge bases; however, it requires occasional curation.  
- Tests focus on deterministic fuzzy scoring behaviour instead of spaCy pipelines.  
- Run metadata grows to include threshold information, aiding debugging but necessitating updated summary formatting.
