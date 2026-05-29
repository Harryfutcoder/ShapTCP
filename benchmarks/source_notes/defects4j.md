# Defects4J Source Notes

Status: tool audited, matrix generation required. Repository HEAD verified by
`git ls-remote` on 2026-05-29.

## Verified Local Source

- Artifact URL: https://github.com/rjust/defects4j
- Previously observed local root: `/private/tmp/defects4j` (not retained in the
  current temp workspace)
- Previously observed local version from README: `3.0.1`
- Observed repository HEAD during 2026-05-29 audit:
  `8c16da8230843cdc918eaf4ddb449637f02b83c6`
- Observed files include `framework/bin/defects4j`, `Dockerfile`,
  `docker-compose.yml`, framework modules for coverage and mutation, and
  project metadata under `framework/projects`.

## Matrix Position

Defects4J is not a ready-made matrix benchmark. Each bug id is a separate
buggy revision, so columns over multiple bug ids should not be described as
simultaneous faults in one program version. ShapTCP must generate data from a
selected protocol:

- per-bug trigger rank: rows are the candidate tests for one buggy revision,
  positives come from `tests.trigger`;
- cross-bug trigger matrix: rows are the union of candidate tests across buggy
  revisions and columns are bug ids; this is adapter smoke or per-bug rank
  aggregation input, not a standard multi-fault TCP instance;
- coverage matrix: rows are tests, columns are coverage entities;
- mutation matrix: rows are tests, columns are mutants.

The trigger matrix is the first development-machine target because it is much
lighter than coverage or mutation.

## Laptop-Safe Metadata Matrix

If Defects4J metadata is present, build a trigger matrix without checkout:

```bash
PYTHONPATH=src python3 scripts/build_defects4j_metadata_matrix.py \
  --defects4j-root /private/tmp/defects4j \
  --project Lang \
  --bugs 1 3 4 \
  --output data/processed/defects4j/Lang_metadata_trigger_1_3_4.txt
```

This is metadata-derived and should be labeled as `pipeline_validation`, not as
an execution-derived benchmark result. It uses triggering tests only as rows,
so it is not a fair candidate test universe for APFD or SOTA claims.

Observed local smoke result:

```text
tests=3, bugs=3
```

All methods tie on this tiny matrix, so it only validates adapter plumbing.

## Current Laptop Limitation

The current Mac audit environment has Java 25, while Defects4J requires Java
11. `svn` and `cpanm` were also not available during the audit. Therefore
checkout/export, coverage, and mutation should be run on the development
machine or a configured Docker/Linux environment.

## Development-Machine Command

```bash
PYTHONPATH=src python3 scripts/build_defects4j_trigger_matrix.py \
  --defects4j-bin /path/to/defects4j/framework/bin/defects4j \
  --project Lang \
  --bugs 1 3 4 \
  --work-dir data/work/defects4j \
  --candidate-property tests.all \
  --output data/processed/defects4j/Lang_trigger_1_3_4.txt \
  --execute
```

Expected outputs:

- `Lang_trigger_1_3_4.txt`: dense binary matrix;
- `Lang_trigger_1_3_4.txt.tests`: row/test ids;
- `Lang_trigger_1_3_4.txt.entities`: bug columns.
- `Lang_trigger_1_3_4.txt.protocol.md`: candidate-universe and cross-version
  warning.

## Accuracy Gate

Before reporting Defects4J results:

- record Defects4J commit/version;
- record Java, Perl, svn, cpanm, and timezone configuration;
- preserve exact bug ids and test ids;
- record whether the candidate universe is `tests.all`, `tests.relevant`, or a
  project-specific executable suite;
- never use only `tests.trigger` as the reportable candidate universe;
- use active bugs unless deprecated bugs are explicitly justified;
- distinguish metadata-derived trigger matrices from execution-derived trigger,
  coverage, or mutation results;
- do not run mutation on a laptop-scale environment.
