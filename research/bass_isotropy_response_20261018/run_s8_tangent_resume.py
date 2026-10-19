#!/usr/bin/env python3
"""S8 R2: repair one NumPy-bool serialization failure; reuse seven histories.

No tangent/nonlinear history is rerun. The only integration is the originally
preregistered, previously unexecuted source-frame GL gauge history.
"""
from __future__ import annotations
import argparse
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
import run_s8_tangent as original
import s8_tangent as st
import coupled_cohorts as cc
from s6_io import apply_limits, check_disk, write_json_once

HERE = Path(__file__).resolve().parent
ORIGINAL_COMMIT = '4508e5de9a9f2c5ad1fc7c9a9f53983305e8f613'
ORIGINAL_PREREG = 'evidence_s8_tangent/PREREGISTRATION.json'
PREREG_PATH = original.LANE+'/evidence_s8_tangent/PREREGISTRATION_RESUME_R2.json'
NEW_SOURCES = ('run_s8_tangent_resume.py', 'test_s8_tangent_resume.py')
RAW_HISTORY_SHA256 = {
    'ANALYTIC_TANGENT.json': '6f10d47ebd398eb5dde6f551414e218ea7573fe7f87bf668ad2be02c1f47e7a4',
    'FD_EPS0_MINUS.json': '3efb01dc784bdfb4b31e2d47f19b1519aac33b1a5d4d08792c2b409f74230d2b',
    'FD_EPS0_PLUS.json': '5c4c91bde5710ce6f3d4b8ff83dded1fd775cc8fc6885bc62ed32706d3cdafda',
    'FD_EPS1_MINUS.json': '26816948077792373c680ebd428a1321cdb76fb98e0a0374cf87fca27a7af67b',
    'FD_EPS1_PLUS.json': '670f51f0573ec0de505f57acb8524f3be040ccd3c5b9bd43bd69c8056651a442',
    'FD_EPS2_MINUS.json': '161315d3c586cc3c3e57d1faef29b9aef53ed5fbe486756acd100ea99c1d102f',
    'FD_EPS2_PLUS.json': '14a6d7a822160e59f784ba87342a6fa03e0afd771a6dbaafa812cf67cbdc7403',
}
ORIGINAL_RECEIPT_SHA256 = {
    ORIGINAL_PREREG: '6f88cac768b78c324705590bf6a7e5b2912311f3a4c9494d958a1e4ed2c2ba58',
    'evidence_s8_tangent/CAMPAIGN_R1_PROCESS_RETURN.json': '3fe4742f1718c185e37b2e0ee65f6e502fd8a72f9a543c10a53b518ee47aa020',
    'evidence_s8_tangent/CAMPAIGN_R1.log': 'ea2ebefb699dbc884607a365dec82ec9e227d4e82a7d7b3f8d6282a13e96f0d6',
    'delivery/s8/TANGENT_PUBLICATION.json': 'a4183a92b6db4603b0c2a54722379b2e66e73b86c704fd4953817af4fe5e6f60',
}


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def git_blob(raw):
    return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()


def source_hashes():
    return {**original.source_hashes(),
            **{name: sha256((HERE/name).read_bytes()) for name in NEW_SOURCES}}


def normalized_assessment(assessment):
    """Convert only the evidenced boolean scalar; retain its true/false value."""
    result = dict(assessment)
    gates = dict(assessment['gate_results'])
    value = gates['richardson_accuracy']
    if not isinstance(value, (bool, np.bool_)):
        raise TypeError('S8_R2_EXPECTED_RICHARDSON_BOOLEAN')
    gates['richardson_accuracy'] = bool(value)
    result['gate_results'] = gates
    json.dumps(result, allow_nan=False)  # No broad scalar/string fallback.
    return result


def read_bound(path, expected_sha256):
    raw = path.read_bytes()
    if sha256(raw) != expected_sha256:
        raise ValueError('S8_R2_REUSED_RAW_BYTES_CHANGED: '+str(path))
    return raw


def verify_reused_inputs():
    for path, digest in ORIGINAL_RECEIPT_SHA256.items():
        read_bound(HERE/path, digest)
    plan = json.loads((HERE/ORIGINAL_PREREG).read_bytes())
    if plan != original.campaign_definition():
        raise ValueError('S8_R2_ORIGINAL_SOURCE_OR_CONTRACT_CHANGED')
    process = json.loads((HERE/'evidence_s8_tangent/CAMPAIGN_R1_PROCESS_RETURN.json').read_bytes())
    if (process['exit_code'] != 1 or process['publication_commit'] != ORIGINAL_COMMIT or
        process['source_sha256_before'] != original.source_hashes() or
        process['source_sha256_after'] != original.source_hashes()):
        raise ValueError('S8_R2_ORIGINAL_EXECUTION_IDENTITY')
    histories = {name: json.loads(read_bound(HERE/'evidence_s8_tangent/run01'/name, digest))
                 for name, digest in RAW_HISTORY_SHA256.items()}
    return plan, process, histories


def contract():
    plan, _, _ = verify_reused_inputs()
    return {'schema': 'bass.s8.tangent.serialization_resume.preregistration.v1',
            'source_sha256': source_hashes(),
            'original_execution_commit': ORIGINAL_COMMIT,
            'original_preregistration_sha256': ORIGINAL_RECEIPT_SHA256[ORIGINAL_PREREG],
            'original_source_sha256': original.source_hashes(),
            'reused_history_sha256': RAW_HISTORY_SHA256,
            'reused_receipt_sha256': ORIGINAL_RECEIPT_SHA256,
            'original_failure': {'kind': 'implementation/serialization_failure', 'exit_code': 1,
                                 'field': 'assessment.gate_results.richardson_accuracy',
                                 'unsupported_type': 'numpy.bool', 'original_files_preserved': True},
            'repair': 'Convert only the evidenced numpy.bool Richardson gate to built-in bool, preserving true and false.',
            'gates': plan['gates'], 'primary': plan['primary'], 'gauge': plan['gauge'], 'solver': plan['solver'],
            'integration_accounting': {'reused_original_analytic': 1, 'reused_original_nonlinear': 6,
                                       'new_gauge_only': 1, 'rerun_histories': 0},
            'limits': plan['limits'], 'scope': plan['scope'], 'not_admitted': plan['not_admitted'],
            'skill_context_used': original.SKILL_CONTEXT}


def verify_publication(path, commit, receipt_path=None, git_root=None):
    raw = path.read_bytes(); plan = json.loads(raw)
    if plan != contract():
        raise ValueError('S8_R2_PREREGISTRATION_SOURCE_OR_CONTRACT_CHANGED')
    if not commit or len(commit) != 40 or any(c not in '0123456789abcdef' for c in commit):
        raise ValueError('S8_R2_PUBLICATION_COMMIT_REQUIRED')
    digest, blob = sha256(raw), git_blob(raw)
    if receipt_path:
        receipt = json.loads(receipt_path.read_bytes())
        if (receipt.get('schema') != original.PUBLICATION_SCHEMA or receipt.get('repo') != original.REPO or
            receipt.get('path') != PREREG_PATH or receipt.get('commit') != commit or
            receipt.get('preregistration_sha256') != digest or receipt.get('preregistration_git_blob_sha') != blob or
            receipt.get('source_sha256') != source_hashes() or receipt.get('remote_readback_verified') is not True):
            raise ValueError('S8_R2_REMOTE_PUBLICATION_RECEIPT_MISMATCH')
        method = 'parent Git connector exact remote ref/tree/blob readback receipt'
    elif git_root:
        if str(path.resolve().relative_to(git_root.resolve())) != PREREG_PATH:
            raise ValueError('S8_R2_COMMITTED_PREREGISTRATION_PATH_MISMATCH')
        expected = {PREREG_PATH: digest,
                    **{original.LANE+'/'+name: sha for name, sha in source_hashes().items()}}
        for name, sha in expected.items():
            observed = subprocess.run(['git', '-C', str(git_root), 'show', commit+':'+name], check=True,
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30).stdout
            if sha256(observed) != sha:
                raise ValueError('S8_R2_COMMITTED_BYTES_MISMATCH: '+name)
        method = 'git show exact committed preregistration and ten source files'
    else:
        raise ValueError('S8_R2_COMMITTED_READBACK_REQUIRED')
    return plan, {'repo': original.REPO, 'path': PREREG_PATH, 'commit': commit,
                  'preregistration_sha256': digest, 'preregistration_git_blob_sha': blob,
                  'verification_method': method}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-prereg', type=Path)
    parser.add_argument('--prereg', type=Path); parser.add_argument('--prereg-commit')
    parser.add_argument('--publication-receipt', type=Path); parser.add_argument('--git-root', type=Path)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    if args.write_prereg:
        write_json_once(args.write_prereg, contract(), indent=2)
        print('R2_PREREGISTRATION_WRITTEN '+str(args.write_prereg)); return 0
    if not args.prereg or not args.out:
        parser.error('--prereg and --out required')
    plan, publication = verify_publication(args.prereg, args.prereg_commit, args.publication_receipt, args.git_root)
    original_plan, original_process, histories = verify_reused_inputs()
    apply_limits(); args.out.mkdir(parents=True, exist_ok=False); started = time.monotonic()
    new_integrations = 0
    new_integrations_completed = 0
    try:
        base = histories['ANALYTIC_TANGENT.json']
        pairs, nonlinear_receipts = [], []
        for i, epsilon in enumerate(original_plan['primary']['epsilon_values']):
            pair = []
            for suffix, sign in (('MINUS', -1), ('PLUS', 1)):
                name = f'FD_EPS{i}_{suffix}.json'
                record = histories[name]
                pair.append(record['primal_diagnostics']['trajectory'])
                nonlinear_receipts.append({'id': name, 'epsilon': epsilon, 'sign': sign,
                    'gate_results': record['primal_diagnostics']['gate_results'],
                    'max_hamiltonian_relative': record['primal_diagnostics']['max_hamiltonian_relative'],
                    'max_covariance_condition': record['max_covariance_condition'],
                    'min_covariance_eigenvalue': record['min_covariance_eigenvalue']})
            pairs.append((epsilon, pair[0], pair[1]))
        assessment = normalized_assessment(original.assess_finite_differences(original_plan, base['trajectory'], pairs))
        write_json_once(args.out/'FINITE_DIFFERENCE_ASSESSMENT.json', assessment, indent=1)
        print('ASSESSMENT_REUSED_SEVEN '+('PASS' if all(assessment['gate_results'].values()) else 'FAIL_GATES'), flush=True)

        new_integrations += 1
        gauge = st.solve_tangent(cc.Config(**plan['gauge']['config']), parameter='b0', modes=('full',))
        new_integrations_completed += 1
        gauge_diag = st.diagnostics(gauge, original_plan['primary']['sample_count'])
        gauge_error_hy = max(max(abs(r['tangent']['full'][q]) for q in ('h', 'y')) for r in gauge_diag['trajectory'])
        gauge_error_b = max(abs(r['tangent']['full']['b']-1) for r in gauge_diag['trajectory'])
        gauge_diag['gauge_max_h_y_abs'] = gauge_error_hy
        gauge_diag['gauge_max_b_minus_one_abs'] = gauge_error_b
        write_json_once(args.out/'SOURCE_FRAME_GAUGE.json', gauge_diag, indent=1)
        print('NEW_GAUGE '+('PASS' if all(gauge_diag['gate_results'].values()) else 'FAIL_GATES'), flush=True)
        verify_reused_inputs()
        gates = {'reused_analytic_conservation_and_tangent': all(base['gate_results'].values()),
                 'all_six_reused_nonlinear_history_gates': all(all(r['gate_results'].values()) for r in nonlinear_receipts),
                 **assessment['gate_results'],
                 'gauge_conservation': all(gauge_diag['gate_results'].values()),
                 'source_frame_gauge': gauge_error_hy <= plan['gates']['source_frame_gauge_h_y_abs'] and
                                       gauge_error_b <= plan['gates']['source_frame_gauge_b_minus_one_abs'],
                 'reused_raw_bytes_unchanged': True,
                 'frozen_sources_unchanged': source_hashes() == plan['source_sha256']}
        result = {'status': 'PASS_SCOPED_FULL_BIRTH_MEMORY_TANGENT' if all(gates.values()) else 'FAIL',
                  'gate_results': gates,
                  'analytic_summary': {k: v for k, v in base.items() if k not in ('trajectory', 'events', 'tangent_memory_digests')},
                  'nonlinear_histories': nonlinear_receipts, 'order2_ratios': assessment['order2_ratios'],
                  'fine_richardson_max_abs_error': assessment['fine_richardson_max_abs_error_after_x_start'],
                  'negative_controls': assessment['negative_controls'],
                  'gauge_max_h_y_abs': gauge_error_hy, 'gauge_max_b_minus_one_abs': gauge_error_b,
                  'gauge_primal_diagnostics': gauge_diag['primal_diagnostics']}
    except (ValueError, ArithmeticError, RuntimeError, TypeError) as error:
        result = {'status': 'FAIL', 'failures': [original.failure_record(error)]}
        write_json_once(args.out/'FAILURE.json', result['failures'], indent=2)
    receipt = {'schema': 'bass.s8.full_birth_memory_tangent.resume_return.v1', **result,
               'publication': publication, 'source_sha256': source_hashes(),
               'original_execution_commit': ORIGINAL_COMMIT,
               'original_failure_retained': plan['original_failure'],
               'reused_history_sha256': RAW_HISTORY_SHA256, 'reused_receipt_sha256': ORIGINAL_RECEIPT_SHA256,
               'integration_accounting': {'original_completed': 7, 'new_integrations_attempted': new_integrations,
                                          'new_integrations_completed': new_integrations_completed,
                                          'historical_reruns': 0, 'complete_planned_total': 7+new_integrations_completed},
               'wall_seconds': time.monotonic()-started, 'original_process_wall_seconds': original_process['wall_seconds'],
               'maxrss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
               'disk_bytes_used_before_receipt': check_disk(args.out), 'limits': plan['limits'],
               'python': sys.version, 'numpy': np.__version__, 'scipy': scipy.__version__,
               'scope': plan['scope'], 'not_admitted': plan['not_admitted'],
               'skill_context_used': original.SKILL_CONTEXT, 'NCP': 'NOT_USED; bounded local gauge integration only'}
    write_json_once(args.out/'RETURN_S8_TANGENT_R2.json', receipt, indent=2)
    print(json.dumps(receipt, indent=2))
    return 0 if result['status'] == 'PASS_SCOPED_FULL_BIRTH_MEMORY_TANGENT' else 2


if __name__ == '__main__':
    sys.exit(main())

