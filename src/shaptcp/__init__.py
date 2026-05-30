"""ShapTCP research prototype."""

from .baselines import cost_aware_additional_coverage_order, shortest_duration_order
from .cooperative import (
    OrderResult,
    StepTrace,
    additional_coverage_order,
    guarded_shaptcp_order,
    random_order,
    shaptcp_order,
    static_shapley_order,
    static_shapley_scores,
    total_coverage_order,
)
from .fault_clustering import apply_fault_clusters, cluster_faults_by_cofailure
from .io import MatrixDataset, load_binary_incidence_matrix
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
    "MatrixDataset",
    "StepTrace",
    "additional_coverage_order",
    "apfd",
    "apfdc",
    "apply_fault_clusters",
    "cluster_faults_by_cofailure",
    "cost_aware_additional_coverage_order",
    "fault_recall_at_k",
    "guarded_shaptcp_order",
    "load_binary_incidence_matrix",
    "random_order",
    "rare_fault_recall_at_k",
    "redundancy_at_k",
    "shaptcp_order",
    "shortest_duration_order",
    "static_shapley_order",
    "static_shapley_scores",
    "time_to_first_fault",
    "total_coverage_order",
]
