## TDD 002 – Data Ingestion & Validation

### Objective
Implement robust loading and validation of the faculty and foundation Excel workbooks, converting them into normalized in-memory representations ready for matching.

### Scope
- Build `src/fmt_tool/ingest.py` with functions:  
  - `load_faculty(path: Path) -> list[FacultyRecord]`  
  - `load_foundations(path: Path) -> list[FoundationRecord]`  
  - `validate_faculty(df: pandas.DataFrame)` and `validate_foundations(df: pandas.DataFrame)` raising custom `FMTValidationError`.  
- Define lightweight dataclasses in `src/fmt_tool/models.py` for faculty and foundation entities.  
- Normalize keyword fields (split on commas, strip whitespace, lowercase).  
- Capture metadata (e.g., total records, duplicate detection) for logging/reporting.

### Input Expectations (Release 1)
- **Faculty workbook (`data/faculty.xlsx`)** columns:  
  - `Name`, `Degree`, `Rank`, `Division ` (note trailing space), `Career Stage`, `Keywords`.  
  - Only Neonatology division present; future iterations may add more.  
- **Foundation workbook (`data/foundations.xlsx`)** columns:  
  - `Foundation name`, `area(s) of funding`, `average grant amount`, `career stage targeted`, `Deadlines, restrictions`, `institution specific preferences`, `Website link`.

### Implementation Notes
1. **Pandas Loading**  
   - Use `pandas.read_excel(..., engine="openpyxl")`.  
   - Enforce `dtype=str` where feasible to avoid unexpected NaNs.  
2. **Validation Rules**  
   - Required columns must exist exactly (case-sensitive). Provide friendly error message listing missing columns.  
   - Ensure `Keywords` columns are non-empty; warn (collect) if empty and exclude from matching.  
   - Drop rows that are completely blank after trimming; report counts.  
   - For faculty, trim whitespace from `Division ` header when mapping to dataclass field `division`.  
   - Detect duplicates by faculty name + division; surface as warning list for later roadmap (do not hard fail).  
3. **Normalization**  
   - Standardize strings: strip, convert to title case (for names) or uppercase? (Decision: preserve original for reporting; only lower-case tokens for matching).  
   - Produce `keywords: set[str]` per record using simple comma splitting, ignoring empty tokens.  
   - Provide `career_stage` from `Career Stage` column; leave as-is for now.  
4. **Data Structures**  
   - `FacultyRecord`: `name`, `degree`, `rank`, `division`, `career_stage`, `keywords`.  
   - `FoundationRecord`: `name`, `areas_of_funding`, `avg_grant_amount`, `career_stage_targeted`, `deadlines`, `institution_prefs`, `website`, `keywords`.  
   - Each record should include `raw_row_index` to aid traceability (1-based Excel row).  
5. **Error Handling**  
   - Define custom exception `FMTValidationError` in `src/fmt_tool/errors.py`.  
   - Raise with descriptive message; CLI will catch and exit gracefully.  
   - Collect non-fatal issues (warnings) and return alongside data (`IngestionResult` dataclass with `records` and `warnings`).
6. **TDD Requirements**  
   - Write failing pytest cases in `tests/test_ingest.py` covering happy path, missing columns, and empty keyword handling before implementing loader logic.  
   - Run `ruff check` to ensure modules conform to style guidelines once tests pass.

### Acceptance Criteria
- Loading known-good sample files returns populated record lists with normalized keyword sets.  
- Missing required column triggers `FMTValidationError` naming the column.  
- Empty keyword cells are reported in warnings, and affected records have empty keyword sets (excluded downstream).  
- Trailing whitespace in column name (`Division `) handled without manual cleaning by operators.

### Testing Strategy
- Pytest-first workflow: author tests before implementing functions, ensuring they initially fail.  
- Unit tests covering happy path and error scenarios (missing column, blank row, empty keywords).  
- Snapshot test (or assertion) verifying keyword parsing for representative rows.  
- Integration test stub calling loader from CLI stub to ensure exception propagation works.  
- Include `ruff check` in routine to guarantee lint compliance; apply `ruff format` if needed.
