"""Validation helpers for per-test execution durations."""

from __future__ import annotations

import math
from typing import Iterable, Mapping

from .types import TestId


def normalize_durations(
    durations: Mapping[TestId, float],
    test_ids: Iterable[TestId],
    *,
    context: str = "durations",
    require_complete: bool = True,
    require_positive: bool = True,
) -> dict[TestId, float]:
    """Return validated durations for the requested tests.

    Reportable APFDc and time-budget experiments need a real duration for every
    candidate test. Silent defaulting to one second makes cost-aware comparisons
    look valid when their cost source is actually incomplete.
    """

    requested = tuple(test_ids)
    missing = [test for test in requested if test not in durations]
    if missing and require_complete:
        preview = ", ".join(str(test) for test in missing[:5])
        suffix = "" if len(missing) <= 5 else f", ... ({len(missing)} missing)"
        raise ValueError(f"{context} missing tests: {preview}{suffix}")

    normalized: dict[TestId, float] = {}
    for test in requested:
        if test not in durations:
            continue
        value = float(durations[test])
        if not math.isfinite(value):
            raise ValueError(f"{context} for {test!r} must be finite")
        if require_positive and value <= 0:
            raise ValueError(f"{context} for {test!r} must be positive")
        if not require_positive and value < 0:
            raise ValueError(f"{context} for {test!r} must be non-negative")
        normalized[test] = value
    return normalized
