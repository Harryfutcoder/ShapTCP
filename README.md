# ShapTCP

ShapTCP is a research prototype for **scarcity-aware test case prioritization**
using exact Shapley attribution over a test-to-fault incidence matrix.

The current implementation is intentionally conservative:

- It does **not** claim an APFD approximation guarantee.
- It treats the first algorithm as **Shapley-weighted residual coverage**, not as
  a stronger dynamic-degree theorem.
- It separates matrix-based experiments from future learned-value or CI-log
  adapters.

## Current Algorithm

For a test set `N`, fault clusters `F`, and test-fault incidence matrix
`F_i`, ShapTCP computes exact coverage-game Shapley scores:

```text
phi_i = sum_{f in F_i} weight_f / |T_f|
T_f = {i : f in F_i}
```

Prioritization then greedily selects the test with the largest residual
Shapley-weighted coverage:

```text
score_i(S) = sum_{f in F_i \\ covered(S)} weight_f / |T_f|
```

This is best understood as **Shapley-weighted additional coverage**. It rewards
tests that cover scarce faults and reduces redundant coverage pressure.

## Repository Layout

```text
src/shaptcp/
  baselines.py        # matrix baselines for first-stage experiments
  cooperative.py      # ShapTCP ordering and simple baselines
  metrics.py          # APFD/APFDc/recall/redundancy metrics
  io.py               # lightweight binary incidence matrix loader
  fault_clustering.py # co-failure clustering for failure-signature dedup
  synthetic.py        # small stress scenarios
scripts/
  run_synthetic.py    # sanity benchmark runner
  run_synthetic_suite.py # multi-seed generated sanity comparison
  run_matrix_file.py  # light matrix benchmark runner
  audit_benchmarks.py # source availability audit
  discover_matrices.py # row-wise 0/1 matrix discovery
  run_benchmark_matrix.py # manifest-compatible matrix runner
  build_defects4j_metadata_matrix.py # metadata-only trigger matrix adapter
  build_defects4j_trigger_matrix.py # Defects4J checkout/export adapter
  validate_run_config.py # run-config fairness gate
  preflight_experiment.py # run-config plus optional matrix/file checks
tests/
  test_*.py           # unit tests
benchmarks/
  manifest.json       # benchmark source registry and status fields
  run_config_template.json # per-run metadata template
  examples/           # known-valid run configs
  schemas/            # machine-readable experiment contracts
  source_notes/       # source-specific audit notes
docs/
  roadmap.md          # research and benchmark roadmap
  theory_review.md    # compressed theory audit and claim boundaries
  full_benchmark_pipeline.md # development-machine benchmark pipeline
  experiment_design.md # paper-level RQs, baselines, metrics, environments
  tcp_problem_modeling.md # TCP formalization, metrics, and ShapTCP surrogate
  paper_experiment_checklist.md # paper experiment artifact/run checklist
  testing_se_research_workflow.md # experiment integrity workflow and gates
  benchmark_audit.md  # verified benchmark/resource notes
  sota_baselines.md   # paper-to-code baseline and benchmark map
  experimental_plan.md # staged experiment plan and claim boundaries
```

## Quick Start

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
PYTHONPATH=src python3 scripts/run_synthetic.py
PYTHONPATH=src python3 scripts/run_synthetic_suite.py
PYTHONPATH=src python3 scripts/audit_benchmarks.py
PYTHONPATH=src python3 scripts/preflight_experiment.py \
  benchmarks/examples/defects4j_metadata_smoke.run_config.json --check-files
```

Expected status right now: unit tests pass and synthetic scenarios run locally.

## Research Roadmap

1. Validate Matrix ShapTCP on synthetic stress cases.
2. Confirm a public matrix benchmark, preferably SIR small subjects first, then
   OCP as a coverage-matrix artifact.
3. Add Defects4J adapters after JDK11/Docker setup and after the matrix source is
   fixed.
4. Add TCPFramework adapter after the matrix version is stable.
5. Only then add broader baselines such as RETECS, tp_rl, DeepOrder, TCP-CI,
   and AutoTCP.

See [docs/roadmap.md](docs/roadmap.md) for the detailed plan.
See [docs/theory_review.md](docs/theory_review.md) for the compressed theory
audit and reviewer-facing claim boundaries.
See [docs/full_benchmark_pipeline.md](docs/full_benchmark_pipeline.md) for the
development-machine benchmark integration plan.
See [docs/experiment_design.md](docs/experiment_design.md) for the paper-level
experiment matrix.
See [docs/tcp_problem_modeling.md](docs/tcp_problem_modeling.md) for the TCP
formalization, metric definitions, and ShapTCP surrogate objective.
See [docs/paper_experiment_checklist.md](docs/paper_experiment_checklist.md)
for the exact paper experiment artifact/run checklist.
See [docs/testing_se_research_workflow.md](docs/testing_se_research_workflow.md)
for the benchmark/baseline/data-semantics integrity workflow.
