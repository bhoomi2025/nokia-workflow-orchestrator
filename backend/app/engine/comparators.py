"""
Comparator registry (spec 2.3): pluggable functions comparing a
registered variable's value against an expected value (e.g. for
`until` / `break_when` conditions, or explicit comparator tasks).

Same extension pattern as validators.py -- add a function, register
it in COMPARATOR_REGISTRY.
"""

from typing import Callable


def _equals(actual, expected) -> bool:
    return actual == expected


def _not_equals(actual, expected) -> bool:
    return actual != expected


def _greater_than(actual, expected) -> bool:
    return actual > expected


def _less_than(actual, expected) -> bool:
    return actual < expected


def _contains(actual, expected) -> bool:
    return expected in actual


COMPARATOR_REGISTRY: dict[str, Callable[..., bool]] = {
    "equals": _equals,
    "not_equals": _not_equals,
    "greater_than": _greater_than,
    "less_than": _less_than,
    "contains": _contains,
}


def run_comparator(name: str, actual, expected) -> dict:
    fn = COMPARATOR_REGISTRY.get(name)
    if fn is None:
        return {"passed": False, "message": f"unknown comparator '{name}'"}
    try:
        passed = fn(actual, expected)
    except Exception as exc:  # noqa: BLE001 -- surfaced to the task result, not raised
        return {"passed": False, "message": f"comparator error: {exc}"}
    return {"passed": passed, "message": f"{actual!r} {name} {expected!r} -> {passed}"}