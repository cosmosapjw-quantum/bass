#!/usr/bin/env python3
"""Source-pinned signed Sigma/Pi pilot adapter; owner dynamics remain unchanged."""
from __future__ import annotations
import argparse
import csv
import glob
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import platform
import sys
import traceback

LANE = Path(__file__).resolve().parent
SNAPSHOT = LANE / 'vendor/rei_c15'
CONTRACT = LANE / 'PILOT_CONTRACT.json'
SOURCE_MANIFEST = SNAPSHOT / 'SOURCE_FETCH_MANIFEST.json'
OWNER_REF = '80825585f9fe31d2ee0d5af545ada3fa1f52be72'


def json_scalar(value):
    """Convert exact NumPy scalars at export; retain strict JSON failures."""
    import numpy as np
    if isinstance(value, np.generic):
        return value.item()
    raise TypeError(f'Object of type {type(value).__name__} is not JSON serializable')


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), allow_nan=False,
                      default=json_scalar).encode()


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, data, immutable=False):
    path = Path(path)
    raw = json.dumps(data, indent=2, sort_keys=True, allow_nan=False, default=json_scalar) + '\n'
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and immutable:
        if json.loads(path.read_text()) != data:
            raise ValueError(f'EXISTING_IMMUTABLE_INPUT_DIFFERS: {path}')
        return
    temp = path.with_name(path.name + '.tmp')
    temp.write_text(raw)
    temp.replace(path)


def verify_snapshot():
    manifest = json.loads(SOURCE_MANIFEST.read_text())
    if manifest['ref'] != OWNER_REF:
        raise ValueError('OWNER_REF_MISMATCH')
    for item in manifest['files']:
        path = SNAPSHOT / item['path']
        if digest(path) != item['sha256']:
            raise ValueError(f'IMMUTABLE_SOURCE_BYTE_IDENTITY_MISMATCH: {path}')
    return manifest


_COUPLED = None

def load_owner():
    global _COUPLED
    if _COUPLED is None:
        verify_snapshot()  # Must precede importing any owner module.
        owner_dir = SNAPSHOT / 'research/rei_c15_sigma_pi_feedback_20261015'
        sys.path.insert(0, str(owner_dir))
        spec = importlib.util.spec_from_file_location('pilot_c15_owner', owner_dir / 'coupled.py')
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
        mod.source_identity()
        _COUPLED = mod
    return _COUPLED


def parameters(Sigma=0., orientation=0, alpha=0.):
    c = load_owner()
    return c.Parameters(Sigma_initial=Sigma, orientation=orientation,
        gamma_quadrupole=alpha, nu_quadrupole=alpha, massive_quadrupole=alpha,
        massive_fraction=.1, massive_mass_over_T=30., L=8,
        native_md14_source=True, enable_thomson=True, enable_primordial_pi=True,
        enable_matter_pi=True, enable_ionizing_pi=True,
        manufactured_ionizing_stress_scale=1., enable_C13_positive_coalescence=True)


class PreparedContext:
    """One validated source/rate/radial/angular preparation per sequential group.

    No evolution method is overridden. All per-case state, proxy, weights,
    counters, solver outputs, photons and gas are separate. Fixed arrays shared
    from the original isotropic constructor are readonly.
    """
    def __init__(self):
        import numpy as np
        c = load_owner()
        prototype = c.EinsteinBoltzmann(parameters(), a0=.1999, fast_massive=True,
                                       source_grid='8X8')
        # This exact list is the owner initializer's fixed fields. Do not copy
        # proxy or case state; the prototype has not yet been initialized.
        names = ('source_grid', 'fast_massive', 'a0', 'cosmo', 'source', 'owner',
                 'H0_ref', 'Om', 'Hubble0', 'Ecrit', 'source_omegas', 'E_gamma0',
                 'E_nu0', 'A_E', 'A_N', 'D', 'massive', 'massive_q2',
                 'mass_ref_density')
        self.shared = {name: getattr(prototype, name) for name in names}
        arrays = [prototype.A_E, prototype.A_N, prototype.D, prototype.massive_q2]
        arrays += [v for v in vars(prototype.massive).values() if isinstance(v, np.ndarray)]
        arrays += [v for v in vars(prototype.source).values() if isinstance(v, np.ndarray)]
        arrays += [prototype.owner.temperatures, prototype.owner.values,
                   prototype.owner.interp.x, prototype.owner.interp.c]
        for a in arrays:
            a.flags.writeable = False
        base = prototype.initial()
        _, J01, _ = prototype.massive_source_3moments(0., 0.)
        self.calibration = {'H_base_per_s': base.H, 'massive_J01': J01,
            'stress_per_alpha_Pa': (prototype.E_gamma0 / prototype.a0**4 +
                prototype.E_nu0 / prototype.a0**4 + prototype.mass_ref_density * J01) / 5,
            'kappa_time': 3 * c.KAPPA}
        self.owner_class = c.EinsteinBoltzmann

    def model(self, params):
        import numpy as np
        c = load_owner()
        # The prepared lane is deliberately confined to the frozen contract.
        expected = parameters(params.Sigma_initial, params.orientation,
                              params.massive_quadrupole)
        if params != expected:
            raise ValueError('PREPARED_CONTEXT_FIXED_PARAMETER_MISMATCH')
        model = object.__new__(c.EinsteinBoltzmann)
        model.__dict__.update(self.shared)
        model.params = params
        model.massive_weight = (model.massive.rw[:, None] / model.massive.norm) * (
            model.massive.wmu * (1 + params.massive_quadrupole * model.massive.p2))[None, :]
        if np.any(model.massive_weight < 0):
            raise ValueError('SOURCE_BASS_MASSIVE_POSITIVE_VLASOV_WEIGHTS')
        model.iterations = 0
        model.rhs_evals = 0
        return model


def signed_grid(contract=None):
    contract = contract or json.loads(CONTRACT.read_text())
    cases = []
    for sigma in contract['grid']['Sigma_half']:
        for pi in contract['grid']['Pi_half']:
            for ss in ((0,) if sigma == 0 else (-1, 1)):
                for ps in ((0,) if pi == 0 else (-1, 1)):
                    cases.append({'case_id': f'case_{len(cases):03d}',
                        'Sigma_half_requested': sigma, 'Pi_half_requested': pi,
                        'shear_sign_requested': ss, 'stress_sign_requested': ps,
                        'signed_Sigma_requested': ss * sigma,
                        'signed_Pi_requested': ps * pi})
    return cases


def seed_for(case, context):
    from sigma_pi_map import initial_seed
    cc = context.calibration
    return initial_seed(Sigma_half=case['Sigma_half_requested'],
        Pi_half=case['Pi_half_requested'], shear_sign=case['shear_sign_requested'],
        stress_sign=case['stress_sign_requested'], H_base=cc['H_base_per_s'],
        stress_per_alpha=cc['stress_per_alpha_Pa'], kappa_time=cc['kappa_time'])


def normalized(*, s, H, components):
    from sigma_pi_map import invariants
    c = load_owner()
    # Physical pressure contraction uses all four physical components, apart
    # from the owner's switched/manufactured Pi_total_source bookkeeping.
    D = sum(components)
    result = invariants(s=s, H=H, delta_pressure=D, kappa_time=3*c.KAPPA)
    result.update({'D_physical_Pa': D, 'signed_Sigma': math.sqrt(3)*s/H,
                   'signed_Pi': 3*c.KAPPA*D/(math.sqrt(3)*H*H),
                   'Pi_orientation_status': 'RESOLVED' if result['Pi_half'] >= 3e-13
                       else 'NUMERICALLY_UNRESOLVED_BELOW_PI_3E-13'})
    return result


def initial_record(model, st):
    f = model._physical(0., st.b, st.s/model.H0_ref, st.moments, model.proxy, 0.)
    g = st.gas_and_UV.gas
    row = {'a': st.a, 'elapsed_s': 0., 'b': st.b, 's_inv_s': st.s, 'H': st.H,
           'Pi_gamma': f['Pi_gamma'], 'Pi_nu': f['Pi_nu'],
           'Pi_massive': f['Pi_massive'], 'Pi_UV': f['Pi_ion'],
           'Pi_total_source': f['Pi_total_source'], 'Tgas_K': g.temperature_K,
           'x_HII': g.nHII/g.nH, 'x_HeII': g.nHeII/g.nHe,
           'gamma_number_N0': float(st.moments[1, 0]),
           'nu_number_N0': float(st.moments[3, 0]), 'nerr': 0., 'eerr': 0.}
    row.update(normalized(s=st.s, H=st.H, components=[f[k] for k in
                         ('Pi_gamma', 'Pi_nu', 'Pi_massive', 'Pi_ion')]))
    return row


def run_case(case, context, nsteps):
    seed = seed_for(case, context)
    p = parameters(case['Sigma_half_requested'], case['shear_sign_requested'],
                   seed['common_P2_alpha'])
    model = context.model(p)
    initial = initial_record(model, model.initial())
    residuals = {'Sigma_initial_abs': abs(initial['Sigma_half'] - case['Sigma_half_requested']),
                 'Pi_initial_abs': abs(initial['Pi_half'] - case['Pi_half_requested'])}
    if any(v > 3e-13 for v in residuals.values()):
        raise RuntimeError(f'INITIAL_REQUESTED_INVARIANT_MISMATCH {residuals}')
    result = model.run(nsteps=nsteps, compress=True, feedback=True)
    for row in result['history']:
        row.update(normalized(s=row['s_inv_s'], H=row['H'], components=[row[k] for k in
                             ('Pi_gamma', 'Pi_nu', 'Pi_massive', 'Pi_UV')]))
        if not (row['H'] > 0 and 10000 <= row['Tgas_K'] <= 24000 and
                0 <= row['x_HII'] <= 1 and 0 <= row['x_HeII'] <= 1):
            raise RuntimeError('PILOT_PHYSICAL_DOMAIN')
    # Owner run already enforces every per-step ledger and number gate.
    gates = {'number_5e-12': result['errors']['photochemical_number_abs_max'] <= 5e-12,
             'energy_5e-11': result['errors']['photochemical_energy_eV_H_abs_max'] <= 5e-11,
             'gamma_monopole_3e-9': result['errors']['gamma_number_monopole_abs_max'] <= 3e-9,
             'nu_monopole_3e-9': result['errors']['nu_number_monopole_abs_max'] <= 3e-9,
             'initial_mapping_3e-13': all(v <= 3e-13 for v in residuals.values()),
             'positive_common_P2_family': -1 <= seed['common_P2_alpha'] <= 2,
             'finite_success_json': True}
    if not all(gates.values()):
        raise RuntimeError(f'PILOT_ORIGINAL_GATE_FAILURE {gates}')
    output = {'case': case, 'seed': seed, 'calibration': context.calibration,
              'initial': initial, 'numeric_checks': residuals, 'gates': gates,
              'owner_result': result}
    canonical(output)  # rejects all nonfinite successful values, including nested data
    return output


def source_binding():
    verify_snapshot()
    files = [p for p in SNAPSHOT.rglob('*') if p.is_file() and
             p.suffix in ('.py', '.csv', '.json')]
    files += [Path(__file__), LANE/'sigma_pi_map.py', CONTRACT, SOURCE_MANIFEST]
    files = sorted(set(files))
    bound = [{'path': str(p.resolve()), 'sha256': digest(p)} for p in files]
    source = hashlib.sha256(canonical([{'path': str(Path(x['path']).relative_to(LANE)),
                                       'sha256': x['sha256']} for x in bound])).hexdigest()
    import numpy, scipy
    toolchain = {'python': platform.python_version(), 'numpy': numpy.__version__,
                 'scipy': scipy.__version__}
    return source, bound, toolchain


def prepare(args):
    contract = json.loads(CONTRACT.read_text())
    if not 2 <= args.nsteps <= 1024 or args.group_size < 1:
        raise ValueError('PREPARE_STEP_OR_GROUP_DOMAIN')
    out = Path(args.out).resolve()
    cases = signed_grid(contract)
    source, bound, tc = source_binding()
    # Case identities do not depend on grouping/concurrency. Job input identity
    # does include grouping because receipts bind an entire group result.
    science = {'contract': contract, 'cases': cases, 'nsteps': args.nsteps,
               'compress': True, 'feedback': True}
    input_hash = hashlib.sha256(canonical(science)).hexdigest()
    binding = {'source': source, 'input': input_hash,
               'toolchain': hashlib.sha256(canonical(tc)).hexdigest()}
    context = PreparedContext()
    # Reject impossible coordinates before producing runnable input.
    alpha_max = max(abs(seed_for(case, context)['common_P2_alpha']) for case in cases)
    source_bound = list(bound)
    jobs = []
    for i in range(0, len(cases), args.group_size):
        job_id = f'group_{i//args.group_size:03d}'
        path = out/'inputs'/f'{job_id}.json'
        data = {'schema': 'rei.sigma_pi.group_input.v1', 'science_binding': binding,
                'toolchain': tc, 'nsteps': args.nsteps,
                'cases': cases[i:i+args.group_size], 'owner_ref': OWNER_REF,
                'bound_files': source_bound}
        write_json(path, data, immutable=True)
        jobs.append({'id': job_id, 'argv': [sys.executable, str(Path(__file__).resolve()),
            'run-group', '--input', str(path), '--output', '{attempt_dir}/result.json'],
            'outputs': ['result.json'], 'cwd': str(LANE), 'memory_mb': 384,
            'timeout_s': 1800})
        bound.append({'path': str(path), 'sha256': digest(path)})
    manifest = {'schema': 'rei.shared_case_science.v1', 'science_binding': binding,
                'bound_files': bound, 'jobs': jobs, 'toolchain': tc,
                'pilot': {'case_count': len(cases), 'group_size': args.group_size,
                          'alpha_abs_max': alpha_max, 'nsteps': args.nsteps}}
    write_json(out/'manifest.json', manifest, immutable=True)
    print(json.dumps({'manifest': str(out/'manifest.json'), 'jobs': len(jobs),
                      'cases': len(cases), 'alpha_abs_max': alpha_max}))


def run_group(args):
    data = json.loads(Path(args.input).read_text())
    # Check the full immutable source/adapter inputs before owner import.
    for item in data['bound_files']:
        if digest(item['path']) != item['sha256']:
            raise ValueError(f"BOUND_INPUT_BYTE_IDENTITY_MISMATCH: {item['path']}")
    import numpy, scipy
    actual_toolchain = {'python': platform.python_version(), 'numpy': numpy.__version__, 'scipy': scipy.__version__}
    if actual_toolchain != data['toolchain']:
        raise ValueError(f'TOOLCHAIN_MISMATCH: expected {data["toolchain"]}, actual {actual_toolchain}')
    context = PreparedContext()
    result = {'schema': 'rei.sigma_pi.group_result.v1',
              'science_binding': data['science_binding'], 'owner_ref': OWNER_REF,
              'nsteps': data['nsteps'], 'cases': []}
    output = Path(args.output)
    try:
        for case in data['cases']:
            completed = run_case(case, context, data['nsteps'])
            result['cases'].append(completed)
            write_json(output.with_name(output.stem+'.checkpoint.json'), result)
        result['status'] = 'SUCCEEDED'
        write_json(output, result)
    except Exception:
        write_json(output.with_name(output.stem+'.failure.json'),
                   {'status': 'FAILED', 'case': case, 'traceback': traceback.format_exc(),
                    'completed_cases': [c['case']['case_id'] for c in result['cases']]})
        raise


def scalar_row(row, prefix=''):
    """Flatten owner mappings for CSV without dropping nested energy fields."""
    flattened = {}
    for key, value in row.items():
        name = f'{prefix}{key}'
        if isinstance(value, dict):
            flattened.update(scalar_row(value, prefix=name+'.'))
        elif isinstance(value, (str, int, float, bool)):
            flattened[name] = value
        else:
            # Preserve any future nonscalar owner fields as exact JSON cells.
            flattened[name] = json.dumps(value, sort_keys=True, allow_nan=False, default=json_scalar)
    return flattened


def result_paths_from_scope(scope):
    paths = []
    # Receipts are the executor's final success authority. Only results named
    # by successful receipts enter the aggregate; stray attempts are ignored.
    for p in Path(scope).rglob('receipt.json'):
        receipt = json.loads(p.read_text())
        if receipt.get('status') != 'PASS' or receipt.get('returncode') != 0:
            continue
        item = receipt.get('outputs', {}).get('result.json')
        if item is None:
            continue
        candidate = p.parent/'result.json'
        if digest(candidate) != item['sha256']:
            raise ValueError(f'RECEIPT_OUTPUT_MISMATCH: {candidate}')
        paths.append(candidate)
    return paths


def aggregate(args):
    manifest = json.loads(Path(args.manifest).read_text())
    paths = []
    for pattern in (args.result_files or []):
        paths += [Path(p) for p in glob.glob(pattern)]
    if args.scope:
        paths += result_paths_from_scope(args.scope)
    if not paths:
        raise ValueError('NO_SUCCESSFUL_RESULT_FILES')
    cases = {}
    provenance = []
    for path in sorted(set(p.resolve() for p in paths)):
        data = json.loads(path.read_text())
        if data.get('status') != 'SUCCEEDED' or data['science_binding'] != manifest['science_binding']:
            raise ValueError(f'RESULT_SCIENCE_OR_STATUS_MISMATCH: {path}')
        provenance.append({'path': str(path), 'sha256': digest(path)})
        for case in data['cases']:
            cid = case['case']['case_id']
            if cid in cases and canonical(cases[cid]) != canonical(case):
                raise ValueError(f'CONFLICTING_DUPLICATE_CASE: {cid}')
            cases[cid] = case
    expected = {c['case_id']: c for c in signed_grid()}
    if set(cases) - set(expected):
        raise ValueError('UNEXPECTED_CASE_ID')
    summaries, histories = [], []
    for cid, data in sorted(cases.items()):
        if data['case'] != expected[cid] or not all(data['gates'].values()):
            raise ValueError(f'CASE_CONTRACT_OR_GATE_MISMATCH: {cid}')
        metadata = data['case']
        final = data['owner_result']['final']
        summaries.append({**metadata, 'alpha': data['seed']['common_P2_alpha'],
            **{f'initial_{k}': v for k, v in scalar_row(data['initial']).items()},
            **{f'final_{k}': v for k, v in scalar_row(final).items()},
            **data['numeric_checks'], **data['owner_result']['errors']})
        for i, row in enumerate([data['initial']] + data['owner_result']['history']):
            histories.append({**metadata, 'step': i, **scalar_row(row)})
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for name, rows in [('cases.csv', summaries), ('history.csv', histories)]:
        keys = list(dict.fromkeys(k for r in rows for k in r))
        with (out/name).open('w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader(); writer.writerows(rows)
    missing = sorted(set(expected)-set(cases))
    write_json(out/'summary.json', {'schema': 'rei.sigma_pi.aggregate.v1',
        'status': 'COMPLETE' if not missing else 'PARTIAL', 'case_count': len(cases),
        'expected_case_count': len(expected), 'missing_case_ids': missing,
        'science_binding': manifest['science_binding'], 'owner_ref': OWNER_REF,
        'nsteps': manifest['pilot']['nsteps'], 'source_grid': '8X8',
        'norm': 'half_contraction', 'a_start': .1999, 'a_end': .2,
        'z_start': 1/.1999-1, 'z_end': 4., 'all_stored_gates_pass': True,
        'result_files': provenance, 'manifest_sha256': digest(args.manifest),
        'claim': 'Preliminary conditional warm near-z4 response; full stellar/emitter and escape Q^a closure, full EoR history and convergence remain open.'})
    print(json.dumps({'out': str(out.resolve()), 'cases': len(cases), 'missing': len(missing)}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('prepare'); p.add_argument('--out', required=True)
    p.add_argument('--nsteps', type=int, default=64); p.add_argument('--group-size', type=int, default=1)
    p.set_defaults(func=prepare)
    p = sub.add_parser('run-group'); p.add_argument('--input', required=True); p.add_argument('--output', required=True)
    p.set_defaults(func=run_group)
    p = sub.add_parser('aggregate'); p.add_argument('--scope'); p.add_argument('--manifest', required=True)
    p.add_argument('--result-files', nargs='+'); p.add_argument('--out', required=True); p.set_defaults(func=aggregate)
    args = parser.parse_args(); args.func(args)


if __name__ == '__main__':
    main()
