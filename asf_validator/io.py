"""Input/output helpers for ASF Validator."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def read_tape(tape_path: Path) -> pd.DataFrame:
    """Read a tape file into a DataFrame.

    Placeholder implementation reads CSV or Excel based on suffix.
    """
    if tape_path.suffix.lower() in {".xls", ".xlsx"}:
        df = pd.read_excel(tape_path)
    else:
        df = pd.read_csv(tape_path)

    if "Loan Number" in df.columns:
        df = df[df["Loan Number"].notna()].copy()

    return df
