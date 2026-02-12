"""Report generation for ASF validation output."""

from __future__ import annotations

import inspect
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

import pandas as pd

from asf_validator.rules import get_validations_registry

_ACRONYM_OVERRIDES = {
    "fico": "FICO",
    "dti": "DTI",
    "cltv": "CLTV",
    "ltv": "LTV",
    "oltv": "OLTV",
    "ocltv": "OCLTV",
    "arm": "ARM",
    "heloc": "HELOC",
    "pmi": "PMI",
    "apr": "APR",
    "io": "IO",
    "atrqm": "ATRQM",
}


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


def _normalize_generated_at(value: Any) -> str:
    """Return an ISO timestamp string with microsecond precision in UTC."""
    if value is None:
        value = datetime.now(timezone.utc)
    if not isinstance(value, str):
        value = value.astimezone(timezone.utc).isoformat(timespec="microseconds")
    return value


def _humanize_rule_name(function_name: str) -> str:
    """Convert a validation function name into a readable label."""
    name = function_name[len("validate_") :] if function_name.startswith("validate_") else function_name
    parts = name.split("_")
    human_parts: list[str] = []
    for part in parts:
        if not part:
            continue
        lower = part.lower()
        if lower in _ACRONYM_OVERRIDES:
            human_parts.append(_ACRONYM_OVERRIDES[lower])
        elif len(part) <= 3 and part.isalpha():
            human_parts.append(part.upper())
        else:
            human_parts.append(part.capitalize())
    return " ".join(human_parts)


def _build_validation_legend_df() -> pd.DataFrame:
    """Assemble a legend of available validation rules for the report."""
    registry = get_validations_registry()
    legend_rows = []
    for rule_name, func in registry.items():
        description = inspect.getdoc(func) or ""
        description = " ".join(description.split())
        if len(description) > 240:
            description = f"{description[:237]}..."
        legend_rows.append(
            {
                "rule_function": rule_name,
                "rule_name": _humanize_rule_name(rule_name),
                "description": description,
            }
        )
    legend_df = pd.DataFrame(legend_rows, columns=["rule_function", "rule_name", "description"])
    if not legend_df.empty:
        legend_df = legend_df.sort_values("rule_function").reset_index(drop=True)
    return legend_df


def write_report(results: Mapping[str, Any], output_path: Path) -> None:
    """Write validation results to an Excel report.

    Writes summary metadata and any provided detail tables.
    """
    generated_at = _normalize_generated_at(results.get("generated_at"))
    validation_legend_df = _build_validation_legend_df()

    issues = results.get("issues", [])
    issues_df = issues if isinstance(issues, pd.DataFrame) else pd.DataFrame(issues)
    missing_required_fields = results.get("missing_required_fields", [])
    if isinstance(missing_required_fields, pd.DataFrame):
        missing_required_fields_df = missing_required_fields
    else:
        missing_required_fields_df = pd.DataFrame(
            missing_required_fields, columns=["Missing Required Field", "Loan Number"]
        )
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

    issue_count = len(issues_df) + len(missing_required_fields_df)
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
                "generated_at",
                "row_count",
                "issue_count",
                "warning_count",
                "executed_rules",
                "skipped_rules",
            ],
            "value": [
                generated_at,
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
        if isinstance(issues_df, pd.DataFrame):
            issues_df.to_excel(writer, index=False, sheet_name="issues")
            _autofit_columns(writer, "issues", issues_df)
        summary_df.to_excel(writer, index=False, sheet_name="summary")
        _autofit_columns(writer, "summary", summary_df)
        if isinstance(missing_required_fields_df, pd.DataFrame):
            missing_required_fields_df.to_excel(
                writer, index=False, sheet_name="missing_required_fields"
            )
            _autofit_columns(writer, "missing_required_fields", missing_required_fields_df)
        if isinstance(warnings_df, pd.DataFrame):
            warnings_df.to_excel(writer, index=False, sheet_name="warnings")
            _autofit_columns(writer, "warnings", warnings_df)
        if isinstance(skipped_rules_df, pd.DataFrame):
            skipped_rules_df.to_excel(writer, index=False, sheet_name="skipped_rules")
            _autofit_columns(writer, "skipped_rules", skipped_rules_df)
        if isinstance(validation_legend_df, pd.DataFrame):
            validation_legend_df.to_excel(writer, index=False, sheet_name="validation_legend")
            _autofit_columns(writer, "validation_legend", validation_legend_df)
