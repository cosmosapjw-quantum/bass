#!/usr/bin/env python3
"""Build a deterministic SHA-256 manifest while rejecting links/special files."""

from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
import tempfile


def excluded(relative: Path, output_relative: Path | None = None) -> bool:
    if relative == output_relative:
        return True
    if ".git" in relative.parts or "__pycache__" in relative.parts:
        return True
    if relative.suffix in {".pyc", ".pyo", ".zip"}:
        return True
    return False


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def manifest_rows(root: Path, output: Path) -> list[str]:
    root = root.resolve()
    output = output.resolve()
    output_relative = output.relative_to(root)
    rows: list[str] = []
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if excluded(relative, output_relative):
            continue
        if path.is_symlink():
            raise RuntimeError(f"symlink rejected: {relative}")
        if path.is_dir():
            continue
        if not path.is_file():
            raise RuntimeError(f"special file rejected: {relative}")
        rows.append(f"{hash_file(path)}  {relative.as_posix()}")
    return rows


def write_atomic(output: Path, text: str) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{output.name}.", dir=output.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        os.replace(temporary, output)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output if args.output.is_absolute() else args.root / args.output
    rows = manifest_rows(args.root, output)
    write_atomic(output, "\n".join(rows) + "\n")
    print(f"wrote {len(rows)} hashes to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
