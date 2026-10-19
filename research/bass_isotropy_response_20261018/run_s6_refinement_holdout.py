#!/usr/bin/env python3
"""S6a held-out check of the angular-refinement rate rho*=min(rho(b),rho(b+d)).

The S6a r1 rate gate failed in the pre-asymptotic regime. Its threshold
2n ln(rho*)>=10 was read off r1 data, so it is tested here on a disjoint
(b, n, d) grid with gates fixed before execution. Existing verified projectors
are only called on new rules; the stored S3 campaign is not rerun.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import resource
import sys
import time
import mpmath as mp
import finite_d_error as fde
from angular_balance import lrs_rule, project as project2
from angular_p24 import project as project24

from s6_io import apply_limits, write_json_once, check_disk

HERE = Path(__file__).resolve().parent
BIRTH_B = [-0.5, 0.5, 0.7, 0.9]
N_MU = [12, 24, 48, 96, 192]
D_SWEEP = [-0.15, -0.05, 0.05, 0.15]
GATES = {
    'asymptotic_x_min': 10.0,          # x=2n ln rho*
    'asymptotic_ratio': [0.7, 1.4],
    'all_pairs_ratio_max': 1.4,        # never faster than rho*^{-2n} by >40%
    'floor': 1e-11,
}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out', type=Path, required=True); a = ap.parse_args()
    apply_limits()
    a.out.mkdir(parents=True, exist_ok=False); start = time.monotonic()
    refs = {d: fde.iso_reference(d)['A'] for d in D_SWEEP}
    rows = []
    for b in BIRTH_B:
        for n in N_MU:
            mu, q = lrs_rule(b, n)
            for mode in ('prior', 'P2', 'P24'):
                rec = {'b': b, 'n': n, 'mode': mode}
                try:
                    w = q if mode == 'prior' else (project2(mu, q).weights if mode == 'P2' else project24(mu, q).weights)
                except (ValueError, ArithmeticError) as e:
                    rec.update(status='REJECTED', error=str(e)); rows.append(rec); continue
                errs = {}
                with mp.workdps(fde.DPS):
                    for d in D_SWEEP:
                        _, _, _, R, D = fde._ctx(d)
                        ws = [mp.mpf(float(x)) for x in w]; ms = [mp.mpf(float(x)) for x in mu]
                        F = mp.fsum(wi*R(m) for wi, m in zip(ws, ms)); G = mp.fsum(wi*D(m) for wi, m in zip(ws, ms))
                        errs[d] = float(G/F-refs[d])
                rec.update(status='MEASURED', E=errs); rows.append(rec)
    pairs = []; fails = []
    idx = {(r['b'], r['n'], r['mode']): r for r in rows if r['status'] == 'MEASURED'}
    for (b, n, mode), r in idx.items():
        r2 = idx.get((b, 2*n, mode))
        if r2 is None:
            continue
        for d in D_SWEEP:
            e1, e2 = abs(r['E'][d]), abs(r2['E'][d]); rs = fde.rho_star(b, d)
            if e1 < GATES['floor'] or e2 < GATES['floor']:
                continue
            x = 2*n*math.log(rs); ratio = math.log(e1/e2)/x
            p = {'b': b, 'n': n, 'mode': mode, 'd': d, 'E_n': e1, 'E_2n': e2, 'rho_star': rs, 'x': x, 'ratio': ratio}
            lo, hi = GATES['asymptotic_ratio']
            if ratio > GATES['all_pairs_ratio_max'] or (x >= GATES['asymptotic_x_min'] and not lo <= ratio <= hi):
                fails.append(p)
            pairs.append(p)
    asym = [p for p in pairs if p['x'] >= GATES['asymptotic_x_min']]
    status = 'PASS_SCOPED' if asym and not fails else 'FAIL'
    write_json_once(a.out/'HOLDOUT_ROWS.json', {'rows': rows, 'pairs': pairs}, indent=1)
    receipt = {'schema': 'bass.s6a.refinement_holdout.v1', 'status': status, 'gates': GATES,
               'grid': {'b': BIRTH_B, 'n': N_MU, 'd': D_SWEEP},
               'rules_attempted': len(rows), 'rules_measured': len(idx),
               'rejections': [{k: r[k] for k in ('b', 'n', 'mode', 'error')} for r in rows if r['status'] != 'MEASURED'],
               'pairs': len(pairs), 'asymptotic_pairs': len(asym), 'failures': fails,
               'asymptotic_ratio_range': [min(p['ratio'] for p in asym), max(p['ratio'] for p in asym)] if asym else None,
               'all_ratio_max': max(p['ratio'] for p in pairs) if pairs else None,
               'preasymptotic_ratio_min': min((p['ratio'] for p in pairs if p['x'] < GATES['asymptotic_x_min']), default=None),
               'source_sha256': {n: hashlib.sha256((HERE/n).read_bytes()).hexdigest() for n in
                                 ('finite_d_error.py', 'run_s6_refinement_holdout.py', 'angular_balance.py', 'angular_p24.py', 's6_io.py')},
               'python': sys.version, 'wall_seconds': time.monotonic()-start,
               'maxrss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    receipt['disk_bytes_used'] = check_disk(a.out)
    write_json_once(a.out/'RETURN_S6_REFINEMENT_HOLDOUT.json', receipt, indent=2)
    print(json.dumps({k: receipt[k] for k in ('status', 'rules_measured', 'pairs', 'asymptotic_pairs',
          'asymptotic_ratio_range', 'all_ratio_max', 'preasymptotic_ratio_min', 'wall_seconds')}, indent=1))
    print('failures', len(fails), 'rejections', len(receipt['rejections']))
    if status != 'PASS_SCOPED':
        sys.exit(2)


if __name__ == '__main__':
    main()
