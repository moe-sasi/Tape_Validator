"""Report generation for ASF validation output."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

import pandas as pd


def write_report(results: Mapping[str, Any], output_path: Path) -> None:
    """Write validation results to an Excel report.

    Placeholder implementation writes summary metadata.
    """
    summary_df = pd.DataFrame(
        {
            "metric": ["row_count", "columns", "issue_count"],
            "value": [
                results.get("row_count", 0),
                ", ".join(results.get("columns", [])),
                len(results.get("issues", [])),
            ],
        }
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary_df.to_excel(output_path, index=False, sheet_name="summary")
