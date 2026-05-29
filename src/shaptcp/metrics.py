"""Evaluation metrics for prioritization orders."""

from __future__ import annotations

from typing import Iterable, Mapping, Sequence

from .cooperative import fault_degrees, normalize_matrix
from .durations import normalize_durations
from .types import FaultId, TestId


def apfd(
    order: Sequence[TestId],
    test_to_faults: Mapping[TestId, Iterable[FaultId]],
    *,
    require_complete: bool = True,
) -> float:
    """Average Percentage of Faults Detected.

    Classic APFD assumes a complete permutation of the candidate test suite.
    Set ``require_complete=False`` only for diagnostic APFD-like calculations;
    public budgeted-prefix experiments should report NAPFD or prefix recall.
    """

    normalized = normalize_matrix(test_to_faults)
    if require_complete:
        _validate_complete_order(order, normalized, metric="APFD")
    faults = set().union(*normalized.values()) if normalized else set()
    n = len(order)
    m = len(faults)
    if n == 0 or m == 0:
        return float("nan")

    first = _first_detection_positions(order, normalized, default=n + 1)
    return 1 - (sum(first[fault] for fault in faults) / (n * m)) + (1 / (2 * n))


def apfdc(
    order: Sequence[TestId],
    test_to_faults: Mapping[TestId, Iterable[FaultId]],
    durations: Mapping[TestId, float],
    *,
    require_complete: bool = True,
) -> float:
    """Cost-cognizant APFD.

    This follows the standard APFDc area formulation. APFDc requires complete,
    strictly positive per-test durations aligned with the candidate suite. Set
    ``require_complete=False`` only for explicitly labeled diagnostics.
    """

    normalized = normalize_matrix(test_to_faults)
    if require_complete:
        _validate_complete_order(order, normalized, metric="APFDc")
    duration_scope = normalized if require_complete else order
    costs = normalize_durations(durations, duration_scope, context="APFDc durations")
    faults = set().union(*normalized.values()) if normalized else set()
    total_cost = sum(costs[test] for test in order)
    m = len(faults)
    if total_cost <= 0 or m == 0 or not order:
        return float("nan")

    first = _first_detection_positions(order, normalized, default=None)
    numerator = 0.0
    for fault in faults:
        pos = first[fault]
        if pos is None:
            continue
        fault_index = pos - 1
        after_and_including = sum(costs[test] for test in order[fault_index:])
        numerator += after_and_including - 0.5 * costs[order[fault_index]]
    return numerator / (m * total_cost)


def fault_recall_at_k(
    order: Sequence[TestId],
    test_to_faults: Mapping[TestId, Iterable[FaultId]],
    *,
    k: int,
) -> float:
    """Fraction of all faults covered by the first k tests."""

    normalized = normalize_matrix(test_to_faults)
    faults = set().union(*normalized.values()) if normalized else set()
    if not faults:
        return float("nan")
    covered = _covered_by_prefix(order[:k], normalized)
    return len(covered) / len(faults)


def rare_fault_recall_at_k(
    order: Sequence[TestId],
    test_to_faults: Mapping[TestId, Iterable[FaultId]],
    *,
    k: int,
    max_degree: int = 1,
) -> float:
    """Recall over rare faults whose coverage degree is <= max_degree."""

    normalized = normalize_matrix(test_to_faults)
    degrees = fault_degrees(normalized)
    rare = {fault for fault, degree in degrees.items() if degree <= max_degree}
    if not rare:
        return float("nan")
    covered = _covered_by_prefix(order[:k], normalized)
    return len(covered & rare) / len(rare)


def redundancy_at_k(
    order: Sequence[TestId],
    test_to_faults: Mapping[TestId, Iterable[FaultId]],
    *,
    k: int,
) -> float:
    """Share of first-k test-fault hits that repeat already covered faults."""

    normalized = normalize_matrix(test_to_faults)
    seen: set[FaultId] = set()
    repeated = 0
    total_hits = 0
    for test in order[:k]:
        for fault in normalized.get(test, set()):
            total_hits += 1
            if fault in seen:
                repeated += 1
        seen.update(normalized.get(test, set()))
    if total_hits == 0:
        return 0.0
    return repeated / total_hits


def time_to_first_fault(
    order: Sequence[TestId],
    test_to_faults: Mapping[TestId, Iterable[FaultId]],
    durations: Mapping[TestId, float] | None = None,
) -> float:
    """Cumulative time until the first detected fault in the order."""

    normalized = normalize_matrix(test_to_faults)
    durations = durations or {}
    elapsed = 0.0
    for test in order:
        elapsed += float(durations.get(test, 1.0))
        if normalized.get(test):
            return elapsed
    return float("inf")


def _covered_by_prefix(order: Sequence[TestId], normalized: Mapping[TestId, set[FaultId]]) -> set[FaultId]:
    covered: set[FaultId] = set()
    for test in order:
        covered.update(normalized.get(test, set()))
    return covered


def _first_detection_positions(
    order: Sequence[TestId],
    normalized: Mapping[TestId, set[FaultId]],
    *,
    default: int | None,
) -> dict[FaultId, int | None]:
    faults = set().union(*normalized.values()) if normalized else set()
    first: dict[FaultId, int | None] = {fault: default for fault in faults}
    for pos, test in enumerate(order, start=1):
        for fault in normalized.get(test, set()):
            if first[fault] == default:
                first[fault] = pos
    return first


def _validate_complete_order(
    order: Sequence[TestId],
    normalized: Mapping[TestId, set[FaultId]],
    *,
    metric: str,
) -> None:
    order_set = set(order)
    expected_set = set(normalized)
    if len(order) != len(order_set):
        raise ValueError(f"{metric} requires a permutation without duplicate tests")
    if order_set != expected_set:
        missing = expected_set - order_set
        extra = order_set - expected_set
        details: list[str] = []
        if missing:
            details.append("missing=" + ",".join(str(test) for test in sorted(missing, key=str)[:5]))
        if extra:
            details.append("extra=" + ",".join(str(test) for test in sorted(extra, key=str)[:5]))
        raise ValueError(f"{metric} requires a complete candidate-suite order ({'; '.join(details)})")
