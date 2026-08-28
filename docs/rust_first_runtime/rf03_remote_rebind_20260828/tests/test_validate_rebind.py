#!/usr/bin/env python3
"""Real-Git regression tests. All repositories and physics bytes here are synthetic.
Only immutable pins are rebound inside the test module; subprocess/Git are real.
"""
from __future__ import annotations
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
TARGET = Path(os.environ.get('RF03_VALIDATOR_UNDER_TEST', ROOT / 'validate_rebind.py'))
R2_FIXTURE = Path(__file__).resolve().parent / 'fixtures' / 'validate_package_r2.py'

def load():
    spec = importlib.util.spec_from_file_location('validator_under_test', TARGET)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def sha(data):
    return hashlib.sha256(data).hexdigest()

def git(repo, *args, data=None):
    r = subprocess.run(['git', *args], cwd=repo, input=data, capture_output=True)
    if r.returncode:
        raise RuntimeError(r.stderr.decode(errors='replace'))
    return r.stdout

def oid(repo, *args, data=None):
    return git(repo, *args, data=data).decode('ascii').strip()

def dump(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + '\n', encoding='utf-8')

class Fixture:
    def __init__(self, repo, mod):
        self.repo, self.mod = repo, mod
        repo.mkdir()
        git(repo, 'init', '-q')
        git(repo, 'config', 'user.name', 'RF03 synthetic test')
        git(repo, 'config', 'user.email', 'rf03-test@example.invalid')
        git(repo, 'config', 'core.autocrlf', 'false')
        source_names = [
            'bianchi/matter/fluid.py', 'bianchi/matter/species.py',
            'bianchi/matter/tilt_admissibility.py', 'bianchi/thermo/temperature.py',
            'compiler/validation/typeii_fixture_authority.json',
            'runtime/rust/typeii/tests/FIXTURE_PROVENANCE.json']
        self.sources = {}
        for name in source_names:
            p = repo / name; p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(('SYNTHETIC IDENTITY-ONLY SOURCE ' + name + '\n').encode())
            self.sources[name] = oid(repo, 'hash-object', str(p))
        self.base = self.commit('synthetic source base')
        self.base_tree = oid(repo, 'rev-parse', self.base + '^{tree}')
        (repo / 'legacy.txt').write_text('immutable historical package\n')
        self.legacy = self.commit('historical package')
        self.legacy_tree = oid(repo, 'rev-parse', self.legacy + '^{tree}')
        (repo / 'bootstrap-note.txt').write_text('new bootstrap on same legacy branch\n')
        self.advanced = self.commit('advance legacy branch')
        self.r1_branch = 'agent/plans/rf03-matter-thermo-tilt-closure-20260828-r1'
        git(repo, 'update-ref', 'refs/remotes/origin/' + self.r1_branch, self.advanced)
        git(repo, 'checkout', '-q', '--detach', self.base)
        direct = repo / mod.AUTH_PATH; direct.mkdir(parents=True)
        upstream = R2_FIXTURE.read_bytes()
        if sha(upstream) != 'caf503153085c8ad2900dd80ef26aa905b8cb8bf7e8541ebd51a7736466c80f8':
            raise AssertionError('R2 fixture no longer matches immutable upstream')
        # Only pins change in this synthetic fixture, not the original checker logic.
        text = upstream.decode().replace(
            'dfa17457d402bd441d3fdf786c2d79c529512ee5', self.base).replace(
            '9fc67fb0ba10e091e25a14d7e1fac88b77a0241e', self.base_tree).replace(
            'b7cda09d337906c17821a2b815032c985ff86bdf', self.legacy)
        old_source_pins = {
            'bianchi/matter/fluid.py': '41905ff26914b2a7931ce2281d67b25fbde273b5',
            'bianchi/matter/species.py': '60a683fcdc639ae790cf6f3c723182d26940d21f',
            'bianchi/matter/tilt_admissibility.py': 'c384a87c1722bd3c6b9b7e02ea71efe7ec88b676',
            'bianchi/thermo/temperature.py': '4b792b04df072446a5d046524ea5323e4237d7e4',
            'compiler/validation/typeii_fixture_authority.json': 'b71372faa7dde85e928802c08c831299ebe99bcd',
            'runtime/rust/typeii/tests/FIXTURE_PROVENANCE.json': 'dfee51903025b4c9d3f62f63581271bd3b6a98cb'}
        for name, digest in old_source_pins.items():
            text = text.replace(digest, self.sources[name])
        (direct / 'validate_package.py').write_bytes(text.encode())
        pid = 'BASS-RF03-AUTHORITY-DIRECT-HANDOFF-20260828-R2'
        dump(direct / 'AUTHORITY_CONTRACT.json', {
            'package_id': pid,
            'production_matter_authority': {
                'model_id': 'explicit_gamma_law_tilted_perfect_fluid_v1',
                'state_order': ['Omega', 'v1', 'v2', 'v3']},
            'thermodynamics_boundary': {'tilted_temperature_formula': 'UNDEFINED_AND_NOT_AUTHORIZED'},
            'claim_boundary': {'current': 'NO_PASS_RF03_CLAIM'}})
        dump(direct / 'WORK_UNITS.json', {'package_id': pid, 'exact_next_action': 'RF03-AUTH-01'})
        (direct / 'README.md').write_bytes(b'  SYNTHETIC fixture\r\nwith whitespace\r\n\r\n')
        (direct / 'CODEX_HANDOFF.md').write_bytes('synthetic 핸드오프\n'.encode())
        (direct / 'MANIFEST.sha256').write_text(''.join(
            f'{sha(p.read_bytes())}  {p.name}\n' for p in sorted(direct.iterdir())), encoding='utf-8')
        self.direct_bytes = {p.name: p.read_bytes() for p in direct.iterdir()}
        self.index = {'canonical_transport': 'DIRECT_TEXT_FILES', 'canonical_path': mod.AUTH_PATH,
                      'canonical_files': [{'name': n, 'sha256': sha(b), 'bytes': len(b),
                         'git_blob_sha1': oid(repo, 'hash-object', str(direct/n))}
                        for n,b in sorted(self.direct_bytes.items())]}
        dump(repo / mod.AUTH_INDEX, self.index)
        self.auth = self.commit('synthetic authority')
        self.auth_tree = oid(repo, 'rev-parse', self.auth + '^{tree}')
        git(repo, 'update-ref', 'refs/remotes/origin/' + mod.AUTH_BRANCH, self.auth)
        git(repo, 'update-ref', 'refs/remotes/origin/' + mod.BASE_BRANCH, self.base)
        mod.AUTH_HEAD, mod.AUTH_TREE = self.auth, self.auth_tree
        mod.BASE_HEAD, mod.BASE_TREE = self.base, self.base_tree
        mod.R1_HEAD, mod.R1_TREE, mod.R1_BRANCH = self.legacy, self.legacy_tree, self.r1_branch
        mod.DIRECT_FILES = {n: sha(b) for n,b in self.direct_bytes.items()}
        mod.SOURCE_BLOBS = dict(self.sources)
        if hasattr(mod, 'AUTH_INDEX_BLOB'):
            mod.AUTH_INDEX_BLOB = oid(repo, 'rev-parse', self.auth + ':' + mod.AUTH_INDEX)

    def commit(self, message):
        git(self.repo, 'add', '-A')
        git(self.repo, 'commit', '-qm', message)
        return oid(self.repo, 'rev-parse', 'HEAD')

    def repin_auth(self):
        self.auth = self.commit('synthetic hostile authority change')
        self.mod.AUTH_HEAD = self.auth
        self.mod.AUTH_TREE = oid(self.repo, 'rev-parse', self.auth + '^{tree}')
        if hasattr(self.mod, 'AUTH_INDEX_BLOB'):
            self.mod.AUTH_INDEX_BLOB = oid(self.repo, 'rev-parse', self.auth + ':' + self.mod.AUTH_INDEX)
        git(self.repo, 'update-ref', 'refs/remotes/origin/' + self.mod.AUTH_BRANCH, self.auth)

class LiveRegression(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='rf03 validator test ')
        self.addCleanup(self.tmp.cleanup)
        self.mod = load()
        self.fx = Fixture(Path(self.tmp.name) / 'repo with spaces', self.mod)

    def test_live_with_advanced_legacy_ref(self):
        # The reported bytes are intact; only the historical branch tip advanced.
        try:
            self.mod.validate_live(self.fx.repo)
        except SystemExit as exc:
            self.fail(str(exc))

    def test_materialized_bytes_are_identical(self):
        target = Path(self.tmp.name) / 'retained authority'
        self.mod.validate_live(self.fx.repo, materialize=target)
        for name, data in self.fx.direct_bytes.items():
            self.assertEqual((target / name).read_bytes(), data)

    def test_auth_branch_move_is_rejected(self):
        git(self.fx.repo, 'update-ref', 'refs/remotes/origin/' + self.mod.AUTH_BRANCH, self.fx.advanced)
        with self.assertRaisesRegex(SystemExit, 'authority branch moved'):
            self.mod.validate_live(self.fx.repo)

    def test_base_branch_move_is_rejected(self):
        git(self.fx.repo, 'update-ref', 'refs/remotes/origin/' + self.mod.BASE_BRANCH, self.fx.advanced)
        with self.assertRaisesRegex(SystemExit, 'base moved'):
            self.mod.validate_live(self.fx.repo)

    def test_wrong_historical_tree_is_rejected(self):
        self.mod.R1_TREE = self.fx.base_tree
        with self.assertRaisesRegex(SystemExit, 'historical R1 tree'):
            self.mod.validate_live(self.fx.repo)

    def test_wrong_source_blob_is_rejected(self):
        self.mod.SOURCE_BLOBS['bianchi/matter/fluid.py'] = '0' * 40
        with self.assertRaisesRegex(SystemExit, 'source blob'):
            self.mod.validate_live(self.fx.repo)

    def test_removed_final_newline_is_not_normalized(self):
        p = self.fx.repo / self.mod.AUTH_PATH / 'AUTHORITY_CONTRACT.json'
        p.write_bytes(p.read_bytes().removesuffix(b'\n'))
        self.fx.repin_auth()
        with self.assertRaisesRegex(SystemExit, 'digest mismatch'):
            self.mod.validate_live(self.fx.repo)

    def test_wrong_transport_is_rejected(self):
        self.fx.index['canonical_transport'] = 'ZIP'
        dump(self.fx.repo / self.mod.AUTH_INDEX, self.fx.index); self.fx.repin_auth()
        with self.assertRaisesRegex(SystemExit, 'transport'):
            self.mod.validate_live(self.fx.repo)

    def test_duplicate_index_entry_is_rejected(self):
        self.fx.index['canonical_files'].append(dict(self.fx.index['canonical_files'][0]))
        dump(self.fx.repo / self.mod.AUTH_INDEX, self.fx.index); self.fx.repin_auth()
        with self.assertRaisesRegex(SystemExit, 'duplicate'):
            self.mod.validate_live(self.fx.repo)

    def test_missing_direct_file_is_rejected(self):
        (self.fx.repo / self.mod.AUTH_PATH / 'README.md').unlink(); self.fx.repin_auth()
        with self.assertRaises(SystemExit):
            self.mod.validate_live(self.fx.repo)

    def test_index_blob_pin_is_enforced(self):
        self.mod.AUTH_INDEX_BLOB = '0' * 40
        with self.assertRaisesRegex(SystemExit, 'authority index blob'):
            self.mod.validate_live(self.fx.repo)

    def test_original_r2_semantics_are_executed(self):
        direct = self.fx.repo / self.mod.AUTH_PATH
        contract = json.loads((direct / 'AUTHORITY_CONTRACT.json').read_bytes())
        contract['production_matter_authority']['model_id'] = 'forbidden_model'
        dump(direct / 'AUTHORITY_CONTRACT.json', contract)
        (direct / 'MANIFEST.sha256').write_text(''.join(
            f'{sha(p.read_bytes())}  {p.name}\n' for p in sorted(direct.iterdir())
            if p.name != 'MANIFEST.sha256'), encoding='utf-8')
        self.mod.DIRECT_FILES = {p.name: sha(p.read_bytes()) for p in direct.iterdir()}
        self.fx.index['canonical_files'] = [
            {'name': n, 'sha256': h} for n,h in sorted(self.mod.DIRECT_FILES.items())]
        dump(self.fx.repo / self.mod.AUTH_INDEX, self.fx.index)
        self.fx.repin_auth()
        with self.assertRaisesRegex(SystemExit, 'R2 offline checker:.*model id'):
            self.mod.validate_live(self.fx.repo)

    def test_existing_materialization_is_not_overwritten(self):
        target = Path(self.tmp.name) / 'occupied'; target.mkdir()
        marker = target / 'keep.txt'; marker.write_bytes(b'keep unknown work')
        with self.assertRaisesRegex(SystemExit, 'already exists'):
            self.mod.validate_live(self.fx.repo, materialize=target)
        self.assertEqual(marker.read_bytes(), b'keep unknown work')

    def test_live_checks_do_not_mutate_repository(self):
        marker = self.fx.repo / 'untracked.bin'; marker.write_bytes(b'keep\0unknown\n')
        before = (git(self.fx.repo, 'status', '--porcelain=v1', '-z'),
                  git(self.fx.repo, 'show-ref'), marker.read_bytes())
        self.mod.validate_live(self.fx.repo)
        after = (git(self.fx.repo, 'status', '--porcelain=v1', '-z'),
                 git(self.fx.repo, 'show-ref'), marker.read_bytes())
        self.assertEqual(before, after)

    def test_child_uses_current_interpreter(self):
        bindir = Path(self.tmp.name) / 'bin'; bindir.mkdir()
        fake = bindir / 'python'; fake.write_text('#!/bin/sh\nexit 97\n'); fake.chmod(0o755)
        prior = os.environ.get('PATH', '')
        try:
            os.environ['PATH'] = str(bindir) + os.pathsep + prior
            self.mod.validate_live(self.fx.repo)
        finally:
            os.environ['PATH'] = prior

class BytesRegression(unittest.TestCase):
    def test_git_blob_edge_cases(self):
        mod = load()
        with tempfile.TemporaryDirectory(prefix='rf03 raw bytes ') as td:
            repo = Path(td); git(repo, 'init', '-q')
            cases = [b'line\n', b'line\r\n', b'line', b' \tline \t\n\n',
                     b'\r', b'\n\n', b'', '한국어 α\n'.encode(), b'\xff\x00\x80\r\n']
            for data in cases:
                with self.subTest(data=data):
                    blob = oid(repo, 'hash-object', '-w', '--stdin', data=data)
                    self.assertEqual(mod.git_bytes(repo, 'cat-file', 'blob', blob), data)

if __name__ == '__main__':
    unittest.main(verbosity=2)
