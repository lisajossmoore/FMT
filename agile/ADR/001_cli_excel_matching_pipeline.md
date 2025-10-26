## ADR 001 – CLI-Based Excel Matching Pipeline (Python)

### Context
- Release v0.1.0 must transform two Excel inputs (faculty keywords and foundation opportunities) into division-ready match digests with weighted scoring.  
- Pre-Award staff will execute the tool twice yearly on Windows machines using WSL; they are unfamiliar with software development practices.  
- Dataset sizes are modest (≈40 faculty, ≈100 foundations) so in-memory processing is acceptable.  
- The product requirement emphasizes minimal complexity while ensuring maintainability and transparent matching logic.  
- External libraries are acceptable when they significantly reduce custom code surface area.

### Decision
1. **Language & Runtime**: Standardize on Python 3.11 for the CLI tool to leverage modern typing features and long-term support.  
2. **CLI Structure**: Implement a single-entry command-line interface using the standard library `argparse` module to avoid extra dependencies while providing clear flags for input/output paths and run metadata.  
3. **Data Handling**: Use `pandas` with the `openpyxl` engine to read and write Excel files, enabling schema validation, tabular transformations, and Excel output without reinventing parsing logic.  
4. **Matching Engine Design**: Build an internal pipeline with explicit stages—input validation, keyword normalization, match scoring (strict vs. broad profiles), and formatted output—each encapsulated in its own module/function to keep logic testable and explainable.  
5. **Packaging & Dependencies**: Distribute via a project-level `requirements.txt` (limited to `pandas` and `openpyxl`) and a lightweight `Makefile` or documentation snippet showing `python -m venv` setup and execution; no additional packaging tooling for v0.1.0.  
6. **Testing & Quality Tooling**: Adopt strict test-driven development with automated tests authored before implementation, using `pytest` plus the `ruff` linter/formatter as development-only dependencies documented in `requirements-dev.txt`.  
7. **Artifacts & Logging**: Embed run metadata (timestamp, operator name, divisions processed) in the Excel output’s summary sheet rather than maintaining separate log files, aligning with the PRD decision to avoid external logging.

### Consequences
- Targeting Python 3.11 ensures access to current language features but requires verifying WSL environments meet that version.  
- Using `argparse` keeps the CLI dependency-free but limits advanced UX; future releases could adopt `click` if usability gaps emerge.  
- Relying on `pandas` + `openpyxl` simplifies Excel IO and allows rapid iteration, at the cost of slightly higher install footprint; documentation must guide staff through dependency installation.  
- Modular pipeline design makes it easier to extend weighting logic or introduce web interfaces later, but demands a small upfront design effort.  
- Minimal packaging reduces setup overhead now but means we must document environment preparation clearly for non-technical operators.  
- Embedding run metadata within output files satisfies auditing requirements without building a logging subsystem; however, historical run analysis will require users to keep copies of generated workbooks.  
- Enforcing TDD with `pytest` and linting/formatting via `ruff` introduces small additional setup steps for developers but keeps runtime footprint unchanged while giving confidence in behavior and consistency.
