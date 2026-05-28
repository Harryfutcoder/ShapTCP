# Theory Review Notes

This document is the compressed reviewer-facing version of the ShapTCP and
future GuardTCP theory audit. It records the claims we can defend, the claims
we should avoid, and how the current code maps to the corrected theory.

## Current ShapTCP Position

ShapTCP should be described as:

```text
exact static Shapley scarcity weights + residual/additional coverage greedy
```

This position is aligned with the classic TCP formulation in which a
prioritizer searches over permutations of a test suite to maximize a chosen
performance function. In our paper, APFD/APFDc are evaluation functions over
the final permutation, while ShapTCP's optimized surrogate is residual
Shapley-weighted coverage.

For a test-to-entity matrix `F_i`, with `T_f = {i : f in F_i}`, the exact
coverage-game Shapley contribution is:

```text
phi_i = sum_{f in F_i} weight_f / |T_f|
```

The implemented ordering is:

```text
score_i(S) = sum_{f in F_i and f not in covered(S)} weight_f / |T_f|
```

This is intentionally conservative. It uses fixed Shapley scarcity weights and
a residual coverage filter. It does not claim a dynamic-degree Shapley theorem
or an APFD approximation guarantee.

Assumptions for this theory statement:

- deterministic binary coverage/detection matrix;
- non-negative entity weights;
- fixed candidate test set;
- entity semantics documented before evaluation;
- no current/future-cycle information in history-based settings.

## Paper 1 Audit: Dynamic Degree Collapse

The risky formulation is a "dynamic conditional Shapley" degree:

```text
d_f(S) = number of remaining tests that can still cover f
```

In deterministic coverage, if `f` is still residual, then no selected test has
covered it. Therefore all original tests that cover `f` are still unselected,
and `d_f(S)` remains `|T_f|`. The degree does not shrink dynamically.

The corrected method is Shapley-weighted residual coverage:

- compute fixed scarcity weights `1 / |T_f|`;
- greedily select newly covered residual entities under those weights;
- use `static_shapley_order` only as an ablation;
- use `shaptcp_order` as the main method.

The code currently reflects this correction:

- `static_shapley_scores` computes the exact fixed Shapley weights;
- `static_shapley_order` isolates pure static attribution;
- `shaptcp_order` performs residual/additional scheduling;
- `lexicographic_unique=True` is an ablation or policy variant, not a theorem
  about APFD.

Defensible theory language:

- coverage is monotone submodular;
- greedy has the standard guarantee for fixed weighted coverage subset
  objectives;
- TCP's classic APFD objective is a sequence-level first-detection objective,
  whereas ShapTCP optimizes a prefix coverage surrogate;
- APFD/APFDc improvements are empirical claims;
- unique-entity priority is a deterministic policy property only when the
  lexicographic variant is enabled.

Avoid:

- "dynamic Shapley degree";
- "convex game" or "core non-empty" language for the coverage game;
- APFD approximation guarantees.

## Shared Audit: Fault Explosion

Raw CI failure signatures are not true faults. One root cause can produce many
assertions, stack traces, or failing tests. Treating every signature as an
independent `f` inflates verbose bugs and contaminates Shapley weights.

The required engineering layer is root-cause proxy construction:

- prefer benchmark-provided bug ids, mutant ids, or fault ids when available;
- otherwise cluster failure signatures by co-failing test sets;
- report results separately for raw signatures and clustered proxies when
  using CI logs.

The current repository includes the first deterministic baseline for this:

- `cluster_faults_by_cofailure` uses Jaccard similarity over failing-test sets;
- `apply_fault_clusters` rewrites raw signature matrices into clustered
  root-cause proxy matrices.

This clustering is not a substitute for real ground truth when a benchmark
provides it. It is a CI-log adapter decision that must be documented per
benchmark.

## Paper 2 Audit: GuardTCP / MinMax Projection Gap

The non-cooperative idea should be named GuardTCP in project notes:

```text
GuardTCP: distributionally robust TCP via adversarial fault games
```

It is not implemented in the current ShapTCP codebase yet. The defensible
future formulation is:

- Scheduler chooses a subset or a distribution over subsets.
- Nature chooses a fault/entity distribution in a KL ball around a smoothed
  empirical prior.
- Scheduler best response is weighted maximum coverage, approximated by
  greedy.
- Nature best response is KL-constrained convex optimization with a Gibbs-form
  solution, not a linear program.

The key mathematical boundary:

- the mixed strategy can inherit the robust coverage guarantee under the
  original assumptions;
- deterministic sorting by marginal probabilities is a heuristic projection;
- top-m truncation of marginals does not preserve the mixed-strategy guarantee
  in general.

Future implementation notes:

- smooth the empirical fault prior so unseen but plausible regions have
  non-zero support;
- tune the KL radius with an adaptive epsilon scheduler based on churn,
  recent-history divergence, and new-test ratio;
- record deterministic marginal sorting as an engineering projection;
- mention dependent or pipage rounding only as a theoretical alternative unless
  implemented and evaluated.

## Reviewer Defense Table

| Risk | Compressed Fix | Code/Doc Status |
|---|---|---|
| Dynamic degree collapse | fixed `1 / |T_f|` Shapley weights plus residual coverage | implemented in `shaptcp_order` |
| Static attribution confused with ordering | add `static_shapley_order` as ablation | implemented and tested |
| APFD guarantee overclaim | APFD/APFDc are empirical metrics only | documented in README and plan |
| Fault explosion | co-failure clustering or benchmark ground truth ids | clustering utilities implemented |
| Coverage game terminology | monotone submodular coverage, not convex game | documented here |
| MinMax truncation gap | marginal sorting is heuristic projection | future GuardTCP note only |
| KL zero-support issue | smooth empirical prior before KL game | future GuardTCP note only |

## Paper Wording

Recommended concise method sentence:

> ShapTCP uses exact Shapley values of a weighted coverage game as fixed
> scarcity weights, then applies residual greedy prioritization to surface
> scarce, non-redundant entities early in the sequence.

Recommended limitation sentence:

> We do not claim an approximation guarantee for APFD or for deterministic
> projections of future adversarial mixed strategies; these are evaluated
> empirically under benchmark-specific protocols.
