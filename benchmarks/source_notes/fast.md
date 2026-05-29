# FAST Source Notes

Status: source URL verified from the ICSE 2018 paper footnote; repository HEAD
verified by `git ls-remote` and shallow clone on 2026-05-29.

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
PYTHONPATH=src python3 scripts/discover_matrices.py "$SHAPTCP_FAST_ROOT" --scan-zip
```

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
