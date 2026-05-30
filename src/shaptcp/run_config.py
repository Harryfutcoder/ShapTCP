"""Validation helpers for benchmark run configuration files."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping


PUBLIC_EVIDENCE_LEVELS = {"public_benchmark", "paper_evidence"}
ALLOWED_COLUMN_SEMANTICS = {"fault", "mutant", "statement", "branch", "method", "bug", "ci_proxy"}
ALLOWED_ROW_SEMANTICS = {"test_method", "test_class", "test_script", "ci_job", "generated_test"}
ALLOWED_VALUE_SEMANTICS = {
    "covers",
    "kills",
    "detects",
    "triggering_test_detects_bug",
    "fails_with",
    "co_occurs_with",
}
ALLOWED_GROUND_TRUTH_LEVELS = {
    "true_fault",
    "true_bug_metadata",
    "execution_derived_bug",
    "mutant_proxy",
    "coverage_only",
    "ci_proxy",
}
BLOCKING_COMPATIBILITY_VALUES = {"unknown", "unchecked", "different", "unaligned", "future_leakage"}


def validate_run_config(config: Mapping[str, Any], *, repo_root: Path | None = None) -> list[str]:
    """Return blocking validation errors for a ShapTCP run config."""

    errors: list[str] = []
    repo_root = repo_root or Path.cwd()

    required = [
        "schema_version",
        "id",
        "evidence_level",
        "claim_scope",
        "source_status",
        "matrix_status",
        "result_status",
        "source",
        "subject",
        "matrix",
        "protocol",
        "methods",
        "metrics",
        "baseline_compatibility",
        "outputs",
        "claim_boundary",
    ]
    for key in required:
        if key not in config:
            errors.append(f"missing top-level field: {key}")

    if errors:
        return errors

    evidence_level = str(config["evidence_level"])
    source_status = str(config["source_status"])
    matrix_status = str(config["matrix_status"])
    result_status = str(config["result_status"])
    methods = list(config["methods"])
    protocol = config["protocol"]
    matrix = config["matrix"]
    metrics = list(config["metrics"])
    compatibility = config["baseline_compatibility"]
    outputs = config["outputs"]

    matrix_required = [
        "path",
        "row_semantics",
        "column_semantics",
        "value_semantics",
        "ground_truth_level",
        "empty_policy",
        "duplicate_policy",
        "verified_by",
    ]
    for key in matrix_required:
        if key not in matrix:
            errors.append(f"missing matrix field: {key}")

    row_semantics = str(matrix.get("row_semantics", "unverified"))
    if row_semantics == "unverified":
        errors.append("matrix.row_semantics must be verified, not unverified")
    elif row_semantics not in ALLOWED_ROW_SEMANTICS:
        errors.append(f"matrix.row_semantics has unsupported value: {row_semantics}")

    semantics = str(matrix.get("column_semantics", "unverified"))
    if semantics == "unverified":
        errors.append("matrix.column_semantics must be verified, not unverified")
    elif semantics not in ALLOWED_COLUMN_SEMANTICS:
        errors.append(f"matrix.column_semantics has unsupported value: {semantics}")

    value_semantics = str(matrix.get("value_semantics", "unverified"))
    if value_semantics == "unverified":
        errors.append("matrix.value_semantics must be verified, not unverified")
    elif value_semantics not in ALLOWED_VALUE_SEMANTICS:
        errors.append(f"matrix.value_semantics has unsupported value: {value_semantics}")

    ground_truth_level = str(matrix.get("ground_truth_level", "unverified"))
    if ground_truth_level == "unverified":
        errors.append("matrix.ground_truth_level must be verified, not unverified")
    elif ground_truth_level not in ALLOWED_GROUND_TRUTH_LEVELS:
        errors.append(f"matrix.ground_truth_level has unsupported value: {ground_truth_level}")

    if "shaptcp" in methods and "additional" not in methods:
        errors.append("shaptcp runs must include additional as the closest baseline")

    if "guarded_shaptcp" in methods and "additional" not in methods:
        errors.append("guarded_shaptcp runs must include additional as the guard baseline")

    if "static_shapley" not in methods and "shaptcp" in methods:
        errors.append("shaptcp runs should include static_shapley as the attribution ablation")

    if "static_shapley" not in methods and "guarded_shaptcp" in methods:
        errors.append("guarded_shaptcp runs should include static_shapley as the attribution ablation")

    random_seeds = int(protocol.get("random_seeds", 0) or 0)
    if evidence_level in PUBLIC_EVIDENCE_LEVELS and "random" in methods and random_seeds < 30:
        errors.append("public benchmark random baseline must use at least 30 seeds")

    if evidence_level in PUBLIC_EVIDENCE_LEVELS:
        if source_status in {"unknown", "source-needed", "access-needed"}:
            errors.append(f"public benchmark source_status is not ready: {source_status}")
        if matrix_status != "verified":
            errors.append(f"public benchmark matrix_status must be verified, got: {matrix_status}")
        if result_status in {"unknown", "no-shaptcp-public-result", "local_smoke_only"}:
            errors.append(f"public benchmark result_status is not reportable: {result_status}")

    compatibility_required = [
        "candidate_tests",
        "observable_information",
        "split",
        "budget",
        "metric_definition",
        "duration_source",
    ]
    for key in compatibility_required:
        value = str(compatibility.get(key, "unknown"))
        if value in BLOCKING_COMPATIBILITY_VALUES:
            errors.append(f"baseline_compatibility.{key} is not aligned: {value}")

    if "apfdc" in metrics and str(compatibility.get("duration_source", "unknown")) in {"not_applicable", "synthetic"}:
        errors.append("APFDc runs require an aligned real duration source")

    if not outputs.get("run_id"):
        errors.append("outputs.run_id must be set")
    if not outputs.get("results_csv"):
        errors.append("outputs.results_csv must be set")

    verified_by = matrix.get("verified_by")
    if not verified_by:
        errors.append("matrix.verified_by must point to a source note")
    elif not (repo_root / str(verified_by)).exists():
        errors.append(f"matrix.verified_by does not exist: {verified_by}")

    split = str(protocol.get("split", ""))
    if split == "temporal" and not protocol.get("leakage_guard"):
        errors.append("temporal protocols must document leakage_guard")

    return errors
