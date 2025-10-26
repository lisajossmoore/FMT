import sys
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from fmt_tool import cli, errors, models  # noqa: E402


def test_parser_requires_mandatory_arguments():
    parser = cli.build_parser()

    with pytest.raises(SystemExit) as excinfo:
        parser.parse_args([])

    assert excinfo.value.code == 2


def test_help_lists_expected_options(capsys):
    parser = cli.build_parser()

    with pytest.raises(SystemExit) as excinfo:
        parser.parse_args(["--help"])

    assert excinfo.value.code == 0
    help_out = capsys.readouterr().out
    assert "--faculty-xlsx" in help_out
    assert "--foundations-xlsx" in help_out
    assert "--output-xlsx" in help_out
    assert "--operator" in help_out


def test_main_invokes_pipeline_with_defaults(monkeypatch, tmp_path):
    called = {}

    def fake_run(args):
        called["args"] = args
        return (
            tmp_path / "neonatology.xlsx",
            models.PipelineSummary(
                total_faculty=2,
                total_foundations=3,
                total_matches=5,
                warnings=[],
            ),
        )

    monkeypatch.setattr(cli.pipeline, "run", fake_run)

    exit_code = cli.main(
        [
            "--faculty-xlsx",
            "faculty.xlsx",
            "--foundations-xlsx",
            "foundations.xlsx",
            "--output-xlsx",
            "output.xlsx",
        ]
    )

    assert exit_code == 0
    args = called["args"]
    assert Path(args.faculty_xlsx) == Path("faculty.xlsx")
    assert Path(args.foundations_xlsx) == Path("foundations.xlsx")
    assert Path(args.output_xlsx) == Path("output.xlsx")
    assert args.operator == "Unknown"
    assert args.run_label is None
    assert args.run_date is None


def test_main_handles_fmt_error(monkeypatch, capsys):
    def fail_run(args):
        raise errors.FMTError("invalid spreadsheet")

    monkeypatch.setattr(cli.pipeline, "run", fail_run)

    exit_code = cli.main(
        [
            "--faculty-xlsx",
            "faculty.xlsx",
            "--foundations-xlsx",
            "foundations.xlsx",
            "--output-xlsx",
            "output.xlsx",
        ]
    )

    assert exit_code == 2
    captured = capsys.readouterr()
    assert "invalid spreadsheet" in captured.err.lower()


def test_main_handles_unexpected_exception(monkeypatch, capsys):
    def boom(args):
        raise RuntimeError("boom")

    monkeypatch.setattr(cli.pipeline, "run", boom)

    exit_code = cli.main(
        [
            "--faculty-xlsx",
            "faculty.xlsx",
            "--foundations-xlsx",
            "foundations.xlsx",
            "--output-xlsx",
            "output.xlsx",
        ]
    )

    assert exit_code == 1
    captured = capsys.readouterr()
    assert "unexpected error" in captured.err.lower()
    assert "boom" in captured.err.lower()
