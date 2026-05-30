# FAST Source Notes

Status: source URL verified from the ICSE 2018 paper footnote; repository HEAD
verified by `git ls-remote` and shallow clone on 2026-05-29. C-subject fault
matrix conversion is implemented in `scripts/convert_fast_fault_matrix.py`.

## Verified Source

- Paper: Breno Miranda, Emilio Cruciani, Roberto Verdecchia, Antonia
  Bertolino, "FAST Approaches to Scalable Similarity-Based Test Case
  Prioritization", ICSE 2018.
- DOI: `10.1145/3180155.3180210`.
- Artifact URL from the paper footnote: https://github.com/icse18-fast/FAST
- Observed HEAD on 2026-05-29:
  `e6e8f287178963ac72d7cbb1c18b82b23ff84494`
- Observed temporary clone:
  `/private/tmp/shaptcp-audit-FAST2`
- Development-machine clone:
  `data/raw/FAST`

## Expected Use

FAST is the main similarity/diversity baseline family for ShapTCP's matrix
experiments. It should be used only after the artifact is cloned and its input
matrix schema is recorded.

Observed details:

- `input/*/fault_matrix.pickle` or `fault_matrix_key_tc.pickle` files are
  shipped alongside `*-line.txt`, `*-branch.txt`, `*-function.txt`, and
  `*-bbox.txt` representations.
- FAST fault-matrix schema differs by subject family: for C subjects,
  `fault_matrix_key_tc.pickle` is `test_id -> [detected fault ids]`; for Java
  subjects, `fault_matrix.pickle` is interpreted by `py/metric.py` as
  `version/bug id -> [faulty test ids]` and APFD is averaged/listed per buggy
  version. A ShapTCP loader must preserve that semantic split.
- `py/competitors.py` comments the white-box family as `GreedyTotal`,
  `GreedyAdditional`, `AdditionalSpanning`, `Jiang`, and `Zhou`.
- `GT` maps to Greedy Total, `GA` maps to Greedy Additional, and `GA-S` maps to
  Additional Spanning in the artifact scripts.
- `results/RQ1-RQ2-EffectivenessEfficiencyResults.tsv` contains `sig_time`,
  `prio_time`, `tot_time`, and `apfd`; these are artifact effectiveness and
  prioritization-time fields, not per-test execution durations.

## First Commands

```bash
git clone https://github.com/icse18-fast/FAST.git data/raw/FAST
export SHAPTCP_FAST_ROOT="$PWD/data/raw/FAST"

PYTHONPATH=src python3 scripts/convert_fast_fault_matrix.py \
  --fast-root "$SHAPTCP_FAST_ROOT" \
  --subject flex_v3 \
  --entity line \
  --output data/processed/fast/flex_v3_faults.txt

PYTHONPATH=src python3 scripts/run_benchmark_matrix.py \
  data/processed/fast/flex_v3_faults.txt \
  --test-ids data/processed/fast/flex_v3_faults.txt.tests \
  --fault-ids data/processed/fast/flex_v3_faults.txt.entities \
  --benchmark FAST \
  --subject flex_v3_faults \
  --semantics fault \
  --evidence-level pipeline_validation \
  --claim-scope fast_c_fault_matrix_core_baselines \
  --source-status source-audited \
  --matrix-status verified \
  --result-status local_smoke_only \
  --ground-truth-level true_fault \
  --duration-source not_available \
  --k 20 \
  --random-seeds 30
```

## Current Local Smoke Result

On 2026-05-30, the five C subjects `flex_v3`, `grep_v3`, `gzip_v1`,
`make_v1`, and `sed_v6` were converted with `entity=line` and evaluated against
local core baselines only (`total`, `additional`, `static_shapley`, `shaptcp`,
and random seeds). This is pipeline validation, not a SOTA claim.

Mean over the five C subjects:

| Method | APFD | Recall@20 | Redundancy@20 |
|---|---:|---:|---:|
| total | 0.953236 | 0.876984 | 0.890963 |
| additional | 0.997626 | 1.000000 | 0.874901 |
| static_shapley | 0.994715 | 1.000000 | 0.861297 |
| shaptcp | 0.997342 | 1.000000 | 0.611496 |

Interpretation: ShapTCP nearly matches additional coverage on APFD while
substantially reducing early duplicate fault hits. This supports the intended
scarcity/redundancy claim, but artifact-native FAST baselines still need to be
run before any strong comparative claim.

## Accuracy Gate

Before reporting FAST comparisons:

- record the artifact commit;
- identify the exact input matrix files;
- confirm whether artifact names such as `GA` mean Greedy Additional rather
  than genetic algorithm before writing baseline labels;
- document whether columns are faults, coverage entities, or black-box
  representations;
- do not use artifact prioritization runtime as per-test execution duration for
  APFDc;
- isolate the old Python/scipy/xxhash environment for artifact-native methods;
- do not mix FAST artifact results with ShapTCP results unless they use the
  same subject, candidate tests, and metric protocol.
