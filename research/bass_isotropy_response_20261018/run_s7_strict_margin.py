#!/usr/bin/env python3
"""R3: one preregistered stricter-internal-margin birth projection history.

All c689 R2 sources remain byte-for-byte unchanged. This runner explicitly
injects the existing P24 projector with atol=1e-15 into NEW isotropic births of
one fixed case. The exact admission gate stays 3/10^15. No old stock is patched.
"""
from __future__ import annotations
import argparse
from contextlib import contextmanager
from dataclasses import asdict
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
from run_s7_coupled import source_hashes as r2_source_hashes
from s6_io import apply_limits, check_disk, write_json_once

HERE = Path(__file__).resolve().parent
LANE = 'research/bass_isotropy_response_20261018'
R2_COMMIT = 'c689dcf151a9b3a6ba830d2a7f4fe8cc6a68385a'
EXECUTION_R1 = '2865f60bf0a247eaab4997c222ad82ae22a4c8fa'
CASE_ID = 'b03_n32_P24_K64'
REFERENCE_ID = 'ref_b03_K64'
INTERNAL_ATOL = 1e-15
ORIGINAL_BIRTH_RULE = cc.birth_rule
INPUTS = (
    'evidence_s7_coupled/PREREGISTRATION_R2.json',
    'evidence_s7_coupled/run01/b03_n32_P24_K64.json',
    'evidence_s7_coupled/run01/ref_b03_K64.json',
    'evidence_s7_coupled/run01/RETURN_S7_COUPLED.json',
    'evidence_s7_coupled/revalidate_r2/RETURN_S7_COUPLED_REANALYSIS.json',
    'evidence_s7_coupled/EXACT_MOMENT_FAILURES_R2.json',
)


def source_hashes():
    result = r2_source_hashes()
    for name in ('run_s7_strict_margin.py', 'test_s7_strict_margin.py'):
        result[name] = hashlib.sha256((HERE/name).read_bytes()).hexdigest()
    return result


def config():
    return cc.Config(K=64, n=32, mode='P24', b0=0.3)


def strict_birth_rule(b, n, mode):
    if n != 32 or mode != 'P24':
        raise ValueError('S7_R3_ONLY_N32_P24_NEW_BIRTHS')
    mu, prior = cc.lrs_rule(float(b), n)
    projected = cc.project_p24(mu, prior, atol=INTERNAL_ATOL)
    return mu, projected.weights


@contextmanager
def strict_new_births():
    """Single-thread, explicit scoped injection; restore even on any failure."""
    if cc.birth_rule is not ORIGINAL_BIRTH_RULE:
        raise ValueError('S7_R3_UNEXPECTED_EXISTING_BIRTH_OVERRIDE')
    state = {'strict_projection_calls': 0}

    def injected(b, n, mode):
        state['strict_projection_calls'] += 1
        return strict_birth_rule(b, n, mode)

    cc.birth_rule = injected
    try:
        yield state
    finally:
        cc.birth_rule = ORIGINAL_BIRTH_RULE


def campaign_definition():
    entries = []
    for name in INPUTS:
        raw = (HERE/name).read_bytes()
        entries.append({'path': name, 'bytes': len(raw),
                        'sha256': hashlib.sha256(raw).hexdigest()})
    return {'schema': 'bass.s7.coupled.strict_margin_preregistration.v1',
            'revision': 'R3_ONE_HISTORY_EXISTING_P24_INTERNAL_MARGIN',
            'source_sha256': source_hashes(), 'frozen_R2_source_sha256': r2_source_hashes(),
            'frozen_R2_commit': R2_COMMIT, 'original_execution_commit': EXECUTION_R1,
            'case': {'id': CASE_ID, 'config': asdict(config())}, 'reference': REFERENCE_ID,
            'internal_projector_atol': INTERNAL_ATOL, 'exact_admission_gate_rational': '3/1000000000000000',
            'gates': dict(cc.GATES),
            'solver': {'method': 'DOP853', 'rtol': cc.RTOL, 'atol': cc.ATOL, 'max_step': 0.08},
            'inputs': entries,
            'change': 'Call existing P24 API with atol=1e-15 for newly born isotropic rays of this one case.',
            'unchanged': ['R2 source files', 'owner', 'P24 algorithm file', 'initial stock', 'source-frame mapping',
                          'event law', 'independent Raychaudhuri ODE', 'exact admission gate'],
            'comparisons': {'stored_grid': 'Require identical x values; no interpolation or reference integration.',
                            'quantities': ['h', 'b', 'y', 'E_donor', 'E_radiation', 'Pi', 'Sigma'],
                            'trajectory_difference_gate': None,
                            'reason': 'Report R3-minus-R1 and R3-minus-GL128 differences as diagnostics.'},
            'required': ['64 strict new-birth calls', 'all 64 exact P2/P4 certificates',
                         'same original old-stock digests', 'positive weights and exact parity',
                         'all unchanged conservation gates', 'input/source hashes unchanged after execution'],
            'limits': {'workers': 1, 'ram_bytes': 16*1024**3, 'disk_bytes': 4*1024**3, 'job_seconds': 1800},
            'failure_policy': 'Retain R1 and R2 FAIL; no acceptance tolerance relaxation, negative weights or support changes.',
            'scope': 'One repaired manufactured coupled history only; no full 36-case or 7-benchmark rerun.',
            'not_admitted': ['all-grid stricter-projector validation', 'old FAIL erasure', 'native owner feedback',
                             'continuum accuracy', 'native finite-bin photon/energy conservation',
                             'production', 'full EoR', 'merge']}


def verify_preregistration(path, commit, receipt_path=None, git_root=None):
    raw = path.read_bytes(); plan = json.loads(raw)
    if plan != campaign_definition():
        raise ValueError('S7_R3_PREREGISTRATION_SOURCE_INPUT_OR_GATE_CHANGED')
    if not commit or len(commit) != 40 or any(c not in '0123456789abcdef' for c in commit):
        raise ValueError('S7_R3_PUBLICATION_COMMIT_REQUIRED')
    digest = hashlib.sha256(raw).hexdigest()
    blob = hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
    if git_root:
        rel = str(path.resolve().relative_to(git_root.resolve()))
        published = subprocess.run(['git', '-C', str(git_root), 'show', commit+':'+rel],
                                   check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30).stdout
        if published != raw:
            raise ValueError('S7_R3_COMMITTED_PREREGISTRATION_MISMATCH')
        for name, sha in source_hashes().items():
            source = subprocess.run(['git', '-C', str(git_root), 'show', commit+':'+LANE+'/'+name],
                                    check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30).stdout
            if hashlib.sha256(source).hexdigest() != sha:
                raise ValueError('S7_R3_COMMITTED_SOURCE_MISMATCH: '+name)
        method = 'git show exact committed preregistration and eight source files'
    elif receipt_path:
        receipt = json.loads(receipt_path.read_text())
        if (receipt.get('commit') != commit or receipt.get('preregistration_sha256') != digest or
            receipt.get('preregistration_git_blob_sha') != blob or
            receipt.get('source_sha256') != source_hashes() or receipt.get('remote_readback_verified') is not True):
            raise ValueError('S7_R3_REMOTE_PUBLICATION_RECEIPT_MISMATCH')
        method = 'parent Git connector exact remote ref/tree/blob readback receipt'
    else:
        raise ValueError('S7_R3_COMMITTED_READBACK_REQUIRED')
    return plan, {'commit': commit, 'preregistration_sha256': digest,
                  'preregistration_git_blob_sha': blob, 'verification_method': method}


def verify_inputs(plan):
    records = {}
    for entry in plan['inputs']:
        raw = (HERE/entry['path']).read_bytes()
        if len(raw) != entry['bytes'] or hashlib.sha256(raw).hexdigest() != entry['sha256']:
            raise ValueError('S7_R3_INPUT_HASH_CHANGED: '+entry['path'])
        records[entry['path']] = json.loads(raw)
    old_plan = records[INPUTS[0]]
    if old_plan['source_sha256'] != plan['frozen_R2_source_sha256'] or r2_source_hashes() != plan['frozen_R2_source_sha256']:
        raise ValueError('S7_R3_FROZEN_R2_SOURCE_CHANGED')
    if old_plan['gates'] != plan['gates'] or old_plan['solver'] != plan['solver']:
        raise ValueError('S7_R3_ADMISSION_OR_SOLVER_CHANGED')
    old = records[INPUTS[1]]; reference = records[INPUTS[2]]
    if old['case']['id'] != CASE_ID or old['case']['config'] != plan['case']['config']:
        raise ValueError('S7_R3_TARGET_CONFIG_CHANGED')
    if reference['case']['id'] != REFERENCE_ID:
        raise ValueError('S7_R3_REFERENCE_CHANGED')
    if records[INPUTS[3]]['preregistration']['commit'] != EXECUTION_R1:
        raise ValueError('S7_R3_ORIGINAL_EXECUTION_CHANGED')
    if records[INPUTS[4]]['analysis_publication']['commit'] != R2_COMMIT:
        raise ValueError('S7_R3_ORIGINAL_ANALYSIS_CHANGED')
    return old, reference


def compare_rows(current, reference, quantities):
    if len(current) != len(reference) or any(a['x'] != b['x'] for a, b in zip(current, reference)):
        raise ValueError('S7_R3_STORED_GRID_MISMATCH')
    differences = [{'x': a['x'], **{q: a[q]-b[q] for q in quantities}}
                   for a, b in zip(current, reference)]
    return {'max_abs_difference': {q: max(abs(r[q]) for r in differences) for q in quantities},
            'endpoint_difference': differences[-1], 'trajectory_difference': differences}


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
        print('PREREGISTRATION_WRITTEN '+str(args.write_prereg)); return 0
    if not args.prereg or not args.out:
        parser.error('--prereg and --out are required')
    plan, publication = verify_preregistration(args.prereg, args.prereg_commit,
                                              args.publication_receipt, args.git_root)
    original, reference = verify_inputs(plan)
    apply_limits(); args.out.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    try:
        with strict_new_births() as injection:
            history = cc.solve_history(config())
        diag = cc.diagnostics(history)
        old_match = diag['old_stock_digests'] == original['old_stock_digests']
        rays = []
        for event, cohort in zip(history.events, (c for c in history.bank.cohorts if c.role.startswith('new_'))):
            if event['birth_rule_sha256'] != cohort.digest():
                raise ValueError('S7_R3_BIRTH_DIGEST_CHANGED')
            rays.append({'u': cohort.u, 'b_birth': cohort.b_birth, 'energy_birth': cohort.energy_birth,
                         'role': cohort.role, 'mu': cohort.mu.tolist(), 'alpha': cohort.alpha.tolist(),
                         'birth_rule_sha256': cohort.digest(),
                         'exact_moment_certificate': event['exact_moment_certificate']})
        gates = dict(diag['gate_results'])
        gates['old_stock_matches_original'] = old_match
        gates['strict_projection_calls_64'] = injection['strict_projection_calls'] == 64
        gates['birth_count_64'] = len(rays) == 64
        verify_inputs(plan)
        gates['frozen_R2_sources_and_inputs_unchanged'] = True
        comparisons = {'R3_minus_original_R1': compare_rows(diag['trajectory'], original['trajectory'],
                                                           plan['comparisons']['quantities']),
                       'R3_minus_original_GL128': compare_rows(diag['trajectory'], reference['trajectory'],
                                                               plan['comparisons']['quantities'])}
        write_json_once(args.out/'HISTORY_R3_STRICT_MARGIN.json',
                        {'case': plan['case'], 'publication': publication,
                         'internal_projector_atol': INTERNAL_ATOL, **diag, 'birth_rays': rays}, indent=1)
        write_json_once(args.out/'TRAJECTORY_COMPARISONS_R3.json', comparisons, indent=1)
        result = {'status': 'PASS_ONE_REPAIRED_HISTORY' if all(gates.values()) else 'FAIL',
                  'gate_results': gates, 'strict_projection_calls': injection['strict_projection_calls'],
                  'birth_rules_checked': len(rays), 'old_stock_digests': diag['old_stock_digests'],
                  'max_exact_birth_moment_abs': diag['max_birth_moment_abs'],
                  'max_legacy_f64_birth_moment_abs': diag['max_legacy_f64_birth_moment_abs'],
                  'max_hamiltonian_relative': diag['max_hamiltonian_relative'],
                  'max_cohort_energy_relative': diag['max_cohort_energy_relative'],
                  'max_event_energy_relative': diag['max_event_energy_relative'],
                  'comparisons': {k: {m: v[m] for m in ('max_abs_difference', 'endpoint_difference')}
                                  for k, v in comparisons.items()}}
    except (ValueError, ArithmeticError, RuntimeError) as error:
        result = {'status': 'FAIL', 'error': type(error).__name__+': '+str(error),
                  'failure': error.record if isinstance(error, cc.BirthRuleFailure) else
                              {'kind': 'numerical_or_implementation'}}
    receipt = {'schema': 'bass.s7.coupled.strict_margin_return.v1', **result,
               'preregistration': publication, 'source_sha256': source_hashes(),
               'frozen_R2_source_sha256': plan['frozen_R2_source_sha256'],
               'original_execution_commit': EXECUTION_R1, 'original_analysis_commit': R2_COMMIT,
               'original_R1_status': 'FAIL_RETAINED', 'original_R2_status': 'FAIL_RETAINED',
               'case': plan['case'], 'internal_projector_atol': INTERNAL_ATOL,
               'exact_admission_gate_rational': plan['exact_admission_gate_rational'],
               'inputs': plan['inputs'], 'history_executions': 1, 'benchmark_executions': 0,
               'scope': plan['scope'], 'not_admitted': plan['not_admitted'],
               'wall_seconds': time.monotonic()-started,
               'maxrss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
               'disk_bytes_used': check_disk(args.out), 'limits': plan['limits'],
               'python': sys.version, 'numpy': np.__version__, 'scipy': scipy.__version__,
               'NCP': 'NOT_USED; one local manufactured history'}
    write_json_once(args.out/'RETURN_S7_STRICT_MARGIN_R3.json', receipt, indent=2)
    print(json.dumps(receipt, indent=2))
    return 0 if result['status'] == 'PASS_ONE_REPAIRED_HISTORY' else 2


if __name__ == '__main__':
    sys.exit(main())
