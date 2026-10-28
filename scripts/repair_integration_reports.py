"""Restore two identified posting differences to immutable report identities.

Only exact, recorded preimages are accepted. CODEGEN.json expected identities
are not changed. Unrecognized damage fails before any file is written.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOSSIER = 'research/integration_transition_20261028'
REPAIRS = {
    '15_KM2C.md': (
        'da965c171a9fe388d84a56dfc2b08961c3c260a0',
        '758f71bef1614ee84515c215b5a137cc059b1c68',
        'ray-rate 인자 D'.encode(), b'ray-rate D'),
    '20_BF3C.md': (
        'af3b2b32b67e69de5c20edeb699d411209a0cd8b',
        '16a8f46d6f98af5bc268427e92eb7ddf5047a94c',
        b'\n y,z translation', b'\ny,z translation'),
}


def blob(data: bytes) -> str:
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()


def restore(root: Path) -> dict:
    root = root.resolve()
    manifest = json.loads((root / DOSSIER / 'CODEGEN.json').read_text())
    pending = []
    for rel, expected in manifest['reports']:
        path = (root / rel).resolve()
        if not path.is_relative_to(root):
            raise ValueError('Report path escapes repository')
        data = path.read_bytes()
        actual = blob(data)
        if actual == expected:
            continue
        rule = REPAIRS.get(path.name)
        if rule is None or actual != rule[0] or expected != rule[1]:
            raise ValueError(f'Unrecognized report difference: {rel} {actual}')
        restored = data.replace(rule[2], rule[3])
        if blob(restored) != expected:
            raise ValueError(f'Restoration does not match original: {rel}')
        pending.append((path, restored, rel, actual, expected))
    for path, data, _, _, _ in pending:
        temporary = path.with_suffix(path.suffix+'.restore-tmp')
        temporary.write_bytes(data)
        temporary.replace(path)
    return {'reports_checked': len(manifest['reports']),
            'restored': [{'path': rel, 'before': before, 'after': after}
                         for _, _, rel, before, after in pending],
            'expected_identities_changed': False, 'physics_changed': False}


if __name__ == '__main__':
    print(json.dumps(restore(ROOT), indent=2))
