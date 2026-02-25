"""Tests for original term-to-maturity date-gap validation."""

from __future__ import annotations

import pandas as pd

from asf_validator.engine import run_validations
from asf_validator.rules.asf_validations import validate_original_term_to_maturity_date_gap


RULE_NAME = "validate_original_term_to_maturity_date_gap"


def _rule_issue_count(results: dict, rule_name: str) -> int:
    issues = results["issues"]
    if issues.empty:
        return 0
    return int((issues["rule"] == rule_name).sum())


def test_original_term_to_maturity_gap_flags_when_difference_is_one() -> None:
    assert (
        validate_original_term_to_maturity_date_gap(
            first_payment_date_of_loan="2025-01-01",
            maturity_date="2055-01-01",
            original_term_to_maturity=360,
        )
        is True
    )


def test_original_term_to_maturity_gap_passes_when_terms_match() -> None:
    assert (
        validate_original_term_to_maturity_date_gap(
            first_payment_date_of_loan="2025-02-01",
            maturity_date="2055-01-01",
            original_term_to_maturity=360,
        )
        is False
    )


def test_original_term_to_maturity_gap_flags_on_missing_values() -> None:
    assert (
        validate_original_term_to_maturity_date_gap(
            first_payment_date_of_loan="",
            maturity_date="2055-01-01",
            original_term_to_maturity=360,
        )
        is True
    )


def test_engine_runs_original_term_to_maturity_date_gap_rule() -> None:
    tape_df = pd.DataFrame(
        [
            {
                "loan_number": "LN-1",
                "first_payment_date_of_loan": "2025-01-01",
                "maturity_date": "2055-01-01",
                "original_term_to_maturity": 360,
            }
        ]
    )

    results = run_validations(tape_df)
    skipped_rules = results["skipped_rules"]

    assert skipped_rules[skipped_rules["rule"] == RULE_NAME].empty
    assert _rule_issue_count(results, RULE_NAME) == 1
