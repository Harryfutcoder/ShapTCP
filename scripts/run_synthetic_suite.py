"""Run a lightweight multi-seed synthetic comparison.

This is a sanity experiment, not paper evidence. It compares ShapTCP against
classic strong matrix baselines on generated redundancy/scarcity cases.
"""

from __future__ import annotations

import argparse
import random
from collections import defaultdict
from statistics import mean

from shaptcp import (
    additional_coverage_order,
    apfd,
    apfdc,
    cost_aware_additional_coverage_order,
    fault_recall_at_k,
    random_order,
    rare_fault_recall_at_k,
    redundancy_at_k,
    shaptcp_order,
    static_shapley_order,
    total_coverage_order,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seeds", type=int, default=50, help="Number of generated cases.")
    parser.add_argument("--tests", type=int, default=100, help="Tests per generated case.")
    parser.add_argument("--faults", type=int, default=200, help="Fault/entity ids per generated case.")
    parser.add_argument("--k", type=int, default=20, help="Prefix length for early metrics.")
    args = parser.parse_args()

    results: dict[str, list[dict[str, float]]] = defaultdict(list)
    wins_vs_additional: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for seed in range(args.seeds):
        matrix, durations = generate_case(seed, n_tests=args.tests, n_faults=args.faults)
        orders = {
            "random": random_order(matrix, seed=seed),
            "total": total_coverage_order(matrix),
            "additional": additional_coverage_order(matrix),
            "static_shapley": static_shapley_order(matrix),
            "shaptcp": shaptcp_order(matrix).order,
            "cost_additional": cost_aware_additional_coverage_order(matrix, durations),
            "cost_shaptcp": shaptcp_order(matrix, durations=durations, cost_exponent=1.0).order,
        }

        metrics = {name: score_order(order, matrix, durations, args.k) for name, order in orders.items()}
        baseline = metrics["additional"]
        for name, values in metrics.items():
            results[name].append(values)
            for metric, value in values.items():
                if value > baseline[metric]:
                    wins_vs_additional[name][metric] += 1

    print(f"synthetic_cases={args.seeds}, tests={args.tests}, faults={args.faults}, k={args.k}")
    print(
        "method,apfd,apfdc,recall_at_k,rare_recall_at_k,redundancy_at_k,"
        "wins_apfd,wins_apfdc,wins_rare,wins_redundancy_lower"
    )
    for name in [
        "random",
        "total",
        "additional",
        "static_shapley",
        "shaptcp",
        "cost_additional",
        "cost_shaptcp",
    ]:
        rows = results[name]
        redundancy_wins = sum(
            1
            for index, row in enumerate(rows)
            if row["redundancy_at_k"] < results["additional"][index]["redundancy_at_k"]
        )
        print(
            ",".join(
                [
                    name,
                    fmt(mean(row["apfd"] for row in rows)),
                    fmt(mean(row["apfdc"] for row in rows)),
                    fmt(mean(row["recall_at_k"] for row in rows)),
                    fmt(mean(row["rare_recall_at_k"] for row in rows)),
                    fmt(mean(row["redundancy_at_k"] for row in rows)),
                    str(wins_vs_additional[name]["apfd"]),
                    str(wins_vs_additional[name]["apfdc"]),
                    str(wins_vs_additional[name]["rare_recall_at_k"]),
                    str(redundancy_wins),
                ]
            )
        )


def generate_case(seed: int, *, n_tests: int, n_faults: int) -> tuple[dict[str, set[str]], dict[str, float]]:
    rng = random.Random(seed)
    n_common = max(1, int(n_faults * 0.65))
    common = [f"c{i}" for i in range(n_common)]
    rare = [f"r{i}" for i in range(n_faults - n_common)]
    matrix: dict[str, set[str]] = {}
    durations: dict[str, float] = {}

    for test_index in range(n_tests):
        test = f"t{test_index}"
        roll = rng.random()
        faults: set[str] = set()

        if roll < 0.35:
            faults.update(rng.sample(common, rng.randint(8, min(18, len(common)))))
            durations[test] = rng.uniform(8.0, 15.0)
        elif roll < 0.80:
            faults.update(rng.sample(common, rng.randint(3, min(10, len(common)))))
            if rare:
                faults.update(rng.sample(rare, rng.randint(1, min(3, len(rare)))))
            durations[test] = rng.uniform(2.0, 7.0)
        else:
            if rare:
                faults.update(rng.sample(rare, rng.randint(1, min(5, len(rare)))))
            faults.update(rng.sample(common, rng.randint(0, min(2, len(common)))))
            durations[test] = rng.uniform(0.5, 3.0)

        matrix[test] = faults

    # Ensure rare entities exist and stay scarce instead of becoming uncovered.
    for fault in rare:
        carriers = rng.sample(list(matrix), rng.randint(1, min(3, n_tests)))
        for test in carriers:
            matrix[test].add(fault)

    return matrix, durations


def score_order(
    order: tuple[str, ...],
    matrix: dict[str, set[str]],
    durations: dict[str, float],
    k: int,
) -> dict[str, float]:
    return {
        "apfd": apfd(order, matrix),
        "apfdc": apfdc(order, matrix, durations),
        "recall_at_k": fault_recall_at_k(order, matrix, k=k),
        "rare_recall_at_k": rare_fault_recall_at_k(order, matrix, k=k, max_degree=3),
        "redundancy_at_k": redundancy_at_k(order, matrix, k=k),
    }


def fmt(value: float) -> str:
    return f"{value:.6f}"


if __name__ == "__main__":
    main()
