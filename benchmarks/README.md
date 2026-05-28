# Benchmark Pipeline

This directory stores the benchmark manifest and source notes for development
machine experiments. It does not store large datasets.

## Layout

```text
benchmarks/
  manifest.json              # benchmark source and adapter registry
  SOURCE_NOTES_TEMPLATE.md   # copy per benchmark after download/audit
  RUN_RECORD_TEMPLATE.md     # copy per reported run
  run_config_template.json   # copy per experiment
  examples/                  # known-valid smoke run configs
  schemas/                   # matrix, baseline, and result table contracts
data/
  raw/                       # ignored local artifact downloads
  processed/                 # ignored converted matrices and result tables
```

The repository tracks code, manifests, and notes. Raw benchmark data should stay
outside git.

## First Commands

Audit which sources are available:

```bash
PYTHONPATH=src python3 scripts/audit_benchmarks.py
```

Validate a run configuration:

```bash
PYTHONPATH=src python3 scripts/validate_run_config.py path/to/run_config.json
PYTHONPATH=src python3 scripts/preflight_experiment.py path/to/run_config.json
PYTHONPATH=src python3 scripts/preflight_experiment.py path/to/run_config.json --check-files
```

Try the checked metadata-smoke example:

```bash
PYTHONPATH=src python3 scripts/preflight_experiment.py \
  benchmarks/examples/defects4j_metadata_smoke.run_config.json --check-files
```

Find row-wise dense `0/1` matrices in an artifact:

```bash
PYTHONPATH=src python3 scripts/discover_matrices.py "$SHAPTCP_OCP_ROOT"
```

For zipped artifacts, add:

```bash
PYTHONPATH=src python3 scripts/discover_matrices.py "$SHAPTCP_OCP_ROOT" --scan-zip
```

Run ShapTCP and core baselines on one confirmed matrix:

```bash
PYTHONPATH=src python3 scripts/run_benchmark_matrix.py \
  path/to/matrix.txt --semantics statement --k 20
```

For Defects4J, start with dry-run commands:

```bash
PYTHONPATH=src python3 scripts/build_defects4j_trigger_matrix.py \
  --project Lang --bugs 1 3 4 --work-dir data/work/defects4j
```

Add `--execute` only on the development machine after Java/Perl/Defects4J are
configured.

If Defects4J metadata is already available, use the metadata-only smoke adapter:

```bash
PYTHONPATH=src python3 scripts/build_defects4j_metadata_matrix.py \
  --defects4j-root "$DEFECTS4J_HOME" \
  --project Lang --bugs 1 3 4 \
  --output data/processed/defects4j/Lang_metadata_trigger_1_3_4.txt
```

This is only pipeline validation.
