## TDD 005 – End-to-End Pipeline Integration

### Objective
Connect CLI argument parsing, data ingestion, matching, and output rendering into a cohesive execution pipeline with clear error handling and operator messaging.

### Scope
- Implement `src/fmt_tool/pipeline.py` with a public function `run(args: Namespace) -> Path`.  
- Orchestrate modules from TDDs 002–004 in sequence, consolidating warnings and populating run context.  
- Ensure consistent error handling, including conversion of unexpected exceptions into user-facing summaries with exit codes.

### Execution Flow
1. **Argument Parsing (from CLI)**  
   - CLI constructs `argparse.Namespace` containing all required fields.  
2. **Run Context Initialization**  
   - Create `RunContext` with current timestamp, operator, run label, and source file names.  
3. **Ingestion**  
   - Call `ingest.load_faculty` and `ingest.load_foundations`.  
   - Collect warnings from both loaders; append to context.  
   - If either returns zero valid records, raise `FMTValidationError` to halt execution.
4. **Matching**  
   - Invoke `match.generate_matches`.  
   - Append any matching warnings to context.  
   - Compute aggregate metrics (e.g., total matches) for summary sheet.  
5. **Output**  
   - Group matches by division/faculty via helper (from TDD 003).  
   - Pass grouped data and context to renderer to build/write workbook.  
   - Return output file path for CLI to report success.
6. **TDD Requirements**  
   - Draft failing end-to-end pytest cases in `tests/test_pipeline.py` (using temporary directories and fixture spreadsheets) before wiring the pipeline.  
   - Run `ruff check` to ensure pipeline and CLI modules conform to lint rules post-implementation.

### Error Handling
- Catch `FMTValidationError` and `FMTError` to provide clean messages; re-raise others after logging a generic failure message.  
- CLI should set exit code `2` for validation errors, `1` for runtime failures.  
- Provide actionable hints in messages (e.g., “Check keywords column in faculty.xlsx for blanks.”).

### Operator Feedback
- CLI prints progress milestones: “Loading faculty data…”, “Matching opportunities…”, “Writing Neonatology digest…”, “Done → <path>”.  
- On success, output final summary including counts (faculty processed, matches generated).  
- Optionally emit warning count and refer operator to Summary sheet for details.

### Acceptance Criteria
- Running pipeline on provided sample spreadsheets yields an Excel file with populated Summary/Neonatology sheets.  
- Removing a required column triggers validation error and stops process before matching/output.  
- CLI communicates both success and failure states in plain language suitable for non-technical staff.  
- Return value from `pipeline.run` is used by CLI to confirm location of generated file.

### Testing Strategy
- Pytest-first workflow: implement failing tests prior to writing pipeline orchestration code.  
- Integration test executing pipeline with fixture workbooks, asserting resulting file exists and contains expected sheet names/metadata.  
- Negative test feeding malformed workbook to ensure graceful halt.  
- Mock-based unit tests verifying CLI exit codes map correctly to exceptions.  
- Include `ruff check`/`ruff format` as part of verification.
