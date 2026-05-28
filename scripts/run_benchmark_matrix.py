"""Run ShapTCP and first-stage baselines on a confirmed matrix file."""

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
    random_order,
    rare_fault_recall_at_k,
    redundancy_at_k,
    shaptcp_order,
    shortest_duration_order,
    static_shapley_order,
    total_coverage_order,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("matrix", type=Path)
    parser.add_argument("--benchmark", default="manual", help="Benchmark id for output metadata.")
    parser.add_argument("--subject", default="unknown", help="Subject/version id for output metadata.")
    parser.add_argument("--semantics", default="unverified", help="Column semantics: fault/mutant/statement/etc.")
    parser.add_argument("--run-id", default="manual-run", help="Traceable run id for output metadata.")
    parser.add_argument("--evidence-level", default="pipeline_validation")
    parser.add_argument("--claim-scope", default="adapter_smoke")
    parser.add_argument("--source-status", default="unknown")
    parser.add_argument("--matrix-status", default="unknown")
    parser.add_argument("--result-status", default="local_smoke_only")
    parser.add_argument("--ground-truth-level", default="unverified")
    parser.add_argument("--duration-source", default="not_available")
    parser.add_argument("--budget-policy", default="count")
    parser.add_argument("--allow-unverified", action="store_true", help="Allow --semantics unverified.")
    parser.add_argument("--durations", type=Path, help="Optional CSV with test_id,duration.")
    parser.add_argument("--test-ids", type=Path, help="Optional newline file of row/test ids.")
    parser.add_argument("--fault-ids", type=Path, help="Optional newline file of column/entity ids.")
    parser.add_argument("--k", type=int, default=20)
    parser.add_argument("--budget-count", type=int)
    parser.add_argument("--random-seeds", type=int, default=30)
    args = parser.parse_args()
    if args.semantics == "unverified" and not args.allow_unverified:
        raise SystemExit("Refusing to run with --semantics unverified. Pass a verified value or --allow-unverified.")

    test_ids = load_id_file(args.test_ids) if args.test_ids else load_optional_sidecar(args.matrix, ".tests")
    fault_ids = load_id_file(args.fault_ids) if args.fault_ids else load_optional_sidecar(args.matrix, ".entities")
    dataset = load_binary_incidence_matrix(args.matrix, test_ids=test_ids, fault_ids=fault_ids)
    durations = load_durations(args.durations) if args.durations else {}
    orders = build_orders(dataset.test_to_faults, durations, args.budget_count, args.random_seeds)

    print(
        "run_id,benchmark,subject,semantics,evidence_level,claim_scope,"
        "source_status,matrix_status,result_status,ground_truth_level,duration_source,"
        "k,budget_policy,budget_count,random_seeds,method,selected,"
        "apfd,apfdc,recall_at_k,rare_recall_at_k,redundancy_at_k"
    )
    for name, order in orders.items():
        full_order = len(order) == len(dataset.test_ids)
        apfd_value = apfd(order, dataset.test_to_faults) if full_order else float("nan")
        apfdc_value = apfdc(order, dataset.test_to_faults, durations) if durations and full_order else float("nan")
        print(
            ",".join(
                [
                    args.run_id,
                    args.benchmark,
                    args.subject,
                    args.semantics,
                    args.evidence_level,
                    args.claim_scope,
                    args.source_status,
                    args.matrix_status,
                    args.result_status,
                    args.ground_truth_level,
                    args.duration_source,
                    str(args.k),
                    args.budget_policy,
                    "" if args.budget_count is None else str(args.budget_count),
                    str(args.random_seeds),
                    name,
                    str(len(order)),
                    fmt(apfd_value),
                    fmt(apfdc_value),
                    fmt(fault_recall_at_k(order, dataset.test_to_faults, k=args.k)),
                    fmt(rare_fault_recall_at_k(order, dataset.test_to_faults, k=args.k)),
                    fmt(redundancy_at_k(order, dataset.test_to_faults, k=args.k)),
                ]
            )
        )


def build_orders(test_to_faults, durations, budget_count: int | None, random_seeds: int):
    orders = {
        "total": clip(total_coverage_order(test_to_faults), budget_count),
        "additional": additional_coverage_order(test_to_faults, budget_count=budget_count),
        "static_shapley": clip(static_shapley_order(test_to_faults), budget_count),
        "shaptcp": shaptcp_order(test_to_faults, budget_count=budget_count).order,
    }
    for seed in range(random_seeds):
        orders[f"random_{seed}"] = clip(random_order(test_to_faults, seed=seed), budget_count)
    if durations:
        orders["shortest"] = clip(shortest_duration_order(test_to_faults, durations), budget_count)
        orders["cost_additional"] = cost_aware_additional_coverage_order(
            test_to_faults,
            durations,
            budget_count=budget_count,
        )
        orders["cost_shaptcp"] = shaptcp_order(
            test_to_faults,
            durations=durations,
            budget_count=budget_count,
            cost_exponent=1.0,
        ).order
    return orders


def load_durations(path: Path) -> dict[str, float]:
    durations: dict[str, float] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = {"test_id", "duration"}
        if set(reader.fieldnames or []) < required:
            raise ValueError(f"{path} must contain columns: test_id,duration")
        for row in reader:
            durations[row["test_id"]] = float(row["duration"])
    return durations


def load_optional_sidecar(matrix_path: Path, suffix: str) -> tuple[str, ...] | None:
    sidecar = matrix_path.with_suffix(matrix_path.suffix + suffix)
    if not sidecar.exists():
        return None
    return load_id_file(sidecar)


def load_id_file(path: Path) -> tuple[str, ...]:
    return tuple(line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def clip(order: tuple[str, ...], budget_count: int | None) -> tuple[str, ...]:
    if budget_count is None:
        return order
    return order[:budget_count]


def fmt(value: float) -> str:
    if value != value:
        return "nan"
    return f"{value:.6f}"


if __name__ == "__main__":
    main()
