"""ShapTCP research prototype."""

from .cooperative import (
    OrderResult,
    StepTrace,
    additional_coverage_order,
    random_order,
    shaptcp_order,
    static_shapley_scores,
    total_coverage_order,
)
from .fault_clustering import apply_fault_clusters, cluster_faults_by_cofailure
from .metrics import (
    apfd,
    apfdc,
    fault_recall_at_k,
    rare_fault_recall_at_k,
    redundancy_at_k,
    time_to_first_fault,
)

__all__ = [
    "OrderResult",
    "StepTrace",
    "additional_coverage_order",
    "apfd",
    "apfdc",
    "apply_fault_clusters",
    "cluster_faults_by_cofailure",
    "fault_recall_at_k",
    "random_order",
    "rare_fault_recall_at_k",
    "redundancy_at_k",
    "shaptcp_order",
    "static_shapley_scores",
    "time_to_first_fault",
    "total_coverage_order",
]
