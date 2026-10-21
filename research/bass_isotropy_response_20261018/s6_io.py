"""S6 runner helpers: single-call receipts and enforced resource limits."""
from __future__ import annotations
import json
from pathlib import Path
import resource
import signal

RAM = 16*1024**3
DISK = 4*1024**3
JOB_SECONDS = 1800


def apply_limits():
    """Address space 16 GiB, file size 4 GiB, wall alarm 1800 s (inherited by workers)."""
    resource.setrlimit(resource.RLIMIT_AS, (RAM, RAM))
    resource.setrlimit(resource.RLIMIT_FSIZE, (DISK, DISK))
    signal.alarm(JOB_SECONDS)


def write_json_once(path: Path, value, **kw):
    """Serialize fully before creating the file, so a crash never leaves a partial receipt."""
    text = json.dumps(value, allow_nan=False, **kw)+'\n'
    with Path(path).open('x') as f:
        f.write(text)


def check_disk(out: Path) -> int:
    used = sum(p.stat().st_size for p in Path(out).rglob('*') if p.is_file())
    if used > DISK:
        raise RuntimeError('DISK_LIMIT')
    return used
