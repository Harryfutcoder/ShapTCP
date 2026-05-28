# Paper Experiment Checklist

This is the paper experiment list for ShapTCP. It tells a future runner exactly
which artifacts to clone or download, which paper each artifact belongs to,
where local paths should live, and which command to try first.

## Repository Setup

Clone ShapTCP:

```bash
git clone https://github.com/Harryfutcoder/ShapTCP.git
cd ShapTCP
```

Create a lightweight Python environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e .
```

Smoke test:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
PYTHONPATH=src python3 scripts/audit_benchmarks.py
PYTHONPATH=src python3 scripts/run_synthetic_suite.py --seeds 50
```

The ShapTCP core has no GPU requirement.

## Local Data Convention

Raw benchmark data should not be committed. Use ignored local directories:

```text
data/raw/<benchmark>        # cloned/downloaded upstream artifacts
data/processed/<benchmark>  # converted matrices and result CSVs
data/work/<benchmark>       # temporary checkouts/build outputs
outputs/<run_id>            # final run tables, orders, traces
```

Every benchmark should have a source note copied from:

```text
benchmarks/SOURCE_NOTES_TEMPLATE.md
```

The result table must include:

- `evidence_level`;
- `claim_scope`;
- `source_status`;
- `matrix_status`;
- `result_status`;
- verified `semantics`.

Each reported run must also state:

- candidate test set and whether it came from a selector;
- row semantics, column semantics, and value semantics;
- whether columns are true bugs/faults, mutants, coverage entities, or CI
  proxies;
- budget policy: full suite, count budget, or time budget;
- metric formulas used for APFD/APFDc/NAPFD or benchmark-native CI metrics;
- tie-breaking policy and random seeds.

## First Benchmark Order

Run in this order unless a source is blocked:

1. `Defects4J metadata trigger matrix`: laptop-safe adapter validation.
2. `SIR` or `FAST` small matrix: first real public matrix if source is ready.
3. `OCP`: after locating the original raw dense matrix used by the artifact.
4. `Defects4J execution trigger matrix`: first execution-derived bug matrix.
5. `Defects4J coverage/mutation`: later, heavier public evidence.
6. `TCPFramework / RETECS / tp_rl / DeepOrder / TCP-CI / AutoTCP`: CI-history
   extension and broader learning baselines.

## Artifact Map

| Id | Paper / Artifact Role | Code or Data URL | Local Root | Env Var | First Action | Resource Level |
|---|---|---|---|---|---|---|
| `sir` | Software-artifact Infrastructure Repository; useful for small fault-matrix subjects | https://sir.csc.ncsu.edu/portal/index.php | `data/raw/SIR` | `SHAPTCP_SIR_ROOT` | download one small object, inspect for fault matrix or generation scripts | low to medium |
| `ocp` | Zhang et al., JSS 2022, partial-attention / OCP coverage TCP | https://github.com/QuanjunZhang/OCP | `data/raw/OCP` | `SHAPTCP_OCP_ROOT` | clone repo, run matrix discovery, locate original coverage matrix inputs | medium |
| `fast` | Miranda et al., ICSE 2018, similarity-based FAST TCP | https://github.com/icse18-fast/FAST | `data/raw/FAST` | `SHAPTCP_FAST_ROOT` | clone repo, inspect input matrices and old requirements | medium |
| `defects4j` | Just et al., ISSTA 2014, real Java bugs benchmark | https://github.com/rjust/defects4j | `data/raw/defects4j` | `DEFECTS4J_HOME` | set up Java 11, run metadata matrix, then checkout/export trigger matrix | medium to high |
| `tcpframework` | Chojnacki and Madeyski TCPFramework / RTPTorrent CI benchmark | https://github.com/LechMadeyski/MSc25TomaszChojnacki | `data/raw/tcp-framework` | `SHAPTCP_TCPFRAMEWORK_ROOT` | clone code, then obtain RTPTorrent/TravisTorrent data | high |
| `rtptorrent` | CI execution data used by TCPFramework | https://zenodo.org/records/4046180 | `data/raw/rtptorrent` | `SHAPTCP_RTPTORRENT_ROOT` | download only on development machine | high |
| `retecs` | Spieker et al., ISSTA 2017, RL-TCP classic baseline | https://github.com/mregorova/RETECS | `data/raw/RETECS` | `SHAPTCP_RETECS_ROOT` | clone repo, inspect bundled DATA and Docker/old Python path | medium |
| `tp_rl` | Bagherzadeh et al., TSE 2021, RL formulations | https://github.com/moji1/tp_rl | `data/raw/tp_rl` | `SHAPTCP_TPRL_ROOT` | clone repo, inspect `data/`, isolate Python 3.7 + Stable Baselines 2.10 | high |
| `deeporder` | Sharif et al., ICSME 2021, deep CI-TCP | https://github.com/T3AS/DeepOrder-ICSME21 | `data/raw/DeepOrder-ICSME21` | `SHAPTCP_DEEPORDER_ROOT` | clone repo, obtain linked data, isolate Python 3.6 + TF 2.1 | high |
| `tcp_ci` | Yaraghi et al., TSE 2022, feature-rich CI TCP | https://github.com/Ahmadreza-SY/TCP-CI | `data/raw/TCP-CI` | `SHAPTCP_TCPCI_ROOT` | clone repo, download Zenodo dataset, avoid Understand pipeline at first | high |
| `autotcp` | Romero et al., EMSE 2026, AutoML TCP comparator | https://github.com/humains-lab/2026-AutoTCP | `data/raw/2026-AutoTCP` | `SHAPTCP_AUTOTCP_ROOT` | clone repo, inspect run scripts and Yaraghi dataset dependency | high |

## Exact Clone Commands

```bash
mkdir -p data/raw

git clone https://github.com/QuanjunZhang/OCP.git data/raw/OCP
export SHAPTCP_OCP_ROOT="$PWD/data/raw/OCP"

git clone https://github.com/icse18-fast/FAST.git data/raw/FAST
export SHAPTCP_FAST_ROOT="$PWD/data/raw/FAST"

git clone https://github.com/rjust/defects4j.git data/raw/defects4j
export DEFECTS4J_HOME="$PWD/data/raw/defects4j"

git clone https://github.com/LechMadeyski/MSc25TomaszChojnacki.git data/raw/MSc25TomaszChojnacki
export SHAPTCP_TCPFRAMEWORK_ROOT="$PWD/data/raw/MSc25TomaszChojnacki/tcp-framework"

git clone https://github.com/mregorova/RETECS.git data/raw/RETECS
export SHAPTCP_RETECS_ROOT="$PWD/data/raw/RETECS"

git clone https://github.com/moji1/tp_rl.git data/raw/tp_rl
export SHAPTCP_TPRL_ROOT="$PWD/data/raw/tp_rl"

git clone https://github.com/T3AS/DeepOrder-ICSME21.git data/raw/DeepOrder-ICSME21
export SHAPTCP_DEEPORDER_ROOT="$PWD/data/raw/DeepOrder-ICSME21"

git clone https://github.com/Ahmadreza-SY/TCP-CI.git data/raw/TCP-CI
export SHAPTCP_TCPCI_ROOT="$PWD/data/raw/TCP-CI"

git clone https://github.com/humains-lab/2026-AutoTCP.git data/raw/2026-AutoTCP
export SHAPTCP_AUTOTCP_ROOT="$PWD/data/raw/2026-AutoTCP"
```

After cloning, run:

```bash
PYTHONPATH=src python3 scripts/audit_benchmarks.py
```

Before any public benchmark run, validate the run config:

```bash
PYTHONPATH=src python3 scripts/validate_run_config.py path/to/run_config.json
PYTHONPATH=src python3 scripts/preflight_experiment.py path/to/run_config.json --check-files
```

Use `benchmarks/examples/defects4j_metadata_smoke.run_config.json` as a known
valid template, but keep its `claim_scope=metadata_adapter_smoke` unless the
matrix is regenerated from real execution.

## Matrix Benchmark Commands

Discover candidate dense binary matrices:

```bash
PYTHONPATH=src python3 scripts/discover_matrices.py "$SHAPTCP_OCP_ROOT" --scan-zip
PYTHONPATH=src python3 scripts/discover_matrices.py "$SHAPTCP_FAST_ROOT" --scan-zip
```

If a matrix is inside a zip:

```bash
PYTHONPATH=src python3 scripts/extract_zip_member.py \
  path/to/archive.zip path/inside/archive.txt data/processed/<benchmark>/<subject>.txt
```

Run ShapTCP and first-stage baselines on a confirmed matrix:

```bash
PYTHONPATH=src python3 scripts/run_benchmark_matrix.py \
  data/processed/<benchmark>/<subject>.txt \
  --benchmark <benchmark> \
  --subject <subject> \
  --semantics <fault|bug|mutant|statement|branch|method|ci_proxy> \
  --run-id <benchmark>-<subject>-matrix-core \
  --evidence-level public_benchmark \
  --claim-scope matrix_core \
  --source-status source-audited \
  --matrix-status verified \
  --result-status reportable \
  --k 20 \
  --random-seeds 30
```

The runner refuses `--semantics unverified` unless `--allow-unverified` is
passed. Do not use `--allow-unverified` for reported results.

## Defects4J Setup

Defects4J 3.0.1 requires Java 11, Git, svn, Perl, and `cpanm`. It also expects:

```bash
export TZ=America/Los_Angeles
```

Install and initialize:

```bash
cd "$DEFECTS4J_HOME"
cpanm --installdeps .
./init.sh
export PATH="$PATH:$DEFECTS4J_HOME/framework/bin"
defects4j info -p Lang
```

Laptop-safe metadata matrix:

```bash
cd /path/to/ShapTCP
PYTHONPATH=src python3 scripts/build_defects4j_metadata_matrix.py \
  --defects4j-root "$DEFECTS4J_HOME" \
  --project Lang \
  --bugs 1 3 4 \
  --output data/processed/defects4j/Lang_metadata_trigger_1_3_4.txt
```

Execution-derived trigger matrix:

```bash
PYTHONPATH=src python3 scripts/build_defects4j_trigger_matrix.py \
  --defects4j-bin "$DEFECTS4J_HOME/framework/bin/defects4j" \
  --project Lang \
  --bugs 1 3 4 \
  --work-dir data/work/defects4j \
  --output data/processed/defects4j/Lang_trigger_1_3_4.txt \
  --execute
```

Run it:

```bash
PYTHONPATH=src python3 scripts/run_benchmark_matrix.py \
  data/processed/defects4j/Lang_trigger_1_3_4.txt \
  --benchmark defects4j \
  --subject Lang_1_3_4_trigger \
  --semantics bug \
  --run-id defects4j-lang-1-3-4-trigger \
  --evidence-level public_benchmark \
  --claim-scope execution_derived_trigger_matrix \
  --source-status tool-audited \
  --matrix-status verified \
  --result-status reportable \
  --ground-truth-level execution_derived_bug \
  --k 10
```

Do not start mutation analysis until trigger and coverage matrices are stable.

## Baseline Map for Paper 1

| Baseline Group | Methods | Paper Anchor | Artifact / Implementation | First Use |
|---|---|---|---|---|
| Controls | random | standard TCP control | local `random_order` | every matrix experiment |
| Coverage greedy | total, additional | Rothermel et al., TSE 2001 | local implementation; OCP Java comparators | Experiment 1 |
| ShapTCP ablation | static_shapley | ShapTCP theory audit | local implementation | Experiment 1 |
| Cost-aware | cost_additional, shortest, cost_shaptcp | APFDc/cost-aware TCP literature | local implementation | Experiment 2 |
| Diversity | ART-F, ART-D | Jiang et al., ASE 2009 | FAST/OCP artifact where verified | Experiment 4 |
| Search | GA/search-based TCP | Li et al., TSE 2007 | FAST/OCP artifact where verified | Experiment 4 |
| Similarity | FAST-pw, FAST-one, FAST-log, FAST-sqrt, FAST-all | Miranda et al., ICSE 2018 | FAST artifact | Experiment 4 |
| OCP | OCP and paper comparators | Zhang et al., JSS 2022 | OCP artifact | Experiment 4 |
| CI-history RL | RETECS, tp_rl | Spieker et al.; Bagherzadeh et al. | RETECS, tp_rl repos | Experiment 6 only |
| CI-history deep/ML | DeepOrder, TCP-CI, AutoTCP | Sharif et al.; Yaraghi et al.; Romero et al. | listed repos | Experiment 6 only |

## Environment Profiles

| Profile | Use | Requirements |
|---|---|---|
| `shaptcp-core` | core algorithm, synthetic, confirmed matrices | Python >= 3.10, no GPU |
| `fast-legacy` | FAST artifact baselines | isolated old Python/scipy/xxhash environment |
| `defects4j-java11` | Defects4J trigger/coverage/mutation | Linux/Docker-friendly, Java 11, Git, svn, Perl, cpanm, large disk |
| `tcpframework` | RTPTorrent/TCPFramework | Python >= 3.13, `uv`, RTPTorrent data, TravisTorrent CSV, 11 repo checkouts |
| `rl-legacy` | RETECS/tp_rl/DeepOrder | separate old Python/Stable-Baselines/TensorFlow environments |
| `feature-rich-ci` | TCP-CI/AutoTCP | Yaraghi dataset, Understand/RankLib for TCP-CI, AutoML dependencies for AutoTCP |

## Claim Checklist

Before any table goes into a paper:

- source note exists under `benchmarks/source_notes/`;
- raw data or artifact commit/version is recorded;
- matrix row and column meanings are verified;
- benchmark class is stated: matrix, generated real-bug, coverage/mutation
  proxy, or CI-history;
- result CSV includes `evidence_level` and `claim_scope`;
- `additional` is included whenever ShapTCP is included;
- random uses at least 30 seeds;
- APFD is not overclaimed if only rare recall improves;
- coverage-entity results are not described as true fault results;
- partial-budget results are not reported as classic full-suite APFD/APFDc;
- CI failure signatures are clustered or clearly labeled as proxies.

## First Week Target

Day 1:

- clone sources;
- run `audit_benchmarks.py`;
- fill source notes for OCP, FAST, and Defects4J.

Day 2:

- run Defects4J metadata matrix;
- locate one confirmed FAST or SIR dense matrix;
- run `run_benchmark_matrix.py` on one confirmed matrix.

Day 3:

- add source-specific converter if needed;
- run Experiment 1 on 3-5 subjects;
- check APFD, rare_recall@k, redundancy@k, runtime.

Day 4-5:

- add FAST/OCP artifact-native baselines only after input protocol is confirmed;
- prepare first public benchmark result table;
- record neutral or negative cases.
