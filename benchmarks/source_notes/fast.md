# FAST Source Notes

Status: source URL verified from the ICSE 2018 paper footnote, local source not
yet cloned in this workspace.

## Verified Source

- Paper: Breno Miranda, Emilio Cruciani, Roberto Verdecchia, Antonia
  Bertolino, "FAST Approaches to Scalable Similarity-Based Test Case
  Prioritization", ICSE 2018.
- DOI: `10.1145/3180155.3180210`.
- Artifact URL from the paper footnote: https://github.com/icse18-fast/FAST

## Expected Use

FAST is the main similarity/diversity baseline family for ShapTCP's matrix
experiments. It should be used only after the artifact is cloned and its input
matrix schema is recorded.

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
- document whether columns are faults, coverage entities, or black-box
  representations;
- isolate the old Python/scipy/xxhash environment for artifact-native methods;
- do not mix FAST artifact results with ShapTCP results unless they use the
  same subject, candidate tests, and metric protocol.
