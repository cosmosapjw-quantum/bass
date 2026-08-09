#!/usr/bin/env python3
"""Create a deterministic ZIP of the harness without following links."""

from __future__ import annotations

import argparse
from pathlib import Path
import stat
import sys
import tempfile
import zipfile

HARNESS_ROOT = Path(__file__).resolve().parents[1]
if str(HARNESS_ROOT) not in sys.path:
    sys.path.insert(0, str(HARNESS_ROOT))
from tools.build_file_manifest import excluded


ZIP_TIME = (1980, 1, 1, 0, 0, 0)


def bundle(root: Path, output: Path) -> int:
    root = root.resolve()
    output = output.resolve()
    if output == root or root in output.parents:
        raise ValueError("bundle output must be outside the harness root")
    output.parent.mkdir(parents=True, exist_ok=True)
    prefix = root.name
    files: list[Path] = []
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if excluded(relative):
            continue
        if path.is_symlink():
            raise RuntimeError(f"symlink rejected: {relative}")
        if path.is_dir():
            continue
        if not path.is_file():
            raise RuntimeError(f"special file rejected: {relative}")
        files.append(path)

    with tempfile.NamedTemporaryFile(
        prefix=f".{output.name}.", suffix=".tmp", dir=output.parent, delete=False
    ) as handle:
        temporary = Path(handle.name)
    try:
        with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED,
                             compresslevel=9, strict_timestamps=True) as archive:
            for path in files:
                relative = path.relative_to(root)
                info = zipfile.ZipInfo(f"{prefix}/{relative.as_posix()}", ZIP_TIME)
                info.compress_type = zipfile.ZIP_DEFLATED
                info.create_system = 3
                mode = stat.S_IMODE(path.stat().st_mode)
                info.external_attr = ((stat.S_IFREG | mode) & 0xFFFF) << 16
                archive.writestr(info, path.read_bytes(), compresslevel=9)
        temporary.replace(output)
    finally:
        temporary.unlink(missing_ok=True)
    return len(files)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    count = bundle(args.root, args.output)
    print(f"wrote {count} files to {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
