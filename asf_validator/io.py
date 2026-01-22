"""Input/output helpers for ASF Validator."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def read_tape(tape_path: Path) -> pd.DataFrame:
    """Read a tape file into a DataFrame.

    Placeholder implementation reads CSV or Excel based on suffix.
    """
    if tape_path.suffix.lower() in {".xls", ".xlsx"}:
        return pd.read_excel(tape_path)
    return pd.read_csv(tape_path)
