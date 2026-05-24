"""Run ShapTCP on built-in synthetic scenarios."""

from __future__ import annotations

from shaptcp import (
    additional_coverage_order,
    apfd,
    apfdc,
    fault_recall_at_k,
    rare_fault_recall_at_k,
    redundancy_at_k,
    shaptcp_order,
)
from shaptcp.synthetic import all_scenarios


def main() -> None:
    for scenario in all_scenarios():
        print(f"\n== {scenario.name} ==")
        print(scenario.description)

        add_order = additional_coverage_order(scenario.test_to_faults)
        shap_order = shaptcp_order(scenario.test_to_faults).order
        unique_order = shaptcp_order(scenario.test_to_faults, lexicographic_unique=True).order
        cost_order = shaptcp_order(
            scenario.test_to_faults,
            durations=scenario.durations,
            cost_exponent=1.0,
        ).order

        for name, order in [
            ("additional", add_order),
            ("shaptcp", shap_order),
            ("unique_shaptcp", unique_order),
            ("cost_shaptcp", cost_order),
        ]:
            print(
                f"{name:14s} order={order} "
                f"APFD={apfd(order, scenario.test_to_faults):.3f} "
                f"APFDc={apfdc(order, scenario.test_to_faults, scenario.durations):.3f} "
                f"Recall@2={fault_recall_at_k(order, scenario.test_to_faults, k=2):.3f} "
                f"Rare@2={rare_fault_recall_at_k(order, scenario.test_to_faults, k=2):.3f} "
                f"Red@2={redundancy_at_k(order, scenario.test_to_faults, k=2):.3f}"
            )


if __name__ == "__main__":
    main()
