"""Run ShapTCP and core matrix baselines on a binary incidence matrix."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from shaptcp import (
    additional_coverage_order,
    apfd,
    apfdc,
    cost_aware_additional_coverage_order,
    fault_recall_at_k,
    load_binary_incidence_matrix,
    rare_fault_recall_at_k,
    redundancy_at_k,
    shaptcp_order,
    shortest_duration_order,
    static_shapley_order,
    total_coverage_order,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("matrix", type=Path, help="Row-wise binary matrix file.")
    parser.add_argument("--durations", type=Path, help="Optional CSV with columns test_id,duration.")
    parser.add_argument("--k", type=int, default=10, help="Prefix length for recall/redundancy metrics.")
    parser.add_argument("--budget-count", type=int, help="Optional top-k execution budget.")
    parser.add_argument("--time-budget", type=float, help="Optional time budget for cost-aware methods.")
    args = parser.parse_args()

    dataset = load_binary_incidence_matrix(args.matrix)
    durations = _load_durations(args.durations) if args.durations else {}

    orders = {
        "total": total_coverage_order(dataset.test_to_faults),
        "additional": additional_coverage_order(dataset.test_to_faults, budget_count=args.budget_count),
        "static_shapley": _clip(static_shapley_order(dataset.test_to_faults), args.budget_count),
        "shaptcp": shaptcp_order(
            dataset.test_to_faults,
            budget_count=args.budget_count,
            durations=durations,
            time_budget=args.time_budget,
        ).order,
    }

    if durations:
        orders["shortest"] = shortest_duration_order(dataset.test_to_faults, durations)
        orders["cost_additional"] = cost_aware_additional_coverage_order(
            dataset.test_to_faults,
            durations,
            budget_count=args.budget_count,
            time_budget=args.time_budget,
        )
        orders["cost_shaptcp"] = shaptcp_order(
            dataset.test_to_faults,
            budget_count=args.budget_count,
            durations=durations,
            time_budget=args.time_budget,
            cost_exponent=1.0,
        ).order

    print("method,selected,apfd,apfdc,recall_at_k,rare_recall_at_k,redundancy_at_k")
    for name, order in orders.items():
        apfdc_value = apfdc(order, dataset.test_to_faults, durations) if durations else float("nan")
        print(
            ",".join(
                [
                    name,
                    str(len(order)),
                    _fmt(apfd(order, dataset.test_to_faults)),
                    _fmt(apfdc_value),
                    _fmt(fault_recall_at_k(order, dataset.test_to_faults, k=args.k)),
                    _fmt(rare_fault_recall_at_k(order, dataset.test_to_faults, k=args.k)),
                    _fmt(redundancy_at_k(order, dataset.test_to_faults, k=args.k)),
                ]
            )
        )


def _load_durations(path: Path) -> dict[str, float]:
    durations: dict[str, float] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = {"test_id", "duration"}
        if set(reader.fieldnames or []) < required:
            raise ValueError(f"{path} must contain columns: test_id,duration")
        for row in reader:
            durations[row["test_id"]] = float(row["duration"])
    return durations


def _fmt(value: float) -> str:
    if value != value:
        return "nan"
    return f"{value:.6f}"


def _clip(order: tuple[str, ...], budget_count: int | None) -> tuple[str, ...]:
    if budget_count is None:
        return order
    return order[:budget_count]


if __name__ == "__main__":
    main()
