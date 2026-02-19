"""Regression tests for percent/rate fields provided above 1.0."""

from __future__ import annotations

import pandas as pd

from asf_validator.engine import run_validations
from asf_validator.rules.asf_validations import validate_percentage_fields_over_one


RULE_NAME = "validate_percentage_fields_over_one"


def _rule_issue_count(results: dict, rule_name: str) -> int:
    issues = results["issues"]
    if issues.empty:
        return 0
    return int((issues["rule"] == rule_name).sum())


def test_percentage_fields_over_one_flags_lifetime_max_rate_above_one() -> None:
    assert validate_percentage_fields_over_one(lifetime_max_rate_ceiling=108.75) is True


def test_percentage_fields_over_one_allows_decimal_lifetime_max_rate() -> None:
    assert validate_percentage_fields_over_one(lifetime_max_rate_ceiling=0.10875) is False


def test_percentage_fields_over_one_ignores_exception_fields() -> None:
    assert (
        validate_percentage_fields_over_one(
            subsequent_interest_rate_reset_period=6,
            subsequent_interest_rate_cap_change_down=2,
            subsequent_interest_rate_cap_change_up=2,
            subsequent_payment_reset_period=12,
            mortgage_insurance_percent=25,
        )
        is False
    )


def test_engine_flags_percentage_rule_for_value_above_one() -> None:
    tape_df = pd.DataFrame(
        [
            {
                "loan_number": "LN-00001",
                "Lifetime Maximum Rate (Ceiling)": 108.75,
            }
        ]
    )

    results = run_validations(tape_df)
    matching = results["issues"][results["issues"]["rule"] == RULE_NAME]

    assert _rule_issue_count(results, RULE_NAME) == 1
    assert matching.iloc[0]["columns"] == "Lifetime Maximum Rate (Ceiling)"


def test_engine_does_not_flag_percentage_rule_for_decimal_value() -> None:
    tape_df = pd.DataFrame(
        [
            {
                "loan_number": "LN-00001",
                "Lifetime Maximum Rate (Ceiling)": 0.10875,
            }
        ]
    )

    results = run_validations(tape_df)

    assert _rule_issue_count(results, RULE_NAME) == 0


def test_engine_flags_each_percentage_field_above_one() -> None:
    tape_df = pd.DataFrame(
        [
            {
                "loan_number": "LN-00001",
                "Lifetime Maximum Rate (Ceiling)": 108.75,
                "Original Interest Rate": 1.25,
            }
        ]
    )

    results = run_validations(tape_df)
    matching = results["issues"][results["issues"]["rule"] == RULE_NAME]

    assert len(matching) == 2
    assert set(matching["columns"].tolist()) == {
        "Lifetime Maximum Rate (Ceiling)",
        "Original Interest Rate",
    }


def test_engine_ignores_exception_fields_over_one() -> None:
    tape_df = pd.DataFrame(
        [
            {
                "loan_number": "LN-00001",
                "Subsequent Interest Rate Reset Period": 6,
                "Subsequent Interest Rate Cap (Change Down)": 2,
                "Subsequent Interest Rate Cap (Change Up)": 2,
                "Subsequent Payment Reset Period": 12,
                "Mortgage Insurance Percent": 25,
            }
        ]
    )

    results = run_validations(tape_df)

    assert _rule_issue_count(results, RULE_NAME) == 0
