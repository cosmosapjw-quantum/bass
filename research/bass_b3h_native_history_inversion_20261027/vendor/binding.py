"""Saved-input identities, unchanged B3f imports, and actual birth moments.

This module never runs a source solve, sweep, angular campaign or trajectory.
"""
from pathlib import Path
import hashlib
import importlib
import json
import math
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
ROUND = 512 * np.finfo(float).eps
C = 299792458.0
MODEL = 'MANUFACTURED_COLD_NON_TILTED_RECOIL_FREE_DETACHED_FPLUS_ZERO_BIANCHI_I'


def read_json(relative):
    return json.loads((ROOT / relative).read_text())


def verify_inputs():
    manifest = read_json('inputs/MANIFEST.json')
    for row in manifest['files']:
        path = ROOT / row['destination']
        if not path.exists() and row.get('optional_for_consumer',False):
            continue  # Reuse the saved owner admission; never reconstruct queries.
        if path.stat().st_size != row['bytes'] or hashlib.sha256(path.read_bytes()).hexdigest() != row['sha256']:
            raise ValueError('immutable input byte mismatch: ' + row['destination'])
    return manifest


def reused_modules():
    """Verify exact selected dependencies before importing unchanged code."""
    verify_inputs()
    reuse = ROOT / 'inputs/b3f'
    sys.path.insert(0, str(reuse / 'code'))
    sys.path.insert(0, str(reuse))
    finite = importlib.import_module('cohort_input_error')
    core = importlib.import_module('vendor.core')
    if Path(finite.__file__).resolve() != reuse / 'code/cohort_input_error.py' or Path(core.__file__).resolve() != reuse / 'vendor/core.py':
        raise ValueError('incorrect reused module identity')
    return finite, core


def real(x, shape, name):
    a = np.asarray(x)
    if a.shape != shape or a.dtype.kind not in 'fiu' or not np.all(np.isfinite(a)):
        raise ValueError(name + ' requires finite real shape ' + str(shape))
    return a.astype(float, copy=False)


def birth_moments(S, n, energy):
    S = real(S, (3, 3), 'S')
    n = float(real(n, (), 'n')); energy = float(real(energy, (), 'energy'))
    if n <= 0 or energy <= 0:
        raise ValueError('positive birth number and source energy required')
    if np.max(np.abs(S-S.T)) > ROUND or abs(np.trace(S)) > ROUND or np.linalg.eigvalsh(S)[0] < -1:
        raise ValueError('nonphysical source angular tensor')
    weight = energy * n
    if not math.isfinite(weight) or weight <= 0:
        raise ValueError('positive finite emitted energy scale required')
    pi = 2 * weight * S / 15
    T = np.zeros((4, 4)); T[0, 0] = weight
    T[1:, 1:] = weight * (np.eye(3)/3 + 2*S/15)
    return T, pi


def bind_birth(receipt, fixture, snapshot, finite):
    """Consume a gross receipt exactly once; its count is already integrated."""
    ledger = receipt['ledger']; owner = ledger['owner_map']
    if ledger['up_m3'] != 0 or owner['f_plus'] != 0:
        raise ValueError('selected source requires exactly zero upward count and f_plus')
    n = ledger['down_m3']; energy = fixture['card']['energy_J']
    if finite.p.EB != energy:
        raise ValueError('unchanged B3f fixed source energy differs from actual receipt card')
    T, pi = birth_moments(receipt['midpoint_S'], n, energy)
    w = T[0, 0]; stock = receipt['midpoint_N_m3']
    if not math.isfinite(stock) or stock <= 0:
        raise ValueError('positive atom stock scale required')
    dtau = receipt['source_subflow_duration_tau']
    if not math.isfinite(dtau) or dtau <= 0:
        raise ValueError('positive authoritative source-subflow duration required')
    endpoint_dtau = receipt['interval_end_tau'] - receipt['interval_start_tau']
    expected_dt = fixture['L_m'] * dtau / C
    representation = dict(
        energy=(T[0, 0]-owner['delta_u_radiation_J_m3'])/w,
        spatial=(T[1:, 1:]-np.asarray(owner['radiation_spatial_packet_J_m3']))/w,
        pi=(pi-np.asarray(owner['energy_PSTF_packet_J_m3']))/w,
        atomic_upper_loss=(owner['delta_n_upper_m3']+n)/n,
        atomic_lower_gain=(owner['delta_n_lower_m3']-n)/n,
        duration=(receipt['source_subflow_duration_s']-expected_dt)/expected_dt,
        ledger_duration=(ledger['dt_s']-expected_dt)/expected_dt)
    stocks = dict(
        upper_loss=(receipt['upper_before_m3']-receipt['upper_after_m3']-n)/stock,
        lower_gain=(receipt['lower_after_m3']-receipt['lower_before_m3']-n)/stock,
        total_atoms=((receipt['upper_after_m3']+receipt['lower_after_m3'])-(receipt['upper_before_m3']+receipt['lower_before_m3']))/stock)
    if min(receipt[k] for k in ['upper_before_m3','upper_after_m3','lower_before_m3','lower_after_m3']) < 0:
        raise ValueError('negative atom stock')
    for label, value in {**representation, **stocks}.items():
        if not np.all(np.isfinite(value)) or np.max(np.abs(value)) > ROUND:
            raise ArithmeticError('birth representation tolerance: ' + label)
    certificate = finite.ball(receipt['midpoint_S'], np.eye(3), n, 0, eR=0, eS=None, en=None)
    if certificate['status'] != 'INPUT_ERROR_UNSPECIFIED':
        raise ArithmeticError('unspecified source uncertainty unexpectedly certified')
    return dict(transfer_id=receipt['transfer_id'], physical_transfer_key=receipt['physical_transfer_key'],
        source_snapshot=snapshot, source_model=MODEL, tau_birth=receipt['deposition_epoch_tau'],
        interval_tau=[receipt['interval_start_tau'],receipt['interval_end_tau']],
        source_subflow_duration_tau=dtau,
        interval_endpoint_subtraction_minus_source_duration_tau=endpoint_dtau-dtau,
        fixed_L_m=fixture['L_m'], proper_seconds=receipt['source_subflow_duration_s'], frame=fixture['frame'],
        card=fixture['card'], closure=fixture['closure'], S=receipt['midpoint_S'],
        n_b_m3=n, E_b_J=energy, R=np.eye(3), detR=1., T_J_m3=T, pi_J_m3=pi,
        alpha_birth=-math.log(stock/fixture['N0_m3'])/3,
        alpha_birth_status='NOMINAL_LOG_DENSITY_RECONSTRUCTION_NOT_ORIGINAL_ALPHA_BYTES',
        alpha_birth_numerical_error_bound=None,
        B_T_birth=0., B_T_provenance='Q14_EXACT_DEGREE_FOUR_AT_BIRTH',
        physical_radii=dict(eR=0.,eR_provenance='R(t_b,t_b)=I_SAME_EVENT_AND_FRAME',
            eS=None,en=None,eE=None,missing_reasons=dict(
                eS='B3c manufactured angular source has no physical model-error radius',
                en='B3c integrated source count has no physical source-error radius',
                eE='B3c unchanged effective card supplies no physical source-energy radius')),
        fixed_energy_B3f_ball=certificate,source_energy_uncertainty_outside_fixed_E_theorem=True,
        final_transport=dict(status='INPUT_DEPENDENT',R=None,
            missing_fields=['midpoint_beta_birth','midpoint_beta_interpolation_error_bound']),
        signed_representation_residuals=representation, signed_atom_stock_residuals=stocks,
        atom_stock_scale_m3=stock, representation_scale_J_m3=w, whole_physical_error=None)


def serializable(value):
    if isinstance(value,np.ndarray): return value.tolist()
    if isinstance(value,np.generic): return value.item()
    raise TypeError(type(value).__name__)


def write_json(path, value):
    path.write_text(json.dumps(value, default=serializable, indent=2, allow_nan=False)+'\n')
