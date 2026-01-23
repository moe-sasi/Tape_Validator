# ASF Validator

ASF Validator is a portable CLI for validating ASF loan tapes and producing Excel reports.

## Features

- Typer-based CLI with subcommands.
- Validation engine separated from report generation.
- Excel output via `openpyxl` with pandas.
- Utility helpers for parsing and normalization.

## Installation (editable)

```bash
pip install -e .
```

## Usage

```bash
asf-validator run path/to/tape.xlsx --output validation-report.xlsx
```

### Example usage
`python -m asf_validator.cli "SEMT_2026-2_01212026(RA).xlsx" --output validation-report.xlsx`

## Project layout

```
asf_validator/
  cli.py            # CLI entry points
  engine.py         # Validation engine
  io.py             # Input helpers
  report.py         # Excel report writer
  summary.py        # Stratification summaries
  util.py           # Parsing/normalization helpers
  rules/
    asf_validations.py  # Rule implementations live here
    registry.py         # Rule registry
```

## Packaging with PyInstaller

Build a single-file executable (example on macOS/Linux):

```bash
pip install pyinstaller
pyinstaller --onefile --name asf-validator -m asf_validator.cli
```

The executable will be available in `dist/asf-validator`.
