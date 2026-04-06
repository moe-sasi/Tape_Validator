"""Regression tests for buy-down period report-only behavior."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pandas as pd

from asf_validator.engine import run_validations
from asf_validator.report import write_report
from asf_validator.rules.asf_validations import validate_buy_down_period


RULE_NAME = "validate_buy_down_period"


def _report_output_path() -> Path:
    base_dir = Path(".codex_test_output")
    base_dir.mkdir(exist_ok=True)
    return base_dir / f"{uuid4().hex}_report.xlsx"


def test_validate_buy_down_period_handles_numeric_and_string_values() -> None:
    assert validate_buy_down_period(2) is True
    assert validate_buy_down_period("2") is True
    assert validate_buy_down_period(0) is False
    assert validate_buy_down_period("0") is False
    assert validate_buy_down_period("") is False


def test_engine_routes_buy_down_period_to_dedicated_report() -> None:
    tape_df = pd.DataFrame(
        [
            {"loan_number": "LN-0", "buy_down_period": 0},
            {"loan_number": "LN-1", "buy_down_period": 2},
            {"loan_number": "LN-2", "buy_down_period": "3"},
        ]
    )

    results = run_validations(tape_df)

    assert RULE_NAME not in results["issues"]["rule"].tolist()
    assert RULE_NAME not in results["rule_summary"]["rule"].tolist()
    assert results["buy_down_period_report"].to_dict("records") == [
        {"Loan Number": "LN-1", "Buy Down Period": 2},
        {"Loan Number": "LN-2", "Buy Down Period": "3"},
    ]


def test_write_report_writes_buy_down_period_report_sheet() -> None:
    tape_df = pd.DataFrame(
        [
            {"loan_number": "LN-0", "buy_down_period": 0},
            {"loan_number": "LN-1", "buy_down_period": 2},
        ]
    )
    results = run_validations(tape_df)
    results["generated_at"] = "2026-04-06T00:00:00.000000+00:00"
    results["tape_df"] = tape_df

    output_path = _report_output_path()
    write_report(results, output_path)

    with pd.ExcelFile(output_path) as xlsx:
        assert "buy_down_period_report" in xlsx.sheet_names
        issues_df = pd.read_excel(xlsx, sheet_name="issues")
        report_df = pd.read_excel(xlsx, sheet_name="buy_down_period_report")

    assert RULE_NAME not in issues_df.get("rule", pd.Series(dtype=str)).tolist()
    assert report_df.to_dict("records") == [
        {"Loan Number": "LN-1", "Buy Down Period": 2},
    ]
