# ShapTCP Experimental Plan

This plan is the staged execution path for ShapTCP. It is intentionally
conservative: each stage has an accuracy gate, a compute boundary, and a clear
claim boundary before moving to the next stage.

## Project Positioning

ShapTCP is a matrix-first TCP method:

```text
input:  test -> fault / mutant / coverage-entity incidence matrix
method: Shapley-weighted additional coverage
goal:   prioritize scarce, non-redundant fault/entity coverage early
```

The first paper claim should be narrow and defensible:

> ShapTCP is a cooperative-game-derived scarcity weighting for additional
> coverage. It is designed to improve early discovery of rare or less redundant
> fault/entity coverage under matrix-based TCP settings.

Do not claim:

- an APFD approximation guarantee;
- that ShapTCP is universally better than additional coverage;
- that raw CI failure signatures are true root-cause faults;
- that CI-history baselines are directly comparable to matrix baselines without
  aligning data, splits, metrics, and observable features.
- that existing TCP methods ignore redundancy; additional coverage, OCP,
  ART/diversity, and combinator methods already address related issues.

## Research Questions

| RQ | Question | Primary Evidence | Main Metrics | Claim Boundary |
|---|---|---|---|---|
| RQ1 | Does ShapTCP prioritize scarce faults/entities earlier than standard coverage TCP? | SIR/OCP/FAST matrix benchmarks | rare-fault recall@k, first/median rank by degree, prefix recall stratified by degree | scarcity attribution only |
| RQ2 | Does ShapTCP reduce early redundant test-fault/entity hits? | SIR/OCP/FAST matrix benchmarks | redundancy@k, unique newly covered entities per prefix, duplicate-hit share | matrix benchmarks only |
| RQ3 | Does ShapTCP maintain or improve conventional fault-detection effectiveness? | matrix benchmarks | APFD, fault recall@k, time-to-first-fault | empirical claim, not theorem |
| RQ4 | Does cost-aware ShapTCP improve feedback under duration budgets? | benchmarks with durations or reconstructed execution cost | APFDc, time-budget recall, rare recall under time budgets | cost-aware variant |
| RQ5 | How sensitive is ShapTCP to fault/entity representation? | bug id vs mutant id vs coverage entity vs clustered/raw failure signature | metric deltas, degree distribution before/after clustering | depends on representation protocol |
| RQ6 | How does ShapTCP compare to broader matrix SOTA families? | OCP/FAST baselines: ART, GA/search, similarity/diversity, OCP | APFD/APFDc, recall@k, redundancy@k, prioritization time | same benchmark family only |
| RQ7 | Can ShapTCP transfer to CI-history settings? | TCPFramework/RTPTorrent or RETECS/tp_rl adapters | rAPFDc, NTR, ATR, NAPFD | second-stage adapter study |

## Stage 0: Source Audit and Reproducibility Lock

Goal: freeze facts before running experiments.

Tasks:

1. Record exact paper, repo, dataset, and environment source for each baseline in
   [sota_baselines.md](sota_baselines.md).
2. Keep [theory_review.md](theory_review.md) aligned with the code before
   claiming a theorem, guarantee, or benchmark result.
3. For every benchmark, store a local `SOURCE_NOTES.md` with download URL,
   checksum if available, license/access note, and observed file structure.
4. Pin the local ShapTCP commit hash for every reported run.
5. Separate `verified fact`, `adapter decision`, and `paper interpretation` in
   all notes.

Exit criteria:

- `docs/sota_baselines.md` has no baseline without a paper and artifact note.
- The first selected benchmark has a confirmed matrix file or a confirmed
  script for generating one.
- No heavy baseline training has started.

## Stage 1: Matrix Smoke Test

Goal: validate the evaluation pipeline on one small binary matrix.

Preferred input:

1. SIR small subject matrix, if available.
2. OCP/FAST small coverage or fault matrix, if SIR access is blocked.
3. A tiny manually extracted matrix only for plumbing, never for paper results.

Command:

```bash
PYTHONPATH=src python3 scripts/run_matrix_file.py path/to/matrix.txt --k 10
```

If durations exist:

```bash
PYTHONPATH=src python3 scripts/run_matrix_file.py path/to/matrix.txt \
  --durations path/to/durations.csv \
  --k 10
```

Baselines:

- `random`
- `total coverage`
- `additional coverage`
- `cost-aware additional coverage`, only if durations exist
- `shortest duration`, only if durations exist
- `ShapTCP`
- `cost-aware ShapTCP`, only if durations exist

Metrics:

- `APFD`
- `APFDc`, only if durations exist
- `fault_recall_at_k`
- `rare_fault_recall_at_k`
- `redundancy_at_k`

Exit criteria:

- All methods run on the same candidate test set and same matrix.
- Order length, covered entities, and first-detection positions are manually
  spot-checked for at least one small subject.
- Results are treated as pipeline validation, not performance evidence.

## Stage 2: Public Matrix Benchmark

Goal: collect first real evidence for ShapTCP's scarcity/redundancy behavior.

Priority:

| Priority | Benchmark | Why | Accuracy Gate |
|---|---|---|---|
| P0 | SIR small subjects | Closest to `test -> fault` if fault matrices are available/generated | confirm object package format and license |
| P1 | OCP | Strong coverage/mutation artifact with APFD/time/order results | confirm raw matrix path and method-to-result mapping |
| P2 | FAST | Similarity/diversity artifact with fault matrix, coverage info, and black-box representation | isolate old Python/scipy environment |
| P3 | Defects4J small subset | High community recognition | JDK11/Docker setup and matrix-generation protocol |

Baseline expansion:

- Stage 1 baselines.
- OCP, if running OCP artifact.
- FAST variants, if running FAST artifact.
- ART-F/ART-D, from FAST/OCP artifact where available.
- GA/search-based, from FAST/OCP artifact where available.

Recommended first paper table:

| Benchmark | Methods | Metrics | Seeds |
|---|---|---|---|
| SIR/OCP small set | random, total, additional, ShapTCP | APFD, recall@k, rare recall@k, redundancy@k | random >= 30 |
| duration-aware subset | additional, cost-additional, ShapTCP, cost-ShapTCP, shortest | APFDc, time-budget recall | random >= 30 |
| FAST/OCP stronger set | artifact baselines + ShapTCP | benchmark-native APFD/APFDc plus our redundancy metrics | artifact protocol |

Exit criteria:

- ShapTCP is compared against additional coverage on every matrix benchmark.
- Random results use multiple seeds.
- The report states whether matrix columns are true faults, mutants, or coverage
  entities.
- The report includes at least one negative/neutral case if ShapTCP does not
  improve APFD.

## Stage 3: Defects4J Matrix Construction

Goal: use a recognized real-bug benchmark without pretending it is a ready-made
matrix dataset.

Environment:

```text
OS: Linux or Docker-friendly environment
Java: JDK 11
Tools: Git, svn, Perl, cpanm
Timezone: America/Los_Angeles
```

Protocol options:

| Matrix Type | Construction | Pros | Cons |
|---|---|---|---|
| trigger matrix | `tests.trigger` per bug | fast and real-bug grounded | sparse, only exposing tests |
| coverage matrix | `defects4j coverage` per test/suite | closer to coverage TCP | coverage entity is not fault |
| mutation matrix | `defects4j mutation` per test/suite | strong fault proxy | slow and CPU/disk heavy |

First subset:

- `Lang`, `Chart`, `Codec`, or `Cli`.
- Start with 3-5 bugs only.
- Do not run Closure/Math/JacksonDatabind mutation first.

Exit criteria:

- A documented script converts Defects4J output to `MatrixDataset`.
- Bug IDs, test IDs, and entity IDs are preserved.
- Runtime and disk use are recorded.

## Stage 4: CI-History Adapter

Goal: test whether ShapTCP's matrix idea can be adapted to CI logs.

Primary benchmark:

- TCPFramework / RTPTorrent / TravisTorrent.

Why:

- TCPFramework provides modern non-RL history/combinator baselines:
  `FoldFails`, `FailDensity`, `Rocket(100)`, `BordaMixed`, `Interpolated`,
  `GenericBroken`.
- Metrics include `rAPFDc`, `NTR`, and `ATR`.

Environment:

```text
Python >= 3.13
uv
RTPTorrent Zenodo package
TravisTorrent metadata
11 Java project checkouts
large disk budget
```

Adapter design:

1. Implement ShapTCP as a TCPFramework `Approach`, or export per-cycle order
   from ShapTCP and evaluate with TCPFramework metrics.
2. Construct fault/entity proxy using one of:
   - previous failure clusters;
   - failing-test co-occurrence clusters;
   - changed-file/test-entity relations, if available.
3. Use only information visible before the current cycle.

Exit criteria:

- Temporal split is preserved.
- Failure clustering protocol is documented.
- We report where the adapter uses inferred fault proxies rather than ground
  truth faults.

## Stage 5: ML/RL/AutoML Comparisons

Goal: compare against learning-based TCP without mixing incompatible data.

Use these only after matrix and TCPFramework stages are stable.

| Artifact | Use | Environment | ShapTCP Integration |
|---|---|---|---|
| RETECS | classic RL-TCP baseline | old Python/Docker | external baseline on CI-history data |
| tp_rl | RL formulation benchmark | Python 3.7 + Stable Baselines 2.10 | external baseline; align APFD/NRPA and split |
| DeepOrder | deep CI-history baseline | Python 3.6 + TF 2.1/Keras 2.2 | external baseline; align data and metrics |
| TCP-CI | feature-rich learning-to-rank | Understand + RankLib + Java/Python | future risk-aware ShapTCP weights/prior |
| AutoTCP | AutoML comparator | Yaraghi dataset + AutoML dependencies | feature-rich CI comparator, not matrix baseline |

Exit criteria:

- Each learning baseline uses its intended dataset and protocol.
- ShapTCP is not compared to learned methods unless the same candidate tests,
  training history, and evaluation cycles are aligned.
- We report per-project results, not only aggregate means.

## Ablations

Required:

- `additional coverage` vs `ShapTCP`
- static Shapley ranking vs residual ShapTCP, to separate attribution from
  sequence-aware residual scheduling
- `cost-aware additional` vs `cost-aware ShapTCP`
- with vs without fault/root-cause clustering when using failure signatures
- fault/entity degree distribution analysis
- rare-fault threshold sensitivity: degree <= 1, degree <= 2, degree <= 3
- count-budget sensitivity: absolute k in {1, 5, 10} and relative k in {10%,
  20%, 50%, 100%}
- time-budget sensitivity, when durations exist: {10%, 20%, 50%, 100%} of
  total suite time
- deterministic tie-breaking policy for greedy methods
- random/stochastic baseline seeds

Optional:

- `lexicographic_unique=True`
- non-uniform fault weights
- changed-file or risk-based weights

## Statistical Reporting

Use conservative reporting:

- per-subject table;
- aggregate table only after per-subject results;
- effect size and confidence intervals where practical;
- Wilcoxon signed-rank or paired permutation tests for paired subject-level
  metrics;
- multiple comparison correction when many methods are compared.

Randomized baselines should use at least 30 seeds. Deterministic baselines should
use fixed lexical tie-breaking or report tie-breaking policy.

## Compute Guidance

GPU is not required for the ShapTCP core, SIR/OCP matrix experiments,
Defects4J coverage/mutation, TCPFramework, or RankLib-style learning-to-rank.

Recommended development machine:

```text
CPU: 8-16 cores
RAM: 32GB minimum, 64GB comfortable
Disk: 300GB-1TB SSD
OS: Ubuntu 22.04/20.04 or Docker-friendly Linux
Java: JDK11, optionally JDK8
GPU: optional, useful mainly for DeepOrder or some large ML/RL runs
```

## First Three Execution Days

Day 1:

1. Clone ShapTCP.
2. Run unit tests and scale smoke test.
3. Download or inspect one SIR/OCP/FAST small matrix candidate.
4. Convert it to row-wise binary matrix if needed.
5. Run `scripts/run_matrix_file.py`.

Day 2:

1. Add a benchmark-specific adapter for the first confirmed data source.
2. Save raw result CSVs under an ignored `results/` directory.
3. Add a `SOURCE_NOTES.md` for the benchmark.
4. Run Stage 1 baselines with multiple random seeds.

Day 3:

1. Add a second subject or benchmark.
2. Add rare-fault and redundancy plots/tables.
3. Decide whether the next step is OCP/FAST stronger baselines or Defects4J
   setup.

## Stop Conditions

Pause and re-evaluate if:

- ShapTCP only ties additional coverage on all matrix benchmarks and does not
  improve redundancy or rare-fault recall;
- fault/entity columns cannot be interpreted consistently;
- a benchmark requires enough reconstruction that it becomes a paper by itself;
- a baseline cannot be tied to a paper and artifact.
