"""Regression tests for Original vs Most Recent Property Value2 variance validation."""

from __future__ import annotations

import pandas as pd

from asf_validator.engine import run_validations
from asf_validator.rules.asf_validations import validate_property_value2_variance_over_10_percent


RULE_NAME = "validate_property_value2_variance_over_10_percent"


def _rule_issue_count(results: dict, rule_name: str) -> int:
    issues = results["issues"]
    if issues.empty:
        return 0
    return int((issues["rule"] == rule_name).sum())


def test_property_value2_variance_exactly_10_percent_not_flagged() -> None:
    assert (
        validate_property_value2_variance_over_10_percent(
            original_appraised_property_value=100000,
            most_recent_property_value2=110000,
        )
        is False
    )


def test_property_value2_variance_above_10_percent_upward_flagged() -> None:
    assert (
        validate_property_value2_variance_over_10_percent(
            original_appraised_property_value=100000,
            most_recent_property_value2=110001,
        )
        is True
    )


def test_property_value2_variance_above_10_percent_downward_flagged() -> None:
    assert (
        validate_property_value2_variance_over_10_percent(
            original_appraised_property_value=100000,
            most_recent_property_value2=89999,
        )
        is True
    )


def test_property_value2_variance_missing_values_not_flagged() -> None:
    assert (
        validate_property_value2_variance_over_10_percent(
            original_appraised_property_value="",
            most_recent_property_value2=100000,
        )
        is False
    )
    assert (
        validate_property_value2_variance_over_10_percent(
            original_appraised_property_value=100000,
            most_recent_property_value2="",
        )
        is False
    )


def test_property_value2_variance_zero_or_negative_original_flagged() -> None:
    assert (
        validate_property_value2_variance_over_10_percent(
            original_appraised_property_value=0,
            most_recent_property_value2=100000,
        )
        is True
    )
    assert (
        validate_property_value2_variance_over_10_percent(
            original_appraised_property_value=-100000,
            most_recent_property_value2=100000,
        )
        is True
    )


def test_engine_flags_property_value2_variance_over_10_percent() -> None:
    tape_df = pd.DataFrame(
        [
            {
                "Loan Number": "LN-1",
                "Original Appraised Property Value": 100000,
                "Most Recent Property Value2": 112000,
            },
            {
                "Loan Number": "LN-2",
                "Original Appraised Property Value": 100000,
                "Most Recent Property Value2": 105000,
            },
        ]
    )

    results = run_validations(tape_df)
    skipped_rules = results["skipped_rules"]
    issues = results["issues"]

    assert skipped_rules[skipped_rules["rule"] == RULE_NAME].empty
    assert _rule_issue_count(results, RULE_NAME) == 1

    rule_issues = issues[issues["rule"] == RULE_NAME]
    assert len(rule_issues) == 1
    assert rule_issues.iloc[0]["loan_number"] == "LN-1"
