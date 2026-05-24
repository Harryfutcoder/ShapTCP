# ShapTCP Roadmap

## Stage 0: Algorithm Sanity

Goal: prove the code matches the defensible theory.

- Exact Shapley scores for weighted coverage games.
- Shapley-weighted residual coverage ordering.
- Cost-aware ordering via `score / duration^alpha`.
- Time-budget and count-budget execution.
- Co-failure clustering for raw failure signature deduplication.
- Metrics: APFD, APFDc, recall@k, rare-fault recall@k, redundancy@k.

## Stage 1: Matrix Benchmarks

Goal: evaluate the core algorithm where the test-fault matrix is explicit.

Priority:

1. OCP, if the artifact exposes test/mutant/fault matrices cleanly.
2. Defects4J or SIR if we can construct `test -> bug/mutant` matrices.

Baselines for this stage:

- Random.
- Total coverage.
- Additional coverage.
- Cost-aware additional coverage.
- ShapTCP.
- Cost-aware ShapTCP.
- Lexicographic unique-fault ShapTCP as an ablation.

Metrics:

- APFD / APFDc.
- Fault recall under budget.
- Rare-fault recall@k.
- Redundancy@k.
- Time to first failure/fault.

## Stage 2: CI-History Benchmarks

Goal: move from explicit matrices to real CI logs.

Priority:

1. TCPFramework adapter.
2. RETECS / tp_rl failure-log adapters.
3. TCP-CI feature-rich experiments.

Key added work:

- Failure signature normalization.
- Co-failure/root-cause clustering.
- Censoring-aware treatment of unexecuted tests.
- Strict temporal train/test split.

## Stage 3: Learned Value TCP

This is a separate, later line inspired by Shapley context pruning.

Instead of exact matrix Shapley, learn a set value function:

```text
v_theta(S) -> expected fault-detection utility
```

Then estimate Shapley values by Monte Carlo permutations. This should only be
attempted after the exact matrix version is stable and after feature-rich data is
available.
