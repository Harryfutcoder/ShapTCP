"""Validate a ShapTCP benchmark run configuration."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from shaptcp.run_config import validate_run_config


REPO_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path)
    args = parser.parse_args()

    with args.config.open(encoding="utf-8") as handle:
        config = json.load(handle)

    errors = validate_run_config(config, repo_root=REPO_ROOT)
    if errors:
        print("invalid run config")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print("run config OK")


if __name__ == "__main__":
    main()
