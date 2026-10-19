#!/usr/bin/env python3
"""Preregister, publish, then run the bounded S8 full birth-memory tangent test.

Eight integrations: one primary analytic base with four tangent columns,
six symmetric nonlinear perturbations, and one source-frame GL gauge history.
No S7 campaign or measured-forcing Duhamel calculation is rerun.
"""
from __future__ import annotations
import argparse
from dataclasses import asdict, replace
import hashlib
import json
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
import coupled_cohorts as cc
import s8_tangent as st
import s8_tangent_math as sm
from s6_io import apply_limits, check_disk, write_json_once

HERE = Path(__file__).resolve().parent
LANE = 'research/bass_isotropy_response_20261018'
REPO = 'cosmosapjw-quantum/bass'
PREREGISTRATION_PATH = LANE+'/evidence_s8_tangent/PREREGISTRATION.json'
PUBLICATION_SCHEMA = 'bass.git.preregistered.file.v1'
RECOVERED_HEAD = 'fe083a28e066a95e2191bcc6a090adf53605453f'
FROZEN_SOURCE_SHA256 = {
    'coupled_cohorts.py': 'dbdae568fd47a3ffd041ebb47ae09ffefb4b026369ad5f73e48b8d8f2a155c58',
    'angular_balance.py': '1ed6e5d9ea865684fda255055acac3c10efef5d0131118bc568260b0d55a21e9',
    'angular_p24.py': '1d603fcd99d55146a351537564d8a36aad068bb016c83e7e282c9925e9710992',
    's6_io.py': '6ba2504bf5328c722f166e01cfcc2c343c7b2a4cc1e55f1ff46cfd55c8f0ddee',
}
NEW_SOURCES = ('s8_tangent_math.py', 's8_tangent.py', 'run_s8_tangent.py', 'test_s8_tangent.py')
SKILL_CONTEXT = {
    'name': 'physmath-research-loop', 'version': '1.3.0',
    'package': 'skill://plugins_6acdfbba921881919e0c17843706aef4/physmath-research-loop',
    'resources_read': ['SKILL.md', 'references/POLICY_INTEGRATION.md', 'references/CODING_LOOP.md',
                       'references/THEORY_LOOP.md', 'references/SUBAGENT_MODE.md'],
    'selected_scope': 'S8 theory R3-R9 and coding C2-C9; publication/readback before scientific campaign',
    'applied': ['reuse frozen S7 evidence without replay', 'positive new-birth-only projection',
                'exact admission unchanged', 'one production/verification pass with complementary independent review',
                'typed source identity and bounded productive repair'],
    'worker': '/root/s6_backup_intake', 'parent': '/root', 'independent_theory_reviewer': '/root/s6_rank1',
}


def source_hashes():
    return {name: hashlib.sha256((HERE/name).read_bytes()).hexdigest()
            for name in (*FROZEN_SOURCE_SHA256, *NEW_SOURCES)}


def primary_config():
    return cc.Config(K=32, n=16, mode='P24', b0=0.3, y0=0.08)


def campaign_definition():
    hashes = source_hashes()
    if any(hashes[name] != digest for name, digest in FROZEN_SOURCE_SHA256.items()):
        raise ValueError('S8_FROZEN_S7_SOURCE_CHANGED')
    return {'schema': 'bass.s8.full_birth_memory_tangent.preregistration.v1',
            'algorithm': st.ALGORITHM_ID, 'source_sha256': hashes,
            'frozen_S7_source_sha256': FROZEN_SOURCE_SHA256, 'recovered_head_before_research': RECOVERED_HEAD,
            'primary': {'config': asdict(primary_config()), 'parameter': 'y0', 'tangent_modes': list(st.CONTROLS),
                        'parameter_convention': 'Derivative at fixed x and fixed Hstar; event x and donor amplitudes fixed.',
                        'initial_tangent_h_b_y': ['y0/h0', 0, 1],
                        'epsilon_values': [0.02, 0.01, 0.005],
                        'sample_count': 121, 'comparison_x_start': 0.2},
            'gauge': {'config': asdict(replace(primary_config(), K=8, mode='source_frame_GL')),
                      'parameter': 'b0', 'modes': ['full'],
                      'convention': 'Shift current b and every birth b together; source-frame mu/alpha fixed.',
                      'expected_h_b_y': [0, 1, 0]},
            'solver': {'method': 'DOP853', 'rtol': cc.RTOL, 'atol': cc.ATOL, 'max_step': 0.08},
            'new_birth_rule': {'existing_P24_internal_atol': sm.INTERNAL_ATOL,
                               'exact_admission_gate_rational': '3/1000000000000000',
                               'derivative': 'Smooth ideal positive KL optimum at stored approximate optimum; not stopping-branch derivative.'},
            'gates': {'primal': dict(cc.GATES),
                      'linearized_constraint_scaled': st.LINEARIZED_CONSTRAINT_ATOL,
                      'linearized_constraint_propagation_scaled': st.LINEARIZED_CONSTRAINT_ATOL,
                      'per_cohort_tangent_energy_relative': st.TANGENT_ENERGY_ATOL,
                      'source_event_tangent_energy_scaled': st.TANGENT_EVENT_ATOL,
                      'moment_derivative_abs': sm.TANGENT_MOMENT_ATOL,
                      'covariance_min_eigenvalue': sm.COV_MIN_EIGENVALUE,
                      'covariance_max_condition': sm.COV_MAX_CONDITION,
                      'central_difference_order2_ratios': [3.5, 4.5],
                      'ratio_quantities': ['b', 'y', 'h_b_y_joint'],
                      'finest_central_h_b_y_max_abs': 2e-5,
                      'fine_richardson_h_b_y_max_abs': 1e-8,
                      'negative_control_y_min_abs': 1e-5,
                      'negative_control_over_full_error_min': 100,
                      'source_frame_gauge_h_y_abs': 1e-11,
                      'source_frame_gauge_b_minus_one_abs': 1e-11},
            'negative_controls': {
                'omit_birth_memory': 'Drop only -R_d/D_d times birth-b sensitivity; keep mu_b and alpha_b terms.',
                'omit_mu_b': 'Drop only the moving source-frame ray-direction term.',
                'omit_alpha_b': 'Drop only the KL weight derivative term.',
                'prior_score_note': 'Raw prior log score 6P2 lies in the feature span, so consistent omission can shift only lambda_b; not a required failing control.'},
            'finite_difference_contract': 'Use actual symmetric nonlinear S8 histories only for comparison; analytic RHS contains no finite differences.',
            'richardson': '(4 D(epsilon=0.005)-D(epsilon=0.01))/3',
            'integration_count': {'primary_analytic_with_controls': 1, 'nonlinear_fd': 6, 'gauge_analytic': 1},
            'limits': {'workers': 1, 'ram_bytes': 16*1024**3, 'disk_bytes': 4*1024**3, 'job_seconds': 1800},
            'failure_policy': 'Retain feasibility/rank/conditioning/exact-moment/numerical failures; no pseudoinverse, negative weights or tolerance relaxation.',
            'scope': 'Full birth-memory tangent of closed manufactured donor+radiation+Lambda; old physical stock transported without projection.',
            'not_admitted': ['differentiability across feasibility/rank boundaries', 'exact derivative of discrete stopping decisions',
                             'continuum angular accuracy', 'actual MD14/native spectral-owner feedback',
                             'native finite-bin photon/energy conservation', 'production', 'full EoR', 'merge'],
            'skill_context_used': SKILL_CONTEXT}


def verify_preregistration(path, commit, receipt_path=None, git_root=None):
    raw = path.read_bytes(); plan = json.loads(raw)
    if plan != campaign_definition():
        raise ValueError('S8_PREREGISTRATION_SOURCE_OR_CONTRACT_CHANGED')
    if not commit or len(commit) != 40 or any(c not in '0123456789abcdef' for c in commit):
        raise ValueError('S8_PUBLICATION_COMMIT_REQUIRED')
    digest = hashlib.sha256(raw).hexdigest()
    blob = hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
    if git_root:
        rel = str(path.resolve().relative_to(git_root.resolve()))
        if rel != PREREGISTRATION_PATH:
            raise ValueError('S8_COMMITTED_PREREGISTRATION_PATH_MISMATCH')
        published = subprocess.run(['git', '-C', str(git_root), 'show', commit+':'+rel],
                                   check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30).stdout
        if published != raw:
            raise ValueError('S8_COMMITTED_PREREGISTRATION_MISMATCH')
        for name, sha in source_hashes().items():
            source = subprocess.run(['git', '-C', str(git_root), 'show', commit+':'+LANE+'/'+name],
                                    check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30).stdout
            if hashlib.sha256(source).hexdigest() != sha:
                raise ValueError('S8_COMMITTED_SOURCE_MISMATCH: '+name)
        method = 'git show exact committed preregistration and eight source files'
    elif receipt_path:
        receipt = json.loads(receipt_path.read_text())
        if (receipt.get('schema') != PUBLICATION_SCHEMA or receipt.get('repo') != REPO or
            receipt.get('path') != PREREGISTRATION_PATH or receipt.get('commit') != commit or
            receipt.get('preregistration_sha256') != digest or
            receipt.get('preregistration_git_blob_sha') != blob or receipt.get('source_sha256') != source_hashes() or
            receipt.get('remote_readback_verified') is not True):
            raise ValueError('S8_REMOTE_PUBLICATION_RECEIPT_MISMATCH')
        method = 'parent Git connector exact remote ref/tree/blob readback receipt'
    else:
        raise ValueError('S8_COMMITTED_READBACK_REQUIRED')
    return plan, {'repo': REPO, 'path': PREREGISTRATION_PATH, 'commit': commit, 'preregistration_sha256': digest,
                  'preregistration_git_blob_sha': blob, 'verification_method': method}


def nonlinear_diagnostics(history, sample_count):
    diag = cc.diagnostics(history, sample_count)
    births, conditions, eigs = [], [], []
    for cohort, event in zip((c for c in history.bank.cohorts if c.role.startswith('new_')), history.events):
        _, _, covariance = sm.feature_statistics(cohort.mu, cohort.alpha)
        _, eigenvalues, condition = sm.checked_covariance_solve(covariance, np.zeros(2))
        conditions.append(condition); eigs.append(float(eigenvalues[0]))
        births.append({'u': cohort.u, 'b_birth': cohort.b_birth, 'energy_birth': cohort.energy_birth,
                       'mu': cohort.mu.tolist(), 'alpha': cohort.alpha.tolist(),
                       'birth_rule_sha256': cohort.digest(), 'covariance_eigenvalues': eigenvalues.tolist(),
                       'covariance_condition': condition,
                       'exact_moment_certificate': event['exact_moment_certificate']})
    return {'primal_diagnostics': diag, 'births': births,
            'max_covariance_condition': max(conditions, default=0.0),
            'min_covariance_eigenvalue': min(eigs, default=None)}


def failure_record(error):
    result = {'type': type(error).__name__, 'error': str(error),
              'record': getattr(error, 'record', {'kind': 'implementation_or_numerical'})}
    if getattr(error, '__cause__', None) is not None and hasattr(error.__cause__, 'record'):
        result['cause_record'] = error.__cause__.record
    return result


def assess_finite_differences(plan, base_rows, nonlinear_pairs):
    quantities = ('h', 'b', 'y', 'E_radiation', 'Pi', 'Sigma')
    window = np.array([r['x'] >= plan['primary']['comparison_x_start'] for r in base_rows])
    exact = np.array([[r['tangent']['full'][q] for q in quantities] for r in base_rows])
    series, derivatives = [], []
    for epsilon, minus, plus in nonlinear_pairs:
        if len(minus) != len(base_rows) or len(plus) != len(base_rows) or any(
                a['x'] != b['x'] or a['x'] != c['x'] for a, b, c in zip(base_rows, minus, plus)):
            raise ValueError('S8_FINITE_DIFFERENCE_GRID_MISMATCH')
        diff = np.array([[(p[q]-m[q])/(2*epsilon) for q in quantities] for m, p in zip(minus, plus)])
        error = np.max(np.abs(diff[window]-exact[window]), axis=0)
        derivatives.append(diff)
        series.append({'epsilon': epsilon, 'max_abs_error_after_x_start': dict(zip(quantities, map(float, error))),
                       'h_b_y_joint_max_abs_error': float(max(error[:3])),
                       'endpoint_error': {q: float(diff[-1, j]-exact[-1, j]) for j, q in enumerate(quantities)},
                       'central_derivative': [{'x': r['x'], **dict(zip(quantities, map(float, row)))}
                                              for r, row in zip(base_rows, diff)]})
    ratios = {}
    for q in ('b', 'y'):
        errors = [r['max_abs_error_after_x_start'][q] for r in series]
        ratios[q] = [a/b if b else None for a, b in zip(errors[:-1], errors[1:])]
    errors = [r['h_b_y_joint_max_abs_error'] for r in series]
    ratios['h_b_y_joint'] = [a/b if b else None for a, b in zip(errors[:-1], errors[1:])]
    richardson = (4*derivatives[-1]-derivatives[-2])/3
    richardson_error = np.max(np.abs(richardson[window]-exact[window]), axis=0)
    full_y_error = series[-1]['max_abs_error_after_x_start']['y']
    controls = []
    for mode in st.CONTROLS[1:]:
        predicted = np.array([r['tangent'][mode]['y'] for r in base_rows])
        error = float(np.max(np.abs(predicted[window]-derivatives[-1][window, 2])))
        ratio = error/full_y_error if full_y_error else None
        rejected = (error >= plan['gates']['negative_control_y_min_abs'] and
                    (full_y_error == 0 or error >= plan['gates']['negative_control_over_full_error_min']*full_y_error))
        controls.append({'mode': mode, 'max_abs_y_error_after_x_start': error,
                         'error_over_full_tangent_error': ratio, 'rejected_by_preregistered_criterion': rejected})
    lo, hi = plan['gates']['central_difference_order2_ratios']
    gates = {'central_difference_order2': all(v is not None and lo <= v <= hi for a in ratios.values() for v in a),
             'finest_central_accuracy': series[-1]['h_b_y_joint_max_abs_error'] <= plan['gates']['finest_central_h_b_y_max_abs'],
             'richardson_accuracy': max(richardson_error[:3]) <= plan['gates']['fine_richardson_h_b_y_max_abs'],
             'all_three_omission_controls_rejected': all(c['rejected_by_preregistered_criterion'] for c in controls)}
    return {'schema': 'bass.s8.finite_difference_assessment.v1', 'gate_results': gates,
            'series': series, 'order2_ratios': ratios,
            'fine_richardson_max_abs_error_after_x_start': dict(zip(quantities, map(float, richardson_error))),
            'negative_controls': controls}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-prereg', type=Path)
    parser.add_argument('--prereg', type=Path); parser.add_argument('--prereg-commit')
    parser.add_argument('--publication-receipt', type=Path); parser.add_argument('--git-root', type=Path)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    if args.write_prereg:
        args.write_prereg.parent.mkdir(parents=True, exist_ok=True)
        write_json_once(args.write_prereg, campaign_definition(), indent=2)
        print('PREREGISTRATION_WRITTEN '+str(args.write_prereg)); return 0
    if not args.prereg or not args.out:
        parser.error('--prereg and --out are required')
    plan, publication = verify_preregistration(args.prereg, args.prereg_commit, args.publication_receipt, args.git_root)
    apply_limits(); args.out.mkdir(parents=True, exist_ok=False); started = time.monotonic()
    integrations_attempted, failures = 0, []
    try:
        integrations_attempted += 1
        base = st.solve_tangent(primary_config(), parameter='y0', modes=st.CONTROLS)
        diag = st.diagnostics(base, plan['primary']['sample_count'])
        write_json_once(args.out/'ANALYTIC_TANGENT.json', diag, indent=1)
        print('PRIMARY_ANALYTIC '+('PASS' if all(diag['gate_results'].values()) else 'FAIL_GATES'), flush=True)
        nonlinear_pairs, nonlinear_receipts = [], []
        for index, epsilon in enumerate(plan['primary']['epsilon_values']):
            pair = []
            for sign in (-1, 1):
                label = f'FD_EPS{index}_'+('MINUS' if sign < 0 else 'PLUS')
                cfg = replace(primary_config(), y0=primary_config().y0+sign*epsilon)
                integrations_attempted += 1
                history = st.solve_nonlinear(cfg)
                record = nonlinear_diagnostics(history, plan['primary']['sample_count'])
                write_json_once(args.out/(label+'.json'), {'config': asdict(cfg), 'epsilon': epsilon, **record}, indent=1)
                pair.append(record['primal_diagnostics']['trajectory'])
                nonlinear_receipts.append({'id': label, 'epsilon': epsilon, 'sign': sign,
                                            'gate_results': record['primal_diagnostics']['gate_results'],
                                            'max_hamiltonian_relative': record['primal_diagnostics']['max_hamiltonian_relative'],
                                            'max_covariance_condition': record['max_covariance_condition'],
                                            'min_covariance_eigenvalue': record['min_covariance_eigenvalue']})
                print(label+' '+('PASS' if all(record['primal_diagnostics']['gate_results'].values()) else 'FAIL_GATES'), flush=True)
                check_disk(args.out)
            nonlinear_pairs.append((epsilon, pair[0], pair[1]))
        assessment = assess_finite_differences(plan, diag['trajectory'], nonlinear_pairs)
        write_json_once(args.out/'FINITE_DIFFERENCE_ASSESSMENT.json', assessment, indent=1)
        integrations_attempted += 1
        gauge = st.solve_tangent(cc.Config(**plan['gauge']['config']), parameter='b0', modes=('full',))
        gauge_diag = st.diagnostics(gauge, plan['primary']['sample_count'])
        gauge_error_hy = max(max(abs(r['tangent']['full'][q]) for q in ('h', 'y')) for r in gauge_diag['trajectory'])
        gauge_error_b = max(abs(r['tangent']['full']['b']-1) for r in gauge_diag['trajectory'])
        gauge_diag['gauge_max_h_y_abs'] = gauge_error_hy; gauge_diag['gauge_max_b_minus_one_abs'] = gauge_error_b
        write_json_once(args.out/'SOURCE_FRAME_GAUGE.json', gauge_diag, indent=1)
        gates = {'analytic_conservation_and_tangent': all(diag['gate_results'].values()),
                 'all_six_nonlinear_history_gates': all(all(r['gate_results'].values()) for r in nonlinear_receipts),
                 **assessment['gate_results'],
                 'gauge_conservation': all(gauge_diag['gate_results'].values()),
                 'source_frame_gauge': gauge_error_hy <= plan['gates']['source_frame_gauge_h_y_abs'] and
                                       gauge_error_b <= plan['gates']['source_frame_gauge_b_minus_one_abs'],
                 'frozen_sources_unchanged': source_hashes() == plan['source_sha256']}
        result = {'status': 'PASS_SCOPED_FULL_BIRTH_MEMORY_TANGENT' if all(gates.values()) else 'FAIL',
                  'gate_results': gates,
                  'analytic_summary': {k: v for k, v in diag.items() if k not in ('trajectory', 'events', 'tangent_memory_digests')},
                  'nonlinear_histories': nonlinear_receipts, 'order2_ratios': assessment['order2_ratios'],
                  'fine_richardson_max_abs_error': assessment['fine_richardson_max_abs_error_after_x_start'],
                  'negative_controls': assessment['negative_controls'],
                  'gauge_max_h_y_abs': gauge_error_hy, 'gauge_max_b_minus_one_abs': gauge_error_b}
    except (ValueError, ArithmeticError, RuntimeError) as error:
        failures.append(failure_record(error))
        result = {'status': 'FAIL', 'failures': failures,
                  'dependent_work': 'Not executed after the recorded current-task failure.'}
        write_json_once(args.out/'FAILURE.json', failures, indent=2)
    receipt = {'schema': 'bass.s8.full_birth_memory_tangent.return.v1', **result,
               'preregistration': publication, 'source_sha256': source_hashes(),
               'frozen_S7_source_sha256': FROZEN_SOURCE_SHA256,
               'integrations_attempted': integrations_attempted, 'planned_integrations': plan['integration_count'],
               'wall_seconds': time.monotonic()-started,
               'maxrss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
               'disk_bytes_used_before_receipt': check_disk(args.out), 'limits': plan['limits'],
               'python': sys.version, 'numpy': np.__version__, 'scipy': scipy.__version__,
               'scope': plan['scope'], 'not_admitted': plan['not_admitted'], 'skill_context_used': SKILL_CONTEXT,
               'NCP': 'NOT_USED; bounded local scientific campaign'}
    write_json_once(args.out/'RETURN_S8_TANGENT.json', receipt, indent=2)
    print(json.dumps(receipt, indent=2))
    return 0 if result['status'] == 'PASS_SCOPED_FULL_BIRTH_MEMORY_TANGENT' else 2


if __name__ == '__main__':
    sys.exit(main())
