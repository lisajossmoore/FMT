## Product Requirements Document – Foundation Matching Tool v0.1.0 (Basic Release)

### 1. Overview
- **Product**: Foundation Matching Tool (FMT)  
- **Release**: v0.1.0 – “Basic FMT”  
- **Primary Goal**: Deliver a command-line tool that ingests existing Excel keyword lists for faculty and foundations, calculates weighted matches per faculty member, and outputs division-ready opportunity digests containing actionable context (match score, funding tier, deadlines, URLs, eligibility notes).

### 2. Objectives & Success Criteria
1. **Empower faculty discovery**: Provide twice-yearly, faculty-specific foundation lists that increase both first-time and repeat submissions.  
2. **Enable pre-award execution**: Allow Pre-Award staff to run the process independently with clear documentation.  
3. **Support quality oversight**: Preserve keyword rationale and run metadata so the Pre-Award director can audit results and validate tool impact.  
4. **Deliver actionable content**: Ensure opportunity digests include enough context for faculty to act immediately without manual cleanup.

### 3. In-Scope Features
#### 3.1 Data Ingestion
- Accept two user-supplied Excel spreadsheets:  
  - Faculty keywords by division, career stage, and experience tier (experienced vs first-time applicants).  
  - Foundation opportunities with associated keywords, funding tiers, deadlines, URLs, and eligibility notes.  
- Validate file structure (required columns, non-empty cells) and surface human-readable errors if validation fails.

#### 3.2 Matching Engine
- Normalize keywords (case, punctuation) and support weighted matching across faculty and foundation keyword sets.  
- Support two match strictness profiles per faculty member:  
  - **Targeted** (high precision) for first-time applicants.  
  - **Broader** (moderate precision) for experienced applicants.  
- Generate match scores that reflect keyword overlap and strictness profile.

#### 3.3 Output Generation
- Produce per-division output files (CSV and/or Excel) grouping opportunities by faculty member.  
- Each opportunity entry must include: faculty name, career stage, match score, foundation name, URL, funding tier (high/med/low), deadline, eligibility notes, and matched keyword rationale.  
- Include summary metadata (run timestamp, operator name, divisions processed) in a header sheet or accompanying log.

#### 3.4 Command-Line Interface
- Provide a single command-line entry point with arguments for input file paths, output directory, and optional run label/operator name.  
- Offer clear progress messages and structured error handling.  
- Supply thorough run documentation and examples tailored to staff unfamiliar with the command line.

### 4. Out-of-Scope (v0.1.0)
- Web-based interface or automated scheduling of runs.  
- Direct distribution to faculty or automated reporting to the department chair.  
- Advanced analytics (conversion rates, award tracking).  
- In-tool annotation workflows for the Pre-Award director.  
- Integration with university data sources beyond the provided Excel files.

### 5. Users & Stories Covered
- **Department Chair** (agile/stories/001_department_chair_targeted_leads.md): Chair indirectly benefits via increased submissions; submission reporting handled outside the tool.  
- **Pre-Award Director** (agile/stories/002_pre_award_director_quality_guardian.md): Gains visibility through run metadata and match rationale for auditing.  
- **Pre-Award Staff Specialist** (agile/stories/003_pre_award_specialist_command_line_ready.md): Primary operator of v0.1.0 CLI workflow.  
- **Faculty (Experienced & First-Time)** (agile/stories/004_faculty_targeted_opportunity_digest.md): Recipients of the generated digests with context-rich opportunity data.

### 6. Dependencies & Inputs
- Availability of faculty keyword Excel file with standardized headers (to be finalized).  
- Availability of foundation opportunity Excel file with keywords, funding tiers, deadlines, URLs, and eligibility notes.  
- Python runtime and required libraries (e.g., `pandas`, `openpyxl`) installed in the target environment.  
- Access to command-line execution environment for Pre-Award staff (with accompanying documentation/training).

### 7. Risks & Mitigations
- **Risk**: Excel formats vary between divisions.  
  - *Mitigation*: Provide template files and validation checks with descriptive error feedback.  
- **Risk**: Match weighting may not reflect faculty expectations.  
  - *Mitigation*: Allow configurable weighting profiles and document tuning process.  
- **Risk**: Staff unfamiliar with CLI hesitate to adopt.  
  - *Mitigation*: Ship step-by-step run guide, sample command scripts, and support contact.  
- **Risk**: Output volume overwhelms faculty.  
  - *Mitigation*: Include match scoring and allow filtering by thresholds (manual or future iteration).  
- **Risk**: Deadlines or funding tiers become outdated between runs.  
  - *Mitigation*: Emphasize reliance on up-to-date input spreadsheets and include data freshness note in outputs.

### 8. Open Questions
1. Confirm required column names and data formats for both input spreadsheets. *(Deferred to a later iteration.)*  
2. Decide on default match weighting and whether weights are configurable via external file. *(Configurable weights not required for v0.1.0; ship with fixed defaults.)*  
3. Determine preferred output format(s): CSV only, Excel only, or both. *(Excel confirmed as required output format.)*  
4. Should the run metadata be logged in a separate file versus embedded within each output file? *(No additional logging beyond output headers needed.)*  
5. Is a dry-run or preview mode required for v0.1.0 to review matches without exporting files? *(No dry-run mode required.)*

### 9. Acceptance for v0.1.0
Release is considered complete when:
- CLI tool runs end-to-end using provided sample spreadsheets, generating per-division outputs with required fields.  
- Validation errors are human-readable and documented troubleshooting steps exist.  
- Run guide and example command usage are reviewed and approved by Pre-Award staff representative.  
- Pre-Award director verifies match rationale visibility and metadata sufficiency for auditing.  
- Outputs are reviewed by customer success (or faculty proxy) to confirm readability and usefulness.
