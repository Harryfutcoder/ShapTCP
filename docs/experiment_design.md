# ShapTCP Experiment Design

This document is the detailed experiment plan for the first ShapTCP paper. It
translates the theory claim into reproducible studies, baseline groups, metrics,
datasets, and environment requirements.

## Paper Claim

Primary claim:

> ShapTCP uses exact Shapley scarcity weights inside residual coverage
> prioritization. It aims to preserve conventional fault-detection effectiveness
> while improving early scarce-entity recall and reducing redundant early
> coverage.

Do not claim:

- universal APFD superiority;
- an APFD approximation guarantee;
- that coverage entities are true faults;
- that CI-history learning baselines are directly comparable to matrix
  baselines without aligned splits and features.

## Source Basis

| Area | Sources Used For Design |
|---|---|
| Classic TCP definition and APFD family | Rothermel et al., TSE 2001; Yoo and Harman survey; TCPFramework survey |
| Coverage baselines | Rothermel et al. total/additional coverage; OCP artifact Java comparators |
| Search and diversity baselines | Li et al. TSE 2007; Jiang et al. ASE 2009 ART; FAST ICSE 2018 |
| Public matrix/data candidates | SIR, OCP, FAST, Defects4J |
| CI-history extension | RTPTorrent, TCPFramework, RETECS, tp_rl, DeepOrder, TCP-CI, AutoTCP |

Primary links:

- Rothermel et al. 2001: https://digitalcommons.unl.edu/csearticles/9/
- TCPFramework survey/code: https://github.com/LechMadeyski/MSc25TomaszChojnacki
- FAST ICSE 2018: https://conf.researchr.org/details/icse-2018/icse-2018-Technical-Papers/84/FAST-Approaches-to-Scalable-Similarity-based-Test-Case-Prioritization
- FAST artifact: https://github.com/icse18-fast/FAST
- OCP artifact: https://github.com/QuanjunZhang/OCP
- SIR: https://sir.csc.ncsu.edu/portal/index.php
- Defects4J: https://github.com/rjust/defects4j
- RTPTorrent: https://zenodo.org/records/4046180
- RETECS: https://github.com/mregorova/RETECS
- tp_rl: https://github.com/moji1/tp_rl
- DeepOrder: https://github.com/T3AS/DeepOrder-ICSME21
- TCP-CI: https://github.com/Ahmadreza-SY/TCP-CI
- AutoTCP: https://github.com/humains-lab/2026-AutoTCP

For the formal TCP problem model, objective families, metric definitions, and
how ShapTCP maps to the standard permutation formulation, see
`docs/tcp_problem_modeling.md`.

## TCP Modeling Alignment

This paper treats TCP as a permutation optimization problem:

```text
Given test suite T, all permutations PT, and objective f: PT -> R,
find pi* in PT such that f(pi*) >= f(pi) for every pi in PT.
```

The primary evaluation objective is early detection, measured by APFD/APFDc or
benchmark-native CI metrics. ShapTCP does not solve this sequence-level
objective exactly. It uses a tractable surrogate:

```text
score_i(S) = sum_{f in F_i \ covered(S)} w_f / |T_f|
```

This surrogate is residual weighted coverage with exact Shapley scarcity
weights. Therefore, ShapTCP's main mechanism-level outcomes are:

- earlier rare-entity detection;
- lower redundant early coverage;
- APFD/APFDc that is competitive with classic additional coverage.

APFD/APFDc superiority is an empirical question, not a theorem.

## Formal Paper Scope

The first paper should keep these layers separate:

| Layer | Formal object | Paper use |
|---|---|---|
| Problem | permutation `pi` over candidate tests `T` | defines TCP task |
| Data | matrix `M[i,e]` with semantic label for `e` | defines what can be claimed |
| Method | greedy maximization of residual Shapley-weighted coverage | defines ShapTCP |
| Evaluation | APFD/APFDc/NAPFD/recall/redundancy/runtime | validates the produced order |
| Evidence | public benchmark + source note + run config | supports paper tables |

Minimum method formalization:

```text
Input:
  T = candidate tests
  E = entities
  M[i,e] in {0,1}
  w_e >= 0, default 1
  optional c_i > 0

Define:
  T_e = {i in T : M[i,e] = 1}
  covered(S) = {e : exists i in S, M[i,e] = 1}
  score_i(S) = sum_{e in F_i \ covered(S)} w_e / |T_e|

Choose:
  pi_t = argmax_{i notin S} score_i(S)
```

Cost-aware variant:

```text
pi_t = argmax score_i(S) / c_i^alpha
```

Use `alpha=0` for main ShapTCP and `alpha=1` only as the cost-aware variant.

Metric eligibility:

| Matrix semantics | Primary metrics | Forbidden wording |
|---|---|---|
| `fault` / `bug` | APFD, APFDc, NAPFD, fault recall, rare fault recall | none, if source is verified |
| `mutant` | mutant APFD, mutation recall, rare mutant recall | true fault detection unless framed as proxy |
| `statement` / `branch` / `method` | coverage/entity recall, redundancy, runtime | true APFD/fault-detection claim |
| `ci_proxy` | benchmark-native CI metrics, clustered-proxy recall | root-cause/fault claim without clustering or mapping |

If a budgeted prefix is used, do not report classic full-suite APFD/APFDc for
that prefix. Use recall@k, time-budget recall, NAPFD with its exact formula, or
the benchmark-native CI metric.

## Experiment 0: Mechanism Sanity

Goal: verify that the implementation matches the corrected theory before using
public data.

Datasets:

- hand-written synthetic scenarios in `src/shaptcp/synthetic.py`;
- generated sparse matrices from `scripts/run_synthetic_suite.py`.

Baselines:

- `random`;
- `total`;
- `additional`;
- `static_shapley`;
- `shaptcp`;
- `cost_additional`;
- `cost_shaptcp`.

Metrics:

- APFD-like entity rank score only if explicitly labeled as synthetic and
  non-reportable;
- APFDc-like cost score only when synthetic durations exist, again
  non-reportable;
- recall@k;
- rare_recall@k;
- redundancy@k;
- runtime.

Expected signal:

- ShapTCP should reduce redundancy against `static_shapley`;
- ShapTCP should improve rare recall against `additional`;
- ShapTCP may not beat `additional` on APFD.

Claim boundary:

- sanity only;
- not paper evidence;
- useful for regression tests and algorithm debugging.

Commands:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
PYTHONPATH=src python3 scripts/run_synthetic.py
PYTHONPATH=src python3 scripts/run_synthetic_suite.py --seeds 50
```

## Experiment 1: Core Matrix Benchmark

Research question:

> Does ShapTCP improve early scarce-entity coverage and reduce redundancy while
> maintaining APFD close to classic additional coverage?

Datasets:

| Priority | Dataset | Matrix Type | Current Status |
|---|---|---|---|
| P0 | SIR small subjects | fault or coverage matrix, if exposed/generated | source access still needed |
| P1 | OCP | coverage/mutation artifact; raw matrix path still unconfirmed | source audited, not matrix-ready |
| P2 | FAST | fault matrix and coverage/black-box representations, after source checkout | source audited; write loader and confirm key/value direction |
| P3 | Defects4J trigger metadata | per-bug trigger-test metadata across separate buggy revisions | adapter smoke only, not a standard multi-fault TCP instance |

Baselines:

- `random`, at least 30 seeds;
- `original`, if the benchmark provides a meaningful native order;
- `total coverage`;
- `additional coverage`;
- `static_shapley`, ablation;
- `shaptcp`.

Metrics:

- APFD only for verified true fault/bug matrices;
- APFD over mutants only when explicitly named as mutant APFD / APFD over
  mutants;
- coverage entities must use coverage/entity recall or first-coverage-rank
  metrics, not true APFD terminology;
- recall@k;
- rare_recall@k with degree thresholds 1, 2, and 3;
- redundancy@k;
- median first-detection rank stratified by entity degree;
- prioritization runtime.

Environment:

- Python >= 3.10 for ShapTCP;
- no GPU;
- only confirmed dense matrix files for this experiment.

Acceptance gate:

- every result row must include `evidence_level`, `claim_scope`, and verified
  `semantics`;
- matrix columns must be labeled as `fault`, `bug`, `mutant`, `statement`,
  `branch`, `method`, or `ci_proxy`;
- ShapTCP must be compared against `additional` on every subject.
- all baselines must receive the same candidate tests and the same matrix;
- deterministic baselines must use documented tie-breaking;
- random baselines must report aggregate over seeds, not one lucky seed.

Success criterion for the first paper:

- APFD or the appropriate semantic-aware rank metric is statistically tied with,
  or not materially below, `additional`;
- rare_recall@k and redundancy@k improve consistently;
- runtime overhead is small relative to data preparation.

Runner:

```bash
PYTHONPATH=src python3 scripts/run_benchmark_matrix.py matrix.txt \
  --benchmark <benchmark> \
  --subject <subject> \
  --semantics <fault|bug|mutant|statement|branch|method|ci_proxy> \
  --evidence-level public_benchmark \
  --claim-scope matrix_core \
  --k 20
```

## Experiment 2: Cost-Aware Feedback

Research question:

> Does cost-aware ShapTCP improve earlier feedback under execution-time budgets?

Datasets:

- OCP only if per-test duration or benchmark-native time data can be mapped to
  test ids;
- Defects4J after per-test execution time is generated;
- TCPFramework/RTPTorrent later, where cost-aware CI metrics are native.

Baselines:

- `additional`;
- `cost_additional`;
- `shortest_duration`;
- `shaptcp`;
- `cost_shaptcp`.

Metrics:

- APFDc;
- NAPFD or recall under a time budget, when not all tests are executed;
- time-budget recall at 10%, 25%, 50% budget;
- rare_recall under time budget;
- first failing/fault-revealing time;
- runtime.

Environment:

- Python for ShapTCP;
- benchmark-specific duration generation if durations are not shipped;
- Defects4J duration generation requires Java 11.

Claim boundary:

- report only when duration source is verified;
- reconstructed durations must be labeled as reconstructed;
- do not mix prioritization-time cost with test-execution-time cost.

## Experiment 3: Representation Robustness

Research question:

> How sensitive is ShapTCP to the meaning of a matrix column?

Representations:

- true fault id, if benchmark provides it;
- mutant id;
- coverage entity: statement, branch, method;
- CI failure signature;
- clustered CI root-cause proxy.

Baselines:

- `additional`;
- `static_shapley`;
- `shaptcp`;
- `shaptcp` with co-failure clustering when using raw failure signatures.

Metrics:

- degree distribution before and after clustering;
- rare_recall@k by degree bucket;
- redundancy@k;
- APFD only when true fault/bug semantics support it; mutant APFD only when
  explicitly named as APFD over mutants;
- APFDc only with verified per-test execution durations;
- sensitivity of ranking under representation changes.

Datasets:

- OCP for coverage/mutant-style representations after raw matrix confirmation;
- Defects4J for per-bug trigger-rank aggregation, then coverage/mutation later;
- TCPFramework/RTPTorrent only for CI failure proxies.

Claim boundary:

- coverage-entity results support scarcity/redundancy claims, not true fault
  detection claims;
- failure signatures must not be treated as true faults without clustering or
  ground-truth issue mapping.

## Experiment 4: Strong Matrix Baselines

Research question:

> Does ShapTCP add value beyond established coverage, diversity, and
> search-based TCP methods?

Baseline families:

| Family | Concrete Methods | Source |
|---|---|---|
| Coverage greedy | total, additional | Rothermel et al.; local implementation |
| Diversity/randomized | ART-F, ART-D | Jiang et al.; FAST artifact where available |
| Search-based | Genetic/search-based TCP | Li et al.; OCP artifact or a separately implemented search baseline |
| FAST greedy family | FAST artifact `GT`, `GA`, `GA-S` where verified | In FAST naming, `GA` denotes Greedy Additional, not genetic algorithm |
| Similarity-based | FAST-pw, FAST-one, FAST-log, FAST-sqrt, FAST-all | FAST ICSE 2018 artifact, `icse18-fast/FAST` |
| OCP | OCP and OCP-related comparators | OCP artifact |

Datasets:

- FAST subjects after source checkout and old environment setup;
- OCP after raw matrix path and metric protocol are confirmed.

Metrics:

- benchmark-native rank/coverage metrics with the artifact's own names;
- fault APFD only when columns are verified true faults/bugs;
- APFDc only when per-test execution durations, not prioritization runtimes,
  are aligned with all candidate tests;
- our rare_recall@k and redundancy@k on the same matrix;
- prioritization time;
- per-subject ranks.

Environment:

- FAST likely needs an isolated old Python/scipy/xxhash environment;
- OCP Java comparators need their original input paths and protocol verified;
- ShapTCP remains Python-only after matrix conversion.

Claim boundary:

- artifact-native baselines can be reported only when their input matrix and
  metric protocol match ShapTCP's input;
- do not call an artifact implementation the "original official code" unless
  that is explicitly documented.

## Experiment 5: Defects4J Generated Matrices

Research question:

> Can ShapTCP operate on a widely recognized real-bug benchmark when the matrix
> is generated under a documented protocol?

Sub-experiments:

| Id | Matrix | Cost | Purpose |
|---|---|---|---|
| E5a | metadata trigger matrix | laptop-safe | adapter validation only |
| E5b | execution-derived trigger matrix | light/medium | bug-id matrix evidence |
| E5c | coverage matrix | medium | coverage-entity evidence |
| E5d | mutation matrix | heavy | mutant/fault-proxy evidence |

Defects4J warning:

- each Defects4J bug id is a distinct buggy revision (`<id>b`), not one fault
  inside a shared multi-fault program version;
- a matrix whose columns are several Defects4J bug ids is therefore a
  cross-version metadata artifact, useful for adapter smoke tests or per-bug
  rank aggregation, not a standard single-suite multi-fault TCP instance;
- reportable trigger experiments must evaluate each bug revision with its own
  candidate test universe and aggregate triggering-test rank, TTFF, or recall.
- the candidate universe must be `tests.all`, `tests.relevant`, or another
  documented executable test set; it must not contain only `tests.trigger`.

First projects:

- `Lang`, active bugs `1 3 4` for smoke;
- then `Chart`, `Codec`, `Cli`, or `Math` subsets after environment is stable.

Environment:

- Linux or Docker-friendly development machine;
- Java 11;
- Git, svn, Perl, cpanm;
- timezone `America/Los_Angeles`;
- enough disk for checkouts and generated reports.

Commands:

```bash
PYTHONPATH=src python3 scripts/build_defects4j_metadata_matrix.py \
  --defects4j-root /path/to/defects4j \
  --project Lang \
  --bugs 1 3 4 \
  --output data/processed/defects4j/Lang_metadata_trigger_1_3_4.txt

PYTHONPATH=src python3 scripts/build_defects4j_trigger_matrix.py \
  --defects4j-bin /path/to/defects4j/framework/bin/defects4j \
  --project Lang \
  --bugs 1 3 4 \
  --work-dir data/work/defects4j \
  --candidate-property tests.all \
  --output data/processed/defects4j/Lang_trigger_1_3_4.txt \
  --execute
```

Claim boundary:

- metadata trigger matrix is `pipeline_validation`;
- execution-derived trigger data can be public benchmark evidence only as
  per-bug rank/TTFF/recall aggregation with a documented candidate universe;
- coverage/mutation matrices require separate protocol notes.

## Experiment 6: CI-History Transfer

Research question:

> Can ShapTCP's scarcity weighting help in CI-history TCP when true fault
> matrices are unavailable?

Datasets:

- TCPFramework / RTPTorrent / TravisTorrent;
- RETECS industrial datasets;
- tp_rl enriched datasets;
- DeepOrder datasets;
- TCP-CI / Yaraghi 25-project dataset.

Baselines:

- TCPFramework: `FoldFails`, `FailDensity`, `Rocket(100)`, `BordaMixed`,
  `Interpolated`, `GenericBroken`;
- RETECS;
- tp_rl pairwise/listwise/pointwise RL;
- DeepOrder;
- TCP-CI learning-to-rank;
- AutoTCP, only as a late feature-rich comparator.

Metrics:

- benchmark-native APFD/NAPFD/NRPA where applicable;
- rAPFDc, NTR, ATR for TCPFramework;
- duration-aware feedback metrics;
- rare failure-cluster recall and redundancy when failure proxies are used.

Environment:

- TCPFramework: Python >= 3.13, `uv`, RTPTorrent package, TravisTorrent CSV,
  11 Java repo checkouts, large disk budget;
- RETECS: old Python stack or Docker;
- tp_rl: Python 3.7 and Stable Baselines 2.10;
- DeepOrder: Python 3.6, TensorFlow 2.1.0, Keras 2.2.4;
- TCP-CI: Understand Build 1029, RankLib, Java, Python dependencies;
- AutoTCP: AutoML dependencies and Yaraghi dataset.

Claim boundary:

- this is second-stage work;
- compare only after candidate tests, temporal split, training history, and
  metrics are aligned;
- ShapTCP must label CI failure clusters as proxies.

## Statistical Protocol

For public benchmark results:

- use per-subject paired comparisons;
- random baseline uses at least 30 seeds;
- report mean, median, standard deviation, and per-subject rank;
- use Wilcoxon signed-rank tests for paired non-parametric comparisons;
- report effect size such as Cliff's delta;
- apply Holm correction across families of hypotheses;
- include negative and neutral cases.

Primary hypotheses:

- H1: ShapTCP improves rare_recall@k over `additional`;
- H2: ShapTCP reduces redundancy@k over `additional`;
- H3: ShapTCP has APFD not materially worse than `additional`;
- H4: cost-aware ShapTCP improves APFDc/time-budget recall when durations are
  verified.

## Expected Outcomes and Decision Gates

Green light for a strong first paper:

- APFD is close to `additional` across matrix benchmarks;
- rare_recall@k and redundancy@k improve consistently;
- gains survive at least one non-synthetic public benchmark;
- ablation shows `static_shapley` alone is insufficient;
- source notes and matrix semantics are complete.

Yellow light:

- ShapTCP wins only rare_recall but loses APFD materially;
- improvements occur only on coverage entities, not faults/mutants;
- strong baselines from FAST/OCP erase the advantage.

Red light:

- public matrices show no rare_recall or redundancy improvement;
- matrix semantics cannot be verified;
- results depend on raw failure signatures without clustering.

## First Development-Machine Milestones

1. Run `audit_benchmarks.py` and fill source notes.
2. Confirm one real dense matrix from SIR, OCP, or FAST.
3. Run Experiment 1 on one subject.
4. Run Defects4J execution-derived per-bug trigger-rank aggregation for
   `Lang 1 3 4`.
5. Add artifact-native OCP/FAST baselines only after raw matrix protocol is
   confirmed.
