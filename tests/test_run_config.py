import json
from pathlib import Path
import unittest

from shaptcp.run_config import validate_run_config


REPO_ROOT = Path(__file__).resolve().parents[1]


class RunConfigValidationTests(unittest.TestCase):
    def test_rejects_public_unverified_semantics(self):
        config = valid_config()
        config["matrix"]["column_semantics"] = "unverified"

        errors = validate_run_config(config)

        self.assertIn("matrix.column_semantics must be verified, not unverified", errors)

    def test_requires_additional_when_shaptcp_is_present(self):
        config = valid_config()
        config["methods"] = ["random", "total", "static_shapley", "shaptcp"]

        errors = validate_run_config(config)

        self.assertIn("shaptcp runs must include additional as the closest baseline", errors)

    def test_public_random_needs_enough_seeds(self):
        config = valid_config()
        config["evidence_level"] = "public_benchmark"
        config["result_status"] = "reportable"
        config["protocol"]["random_seeds"] = 3

        errors = validate_run_config(config)

        self.assertIn("public benchmark random baseline must use at least 30 seeds", errors)

    def test_valid_example_passes(self):
        path = REPO_ROOT / "benchmarks/examples/defects4j_metadata_smoke.run_config.json"
        config = json.loads(path.read_text(encoding="utf-8"))

        errors = validate_run_config(config, repo_root=REPO_ROOT)

        self.assertEqual([], errors)


def valid_config():
    return {
        "schema_version": 1,
        "id": "fast-smoke",
        "evidence_level": "pipeline_validation",
        "claim_scope": "adapter_smoke",
        "source_status": "source-audited",
        "matrix_status": "verified",
        "result_status": "local_smoke_only",
        "source": {"benchmark": "FAST"},
        "subject": {"project": "toy"},
        "matrix": {
            "path": "data/processed/toy.txt",
            "row_semantics": "test_method",
            "column_semantics": "fault",
            "value_semantics": "detects",
            "ground_truth_level": "true_fault",
            "empty_policy": "kept",
            "duplicate_policy": "kept",
            "verified_by": "benchmarks/source_notes/fast.md",
        },
        "protocol": {"split": "none", "random_seeds": 30},
        "methods": ["random", "total", "additional", "static_shapley", "shaptcp"],
        "metrics": ["apfd"],
        "baseline_compatibility": {
            "candidate_tests": "aligned",
            "observable_information": "aligned",
            "split": "aligned",
            "budget": "aligned",
            "metric_definition": "aligned",
            "duration_source": "not_applicable",
        },
        "outputs": {
            "run_id": "fast-smoke",
            "results_csv": "outputs/fast-smoke/results.csv",
        },
        "claim_boundary": {"allowed": [], "disallowed": []},
    }


if __name__ == "__main__":
    unittest.main()
