"""Fault clustering utilities for CI failure-signature deduplication."""

from __future__ import annotations

from typing import Iterable, Mapping

from .types import FaultId, TestId


def cluster_faults_by_cofailure(
    fault_to_tests: Mapping[FaultId, Iterable[TestId]],
    *,
    threshold: float = 0.9,
) -> dict[FaultId, FaultId]:
    """Cluster fault signatures by Jaccard similarity of failing-test sets.

    This is a deterministic root-cause proxy baseline. It is not a replacement
    for benchmark-provided bug ids, mutant ids, or issue links when those exist.
    """

    if not 0 <= threshold <= 1:
        raise ValueError("threshold must be in [0, 1]")

    items = [(fault, set(tests)) for fault, tests in fault_to_tests.items()]
    parent = {fault: fault for fault, _ in items}

    def find(fault: FaultId) -> FaultId:
        while parent[fault] != fault:
            parent[fault] = parent[parent[fault]]
            fault = parent[fault]
        return fault

    def union(left: FaultId, right: FaultId) -> None:
        root_left = find(left)
        root_right = find(right)
        if root_left == root_right:
            return
        parent[max(root_left, root_right, key=str)] = min(root_left, root_right, key=str)

    for index, (fault_a, tests_a) in enumerate(items):
        for fault_b, tests_b in items[index + 1 :]:
            denominator = len(tests_a | tests_b)
            similarity = 1.0 if denominator == 0 else len(tests_a & tests_b) / denominator
            if similarity >= threshold:
                union(fault_a, fault_b)

    return {fault: find(fault) for fault, _ in items}


def apply_fault_clusters(
    test_to_faults: Mapping[TestId, Iterable[FaultId]],
    fault_to_cluster: Mapping[FaultId, FaultId],
) -> dict[TestId, set[FaultId]]:
    """Replace raw fault ids with clustered/root-cause proxy ids."""

    return {
        test: {fault_to_cluster.get(fault, fault) for fault in faults}
        for test, faults in test_to_faults.items()
    }
