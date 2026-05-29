"""Build a Defects4J trigger-test matrix from shipped metadata only.

This does not checkout projects or execute tests. It is useful for adapter
smoke tests and source audits, but it should be reported separately from
execution-derived coverage or mutation matrices.

Rows are only metadata-listed triggering tests, so the output is not a fair
candidate test universe for APFD or SOTA claims.
"""

from __future__ import annotations

import argparse
import csv
import os
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--defects4j-root", type=Path, default=Path(os.environ.get("DEFECTS4J_HOME", "")))
    parser.add_argument("--project", required=True, help="Project id, e.g. Lang.")
    parser.add_argument("--bugs", nargs="+", required=True, help="Bug ids, e.g. 1 3 4.")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--allow-deprecated", action="store_true")
    args = parser.parse_args()

    if not str(args.defects4j_root):
        raise SystemExit("Set --defects4j-root or DEFECTS4J_HOME.")

    project_dir = args.defects4j_root / "framework" / "projects" / args.project
    if not project_dir.exists():
        raise SystemExit(f"Defects4J project metadata not found: {project_dir}")

    active_bugs = load_bug_ids(project_dir / "active-bugs.csv")
    deprecated_bugs = load_bug_ids(project_dir / "deprecated-bugs.csv")
    selected_bugs = [str(bug) for bug in args.bugs]

    for bug in selected_bugs:
        if bug not in active_bugs and not (args.allow_deprecated and bug in deprecated_bugs):
            raise SystemExit(
                f"{args.project} bug {bug} is not active. "
                "Use active-bugs.csv ids or pass --allow-deprecated explicitly."
            )

    trigger_map = {
        bug: read_trigger_tests(project_dir / "trigger_tests" / bug)
        for bug in selected_bugs
    }
    write_matrix(trigger_map, args.output)
    print(f"wrote {args.output}")
    print(f"tests={len(set().union(*trigger_map.values())) if trigger_map else 0}, bugs={len(selected_bugs)}")


def load_bug_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    with path.open(newline="", encoding="utf-8") as handle:
        return {row["bug.id"] for row in csv.DictReader(handle)}


def read_trigger_tests(path: Path) -> set[str]:
    if not path.exists():
        raise SystemExit(f"Missing trigger_tests file: {path}")
    tests = set()
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        stripped = line.strip()
        if stripped.startswith("--- "):
            tests.add(stripped[4:].strip())
    return tests


def write_matrix(trigger_map: dict[str, set[str]], output: Path) -> None:
    tests = sorted(set().union(*trigger_map.values()) if trigger_map else set())
    bugs = list(trigger_map)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        for test in tests:
            handle.write("".join("1" if test in trigger_map[bug] else "0" for bug in bugs) + "\n")
    output.with_suffix(output.suffix + ".tests").write_text("\n".join(tests) + "\n", encoding="utf-8")
    output.with_suffix(output.suffix + ".entities").write_text(
        "\n".join(f"bug_{bug}" for bug in bugs) + "\n",
        encoding="utf-8",
    )
    output.with_suffix(output.suffix + ".protocol.md").write_text(
        "\n".join(
            [
                "# Defects4J Metadata Trigger Matrix Protocol",
                "",
                "- rows: union of metadata-listed triggering tests only",
                "- columns: requested Defects4J bug ids",
                "- value: test is listed in Defects4J `trigger_tests` metadata",
                "",
                "This is an adapter smoke matrix. It is not a reportable TCP",
                "candidate universe and must not be used for APFD/SOTA claims.",
                "",
            ]
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
