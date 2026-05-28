# Testing/SE Research Workflow

This workflow is for ShapTCP experiments intended for software testing or
software engineering venues. It focuses on experiment correctness, not on
marketing claims.

## External Standards Consulted

- ACM artifact review and badging: documented, consistent, complete,
  exercisable, and reusable artifacts
  (https://www.acm.org/publications/policies/artifact-review-and-badging-current).
- SIGSOFT Empirical Standards / empirical SE reporting norms: explicit
  construct, internal, external, conclusion, and reproducibility validity
  (https://github.com/acmsigsoft/EmpiricalStandards).
- TCP literature practice: APFD/APFDc/NAPFD/rAPFDc definitions are
  benchmark-specific and must not be mixed without protocol alignment.

## Workflow Overview

```text
problem/model alignment
  -> source audit
  -> matrix contract
  -> baseline compatibility
  -> run config validation
  -> smoke run
  -> public benchmark run
  -> statistical analysis
  -> result package
  -> paper table/figure
```

Each stage has a stop condition. If a stop condition is hit, update source
notes instead of running more experiments.

## Stage 0: Problem and Metric Alignment

Purpose: ensure the experiment is actually a TCP experiment and that the metric
matches the data semantics.

Required alignment:

- candidate object is a permutation/order over test cases;
- objective/evaluation is stated: APFD, APFDc, NAPFD, recall@k, rare_recall@k,
  redundancy@k, or benchmark-native CI metric;
- formal instance `(T, E, M, c, w, B, H, sigma, protocol)` is identifiable;
- target entities are labeled as faults, bugs, mutants, coverage entities, or
  CI proxies;
- ShapTCP is described as optimizing residual Shapley-weighted coverage, not as
  directly optimizing APFD.

Stop conditions:

- APFD is reported on non-fault entities without relabeling the claim;
- APFDc is reported without verified durations;
- budgeted prefixes are reported as classic full-suite APFD/APFDc;
- coverage or CI-proxy columns are described as true faults;
- the experiment only selects a subset and never defines the induced order.

See `docs/tcp_problem_modeling.md` for the formal model and metric table.

## Stage 1: Source Audit

Purpose: prevent using the wrong benchmark, wrong artifact version, or wrong
data source.

Inputs:

- paper title, venue, year, DOI or official page;
- artifact URL;
- local root;
- license/access constraints;
- artifact commit, tag, DOI, or checksum.

Outputs:

- filled `benchmarks/source_notes/<benchmark>.md`;
- updated `benchmarks/manifest.json`;
- `scripts/audit_benchmarks.py` output.

Stop conditions:

- source URL cannot be verified;
- license/access terms are unclear;
- artifact is present but raw benchmark data is missing;
- only upstream result tables are present and no raw inputs are identified.

ShapTCP rule:

- `artifact present` never means `benchmark ready`;
- `upstream APFD table` never means `ShapTCP result`.

## Stage 2: Matrix Contract

Purpose: prevent mixing faults, mutants, coverage entities, and CI proxies.

For every matrix, record:

- row meaning: test method, test class, test script, CI job, or generated test;
- column meaning: fault, bug, mutant, statement, branch, method, or CI proxy;
- value meaning: covers, kills, detects, fails-with, or co-occurs-with;
- whether columns are ground truth or proxy;
- row id source and column id source;
- empty row/column policy;
- duplicate row/column policy.

Required files:

```text
matrix.txt
matrix.txt.tests
matrix.txt.entities
```

Stop conditions:

- columns cannot be identified;
- row ids do not match benchmark candidate tests;
- matrix was generated using future information;
- CI failure signatures are treated as root-cause faults without clustering.

ShapTCP rule:

- coverage matrices support scarcity/redundancy claims;
- fault/mutant matrices support fault-proxy detection claims;
- CI failure proxies must be labeled as proxies.

## Stage 3: Baseline Compatibility

Purpose: prevent unfair or meaningless baseline comparisons.

Compatibility checks:

- same candidate test set;
- same matrix columns or same benchmark-native data;
- same time budget or count budget;
- same train/test or temporal split;
- same observable information before prioritization time;
- same metric definition;
- same randomized seed protocol.

Baseline tiers:

- Tier 0: `random`, `total`, `additional`, `static_shapley`, `shaptcp`.
- Tier 1: cost-aware variants when durations are verified.
- Tier 2: FAST/OCP/ART/GA artifact-native baselines after raw input protocol is
  confirmed.
- Tier 3: CI-history baselines such as TCPFramework, RETECS, tp_rl, DeepOrder,
  TCP-CI, and AutoTCP after temporal split and feature visibility are aligned.

Stop conditions:

- baseline uses a different candidate set;
- baseline sees future failures or post-cycle data;
- baseline metric cannot be matched;
- artifact-native baseline consumes a representation ShapTCP does not receive.

ShapTCP rule:

- every ShapTCP result must include `additional`;
- every main ShapTCP result should include `static_shapley` ablation;
- random baselines use at least 30 seeds for public benchmark results.

## Stage 4: Run Config Validation

Purpose: make experiment fairness machine-checkable.

Create a JSON run config from:

```text
benchmarks/run_config_template.json
```

Validate it:

```bash
PYTHONPATH=src python3 scripts/validate_run_config.py path/to/run_config.json
PYTHONPATH=src python3 scripts/preflight_experiment.py path/to/run_config.json
PYTHONPATH=src python3 scripts/preflight_experiment.py path/to/run_config.json --check-files
```

The validator blocks common errors:

- `column_semantics=unverified`;
- missing row/value/ground-truth semantics;
- ShapTCP without `additional`;
- ShapTCP without `static_shapley`;
- public benchmark random baseline with fewer than 30 seeds;
- public benchmark source/matrix/result status not ready;
- baseline compatibility fields marked as unknown/unchecked/different;
- missing source note.

Machine-readable contracts live in:

```text
benchmarks/schemas/matrix_contract.schema.json
benchmarks/schemas/baseline_compatibility.schema.json
benchmarks/schemas/result_table.schema.json
```

Use this checked example as the minimum shape for a future run:

```text
benchmarks/examples/defects4j_metadata_smoke.run_config.json
```

Stop condition:

- validator fails.

## Stage 5: Smoke Run

Purpose: validate plumbing, not performance.

Allowed smoke inputs:

- synthetic suite;
- metadata-derived Defects4J trigger matrix;
- tiny manually inspected matrix;
- one confirmed public matrix with `evidence_level=pipeline_validation`.

Commands:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
PYTHONPATH=src python3 scripts/run_synthetic_suite.py --seeds 50
PYTHONPATH=src python3 scripts/run_benchmark_matrix.py matrix.txt \
  --benchmark <id> \
  --subject <subject> \
  --semantics <verified_semantics> \
  --run-id <run_id> \
  --evidence-level pipeline_validation \
  --claim-scope adapter_smoke \
  --source-status source-audited \
  --matrix-status verified \
  --result-status local_smoke_only
```

Stop conditions:

- methods cover different numbers of candidate tests without documented budget;
- APFD/APFDc values are not reproducible;
- a manual spot-check disagrees with first-detection positions.

ShapTCP rule:

- smoke results can debug code;
- smoke results cannot support paper performance claims.

## Stage 6: Public Benchmark Run

Purpose: generate reportable evidence.

Requirements:

- source note filled;
- run config validated;
- source commit/checksum recorded;
- ShapTCP commit recorded;
- matrix semantics verified;
- baseline compatibility checked;
- run command recorded.

Output package:

```text
outputs/<run_id>/
  run_config.json
  RUN_RECORD.md
  results.csv
  orders/
  traces/
  logs/
```

Stop conditions:

- result table does not include evidence/status metadata;
- random seed count is below protocol;
- durations are reconstructed but not labeled;
- any method fails silently or drops tests.

## Stage 7: Statistical Analysis

Purpose: prevent cherry-picking and weak conclusion validity.

Required:

- per-subject results, not only aggregate means;
- random mean/median and variance over seeds;
- Wilcoxon signed-rank test for paired comparisons;
- effect size such as Cliff's delta;
- Holm correction across related hypotheses;
- negative and neutral cases reported.

Primary comparisons:

- `shaptcp` vs `additional` for APFD when the matrix semantics permit it;
- `shaptcp` vs `additional` for rare_recall@k;
- `shaptcp` vs `additional` for redundancy@k;
- `cost_shaptcp` vs `cost_additional` for APFDc/time-budget recall.

Stop condition:

- too few independent subjects for statistical testing; report descriptive
  results only.

## Stage 8: Result Package and Paper Assets

Purpose: make tables and figures traceable.

Every table/figure should map to:

- exact run id;
- exact source note;
- exact run config;
- exact script command;
- exact ShapTCP commit;
- metric definitions;
- excluded subjects and reasons.

Do not use a table if:

- any data source is unclear;
- a baseline is not compatible;
- the matrix semantics are incomplete;
- result status is `local_smoke_only`.

## Reviewer Attack Checklist

Before submission, try to attack the experiment:

- Is this benchmark actually measuring faults, or only coverage entities?
- Did ShapTCP and the baseline see the same information?
- Is `additional` included everywhere ShapTCP appears?
- Are FAST/OCP/ART/GA baselines using the same candidate tests?
- Are APFD and APFDc computed with the same definitions as the benchmark?
- Are random baselines averaged over enough seeds?
- Are CI-history experiments temporally split?
- Are failure signatures clustered before being treated as root-cause proxies?
- Are negative results shown?
- Can another runner reproduce the table from source notes and run configs?

If the answer is no, fix the workflow before writing stronger claims.
