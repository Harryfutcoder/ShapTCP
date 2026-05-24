"""Lightweight scaling benchmark for the current ShapTCP implementation.

This script uses synthetic sparse test-fault matrices. It is not a scientific
evaluation; it only estimates local runtime for algorithm sanity.
"""

from __future__ import annotations

import argparse
import random
import time

from shaptcp import shaptcp_order, static_shapley_scores


def make_matrix(
    *,
    tests: int,
    faults: int,
    faults_per_test: int,
    seed: int,
) -> dict[str, set[str]]:
    rng = random.Random(seed)
    fault_ids = [f"f{idx}" for idx in range(faults)]
    matrix: dict[str, set[str]] = {}
    sample_size = min(faults_per_test, faults)
    for test_idx in range(tests):
        matrix[f"t{test_idx}"] = set(rng.sample(fault_ids, sample_size))
    return matrix


def run_case(*, tests: int, faults: int, faults_per_test: int, budget: int, seed: int) -> dict[str, float]:
    matrix = make_matrix(tests=tests, faults=faults, faults_per_test=faults_per_test, seed=seed)

    started = time.perf_counter()
    static_shapley_scores(matrix)
    static_s = time.perf_counter() - started

    started = time.perf_counter()
    result = shaptcp_order(matrix, budget_count=min(budget, tests))
    order_s = time.perf_counter() - started

    return {
        "tests": float(tests),
        "faults": float(faults),
        "faults_per_test": float(faults_per_test),
        "budget": float(min(budget, tests)),
        "static_s": static_s,
        "order_s": order_s,
        "selected": float(len(result.order)),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--budget", type=int, default=100)
    parser.add_argument(
        "--cases",
        nargs="*",
        default=["100,200,10", "500,1000,20", "1000,2000,20"],
        help="Cases formatted as tests,faults,faults_per_test.",
    )
    args = parser.parse_args()

    print("tests,faults,faults_per_test,budget,static_s,order_s,selected")
    for case in args.cases:
        tests, faults, faults_per_test = (int(part) for part in case.split(","))
        row = run_case(
            tests=tests,
            faults=faults,
            faults_per_test=faults_per_test,
            budget=args.budget,
            seed=args.seed,
        )
        print(
            f"{int(row['tests'])},{int(row['faults'])},{int(row['faults_per_test'])},"
            f"{int(row['budget'])},{row['static_s']:.6f},{row['order_s']:.6f},"
            f"{int(row['selected'])}"
        )


if __name__ == "__main__":
    main()
