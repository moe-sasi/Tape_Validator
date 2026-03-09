"""Regression tests for Most Recent Property Valuation Type AVM/BPO validation."""

from __future__ import annotations

import pandas as pd

from asf_validator.engine import run_validations
from asf_validator.rules.asf_validations import (
    validate_most_recent_property_valuation_type_avm_or_bpo,
)


RULE_NAME = "validate_most_recent_property_valuation_type_avm_or_bpo"


def _rule_issue_count(results: dict, rule_name: str) -> int:
    issues = results["issues"]
    if issues.empty:
        return 0
    return int((issues["rule"] == rule_name).sum())


def test_most_recent_property_valuation_type_accepts_avm_case_insensitive() -> None:
    assert (
        validate_most_recent_property_valuation_type_avm_or_bpo(
            most_recent_property_valuation_type="avm",
        )
        is False
    )


def test_most_recent_property_valuation_type_accepts_bpo() -> None:
    assert (
        validate_most_recent_property_valuation_type_avm_or_bpo(
            most_recent_property_valuation_type="BPO",
        )
        is False
    )


def test_most_recent_property_valuation_type_accepts_numeric_code() -> None:
    assert (
        validate_most_recent_property_valuation_type_avm_or_bpo(
            most_recent_property_valuation_type=10,
        )
        is False
    )


def test_most_recent_property_valuation_type_accepts_code_with_description() -> None:
    assert (
        validate_most_recent_property_valuation_type_avm_or_bpo(
            most_recent_property_valuation_type="10 BPO as-is",
        )
        is False
    )


def test_most_recent_property_valuation_type_accepts_long_description_text() -> None:
    assert (
        validate_most_recent_property_valuation_type_avm_or_bpo(
            most_recent_property_valuation_type="Automated Valuation Model (also indicate system code in field 127)",
        )
        is False
    )


def test_most_recent_property_valuation_type_flags_invalid_value() -> None:
    assert (
        validate_most_recent_property_valuation_type_avm_or_bpo(
            most_recent_property_valuation_type="APPRAISAL",
        )
        is True
    )


def test_most_recent_property_valuation_type_flags_invalid_numeric_code() -> None:
    assert (
        validate_most_recent_property_valuation_type_avm_or_bpo(
            most_recent_property_valuation_type=17,
        )
        is True
    )


def test_most_recent_property_valuation_type_blank_not_flagged() -> None:
    assert (
        validate_most_recent_property_valuation_type_avm_or_bpo(
            most_recent_property_valuation_type="",
        )
        is False
    )


def test_engine_flags_invalid_most_recent_property_valuation_type() -> None:
    tape_df = pd.DataFrame(
        [
            {
                "Loan Number": "LN-1",
                "Most Recent Property Valuation Type": "AVM",
            },
            {
                "Loan Number": "LN-2",
                "Most Recent Property Valuation Type": "BPO",
            },
            {
                "Loan Number": "LN-3",
                "Most Recent Property Valuation Type": 17,
            },
            {
                "Loan Number": "LN-4",
                "Most Recent Property Valuation Type": "",
            },
            {
                "Loan Number": "LN-5",
                "Most Recent Property Valuation Type": "7 Automated Valuation Model (also indicate system code in field 127)",
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
    assert rule_issues.iloc[0]["loan_number"] == "LN-3"
