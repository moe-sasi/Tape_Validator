"""Regression tests for consolidated cash-out validation behavior."""

from __future__ import annotations

import pandas as pd

from asf_validator.engine import run_validations
from asf_validator.rules import get_validations_registry
from asf_validator.rules.asf_validations import (
    validate_cash_out_amount,
    validate_refi_cash_out_threshold,
)


RULE_NAME = "validate_cash_out_amount"
LEGACY_RULE_NAME = "validate_refi_cash_out_threshold"


def _rule_issue_count(results: dict, rule_name: str) -> int:
    issues = results["issues"]
    if issues.empty:
        return 0
    return int((issues["rule"] == rule_name).sum())


def test_cash_out_amount_flags_cash_out_refi_below_2000() -> None:
    assert validate_cash_out_amount(1500, 3, 300000) is True


def test_cash_out_amount_accepts_cash_out_refi_at_2000() -> None:
    assert validate_cash_out_amount(2000, 3, 300000) is False


def test_cash_out_amount_flags_refi_above_percent_threshold() -> None:
    assert validate_cash_out_amount(1500, 9, 100000) is True


def test_cash_out_amount_accepts_refi_within_combined_threshold() -> None:
    assert validate_cash_out_amount(1500, 9, 500000) is False


def test_cash_out_amount_flags_purchase_when_cash_out_exceeds_one_percent() -> None:
    assert validate_cash_out_amount(1500, 6, 100000) is True


def test_refi_cash_out_threshold_preserves_legacy_two_argument_behavior() -> None:
    assert validate_refi_cash_out_threshold(3, 1500) is True
    assert validate_refi_cash_out_threshold(9, 1500) is False
    assert validate_refi_cash_out_threshold(9, 2500) is True


def test_refi_cash_out_threshold_uses_consolidated_logic_when_original_loan_amount_provided() -> None:
    assert validate_refi_cash_out_threshold(9, 1500, 100000) is True
    assert validate_refi_cash_out_threshold(9, 1500, 500000) is False


def test_cash_out_registry_excludes_legacy_threshold_rule() -> None:
    registry = get_validations_registry()

    assert RULE_NAME in registry
    assert LEGACY_RULE_NAME not in registry


def test_engine_reports_only_consolidated_cash_out_rule() -> None:
    tape_df = pd.DataFrame(
        [
            {
                "loan_number": "LN-1",
                "cash_out_amount": 1500,
                "loan_purpose": 3,
                "original_loan_amount": 300000,
            }
        ]
    )

    results = run_validations(tape_df)

    assert _rule_issue_count(results, RULE_NAME) == 1
    assert _rule_issue_count(results, LEGACY_RULE_NAME) == 0
