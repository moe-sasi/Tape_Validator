"""Registry for validation rule functions."""

from __future__ import annotations

from typing import Callable, Dict

from asf_validator.rules import asf_validations


def get_validations_registry() -> Dict[str, Callable]:
    """Return a mapping of validation names to callables.

    Uses the validation functions defined in asf_validations.
    """
    registry: Dict[str, Callable] = {}
    for name in getattr(asf_validations, "__all__", []):
        if name.startswith("validate_"):
            registry[name] = getattr(asf_validations, name)
    if not registry:
        for name, value in vars(asf_validations).items():
            if name.startswith("validate_") and callable(value):
                registry[name] = value
    return dict(sorted(registry.items()))
