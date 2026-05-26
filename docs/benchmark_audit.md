# Benchmark Audit

This file is the conservative execution map for ShapTCP experiments. It
separates what is already verified from what still needs local reproduction.
Artifact availability is not the same as ShapTCP benchmark evidence.

## Current Verified Status

ShapTCP core is lightweight. On a synthetic sparse matrix with 1000 tests, 2000
faults, and a top-100 budget, the pure Python ordering path runs in roughly a
few tenths of a second on the current laptop. The heavy work is not the core
algorithm; it is dataset reconstruction and baseline training.

## Stage-1 Matrix Candidates

| Candidate | Verified facts | ShapTCP fit | Risk |
|---|---|---|---|
| SIR | Public artifact repository for testing and analysis materials. Some public pages and the EMSE SIR paper mention fault-matrix tooling, including `gen-fault-matrix`, but concrete object package formats still need download-time verification. | Best theoretical fit if small subjects expose or generate `test -> fault` or `test -> coverage entity` matrices. | License/download friction, old build scripts, object-specific formats. |
| OCP | Repository includes code, experimental data, subject programs/test suites, mutants, upstream APFD results, prioritization time, and prioritized orders. Java prioritizers read coverage-matrix files. | Good public artifact candidate for coverage-matrix experiments. Do not assume a ready `test -> mutant/fault` matrix until raw files are confirmed. Existing APFD tables are upstream artifact results, not ShapTCP results. | Local clone is large enough to inspect, but raw matrix mapping needs work. |
| Defects4J | Reproducible Java bugs and infrastructure with `coverage`, `mutation`, `export`, and `query`; currently requires Java 11. | Strong later benchmark, especially with small projects first. | Not a direct matrix dataset; mutation extraction is CPU/disk heavy. |

## Stage-2 CI/ML Candidates

| Candidate | Verified facts | ShapTCP role | Risk |
|---|---|---|---|
| TCPFramework | Requires RTPTorrent/TravisTorrent data reconstruction and 11 Java repo checkouts; data is not shipped with the repository. | CI-history/combinator comparison after matrix ShapTCP is stable. | More than 6GB generated data and many files. |
| TCP-CI | TSE 2022 supplement using a 25-project Java dataset; needs Understand, RankLib, Java, and Python dependencies. | Risk-aware ShapTCP feature source and learning-to-rank comparator. | Understand is not a normal pip dependency. |
| AutoTCP | Uses the Yaraghi 25-project dataset and grammar-guided AutoML. | Feature-rich CI comparator, not a first core benchmark. | Multi-seed AutoML search can be long. |
| RETECS / tp_rl / DeepOrder | RL and deep CI-TCP baselines with older Python/TensorFlow/Stable-Baselines stacks. | Cross-family baselines after data alignment. | Old dependencies and metric/split alignment. |

## Recommended First Experiments

1. Verify whether SIR small subjects expose usable matrices.
2. Build a minimal matrix loader for row-wise `0/1` coverage matrices.
3. Run ShapTCP, cost-aware ShapTCP, random, total coverage, and additional
   coverage on one confirmed small subject.
4. Report APFD, APFDc if durations exist, recall@k, rare-fault recall@k, and
   redundancy@k.
5. Only after this passes, add OCP-specific and Defects4J-specific adapters.

See [sota_baselines.md](sota_baselines.md) for the paper-to-code baseline map.

## Development Machine Guidance

A normal laptop is enough for ShapTCP core and small matrix artifacts. A larger
Linux or Docker-based machine becomes useful for Defects4J mutation,
TCPFramework data reconstruction, TCP-CI Understand processing, AutoTCP search,
and multi-seed RL baselines.

## Source Links

- SIR: https://sir.csc.ncsu.edu/php/index.php
- OCP: https://github.com/QuanjunZhang/OCP
- Defects4J: https://github.com/rjust/defects4j
- TCPFramework: https://github.com/LechMadeyski/MSc25TomaszChojnacki
- TCP-CI: https://github.com/Ahmadreza-SY/TCP-CI
- AutoTCP: https://github.com/humains-lab/2026-AutoTCP
- RETECS: https://github.com/mregorova/RETECS
- tp_rl: https://github.com/moji1/tp_rl
- DeepOrder: https://github.com/T3AS/DeepOrder-ICSME21
