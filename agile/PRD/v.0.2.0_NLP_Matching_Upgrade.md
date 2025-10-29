## Product Requirements Document – Foundation Matching Tool v0.2.0 (NLP Matching Upgrade)

### 1. Overview
- **Product**: Foundation Matching Tool (FMT)  
- **Release**: v0.2.0 – “NLP Matching Upgrade”  
- **Primary Goal**: Enhance the matching engine so it reliably surfaces relevant opportunities using the existing faculty and foundation spreadsheets by incorporating robust NLP-based keyword normalization and a configurable similarity threshold.

### 2. Objectives & Success Criteria
1. **Deliver credible matches**: Faculty with known overlaps (e.g., pulmonary hypertension focus) receive relevant foundations without manual keyword rewrites.  
2. **Enable tuning**: Operators can set a numeric similarity threshold per run to balance precision vs. breadth.  
3. **Preserve transparency**: Continue providing match scores and rationale so staff can prioritize and audit results.  
4. **Maintain usability**: CLI workflow, documentation, and outputs remain familiar to Pre-Award staff.

### 3. In-Scope Features
#### 3.1 Advanced Keyword Normalization
- Integrate a production-ready NLP library (e.g., spaCy) to perform lemmatization and/or stemming.  
- Support synonym or phrase expansion for common clinical terms where feasible.  
- Normalize foundation and faculty keywords through the same pipeline before scoring.

#### 3.2 Similarity Scoring Enhancements
- Replace pure exact-overlap scoring with a similarity function that accounts for partial phrase matches and inflectional variants.  
- Allow operators to supply a numeric match threshold (e.g., 0.0–1.0 or 0–100) via configuration or flag; default to a sensible mid-range.  
- Continue surfacing integer match scores for reporting, mapping the similarity metric into 0–100.

#### 3.3 Output & Reporting Adjustments
- Highlight scores that fall near the chosen threshold so staff know which matches may require manual vetting.  
- Provide a simple verification command or appendix describing how to reproduce a known match (e.g., Matthew Douglass ↔ pediatric pulmonary hypertension foundation) for QA.

#### 3.4 Data Compatibility
- Operate directly on the existing `data/faculty.xlsx` and `data/foundations.xlsx` column layouts.  
- No manual keyword rewriting required; however, documentation can suggest optional keyword cleanup tips.

### 4. In/Out of Scope
- **In Scope**: Matching logic overhaul, threshold configuration, NLP dependency setup, updated documentation and samples.  
- **Out of Scope**: New UI, web interface, per-faculty tuning controls, automated alerting, or integration with external databases.

### 5. Users & Stories Covered
- **Pre-Award Director** (agile/stories/005_pre_award_director_needs_richer_matching.md): Primary driver for reliable matching with current spreadsheets.  
- **Pre-Award Staff Specialist** (agile/stories/003_pre_award_specialist_command_line_ready.md): Continues to operate the CLI; relies on clearer matches.  
- **Faculty & Leadership** (agile/stories/001–004): Benefit downstream from improved opportunity relevance and scoring.

### 6. Dependencies & Inputs
- Existing Excel inputs (`data/faculty.xlsx`, `data/foundations.xlsx`).  
- Python runtime with added NLP library (spaCy recommended; consider `en_core_web_sm` model).  
- Ability to download/install the NLP model in the deployment environment (document installation steps).  
- Continued use of `pandas`, `openpyxl`, `pytest`, `ruff`.  
- Development process remains strict test-driven development; new behaviors must be covered by failing tests before implementation.

### 7. Risks & Mitigations
- **Risk**: NLP library increases setup complexity.  
  - *Mitigation*: Provide scripted installation steps and lightweight model selection; document offline installation options.  
- **Risk**: Similarity threshold defaults may not suit all divisions.  
  - *Mitigation*: Allow operators to override threshold and include guidance for tuning.  
- **Risk**: Higher match volume could overwhelm faculty.  
  - *Mitigation*: Emphasize score sorting; consider optional top-N filtering tips in documentation.  
- **Risk**: NLP performance or accuracy gaps.  
  - *Mitigation*: Validate with multiple sample pairs; allow fallback to simple matching if model load fails.

### 8. Milestones & Acceptance
- **Milestone**: “Real Matches Demo” – Run v0.2.0 pipeline on current spreadsheets and produce non-zero matches for known faculty-foundation pairs (e.g., pulmonary hypertension).  
- **Acceptance Criteria**:  
  1. CLI runs end-to-end with new NLP dependencies documented.  
  2. Operators can set a numeric similarity threshold; defaults are documented.  
  3. At least three representative faculty receive correct matches during QA review.  
  4. Updated README or run guide explains installation, threshold usage, and QA verification steps.  
  5. Regression tests cover new normalization and scoring logic, including edge cases.

### 9. Open Questions
1. Should we maintain a small curated synonym/abbreviation dictionary (e.g., mapping “BPD” → “bronchopulmonary dysplasia”) in addition to NLP lemmatization? *(Clarify preference.)*  
2. Do we need to persist the chosen threshold/parameters in the Summary sheet for auditing? *(Decision: No.)*  
3. Are there institutional requirements for downloading or packaging the NLP model (e.g., offline distribution)? *(Decision: None identified.)*
