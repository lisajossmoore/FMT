## TDD 004 – Output Assembly & Excel Generation

### Objective
Convert match results into an operator-friendly Excel workbook that satisfies PRD requirements for faculty digests and embedded run metadata.

### Scope
- Implement `src/fmt_tool/render.py` with functions:  
  - `build_workbook(matches_by_faculty, run_context) -> openpyxl.Workbook`  
  - `write_workbook(workbook, output_path)`  
- Embed run metadata (operator, run date/time, source file names) in a dedicated “Summary” sheet.  
- Produce a “Neonatology” sheet (Release 1) listing matches grouped by faculty and sorted by descending score.

### Layout Specification
1. **Summary Sheet**  
   - Header rows capturing:  
     - Run timestamp (ISO 8601).  
     - Operator name.  
     - Run label (if provided).  
     - Faculty source file name.  
     - Foundation source file name.  
     - Counts: total faculty processed, total foundations processed, total matches generated.  
     - Warning log (multi-line cell) summarizing ingestion/matching warnings.
2. **Division Sheet(s)**  
   - For v0.1.0, single sheet titled `Neonatology`.  
   - Columns: `Faculty Name`, `Faculty Career Stage`, `Foundation Name`, `Match Score`, `Matched Keywords`, `Funding Tier`, `Deadline`, `Website`, `Eligibility Notes`, `Areas of Funding`, `Average Grant Amount`, `Career Stage Targeted`, `Institution Preferences`, `Row Reference`.  
   - Include blank spacer row between different faculty for readability.  
   - Sort matches per faculty by descending `Match Score`, then by `Foundation Name`.

### Implementation Notes
1. **Library Usage**  
   - Use `pandas` DataFrame to construct table, then write via `pandas.ExcelWriter(engine="openpyxl")`.  
   - For summary sheet, write via `worksheet[cell] = value` using openpyxl for formatting flexibility.  
2. **Formatting**  
   - Autofit not easily available; set reasonable column widths manually (e.g., 20–30 chars) for key columns.  
   - Apply header bold styling and freeze panes at first data row.  
   - Format matched keywords as comma-separated string sorted alphabetically.  
3. **Run Context**  
   - Define `RunContext` dataclass in `models.py` with attributes: `timestamp`, `operator`, `run_label`, `faculty_source`, `foundation_source`, `warnings`.  
   - CLI populates context and passes to renderer.  
4. **Warning Presentation**  
   - Concatenate warnings into multi-line string (e.g., `- message`).  
   - If warning list empty, display “None”.
5. **File Output**  
   - Ensure directories for output path exist (create parent directories).  
   - Overwrite existing file only after successful workbook construction (write to temp file then replace).  
   - Return final path for CLI messaging.
6. **TDD Requirements**  
   - Begin with failing pytest cases in `tests/test_render.py` validating sheet names, header content, and warning aggregation prior to implementing rendering logic.  
   - Run `ruff check` to maintain formatting/lint compliance after code changes.

### Acceptance Criteria
- Generated workbook opens in Excel with separate “Summary” and “Neonatology” sheets populated as specified.  
- Summary sheet captures operator metadata and warning log.  
- Matches correctly grouped and sorted with clear separation per faculty.  
- Output writing handles existing directory but fails gracefully if path unwritable.

### Testing Strategy
- Pytest-authored tests precede code changes, ensuring red→green cycles.  
- Unit/integration test generating workbook from synthetic matches, asserting sheet names and key cell contents.  
- Manual verification by opening produced Excel file (optional acceptance step).  
- Test for warning aggregation (e.g., when ingestion flagged empty keywords) to ensure summary logs appear.  
- Include `ruff check`/`ruff format` in the validation workflow.
