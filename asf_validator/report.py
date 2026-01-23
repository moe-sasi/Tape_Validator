"""Report generation for ASF validation output."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

import pandas as pd


def write_report(results: Mapping[str, Any], output_path: Path) -> None:
    """Write validation results to an Excel report.

    Writes summary metadata and any provided detail tables.
    """
    issues = results.get("issues", [])
    issues_df = issues if isinstance(issues, pd.DataFrame) else pd.DataFrame(issues)
    rule_summary_df = results.get("rule_summary")
    skipped_rules_df = results.get("skipped_rules")

    issue_count = len(issues_df)
    executed_rules = len(rule_summary_df) if isinstance(rule_summary_df, pd.DataFrame) else 0
    skipped_rules = len(skipped_rules_df) if isinstance(skipped_rules_df, pd.DataFrame) else 0

    summary_df = pd.DataFrame(
        {
            "metric": ["row_count", "issue_count", "executed_rules", "skipped_rules"],
            "value": [
                results.get("row_count", 0),
                issue_count,
                executed_rules,
                skipped_rules,
            ],
        }
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(output_path) as writer:
        summary_df.to_excel(writer, index=False, sheet_name="summary")
        if isinstance(issues_df, pd.DataFrame):
            issues_df.to_excel(writer, index=False, sheet_name="issues")
        if isinstance(rule_summary_df, pd.DataFrame):
            rule_summary_df.to_excel(writer, index=False, sheet_name="rule_summary")
        if isinstance(skipped_rules_df, pd.DataFrame):
            skipped_rules_df.to_excel(writer, index=False, sheet_name="skipped_rules")
