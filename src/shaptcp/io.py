"""Input helpers for matrix-based TCP artifacts."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from .types import FaultId, TestId


@dataclass(frozen=True)
class MatrixDataset:
    """A binary test-entity incidence matrix loaded from disk."""

    test_to_faults: dict[TestId, set[FaultId]]
    test_ids: tuple[TestId, ...]
    fault_ids: tuple[FaultId, ...]


def load_binary_incidence_matrix(
    path: str | Path,
    *,
    test_ids: Sequence[TestId] | None = None,
    fault_ids: Sequence[FaultId] | None = None,
    test_prefix: str = "T",
    fault_prefix: str = "F",
) -> MatrixDataset:
    """Load a row-wise binary incidence matrix.

    Supported row formats:

    - dense rows such as `0101`
    - CSV rows such as `0,1,0,1`
    - whitespace rows such as `0 1 0 1`

    Rows are tests. Columns are faults, mutants, or coverage entities depending
    on the benchmark adapter that calls this helper.
    """

    rows: list[list[str]] = []
    matrix_path = Path(path)

    for line_number, raw_line in enumerate(
        matrix_path.read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        stripped = raw_line.strip()
        if not stripped:
            continue

        values = _parse_binary_row(stripped)
        invalid = [value for value in values if value not in {"0", "1"}]
        if invalid:
            raise ValueError(f"{matrix_path}:{line_number} contains non-binary values: {invalid[:3]!r}")
        rows.append(values)

    if not rows:
        return MatrixDataset(test_to_faults={}, test_ids=tuple(), fault_ids=tuple())

    width = len(rows[0])
    for index, row in enumerate(rows, start=1):
        if len(row) != width:
            raise ValueError(f"{matrix_path}:{index} has {len(row)} columns, expected {width}")

    if test_ids is not None:
        resolved_test_ids = tuple(test_ids)
    else:
        resolved_test_ids = tuple(f"{test_prefix}{index}" for index in range(1, len(rows) + 1))

    if fault_ids is not None:
        resolved_fault_ids = tuple(fault_ids)
    else:
        resolved_fault_ids = tuple(f"{fault_prefix}{index}" for index in range(1, width + 1))

    if len(resolved_test_ids) != len(rows):
        raise ValueError(f"expected {len(rows)} test ids, got {len(resolved_test_ids)}")
    if len(resolved_fault_ids) != width:
        raise ValueError(f"expected {width} fault ids, got {len(resolved_fault_ids)}")

    test_to_faults: dict[TestId, set[FaultId]] = {}
    for test_id, row in zip(resolved_test_ids, rows):
        test_to_faults[test_id] = {fault_id for fault_id, value in zip(resolved_fault_ids, row) if value == "1"}

    return MatrixDataset(
        test_to_faults=test_to_faults,
        test_ids=resolved_test_ids,
        fault_ids=resolved_fault_ids,
    )


def _parse_binary_row(row: str) -> list[str]:
    if "," in row:
        return [value.strip() for value in row.split(",")]
    if any(char.isspace() for char in row):
        return row.split()
    return list(row)
