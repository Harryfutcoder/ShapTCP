# OCP Source Notes

Status: source audited, matrix not yet confirmed for ShapTCP.

## Verified Local Source

- Artifact URL: https://github.com/QuanjunZhang/OCP
- Observed local root: `/private/tmp/OCP`
- README states the artifact contains code, experimental data, subject programs,
  test suites, mutants, figures, and result data.

## Observed Structure

- `README.md`: artifact overview.
- `code/ComparingTechniques/`: Java implementations for comparator techniques.
- `code/OCP/OCP.java`: OCP implementation.
- `data/APFD/CSVFile/`: upstream APFD CSV result tables.
- `data/APFD/JsonFile/`: upstream APFD JSON result tables.
- `data/PrioritizationTime/`: upstream prioritization-time data.
- `data/PrioritizationTS/`: upstream prioritized-test-suite data.
- `Subject progaram and test suites/`: zipped subject programs and test suites.
- `mutants/`: mutant data for C subjects.

## Verified Code Behavior

`code/ComparingTechniques/GreedyAdditional.java` reads a coverage file as a
dense character matrix. Each file line is one test case; each character is a
coverage bit. `code/OCP/OCP.java` follows the same dense line-oriented coverage
matrix assumption.

This confirms the artifact uses dense coverage matrices internally, but it does
not yet identify a specific raw matrix file for ShapTCP.

## Current ShapTCP Audit Result

Command:

```bash
PYTHONPATH=src python3 scripts/discover_matrices.py /private/tmp/OCP --scan-zip --limit 10
```

Observed result: no dense candidate matrix was found by the current shallow
scanner.

Interpretation:

- OCP is not yet matrix-ready for ShapTCP.
- Existing APFD/priority/time CSV/JSON files are upstream artifact results, not
  ShapTCP results.
- Next step is to inspect or run the original Java artifact to locate the
  coverage-matrix inputs, or to generate matrices from the subject packages
  under the original protocol.

## Accuracy Gate

Before reporting OCP results:

- identify the exact matrix file used by the original artifact;
- record whether columns are statements, branches, methods, mutants, or faults;
- confirm candidate test rows match the original benchmark protocol;
- decide whether OCP result tables are used only as upstream comparison data or
  whether baseline code is rerun.
