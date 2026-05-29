"""Cooperative-game prioritization algorithms.

The main algorithm is ShapTCP: exact Shapley-weighted residual coverage.
It is intentionally framed as a matrix-based method over fault clusters,
mutants, bug ids, or other root-cause proxies.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence

from .baselines import additional_coverage_order, random_order, total_coverage_order
from .durations import normalize_durations

from .types import FaultId, TestId


@dataclass(frozen=True)
class StepTrace:
    """Diagnostics for one selected test."""

    test: TestId
    raw_score: float
    adjusted_score: float
    newly_covered_faults: frozenset[FaultId]
    cumulative_time: float
    covered_fault_count: int
    residual_fault_count: int


@dataclass(frozen=True)
class OrderResult:
    """Prioritization result with useful traces."""

    order: tuple[TestId, ...]
    static_scores: Mapping[TestId, float]
    traces: tuple[StepTrace, ...]


def normalize_matrix(test_to_faults: Mapping[TestId, Iterable[FaultId]]) -> dict[TestId, set[FaultId]]:
    """Normalize any iterable-valued incidence matrix into sets."""

    return {test: set(faults) for test, faults in test_to_faults.items()}


def all_faults(test_to_faults: Mapping[TestId, Iterable[FaultId]]) -> set[FaultId]:
    """Return the union of all faults in the matrix."""

    normalized = normalize_matrix(test_to_faults)
    return set().union(*normalized.values()) if normalized else set()


def invert_matrix(test_to_faults: Mapping[TestId, Iterable[FaultId]]) -> dict[FaultId, set[TestId]]:
    """Return fault -> tests incidence from test -> faults incidence."""

    fault_to_tests: dict[FaultId, set[TestId]] = {}
    for test, faults in test_to_faults.items():
        for fault in faults:
            fault_to_tests.setdefault(fault, set()).add(test)
    return fault_to_tests


def fault_degrees(test_to_faults: Mapping[TestId, Iterable[FaultId]]) -> dict[FaultId, int]:
    """Count how many tests cover each fault."""

    return {fault: len(tests) for fault, tests in invert_matrix(test_to_faults).items()}


def static_shapley_scores(
    test_to_faults: Mapping[TestId, Iterable[FaultId]],
    *,
    fault_weights: Mapping[FaultId, float] | None = None,
) -> dict[TestId, float]:
    """Compute exact Shapley scores for a weighted coverage game."""

    normalized = normalize_matrix(test_to_faults)
    degrees = fault_degrees(normalized)
    weights = _normalize_fault_weights(fault_weights)
    scores: dict[TestId, float] = {}

    for test, faults in normalized.items():
        score = 0.0
        for fault in faults:
            degree = degrees.get(fault, 0)
            if degree:
                score += float(weights.get(fault, 1.0)) / degree
        scores[test] = score
    return scores


def static_shapley_order(
    test_to_faults: Mapping[TestId, Iterable[FaultId]],
    *,
    fault_weights: Mapping[FaultId, float] | None = None,
) -> tuple[TestId, ...]:
    """Order tests by static Shapley score without residual updates.

    This is an ablation baseline. It isolates the attribution effect from the
    residual/additional-coverage scheduling step used by ShapTCP.
    """

    scores = static_shapley_scores(test_to_faults, fault_weights=fault_weights)
    return tuple(sorted(scores, key=lambda test: (-scores[test], str(test))))


def shaptcp_order(
    test_to_faults: Mapping[TestId, Iterable[FaultId]],
    *,
    budget_count: int | None = None,
    durations: Mapping[TestId, float] | None = None,
    time_budget: float | None = None,
    fault_weights: Mapping[FaultId, float] | None = None,
    cost_exponent: float = 0.0,
    exploration_bonus: Mapping[TestId, float] | None = None,
    lexicographic_unique: bool = False,
) -> OrderResult:
    """Order tests by Shapley-weighted residual coverage.

    The residual score is:

        sum_{f in F_i and not-yet-covered} weight_f / |T_f|

    `cost_exponent` supports cost-aware variants:

    - 0.0: pure ShapTCP
    - 0.5: mild duration penalty
    - 1.0: score per second

    `lexicographic_unique` prioritizes the count of residual faults whose
    original degree is one before the weighted score. It is an ablation/policy
    variant, not an APFD guarantee.
    """

    if budget_count is None and time_budget is None:
        budget_count = len(test_to_faults)
    if budget_count is not None and budget_count < 0:
        raise ValueError("budget_count must be non-negative")
    if time_budget is not None and time_budget < 0:
        raise ValueError("time_budget must be non-negative")
    if cost_exponent < 0:
        raise ValueError("cost_exponent must be non-negative")

    normalized = normalize_matrix(test_to_faults)
    uses_durations = bool(durations) or time_budget is not None or cost_exponent > 0
    if uses_durations:
        costs = normalize_durations(durations or {}, normalized, context="durations")
    else:
        costs = {test: 1.0 for test in normalized}
    duration_affects_priority = time_budget is not None or cost_exponent > 0
    weights = _normalize_fault_weights(fault_weights)
    bonuses = exploration_bonus or {}
    degrees = fault_degrees(normalized)
    static_scores = static_shapley_scores(normalized, fault_weights=weights)

    remaining_tests = set(normalized)
    covered_faults: set[FaultId] = set()
    total_faults = all_faults(normalized)
    order: list[TestId] = []
    traces: list[StepTrace] = []
    cumulative_time = 0.0

    while remaining_tests:
        if budget_count is not None and len(order) >= budget_count:
            break

        best_test: TestId | None = None
        best_key: tuple[float, float, float] | None = None
        best_raw = 0.0
        best_adjusted = 0.0
        best_new: set[FaultId] = set()

        for test in sorted(remaining_tests, key=str):
            duration = costs[test]
            if time_budget is not None and cumulative_time + duration > time_budget:
                continue

            newly_covered = normalized[test] - covered_faults
            raw_score = sum(float(weights.get(fault, 1.0)) / degrees[fault] for fault in newly_covered)
            raw_score += float(bonuses.get(test, 0.0))
            adjusted_score = raw_score / (duration**cost_exponent)
            unique_count = sum(1 for fault in newly_covered if degrees[fault] == 1)
            duration_tie_break = -duration if duration_affects_priority else 0.0

            if lexicographic_unique:
                key = (float(unique_count), adjusted_score, duration_tie_break)
            else:
                key = (adjusted_score, duration_tie_break, 0.0)

            if best_key is None or key > best_key:
                best_test = test
                best_key = key
                best_raw = raw_score
                best_adjusted = adjusted_score
                best_new = newly_covered

        if best_test is None:
            break

        remaining_tests.remove(best_test)
        order.append(best_test)
        covered_faults.update(best_new)
        cumulative_time += costs[best_test]
        traces.append(
            StepTrace(
                test=best_test,
                raw_score=best_raw,
                adjusted_score=best_adjusted,
                newly_covered_faults=frozenset(best_new),
                cumulative_time=cumulative_time,
                covered_fault_count=len(covered_faults),
                residual_fault_count=len(total_faults - covered_faults),
            )
        )

    return OrderResult(order=tuple(order), static_scores=static_scores, traces=tuple(traces))


def _reverse_sort_key(value: TestId) -> str:
    """Make deterministic max() tie-breaking prefer lexical ascending ids."""

    return "".join(chr(255 - ord(ch)) for ch in str(value))


def _normalize_fault_weights(fault_weights: Mapping[FaultId, float] | None) -> dict[FaultId, float]:
    weights: dict[FaultId, float] = {}
    for fault, weight in (fault_weights or {}).items():
        value = float(weight)
        if value < 0:
            raise ValueError(f"fault weight for {fault!r} must be non-negative")
        weights[fault] = value
    return weights
