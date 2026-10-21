#!/usr/bin/env python3
"""Frozen ACCEL03 27-point quadrature response check; no evolution or native.

Writes actual quadrature inputs, every stencil evaluation, and bounded results.
An observed numerical PASS is pending independent scientific review.
"""
from __future__ import annotations

import os

THREAD_KEYS = ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
               'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS', 'BLIS_NUM_THREADS')
for _key in THREAD_KEYS:
    os.environ[_key] = '1'
if hasattr(os, 'sched_getaffinity'):
    os.sched_setaffinity(0, sorted(os.sched_getaffinity(0))[:2])

from dataclasses import asdict
import hashlib
import json
import math
from pathlib import Path
import platform
import sys

import numpy as np

LANE = Path(__file__).resolve().parent
sys.path.insert(0, str(LANE))
from moment_response import moment_response

PILOT = LANE.parent/'rei_sigma_pi_pilot_20261021'
sys.path.insert(0, str(PILOT))
import split_sweep as split

H = 2.0**-15
EPS = float(np.finfo(np.float64).eps)
LIMIT = 2e-9
OUT = LANE/'evidence'


def save(name, data):
    OUT.mkdir(exist_ok=True)
    (OUT/name).write_text(json.dumps(data, indent=2, sort_keys=True,
                                    allow_nan=False)+'\n')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def five_point(values):
    return (values[-2]-8*values[-1]+8*values[1]-values[2])/(12*H)


def main():
    # Existing preparation validates immutable owner source; it creates no
    # trajectory and invokes no run/step/RHS/solver/native methods.
    context = split.PreparedContext()
    source_id, sources, toolchain = split.source_binding()
    inputs = {'schema': 'rei.accel03.moment_response.inputs.v1',
              'owner_ref': split.OWNER_REF, 'pilot_source_binding': source_id,
              'bound_sources': sources, 'toolchain': toolchain,
              'frozen_contract_sha256': sha(LANE/'FROZEN_CONTRACT.md'),
              'theory_sha256': sha(LANE/'THEORY.md'),
              'implementation_sha256': sha(LANE/'moment_response.py'),
              'verifier_sha256': sha(__file__), 'cases': []}
    rows = []
    raw = {'schema': 'rei.accel03.moment_response.raw.v1', 'h': H,
           'normalization': 'positive central energy J0', 'limit': LIMIT,
           'g_lower_bound': '-128*eps64*J0', 'eps64': EPS, 'points': rows}
    for alpha in (-.9, 0., 1.8):
        params = split.parameters(alpha_m=alpha)
        model = context.model(params)
        arrays = (model.massive_q2, model.massive.mu2, model.massive_weight)
        if (arrays[0].shape != (96, 1) or arrays[1].shape != (32,)
                or arrays[2].shape != (96, 32) or model.massive.mass != 30.):
            raise AssertionError('FROZEN_QUADRATURE_OR_MASS_MISMATCH')
        inputs['cases'].append({'alpha_m': alpha, 'parameters': asdict(params),
            'mass': model.massive.mass, 'qbar2': arrays[0].tolist(),
            'mu2': arrays[1].tolist(), 'weights': arrays[2].tolist()})
        save('MOMENT_RESPONSE_INPUTS.json', inputs)
        for x in (0., math.log(.2/.1999), .1):
            for b in (-.1, 0., .1):
                central = moment_response(*arrays, model.massive.mass, x, b)
                stencils = {}
                for axis in ('x', 'b'):
                    evaluations = []
                    values = {}
                    for offset in (-2, -1, 1, 2):
                        xx, bb = (x+offset*H, b) if axis == 'x' else (x, b+offset*H)
                        diagnostic = moment_response(*arrays, model.massive.mass, xx, bb)
                        evaluations.append({'offset': offset, 'x': xx, 'b': bb,
                                            'diagnostic': diagnostic})
                        values[offset] = diagnostic['J2']
                    derivative = five_point(values)
                    analytic = central['J2_'+axis]
                    stencils[axis] = {'evaluations': evaluations,
                        'finite_difference': derivative, 'analytic': analytic,
                        'signed_difference': derivative-analytic,
                        'energy_scaled_residual': abs(derivative-analytic)/central['J0']}
                g_lower = -128*EPS*central['J0']
                row = {'alpha_m': alpha, 'x': x, 'b': b, 'central': central,
                    'stencils': stencils, 'G_lower_bound': g_lower,
                    'G_nonnegative_within_envelope': central['G'] >= g_lower,
                    'pass': all(s['energy_scaled_residual'] <= LIMIT for s in stencils.values())
                            and central['G'] >= g_lower}
                rows.append(row)
                save('MOMENT_RESPONSE_RAW.json', raw)
                if not row['pass']:
                    raise AssertionError('MOMENT_RESPONSE_ACCEPTANCE_FAILED: '+repr(row))
    if len(rows) != 27:
        raise AssertionError('FROZEN_POINT_COUNT')

    # One-node analytic computational limits, separate from the C15 study.
    limits = []
    for label, mass in (('massless', 0.), ('nonrelativistic', 1e6)):
        point = moment_response([1.], [1.], [[1.]], mass, 0., 0.)
        exact_v2 = 1/(mass*mass+1)
        limits.append({'label': label, 'scope': 'illustrative one-node; not C15',
            'mass': mass, 'qbar2': 1., 'mu2': 1., 'weight': 1.,
            'diagnostic': point, 'analytic_v2': exact_v2,
            'observed_J4_over_J2': point['J4']/point['J2'],
            'observed_redshift_exponent': point['J2_x']/point['J2'],
            'expected_redshift_exponent': -5+exact_v2,
            'pass': abs(point['J4']/point['J2']-exact_v2) <= 8*EPS
                    and abs(point['J2_x']/point['J2']-(-5+exact_v2)) <= 8*EPS})
    save('MOMENT_RESPONSE_ILLUSTRATIVE_LIMITS.json', limits)
    if not all(item['pass'] for item in limits):
        raise AssertionError('ILLUSTRATIVE_LIMIT_FAILED')
    status = {'status': 'PENDING_INDEPENDENT_REVIEW', 'numerical_checks': 'PASS',
        'point_count': len(rows), 'stencil_evaluations': 8*len(rows),
        'max_energy_scaled_x_residual': max(r['stencils']['x']['energy_scaled_residual'] for r in rows),
        'max_energy_scaled_b_residual': max(r['stencils']['b']['energy_scaled_residual'] for r in rows),
        'min_G': min(r['central']['G'] for r in rows), 'limit': LIMIT,
        'mass_over_T': 30., 'quadrature': [96, 32], 'solver_calls': 0,
        'native_builds': 0, 'benchmarks': 0, 'requested_execution_model': 'gpt-6.1-sol',
        'observed_runtime_model': None, 'python': platform.python_version(),
        'numpy': np.__version__, 'thread_environment': {k: os.environ[k] for k in THREAD_KEYS},
        'cpu_affinity': sorted(os.sched_getaffinity(0)) if hasattr(os, 'sched_getaffinity') else None,
        'pilot_source_binding': source_id, 'owner_ref': split.OWNER_REF,
        'raw_inputs_sha256': sha(OUT/'MOMENT_RESPONSE_INPUTS.json'),
        'raw_outputs_sha256': sha(OUT/'MOMENT_RESPONSE_RAW.json')}
    save('MOMENT_RESPONSE_STATUS.json', status)
    print(json.dumps(status, sort_keys=True))


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        save('MOMENT_RESPONSE_STATUS.json', {'status': 'FAILED', 'error': repr(error),
             'requested_execution_model': 'gpt-6.1-sol', 'observed_runtime_model': None})
        raise
