"""Command-line interface for ASF Validator."""

import logging
from datetime import datetime, timezone
from pathlib import Path

import typer
from rich.logging import RichHandler

from asf_validator.engine import run_validations
from asf_validator.io import read_tape
from asf_validator.report import write_report

app = typer.Typer(help="Validate ASF loan tapes.")


def setup_logging(level: str) -> None:
    logging.basicConfig(
        level=level.upper(),
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)],
    )


@app.command()
def run(
    tape_path: Path = typer.Argument(..., help="Path to input tape file."),
    output_path: Path = typer.Option(
        Path("asf-validation-report.xlsx"),
        "--output",
        "-o",
        help="Path for the Excel report output.",
    ),
    log_level: str = typer.Option("INFO", "--log-level", help="Logging level."),
) -> None:
    """Run validations on a tape and write an Excel report."""
    setup_logging(log_level)
    run_timestamp = datetime.now(timezone.utc)
    timestamp_label = run_timestamp.strftime("%Y%m%d_%H%M%S")
    output_path = output_path.with_name(f"{output_path.stem}_{timestamp_label}{output_path.suffix}")
    logging.info("Loading tape from %s", tape_path)
    tape_df = read_tape(tape_path)
    logging.info("Running validations")
    results = run_validations(tape_df)
    results["generated_at"] = run_timestamp
    logging.info("Writing report to %s", output_path)
    write_report(results, output_path)
    logging.info("Validation complete")


if __name__ == "__main__":
    app()
