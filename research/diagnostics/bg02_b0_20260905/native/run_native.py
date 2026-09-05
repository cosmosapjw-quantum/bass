#!/usr/bin/env python3
"""Run only the native xAct calibration, preserving failures and source identity.

Prepared but UNEXECUTED in the publishing session. No auxiliary CAS, network,
Git writes, cleanup, retries, production patch, or provider admission.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write_new(path: Path, data: dict) -> None:
    text = json.dumps(data, indent=2, sort_keys=True, allow_nan=False) + '\n'
    tmp = path.with_name(path.name + '.tmp.' + str(os.getpid()))
    with tmp.open('x', encoding='utf-8') as stream:
        stream.write(text); stream.flush(); os.fsync(stream.fileno())
    if json.loads(tmp.read_text(encoding='utf-8')) != data:
        raise RuntimeError('JSON round-trip failed')
    os.link(tmp, path)  # atomic, refuses to replace previous evidence
    tmp.unlink()

def git(repo: Path, *args: str) -> str:
    p = subprocess.run(['git', '-C', str(repo), *args], stdin=subprocess.DEVNULL,
                       capture_output=True, text=True, timeout=10, check=True)
    return p.stdout.rstrip('\n')

class Blocker(RuntimeError):
    pass

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repo', type=Path, default=HERE.parents[3])
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--xact-source', type=Path, required=True)
    ap.add_argument('--wolfram', default=os.environ.get('BASS_WOLFRAM_BIN', 'wolframscript'))
    ap.add_argument('--timeout', type=float, default=360)
    args = ap.parse_args()
    repo, out = args.repo.resolve(), args.output.resolve()
    if not 1 <= args.timeout <= 1800:
        ap.error('timeout must be between 1 and 1800 seconds')
    if out.is_relative_to(repo):
        ap.error('output must be outside the source checkout')
    if out.exists():
        ap.error('use a new output directory; existing evidence is never reset')
    out.mkdir(parents=True, mode=0o700)
    result = {
        'schema_version': '1.0.0',
        'stage_id': 'BG02_B0R1_NATIVE_TYPED_VIEW_LAUNCH',
        'status': 'NOT_STARTED', 'native_xact_evaluated': False,
        'test_counts': None, 'auxiliary_cas_executed': False,
        'production_amendment': False, 'abstract_bridge_admission': False,
        'provider_admission': False, 'git_write_requested': False,
    }
    before = None
    inputs = {}
    proc = None
    start = time.monotonic()
    try:
        if Path(git(repo, 'rev-parse', '--show-toplevel')).resolve() != repo:
            raise Blocker('REPOSITORY_ROOT_MISMATCH')
        before = git(repo, 'status', '--porcelain', '--untracked-files=all')
        if before:
            raise Blocker('DIRTY_CHECKOUT: no files were cleaned or changed')
        result['source_head'] = git(repo, 'rev-parse', 'HEAD')
        result['source_tree'] = git(repo, 'rev-parse', 'HEAD^{tree}')
        expected_here = repo / 'research/diagnostics/bg02_b0_20260905/native'
        if HERE != expected_here.resolve():
            raise Blocker('LAUNCHER_AND_CHECKOUT_DIFFER')
        contract = json.loads((HERE / 'CONTRACT.json').read_text(encoding='utf-8'))
        ids = contract['required_ids']
        if len(ids) != 12 or len(set(ids)) != 12:
            raise Blocker('INVALID_TEST_ID_CONTRACT')
        paths = [HERE/'CONTRACT.json', HERE/'calibrate.wls', Path(__file__).resolve(),
                 repo / contract['activation_helper']]
        inputs = {str(p.relative_to(repo)): sha(p) for p in paths}
        result['input_sha256'] = inputs
        archive = args.xact_source.resolve(strict=True)
        result['archive_sha256'] = sha(archive)
        if result['archive_sha256'] != contract['xact_archive_sha256']:
            raise Blocker('PINNED_XACT_ARCHIVE_IDENTITY_MISMATCH: no formula verdict')
        executable = shutil.which(args.wolfram)
        if executable is None:
            raise Blocker('WOLFRAM_EXECUTABLE_NOT_FOUND')
        result['executable'] = executable
        result['status'] = 'RUNNING'
        write_new(out/'CHECKPOINT.json', result)
        env = os.environ.copy()
        env.update(BASS_NATIVE_REPO=str(repo), BASS_NATIVE_OUTPUT=str(out),
                   BASS_XACT_SOURCE=str(archive))
        timed_out = False
        with (out/'stdout.log').open('xb') as so, (out/'stderr.log').open('xb') as se:
            proc = subprocess.Popen([executable, '-file', str(HERE/'calibrate.wls')],
                cwd=repo, env=env, stdin=subprocess.DEVNULL, stdout=so, stderr=se,
                start_new_session=True)
            try:
                rc = proc.wait(timeout=args.timeout)
            except subprocess.TimeoutExpired:
                timed_out = True
                try: os.killpg(proc.pid, signal.SIGTERM)
                except ProcessLookupError: pass
                try: rc = proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    try: os.killpg(proc.pid, signal.SIGKILL)
                    except ProcessLookupError: pass
                    rc = proc.wait()
        result.update(process_exit_code=rc, timed_out=timed_out)
        native_path = out/'native.json'
        if native_path.is_file():
            native = json.loads(native_path.read_text(encoding='utf-8'))
            result['native_receipt_sha256'] = sha(native_path)
            result['native_status'] = native.get('status')
            result['native_xact_evaluated'] = native.get('native_xact_evaluated') is True
            checks = native.get('checks', {})
            exact = (isinstance(checks, dict) and set(checks) == set(ids)
                     and sorted(native.get('observed_ids', [])) == sorted(ids)
                     and all(isinstance(v, bool) for v in checks.values()))
            result['exact_test_ids'] = exact
            if exact:
                result['test_counts'] = {'observed': len(checks),
                    'passed': sum(checks.values()), 'failed': sum(not v for v in checks.values())}
            passed = (rc == 0 and not timed_out and exact
                and all(checks.values()) and native.get('failed_ids') == []
                and native.get('messages') == [] and result['native_xact_evaluated']
                and native.get('status') == contract['native_success_status']
                and native.get('stage_id') == contract['stage_id']
                and native.get('activation', {}).get('archive_sha256') == result['archive_sha256'])
            result['status'] = 'PASS_NATIVE_CALIBRATION_ONLY' if passed else 'FAIL_OR_BLOCKED_NATIVE_CALIBRATION'
        else:
            result['status'] = 'BLOCKED_NATIVE_TIMEOUT' if timed_out else 'FAIL_NATIVE_RECEIPT_ABSENT'
    except (KeyboardInterrupt, Exception) as error:
        if proc is not None and proc.poll() is None:
            try: os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError: pass
            proc.wait()
        result['status'] = 'BLOCKED_LAUNCH' if isinstance(error, Blocker) else 'FAILED_LAUNCH_OR_INTERRUPTED'
        result['error_type'] = type(error).__name__
        result['error'] = str(error)
    finally:
        if before is not None:
            try:
                after = git(repo, 'status', '--porcelain', '--untracked-files=all')
                result['worktree_clean_after'] = after == ''
                result['source_head_unchanged'] = git(repo, 'rev-parse', 'HEAD') == result.get('source_head')
                result['input_bytes_unchanged'] = all(sha(repo/p) == h for p,h in inputs.items())
                if not (result['worktree_clean_after'] and result['source_head_unchanged']
                        and result['input_bytes_unchanged']):
                    result['status'] = 'BLOCKED_SOURCE_CHANGED_OR_DIRTY'
                    result['status_porcelain_after'] = after
            except Exception as error:
                result['status'] = 'BLOCKED_POST_RUN_SOURCE_READBACK'
                result['postcheck_error'] = str(error)
        result['elapsed_seconds'] = round(time.monotonic()-start, 6)
        result['logs_sha256'] = {p.name: sha(p) for p in out.glob('*.log')}
        write_new(out/'PROCESS_RECEIPT.json', result)
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    print('artifacts=' + str(out))
    return 0 if result['status'] == 'PASS_NATIVE_CALIBRATION_ONLY' else 2

if __name__ == '__main__':
    raise SystemExit(main())
