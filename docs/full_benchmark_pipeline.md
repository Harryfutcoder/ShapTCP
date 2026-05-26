# Full Benchmark Pipeline

This document is the development-machine execution plan for ShapTCP benchmark
integration. It is deliberately manifest-driven: every dataset must have a
source note, an adapter path, and a documented matrix meaning before any
performance claim.

## Principle

The repository should support two modes:

- `audit mode`: safe on a laptop; checks paths, schemas, and commands.
- `execution mode`: development-machine only; downloads data, generates
  matrices, runs heavier baselines, and writes result tables.

Do not commit raw datasets or generated outputs. `data/` and `outputs/` are
ignored by git.

Every reported table must carry:

- `evidence_level`;
- `claim_scope`;
- `source_status`;
- `matrix_status`;
- `result_status`;
- verified column semantics.

## Manifest

Benchmark source metadata lives in:

```text
benchmarks/manifest.json
```

Each entry records:

- artifact URL;
- local root environment variable;
- fallback local path;
- adapter script;
- matrix semantics;
- source, matrix, and result status;
- evidence level;
- heavy steps;
- accuracy gate.

Run the audit:

```bash
PYTHONPATH=src python3 scripts/audit_benchmarks.py
```

Use JSON output for CI or automation:

```bash
PYTHONPATH=src python3 scripts/audit_benchmarks.py --json
```

## Stage A: Matrix Artifacts

Target benchmarks:

- `OCP`: artifact already includes code, subject packages, result tables, and
  Java prioritizers that read dense coverage matrices.
- `FAST`: source must be re-verified before paper use; use the same matrix
  discovery path after download.
- `SIR`: use only after object package format and access/license constraints
  are recorded.

Find candidate dense matrices:

```bash
export SHAPTCP_OCP_ROOT=/path/to/OCP
PYTHONPATH=src python3 scripts/discover_matrices.py "$SHAPTCP_OCP_ROOT" --scan-zip
```

If a candidate matrix is inside a zip, extract only that confirmed member:

```bash
PYTHONPATH=src python3 scripts/extract_zip_member.py \
  /path/to/artifact.zip path/inside/archive.txt data/processed/benchmark/matrix.txt
```

Before reporting any result, copy:

```text
benchmarks/SOURCE_NOTES_TEMPLATE.md
```

into a benchmark-specific note and fill in row/column semantics. For example,
state whether columns are statements, branches, methods, mutants, true faults,
or failure-signature proxies.

Run a confirmed matrix:

```bash
PYTHONPATH=src python3 scripts/run_benchmark_matrix.py \
  path/to/matrix.txt \
  --benchmark ocp \
  --subject gnu_flex_v1_statement \
  --semantics statement \
  --k 20
```

The runner refuses `--semantics unverified` unless `--allow-unverified` is
passed. Use `--allow-unverified` only for plumbing checks, never for reported
results.

If sidecar files exist next to the matrix, they are loaded automatically:

```text
matrix.txt.tests
matrix.txt.entities
```

You can also pass them explicitly:

```bash
PYTHONPATH=src python3 scripts/run_benchmark_matrix.py matrix.txt \
  --test-ids matrix.tests \
  --fault-ids matrix.entities
```

## Stage B: Defects4J Trigger Matrix

Defects4J is not a ready-made matrix benchmark. Start with a small trigger-test
matrix before any coverage or mutation experiment.

Dry-run commands:

```bash
PYTHONPATH=src python3 scripts/build_defects4j_trigger_matrix.py \
  --defects4j-bin /path/to/defects4j \
  --project Lang \
  --bugs 1 3 4 \
  --work-dir data/work/defects4j \
  --output data/processed/defects4j/Lang_trigger_1_3_4.txt
```

If Defects4J metadata is already present, a laptop-safe adapter smoke test can
build a metadata-derived trigger matrix without checkout:

```bash
PYTHONPATH=src python3 scripts/build_defects4j_metadata_matrix.py \
  --defects4j-root /path/to/defects4j \
  --project Lang \
  --bugs 1 3 4 \
  --output data/processed/defects4j/Lang_metadata_trigger_1_3_4.txt
```

Label this as `pipeline_validation`, not execution-derived evidence.

Execute on a configured development machine:

```bash
PYTHONPATH=src python3 scripts/build_defects4j_trigger_matrix.py \
  --defects4j-bin /path/to/defects4j \
  --project Lang \
  --bugs 1 3 4 \
  --work-dir data/work/defects4j \
  --output data/processed/defects4j/Lang_trigger_1_3_4.txt \
  --execute
```

The script writes:

```text
Lang_trigger_1_3_4.txt           # dense binary matrix
Lang_trigger_1_3_4.txt.tests     # row ids
Lang_trigger_1_3_4.txt.entities  # bug columns
```

Run it:

```bash
PYTHONPATH=src python3 scripts/run_benchmark_matrix.py \
  data/processed/defects4j/Lang_trigger_1_3_4.txt \
  --benchmark defects4j \
  --subject Lang_1_3_4_trigger \
  --semantics bug \
  --k 10
```

Only after this works should we consider heavier Defects4J coverage or mutation
matrices.

## Stage C: CI-History Benchmarks

TCPFramework / RTPTorrent is second-stage work. It should not be mixed with
matrix benchmark claims until the adapter is explicit about temporal splits and
failure proxies.

Required before implementation:

- RTPTorrent package root;
- TravisTorrent metadata root;
- project checkout cache;
- exact TCPFramework commit;
- decision on failure clustering protocol.

ShapTCP should either:

- implement a TCPFramework `Approach`; or
- export per-cycle orders and evaluate with TCPFramework metrics.

The second path is safer for first integration because it keeps ShapTCP code
independent while preserving the framework's metric protocol.

## Baseline Scope

Always include these first-stage baselines:

- `random`, with at least 30 seeds;
- `total coverage`;
- `additional coverage`;
- `static_shapley`, as an ablation;
- `shaptcp`;
- cost-aware variants only when durations are verified.

Artifact-native baselines such as OCP, FAST variants, ART, GA, and search-based
methods should be added only after the artifact's original matrix and metric
protocol are confirmed.

## Stop Conditions

Stop and update source notes when:

- matrix columns cannot be identified;
- test ids do not match original candidate tests;
- costs/durations are reconstructed rather than benchmark-provided;
- CI-history data would use future information;
- a script requires mutation, large downloads, or long training on a laptop.
