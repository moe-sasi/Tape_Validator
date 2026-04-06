"""Regression tests for valuation age validation."""

from __future__ import annotations

import pandas as pd

from asf_validator.engine import run_validations
from asf_validator.rules.asf_validations import validate_valuation_age


RULE_NAME = "validate_valuation_age"


def _rule_issue_count(results: dict, rule_name: str) -> int:
    issues = results["issues"]
    if issues.empty:
        return 0
    return int((issues["rule"] == rule_name).sum())


def test_valuation_age_accepts_recent_most_recent_valuation_date() -> None:
    assert (
        validate_valuation_age(
            original_property_valuation_date="2025-01-01",
            origination_date="2026-01-01",
            most_recent_property_valuation_date="2025-12-01",
        )
        is False
    )


def test_valuation_age_flags_when_all_populated_valuations_are_older_than_180_days() -> None:
    assert (
        validate_valuation_age(
            original_property_valuation_date="2025-01-01",
            origination_date="2026-01-01",
            most_recent_property_valuation_date="2025-06-01",
        )
        is True
    )


def test_valuation_age_uses_most_recent_when_original_missing() -> None:
    assert (
        validate_valuation_age(
            original_property_valuation_date="",
            origination_date="2026-01-01",
            most_recent_property_valuation_date="2025-12-01",
        )
        is False
    )


def test_engine_valuation_age_uses_most_recent_property_valuation_date() -> None:
    tape_df = pd.DataFrame(
        [
            {
                "Loan Number": "LN-1",
                "Original Property Valuation Date": "2025-01-01",
                "Most Recent Property Valuation Date": "2025-12-01",
                "Origination Date": "2026-01-01",
            }
        ]
    )

    results = run_validations(tape_df)

    assert _rule_issue_count(results, RULE_NAME) == 0
