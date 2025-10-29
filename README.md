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

### Configuration

Create `config/settings.toml` to override defaults:

```toml
[matching]
similarity_threshold = 0.6
use_weights = true
keyword_weight = 0.6
grant_weight = 0.2
stage_weight = 0.2
ignored_tokens = ["career", "development", "prevention", "and", "in", "neonatal"]
[matching.synonyms]
BPD = ["bronchopulmonary dysplasia"]
```

- `similarity_threshold` is the minimum final score (0–1) for a match to appear in the digest.
- `use_weights` applies the `keyword_weight`/`grant_weight`/`stage_weight` blend when calculating scores.
- `ignored_tokens` removes generic phrases before matching (phrases composed entirely of ignored words are dropped).

## Quality Checks

Use the helper script to format, lint, and run tests:

```bash
chmod +x script/test.sh  # one-time
script/test.sh
```

## Quick Match Verification

After generating the digest you can preview top matches for a specific faculty member without opening Excel:

```bash
script/verify_match.py --faculty-name "Matthew Douglass" \
  --faculty-xlsx data/faculty.xlsx \
  --foundations-xlsx data/foundations.xlsx --top 5
```
