"""Registry for validation rule functions."""

from __future__ import annotations

from typing import Callable, Dict


def get_validations_registry() -> Dict[str, Callable]:
    """Return a mapping of validation names to callables.

    Placeholder implementation returns an empty registry.
    """
    return {}
