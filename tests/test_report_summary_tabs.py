"""Tests for report summary tab outputs."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from asf_validator.report import (
    _build_field_min_max_df,
    _build_field_unique_values_df,
    write_report,
)


def test_field_min_max_excludes_selected_fields() -> None:
    tape_df = pd.DataFrame(
        {
            "Primary Servicer": ["Servicer A", "Servicer B", "Servicer A"],
            "Servicing Fee %": [0.25, 0.30, 0.25],
            "Current UPB": [100000, 90000, 95000],
        }
    )

    min_max_df = _build_field_min_max_df(
        tape_df,
        excluded_fields=("Primary Servicer", "Servicing Fee %"),
    )

    assert "Primary Servicer" not in min_max_df["field"].tolist()
    assert "Servicing Fee %" not in min_max_df["field"].tolist()
    assert "Current UPB" in min_max_df["field"].tolist()


def test_field_unique_values_builds_distinct_values_and_handles_missing_field() -> None:
    tape_df = pd.DataFrame(
        {
            "Primary Servicer": ["Servicer A", "Servicer B", "Servicer A", None, ""],
            "Channel": ["Retail", "Wholesale", "Retail", " ", None],
        }
    )

    unique_df = _build_field_unique_values_df(
        tape_df,
        fields=("Primary Servicer", "Channel", "Missing Field"),
    )

    primary_values = unique_df.loc[
        unique_df["field"] == "Primary Servicer", "unique_value"
    ].tolist()
    channel_values = unique_df.loc[unique_df["field"] == "Channel", "unique_value"].tolist()
    missing_values = unique_df.loc[unique_df["field"] == "Missing Field", "unique_value"].tolist()

    assert primary_values == ["Servicer A", "Servicer B"]
    assert channel_values == ["Retail", "Wholesale"]
    assert len(missing_values) == 1
    assert pd.isna(missing_values[0])


def test_write_report_writes_unique_values_sheet_and_excludes_from_min_max(tmp_path: Path) -> None:
    tape_df = pd.DataFrame(
        {
            "Primary Servicer": ["Servicer A", "Servicer B", "Servicer A"],
            "Servicing Fee %": [0.25, 0.30, 0.25],
            "Channel": ["Retail", "Wholesale", "Retail"],
            "Current UPB": [100000, 90000, 95000],
        }
    )
    output_path = tmp_path / "report.xlsx"
    results = {
        "generated_at": "2026-02-19T00:00:00.000000+00:00",
        "row_count": len(tape_df),
        "issues": pd.DataFrame(columns=["rule", "loan_number", "columns", "message"]),
        "missing_required_fields": [],
        "warnings": pd.DataFrame(columns=["rule", "loan_number", "columns", "message"]),
        "rule_summary": pd.DataFrame(columns=["rule", "issue_count"]),
        "warning_summary": pd.DataFrame(columns=["rule", "issue_count"]),
        "skipped_rules": pd.DataFrame(columns=["rule", "reason"]),
        "tape_df": tape_df,
    }

    write_report(results, output_path)

    with pd.ExcelFile(output_path) as xlsx:
        assert "field_unique_values" in xlsx.sheet_names
        min_max_df = pd.read_excel(xlsx, sheet_name="field_min_max")
        unique_df = pd.read_excel(xlsx, sheet_name="field_unique_values")

    assert "Primary Servicer" not in min_max_df["field"].tolist()
    assert "Servicing Fee %" not in min_max_df["field"].tolist()
    assert "Current UPB" in min_max_df["field"].tolist()
    assert "Primary Servicer" in unique_df["field"].tolist()
    assert "Servicing Fee %" in unique_df["field"].tolist()
