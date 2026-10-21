#!/usr/bin/env python3
"""One explicit target-local build. Binaries are generated, not source artifacts."""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import platform
import shutil
import subprocess

LANE = Path(__file__).resolve().parent
FLAGS = ('-O3', '-std=c++17', '-fPIC', '-shared', '-fno-fast-math', '-ffp-contract=off')
SOURCES = ('moments.cpp', 'build_native.py')
DEFAULT_BUILD = LANE / 'build'

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def source_hashes():
    return {name: sha(LANE / name) for name in SOURCES}

def inspect_build(build_dir=DEFAULT_BUILD):
    directory = Path(build_dir).resolve()
    receipt_path = directory / 'build_receipt.json'
    library = directory / 'librei_moments.so'
    try:
        receipt = json.loads(receipt_path.read_text())
        valid = (receipt['schema'] == 'rei.native.build.v1' and receipt['source_sha256'] == source_hashes()
                 and receipt['flags'] == list(FLAGS) and receipt['library_sha256'] == sha(library)
                 and receipt['platform'] == platform.platform() and receipt['machine'] == platform.machine())
    except (OSError, ValueError, KeyError):
        valid = False
    if not valid:
        raise ValueError('NATIVE_BUILD_MISSING_OR_STALE: rebuild with python build_native.py --out ' + str(directory))
    return library, receipt_path, receipt

def build(directory, compiler='g++'):
    directory = Path(directory).resolve()
    directory.mkdir(parents=True, exist_ok=True)
    executable = shutil.which(compiler)
    if executable is None:
        raise ValueError('CXX17_COMPILER_NOT_AVAILABLE')
    library = directory / 'librei_moments.so'
    argv = [executable, *FLAGS, str(LANE / 'moments.cpp'), '-o', str(library)]
    completed = subprocess.run(argv, check=True, capture_output=True, text=True)
    receipt = {'schema': 'rei.native.build.v1', 'source_sha256': source_hashes(),
               'compiler': executable, 'compiler_version': subprocess.check_output([executable, '--version'], text=True),
               'flags': list(FLAGS), 'argv': argv, 'library_sha256': sha(library),
               'platform': platform.platform(), 'machine': platform.machine(),
               'built_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
               'stdout': completed.stdout, 'stderr': completed.stderr}
    (directory / 'build_receipt.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    return receipt

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=DEFAULT_BUILD)
    parser.add_argument('--compiler', default='g++')
    args = parser.parse_args()
    print(json.dumps(build(args.out, args.compiler), indent=2, sort_keys=True))
