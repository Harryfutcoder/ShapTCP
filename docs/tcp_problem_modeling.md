# TCP Problem Modeling Notes

This document aligns ShapTCP with the standard test case prioritization (TCP)
problem definition used in regression-testing literature. It is a modeling
guide, not a result-claim document.

## Literature Anchor

Classic TCP work defines prioritization as an ordering problem: schedule test
cases so that some performance goal is improved, often the rate of fault
detection. The standard abstract formulation is:

```text
Given:
  T      = a test suite
  PT     = all permutations/orderings of T
  f      = objective function, f: PT -> R

Find:
  pi* in PT such that f(pi*) >= f(pi) for every pi in PT
```

This formulation is intentionally broad: different studies instantiate `f`
with rate of fault detection, cost-aware feedback, requirement coverage, fault
severity, historical failure probability, or CI-specific metrics.

Survey-level framing:

- Yoo and Harman describe test case prioritization as ordering tests so that
  early fault detection is maximized.
- Khatibsyarbini et al. classify TCP approaches by input data, technique type,
  and evaluation target, and emphasize that prioritization improves testing
  efficiency by scheduling execution order.
- Khatibsyarbini et al. explicitly separate minimization, selection, and
  prioritization: minimization removes redundant tests, selection chooses
  change-relevant tests, and prioritization orders the candidate tests.
- TCPFramework-style CI work treats TCP as an online/CI scheduling problem with
  temporal history, durations, flaky tests, and per-cycle feedback.
- CI-focused mapping work reports that many CI TCP approaches are
  history-based and are commonly evaluated by time and fault-detection
  effectiveness.

Reference links used for this alignment:

- Rothermel et al., "Prioritizing Test Cases For Regression Testing":
  https://digitalcommons.unl.edu/csearticles/9/
- Yoo and Harman, "Regression testing minimization, selection and
  prioritization: a survey":
  https://kclpure.kcl.ac.uk/portal/en/publications/regression-testing-minimization-selection-and-prioritization-a-su
- Khatibsyarbini et al., "Test case prioritization approaches in regression
  testing: A systematic literature review":
  https://eprints.utm.my/85361/
- Lima et al., "Test Case Prioritization in Continuous Integration
  environments: A systematic mapping study":
  https://www.sciencedirect.com/science/article/pii/S0950584920300185
- Chojnacki and Madeyski, TCPFramework systematic review and replication
  package:
  https://github.com/LechMadeyski/MSc25TomaszChojnacki

## Domain Objects

A TCP experiment must state the meaning of each object.

```text
P_b, P_f    buggy/fixed or old/new program versions
T           candidate tests available at prioritization time
pi          a permutation/order over T
F           target entities to detect or cover
c_i         execution cost/duration of test i
s_f         severity or utility weight of entity f
H           history visible before the current prioritization point
M           test-entity matrix, M[i, f] in {0, 1}
```

The entity set `F` is not always true faults:

| Column semantics | Meaning | Valid claim type |
|---|---|---|
| `fault` / `bug` | benchmark-provided real fault or bug id | fault/bug detection |
| `mutant` | mutation-analysis proxy | mutation/fault-proxy detection |
| `statement`, `branch`, `method` | coverage entity | coverage and redundancy only |
| `ci_proxy` | failure signature or clustered CI failure proxy | CI feedback proxy only |

This distinction is a construct-validity requirement. A coverage matrix should
not be described as a true fault-detection benchmark.

## Regression Testing Task Boundaries

Do not merge these tasks in the paper or code.

| Task | Output | Typical Goal | ShapTCP Relation |
|---|---|---|---|
| Test suite minimization/reduction | smaller suite | permanently remove redundant tests while preserving a criterion | not our target |
| Regression test selection | subset for current change | temporarily run change-relevant tests | can feed candidate set, but not ShapTCP itself |
| Test case prioritization | ordered sequence/permutation | execute higher-value tests earlier | our target |
| Test suite augmentation/generation | new tests | add tests for new behavior | outside current paper |

ShapTCP takes the candidate set as fixed. If an upstream selector filters tests,
that selector must be part of the documented protocol and must be applied
equally to all baselines.

## TCP Scenario Families

TCP studies differ mainly by what information is visible before ordering.

| Scenario | Visible Information | Common Data Semantics | Common Metrics | Risk |
|---|---|---|---|---|
| White-box regression TCP | coverage from previous version, program structure | statement/branch/method/mutant/fault matrix | APFD, APFDc, coverage recall | treating coverage as true faults |
| Black-box/input TCP | test text, input strings, names, distances | similarity/distance, failure history | APFD, NAPFD, time to failure | comparing against coverage baselines with extra information |
| History-based TCP | previous outcomes and durations | pass/fail/failure count/duration history | APFD/APFDc/NAPFD, CI metrics | leakage from current/future cycle |
| CI TCP | per-build history, changed files, flaky tests, time limits | failing tests or failure-signature proxies | NTR, ATR, rAPFDc, TTFF, time-budget recall | temporal split and proxy semantics |
| ML/RL TCP | engineered features and labels/rewards | learned failure probability or ranking reward | benchmark-native metrics plus training cost | unfair feature visibility or retraining protocol |

ShapTCP's first paper is a matrix-based method. It can be evaluated in
white-box or generated-matrix settings first; history-based/CI use requires a
separate adapter that constructs valid entities from historical outcomes.

## Standard Objective Families

### Sequence-Level Objective

The canonical TCP objective is sequence-level:

```text
maximize Eval(pi)
```

where `Eval` is often APFD, APFDc, NAPFD, time-to-first-failure, or a
benchmark-native CI metric. This objective depends on the first position or
first time at which each fault/entity is observed.

Let:

```text
TF_f(pi) = position of the first test in pi that detects/covers f
n        = number of tests
m        = number of target entities
```

For classic equal-cost APFD:

```text
APFD(pi) = 1 - (sum_f TF_f(pi)) / (n * m) + 1 / (2n)
```

Maximizing APFD is equivalent to minimizing the sum of first-detection
positions. Exact optimization is combinatorial over `n!` orderings and is
normally approached with heuristics or greedy surrogates.

Important distinction:

```text
APFD/APFDc/NAPFD = evaluation functions over a produced order.
Algorithm score  = rule used to construct the order.
```

A TCP paper may optimize a surrogate score and evaluate with APFD, but it must
not state that it directly maximizes APFD unless the optimizer actually searches
that objective.

### Cost-Aware Objective

When real test durations are available, APFDc accounts for both fault severity
and test cost. A common form is:

```text
APFDc(pi) =
  sum_f s_f * (sum_{j=TF_f(pi)}^n c_{pi_j} - 0.5 * c_{pi_TF_f})
  / ((sum_i c_i) * (sum_f s_f))
```

With equal costs and equal severities, APFDc reduces to the same intuition as
APFD. APFDc must not be reported unless the duration source is verified and
aligned across baselines.

### Partial-Budget Objective

Under a count or time budget, not every fault may be detected. Studies often
use NAPFD, recall@k, time-budget recall, or benchmark-native CI metrics.
Because NAPFD and CI metrics have multiple variants in the literature, a run
must record the exact formula used by the benchmark or implementation.

### Prefix-Coverage Surrogate

Many TCP techniques optimize a prefix-level surrogate:

```text
maximize g(S) = sum_f w_f * 1[f is covered by some test in S]
subject to |S| <= k or cost(S) <= B
```

For deterministic coverage, `g(S)` is monotone submodular. Greedy selection has
the standard `(1 - 1/e)` guarantee for fixed weighted maximum coverage under a
cardinality budget. This is a subset/prefix coverage guarantee, not an APFD
guarantee over the entire sequence.

## Metric Definitions and Use

| Metric | Optimizes/Measures | Use When | Main Risk |
|---|---|---|---|
| APFD | early first detection by test position | equal-cost full-suite setting | hides test duration |
| APFDc | early first detection by time/cost and severity | real durations exist | invalid with synthetic or mismatched durations |
| NAPFD | normalized partial-suite detection | incomplete/partial execution | variants differ by paper |
| recall@k | fraction of entities found by first `k` tests | early prefix matters | insensitive to exact rank inside prefix |
| rare_recall@k | recall over low-degree entities | scarcity is central | rare threshold must be declared |
| redundancy@k | overlap/repeated coverage in first `k` tests | diversity/non-redundancy matters | not a fault-detection metric alone |
| TTFF | time/rank to first failing test | CI feedback | only meaningful with failing builds |
| NTR/ATR/rAPFDc | CI-history ranking/cost metrics | TCPFramework-like CI studies | formulas must follow benchmark implementation |

## Baseline Modeling

Baselines must be compared under the same candidate tests, visibility, split,
budget, and metric formula.

| Baseline | Mathematical view | Notes |
|---|---|---|
| `random` | uniform random permutation | use >=30 seeds for reportable public runs |
| original/order-as-is | benchmark-native order | only if provided and meaningful |
| total coverage | sort by `|F_i|` | coverage volume, no residual update |
| additional coverage | greedy by `|F_i \ covered(S)|` | canonical coverage baseline |
| static_shapley | sort by exact static coverage-game Shapley score | ShapTCP attribution ablation |
| cost_additional | greedy by residual coverage per cost | requires verified durations |
| FAST/ART/diversity | similarity or diversity surrogate | use artifact-native protocol only after input alignment |
| GA/search-based | search over orderings or prefixes | compare only with matched objective/inputs |
| RL/ML CI methods | learned policy/ranker over history/features | require temporal split and same observable information |

## Technique Families in Prior TCP Work

This taxonomy is useful when deciding which baselines belong in the same
experiment.

| Family | Examples | Primary Signal Used | Fair Comparison Requirement |
|---|---|---|---|
| Untreated/random controls | original order, random | none or benchmark-native order | same candidate tests, enough seeds |
| Coverage-count heuristics | total, additional | coverage/fault/mutant matrix | same matrix and same budget |
| Greedy cost-aware heuristics | shortest, cost-additional | matrix plus durations | verified duration source |
| Requirement/risk/value based | requirement priority, severity | requirements, business value, severity | same requirement/fault weights available to all methods |
| Similarity/diversity based | ART, FAST | distance/similarity over tests | same representation and distance protocol |
| Search-based | GA, ACO, PSO, multi-objective search | explicit objective/fitness | same objective, time budget, and repeated runs |
| History-based heuristics | recent failures, failure density, duration | previous build/test outcomes | strict temporal split |
| ML/ranking/RL | learning-to-rank, RL policies, deep models | historical features and labels | same training window, feature visibility, and retraining cadence |

ShapTCP should be compared first with coverage-count and cost-aware heuristics.
Similarity, search, and history/ML baselines are meaningful only after their
input representation is aligned with ShapTCP's matrix and protocol.

## Where ShapTCP Fits

ShapTCP does not directly optimize APFD. It optimizes a scarcity-aware coverage
surrogate at each step.

For each entity:

```text
T_f = {i in T : M[i, f] = 1}
```

The exact Shapley contribution in a weighted coverage game is:

```text
phi_i = sum_{f in F_i} w_f / |T_f|
```

ShapTCP then performs residual greedy prioritization:

```text
score_i(S) = sum_{f in F_i \ covered(S)} w_f / |T_f|
pi_t       = argmax_{i notin S} score_i(S)
```

Cost-aware ShapTCP uses:

```text
score_i(S) / c_i^alpha
```

where `alpha=0` is pure ShapTCP and `alpha=1` is score per unit cost.

This places ShapTCP between classic additional coverage and pure Shapley
attribution:

- compared with `additional`, ShapTCP discounts entities covered by many tests;
- compared with `static_shapley`, ShapTCP removes already covered entities
  during ordering;
- compared with APFD/APFDc, ShapTCP is a tractable surrogate whose sequence
  effectiveness must be evaluated empirically.

ShapTCP is not:

- a test-selection method;
- a learned failure predictor;
- an APFD optimizer;
- a dynamic-degree Shapley method;
- a CI-history method unless a valid history-to-entity adapter is added.

ShapTCP is:

- a deterministic matrix-based prioritizer;
- a scarcity-aware variant of residual/additional coverage;
- a cooperative-game attribution layer over weighted coverage;
- a low-cost method that can run without GPU or training data.

## Mathematical Properties We Can Defend

- The weighted coverage function is monotone submodular under deterministic
  binary coverage.
- The closed-form `sum_f w_f / |T_f|` is the exact Shapley value for this
  weighted coverage game.
- ShapTCP's step score is a residual weighted-coverage marginal gain using
  Shapley scarcity weights.
- Fixed weighted maximum coverage has the standard greedy subset guarantee.
- APFD/APFDc/NAPFD are evaluation metrics; ShapTCP does not inherit an APFD
  approximation guarantee.

## Modeling Pitfalls to Avoid

- Do not call coverage entities faults.
- Do not compare APFDc without the same real duration source.
- Do not mix full-suite APFD with partial-budget NAPFD without saying so.
- Do not let a baseline see future failures, post-cycle coverage, or a larger
  candidate test set.
- Do not describe CI failure signatures as root causes unless clustered or
  mapped to benchmark issue ids.
- Do not call ShapTCP a dynamic-degree Shapley method; deterministic residual
  faults keep their original covering-test degree.

## Paper-Safe Summary

```text
TCP is a permutation optimization problem over tests. Classic evaluation
maximizes early fault detection, commonly APFD/APFDc. ShapTCP optimizes a
tractable, monotone-submodular coverage surrogate: residual weighted coverage
where each entity is weighted by its exact Shapley scarcity contribution
1 / |T_f|. Therefore, its expected strengths are early rare-entity recall and
lower redundant early coverage; APFD/APFDc gains must be validated empirically
under benchmark-specific protocols.
```
