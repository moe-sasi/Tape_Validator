"""Regression tests for missing required-field behavior."""

from __future__ import annotations

import inspect

import pandas as pd

from asf_validator.engine import run_validations
from asf_validator.rules.asf_validations import validate_missing_required_fields


def _required_field_kwargs() -> dict[str, object]:
    params = inspect.signature(validate_missing_required_fields).parameters
    values: dict[str, object] = {name: 1 for name in params}
    values["loan_number"] = "LN-1"
    values["primary_servicer"] = "SERVICER"
    values["total_number_of_borrowers"] = 1
    values["length_of_employment_co_borrower"] = 1
    return values


def test_missing_required_fields_co_borrower_not_required_for_single_borrower() -> None:
    values = _required_field_kwargs()
    values["total_number_of_borrowers"] = 1
    values["length_of_employment_co_borrower"] = ""

    assert validate_missing_required_fields(**values) is False


def test_missing_required_fields_co_borrower_required_for_multiple_borrowers() -> None:
    values = _required_field_kwargs()
    values["total_number_of_borrowers"] = 2
    values["length_of_employment_co_borrower"] = ""

    assert validate_missing_required_fields(**values) is True


def test_missing_required_fields_co_borrower_zero_is_populated() -> None:
    values = _required_field_kwargs()
    values["total_number_of_borrowers"] = 2
    values["length_of_employment_co_borrower"] = 0

    assert validate_missing_required_fields(**values) is False


def test_missing_required_report_excludes_co_borrower_for_single_borrower() -> None:
    row = _required_field_kwargs()
    row["primary_servicer"] = ""
    row["total_number_of_borrowers"] = 1
    row["length_of_employment_co_borrower"] = ""

    results = run_validations(pd.DataFrame([row]))
    missing_fields = set(results["missing_required_fields"]["Missing Required Field"].tolist())

    assert "primary_servicer" in missing_fields
    assert "length_of_employment_co_borrower" not in missing_fields


def test_missing_required_report_includes_co_borrower_for_multiple_borrowers() -> None:
    row = _required_field_kwargs()
    row["total_number_of_borrowers"] = 2
    row["length_of_employment_co_borrower"] = ""

    results = run_validations(pd.DataFrame([row]))
    missing_fields = set(results["missing_required_fields"]["Missing Required Field"].tolist())

    assert "length_of_employment_co_borrower" in missing_fields
