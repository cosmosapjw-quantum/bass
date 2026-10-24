"""One focused independent admission/depletion probe; no suite or IVP.

The implementation test fixture is reused solely to construct the actual
core/kinetic receiver. The depletion oracle is the unchanged REC owner's
positive finite endpoint, not the candidate's subtraction-based stock update.
"""
from dataclasses import replace
import json
from pathlib import Path
import sys
import warnings

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tests'))
from test_finite_exchange import transaction_fixture, duration, fx


def snapshot(kwargs):
    state, source = kwargs['state'], kwargs['source']
    return {
        'state': state.pack().copy(),
        'pressure': np.asarray(source.pressure).copy(),
        'pi': np.asarray(source.pi).copy(),
        'energy_transfer': None if source.energy_transfer is None else np.asarray(source.energy_transfer).copy(),
        'momentum_transfer': None if source.momentum_transfer is None else np.asarray(source.momentum_transfer).copy(),
        'photon_k': kwargs['photons'].k.copy(),
        'photon_w': kwargs['photons'].w.copy(),
        'photon_mass': kwargs['photons'].mass.copy(),
        'line_S': kwargs['line'].S.copy(),
        'population': (kwargs['population'].n_u_m3, kwargs['population'].n_l_m3, kwargs['population'].applied),
    }


def unchanged(before, kwargs):
    after = snapshot(kwargs)
    return all((before[k] == after[k]) if k == 'population' else
               (after[k] is None if before[k] is None else np.array_equal(before[k], after[k]))
               for k in before)


records = []
kwargs = transaction_fixture()
kwargs['dt_s'] = duration(kwargs['line'], 50.0)
excitation_scale = kwargs['scale'].density_factor * kwargs['line'].card.energy_J
kwargs['state'].rho[0] = excitation_scale * kwargs['population'].n_u_m3
before = snapshot(kwargs)
out = fx.commit_emission(**kwargs)
owner_remaining = kwargs['line'].N * out['ledger']['owner_map']['x1']
records.append({
    'case': 'large_finite_depletion_omega_50',
    'owner_endpoint_x1': out['ledger']['owner_map']['x1'],
    'owner_remaining_upper_m3': owner_remaining,
    'candidate_remaining_upper_m3': out['population'].n_u_m3,
    'owner_remaining_excitation_fixed_units': excitation_scale * owner_remaining,
    'candidate_remaining_atomic_energy_fixed_units': float(out['state'].rho[0]),
    'net_count_m3': out['ledger']['net_m3'],
    'committed': True,
    'inputs_unchanged': unchanged(before, kwargs),
    'contract_problem_observed': owner_remaining > 0 and out['population'].n_u_m3 == 0,
})

kwargs = transaction_fixture()
kwargs['state'].n = kwargs['state'].n.astype(complex)
kwargs['state'].n[0, 0] += 0.01j
before = snapshot(kwargs)
with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter('always')
    try:
        out = fx.commit_emission(**kwargs)
        accepted = True
        detail = {'returned_n00': repr(out['state'].n[0, 0]),
                  'returned_constraint_scale': out['tolerance']['constraint_gross_scale']}
    except Exception as exc:
        accepted = False
        detail = {'exception': type(exc).__name__, 'message': str(exc)}
records.append({'case': 'nonreal_geometry_n', 'committed': accepted,
                'contract_problem_observed': accepted,
                'inputs_unchanged': unchanged(before, kwargs),
                'warnings': [str(w.message) for w in caught], **detail})

kwargs = transaction_fixture()
kwargs['dt_s'] = np.array([kwargs['dt_s']])
before = snapshot(kwargs)
try:
    fx.commit_emission(**kwargs)
    accepted, detail = True, {}
except Exception as exc:
    accepted, detail = False, {'exception': type(exc).__name__, 'message': str(exc)}
records.append({'case': 'nonscalar_duration', 'committed': accepted,
                'contract_problem_observed': accepted,
                'inputs_unchanged': unchanged(before, kwargs), **detail})

kwargs = transaction_fixture(occupied=True)
kwargs['photons'] = replace(kwargs['photons'], w=kwargs['photons'].w.astype(complex))
before = snapshot(kwargs)
try:
    fx.commit_emission(**kwargs)
    accepted, detail = True, {}
except Exception as exc:
    accepted, detail = False, {'exception': type(exc).__name__, 'message': str(exc)}
records.append({'case': 'complex_photon_weight_array', 'committed': accepted,
                'contract_problem_observed': accepted,
                'inputs_unchanged': unchanged(before, kwargs), **detail})

print(json.dumps({'scope': 'single targeted independent code review probe',
                  'new_ivp': 0, 'campaign_replay': 0, 'records': records}, indent=2))
raise SystemExit(1 if any(r['contract_problem_observed'] for r in records) else 0)
