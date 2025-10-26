# Foundation Matching Tool (FMT)

Command-line utility for generating pediatric foundation funding digests from faculty and foundation keyword spreadsheets.

## Getting Started

These steps assume a Unix-like shell (e.g., WSL on Windows).

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## Running the Tool

```bash
python -m fmt_tool.cli \
  --faculty-xlsx data/faculty.xlsx \
  --foundations-xlsx data/foundations.xlsx \
  --output-xlsx output/neonatology_digest.xlsx \
  --operator "Your Name" \
  --run-label "Spring 2025"
```

Arguments:

- `--faculty-xlsx` (required): Path to the faculty keyword workbook.
- `--foundations-xlsx` (required): Path to the foundation opportunity workbook.
- `--output-xlsx` (required): Destination for the generated digest workbook.
- `--operator`: Name of the person running the tool (defaults to `Unknown`).
- `--run-label`: Optional free-text descriptor for the run.
- `--run-date`: Optional ISO date string overriding the run timestamp.

## Quality Checks

Use the helper script to format, lint, and run tests:

```bash
chmod +x script/test.sh  # one-time
script/test.sh
```
