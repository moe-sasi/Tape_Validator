"""Validation engine for ASF tapes."""

from __future__ import annotations

import inspect
import logging
import bdb
from typing import Iterable

import pandas as pd

from asf_validator.rules import get_validations_registry
from asf_validator.rules.asf_validations import _is_blank
from asf_validator.util import normalize_columns

_LOGGER = logging.getLogger(__name__)

_PARAM_ALIASES = {
    "pbw": "primary_borrower_wage_income",
    "cbw": "co_borrower_wage_income",
    "pbo": "primary_borrower_other_income",
    "cbo": "co_borrower_other_income",
    "abti": "all_borrower_total_income",
    "abw": "all_borrower_wage_income",
    "total_borrowers": "total_number_of_borrowers",
    "b1_len_emp": "length_of_employment_borrower",
    "b2_len_emp": "length_of_employment_co_borrower",
    "b1_emp_ver": "borrower_employment_verification",
    "b2_emp_ver": "co_borrower_employment_verification",
    "application_date": "application_received_date",
    "percent_down_payment": "percentage_of_down_payment_from_borrower_own_funds",
    "cap_up": "initial_interest_rate_cap_change_up",
    "cap_down": "initial_interest_rate_cap_change_down",
    "first_payment_date": "first_payment_date_of_loan",
    "junior_drawn_amount": "junior_mortgage_drawn_amount",
    "lifetime_max_rate_ceiling": "lifetime_maximum_rate_ceiling",
    "lifetime_min_rate_floor": "lifetime_minimum_rate_floor",
    "borrower_fico_score": "original_primary_borrower_fico",
}

_VARARGS_RULE_COLUMNS = {
    "validate_negative_incomes": [
        "primary_borrower_wage_income",
        "co_borrower_wage_income",
        "primary_borrower_other_income",
        "co_borrower_other_income",
        "all_borrower_wage_income",
        "all_borrower_total_income",
    ]
}

_ALLOW_MISSING_PARAM_RULES = {
    "validate_arm_fields_populated_for_fixed_rate",
    "validate_arm_fields_required_for_adjustable_rate",
    "validate_missing_required_fields",
    "validate_most_recent_fico_recency",
}

_WARNING_RULES = {
    "validate_margin_less_than_floor",
    "validate_negative_incomes",
    "validate_refi_with_less_than_1_year_in_home",
    "validate_appraised_value_over_8000000",
    "validate_total_number_of_borrowers_over_4",
}

_CANONICAL_REPLACEMENTS = {
    "yrs": "years",
    "yr": "year",
    "pct": "percent",
    "num": "number",
    "nbr": "number",
    "amt": "amount",
}

_STOPWORDS = {"of", "the", "and", "or", "at", "in", "for", "to", "from"}


def _normalize_name(name: str) -> str:
    return normalize_columns([name])[0]


def _canonical_key(name: str) -> str:
    tokens = _normalize_name(name).split("_")
    canonical_tokens = []
    for token in tokens:
        if not token or token in _STOPWORDS:
            continue
        canonical_tokens.append(_CANONICAL_REPLACEMENTS.get(token, token))
    return "".join(canonical_tokens)


def _build_column_maps(columns: Iterable[str]) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    normalized_map: dict[str, list[str]] = {}
    canonical_map: dict[str, list[str]] = {}
    for col in columns:
        normalized = _normalize_name(col)
        canonical = _canonical_key(col)
        normalized_map.setdefault(normalized, []).append(col)
        canonical_map.setdefault(canonical, []).append(col)
    return normalized_map, canonical_map


def _resolve_column_name(
    name: str,
    normalized_map: dict[str, list[str]],
    canonical_map: dict[str, list[str]],
) -> str | None:
    normalized = _normalize_name(name)
    if normalized in normalized_map:
        return normalized_map[normalized][0]
    canonical = _canonical_key(name)
    if canonical in canonical_map:
        return canonical_map[canonical][0]
    return None


def _resolve_param_name(
    param_name: str,
    normalized_map: dict[str, list[str]],
    canonical_map: dict[str, list[str]],
) -> str | None:
    alias = _PARAM_ALIASES.get(param_name, param_name)
    return _resolve_column_name(alias, normalized_map, canonical_map)


def run_validations(tape_df: pd.DataFrame) -> dict:
    """Run validation rules against the tape data."""
    registry = get_validations_registry()
    normalized_map, canonical_map = _build_column_maps(tape_df.columns)
    issues: list[dict[str, object]] = []
    warnings: list[dict[str, object]] = []
    missing_required_records: list[dict[str, object]] = []
    rule_summary: list[dict[str, object]] = []
    warning_summary: list[dict[str, object]] = []
    skipped_rules: list[dict[str, str]] = []
    loan_number_column = _resolve_column_name("loan_number", normalized_map, canonical_map)

    for rule_name, func in registry.items():
        is_warning = rule_name in _WARNING_RULES
        issue_bucket = warnings if is_warning else issues
        summary_bucket = warning_summary if is_warning else rule_summary
        signature = inspect.signature(func)
        params = list(signature.parameters.values())
        varargs = next(
            (param for param in params if param.kind == inspect.Parameter.VAR_POSITIONAL),
            None,
        )

        if varargs:
            column_names = _VARARGS_RULE_COLUMNS.get(rule_name)
            if not column_names:
                skipped_rules.append(
                    {
                        "rule": rule_name,
                        "reason": "missing_varargs_mapping",
                        "missing_columns": varargs.name,
                    }
                )
                continue
            columns = []
            missing = []
            for column_name in column_names:
                resolved = _resolve_column_name(column_name, normalized_map, canonical_map)
                if resolved is None:
                    missing.append(column_name)
                else:
                    columns.append(resolved)
            if missing:
                skipped_rules.append(
                    {
                        "rule": rule_name,
                        "reason": "missing_columns",
                        "missing_columns": ", ".join(missing),
                    }
                )
                continue
        else:
            columns = []
            missing = []
            param_columns: list[str | None] = []
            for param in params:
                resolved = _resolve_param_name(param.name, normalized_map, canonical_map)
                if resolved is None:
                    missing.append(param.name)
                    param_columns.append(None)
                else:
                    columns.append(resolved)
                    param_columns.append(resolved)
            if missing:
                if rule_name in _ALLOW_MISSING_PARAM_RULES:
                    missing = []
                else:
                    skipped_rules.append(
                        {
                            "rule": rule_name,
                            "reason": "missing_columns",
                            "missing_columns": ", ".join(missing),
                        }
                    )
                    continue
            
        if rule_name == "validate_missing_required_fields" and not varargs:
            display_columns = []
            for param, resolved in zip(params, param_columns):
                if resolved is None:
                    display_columns.append(_PARAM_ALIASES.get(param.name, param.name))
                else:
                    display_columns.append(resolved)

            def apply_missing_required(row: pd.Series) -> bool:
                values = [
                    row[col] if col is not None else None
                    for col in param_columns
                ]
                return bool(func(*values))

            def collect_missing_required(row: pd.Series) -> list[str]:
                missing_columns: list[str] = []
                for resolved, display in zip(param_columns, display_columns):
                    value = row[resolved] if resolved is not None else None
                    if _is_blank(value):
                        missing_columns.append(display)
                return missing_columns

            issue_mask = tape_df.apply(apply_missing_required, axis=1)
            issue_mask = issue_mask.fillna(False).astype(bool)
            missing_per_row = tape_df[issue_mask].apply(collect_missing_required, axis=1)
            missing_record_count = int(sum(len(missing) for missing in missing_per_row))
            summary_bucket.append({"rule": rule_name, "issue_count": missing_record_count})

            if missing_record_count == 0:
                continue

            for row_index in missing_per_row.index:
                loan_number_value = (
                    tape_df.at[row_index, loan_number_column] if loan_number_column else None
                )
                for missing_field in missing_per_row.at[row_index]:
                    missing_required_records.append(
                        {
                            "Missing Required Field": missing_field,
                            "Loan Number": loan_number_value,
                        }
                    )
            continue

        def apply_rule(row: pd.Series) -> bool:
            try:
                if varargs:
                    values = [row[col] for col in columns]
                else:
                    values = [
                        row[col] if col is not None else None
                        for col in param_columns
                    ]
                return bool(func(*values))
            except Exception as exc:  # pragma: no cover - defensive
                if isinstance(exc, bdb.BdbQuit):
                    raise
                return True

        mask = tape_df.apply(apply_rule, axis=1)
        mask = mask.fillna(False).astype(bool)
        issue_count = int(mask.sum())
        summary_bucket.append({"rule": rule_name, "issue_count": issue_count})

        if issue_count == 0:
            continue

        for row_index in mask[mask].index:
            record: dict[str, object] = {
                "rule": rule_name,
                "row_index": row_index,
                "columns": ", ".join(columns),
            }
            if loan_number_column:
                record["loan_number"] = tape_df.at[row_index, loan_number_column]
            issue_bucket.append(record)

    issues_columns = ["rule", "row_index", "columns"]
    if loan_number_column:
        issues_columns.insert(2, "loan_number")
    issues_df = pd.DataFrame(issues, columns=issues_columns)
    warnings_df = pd.DataFrame(warnings, columns=issues_columns)
    missing_required_fields_df = pd.DataFrame(
        missing_required_records, columns=["Missing Required Field", "Loan Number"]
    )
    rule_summary_df = pd.DataFrame(rule_summary)
    if not rule_summary_df.empty:
        rule_summary_df = rule_summary_df.sort_values("rule").reset_index(drop=True)
    else:
        rule_summary_df = pd.DataFrame(columns=["rule", "issue_count"])

    warning_summary_df = pd.DataFrame(warning_summary)
    if not warning_summary_df.empty:
        warning_summary_df = warning_summary_df.sort_values("rule").reset_index(drop=True)
    else:
        warning_summary_df = pd.DataFrame(columns=["rule", "issue_count"])

    skipped_rules_df = pd.DataFrame(skipped_rules)
    if not skipped_rules_df.empty:
        skipped_rules_df = skipped_rules_df.sort_values("rule").reset_index(drop=True)
    else:
        skipped_rules_df = pd.DataFrame(columns=["rule", "reason", "missing_columns"])

    if skipped_rules_df.empty:
        _LOGGER.debug("All validation rules resolved to input columns.")

    return {
        "row_count": len(tape_df),
        "columns": list(tape_df.columns),
        "issues": issues_df,
        "warnings": warnings_df,
        "missing_required_fields": missing_required_fields_df,
        "rule_summary": rule_summary_df,
        "warning_summary": warning_summary_df,
        "skipped_rules": skipped_rules_df,
    }
