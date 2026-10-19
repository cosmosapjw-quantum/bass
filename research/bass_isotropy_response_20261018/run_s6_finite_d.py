#!/usr/bin/env python3
"""S6a: finite-d error certificates on the stored S3 campaign (no re-optimization).

Reads the published ANGULAR_CAMPAIGN.json (SHA256-pinned), evaluates the exact
moment identity A_alpha-A_iso=sum_l k_l(d)M_l/F_alpha at 30 digits with a rigorous
Bernstein tail, and separates constraint (P2->P24 at fixed rays) from angular
refinement (n->2n at fixed constraint). Gates are fixed before execution.
"""
from __future__ import annotations
import argparse
from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
import math
from pathlib import Path
import resource
import sys
import time
import mpmath as mp
import finite_d_error as fde
from s6_io import apply_limits, write_json_once, check_disk

HERE = Path(__file__).resolve().parent
CAMPAIGN = HERE/'evidence_s3/campaign/ANGULAR_CAMPAIGN.json'
CAMPAIGN_SHA256 = '01f3d130d10a318d411f10252f928057dd79a5145ba419aee5094b988102f03d'
LMAX = 100
GATES = {
    'series_vs_direct_abs': 1e-24,        # truncation+tail at 30 digits
    # G3a: |direct|<=(sum|k_l M_l|+tail)/F+floor; G3b: (S6.4) for P2 (m=1), P24 (m=2)
    'stored_vs_direct_abs': 1e-14,        # binary64 campaign + SciPy reference
    'tail_bound_max': 1e-20,              # L=100 must make the tail negligible
    'refinement_rate_ratio': [0.7, 1.4],  # ln|E_n/E_2n|/(2n ln rho*), n>=16, |E|>=1e-11
    'refinement_floor': 1e-11,
}


def s(x, n=20):
    return mp.nstr(x, n)


def coeff_job(d):
    c = fde.kernel_coefficients(d, LMAX)
    a = float(c['reference']['A'])
    tb = fde.tail_bound(d, a, LMAX) if d != 0 else {'tail': 0.0, 'rho_prime': None}
    return d, c, tb


def rule_job(args):
    rid, mode, mu, w, dlist, coeffs = args
    mom = fde.rule_moments(mu, w, LMAX)
    out = {'id': rid, 'moments': {l: s(mom[l]) for l in (2, 4, 6, 8, 10, 12)}, 'd': []}
    for d in dlist:
        if d == 0:
            continue
        cert = fde.certificate(d, mu, w, coeffs[d], mom)
        t = cert['terms']
        out['d'].append({
            'd': d, 'direct': s(cert['direct']), 'series': s(cert['series']),
            'series_minus_direct': float(cert['series']-cert['direct']),
            'bound': s(cert['bound']), 'abs_bound': s(cert['abs_bound']),
            'tail_bound': float(cert['tail_bound']),
            'S6_4_bound': s(cert['low_abs'][{'P2': 1, 'P24': 2}[mode]]/cert['Fmin']+
                            fde.constraint_only_guarantee(d, coeffs[d], {'P2': 1, 'P24': 2}[mode]))
                          if mode in ('P2', 'P24') else None,
            'term_l2': float(t[2]), 'term_l4': float(t[4]), 'term_l6': float(t[6]),
            'term_l8': float(t[8]), 'term_ge10': float(mp.fsum(v for l, v in t.items() if l >= 10)),
            'F': float(cert['F'])})
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--workers', type=int, default=10); a = ap.parse_args()
    if not 1 <= a.workers <= 16:
        raise ValueError('EXECUTION_LIMIT')
    apply_limits()
    a.out.mkdir(parents=True, exist_ok=False); start = time.monotonic()
    raw = CAMPAIGN.read_bytes()
    if hashlib.sha256(raw).hexdigest() != CAMPAIGN_SHA256:
        raise ValueError('STORED_CAMPAIGN_IDENTITY')
    saved = json.loads(raw)
    dlist = [r['d'] for r in saved['continuum_reference']]
    with ProcessPoolExecutor(max_workers=a.workers) as pool:
        coeffs, tails = {}, {}
        for d, c, tb in pool.map(coeff_job, dlist):
            coeffs[d], tails[d] = c, tb
        measured = [r for r in saved['rows'] if r['status'] == 'MEASURED']
        jobs = [(r['id'], r['constraint'], r['mu'], r['weights'], dlist, coeffs) for r in measured]
        certs = {o['id']: o for o in pool.map(rule_job, jobs, chunksize=2)}
    # Coefficient table and constraint-only guarantees.
    table = []
    for d in dlist:
        c = coeffs[d]
        row = {'d': d, 'rho': fde.rho(d) if d else None, 'A_iso': s(c['reference']['A']),
               'k': {l: s(c['k'][l], 25) for l in c['k']}, 'tail_bound_L100': tails[d]['tail'],
               'tail_rho_prime': tails[d]['rho_prime']}
        if d:
            row['constraint_only_guarantee'] = {m: fde.constraint_only_guarantee(d, c, m) for m in range(1, 9)}
            row['required_constraint_order'] = {str(e): fde.required_constraint_order(d, e, c) for e in (1e-3, 1e-6, 1e-9)}
        table.append(row)
    # Gates G1-G3 over all stored rows.
    stored = {(r['id'], v['d']): v['A_error'] for r in measured for v in r['response']}
    g1 = g2 = 0.0; viol = []; s64_checked = 0; s64_margin = None
    with mp.workdps(fde.DPS):
        for rid, o in certs.items():
            for v in o['d']:
                g1 = max(g1, abs(v['series_minus_direct']))
                direct = abs(mp.mpf(v['direct']))
                g2 = max(g2, abs(stored[(rid, v['d'])]-float(mp.mpf(v['direct']))))
                # G3a: sign-free moment bound, compared in mp without relative slack.
                if direct > mp.mpf(v['abs_bound']):
                    viol.append({'gate': 'G3a', 'id': rid, 'd': v['d']})
                # G3b: theorem (S6.4) with only the constrained low moments of the rule.
                if v['S6_4_bound'] is not None:
                    s64_checked += 1
                    margin = float(mp.mpf(v['S6_4_bound'])/max(direct, mp.mpf(1e-300)))
                    s64_margin = margin if s64_margin is None else min(s64_margin, margin)
                    if direct > mp.mpf(v['S6_4_bound']):
                        viol.append({'gate': 'G3b', 'id': rid, 'd': v['d']})
    g3 = not viol
    tmax = max(t['tail'] for t in tails.values())
    # Constraint effect at fixed rays: P2 -> P24 decomposition.
    constraint = []
    for r in measured:
        if r['constraint'] != 'P24':
            continue
        p2 = f"b{r['birth_b']:+.2f}_n{r['n_mu']}_P2"
        if p2 not in certs:
            continue
        for v24, v2 in zip(certs[r['id']]['d'], certs[p2]['d']):
            e24, e2 = float(mp.mpf(v24['direct'])), float(mp.mpf(v2['direct']))
            constraint.append({'b': r['birth_b'], 'n': r['n_mu'], 'd': v24['d'], 'E_P2': e2, 'E_P24': e24,
                               'targeted_l4_change': v24['term_l4']-v2['term_l4'],
                               'collateral_l_ge6_change': (v24['term_l6']+v24['term_l8']+v24['term_ge10'])-
                                                           (v2['term_l6']+v2['term_l8']+v2['term_ge10']),
                               'l2_change': v24['term_l2']-v2['term_l2'],
                               'improved': abs(e24) < abs(e2)})
    # Angular refinement at fixed constraint: n -> 2n.
    refine = []; rate_fail = []
    for r in measured:
        n2 = f"b{r['birth_b']:+.2f}_n{2*r['n_mu']}_{r['constraint']}"
        if n2 not in certs:
            continue
        for v1, v2 in zip(certs[r['id']]['d'], certs[n2]['d']):
            e1, e2 = abs(float(mp.mpf(v1['direct']))), abs(float(mp.mpf(v2['direct'])))
            rs = fde.rho_star(r['birth_b'], v1['d'])
            rec = {'b': r['birth_b'], 'mode': r['constraint'], 'n': r['n_mu'],
                   'd': v1['d'], 'E_n': e1, 'E_2n': e2, 'rho_star': rs}
            if e1 >= GATES['refinement_floor'] and e2 >= GATES['refinement_floor'] and math.isfinite(rs):
                rec['rate_ratio'] = math.log(e1/e2)/(2*r['n_mu']*math.log(rs))
                lo, hi = GATES['refinement_rate_ratio']
                if r['n_mu'] >= 16 and not lo <= rec['rate_ratio'] <= hi:
                    rate_fail.append(rec)
            refine.append(rec)
    gated = [x for x in refine if 'rate_ratio' in x and x['n'] >= 16]
    status = {
        'G1_series_vs_direct': g1 <= GATES['series_vs_direct_abs'],
        'G2_stored_vs_direct': g2 <= GATES['stored_vs_direct_abs'],
        'G3a_sign_free_bound': not any(x['gate'] == 'G3a' for x in viol),
        'G3b_theorem_S6_4': s64_checked > 0 and not any(x['gate'] == 'G3b' for x in viol),
        'G4_tail_negligible': tmax <= GATES['tail_bound_max'],
        'G5_refinement_rate_rho_star': not rate_fail and len(gated) > 0,
    }
    for name, value in [('FINITE_D_KERNEL_TABLE.json', table), ('FINITE_D_CERTIFICATES.json', certs),
                        ('CONSTRAINT_EFFECT.json', constraint), ('REFINEMENT_EFFECT.json', refine)]:
        write_json_once(a.out/name, value, indent=1)
    receipt = {
        'schema': 'bass.s6a.finite_d.v1', 'algorithm': fde.ALGORITHM_ID,
        'status': 'PASS_SCOPED' if all(status.values()) else 'FAIL',
        'gates': GATES, 'gate_results': status,
        'max_series_minus_direct': g1, 'max_stored_minus_direct': g2, 'max_tail_bound': tmax,
        'bound_violations': viol, 'S6_4_points_checked': s64_checked, 'S6_4_min_bound_over_actual': s64_margin, 'refinement_rate_failures': rate_fail,
        'refinement_pairs_gated': len(gated),
        'refinement_rate_ratio_range': [min(x['rate_ratio'] for x in gated), max(x['rate_ratio'] for x in gated)] if gated else None,
        'constraint_pairs': len(constraint), 'constraint_improved': sum(x['improved'] for x in constraint),
        'constraint_worsened': sum(not x['improved'] for x in constraint),
        'stored_campaign_sha256': CAMPAIGN_SHA256, 'measured_rules': len(certs),
        'certificate_points': sum(len(o['d']) for o in certs.values()), 'lmax': LMAX, 'dps': fde.DPS,
        'source_sha256': {n: hashlib.sha256((HERE/n).read_bytes()).hexdigest()
                          for n in ('finite_d_error.py', 'run_s6_finite_d.py', 's6_io.py')},
        'python': sys.version, 'mpmath': mp.__version__, 'workers': a.workers,
        'wall_seconds': time.monotonic()-start,
        'maxrss_kib_self': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        'maxrss_kib_children': resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
        'scope': 'Stored frozen single-birth rules; no optimizer rerun, no native, no coupled history.',
        'continuum_admission': False,
    }
    receipt['disk_bytes_used'] = check_disk(a.out)
    write_json_once(a.out/'RETURN_S6_FINITE_D.json', receipt, indent=2)
    print(json.dumps({k: receipt[k] for k in ('status', 'gate_results', 'max_series_minus_direct',
          'max_stored_minus_direct', 'max_tail_bound', 'refinement_rate_ratio_range', 'constraint_improved',
          'constraint_worsened', 'wall_seconds')}, indent=1))
    if receipt['status'] != 'PASS_SCOPED':
        sys.exit(2)


if __name__ == '__main__':
    main()
