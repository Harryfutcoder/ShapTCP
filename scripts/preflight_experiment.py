"""Preflight a ShapTCP experiment before running/reporting it."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from shaptcp.io import load_binary_incidence_matrix
from shaptcp.run_config import validate_run_config


REPO_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path, help="Run config JSON.")
    parser.add_argument(
        "--check-files",
        action="store_true",
        help="Also check matrix/sidecar files and the recorded matrix checksum.",
    )
    args = parser.parse_args()

    with args.config.open(encoding="utf-8") as handle:
        config = json.load(handle)

    errors = validate_run_config(config, repo_root=REPO_ROOT)
    if args.check_files:
        errors.extend(check_matrix_files(config))

    if errors:
        print("preflight failed")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print("preflight OK")


def check_matrix_files(config: dict) -> list[str]:
    errors: list[str] = []
    matrix = config.get("matrix", {})

    matrix_path = resolve_repo_path(matrix.get("path"))
    test_ids_path = resolve_repo_path(matrix.get("test_ids_path"))
    entity_ids_path = resolve_repo_path(matrix.get("entity_ids_path"))

    for label, path in [
        ("matrix.path", matrix_path),
        ("matrix.test_ids_path", test_ids_path),
        ("matrix.entity_ids_path", entity_ids_path),
    ]:
        if path is None:
            errors.append(f"{label} must be set for --check-files")
        elif not path.exists():
            errors.append(f"{label} does not exist: {path}")

    if errors:
        return errors

    assert matrix_path is not None
    assert test_ids_path is not None
    assert entity_ids_path is not None

    test_ids = load_id_file(test_ids_path)
    entity_ids = load_id_file(entity_ids_path)
    try:
        load_binary_incidence_matrix(matrix_path, test_ids=test_ids, fault_ids=entity_ids)
    except ValueError as exc:
        errors.append(f"matrix shape/id contract failed: {exc}")

    expected_checksum = str(matrix.get("checksum_sha256", "")).strip()
    if expected_checksum:
        observed_checksum = sha256_file(matrix_path)
        if observed_checksum != expected_checksum:
            errors.append(
                "matrix checksum mismatch: "
                f"expected {expected_checksum}, observed {observed_checksum}"
            )

    return errors


def resolve_repo_path(value: object) -> Path | None:
    if not value:
        return None
    path = Path(str(value))
    if path.is_absolute():
        return path
    return REPO_ROOT / path


def load_id_file(path: Path) -> tuple[str, ...]:
    return tuple(line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


if __name__ == "__main__":
    main()
