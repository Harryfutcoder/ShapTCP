"""Build or dry-run a Defects4J trigger-test matrix.

Default mode is dry-run: it prints the commands that should be executed on a
development machine. Add --execute to actually run Defects4J checkouts/exports.
"""

from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--defects4j-bin", type=Path, default=Path(os.environ.get("DEFECTS4J_BIN", "defects4j")))
    parser.add_argument("--project", required=True, help="Defects4J project id, e.g. Lang.")
    parser.add_argument("--bugs", nargs="+", required=True, help="Bug ids, e.g. 1 2 3.")
    parser.add_argument("--work-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("defects4j_trigger_matrix.csv"))
    parser.add_argument("--execute", action="store_true", help="Actually run checkout/export commands.")
    args = parser.parse_args()

    commands = []
    trigger_map: dict[str, set[str]] = {}
    for bug in args.bugs:
        checkout_dir = args.work_dir / f"{args.project}-{bug}b"
        commands.append(
            [
                str(args.defects4j_bin),
                "checkout",
                "-p",
                args.project,
                "-v",
                f"{bug}b",
                "-w",
                str(checkout_dir),
            ]
        )
        commands.append([str(args.defects4j_bin), "export", "-p", "tests.trigger", "-w", str(checkout_dir)])

        if args.execute:
            checkout_dir.parent.mkdir(parents=True, exist_ok=True)
            run(commands[-2])
            output = run(commands[-1])
            trigger_map[bug] = parse_trigger_tests(output)

    if not args.execute:
        print("# Dry-run only. Re-run with --execute on the development machine.")
        for command in commands:
            print(shell_join(command))
        return

    write_trigger_matrix(trigger_map, args.output)
    print(f"wrote {args.output}")


def run(command: list[str]) -> str:
    completed = subprocess.run(command, check=True, text=True, capture_output=True)
    return completed.stdout


def parse_trigger_tests(output: str) -> set[str]:
    return {line.strip() for line in output.splitlines() if line.strip()}


def write_trigger_matrix(trigger_map: dict[str, set[str]], output: Path) -> None:
    tests = sorted(set().union(*trigger_map.values()) if trigger_map else set())
    bugs = sorted(trigger_map, key=lambda value: int(value) if value.isdigit() else value)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        for test in tests:
            handle.write("".join("1" if test in trigger_map[bug] else "0" for bug in bugs) + "\n")
    output.with_suffix(output.suffix + ".tests").write_text("\n".join(tests) + "\n", encoding="utf-8")
    output.with_suffix(output.suffix + ".entities").write_text(
        "\n".join(f"bug_{bug}" for bug in bugs) + "\n",
        encoding="utf-8",
    )


def shell_join(command: list[str]) -> str:
    return " ".join(quote(part) for part in command)


def quote(value: str) -> str:
    if all(char.isalnum() or char in "._/-" for char in value):
        return value
    return "'" + value.replace("'", "'\"'\"'") + "'"


if __name__ == "__main__":
    main()
