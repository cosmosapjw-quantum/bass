"""LINE01 detached bound-bound source and exact local thick-model map.

SI physical densities; c, h=2*pi*hbar, k_B explicit. No cosmological IVP.
The primary collapsed card is a declared coincident-line model, not native parity.
"""
from __future__ import annotations

import ast
from collections import Counter
from dataclasses import dataclass, asdict
import csv
import hashlib
import math
from pathlib import Path
import sys
import types
from typing import Any

import numpy as np
from scipy.optimize import brentq
import escape_moments as angular

C = 299792458.0
H_PLANCK = 6.62607015e-34
HBAR = H_PLANCK / (2.0 * math.pi)
K_B = 1.380649e-23
EV_J = 1.602176634e-19
EPS = np.finfo(float).eps
THICK_EPSILON = 1.0e-8
THICK_THRESHOLD = math.log1p(1.0 / THICK_EPSILON)
ROOT = Path(__file__).resolve().parents[1]
COUNTERS: Counter[str] = Counter()


@dataclass(frozen=True)
class SourceCard:
    id: str
    population_scope: str
    g: float
    A_s_inv: float
    energy_J: float
    wavelength_m: float
    frequency_Hz: float
    source: str
    physical_uncertainty: str
    closure: str


def _card(key, scope, g, A, *, energy_eV=None, wavelength_m=None, closure):
    energy = energy_eV * EV_J if energy_eV is not None else H_PLANCK * C / wavelength_m
    wavelength = H_PLANCK * C / energy if wavelength_m is None else wavelength_m
    return SourceCard(key, scope, float(g), float(A), energy, wavelength,
                      energy / H_PLANCK,
                      'NIST_HI_PERSISTENT + native E21' if energy_eV else 'NIST_HI_PERSISTENT',
                      'NOT_PROVIDED_ON_TABLE; model error not angular tolerance', closure)


CARDS = {
    'H_LYA_EFFECTIVE_2P': _card('H_LYA_EFFECTIVE_2P', 'collapsed_2p', 3,
        (626490000.0 + 2.0 * 626480000.0) / 3.0, energy_eV=10.198714553953742,
        closure='effective coincident lines; statistical 1:2 sublevels; common profile/frequency/f_plus'),
    'H_LYA_J1HALF': _card('H_LYA_J1HALF', '2p_J1half', 1, 626490000.0,
        wavelength_m=1215.67364e-10, closure='isolated fine component, all magnetic substates'),
    'H_LYA_J3HALF': _card('H_LYA_J3HALF', '2p_J3half', 2, 626480000.0,
        wavelength_m=1215.66824e-10, closure='isolated unpolarized fine component, all magnetic substates'),
}


def finite_scalar(value: Any, name: str, *, positive=False, nonnegative=False) -> float:
    if isinstance(value, (bool, np.bool_)) or np.ndim(value) != 0 or np.iscomplexobj(value):
        raise ValueError(f'{name} must be a finite real scalar')
    try:
        value = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f'{name} must be a finite real scalar') from exc
    if not math.isfinite(value) or (positive and value <= 0) or (nonnegative and value < 0):
        raise ValueError(f'invalid {name}')
    return value


def source_card(card: str | SourceCard) -> SourceCard:
    if isinstance(card, str):
        if card not in CARDS:
            raise ValueError('Unknown or incompatible source card; whole-n=2 shell is excluded')
        return CARDS[card]
    if not isinstance(card, SourceCard) or card.id not in CARDS or card != CARDS[card.id]:
        raise ValueError('Source card differs from the frozen coefficient/population registry')
    return card


def validate_owner(owner_mode: str, native_line_owner_active: bool) -> None:
    if owner_mode != 'standalone_detached' or native_line_owner_active is not False:
        raise ValueError('Exclusive detached owner required; canonical native-line addition is forbidden')


def _readonly(a):
    result = np.array(a, dtype=float, copy=True)
    result.setflags(write=False)
    return result


@dataclass(frozen=True)
class LineState:
    card_id: str
    population_scope: str
    n_l_m3: float
    n_u_m3: float
    H_s_inv: float
    f_plus: float
    S: np.ndarray
    state_provenance: str
    angular_provenance: str = 'SUPPLIED_FIXTURE_NOT_NATIVE_ANGULAR_STATE'
    owner_mode: str = 'standalone_detached'
    native_line_owner_active: bool = False
    n_H_reference_m3: float | None = None

    def __post_init__(self):
        card = source_card(self.card_id)
        validate_owner(self.owner_mode, self.native_line_owner_active)
        if self.population_scope != card.population_scope:
            raise ValueError('Population scope does not match source card')
        for key in ('n_l_m3', 'n_u_m3', 'f_plus'):
            object.__setattr__(self, key, finite_scalar(getattr(self, key), key, nonnegative=True))
        object.__setattr__(self, 'H_s_inv', finite_scalar(self.H_s_inv, 'H', positive=True))
        N = self.n_l_m3 + self.n_u_m3
        delta = card.g * self.n_l_m3 - self.n_u_m3
        if not math.isfinite(N) or N <= 0 or not math.isfinite(delta) or delta <= 0:
            raise ValueError('Finite positive total density and strictly non-inverted opacity required')
        if self.n_H_reference_m3 is not None:
            object.__setattr__(self, 'n_H_reference_m3', finite_scalar(self.n_H_reference_m3,
                                  'n_H_reference_m3', positive=True))
        validated = angular.validate_inputs(1.0, self.S)
        object.__setattr__(self, 'S', _readonly(validated.tensor))
        if not self.state_provenance or not self.angular_provenance:
            raise ValueError('Source and angular provenance are required')

    @property
    def card(self):
        return source_card(self.card_id)

    @property
    def N(self):
        return self.n_l_m3 + self.n_u_m3

    @property
    def x(self):
        return self.n_u_m3 / self.N


def driving_fraction(g: float, f: float, driving: str) -> float:
    eq = g * f / (1.0 + (g + 1.0) * f)
    if driving == 'LTE':
        return eq
    if driving == 'emission':
        return 0.5 * (eq + g / (g + 1.0))
    if driving == 'absorption' and f > 0:
        return 0.5 * eq
    raise ValueError('Unsupported driving case')


def shear_fixtures() -> dict[str, np.ndarray]:
    a, b = 0.37, 0.41
    Rz = np.array([[math.cos(a), -math.sin(a), 0], [math.sin(a), math.cos(a), 0], [0, 0, 1]])
    Ry = np.array([[math.cos(b), 0, math.sin(b)], [0, 1, 0], [-math.sin(b), 0, math.cos(b)]])
    triaxial = np.diag([-0.4, 0.1, 0.3])
    R = Rz @ Ry
    return {'isotropic': np.zeros((3, 3)), 'triaxial': triaxial,
            'rotated': R @ triaxial @ R.T}


def state_at_depth(card_id: str, driving: str, t: float, S: np.ndarray,
                   *, N=1.0e9, f_plus=0.1) -> LineState:
    card = source_card(card_id)
    x = driving_fraction(card.g, f_plus, driving)
    upper = N * x
    lower = N - upper
    delta = card.g * lower - upper
    H = card.A_s_inv * card.wavelength_m**3 * delta / (8.0 * math.pi * t)
    return LineState(card.id, card.population_scope, lower, upper, H, f_plus, S,
                     f'CONSTRUCTED_{driving}_N={N}_target_depth={t}', n_H_reference_m3=N)


def native_snapshot_state(S: np.ndarray) -> tuple[LineState, dict]:
    path = ROOT / 'fixtures/ORIGINAL_HYREC_TRAJECTORY_SNAPSHOT.csv'
    raw = path.read_bytes()
    blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    if blob != '6399b59ca3c97d6c5b1162f83f50a6677fad06ff':
        raise ValueError('Pinned native source snapshot byte identity failed')
    rows = list(csv.reader(raw.decode().splitlines()))
    fields = {r[1]: r[2] for r in rows if r[0] == 'META'}
    real = {int(r[1]): float(r[2]) for r in rows if r[0] == 'REAL'}
    m = {k: float(v) for k, v in fields.items()}
    if m['fsR'] != 1 or m['meR'] != 1:
        raise ValueError('Only saved fsR=meR=1 snapshot is selected')
    E21 = 10.198714553953742
    nH = m['nH_cm3'] * 1.0e6
    w = math.exp(-E21 / m['TR_eV_rescaled'])
    x2p = real[1] + 3.0 * m['x1s'] * w
    f_planck = 1.0 / math.expm1(E21 / m['TR_eV_rescaled'])
    state = LineState('H_LYA_EFFECTIVE_2P', 'collapsed_2p', nH * m['x1s'], nH * x2p,
                      m['H_sInv'], f_planck + m['Dfplus_Lya'], S,
                      'PREEXISTING_NATIVE_FLRW_FULL_STATE_READ_ONLY', n_H_reference_m3=nH)
    return state, {'snapshot_blob': blob, 'snapshot_sha256': hashlib.sha256(raw).hexdigest(),
        'source_decimal_fields': fields, 'x2p_restored': x2p, 'xr2p_signed': real[1],
        'native_Wien_factor': w, 'Planck_background': f_planck,
        'f_plus_total': state.f_plus, 'T_R_K_modern_SI': m['TR_eV_rescaled'] * EV_J / K_B,
        'T_R_K_native': m['TR_eV_rescaled'] / 8.617343e-5,
        'mode': 'standalone full-Planck/stimulated source; NOT native compressed-source parity',
        'new_native_solver_calls': 0}


def _ensure_finite(value, label):
    a = np.asarray(value)
    if not np.all(np.isfinite(a)):
        raise ValueError(f'{label} is outside representable numeric contract')


def exchange_source(state: LineState, *, n_mu=64, n_phi=128) -> dict:
    if not isinstance(state, LineState):
        raise ValueError('A validated LineState is required')
    card = state.card
    delta = card.g * state.n_l_m3 - state.n_u_m3
    t = card.A_s_inv * card.wavelength_m**3 * delta / (8.0 * math.pi * state.H_s_inv)
    finite_scalar(t, 'optical depth', positive=True)
    moments = angular.angular_moments(t, state.S, n_mu=n_mu, n_phi=n_phi, mode='quadrature')
    F = 1.0 + (card.g + 1.0) * state.f_plus
    xeq = card.g * state.f_plus / F
    D = state.N * F * (state.x - xeq)
    down_micro = state.n_u_m3 * (1.0 + state.f_plus)
    up_micro = card.g * state.n_l_m3 * state.f_plus
    gross = down_micro + up_micro
    R = card.A_s_inv * moments.mean * D
    down = card.A_s_inv * moments.mean * down_micro
    up = card.A_s_inv * moments.mean * up_micro
    Q = moments.pstf
    number_pstf = card.A_s_inv * D * Q
    energy = card.energy_J * R
    energy_pstf = card.energy_J * number_pstf
    pressure = card.energy_J * card.A_s_inv * D * (moments.mean * np.eye(3) / 3.0 + Q)
    for value in (F, D, gross, R, down, up, number_pstf, energy_pstf, pressure):
        _ensure_finite(value, 'line source')
    result = {'card_id': card.id, 'population_scope': card.population_scope,
        'state_provenance': state.state_provenance, 'angular_provenance': state.angular_provenance,
        'owner_mode': state.owner_mode, 'native_line_owner_active': False,
        'N_m3': state.N, 'n_l_m3': state.n_l_m3, 'n_u_m3': state.n_u_m3,
        'H_s_inv': state.H_s_inv, 'f_plus': state.f_plus, 'S': state.S,
        'x': state.x, 'x_eq': xeq, 'opacity_delta_m3': delta,
        'driving_defect_m3': D, 'gross_microscopic_density_m3': gross,
        'gross_to_net_condition': gross / abs(D) if D != 0 else None,
        't': t, 'B': moments.mean, 'Q': Q, 'angular_nodes': moments.nodes,
        'gross_escaped_down_m3_s': down, 'gross_escaped_up_m3_s': up,
        'net_R_m3_s': R, 'dn_upper_m3_s': -R, 'dn_lower_m3_s': R, 'dn_gamma_m3_s': R,
        'du_internal_J_m3_s': -energy, 'du_radiation_J_m3_s': energy, 'du_thermal_J_m3_s': 0.0,
        'ionic_yield': 0.0, 'free_electron_yield': 0.0,
        'number_PSTF_m3_s': number_pstf, 'energy_PSTF_J_m3_s': energy_pstf,
        'radiation_spatial_injection_J_m3_s': pressure, 'odd_momentum_injection': np.zeros(3),
        'atom_number_residual': (-R) + R, 'photon_upper_residual': R + (-R),
        'energy_residual': (-energy) + energy,
        'gross_difference_residual_over_micro': abs(D - (down_micro - up_micro)) / max(gross, 1e-300),
        'pressure_trace_residual_over_energy_gross': abs(np.trace(pressure) - energy) /
             max(card.energy_J * card.A_s_inv * moments.mean * gross, 1e-300),
        'PSTF_trace_over_energy_gross': abs(np.trace(energy_pstf)) /
             max(card.energy_J * card.A_s_inv * moments.mean * gross, 1e-300),
        'lte_residual_over_gross': abs(D) / max(gross, 1e-300),
        'bounds': moments.analytic_bounds}
    COUNTERS['source_rows'] += 1
    return result


def load_exact_einstein_class() -> tuple[type, dict]:
    path = ROOT / 'vendor/rec_source_adapter.py'
    raw = path.read_bytes()
    blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    if blob != '00b9eceec888839a0d1cd7644e569a397d4f7279':
        raise ValueError('Pinned Einstein donor byte identity failed')
    text = raw.decode()
    parsed = ast.parse(text, filename=str(path))
    nodes = [node for node in parsed.body if isinstance(node, (ast.FunctionDef, ast.ClassDef))
             and node.name in ('_readonly', 'IsotropicEinsteinLineSource')]
    if len(nodes) != 2:
        raise ValueError('Donor class/function extraction failed')
    module = types.ModuleType('line01_exact_einstein_donor')
    module.__dict__.update(dataclass=dataclass, math=math, np=np, c=C, h=H_PLANCK, k=K_B)
    sys.modules[module.__name__] = module
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), 'exec'), module.__dict__)
    identities = []
    lines = text.splitlines(keepends=True)
    for node in nodes:
        first = min([node.lineno] + [x.lineno for x in node.decorator_list])
        segment = ''.join(lines[first - 1:node.end_lineno]).encode()
        identities.append({'name': node.name, 'first_line': first, 'last_line': node.end_lineno,
                           'source_segment_sha256': hashlib.sha256(segment).hexdigest()})
    return module.IsotropicEinsteinLineSource, {'method': 'AST unchanged class/function nodes; unrelated native imports excluded',
        'donor_git_blob_sha1': blob, 'donor_sha256': hashlib.sha256(raw).hexdigest(),
        'namespace': ['dataclass', 'math', 'numpy', 'c', 'h', 'k_B'], 'segments': identities}


def _log_value(logarithm: float | None) -> dict:
    if logarithm is None:
        return {'value': 0.0, 'log_value': None, 'representation': 'EXACT_ZERO'}
    value = math.exp(logarithm) if logarithm <= math.log(sys.float_info.max) else math.inf
    if value == 0.0:
        return {'value': None, 'log_value': logarithm, 'representation': 'UNDERFLOW_USE_LOG'}
    if not math.isfinite(value):
        return {'value': None, 'log_value': logarithm, 'representation': 'OVERFLOW_USE_LOG'}
    return {'value': value, 'log_value': logarithm, 'representation': 'FLOAT_NOT_INTERVAL'}


def solve_log_flow(z0: float, omega: float) -> tuple[float, float, int]:
    z0 = finite_scalar(z0, 'z0')
    omega = finite_scalar(omega, 'omega', nonnegative=True)
    if z0 <= -1:
        raise ValueError('Principal physical branch requires z0>-1')
    if omega == 0:
        return 0.0, 0.0, 0
    lower = -omega + min(z0, 0.0)
    upper = min(0.0, -omega + max(z0, 0.0))
    # Outward rounding preserves a bracket when |z0| is below an ulp of omega.
    # The real-valued proof interval is unchanged; no residual tolerance is relaxed.
    lower = math.nextafter(lower, -math.inf)
    upper = min(0.0, math.nextafter(upper, math.inf))
    def residual(u):
        COUNTERS['log_root_function_evaluations'] += 1
        return math.fsum((u, z0 * math.expm1(u), omega))
    fl, fu = residual(lower), residual(upper)
    if fl > 0 or fu < 0:
        raise ValueError('Physical log-root bracket not representable')
    if fl == 0:
        return lower, fl, 0
    if fu == 0:
        return upper, fu, 0
    u, report = brentq(residual, lower, upper, xtol=float(np.nextafter(0.0, 1.0)),
                       rtol=4.0 * EPS, maxiter=128, full_output=True, disp=True)
    if not report.converged:
        raise ArithmeticError('Bounded local scalar root did not converge')
    COUNTERS['log_root_solves'] += 1
    return u, residual(u), int(report.iterations)


def thick_local_step(*, card_id: str, population_scope: str, N_m3: float,
                     x0: float, H_s_inv: float, f_plus: float, S: np.ndarray,
                     omega: float, owner_mode='standalone_detached',
                     native_line_owner_active=False) -> dict:
    card = source_card(card_id)
    validate_owner(owner_mode, native_line_owner_active)
    if population_scope != card.population_scope:
        raise ValueError('Map population scope does not match card')
    N = finite_scalar(N_m3, 'N', positive=True)
    H = finite_scalar(H_s_inv, 'H', positive=True)
    x0 = finite_scalar(x0, 'x0', nonnegative=True)
    f = finite_scalar(f_plus, 'f_plus', nonnegative=True)
    omega = finite_scalar(omega, 'omega', nonnegative=True)
    b = card.g + 1.0
    if x0 >= card.g / b:
        raise ValueError('Non-inverted population domain required')
    geometry = angular.validate_inputs(1.0, S)
    F = 1.0 + b * f
    xeq = card.g * f / F
    d0 = card.g / F
    y0 = x0 - xeq
    z0 = -b * y0 / d0
    kappa = 8.0 * math.pi * H / (N * card.wavelength_m**3)
    eta = kappa * F / d0
    dt = omega / eta
    dmin = card.g - b * max(x0, xeq)
    tmin = card.A_s_inv * card.wavelength_m**3 * N * dmin / (8.0 * math.pi * H)
    path_ratio = tmin / geometry.qmax
    for value in (F, xeq, d0, y0, z0, eta, dt, dmin, tmin, path_ratio):
        _ensure_finite(value, 'local map')
    if dmin <= 0 or path_ratio < THICK_THRESHOLD:
        raise ValueError('Whole-path optically thick gate failed')
    log_delta = -path_ratio
    delta = math.exp(log_delta)
    if y0 == 0.0 or omega == 0.0:
        u, residual, iterations = 0.0, 0.0, 0
        dx, x1, u_slow, width = 0.0, x0, 0.0, 0.0
    else:
        u, residual, iterations = solve_log_flow(z0, omega)
        dx = y0 * math.expm1(u)
        x1 = xeq + y0 * math.exp(u)
        if delta == 0.0 or (1.0 - delta) * omega == omega:
            u_slow = u
        else:
            u_slow, _, _ = solve_log_flow(z0, (1.0 - delta) * omega)
        # Difference of departures, not subtraction of rounded endpoints.
        width = abs(y0 * math.exp(u) * math.expm1(u_slow - u))
    packet = -N * dx
    K = 2.0 * geometry.tensor / 15.0
    energy = card.energy_J * packet
    K_norm = float(np.linalg.norm(K, ord='fro'))
    log_shape = math.log(K_norm + math.sqrt(2.0 / 3.0)) + log_delta - math.log1p(-delta)
    log_width_coarse = (log_delta + math.log(omega) + math.log(abs(y0)) - math.log1p(z0)
                       if omega > 0.0 and y0 != 0.0 else None)
    shape = _log_value(log_shape)
    coarse = _log_value(log_width_coarse)
    # Exact analytic coarse upper bound remains meaningful if numerical width rounds to zero.
    log_terms = []
    if K_norm > 0 and log_width_coarse is not None:
        log_terms.append(math.log(K_norm) + log_width_coarse)
    if abs(dx) > 0:
        log_terms.append(math.log(abs(dx)) + log_shape)
    log_tensor_number = None
    if log_terms:
        mx = max(log_terms)
        log_tensor_number = math.log(N) + mx + math.log(sum(math.exp(x - mx) for x in log_terms))
    lower = min(x1, xeq + y0 * math.exp(u_slow))
    upper = max(x1, xeq + y0 * math.exp(u_slow))
    result = {'card_id': card.id, 'population_scope': population_scope,
        'owner_mode': owner_mode, 'native_line_owner_active': False,
        'N_m3': N, 'x0': x0, 'x_eq': xeq, 'x1': x1, 'y0': y0,
        'g': card.g, 'b': b, 'F': F, 'd0': d0, 'z0': z0,
        'H_s_inv': H, 'f_plus': f, 'S': geometry.tensor, 'omega': omega, 'delta_t_s': dt,
        'eta_s_inv': eta, 'u': u, 'log_root_residual': residual, 'root_iterations': iterations,
        'dx': dx, 'delta_n_gamma_m3': packet, 'delta_n_upper_m3': -packet,
        'delta_n_lower_m3': packet, 'delta_u_radiation_J_m3': energy,
        'delta_u_internal_J_m3': -energy, 'delta_u_thermal_J_m3': 0.0,
        'ionic_yield': 0.0, 'free_electron_yield': 0.0,
        'number_PSTF_packet_m3': packet * K,
        'energy_PSTF_packet_J_m3': energy * K,
        'radiation_spatial_packet_J_m3': energy * (np.eye(3) / 3.0 + K),
        'odd_momentum_packet': np.zeros(3), 'path_t_min': tmin,
        'path_qmax': geometry.qmax, 'path_depth_ratio': path_ratio,
        'log_delta': log_delta, 'delta_float': delta,
        'delta_representation': 'UNDERFLOW_USE_LOG' if delta == 0.0 else 'FLOAT_NOT_INTERVAL',
        'finite_endpoint_bracket_float': [lower, upper], 'bracket_width_float': width,
        'bracket_width_status': 'ROUNDED_UNRESOLVED_NOT_EXACT_EQUALITY' if width == 0 and y0 != 0 and omega > 0 else 'FLOAT_NOT_INTERVAL',
        'coarse_population_error_upper_bound': coarse,
        'coarse_energy_error_upper_bound': _log_value(None if log_width_coarse is None else
                                                     math.log(card.energy_J * N) + log_width_coarse),
        'tensor_shape_error_upper_bound': shape,
        'coarse_tensor_number_error_upper_bound': _log_value(log_tensor_number),
        'coarse_tensor_energy_error_upper_bound': _log_value(None if log_tensor_number is None else
                                                         math.log(card.energy_J) + log_tensor_number),
        'certificate': 'ANALYTIC_MODEL_TRUNCATION; float evaluation is not interval arithmetic',
        'atom_number_residual': (-packet) + packet,
        'photon_upper_residual': packet + (-packet), 'energy_residual': (-energy) + energy}
    COUNTERS['local_map_outputs'] += 1
    return result


def local_fixture(*, f_plus, driving, omega, S, path_ratio=20.0) -> dict:
    card = CARDS['H_LYA_EFFECTIVE_2P']
    N = 1.0e9
    x0 = driving_fraction(card.g, f_plus, driving)
    xeq = card.g * f_plus / (1.0 + (card.g + 1.0) * f_plus)
    qmax = angular.validate_inputs(1.0, S).qmax
    dmin = card.g - (card.g + 1.0) * max(x0, xeq)
    H = card.A_s_inv * card.wavelength_m**3 * N * dmin / (8.0 * math.pi * path_ratio * qmax)
    return dict(card_id=card.id, population_scope=card.population_scope, N_m3=N,
                x0=x0, H_s_inv=H, f_plus=f_plus, S=S, omega=omega)
