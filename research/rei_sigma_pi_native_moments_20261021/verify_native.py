#!/usr/bin/env python3
"""Frozen bounded verification only; no benchmark or scientific admission."""
from __future__ import annotations
import argparse
import copy
from dataclasses import replace
import json
import math
from pathlib import Path
import sys

LANE = Path(__file__).resolve().parent
sys.path.insert(0, str(LANE))
import native_context as nc
import native_worker as nw
import batch_worker as worker
import work_plan as wp

EPS = 2.0**-52
OUT = LANE / 'evidence'


def save(name, data):
    # Preserve NumPy scalar exports through the pinned owner's exporter.
    OUT.mkdir(exist_ok=True)
    (OUT / name).write_bytes(nc.cached.split.canonical(data))


def require(condition, description):
    if not condition:
        raise AssertionError(description)


def kernel():
    owner_context, context = nc.cached.split.PreparedContext(), nc.PreparedContext()
    points = []
    for alpha in (-.9, 0., .4, 1.8):
        params = nc.cached.split.parameters(alpha_m=alpha)
        owner, native = owner_context.model(params), context.model(params)
        for x in (0., math.log(.2/.1999), .1, 1., 4.):
            for b in (-1., -.1, -1e-8, 0., 1e-8, .1, 1.):
                ref, got = owner.massive_source_3moments(x, b), native.massive_source_3moments(x, b)
                errors = [abs(a-c)/ref[0] for a, c in zip(ref, got)]
                envelope = 64*EPS*ref[0]
                invariant = (-envelope <= got[1] <= got[0]+envelope
                             and -got[1]/2-envelope <= got[2] <= got[1]+envelope)
                row = {'alpha_m': alpha, 'x': x, 'b': b, 'owner': ref, 'native': got,
                       'energy_scaled_errors': errors, 'invariants_pass': invariant,
                       'pass': max(errors) <= 64*EPS and invariant}
                points.append(row)
                save('KERNEL_RAW.json', {'points': points, 'eps64': EPS, 'limit': 64*EPS})
                require(row['pass'], 'KERNEL_ACCEPTANCE_FAILED: ' + repr(row))
    require(len(points) == 140, 'KERNEL_POINT_COUNT')
    model = context.model(nc.cached.split.parameters(alpha_m=.4))
    derivatives = []
    h = 2.0**-15
    for x, b in ((.01, 0.), (.5, .02), (2., -.3)):
        def fx(t): return model.massive_source_3moments(t, b)[0]
        def fb(t): return model.massive_source_3moments(x, t)[0]
        dx = (fx(x-2*h)-8*fx(x-h)+8*fx(x+h)-fx(x+2*h))/(12*h)
        db = (fb(b-2*h)-8*fb(b-h)+8*fb(b+h)-fb(b+2*h))/(12*h)
        j0, j1, j2 = model.massive_source_3moments(x, b)
        ex, eb = abs(dx+3*j0+j1)/j0, abs(db+2*j2)/j0
        row = {'x': x, 'b': b, 'h': h, 'native': [j0, j1, j2], 'dx_J0': dx, 'db_J0': db,
               'x_identity_residual': ex, 'b_identity_residual': eb, 'pass': max(ex, eb) <= 2e-9}
        derivatives.append(row)
        save('DERIVATIVE_RAW.json', derivatives)
        require(row['pass'], 'DERIVATIVE_ACCEPTANCE_FAILED: ' + repr(row))
    return {'points': len(points), 'max_energy_scaled_error': max(max(p['energy_scaled_errors']) for p in points),
            'max_derivative_residual': max(max(r['x_identity_residual'], r['b_identity_residual']) for r in derivatives)}


def cases():
    output = []
    for index, values in enumerate(((0., 0., 0.), (2.5e-4, 0., 0.), (0., 1e-5, 0.),
                                    (0., 0., 1e-5), (0., 4e-4, -4e-4))):
        row = {'case_id': 'native_check_' + str(index)}
        for value, mag, sign, signed in zip(values, wp.MAGNITUDES, wp.SIGNS, wp.SIGNED):
            row.update({mag: abs(value), sign: 0 if value == 0 else (1 if value > 0 else -1), signed: value})
        row.update(signed_Pi_total_requested=values[1]+values[2], nominal_cancellation=values[1]+values[2] == 0)
        output.append(wp.normalize_case(row))
    return output


def trajectories():
    split, _ = wp.modules()
    reference, native = split.PreparedContext(), nc.PreparedContext()
    comparisons, raw = [], []
    for case in cases():
        ref = split.run_case(case, reference, 2)
        got = split.run_case(case, native, 2)
        raw.append({'case': case, 'original': ref, 'native': got})
        save('TRAJECTORY_RAW.json', raw)
        rows = []
        refrows = [ref['initial'], *ref['owner_result']['history'], ref['owner_result']['final']]
        gotrows = [got['initial'], *got['owner_result']['history'], got['owner_result']['final']]
        for index, (a, c) in enumerate(zip(refrows, gotrows)):
            errors = {name: abs(a[name]-c[name]) for name in
                      ('signed_Sigma', 'signed_Pi_m', 'signed_Pi_r', 'signed_Pi_total', 'x_HII', 'x_HeII')}
            errors.update(H_relative=abs(a['H']-c['H'])/a['H'],
                          Tgas_relative=abs(a['Tgas_K']-c['Tgas_K'])/a['Tgas_K'])
            for component in ('m', 'r', 'total'):
                # H^3/kappa_t normalization is exactly 2 signed Sigma signed Pi.
                errors['normalized_work_' + component] = abs(
                    2*a['signed_Sigma']*a['signed_Pi_'+component] -
                    2*c['signed_Sigma']*c['signed_Pi_'+component])
            limits = {name: (5e-13 if name in ('x_HII', 'x_HeII', 'H_relative') else
                             5e-12 if name == 'Tgas_relative' else 5e-14) for name in errors}
            passed = all(errors[name] <= limits[name] for name in errors)
            rows.append({'row': index, 'absolute_or_relative_errors': errors, 'limits': limits, 'pass': passed,
                         'original_signed_total': a['signed_Pi_total'], 'native_signed_total': c['signed_Pi_total']})
        item = {'case_id': case['case_id'], 'original_gates': ref['gates'], 'native_gates': got['gates'],
                'rows': rows, 'pass': all(r['pass'] for r in rows) and all(ref['gates'].values()) and all(got['gates'].values()),
                'native_cache': native.last_model.moment_cache_info()}
        comparisons.append(item)
        save('TRAJECTORY_COMPARISON.json', comparisons)
        require(item['pass'], 'TRAJECTORY_ACCEPTANCE_FAILED: ' + repr(item))
    save('CUSTOM_CASES.json', cases())
    return {'pairs': len(comparisons), 'steps': 2, 'pass': True}


def integration():
    from unittest.mock import patch
    import shutil
    import tempfile
    checks = {}
    context = nc.PreparedContext()
    model = context.model(nc.cached.split.parameters(alpha_m=.4))
    first = model.massive_source_3moments(.5, .02)
    second = model.massive_source_3moments(.5, .02)
    require(first is second and model.moment_cache_info()['hits'] == 1, 'NATIVE_CACHE_HIT')
    checks['native_cache_hit'] = model.moment_cache_info()
    bad = nc.cached.split.PreparedContext().model(nc.cached.split.parameters())
    bad.massive = copy.copy(bad.massive)
    bad.massive.mu = bad.massive.mu.copy()
    bad.massive.mu[0] += 1e-10
    try:
        nc.fold_model(bad)
    except ValueError as error:
        require('PARITY' in str(error), 'BAD_PARITY_ERROR')
        checks['bad_parity_rejected'] = str(error)
    else:
        raise AssertionError('BAD_PARITY_ACCEPTED')
    import build_native as build
    with tempfile.TemporaryDirectory() as temp:
        directory = Path(temp)
        for name in ('librei_moments.so', 'build_receipt.json'):
            shutil.copy2(build.DEFAULT_BUILD / name, directory / name)
        receipt = json.loads((directory / 'build_receipt.json').read_text())
        receipt['source_sha256']['moments.cpp'] = '0'*64
        (directory / 'build_receipt.json').write_text(json.dumps(receipt))
        try:
            nc.NativeLibrary(directory)
        except ValueError as error:
            checks['changed_source_rejected'] = str(error)
        else:
            raise AssertionError('CHANGED_SOURCE_ACCEPTED')
        shutil.copy2(build.DEFAULT_BUILD / 'build_receipt.json', directory / 'build_receipt.json')
        with (directory / 'librei_moments.so').open('ab') as stream:
            stream.write(b'changed binary')
        try:
            nc.NativeLibrary(directory)
        except ValueError as error:
            checks['changed_binary_rejected'] = str(error)
        else:
            raise AssertionError('CHANGED_BINARY_ACCEPTED')
    registry = wp.load_completed_registry()
    default_id = worker.backend_binding(registry)[0]
    native_id = worker.backend_binding(registry, nw.backend_spec())[0]
    require(default_id != native_id, 'BACKEND_NAMESPACE_COLLISION')
    checks['backend_identity'] = {'default': default_id, 'native': native_id,
                                  'same_science_context': registry['context_id']}
    no_work = OUT / 'completed729'
    plan_path = no_work / 'plan.json'
    worker.write_json(plan_path, wp.build_plan(backend=nw.NAME))
    with patch.object(nw, 'backend_spec', side_effect=AssertionError('no-work inspected native build')), \
            patch.object(nc.ctypes, 'CDLL', side_effect=AssertionError('no-work loaded native library')):
        receipt = nw.prepare(plan_path, no_work / 'prepared', no_work / 'must_not_exist',
                             build_dir=no_work / 'missing_library')
    require(receipt['pending_count'] == 0 and receipt['jobs'] == 0 and not (no_work / 'must_not_exist').exists(), 'NO_WORK')
    checks['completed729_no_native'] = receipt
    save('INTEGRATION_CHECKS.json', checks)
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('check', choices=('kernel', 'trajectories', 'integration'))
    args = parser.parse_args()
    functions = {'kernel': kernel, 'trajectories': trajectories, 'integration': integration}
    try:
        result = functions[args.check]()
        save(args.check.upper() + '_STATUS.json', {'status': 'PASS', 'result': result})
        print(json.dumps({'status': 'PASS', 'check': args.check, 'result': result}, sort_keys=True))
    except Exception as error:
        save(args.check.upper() + '_STATUS.json', {'status': 'FAILED', 'error': repr(error)})
        raise


if __name__ == '__main__':
    main()
