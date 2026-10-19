#!/usr/bin/env python3
"""Preregister and run a bounded S7 manufactured closed Einstein/cohort campaign.

Use --write-prereg FILE first. Publish source and that file, then supply either
--git-root CHECKOUT or --publication-receipt JSON with --prereg-commit SHA.
The external receipt must attest remote Git readback, not merely local intent.
This harness requires no NCP-specific source edits.
"""
from __future__ import annotations
import argparse
from dataclasses import asdict, replace
import hashlib
import json
import math
import os
from pathlib import Path
import resource
import subprocess
import sys
import time
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'
import numpy as np
import scipy
from scipy.linalg import expm
import coupled_cohorts as cc
from s6_io import apply_limits, check_disk, write_json_once

HERE = Path(__file__).resolve().parent
SOURCE_FILES = ('coupled_cohorts.py', 'run_s7_coupled.py', 'test_s7_coupled.py',
                'angular_balance.py', 'angular_p24.py', 's6_io.py')
LANE = 'research/bass_isotropy_response_20261018'


def source_hashes():
    return {n: hashlib.sha256((HERE/n).read_bytes()).hexdigest() for n in SOURCE_FILES}


def campaign_definition():
    cases = []
    for K in (16, 32, 64, 128, 256):
        cases.append({'id': f'ref_b03_K{K}', 'axis': 'birth_refinement',
                      'config': asdict(cc.Config(K=K, n=128, mode='source_frame_GL'))})
    for b, tag in ((0.7, '07'), (0.9, '09')):
        cases.append({'id': f'ref_b{tag}_K64', 'axis': 'matched_reference',
                      'config': asdict(cc.Config(K=64, n=128, mode='source_frame_GL', b0=b))})
    for n in (64, 256):
        cases.append({'id': f'ref_sourceGL{n}_K64', 'axis': 'source_frame_reference_refinement',
                      'config': asdict(cc.Config(K=64, n=n, mode='source_frame_GL'))})
    for b, tag in ((0.3, '03'), (0.7, '07'), (0.9, '09')):
        for n in (8, 16, 32):
            for mode in ('prior', 'P2', 'P24'):
                cases.append({'id': f'b{tag}_n{n}_{mode}_K64', 'axis': 'angular',
                              'reference': f'ref_b{tag}_K64',
                              'config': asdict(cc.Config(K=64, n=n, mode=mode, b0=b))})
    return {'schema': 'bass.s7.coupled.preregistration.v1',
            'physics': 'Closed manufactured donor + collisionless radiation + Lambda; not MD14/native owner history.',
            'algorithm': cc.ALGORITHM_ID, 'source_sha256': source_hashes(),
            'cases': cases, 'solver': {'method': 'DOP853', 'rtol': cc.RTOL, 'atol': cc.ATOL, 'max_step': 0.08},
            'gates': dict(cc.GATES),
            'additional_gates': {'duhamel_identity_abs': 2e-11, 'duhamel_order12_vs20_abs': 2e-12,
                                 'reference_n128_vs256_max': 2e-11,
                                 'radiation_linear_error_ratio': [3.5, 4.5],
                                 'isotropic_donor_exact_discrete_relative': 1e-11,
                                 'isotropic_donor_continuous_error_ratio': [3.5, 4.5]},
            'birth_refinement': {'K': [16, 32, 64, 128, 256],
                                 'ratio_gate': None, 'reason': 'Measured convergence diagnostic, no gate inferred after seeing output.'},
            'radiation_linear_benchmark': {'epsilons': [0.01, 0.005, 0.0025], 'x_end': 2.0,
                 'matrix_q_A': [[-1.0, 1.0], [-1.6, 0.0]],
                 'initial': 'q0=epsilon; A0=epsilon; old physical source-frame distribution 1+5epsilon P2',
                 'prediction': 'First-order matrix exponential; exact nonlinear error scales epsilon^2.'},
            'isotropic_donor_benchmark': {'K': [16, 32, 64, 128], 'source_frame_n': 32,
                 'lambda': 0.7, 'birth_end': 0.8, 'x_end': 1.2,
                 'continuous_Er': 'exp(-4x)[Er0+lambda Ed0 expm1((1-lambda)min(x,T))/(1-lambda)]',
                 'discrete_injection_over_continuous': '(1-lambda)/lambda*sinh(lambda Delta/2)/sinh((1-lambda)Delta/2)'},
            'limits': {'workers': 1, 'ram_bytes': 16*1024**3, 'disk_bytes': 4*1024**3, 'job_seconds': 1800},
            'failure_policy': 'Record positive-support infeasibility with geometry/witness; retain numerical failures; no negative weights or gate relaxation.',
            'not_admitted': ['MD14 feedback', 'native cohort transport', 'spectral convergence', 'production', 'full EoR', 'merge']}


def verify_preregistration(path, commit, receipt_path=None, git_root=None):
    raw = path.read_bytes()
    plan = json.loads(raw)
    if plan != campaign_definition():
        raise ValueError('S7_PREREGISTRATION_SOURCE_OR_GATE_CHANGED')
    if not commit or len(commit) != 40 or any(c not in '0123456789abcdef' for c in commit):
        raise ValueError('S7_PREREGISTRATION_COMMIT_REQUIRED')
    sha256 = hashlib.sha256(raw).hexdigest()
    blob = hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
    if git_root:
        rel = str(path.resolve().relative_to(git_root.resolve()))
        remote = subprocess.run(['git', '-C', str(git_root), 'show', commit+':'+rel],
                                check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30).stdout
        if remote != raw:
            raise ValueError('S7_COMMITTED_PREREGISTRATION_MISMATCH')
        for name, digest in source_hashes().items():
            source = subprocess.run(['git', '-C', str(git_root), 'show', commit+':'+LANE+'/'+name],
                                    check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30).stdout
            if hashlib.sha256(source).hexdigest() != digest:
                raise ValueError('S7_COMMITTED_SOURCE_MISMATCH: '+name)
        method = 'git show exact committed preregistration and six source files'
    elif receipt_path:
        receipt = json.loads(receipt_path.read_text())
        if (receipt.get('commit') != commit or receipt.get('preregistration_sha256') != sha256 or
            receipt.get('preregistration_git_blob_sha') != blob or receipt.get('source_sha256') != source_hashes() or
            receipt.get('remote_readback_verified') is not True):
            raise ValueError('S7_REMOTE_PUBLICATION_RECEIPT_MISMATCH')
        method = 'parent Git connector exact remote tree/ref/blob readback receipt'
    else:
        raise ValueError('S7_COMMITTED_READBACK_REQUIRED')
    return plan, {'commit': commit, 'preregistration_sha256': sha256,
                  'preregistration_git_blob_sha': blob, 'verification_method': method}


def linear_benchmark(plan):
    spec = plan['radiation_linear_benchmark']
    matrix = np.array(spec['matrix_q_A'])
    xs = np.linspace(0, spec['x_end'], 161)
    rows, norms, hamiltonian = [], [], []
    for epsilon in spec['epsilons']:
        config = cc.Config(K=0, mode='source_frame_GL', n=128, b0=0, donor0=0,
                           old_isotropic=0, old_anisotropic=1, eta=5*epsilon,
                           cosmological_constant=0, decay_lambda=0, x_end=spec['x_end'],
                           y0=epsilon/math.sqrt(1-epsilon**2))
        history = cc.solve_history(config)
        diag = cc.diagnostics(history, 161)
        exact = history.sample(xs)
        linear = np.array([expm(matrix*x) @ np.array([epsilon, epsilon]) for x in xs])
        actual = np.array([[r['y']/r['h'], r['A']] for r in exact])
        error = float(np.max(np.abs(actual-linear)))
        norms.append(error); hamiltonian.append(diag['max_hamiltonian_relative'])
        rows.append({'epsilon': epsilon, 'max_absolute_error': error,
                     'error_over_epsilon_squared': error/epsilon**2,
                     'gate_results': diag['gate_results'], 'max_hamiltonian_relative': diag['max_hamiltonian_relative'],
                     'trajectory': [{'x': float(x), 'q': float(a[0]), 'A': float(a[1]),
                                     'linear_q': float(v[0]), 'linear_A': float(v[1])}
                                    for x, a, v in zip(xs, actual, linear)]})
    ratios = [a/b for a, b in zip(norms[:-1], norms[1:])]
    lo, hi = plan['additional_gates']['radiation_linear_error_ratio']
    return {'schema': 'bass.s7.coupled.radiation_linear_benchmark.v1', 'rows': rows,
            'error_ratios': ratios, 'order2_gate': all(lo <= r <= hi for r in ratios),
            'all_conservation_gates': all(all(r['gate_results'].values()) for r in rows),
            'max_hamiltonian_relative': max(hamiltonian),
            'reference': 'Independent first-order Einstein-Vlasov q,A matrix exponential; finite epsilon histories use exact nonlinear kernels.'}


def isotropic_donor_benchmark(plan):
    spec = plan['isotropic_donor_benchmark']
    rows = []
    for K in spec['K']:
        config = cc.Config(K=K, n=spec['source_frame_n'], mode='source_frame_GL', y0=0, eta=0,
                           decay_lambda=spec['lambda'], birth_end=spec['birth_end'], x_end=spec['x_end'])
        history = cc.solve_history(config)
        diag = cc.diagnostics(history, 61)
        measured = history.observe(config.x_end)
        x, lam, du = config.x_end, config.decay_lambda, config.birth_end/K
        injected_continuous = lam*config.donor0*math.expm1((1-lam)*config.birth_end)/(1-lam)
        injection_ratio = (1-lam)/lam*math.sinh(lam*du/2)/math.sinh((1-lam)*du/2)
        Er0 = config.old_isotropic+config.old_anisotropic
        continuous_E = math.exp(-4*x)*(Er0+injected_continuous)
        discrete_E = math.exp(-4*x)*(Er0+injected_continuous*injection_ratio)
        exact_donor = config.donor0*math.exp(-3*x-lam*config.birth_end)
        exact_h = math.sqrt(exact_donor+discrete_E+config.cosmological_constant)
        rows.append({'K': K, 'measured_Er': measured['E_radiation'], 'continuous_Er': continuous_E,
                     'exact_discrete_Er': discrete_E, 'injection_ratio': injection_ratio,
                     'predicted_leading_injection_bias': (2*lam-1)*du**2/24,
                     'continuous_Er_error': measured['E_radiation']-continuous_E,
                     'discrete_Er_relative': abs(measured['E_radiation']-discrete_E)/discrete_E,
                     'discrete_h_relative': abs(measured['h']-exact_h)/exact_h,
                     'gate_results': diag['gate_results']})
    ratios = [a['continuous_Er_error']/b['continuous_Er_error'] for a, b in zip(rows[:-1], rows[1:])]
    lo, hi = plan['additional_gates']['isotropic_donor_continuous_error_ratio']
    return {'schema': 'bass.s7.coupled.isotropic_donor_benchmark.v1', 'rows': rows,
            'continuous_error_ratios': ratios, 'order2_gate': all(lo <= r <= hi for r in ratios),
            'exact_discrete_gate': all(max(r['discrete_Er_relative'], r['discrete_h_relative']) <=
                                       plan['additional_gates']['isotropic_donor_exact_discrete_relative'] for r in rows),
            'all_conservation_gates': all(all(r['gate_results'].values()) for r in rows)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-prereg', type=Path)
    parser.add_argument('--prereg', type=Path)
    parser.add_argument('--prereg-commit')
    parser.add_argument('--publication-receipt', type=Path)
    parser.add_argument('--git-root', type=Path)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    if args.write_prereg:
        args.write_prereg.parent.mkdir(parents=True, exist_ok=True)
        write_json_once(args.write_prereg, campaign_definition(), indent=2)
        print('PREREGISTRATION_WRITTEN '+str(args.write_prereg)); return
    if not args.prereg or not args.out:
        parser.error('--prereg and --out are required for execution')
    plan, publication = verify_preregistration(args.prereg, args.prereg_commit, args.publication_receipt, args.git_root)
    apply_limits()
    args.out.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    histories, summaries, failures = {}, [], []
    for case in plan['cases']:
        t0 = time.monotonic()
        try:
            history = cc.solve_history(cc.Config(**case['config']))
            diag = cc.diagnostics(history)
            histories[case['id']] = history
            write_json_once(args.out/(case['id']+'.json'), {'case': case, **diag}, indent=1)
            summary = {k: v for k, v in diag.items() if k not in ('trajectory', 'events')}
            summaries.append({'id': case['id'], 'axis': case['axis'], 'config': case['config'],
                              'seconds': time.monotonic()-t0, **summary})
            print(case['id']+' '+('PASS' if all(diag['gate_results'].values()) else 'FAIL_GATES'), flush=True)
        except cc.BirthRuleFailure as failure:
            rec = {'id': case['id'], 'config': case['config'], **failure.record}
            failures.append(rec)
            write_json_once(args.out/(case['id']+'.failure.json'), rec, indent=2)
            print(case['id']+' '+failure.record['error'], flush=True)
        except (ValueError, ArithmeticError, RuntimeError) as failure:
            rec = {'id': case['id'], 'config': case['config'], 'kind': 'implementation_or_numerical',
                   'error': type(failure).__name__+': '+str(failure)}
            failures.append(rec); write_json_once(args.out/(case['id']+'.failure.json'), rec, indent=2)
            print(case['id']+' UNEXPECTED_FAILURE '+str(failure), flush=True)
        check_disk(args.out)
    xs = np.linspace(0, cc.Config().x_end, 241)
    quantities = ('h', 'b', 'y', 'E_donor', 'E_radiation', 'Pi', 'Sigma')
    angular = []
    for case in plan['cases']:
        if case['axis'] != 'angular' or case['id'] not in histories:
            continue
        hist, ref = histories[case['id']], histories[case['reference']]
        a, b = hist.sample(xs), ref.sample(xs)
        differences = [{q: row[q]-r[q] for q in quantities} | {'x': row['x']} for row, r in zip(a, b)]
        forcing12 = cc.forcing_comparison(hist, ref, 12)
        forcing20 = cc.forcing_comparison(hist, ref, 20)
        forcing12['order12_vs20_abs'] = abs(forcing12['exact_duhamel']-forcing20['exact_duhamel'])
        angular.append({'id': case['id'], 'reference': case['reference'],
                        'max_abs_difference': {q: max(abs(r[q]) for r in differences) for q in quantities},
                        'endpoint_difference': differences[-1], 'trajectory_difference': differences,
                        'forcing': forcing12})
    birth = []
    for K in (16, 32, 64):
        a, b, c = (histories[f'ref_b03_K{k}'].observe(cc.Config().x_end) for k in (K, 2*K, 4*K))
        birth.append({'K': K, 'same_source_frame_n': 128,
                      'endpoint_difference_ratios': {q: (a[q]-b[q])/(b[q]-c[q]) if abs(b[q]-c[q]) > 1e-14 else None for q in quantities},
                      'coarse_minus_fine': {q: a[q]-b[q] for q in quantities}})
    ref128 = histories['ref_b03_K64'].sample(xs)
    ref256 = histories['ref_sourceGL256_K64'].sample(xs)
    reference_error = max(abs(a[q]-b[q]) for a, b in zip(ref128, ref256) for q in quantities)
    benchmark = linear_benchmark(plan)
    donor_benchmark = isotropic_donor_benchmark(plan)
    write_json_once(args.out/'RADIATION_LINEAR_BENCHMARK.json', benchmark, indent=1)
    write_json_once(args.out/'ISOTROPIC_DONOR_BENCHMARK.json', donor_benchmark, indent=2)
    write_json_once(args.out/'ANGULAR_COMPARISONS.json', angular, indent=1)
    write_json_once(args.out/'BIRTH_REFINEMENT.json', birth, indent=2)
    gates = {'all_completed_history_gates': all(all(s['gate_results'].values()) for s in summaries),
             'no_unexpected_failure': all(f['kind'] == 'feasibility' for f in failures),
             'duhamel_identity': all(a['forcing']['exact_identity_abs'] <= plan['additional_gates']['duhamel_identity_abs'] for a in angular),
             'duhamel_quadrature': all(a['forcing']['order12_vs20_abs'] <= plan['additional_gates']['duhamel_order12_vs20_abs'] for a in angular),
             'source_frame_reference': reference_error <= plan['additional_gates']['reference_n128_vs256_max'],
             'radiation_linear_order2': benchmark['order2_gate'],
             'radiation_linear_conservation': benchmark['all_conservation_gates'],
             'isotropic_donor_order2': donor_benchmark['order2_gate'],
             'isotropic_donor_exact_discrete': donor_benchmark['exact_discrete_gate'],
             'isotropic_donor_conservation': donor_benchmark['all_conservation_gates']}
    receipt = {'schema': 'bass.s7.coupled.return.v1',
               'status': 'PASS_SCOPED' if all(gates.values()) else 'FAIL',
               'gate_results': gates, 'preregistration': publication, 'source_sha256': source_hashes(),
               'cases_attempted': len(plan['cases']), 'cases_completed': len(summaries),
               'cases': summaries, 'failures': failures,
               'max_hamiltonian_relative': max(s['max_hamiltonian_relative'] for s in summaries),
               'max_cohort_energy_relative': max(s['max_cohort_energy_relative'] for s in summaries),
               'max_event_energy_relative': max(s['max_event_energy_relative'] for s in summaries),
               'max_duhamel_identity_abs': max(a['forcing']['exact_identity_abs'] for a in angular),
               'reference_n128_vs256_max': reference_error,
               'radiation_linear_error_ratios': benchmark['error_ratios'],
               'isotropic_donor_continuous_error_ratios': donor_benchmark['continuous_error_ratios'],
               'birth_refinement': birth,
               'python': sys.version, 'numpy': np.__version__, 'scipy': scipy.__version__,
               'wall_seconds': time.monotonic()-started,
               'maxrss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
               'disk_bytes_used': check_disk(args.out),
               'limits': plan['limits'], 'NCP': 'NOT_USED_FOR_THIS_LOCAL_MANUFACTURED_SCOPE',
               'scope': plan['physics'], 'not_admitted': plan['not_admitted']}
    write_json_once(args.out/'RETURN_S7_COUPLED.json', receipt, indent=2)
    print(json.dumps({k: receipt[k] for k in ('status', 'gate_results', 'cases_attempted', 'cases_completed',
                                            'max_hamiltonian_relative', 'max_cohort_energy_relative',
                                            'radiation_linear_error_ratios', 'wall_seconds')}, indent=2))
    return 0 if all(gates.values()) else 2


if __name__ == '__main__':
    sys.exit(main())
