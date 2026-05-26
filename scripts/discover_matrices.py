"""Discover row-wise dense binary incidence matrices under an artifact root."""

from __future__ import annotations

import argparse
from pathlib import Path
from zipfile import ZipFile


TEXT_SUFFIXES = {".txt", ".csv", ".dat", ".matrix", ".m"}
MAX_BYTES_DEFAULT = 20_000_000


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="Artifact root to scan.")
    parser.add_argument("--max-bytes", type=int, default=MAX_BYTES_DEFAULT)
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--scan-zip", action="store_true", help="Inspect text-like files inside zip archives.")
    args = parser.parse_args()

    root = args.root.expanduser()
    if not root.exists():
        raise SystemExit(f"Root does not exist: {root}")

    print("path,rows,cols,delimiter,bytes")
    count = 0
    for path in sorted(iter_files(root, scan_zip=args.scan_zip)):
        if count >= args.limit:
            break
        candidate = inspect_path(path, args.max_bytes)
        if candidate is None:
            continue
        display_path, rows, cols, delimiter, size = candidate
        print(f"{display_path},{rows},{cols},{delimiter},{size}")
        count += 1


def iter_files(root: Path, *, scan_zip: bool):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.name.startswith("."):
            continue
        if scan_zip and path.suffix.lower() == ".zip":
            yield path
            continue
        if path.suffix.lower() in TEXT_SUFFIXES:
            yield path


def inspect_path(path: Path, max_bytes: int) -> tuple[str, int, int, str, int] | None:
    if path.suffix.lower() == ".zip":
        return inspect_zip(path, max_bytes)
    if path.stat().st_size > max_bytes:
        return None
    candidate = inspect_text(path.read_text(encoding="utf-8", errors="ignore"))
    if candidate is None:
        return None
    rows, cols, delimiter = candidate
    return str(path), rows, cols, delimiter, path.stat().st_size


def inspect_zip(path: Path, max_bytes: int) -> tuple[str, int, int, str, int] | None:
    try:
        with ZipFile(path) as archive:
            for info in archive.infolist():
                member = Path(info.filename)
                if info.is_dir() or info.file_size > max_bytes:
                    continue
                if member.suffix.lower() not in TEXT_SUFFIXES:
                    continue
                with archive.open(info) as handle:
                    text = handle.read().decode("utf-8", errors="ignore")
                candidate = inspect_text(text)
                if candidate is None:
                    continue
                rows, cols, delimiter = candidate
                return f"{path}!{info.filename}", rows, cols, delimiter, info.file_size
    except OSError:
        return None
    return None


def inspect_text(text: str) -> tuple[int, int, str] | None:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if len(lines) < 2:
        return None

    rows: list[list[str]] = []
    delimiter = "dense"
    for line in lines:
        if set(line) <= {"0", "1"}:
            values = list(line)
        elif "," in line:
            delimiter = "comma"
            values = [part.strip() for part in line.split(",")]
        else:
            delimiter = "space"
            values = line.split()
        if not values or any(value not in {"0", "1"} for value in values):
            return None
        rows.append(values)

    width = len(rows[0])
    if width == 0 or any(len(row) != width for row in rows):
        return None
    if not any("1" in row for row in rows):
        return None
    return len(rows), width, delimiter


if __name__ == "__main__":
    main()
