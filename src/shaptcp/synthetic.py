"""Small synthetic scenarios for algorithm sanity checks."""

from __future__ import annotations

from dataclasses import dataclass

from .types import FaultId, TestId


@dataclass(frozen=True)
class Scenario:
    name: str
    test_to_faults: dict[TestId, set[FaultId]]
    durations: dict[TestId, float]
    description: str


def redundancy_scenario() -> Scenario:
    """Two redundant tests and one rare-fault test."""

    return Scenario(
        name="redundancy",
        test_to_faults={
            "A": {"f1", "f2"},
            "B": {"f1", "f2"},
            "C": {"f3"},
        },
        durations={"A": 1.0, "B": 1.0, "C": 1.0},
        description="A/B are redundant; C covers a rare fault.",
    )


def verbose_fault_explosion_scenario() -> Scenario:
    """One root cause emits multiple raw signatures before clustering."""

    return Scenario(
        name="verbose_fault_explosion",
        test_to_faults={
            "T1": {"sig_a", "sig_b", "sig_c"},
            "T2": {"sig_a", "sig_b", "sig_c"},
            "T3": {"sig_d"},
        },
        durations={"T1": 2.0, "T2": 2.0, "T3": 1.0},
        description="sig_a/sig_b/sig_c represent one verbose root cause.",
    )


def cost_tradeoff_scenario() -> Scenario:
    """A long broad test competes with short focused tests."""

    return Scenario(
        name="cost_tradeoff",
        test_to_faults={
            "slow_broad": {"f1", "f2", "f3"},
            "fast_rare": {"f4"},
            "fast_common": {"f1"},
            "medium": {"f2", "f5"},
        },
        durations={"slow_broad": 10.0, "fast_rare": 1.0, "fast_common": 1.0, "medium": 3.0},
        description="Cost-aware scoring should change the first choice.",
    )


def all_scenarios() -> list[Scenario]:
    return [
        redundancy_scenario(),
        verbose_fault_explosion_scenario(),
        cost_tradeoff_scenario(),
    ]
