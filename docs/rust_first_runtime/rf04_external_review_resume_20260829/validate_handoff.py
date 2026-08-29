#!/usr/bin/env python3
"""Validate this payload and optional immutable source objects; not physics."""
from __future__ import annotations
import argparse
import ast
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess

REL = Path('docs/rust_first_runtime/rf04_external_review_resume_20260829')
ROOT = Path(__file__).resolve().parents[3]


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(['git', '--no-replace-objects', *args], cwd=repo,
                            capture_output=True, text=True, timeout=30, check=True)
    return result.stdout.rstrip('\n')


def validate(root: Path, repo: Path | None = None) -> dict:
    root = root.resolve()
    directory = root / REL
    contract = json.loads((directory / 'CONTRACT.json').read_text())
    entries = {}
    for line in (directory / 'MANIFEST.sha256').read_text().splitlines():
        digest, name = line.split('  ', 1)
        path = PurePosixPath(name)
        if (not re.fullmatch(r'[0-9a-f]{64}', digest) or path.is_absolute()
                or '..' in path.parts or name in entries or str(path) != name):
            raise ValueError('unsafe or duplicate manifest entry')
        target = root / path
        if target.is_symlink() or not target.is_file() or not target.resolve().is_relative_to(root):
            raise ValueError('missing or unsafe payload file: ' + name)
        if hashlib.sha256(target.read_bytes()).hexdigest() != digest:
            raise ValueError('payload digest mismatch: ' + name)
        if name.endswith('.py'):
            ast.parse(target.read_text(), filename=name)
        entries[name] = digest
    if set(entries) != set(contract['delivery_paths']):
        raise ValueError('manifest does not match declared delivery paths')
    profile = json.dumps(contract['profile'], sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()
    if hashlib.sha256(profile).hexdigest() != contract['profile_sha256']:
        raise ValueError('profile digest mismatch')
    checked = 0
    if repo is not None:
        source = contract['source']
        commit = source['commit']
        if git(repo, 'rev-parse', commit + '^{commit}') != commit:
            raise ValueError('source commit mismatch')
        if git(repo, 'rev-parse', commit + '^{tree}') != source['tree']:
            raise ValueError('source tree mismatch')
        if git(repo, 'rev-parse', commit + '^') != source['parent']:
            raise ValueError('source parent mismatch')
        for path, expected in source['blob_sha1'].items():
            if git(repo, 'rev-parse', commit + ':' + path) != expected:
                raise ValueError('source blob mismatch: ' + path)
            checked += 1
        authority = contract['authority']
        for key in ('control', 'rf03'):
            if git(repo, 'rev-parse', authority[key + '_commit'] + '^{tree}') != authority[key + '_tree']:
                raise ValueError(key + ' tree mismatch')
        if git(repo, 'rev-parse', authority['sci_auth_head'] + '^{tree}') != authority['sci_auth_tree']:
            raise ValueError('SCI-AUTH tree mismatch')
        schema = authority['control_commit'] + ':docs/rust_first_runtime/RF04_PUBLIC_ROUTE_SCHEMA_V1.json'
        if git(repo, 'rev-parse', schema) != authority['a1_schema_blob']:
            raise ValueError('A1 schema blob mismatch')
    return {'status': 'PASS_PAYLOAD_CHECK_ONLY', 'files': len(entries),
            'source_objects': 'CHECKED' if repo else 'NOT_RUN',
            'source_blobs_checked': checked, 'claim': 'NO_PASS_RF04',
            'profile_sha256': contract['profile_sha256']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--repo', type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(validate(args.root, args.repo), sort_keys=True))
    except (ValueError, OSError, subprocess.SubprocessError, KeyError) as error:
        parser.exit(2, f'FAIL_PAYLOAD_CHECK: {error}\n')
