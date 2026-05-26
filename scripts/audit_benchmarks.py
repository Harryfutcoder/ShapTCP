"""Audit configured benchmark artifact locations.

The audit is intentionally read-only. It tells us which sources are present on
the current machine and which heavy steps should be deferred to a development
machine.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = REPO_ROOT / "benchmarks" / "manifest.json"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    args = parser.parse_args()

    manifest = load_manifest(args.manifest)
    rows = [audit_entry(entry) for entry in manifest["benchmarks"]]

    if args.json:
        print(json.dumps(rows, indent=2, sort_keys=True))
        return

    print("id,source_status,matrix_status,result_status,evidence_level,present,root,adapter,accuracy_gate")
    for row in rows:
        print(
            ",".join(
                [
                    row["id"],
                    row["source_status"],
                    row["matrix_status"],
                    row["result_status"],
                    row["evidence_level"],
                    str(row["present"]).lower(),
                    row["root"] or "missing",
                    row["adapter"],
                    quote_csv(row["accuracy_gate"]),
                ]
            )
        )

    missing = [row for row in rows if not row["present"]]
    if missing:
        print("\nmissing_sources")
        for row in missing:
            print(f"- {row['id']}: set {row['root_env']} or place artifact at {row['default_root']}")


def load_manifest(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def audit_entry(entry: dict[str, Any]) -> dict[str, Any]:
    candidates = root_candidates(entry)
    root = next((candidate for candidate in candidates if candidate.exists()), None)
    return {
        "id": entry["id"],
        "name": entry["name"],
        "source_status": entry.get("source_status", entry.get("status", "unknown")),
        "matrix_status": entry.get("matrix_status", "unknown"),
        "result_status": entry.get("result_status", "unknown"),
        "evidence_level": entry.get("evidence_level", "unknown"),
        "present": root is not None,
        "root": str(root) if root else "",
        "root_env": entry["root_env"],
        "default_root": entry["default_root"],
        "adapter": entry["adapter"],
        "artifact_url": entry["artifact_url"],
        "accuracy_gate": entry["accuracy_gate"],
        "heavy_steps": entry["heavy_steps"],
    }


def root_candidates(entry: dict[str, Any]) -> list[Path]:
    candidates: list[Path] = []
    env_value = os.environ.get(entry["root_env"])
    if env_value:
        candidates.append(Path(env_value).expanduser())
    candidates.append(REPO_ROOT / entry["default_root"])
    candidates.extend(Path(path).expanduser() for path in entry.get("known_local_roots", []))
    return candidates


def quote_csv(value: str) -> str:
    escaped = value.replace('"', '""')
    return f'"{escaped}"'


if __name__ == "__main__":
    main()
