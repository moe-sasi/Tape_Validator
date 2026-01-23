"""Utility helpers for ASF Validator."""

from __future__ import annotations

from datetime import datetime
import re
from typing import Iterable, Optional

import pandas as pd


def normalize_columns(columns: Iterable[str]) -> list[str]:
    """Normalize column names to lowercase snake-case."""
    normalized = []
    for col in columns:
        cleaned = re.sub(r"[^0-9A-Za-z]+", "_", str(col).strip().lower())
        cleaned = cleaned.strip("_")
        cleaned = re.sub(r"_+", "_", cleaned)
        normalized.append(cleaned)
    return normalized


def safe_float(value: object) -> Optional[float]:
    """Convert a value to float when possible."""
    try:
        if value is None or (isinstance(value, str) and not value.strip()):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def safe_int(value: object) -> Optional[int]:
    """Convert a value to int when possible."""
    try:
        if value is None or (isinstance(value, str) and not value.strip()):
            return None
        return int(float(value))
    except (TypeError, ValueError):
        return None


def safe_date(value: object, date_format: str = "%Y-%m-%d") -> Optional[datetime]:
    """Parse a date from a string or datetime-like value."""
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, pd.Timestamp):
        return value.to_pydatetime()
    try:
        return datetime.strptime(str(value), date_format)
    except (TypeError, ValueError):
        return None
