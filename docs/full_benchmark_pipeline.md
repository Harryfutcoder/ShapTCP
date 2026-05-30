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

Every reported table must also be traceable to the formal instance:

```text
(T, E, M, c, w, B, H, sigma, protocol)
```

At minimum, record the candidate test set `T`, entity semantics `sigma`, matrix
source `M`, budget `B`, duration source `c`, visible history `H`, and the exact
metric formula. If any of these are unclear, the output is a smoke run rather
than reportable evidence.

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
- `FAST`: C-subject fault-matrix loader is implemented; Java schema is
  documented but should be treated separately because it maps bug/version ids
  to triggering tests.
- `SIR`: use only after object package format and access/license constraints
  are recorded.

Find candidate dense matrices:

```bash
export SHAPTCP_OCP_ROOT=/path/to/OCP
PYTHONPATH=src python3 scripts/discover_matrices.py "$SHAPTCP_OCP_ROOT" --scan-zip
```

If a candidate matrix is inside a zip, extract only that confirmed member:

FAST C-subject fault-matrix smoke:

```bash
export SHAPTCP_FAST_ROOT="$PWD/data/raw/FAST"

PYTHONPATH=src python3 scripts/convert_fast_fault_matrix.py \
  --fast-root "$SHAPTCP_FAST_ROOT" \
  --subject flex_v3 \
  --entity line \
  --output data/processed/fast/flex_v3_faults.txt

mkdir -p outputs/fast-flex_v3-core

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
  --random-seeds 30 \
  > outputs/fast-flex_v3-core/results.csv
```

Repeat for `grep_v3`, `gzip_v1`, `make_v1`, and `sed_v6` before summarizing.
These runs compare only local core baselines; artifact-native FAST variants
remain a separate stronger-baseline stage.

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

Defects4J is not a ready-made matrix benchmark. Its bug ids are separate buggy
revisions, so trigger-test experiments must be framed as per-bug rank
aggregation or explicitly labeled cross-version adapter smoke.

Dry-run commands:

```bash
PYTHONPATH=src python3 scripts/build_defects4j_trigger_matrix.py \
  --defects4j-bin /path/to/defects4j \
  --project Lang \
  --bugs 1 3 4 \
  --work-dir data/work/defects4j \
  --candidate-property tests.all \
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
  --candidate-property tests.all \
  --output data/processed/defects4j/Lang_trigger_1_3_4.txt \
  --execute
```

The script writes:

```text
Lang_trigger_1_3_4.txt           # dense binary matrix
Lang_trigger_1_3_4.txt.tests     # row ids
Lang_trigger_1_3_4.txt.entities  # bug columns
Lang_trigger_1_3_4.txt.protocol.md
```

Do not use `tests.trigger` as the candidate universe for reportable runs. It is
only a trivial adapter smoke setting because all rows are already positive
triggering tests.

Run it:

```bash
PYTHONPATH=src python3 scripts/run_benchmark_matrix.py \
  data/processed/defects4j/Lang_trigger_1_3_4.txt \
  --benchmark defects4j \
  --subject Lang_1_3_4_trigger \
  --semantics bug \
  --evidence-level pipeline_validation \
  --claim-scope execution_trigger_adapter_smoke \
  --result-status local_smoke_only \
  --ground-truth-level true_bug_metadata \
  --k 10
```

The runner emits `nan` for APFD/APFDc unless the metadata marks the matrix as a
true fault matrix or an execution-derived bug matrix. Metadata-only Defects4J
smoke runs should therefore use recall/redundancy output only.

The cross-bug trigger matrix should remain smoke evidence. A paper result needs
a per-bug rank/TTFF/recall aggregator over each bug revision's candidate suite.

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

Do not add CI-history or learning baselines to a matrix table unless ShapTCP is
given the same temporal history/features and the same evaluation cycles. They
belong in a separate CI-history section by default.

## Stop Conditions

Stop and update source notes when:

- matrix columns cannot be identified;
- test ids do not match original candidate tests;
- costs/durations are reconstructed rather than benchmark-provided;
- CI-history data would use future information;
- a script requires mutation, large downloads, or long training on a laptop.
