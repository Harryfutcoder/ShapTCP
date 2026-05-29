# SOTA Baselines and Benchmark Map

This document is the source-of-truth checklist for ShapTCP experiments. Every
baseline must be tied to a paper, code/artifact, data shape, and environment.
When a claim is inferred rather than directly verified from a paper or README,
it is marked as such.

## Accuracy Rules

- Do not call a method "SOTA" without naming the benchmark family where that
  claim is meaningful.
- Do not compare methods across CI-history, feature-rich CI, and coverage/fault
  matrix data unless the candidate test sets, splits, metrics, and observable
  features are aligned.
- Do not treat raw failure signatures as root-cause faults. CI-history adapters
  need clustering or a benchmark-provided bug/fault identifier.
- Do not treat Defects4J, SIR, OCP, RTPTorrent, or the Yaraghi dataset as the
  same benchmark type. They answer different experimental questions.

## Comparison Tiers

Not every published TCP method belongs in the same comparison table. Use this
tiering before adding a baseline.

| Tier | Methods | Same Table As ShapTCP? | Required Alignment |
|---|---|---|---|
| T0 controls | random, original order | yes | same candidate tests and metric |
| T1 matrix heuristics | total, additional, static Shapley, cost-aware variants | yes, main table | same matrix, same budget, same durations if cost-aware |
| T2 matrix SOTA families | FAST, ART, GA/search, OCP artifact methods | yes, after adapter audit | same representation and benchmark-native protocol |
| T3 generated real-bug matrices | Defects4J trigger/coverage/mutation | yes, separate Defects4J table | generated matrix protocol and entity semantics |
| T4 CI-history/combinators | TCPFramework, RETECS, tp_rl, DeepOrder, TCP-CI, AutoTCP | not first-paper main table | temporal split, same visible history/features, benchmark-native metrics |

If a method needs data ShapTCP does not receive, either give ShapTCP the same
data through an adapter or move the method to a separate experiment.

## Required Baseline Metadata

Every baseline row in a report should record:

```text
method name
paper anchor
implementation source or local implementation note
input representation
candidate test set
budget policy
metric formula
random seeds or deterministic tie-breaking
environment profile
known incompatibilities
```

This prevents a "baseline name" from hiding a different benchmark, different
candidate tests, or future information.

## Stage 1: Matrix Baselines

These are the first baselines to run against ShapTCP because they share the same
input abstraction: rows are tests, columns are faults, mutants, or coverage
entities.

| Baseline | Paper anchor | Code status in this repo | External artifact | Benchmark fit | Notes |
|---|---|---|---|---|---|
| Random | Standard control in TCP experiments | `random_order` | none needed | all matrix benchmarks | Use multiple seeds for reported results. |
| Total coverage | Rothermel, Untch, Chu, Harrold, "Prioritizing Test Cases for Regression Testing", IEEE TSE 2001; also derived from the 1999 empirical study | `total_coverage_order` | none needed | SIR/OCP/Defects4J matrix | Sorts by total covered entities. |
| Additional coverage | Rothermel et al., IEEE TSE 2001 | `additional_coverage_order` | none needed | SIR/OCP/Defects4J matrix | Greedy residual coverage; this is the closest non-Shapley comparator. |
| Cost-aware additional coverage | Cost-cognizant TCP literature; APFDc-style experiments commonly use duration-aware variants | `cost_aware_additional_coverage_order` | none needed | benchmarks with durations | This is a pragmatic baseline, not a claim of a single canonical algorithm. |
| Shortest duration first | Common CI/resource baseline | `shortest_duration_order` | none needed | benchmarks with durations | Useful for APFDc and time-budget sanity checks. |
| ART / adaptive random prioritization | Jiang, Zhang, Chan line of ART-based TCP; OCP paper compares against `art-based` | not yet implemented | OCP `code/ComparingTechniques/ARTMaxMin.java` | OCP-style coverage matrix | Add after OCP raw matrix mapping is confirmed. |
| Genetic/search-based | Li, Harman, Hierons, "Search algorithms for regression test case prioritization", IEEE TSE 2007; OCP paper compares against `search-based` | not yet implemented | OCP `code/ComparingTechniques/Genetic.java` or a separately implemented baseline | OCP-style coverage matrix | Use as external wrapper before reimplementing; do not confuse this with FAST `GA`. |
| Lexicographical/unify greedy | Zhang, Hao, Zhang, Rothermel, "A unified test case prioritization approach", ESEC/FSE 2013 | not yet implemented | OCP `UnifyGreedy.java` and `FICBPL_E.java` | OCP-style coverage matrix | Useful only after exact OCP input format is confirmed. |
| OCP | Zhang, Fang, Sun, Yu, Xu, Liu, "Test case prioritization using partial attention", JSS 2022, volume 192 article 111419 | not yet implemented | `QuanjunZhang/OCP` | OCP artifact: 19 Java program versions + 30 C program versions | OCP is a strong coverage/mutation artifact; raw `test -> mutant/fault` matrix path still needs confirmation. |
| FAST similarity | Miranda, Cruciani, Verdecchia, Bertolino, "FAST Approaches to Scalable Similarity-Based Test Case Prioritization", ICSE 2018 | not yet implemented | `icse18-fast/FAST` | FAST subjects include flex, grep, gzip, make, sed, chart, closure, lang, math, time | Important similarity/diversity comparator; paper footnote points to `https://github.com/icse18-fast/FAST`; repo includes input data/tools but uses old dependencies such as `scipy==0.19.1`; write a pickle/input loader and confirm matrix direction before use. |
| ART-F / ART-D | Jiang, Zhang, Chan, Tse, "Adaptive random test case prioritization", ASE 2009 | not yet implemented | `icse18-FAST/FAST` has artifact variants; OCP also compares ART-style baseline | FAST/OCP-style matrices | Do not claim original Jiang 2009 official implementation unless separately verified. |
| FAST `GA` / Greedy Additional | FAST artifact naming for the coverage greedy family (`GT`, `GA`, `GA-S`) | not yet implemented | `icse18-fast/FAST` | FAST matrices | In FAST, `GA` should be treated as Greedy Additional, not genetic algorithm. |
| GA / search-based TCP | Li, Harman, Hierons, "Search Algorithms for Regression Test Case Prioritization", IEEE TSE 2007 | not yet implemented | OCP artifact or our own implementation after objective alignment | OCP-style matrices | Useful strong non-RL comparator; artifact implementation may not be the original authors' code. |

## Stage 2: CI-History Baselines

These methods use CI cycles, execution history, previous failures, and feedback.
They are not direct matrix baselines.

| Baseline | Paper anchor | Repository | Data | Environment | ShapTCP role |
|---|---|---|---|---|---|
| RETECS | Spieker, Gotlieb, Marijan, Mossige, "Reinforcement Learning for Automatic Test Case Prioritization and Selection in Continuous Integration", ISSTA 2017, DOI `10.1145/3092703.3092709` | `mregorova/RETECS`; original paper footnote points to `bitbucket.org/helges/atcs-data` | ABB Paint Control: 114 tests / 312 cycles; IOF/ROL: 2086 tests / 320 cycles; GSDTSR: 5555 tests / 336 cycles | old Python stack; README uses Python 2 style virtualenv; Docker route preferred | Classic RL-TCP baseline after CI-history adapter exists. |
| tp_rl pointwise/pairwise/listwise RL | Bagherzadeh, Kahani, Briand, "Reinforcement Learning for Test Case Prioritization", IEEE TSE 2021, DOI `10.1109/TSE.2021.3070549` | `moji1/tp_rl` | 8 datasets including Paint-Control, IOFROL, and Apache Commons enriched data | Python 3.7, Stable Baselines 2.10; entry `TPDRL.py` covers pointwise/pairwise/listwise and A2C/ACER/ACKTR/DQN/PPO/TRPO | Strong RL formulation benchmark; pairwise-ACER should be described as paper/survey-reported strong configuration, not universal SOTA. |
| DeepOrder | Sharif, Marijan, Liaaen, "DeepOrder: Deep Learning for Test Case Prioritization in Continuous Integration Testing", ICSME 2021 | `T3AS/DeepOrder-ICSME21` | Google Drive data referenced by README; scripts cover Cisco, IOF/ROL, Paint Control, GSDTSR | reported Python 3.6 / TensorFlow 2.1 / Keras 2.2 / SMOGN; Git LFS/data/version provenance must be verified before comparison | Deep learning CI baseline; only compare after dataset/split/metric alignment. |
| TCPFramework combinators | Chojnacki and Madeyski TCPFramework repository and associated article | `LechMadeyski/MSc25TomaszChojnacki` | RTPTorrent + TravisTorrent; 11 selected Java repos | Python >= 3.13, `uv`; generated dataset is not shipped | Best second-stage framework for history/combinator comparison; pin exact article/DOI before venue claims. |
| TCP-CI RankLib RF/all rankers | Yaraghi, Bagherzadeh, Kahani, Briand, "Scalable and Accurate Test Case Prioritization in Continuous Integration Contexts", IEEE TSE 2022, DOI `10.1109/TSE.2022.3184842` | `Ahmadreza-SY/TCP-CI` | 25 Java projects, Zenodo `10.5281/zenodo.6415365`; paper/repository describe thousands of CI builds and failed builds | Python 3.7+, Understand Build 1029 on Linux, manual Understand Python API, Java OpenJDK 1.8/11, RankLib; README requirements include pandas/numpy/scikit-learn/xgboost/PyDriller versions | Feature-rich CI comparator and source for future risk-aware ShapTCP. |
| AutoTCP | Romero, Ramirez, Garcia-Martinez, "Automated machine learning for test case prioritisation", Empirical Software Engineering 2026, volume 31 article 120 | official supplementary Zenodo DOI `10.5281/zenodo.19099729`; GitHub mirror `humains-lab/2026-AutoTCP` | same Yaraghi 25-project dataset | README gives `cd code && pip install -r requirements.txt`, then dataset preprocessing and `run_experiments.py`; actual cloned requirement paths must be checked before running | Feature-rich CI comparator; not universally best per project, report per-project and aggregate results. |
| ML-based TSP SLR | Pan, Bagherzadeh, Ghaleb, Briand, "Test case selection and prioritization using machine learning: a systematic literature review", EMSE 2022, DOI `10.1007/s10664-021-10066-6` | `uOttawa-Nanda-Lab/ML-based-TSP-SLR` | SLR replication artifacts, not an executable TCP baseline | no runner | Use for taxonomy and reproducibility discussion, not as a runnable baseline. |

## Benchmarks

| Benchmark | Type | Source | Direct data shape | Setup status | First useful ShapTCP task |
|---|---|---|---|---|---|
| SIR | matrix/generated fault benchmark | Software-artifact Infrastructure Repository; the EMSE SIR paper describes tooling including `gen-fault-matrix` | object-dependent tar/gz packages; small subjects may expose or generate fault matrices | requires license/download and object-specific inspection; exact package structure still unverified locally | inspect Siemens/tcas/schedule/print_tokens packages for ready matrix files or scripts. |
| OCP | coverage/mutation artifact | `QuanjunZhang/OCP`, JSS 2022 artifact | code, subjects, tests, C mutants, upstream APFD/order/prioritization-time result files; Java prioritizers read coverage matrix files | public artifact inspected through README/code; raw matrix mapping not yet confirmed | adapt row-wise coverage matrix if available, then compare ShapTCP with OCP baselines. Upstream `APFD` filenames are artifact-native coverage/ordering outputs, not automatically true fault APFD. |
| FAST | similarity/diversity artifact | `icse18-fast/FAST`, ICSE 2018 artifact | input data includes fault matrix, coverage information, and black-box representation for listed subjects | needs old Python/scipy environment | use as second Stage-1 comparator for similarity/diversity, ART, and FAST greedy baselines; FAST `GA` means Greedy Additional. |
| Defects4J | generated real-bug benchmark | `rjust/defects4j` | real Java bugs plus tooling, not a direct matrix | needs Java 11, Git, svn, Perl, cpanm, timezone `America/Los_Angeles` | start with small projects and export `tests.trigger`; mutation matrix later. |
| RTPTorrent/TCPFramework | CI-history benchmark | RTPTorrent Zenodo + TravisTorrent + TCPFramework | CI execution records and project repos | generated dataset >6GB and not shipped | second-stage CI-history adapter. |
| Yaraghi 25-project TCP-CI | feature-rich CI benchmark | Zenodo `10.5281/zenodo.6415365` | feature-rich CI dataset; main dataset is about 237MB and full dataset is about 16GB | requires dataset download; TCP-CI extraction additionally needs Understand | later risk-aware ShapTCP and learning-to-rank baselines. |
| RETECS/tp_rl datasets | RL CI-history benchmark | bundled in their repositories | CI cycles with history features | old Python/RL environments | later RL comparison. |

Benchmark acceptance rule:

- `matrix/generated fault benchmark`: eligible for the first ShapTCP paper after
  semantics verification.
- `coverage/mutation artifact`: eligible, but claims must say coverage or
  mutation proxy unless true faults are verified.
- `CI-history benchmark`: second-stage; requires temporal protocol.
- Artifact prioritization runtime files are not per-test execution durations and
  are ineligible for APFDc unless independently mapped to test execution cost.
- `feature-rich CI benchmark`: not comparable to matrix ShapTCP until feature
  visibility and training protocol are aligned.

## Minimum First Experiment

The first real experiment should be intentionally small:

1. Load one confirmed row-wise binary matrix with `load_binary_incidence_matrix`.
2. Run `random`, `total`, `additional`, `cost-aware additional`, `shortest duration`, `ShapTCP`, and `cost-aware ShapTCP`.
3. Report APFD only for verified fault/bug matrices, APFDc only when verified
   durations exist, and otherwise report semantic-aware recall@k,
   rare_recall@k, redundancy@k, and runtime.
4. Do not claim SOTA from this smoke test. Use it to validate data plumbing and metric direction.

## Developer Machine Notes

The current ShapTCP core does not need a large machine. The expensive parts are
benchmark reconstruction and external baselines:

| Task | Minimum practical environment | Why |
|---|---|---|
| ShapTCP core + small matrix smoke tests | normal laptop, Python >= 3.10 | current tests and 1000x2000 synthetic matrix run in under a second. |
| SIR small subjects | Linux shell preferred; old C/Java toolchain may be needed per object | object packages and scripts vary by subject. |
| OCP artifact inspection | normal laptop for reading existing data; Java/C toolchain for reruns | existing results are easy to inspect, raw matrix reconstruction may be heavier. |
| Defects4J | Java 11, Git, svn, Perl, cpanm, `TZ=America/Los_Angeles` | current local Java 25 is not suitable; mutation is CPU/disk heavy. |
| TCPFramework / RTPTorrent | Python >= 3.13, `uv`, large disk/network budget | RTPTorrent zip is about 5GB and generated dataset is over 6GB. |
| TCP-CI / Yaraghi | Java 8/11, Python 3.7+, RankLib, Understand Build 1029 or compatible | Understand is not a pip dependency; full dataset is large. |
| RETECS / tp_rl / DeepOrder | separate old conda/Docker envs | Python 2-era sklearn, Stable-Baselines 2, and TensorFlow 2.1 stacks should not be mixed into ShapTCP. |
| FAST artifact | old Python environment, likely Python 2/early Python 3 with `scipy==0.19.1` and `xxhash==1.0.1` | keep isolated from ShapTCP's modern no-dependency core. |

## Sources To Recheck Before Paper Submission

- Rothermel et al., "Prioritizing Test Cases for Regression Testing", IEEE TSE 2001.
- Elbaum, Malishevsky, Rothermel, "Test Case Prioritization: A Family of Empirical Studies", IEEE TSE 2002.
- Li, Harman, Hierons, "Search Algorithms for Regression Test Case Prioritization", IEEE TSE 2007.
- Zhang et al., "A Unified Test Case Prioritization Approach", ESEC/FSE 2013.
- Miranda et al., "FAST Approaches to Scalable Similarity-based Test Case Prioritization", ICSE 2018.
- Zhang et al., "Test Case Prioritization Using Partial Attention", JSS 2022.
- Jiang et al., "Adaptive Random Test Case Prioritization", ASE 2009.
- Spieker et al., "Reinforcement Learning for Automatic Test Case Prioritization and Selection in Continuous Integration", ISSTA 2017.
- Bagherzadeh et al., "Reinforcement Learning for Test Case Prioritization", IEEE TSE 2021.
- Yaraghi et al., "Scalable and Accurate Test Case Prioritization in Continuous Integration Contexts", IEEE TSE 2022.
- Chojnacki and Madeyski, "Test Case Prioritization: A Snowballing Literature Review and TCPFramework with Approach Combinators", 2026.
