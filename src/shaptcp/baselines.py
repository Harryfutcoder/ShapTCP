"""Baseline prioritizers for matrix-based experiments."""

from __future__ import annotations

import random
from typing import Iterable, Mapping

from .durations import normalize_durations
from .types import FaultId, TestId


def random_order(
    test_to_faults: Mapping[TestId, Iterable[FaultId]],
    *,
    seed: int | None = None,
) -> tuple[TestId, ...]:
    """Random baseline with deterministic seed support."""

    rng = random.Random(seed)
    tests = list(test_to_faults)
    rng.shuffle(tests)
    return tuple(tests)


def total_coverage_order(test_to_faults: Mapping[TestId, Iterable[FaultId]]) -> tuple[TestId, ...]:
    """Sort tests by total entity coverage count."""

    normalized = _normalize_matrix(test_to_faults)
    return tuple(sorted(normalized, key=lambda test: (-len(normalized[test]), str(test))))


def additional_coverage_order(
    test_to_faults: Mapping[TestId, Iterable[FaultId]],
    *,
    budget_count: int | None = None,
) -> tuple[TestId, ...]:
    """Classic greedy additional coverage baseline."""

    normalized = _normalize_matrix(test_to_faults)
    if budget_count is None:
        budget_count = len(normalized)

    remaining_tests = set(normalized)
    covered_faults: set[FaultId] = set()
    order: list[TestId] = []

    while remaining_tests and len(order) < budget_count:
        best = max(
            remaining_tests,
            key=lambda test: (len(normalized[test] - covered_faults), len(normalized[test]), _reverse_sort_key(test)),
        )
        order.append(best)
        remaining_tests.remove(best)
        covered_faults.update(normalized[best])
    return tuple(order)


def cost_aware_additional_coverage_order(
    test_to_faults: Mapping[TestId, Iterable[FaultId]],
    durations: Mapping[TestId, float],
    *,
    budget_count: int | None = None,
    time_budget: float | None = None,
    cost_exponent: float = 1.0,
) -> tuple[TestId, ...]:
    """Greedy additional coverage divided by duration^cost_exponent."""

    if budget_count is None and time_budget is None:
        budget_count = len(test_to_faults)
    if budget_count is not None and budget_count < 0:
        raise ValueError("budget_count must be non-negative")
    if time_budget is not None and time_budget < 0:
        raise ValueError("time_budget must be non-negative")
    if cost_exponent < 0:
        raise ValueError("cost_exponent must be non-negative")

    normalized = _normalize_matrix(test_to_faults)
    costs = normalize_durations(durations, normalized, context="durations")
    remaining_tests = set(normalized)
    covered_faults: set[FaultId] = set()
    order: list[TestId] = []
    cumulative_time = 0.0

    while remaining_tests:
        if budget_count is not None and len(order) >= budget_count:
            break

        best_test: TestId | None = None
        best_key: tuple[float, float, float] | None = None

        for test in sorted(remaining_tests, key=str):
            duration = costs[test]
            if time_budget is not None and cumulative_time + duration > time_budget:
                continue

            new_count = len(normalized[test] - covered_faults)
            adjusted = new_count / (duration**cost_exponent)
            key = (adjusted, float(new_count), -duration)
            if best_key is None or key > best_key:
                best_key = key
                best_test = test

        if best_test is None:
            break

        remaining_tests.remove(best_test)
        order.append(best_test)
        covered_faults.update(normalized[best_test])
        cumulative_time += costs[best_test]

    return tuple(order)


def shortest_duration_order(
    test_to_faults: Mapping[TestId, Iterable[FaultId]],
    durations: Mapping[TestId, float],
) -> tuple[TestId, ...]:
    """Sort tests by duration, then by id."""

    costs = normalize_durations(durations, test_to_faults, context="durations")
    return tuple(sorted(test_to_faults, key=lambda test: (costs[test], str(test))))


def _reverse_sort_key(value: TestId) -> str:
    return "".join(chr(255 - ord(ch)) for ch in str(value))


def _normalize_matrix(test_to_faults: Mapping[TestId, Iterable[FaultId]]) -> dict[TestId, set[FaultId]]:
    return {test: set(faults) for test, faults in test_to_faults.items()}
