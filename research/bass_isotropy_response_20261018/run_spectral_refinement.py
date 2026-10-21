#!/usr/bin/env python3
"""S6c: compile the pinned REI owner unchanged and run the panel/bin probe.

Gates, predictions, row grid and the SHA256 of the probe, adapter, replica and
this runner are read from a preregistration file that must be committed in git
(clean) before execution (R2; run01 used the weaker PREREGISTRATION.json). Owner staging/verification is imported from the
already verified run_native_adapter.py; that runner and native_probe.rs are
not modified or re-executed.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import resource
import shutil
import subprocess
import time
from run_native_adapter import REI_SHA, SOURCE_ID, RAM, DISK, digest, stage_owner, verify_owner
from s6_io import write_json_once

ROOT = Path(__file__).resolve().parent
PREREG = ROOT/'evidence_s6/spectral/PREREGISTRATION_R2.json'
NEW_FILES = ('native_adapter.rs', 'spectral_probe.rs', 'balance.rs', 'balance_p24.rs')


def expected_grid(prereg):
    m = prereg['matrix']; pb = m['panel_bin']; an = m['angular_at_cps64']
    grid = {('panel_bin', pb['n_mu'], ne, c, pb['b']) for c in pb['cps'] for ne in pb['n_energy']}
    grid |= {('angular_cps64', n, an['n_energy'], 64, b) for n in an['n_mu'] for b in an['b']}
    return grid


def validate(path, prereg):
    g = prereg['gates']
    pred = {p['cps']: p['probe_residual_predicted'] for p in prereg['predictions']}
    grid = expected_grid(prereg)
    recs = [json.loads(l) for l in path.read_text().splitlines() if l.strip()]
    done = recs.pop()
    if done.get('schema') != 'bass.angular.native.s6c.complete.v1' or done.get('rows') != len(grid) or len(recs) != len(grid) \
            or done.get('owner_commit') != REI_SHA or done.get('source_id') != SOURCE_ID:
        raise ValueError('S6C_COMPLETION_IDENTITY')
    keys = [(r['block'], r['n_mu'], r['n_energy'], r['cells_per_segment'], r['b_birth']) for r in recs]
    if len(set(keys)) != len(keys) or set(keys) != grid:
        raise ValueError('S6C_ROW_GRID')
    fails = []
    def check(ok, tag, r):
        if not ok:
            fails.append({'tag': tag, 'row': {k: r[k] for k in ('block', 'n_mu', 'n_energy', 'cells_per_segment', 'b_birth')}})
    for r in recs:
        if any(isinstance(v, float) and not math.isfinite(v) for v in r.values()):
            raise ValueError('S6C_NONFINITE')
        cps = r['cells_per_segment']
        r['predicted'] = pred[cps]; r['native_minus_predicted'] = r['energy_vs_source_moment_relative']-pred[cps]
        check(abs(r['native_minus_predicted']) <= g['native_minus_predicted_abs'], 'PREDICTION', r)
        check(abs(r['photon_vs_source_relative']) <= g['photon_relative_abs'], 'PHOTON', r)
        check(abs(r['ledger_n_residual']) <= g['ledger_relative']*r['inventory_n'] and
              abs(r['ledger_u_residual']) <= g['ledger_relative']*r['inventory_u'], 'LEDGER', r)
        expected = -8/5-10/7*r['energy_p2']+36/35*r['energy_p4']
        check(abs(r['derivative_legendre']-expected) <= g['mapping_abs'], 'MAPPING', r)
        check(abs(r['derivative_central']-expected) <= g['derivative_abs'], 'DERIVATIVE', r)
        check(r['min_weight'] > 0 and abs(r['weight_p2']) <= g['moment_abs'] and abs(r['weight_p4']) <= g['moment_abs'], 'WEIGHTS', r)
    by = {}
    for r in recs:
        if r['block'] == 'panel_bin':
            by.setdefault(r['cells_per_segment'], []).append(r['energy_vs_source_moment_relative'])
    spreads = {c: max(v)-min(v) for c, v in by.items()}
    ratios = {f'{c}->{2*c}': (sum(by[c])/len(by[c]))/(sum(by[2*c])/len(by[2*c])) for c in by if 2*c in by}
    lo, hi = g['cps_doubling_ratio']
    gates = {
        'per_row': not fails,
        'spread_over_n_energy': max(spreads.values()) <= g['spread_over_n_energy_abs'],
        'cps_doubling_ratio': all(lo <= v <= hi for v in ratios.values()),
    }
    ang = [r['energy_vs_source_moment_relative'] for r in recs if r['block'] == 'angular_cps64']
    gates['spread_over_angular'] = max(ang)-min(ang) <= g['spread_over_angular_abs']
    return recs, {'gates': gates, 'row_failures': fails, 'spread_over_n_energy': spreads,
                  'cps_doubling_ratio': ratios, 'angular_spread_cps64': max(ang)-min(ang),
                  'max_abs_native_minus_predicted': max(abs(r['native_minus_predicted']) for r in recs),
                  'max_abs_photon_relative': max(abs(r['photon_vs_source_relative']) for r in recs),
                  'max_derivative_abs': max(abs(r['derivative_central']-(-8/5-10/7*r['energy_p2']+36/35*r['energy_p4'])) for r in recs)}


def main():
    p = argparse.ArgumentParser(); p.add_argument('--out', type=Path, required=True)
    p.add_argument('--rei-repo', type=Path); p.add_argument('--owner-root', type=Path)
    p.add_argument('--rustc'); p.add_argument('--prereg', type=Path); p.add_argument('--workers', type=int, default=4); p.add_argument('--timeout', type=int, default=1800)
    a = p.parse_args()
    if not 1 <= a.workers <= 16 or not 1 <= a.timeout <= 1800:
        raise ValueError('EXECUTION_LIMIT')
    out = a.out.resolve()
    if out.exists():
        raise FileExistsError(out)
    out.mkdir(parents=True); started = time.monotonic(); deadline = started+a.timeout
    prereg_path = (a.prereg or PREREG).resolve()
    prereg = json.loads(prereg_path.read_text())
    receipt = {'schema': 'bass.s6c.spectral_refinement.v1', 'started_utc': datetime.now(timezone.utc).isoformat(),
               'owner_commit': REI_SHA, 'preregistration': str(prereg_path), 'preregistration_sha256': digest(prereg_path.read_bytes()),
               'limits': {'additional_workers': a.workers, 'native_threads': 1, 'ram_bytes': RAM, 'disk_bytes': DISK, 'job_seconds': a.timeout},
               'implementation_sha256': {n: digest((ROOT/n).read_bytes()) for n in NEW_FILES},
               'runner_sha256': digest(Path(__file__).read_bytes()),
               'spectral_residual_sha256': digest((ROOT/'spectral_residual.py').read_bytes()),
               'commands': [], 'status': 'STARTED'}
    def save():
        receipt['elapsed_seconds'] = time.monotonic()-started
        (out/'RETURN_SPECTRAL_REFINEMENT.json').write_text(json.dumps(receipt, indent=2, allow_nan=False)+'\n')
    def limit():
        resource.setrlimit(resource.RLIMIT_AS, (RAM, RAM)); resource.setrlimit(resource.RLIMIT_FSIZE, (DISK, DISK))
    def command(label, args):
        left = deadline-time.monotonic()
        if left <= 0:
            raise TimeoutError('JOB_SECONDS')
        env = os.environ.copy(); env.update({'RUST_TEST_THREADS': '1', 'OMP_NUM_THREADS': '1'})
        t = time.monotonic()
        proc = subprocess.run(list(map(str, args)), capture_output=True, timeout=min(left, 1800), env=env, preexec_fn=limit)
        (out/(label+'.stdout')).write_bytes(proc.stdout); (out/(label+'.stderr')).write_bytes(proc.stderr)
        receipt['commands'].append({'label': label, 'args': list(map(str, args)), 'exit_code': proc.returncode, 'seconds': time.monotonic()-t})
        save()
        if proc.returncode:
            raise RuntimeError('COMMAND_FAILED:'+label)
        return proc.stdout.decode(errors='replace')
    try:
        git = ['git', '-C', str(prereg_path.parent)]
        rel = prereg_path.name
        if subprocess.run(git+['ls-files', '--error-unmatch', rel], capture_output=True).returncode or \
                subprocess.run(git+['diff', '--quiet', 'HEAD', '--', rel]).returncode:
            raise ValueError('PREREGISTRATION_NOT_COMMITTED_CLEAN')
        receipt['preregistration_commit'] = subprocess.run(git+['log', '-1', '--format=%H', '--', rel],
                                                           capture_output=True, text=True).stdout.strip()
        current = {n: digest((ROOT/n).read_bytes()) for n in prereg['pinned_sha256']}
        if current != prereg['pinned_sha256']:
            raise ValueError('PINNED_SOURCE_CHANGED_AFTER_PREREGISTRATION')
        manifest = json.loads((ROOT/'native_owner_manifest.json').read_text())
        if manifest['commit'] != REI_SHA:
            raise ValueError('OWNER_MANIFEST_COMMIT')
        if a.owner_root:
            owner = a.owner_root.resolve(); receipt['source_mode'] = 'EXISTING_EXACT_SOURCE_READBACK'
            receipt['owner_verification'] = verify_owner(owner, manifest)
        else:
            owner = out/'owner_source'
            receipt['source_mode'] = 'PINNED_GIT_BLOBS' if a.rei_repo else 'PINNED_RAW_GITHUB_BLOBS'
            receipt['owner_verification'] = stage_owner(owner, manifest, a.rei_repo, a.workers)
        rustc = a.rustc or shutil.which('rustc')
        if not rustc:
            raise FileNotFoundError('COMPILER_MISSING:rustc')
        receipt['rustc_version'] = command('compiler_version', [rustc, '-Vv'])
        work = out/'build'; work.mkdir()
        for n in NEW_FILES:
            (work/n).write_bytes((ROOT/n).read_bytes())
        rlib = work/'librei_microphysics.rlib'
        command('compile_owner', [rustc, '--crate-name', 'rei_microphysics', '--crate-type', 'rlib', '--edition=2021', '-O',
                                  '-C', 'codegen-units=1', owner/'rust/rei_microphysics/src/lib.rs', '-o', rlib])
        command('compile_spectral_probe', [rustc, '--edition=2021', '-O', '-C', 'codegen-units=1', work/'spectral_probe.rs',
                                           '--extern', 'rei_microphysics='+str(rlib), '-o', work/'spectral_probe'])
        command('measure_spectral_refinement', [work/'spectral_probe', out/'SPECTRAL_REFINEMENT.jsonl'])
        recs, val = validate(out/'SPECTRAL_REFINEMENT.jsonl', prereg)
        write_json_once(out/'SPECTRAL_REFINEMENT_ANALYSIS.json', {'rows': recs, **val}, indent=1)
        receipt['validation'] = val
        receipt['native_output_sha256'] = digest((out/'SPECTRAL_REFINEMENT.jsonl').read_bytes())
        receipt['artifact_sha256'] = {f.name: digest(f.read_bytes()) for f in (work/'spectral_probe', rlib)}
        receipt['artifact_sha256_note'] = 'Build-path dependent; not a reproducibility key. Use native_output_sha256.'
        if receipt['implementation_sha256'] != {n: digest((ROOT/n).read_bytes()) for n in NEW_FILES}:
            raise ValueError('IMPLEMENTATION_CHANGED_DURING_RUN')
        verify_owner(owner, manifest)
        receipt['disk_bytes_used'] = sum(x.stat().st_size for x in out.rglob('*') if x.is_file())
        if receipt['disk_bytes_used'] > DISK:
            raise RuntimeError('DISK_LIMIT')
        receipt['children_peak_rss_kib_linux'] = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
        receipt['status'] = 'PASS_SCOPED_SPECTRAL_REFINEMENT' if all(val['gates'].values()) else 'FAIL_PREREGISTERED_GATE'
        receipt['scope'] = ('Source deposition only: photon/energy totals, ledgers, energy moments and frozen-birth '
                            'linear response vs panels and bins. Not transport, absorption or history convergence.')
    except Exception as e:
        receipt['status'] = 'FAILED'; receipt['failure_type'] = type(e).__name__; receipt['failure'] = str(e)
        save(); raise
    save()
    print(json.dumps({'status': receipt['status'], 'gates': val['gates'], 'seconds': receipt['elapsed_seconds']}))
    if not receipt['status'].startswith('PASS'):
        raise SystemExit(2)


if __name__ == '__main__':
    main()
