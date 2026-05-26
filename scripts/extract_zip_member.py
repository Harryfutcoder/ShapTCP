"""Extract one confirmed zip member to a local path."""

from __future__ import annotations

import argparse
from pathlib import Path
from zipfile import ZipFile


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("zip_path", type=Path)
    parser.add_argument("member")
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(args.zip_path) as archive:
        data = archive.read(args.member)
    args.output.write_bytes(data)
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
