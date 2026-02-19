"""Regression tests for original appraisal 24-month age validation."""

from __future__ import annotations

import pandas as pd

from asf_validator.engine import run_validations
from asf_validator.rules.asf_validations import validate_original_appraisal_24_months_old


RULE_NAME = "validate_original_appraisal_24_months_old"


def _rule_issue_count(results: dict, rule_name: str) -> int:
    issues = results["issues"]
    if issues.empty:
        return 0
    return int((issues["rule"] == rule_name).sum())


def test_original_appraisal_uses_most_recent_valuation_date_when_newer() -> None:
    assert (
        validate_original_appraisal_24_months_old(
            original_property_valuation_date="2023-01-15",
            interest_paid_through_date="2026-01-31",
            most_recent_valuation_date="2025-03-10",
        )
        is False
    )


def test_original_appraisal_flags_when_most_recent_valuation_is_24_months_old() -> None:
    assert (
        validate_original_appraisal_24_months_old(
            original_property_valuation_date="2023-01-15",
            interest_paid_through_date="2026-01-31",
            most_recent_valuation_date="2023-12-01",
        )
        is True
    )


def test_original_appraisal_uses_most_recent_when_original_missing() -> None:
    assert (
        validate_original_appraisal_24_months_old(
            original_property_valuation_date="",
            interest_paid_through_date="2026-01-31",
            most_recent_valuation_date="2025-05-01",
        )
        is False
    )


def test_engine_runs_original_appraisal_rule_when_optional_column_missing() -> None:
    tape_df = pd.DataFrame(
        [
            {
                "loan_number": "LN-1",
                "original_property_valuation_date": "2023-01-01",
                "interest_paid_through_date": "2026-02-01",
            }
        ]
    )

    results = run_validations(tape_df)
    skipped_rules = results["skipped_rules"]

    assert skipped_rules[skipped_rules["rule"] == RULE_NAME].empty
    assert _rule_issue_count(results, RULE_NAME) == 1


def test_engine_original_appraisal_rule_uses_most_recent_when_present() -> None:
    tape_df = pd.DataFrame(
        [
            {
                "loan_number": "LN-1",
                "original_property_valuation_date": "2023-01-01",
                "most_recent_valuation_date": "2025-03-01",
                "interest_paid_through_date": "2026-02-01",
            }
        ]
    )

    results = run_validations(tape_df)

    assert _rule_issue_count(results, RULE_NAME) == 0


def test_engine_original_appraisal_rule_uses_property_named_most_recent_date() -> None:
    tape_df = pd.DataFrame(
        [
            {
                "loan_number": "LN-1",
                "original_property_valuation_date": "2023-01-01",
                "most_recent_property_valuation_date": "2025-03-01",
                "interest_paid_through_date": "2026-02-01",
            }
        ]
    )

    results = run_validations(tape_df)

    assert _rule_issue_count(results, RULE_NAME) == 0
