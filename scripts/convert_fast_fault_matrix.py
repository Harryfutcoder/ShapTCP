"""Convert FAST artifact fault matrices into ShapTCP binary matrix files.

FAST stores C-subject fault matrices as ``test_id -> [fault ids]`` and Java
fault matrices as ``bug/version id -> [triggering test ids]``. This converter
keeps those semantics explicit in the generated protocol note.
"""

from __future__ import annotations

import argparse
import pickle
from pathlib import Path
from typing import Mapping


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fast-root", type=Path, required=True)
    parser.add_argument("--subject", required=True, help="FAST subject directory, e.g. flex_v3 or chart_v0.")
    parser.add_argument("--entity", default="line", choices=("line", "branch", "function", "bbox"))
    parser.add_argument(
        "--schema",
        choices=("auto", "c-test-to-faults", "java-bug-to-tests"),
        default="auto",
        help="FAST fault-matrix schema. auto uses the pickle filename.",
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    subject_dir = args.fast_root / "input" / args.subject
    if not subject_dir.exists():
        raise SystemExit(f"FAST subject directory not found: {subject_dir}")

    representation = subject_dir / f"{subject_prefix(args.subject)}-{args.entity}.txt"
    if not representation.exists():
        raise SystemExit(f"FAST representation file not found: {representation}")

    schema, pickle_path = resolve_schema(subject_dir, args.schema)
    fault_map = load_pickle_dict(pickle_path)
    n_tests = count_nonempty_lines(representation)

    if schema == "c-test-to-faults":
        test_to_entities = convert_c_fault_matrix(fault_map, n_tests)
        column_prefix = "fault"
        column_semantics = "fault"
        value_semantics = "detects"
    else:
        test_to_entities = convert_java_fault_matrix(fault_map, n_tests)
        column_prefix = "bug"
        column_semantics = "bug"
        value_semantics = "triggering_test_detects_bug"

    entity_ids = sorted(
        set().union(*test_to_entities.values()) if test_to_entities else set(),
        key=natural_key,
    )
    test_ids = [f"tc_{index}" for index in range(1, n_tests + 1)]
    write_matrix(test_to_entities, test_ids, entity_ids, args.output)
    write_protocol(
        output=args.output,
        subject=args.subject,
        entity=args.entity,
        representation=representation,
        pickle_path=pickle_path,
        schema=schema,
        column_semantics=column_semantics,
        value_semantics=value_semantics,
        column_prefix=column_prefix,
        n_tests=n_tests,
        n_entities=len(entity_ids),
    )
    print(f"wrote {args.output}")
    print(f"schema={schema}, tests={n_tests}, entities={len(entity_ids)}")


def subject_prefix(subject: str) -> str:
    return subject.rsplit("_", 1)[0]


def resolve_schema(subject_dir: Path, requested: str) -> tuple[str, Path]:
    c_path = subject_dir / "fault_matrix_key_tc.pickle"
    java_path = subject_dir / "fault_matrix.pickle"
    if requested == "c-test-to-faults":
        return requested, require_path(c_path)
    if requested == "java-bug-to-tests":
        return requested, require_path(java_path)
    if c_path.exists():
        return "c-test-to-faults", c_path
    if java_path.exists():
        return "java-bug-to-tests", java_path
    raise SystemExit(f"No FAST fault matrix pickle found under {subject_dir}")


def require_path(path: Path) -> Path:
    if not path.exists():
        raise SystemExit(f"FAST fault matrix not found: {path}")
    return path


def load_pickle_dict(path: Path) -> dict[int, list[int]]:
    with path.open("rb") as handle:
        loaded = pickle.load(handle)
    if not isinstance(loaded, Mapping):
        raise SystemExit(f"{path} did not contain a dictionary")
    normalized: dict[int, list[int]] = {}
    for key, values in loaded.items():
        if not isinstance(values, (list, tuple, set)):
            raise SystemExit(f"{path} value for {key!r} is not a list/tuple/set")
        normalized[int(key)] = [int(value) for value in values]
    return normalized


def count_nonempty_lines(path: Path) -> int:
    return sum(1 for line in path.read_text(encoding="utf-8", errors="ignore").splitlines() if line.strip())


def convert_c_fault_matrix(fault_map: Mapping[int, list[int]], n_tests: int) -> dict[str, set[str]]:
    test_to_faults = {f"tc_{index}": set() for index in range(1, n_tests + 1)}
    for test_id, faults in fault_map.items():
        if test_id < 1 or test_id > n_tests:
            raise SystemExit(f"FAST C fault matrix references test {test_id}, outside 1..{n_tests}")
        test_to_faults[f"tc_{test_id}"].update(f"fault_{fault}" for fault in faults)
    return test_to_faults


def convert_java_fault_matrix(fault_map: Mapping[int, list[int]], n_tests: int) -> dict[str, set[str]]:
    test_to_bugs = {f"tc_{index}": set() for index in range(1, n_tests + 1)}
    for bug_id, tests in fault_map.items():
        for test_id in tests:
            if test_id < 1 or test_id > n_tests:
                raise SystemExit(f"FAST Java fault matrix references test {test_id}, outside 1..{n_tests}")
            test_to_bugs[f"tc_{test_id}"].add(f"bug_{bug_id}")
    return test_to_bugs


def write_matrix(
    test_to_entities: Mapping[str, set[str]],
    test_ids: list[str],
    entity_ids: list[str],
    output: Path,
) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        for test in test_ids:
            row = "".join("1" if entity in test_to_entities[test] else "0" for entity in entity_ids)
            handle.write(row + "\n")
    output.with_suffix(output.suffix + ".tests").write_text("\n".join(test_ids) + "\n", encoding="utf-8")
    output.with_suffix(output.suffix + ".entities").write_text("\n".join(entity_ids) + "\n", encoding="utf-8")


def write_protocol(
    *,
    output: Path,
    subject: str,
    entity: str,
    representation: Path,
    pickle_path: Path,
    schema: str,
    column_semantics: str,
    value_semantics: str,
    column_prefix: str,
    n_tests: int,
    n_entities: int,
) -> None:
    lines = [
        "# FAST Fault Matrix Conversion Protocol",
        "",
        f"- subject: `{subject}`",
        f"- representation_entity: `{entity}`",
        f"- representation_file: `{representation}`",
        f"- fault_matrix_pickle: `{pickle_path}`",
        f"- schema: `{schema}`",
        f"- rows: `{n_tests}` FAST test cases, named `tc_1..tc_{n_tests}`",
        f"- columns: `{n_entities}` `{column_prefix}_*` ids from the FAST fault matrix",
        f"- column_semantics: `{column_semantics}`",
        f"- value_semantics: `{value_semantics}`",
        "",
    ]
    if schema == "java-bug-to-tests":
        lines.extend(
            [
                "Java FAST fault matrices are bug/version-to-triggering-tests maps.",
                "Use APFD over bugs only with this artifact-specific semantics recorded.",
                "",
            ]
        )
    output.with_suffix(output.suffix + ".protocol.md").write_text("\n".join(lines), encoding="utf-8")


def natural_key(value: str) -> tuple[str, int]:
    prefix, _, suffix = value.rpartition("_")
    if suffix.isdigit():
        return prefix, int(suffix)
    return value, -1


if __name__ == "__main__":
    main()
