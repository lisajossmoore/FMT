## TDD 001 – CLI Scaffold & Project Setup

### Objective
Create the project skeleton and command-line entry point that orchestrates the Foundation Matching Tool workflow in Python 3.11, aligning with ADR 001 and PRD v0.1.0.

### Scope
- Establish Python package layout under `src/` (e.g., `src/fmt_tool/`).  
- Define dependency management using `requirements.txt` (limited to `pandas`, `openpyxl`).  
- Implement CLI driver (`python -m fmt_tool.cli`) using `argparse` to collect file paths, operator name, and output directory.  
- Wire stub calls to downstream pipeline steps (ingestion, matching, output), leaving actual logic to later TDDs.  
- Provide developer + operator documentation snippets (README section) illustrating environment setup and basic invocation.

### Key Decisions & References
- ADR 001 dictates Python 3.11, `argparse`, and minimal packaging.  
- PRD sections 3.4 and 3.3 require a single CLI entry point and Excel outputs.  
- Staff will run via WSL; instructions must mention `python3 -m venv` steps.

### Implementation Notes
1. **Directory Structure**  
   - `src/fmt_tool/__init__.py` (empty)  
   - `src/fmt_tool/cli.py` for argument parsing and high-level orchestration.  
   - Placeholder modules referenced for later tasks: `ingest`, `match`, `render`.
2. **Dependencies**  
   - `requirements.txt` with pinned minimum versions (`pandas>=2.0`, `openpyxl>=3.1`).  
   - `requirements-dev.txt` listing `pytest>=7.0` and `ruff>=0.1.0` for the TDD + linting workflow.  
   - Document installation via `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && pip install -r requirements-dev.txt`.
3. **CLI Arguments**  
   - `--faculty-xlsx` (required)  
   - `--foundations-xlsx` (required)  
   - `--output-xlsx` (required; single workbook)  
   - `--operator` (optional, defaults to “Unknown”)  
   - `--run-label` (optional descriptive string)  
   - `--run-date` (optional ISO date override; default to `datetime.now()`).
4. **Execution Flow**  
   - Parse args → call `pipeline.run(args)` (to be implemented later).  
   - Apply basic exception handling: capture known `FMTError` (custom) vs unexpected exceptions, emitting user-friendly messages and non-zero exit codes.
5. **TDD Requirements**  
   - Author failing `tests/test_cli.py` pytest cases covering help text, required arguments, and error codes before implementing CLI logic.  
   - Iterate test→code→refactor cycle; ensure CI/local scripts execute `pytest`.  
   - After code passes tests, run `ruff check` and `ruff format` to maintain consistent style.
5. **Documentation Deliverables**  
   - Add README section `Running the Tool (v0.1.0)` with step-by-step commands targeted at non-developers.  
   - Provide example invocation referencing sample files in `/data`.

### Acceptance Criteria
- Running `python -m fmt_tool.cli --help` displays well-formatted usage text.  
- `src/fmt_tool` package imports without errors even before downstream logic is implemented.  
- README instructions allow a teammate to set up the environment from scratch.  
- CLI gracefully fails with message if required arguments missing.

### Testing Strategy
- Pytest suite authored before implementation; focus on argument parser behavior and pipeline invocation stub.  
- Unit test for argument parser (using `argparse` test patterns) verifying defaults and error handling.  
- Manual dry run: invoke CLI with sample paths (can be placeholders) to ensure flow reaches stubbed pipeline function without crashing.  
- Enforce linting by running `ruff check` as part of the red→green cycle; address formatting via `ruff format`.
