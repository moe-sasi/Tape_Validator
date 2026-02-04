"""Report generation for ASF validation output."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

import pandas as pd


def _autofit_columns(writer: pd.ExcelWriter, sheet_name: str, df: pd.DataFrame) -> None:
    if df.empty:
        return
    worksheet = writer.sheets.get(sheet_name)
    if worksheet is None:
        return
    for idx, col in enumerate(df.columns, start=1):
        values = df[col].astype(str).fillna("").tolist()
        max_len = max([len(str(col))] + [len(val) for val in values])
        worksheet.column_dimensions[worksheet.cell(row=1, column=idx).column_letter].width = max_len + 2


def write_report(results: Mapping[str, Any], output_path: Path) -> None:
    """Write validation results to an Excel report.

    Writes summary metadata and any provided detail tables.
    """
    issues = results.get("issues", [])
    issues_df = issues if isinstance(issues, pd.DataFrame) else pd.DataFrame(issues)
    warnings = results.get("warnings", [])
    warnings_df = warnings if isinstance(warnings, pd.DataFrame) else pd.DataFrame(warnings)
    rule_summary_df = results.get("rule_summary")
    warning_summary_df = results.get("warning_summary")
    skipped_rules_df = results.get("skipped_rules")
    rule_summary_output = rule_summary_df
    if isinstance(rule_summary_df, pd.DataFrame) and "issue_count" in rule_summary_df.columns:
        issue_counts = pd.to_numeric(rule_summary_df["issue_count"], errors="coerce").fillna(0)
        rule_summary_output = rule_summary_df.loc[issue_counts > 0].copy()
        if not rule_summary_output.empty:
            rule_summary_output = (
                rule_summary_output.assign(_issue_count_sort=issue_counts.loc[issue_counts > 0].values)
                .sort_values(by="_issue_count_sort", ascending=False, kind="mergesort")
                .drop(columns=["_issue_count_sort"])
            )

    issue_count = len(issues_df)
    warning_count = len(warnings_df)
    executed_rules = 0
    if isinstance(rule_summary_df, pd.DataFrame):
        executed_rules += len(rule_summary_df)
    if isinstance(warning_summary_df, pd.DataFrame):
        executed_rules += len(warning_summary_df)
    skipped_rules = len(skipped_rules_df) if isinstance(skipped_rules_df, pd.DataFrame) else 0

    summary_df = pd.DataFrame(
        {
            "metric": [
                "row_count",
                "issue_count",
                "warning_count",
                "executed_rules",
                "skipped_rules",
            ],
            "value": [
                results.get("row_count", 0),
                issue_count,
                warning_count,
                executed_rules,
                skipped_rules,
            ],
        }
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(output_path) as writer:
        if isinstance(rule_summary_output, pd.DataFrame):
            rule_summary_output.to_excel(writer, index=False, sheet_name="rule_summary")
            _autofit_columns(writer, "rule_summary", rule_summary_output)
        summary_df.to_excel(writer, index=False, sheet_name="summary")
        _autofit_columns(writer, "summary", summary_df)
        if isinstance(issues_df, pd.DataFrame):
            issues_df.to_excel(writer, index=False, sheet_name="issues")
            _autofit_columns(writer, "issues", issues_df)
        if isinstance(warnings_df, pd.DataFrame):
            warnings_df.to_excel(writer, index=False, sheet_name="warnings")
            _autofit_columns(writer, "warnings", warnings_df)
        if isinstance(skipped_rules_df, pd.DataFrame):
            skipped_rules_df.to_excel(writer, index=False, sheet_name="skipped_rules")
            _autofit_columns(writer, "skipped_rules", skipped_rules_df)
