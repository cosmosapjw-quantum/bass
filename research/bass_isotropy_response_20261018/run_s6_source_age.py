#!/usr/bin/env python3
"""S6d: cohort composition in a prescribed (uncoupled) LRS geometry.

Separates birth-time quadrature (K cohorts) from angular error (n, constraint)
for the composite U and DeltaP. Gates are fixed before execution. No Einstein
feedback, no native transport, no existing radiation stock.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import resource
import sys
import time
import numpy as np
import source_age as sa

from s6_io import apply_limits, write_json_once, check_disk

HERE = Path(__file__).resolve().parent
K_LIST = [16, 32, 64, 128]
N_LIST = [8, 16, 32]
MODES = ['prior', 'P2', 'P24']
X_OBS = [0.5, 0.85, 0.9, 1.0]
GATES = {'identity_relative': 1e-12, 'birth_quadrature_ratio': [3.5, 4.5]}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out', type=Path, required=True); a = ap.parse_args()
    apply_limits()
    a.out.mkdir(parents=True, exist_ok=False); start = time.monotonic()
    # Continuum-angular reference: Richardson on midpoint births.
    u1, w1 = sa.cohorts(512); u2, w2 = sa.cohorts(1024)
    ref = {}
    for x in X_OBS:
        s1, s2 = sa.compose_iso(x, u1, w1), sa.compose_iso(x, u2, w2)
        ref[x] = tuple((4*b-c)/3 for b, c in zip(s2, s1))
    iso = {(K, x): sa.compose_iso(x, *sa.cohorts(K)) for K in K_LIST for x in X_OBS}
    rows, rejects, idmax = [], [], 0.0
    for K in K_LIST:
        u, w = sa.cohorts(K)
        for n in N_LIST:
            for mode in MODES:
                try:
                    rules = [sa.rule(sa.b_of_x(uk), n, mode) for uk in u]
                except (ValueError, ArithmeticError) as e:
                    rejects.append({'K': K, 'n': n, 'mode': mode, 'error': str(e)}); continue
                for x in X_OBS:
                    U, P = sa.compose(x, u, w, rules)
                    res, Uc = sa.identity_residual(x, u, w, rules)
                    idmax = max(idmax, abs(res)/Uc)
                    Ui, Pi = iso[(K, x)]
                    rows.append({'K': K, 'n': n, 'mode': mode, 'x': x, 'U': float(U), 'DeltaP': P,
                                 'A': P/U, 'identity_relative': abs(res)/Uc,
                                 'angular_dP': P-Pi, 'angular_dU': U-Ui,
                                 'angular_dA': P/U-Pi/Ui,
                                 'leading_P4_prediction_dP': sa.leading_p4(x, u, w, rules) if mode == 'P2' else None,
                                 'birth_quadrature_dP': Pi-ref[x][1], 'birth_quadrature_dU': Ui-ref[x][0],
                                 'total_dP': P-ref[x][1]})
    ratios = []
    for x in X_OBS:
        for K in K_LIST[:-1]:
            for j in (0, 1):
                e1, e2 = iso[(K, x)][j]-ref[x][j], iso[(2*K, x)][j]-ref[x][j]
                ratios.append({'x': x, 'K': K, 'quantity': 'U' if j == 0 else 'DeltaP', 'ratio': e1/e2})
    lo, hi = GATES['birth_quadrature_ratio']
    gates = {'identity': bool(idmax <= GATES['identity_relative']),
             'birth_quadrature_order2': bool(all(lo <= r['ratio'] <= hi for r in ratios))}
    write_json_once(a.out/'SOURCE_AGE_ROWS.json',
                    {'rows': rows, 'birth_ratios': ratios, 'reference': {str(k): v for k, v in ref.items()}}, indent=1)
    k128 = [r for r in rows if r['K'] == 128 and r['x'] == 1.0]
    receipt = {'schema': 'bass.s6d.source_age.v1', 'status': 'PASS_SCOPED' if all(gates.values()) else 'FAIL',
               'gates': GATES, 'gate_results': gates, 'max_identity_relative': idmax,
               'birth_ratio_range': [min(r['ratio'] for r in ratios), max(r['ratio'] for r in ratios)],
               'rejections': rejects, 'rows': len(rows),
               'angular_dA_at_x1_K128': {f"{r['mode']}_n{r['n']}": r['angular_dA'] for r in k128},
               'birth_dP_at_x1': {K: iso[(K, 1.0)][1]-ref[1.0][1] for K in K_LIST},
               'geometry': 'b=0.15 sin(2x)+0.1x prescribed; j=exp(-((u-0.4)/0.2)^2) on [0,0.8]',
               'coupled_einstein_feedback': 'NOT_RUN', 'native': 'NOT_RUN',
               'source_sha256': {n: hashlib.sha256((HERE/n).read_bytes()).hexdigest() for n in
                                 ('source_age.py', 'run_s6_source_age.py', 'angular_balance.py', 'angular_p24.py', 's6_io.py')},
               'python': sys.version, 'numpy': np.__version__, 'wall_seconds': time.monotonic()-start,
               'maxrss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    receipt['disk_bytes_used'] = check_disk(a.out)
    write_json_once(a.out/'RETURN_S6_SOURCE_AGE.json', receipt, indent=2)
    print(json.dumps({k: receipt[k] for k in ('status', 'gate_results', 'max_identity_relative', 'birth_ratio_range',
                                              'angular_dA_at_x1_K128', 'wall_seconds')}, indent=1))
    print('rejections', len(rejects))
    if receipt['status'] != 'PASS_SCOPED':
        sys.exit(2)


if __name__ == '__main__':
    main()
