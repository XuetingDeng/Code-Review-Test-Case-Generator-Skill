#!/usr/bin/env python3
"""Copy the bundled FastAPI template into a target directory."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def copy_tree(source: Path, target: Path, force: bool) -> list[Path]:
    copied: list[Path] = []
    for path in source.rglob("*"):
        if path.is_dir():
            continue
        relative = path.relative_to(source)
        destination = target / relative
        if destination.exists() and not force:
            raise FileExistsError(f"{destination} already exists; pass --force to overwrite")
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, destination)
        copied.append(destination)
    return copied


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("target", help="Directory where the API project should be copied")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    args = parser.parse_args()

    skill_root = Path(__file__).resolve().parents[1]
    source = skill_root / "assets" / "code-review-api-template"
    target = Path(args.target).expanduser().resolve()
    copied = copy_tree(source, target, args.force)
    print(f"Copied {len(copied)} files to {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
