"""Input/output helpers for ASF Validator."""

from __future__ import annotations

import numbers
import re
from pathlib import Path

import pandas as pd

# Tape columns that should be treated as numeric even when provided as
# currency-formatted strings (commas, dollar signs, or parentheses).
_NUMERIC_COLUMNS = [
    "Cash Out Amount",
    "Senior Loan Amount(s)",
    "Junior Mortgage Balance",
    "Original Loan Amount",
    "Current Loan Amount",
    "Current Payment Amount Due",
    "Current 'Other' Monthly Payment",
    "Current ‘Other’ Monthly Payment",
    "Length of Employment: Borrower",
    "Length of Employment: Co-Borrower",
    "Years in Home",
    "Most Recent 12-month Pay History",
    "Months Foreclosure",
    "Primary Borrower Wage Income",
    "Co-Borrower Wage Income",
    "Primary Borrower Other Income",
    "Co-Borrower Other Income",
    "All Borrower Wage Income",
    "All Borrower Total Income",
    "Liquid / Cash Reserves",
    "Monthly Debt All Borrowers",
    "Sales Price",
    "Original Appraised Property Value",
    "Most Recent Property Value2",
    "Cash To/From Borrower at Closing",
    "Borrower - Yrs at in Industry",
    "Co-Borrower - Yrs at in Industry",
]

_PERCENT_COLUMNS = [
    "Servicing Fee %",
    "Original Interest Rate",
    "Current Interest Rate",
    "Gross Margin",
    "Lifetime Maximum Rate (Ceiling)",
    "Lifetime Minimum Rate (Floor)",
    "Originator DTI",
    "Percentage of Down Payment from Borrower Own Funds",
    "Original AVM Confidence Score",
    "Most Recent AVM Confidence Score",
    "Original CLTV",
    "Original LTV",
]


def _coerce_numeric_value(value: object) -> float | None:
    """Best-effort conversion of currency-like strings to floats."""
    if value is None:
        return None
    if isinstance(value, numbers.Number):
        return float(value)
    if isinstance(value, str):
        cleaned = value.strip()
        if cleaned == "":
            return None

        is_negative = cleaned.startswith("(") and cleaned.endswith(")")
        # Drop surrounding parentheses used to denote negatives.
        if is_negative:
            cleaned = cleaned[1:-1]

        cleaned = cleaned.replace(",", "")
        cleaned = cleaned.replace("$", "")
        cleaned = cleaned.replace(" ", "")
        cleaned = cleaned.replace("−", "-").replace("–", "-").replace("—", "-")

        try:
            number = float(cleaned)
            return -number if is_negative else number
        except ValueError:
            match = re.search(r"-?\d+(?:\.\d+)?", cleaned)
            if match:
                try:
                    number = float(match.group())
                    return -number if is_negative else number
                except ValueError:
                    return None
            return None

    try:
        return float(value)
    except Exception:
        return None


def _coerce_percent_value(value: object) -> float | None:
    """Convert percentage-like values to decimal floats (e.g., '95%' -> 0.95)."""
    if value is None:
        return None

    has_percent = False
    if isinstance(value, str):
        cleaned = value.strip()
        if cleaned == "":
            return None
        if "%" in cleaned:
            has_percent = True
            cleaned = cleaned.replace("%", "")
        numeric = _coerce_numeric_value(cleaned)
    else:
        numeric = _coerce_numeric_value(value)

    if numeric is None:
        return None

    # Scale down to decimal when explicitly marked as percent or when clearly a whole-number percent.
    if has_percent or abs(numeric) > 2:
        return numeric / 100
    return numeric


def _coerce_numeric_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize known numeric columns to floats to avoid validation failures."""
    for column in _NUMERIC_COLUMNS:
        if column in df.columns:
            df[column] = df[column].apply(_coerce_numeric_value)
    return df


def _coerce_percent_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize known percent columns to decimal floats."""
    for column in _PERCENT_COLUMNS:
        if column in df.columns:
            df[column] = df[column].apply(_coerce_percent_value)
    return df


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

    df = _coerce_percent_columns(df)
    df = _coerce_numeric_columns(df)

    return df
