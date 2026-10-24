"""Frozen LINE01 gross ledger and canonical-rest finite emission transaction.

The prescribed incoming boundary f is not a finite photon bath. Only f=0 may
commit state stocks. Source owner and kinetic/core routines are unchanged.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
import copy
import math
from pathlib import Path
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'vendor/rec_line_source/code'))
import line_source as owner
from vendor import core, kinetic

EPS = np.finfo(float).eps
ROUND_FACTOR = 256 * EPS
FRAME = 'rest'
CLOCK = 'proper_time_dt_dV_invariant'


def a_and_r(v):
    """a=1-exp(-v), r=v-a; report alternating-series truncation separately.

    On [0,1/2] each omitted term is smaller in magnitude than its predecessor.
    The next-term bound is mathematical truncation, not a rounding enclosure.
    """
    v = owner.finite_scalar(v, 'v', nonnegative=True)
    a = -math.expm1(-v)
    if v == 0:
        return a, 0.0, 0.0, 0
    if v > 0.5:
        return a, v + math.expm1(-v), 0.0, 0
    term = v * (v / 2)
    if term == 0:
        raise ArithmeticError('positive r(v) underflows; analytic ledger unresolved')
    terms = [term]
    for degree in range(2, 65):
        following = -term * v / (degree + 1)
        if abs(following) <= EPS * abs(math.fsum(terms)):
            return a, math.fsum(terms), abs(following), len(terms)
        terms.append(following)
        term = following
    raise ArithmeticError('bounded r Taylor series did not converge')


def gross_counts(line: owner.LineState, dt_s: float):
    """Integrated positive gross channels; stable net remains owner -N*dx."""
    if not isinstance(line, owner.LineState):
        raise ValueError('validated actual owner LineState required')
    dt = owner.finite_scalar(dt_s, 'dt_s', nonnegative=True)
    card, N, f = line.card, line.N, line.f_plus
    F = 1 + (card.g + 1) * f
    xe = card.g * f / F
    de = card.g / F
    k = 8 * math.pi * line.H_s_inv / (N * card.wavelength_m**3)
    eta = k * F / de
    omega = eta * dt
    mapped = owner.thick_local_step(card_id=card.id,
        population_scope=line.population_scope, N_m3=N, x0=line.x,
        H_s_inv=line.H_s_inv, f_plus=f, S=line.S, omega=omega,
        owner_mode=line.owner_mode, native_line_owner_active=line.native_line_owner_active)
    v = omega if line.x == xe else -mapped['u']
    a, r, next_term, terms = a_and_r(v)
    down = N * (1 + f) / F * math.fsum((line.x * a, xe * r))
    up = N * card.g * f / F * math.fsum(((1-line.x) * a, (1-xe) * r))
    net = mapped['delta_n_gamma_m3']
    if not all(math.isfinite(x) and x >= 0 for x in (down, up)):
        raise ArithmeticError('gross channels outside representable nonnegative domain')
    if dt > 0 and v == 0 and line.x != xe:
        raise ArithmeticError('nonzero flow underflowed')
    if dt > 0 and ((line.x > 0 or f > 0) and down == 0):
        raise ArithmeticError('nonzero down channel underflowed')
    if dt > 0 and f > 0 and up == 0:
        raise ArithmeticError('nonzero up channel underflowed')
    return dict(down_m3=down, up_m3=up, net_m3=net, v=v, a=a, r=r,
        r_next_term_truncation_bound=next_term, r_series_terms=terms,
        dt_s=dt, k_line_s_inv=k, eta_s_inv=eta, owner_map=mapped,
        gross_difference_residual_over_gross=(down-up-net)/(down+up) if down+up else 0.,
        qualification='THICK_MODEL; owner finite-opacity envelopes FLOAT_NOT_INTERVAL; '
                      'no new gross-channel finite-opacity relative certificate')


def cubature14():
    directions = []
    weights = []
    for i in range(3):
        for sign in (-1., 1.):
            row = np.zeros(3); row[i] = sign
            directions.append(row); weights.append(1/15)
    for x in (-1., 1.):
        for y in (-1., 1.):
            for z in (-1., 1.):
                directions.append(np.array([x, y, z]) / math.sqrt(3))
                weights.append(3/40)
    return np.array(directions), np.array(weights)


@dataclass(frozen=True)
class Identity:
    """Concrete physical binding; representation is intentionally not a key."""
    owner: str
    card_id: str
    population_scope: str
    epoch: str
    scale: core.FixedScale
    Pstar: float
    frame: str = FRAME
    clock: str = CLOCK
    representation: str = 'canonical_packet_state'

    def physical(self):
        return (self.owner, self.card_id, self.population_scope, self.epoch,
                self.scale, self.Pstar, self.frame, self.clock)


@dataclass(frozen=True)
class PopulationStock:
    identity: Identity
    n_u_m3: float
    n_l_m3: float
    applied: frozenset = frozenset()


@dataclass(frozen=True)
class PhotonStock:
    identity: Identity
    k: np.ndarray
    w: np.ndarray
    mass: np.ndarray
    applied: frozenset = frozenset()

    @classmethod
    def vacuum(cls, identity):
        return cls(identity, np.empty((0, 3)), np.empty(0), np.empty(0))


def photon_moments(stock):
    """True vacuum bypasses the upstream nonempty packet helper."""
    if stock.k.shape == (0, 3) and stock.w.shape == (0,) and stock.mass.shape == (0,):
        return 0., np.zeros(3), 0., np.zeros((3, 3))
    if np.any(np.asarray(stock.mass) != 0):
        raise ValueError('photon stock must be massless')
    return kinetic.moments(stock.k, stock.w, stock.mass)


def _match(actual, expected, scale, label):
    residual = float(np.max(np.abs(np.asarray(actual)-np.asarray(expected))))
    tolerance = ROUND_FACTOR * scale
    if not math.isfinite(residual) or residual > tolerance:
        raise ValueError(f'{label} mismatch: residual={residual}, tolerance={tolerance}')
    return residual / scale if scale else 0.


def _finite_real_array(value, label):
    """Validate physical inputs before core arithmetic; never discard an Im part."""
    array = np.asarray(value)
    if np.iscomplexobj(array) or array.dtype.kind not in 'fiu' or not np.all(np.isfinite(array)):
        raise ValueError(f'{label} must contain finite real numeric values')


def commit_emission(*, line, source_identity, state_identity, state, source,
                    population, photons, scale, Pstar, dt_s, transfer_id,
                    atomic_sector=0, photon_sector=1):
    """Return copies after all admission checks; never mutate inputs.

    Input U/J must already be zero so unrelated rate sources cannot be erased.
    On rejection callers may retain a separately evaluated analytic gross ledger.
    All stock/energy consistency errors use 256 eps times the stated gross scale.
    """
    if not isinstance(source_identity, Identity) or not isinstance(state_identity, Identity):
        raise ValueError('explicit source/state identity required')
    identity = source_identity
    if not all(isinstance(v, str) and v for v in
               (identity.owner, identity.epoch, identity.card_id, identity.population_scope, transfer_id)):
        raise ValueError('concrete owner/card/scope/epoch/transfer ID required')
    if identity.frame != FRAME or identity.clock != CLOCK:
        raise ValueError('canonical rest frame and proper-time clock required')
    if identity.scale != scale or identity.Pstar != Pstar:
        raise ValueError('source fixed scale/Pstar mismatch')
    owner.finite_scalar(Pstar, 'Pstar', positive=True)
    if scale.c != owner.C:
        raise ValueError('canonical SI source c must match FixedScale')
    for binding in (state_identity, population.identity, photons.identity):
        if binding.physical() != identity.physical():
            raise ValueError('source/state/stock owner, card, scope, epoch, frame, clock or scale mismatch')
    if identity.card_id != line.card_id or identity.population_scope != line.population_scope:
        raise ValueError('line source card/population scope mismatch')
    owner.validate_owner(line.owner_mode, line.native_line_owner_active)
    if line.f_plus != 0:
        raise ValueError('f>0 is prescribed boundary ledger only; no closed stock absorption')
    key = (identity.owner, identity.epoch, transfer_id)
    if key in population.applied or key in photons.applied:
        raise ValueError('physical transfer already charged, independent of representation')
    if population.applied != photons.applied:
        raise ValueError('population/photon transfer histories differ')
    if population.n_u_m3 != line.n_u_m3 or population.n_l_m3 != line.n_l_m3:
        raise ValueError('stale population/source stock')
    if not isinstance(state, core.State) or not isinstance(source, core.Source):
        raise ValueError('actual core.State and core.Source required')
    for label in ('h', 'alpha'):
        owner.finite_scalar(getattr(state, label), 'State.' + label)
    for label in ('sigma', 'n', 'a', 'rho', 'flux'):
        _finite_real_array(getattr(state, label), 'State.' + label)
    for label in ('pressure', 'pi', 'energy_transfer', 'momentum_transfer'):
        value = getattr(source, label)
        if value is not None:
            _finite_real_array(value, 'Source.' + label)
    state.validate()
    ns = len(state.rho)
    if atomic_sector == photon_sector or not (0 <= atomic_sector < ns and 0 <= photon_sector < ns):
        raise ValueError('distinct valid atomic/photon sectors required')
    pressure, pi, U, J = source.arrays(ns)
    if np.any(U != 0) or np.any(J != 0):
        raise ValueError('finite transaction requires zero incoming interval transfer fields')
    h_expected = line.H_s_inv * scale.length_m / scale.c
    _match(state.h, h_expected, abs(h_expected), 'h=H L/c')
    _match(state.sigma, h_expected * line.S, abs(h_expected), 'sigma=h S')
    rho0, flux0, p0, pi0 = photon_moments(photons)
    photon_scale = abs(rho0)
    consistency = {}
    for name, actual, expected in (
            ('rho', state.rho[photon_sector], rho0),
            ('flux', state.flux[photon_sector], flux0),
            ('pressure', pressure[photon_sector], p0),
            ('pi', pi[photon_sector], pi0)):
        consistency[name] = _match(actual, expected, photon_scale, 'photon '+name)
    excitation = scale.density_factor * line.card.energy_J * population.n_u_m3
    if state.rho[atomic_sector] < excitation:
        raise ValueError('atomic sector does not own its excitation energy')
    ledger = gross_counts(line, dt_s)
    D = ledger['net_m3']
    if D < 0 or D > population.n_u_m3:
        raise ArithmeticError('finite donor exceeded')
    drho = scale.density_factor * line.card.energy_J * D
    # D can round to the whole donor while the owner's endpoint is still a
    # positive, representable density. Construct that endpoint, not nu0-D.
    x1 = ledger['owner_map']['x1']
    if D == 0:
        nu1, nl1 = population.n_u_m3, population.n_l_m3
    else:
        if x1 == 0 and population.n_u_m3 > 0:
            raise ArithmeticError('positive finite owner population endpoint underflowed')
        nu1 = line.N * x1
        nl1 = line.N - nu1
        if x1 > 0 and nu1 == 0:
            raise ArithmeticError('positive owner population endpoint unrepresentable')
    if x1 > 0:
        endpoint_residual = _match(nu1/line.N, x1, x1, 'owner population endpoint')
    else:
        endpoint_residual = _match(nu1, 0., 0., 'zero owner population endpoint')
    if D != 0 and (ledger['owner_map']['x1'] == line.x or
                   nu1 == population.n_u_m3 or nl1 == population.n_l_m3 or drho == 0):
        raise ArithmeticError('requested population or energy increment unrepresentable')
    new_state = copy.deepcopy(state)
    new_source = copy.deepcopy(source)
    # Preserve caller-owned constant atomic energy and the owner's remaining
    # excitation separately. Subtracting drho can erase a resolved remainder.
    rho_other = state.rho[atomic_sector] - excitation
    excitation1 = scale.density_factor * line.card.energy_J * nu1
    if nu1 > 0 and excitation1 == 0:
        raise ArithmeticError('positive endpoint excitation energy unrepresentable')
    if D != 0:
        atomic_rho1 = rho_other + excitation1
        if excitation1 > 0 and atomic_rho1 == rho_other:
            raise ArithmeticError('remaining endpoint sector excitation unrepresentable')
        new_state.rho[atomic_sector] = atomic_rho1
    new_state.rho[photon_sector] += drho
    if D != 0 and (new_state.rho[atomic_sector] == state.rho[atomic_sector] or
                   new_state.rho[photon_sector] == state.rho[photon_sector]):
        raise ArithmeticError('requested sector energy increment unrepresentable')
    if new_state.rho[atomic_sector] < 0:
        raise ArithmeticError('atomic donor energy negative')
    if D != 0:
        nhat, A = cubature14()
        q = 1 + np.einsum('ni,ij,nj->n', nhat, line.S, nhat)
        dn = D * A * q
        k = line.card.energy_J / (scale.c * Pstar) * nhat
        w = scale.density_factor * scale.c * Pstar * dn
        if np.any(dn <= 0) or np.any(w <= 0) or not np.all(np.isfinite(w)):
            raise ArithmeticError('positive emitted packet outside representable domain')
        new_photons = PhotonStock(identity, np.concatenate((photons.k, k)),
            np.concatenate((photons.w, w)), np.concatenate((photons.mass, np.zeros(14))),
            photons.applied | {key})
        emitted = kinetic.moments(k, w, np.zeros(14))
    else:
        new_photons = PhotonStock(identity, photons.k.copy(), photons.w.copy(),
                                  photons.mass.copy(), photons.applied | {key})
        emitted = (0., np.zeros(3), 0., np.zeros((3, 3)))
    predicted_pi = core.stf(core.five(drho * 2 * line.S / 15))
    packet_residuals = {}
    for name, actual, expected in zip(('rho', 'flux', 'p', 'pi'), emitted,
                                     (drho, np.zeros(3), drho/3, predicted_pi)):
        packet_residuals[name] = _match(actual, expected, abs(drho), 'emitted '+name)
    new_source.pressure = pressure.copy()
    new_source.pi = pi.copy()
    new_source.pressure[photon_sector] += drho / 3
    new_source.pi[photon_sector] = core.stf(core.five(pi[photon_sector] + predicted_pi))
    new_source.energy_transfer = np.zeros(ns)
    new_source.momentum_transfer = np.zeros((ns, 3))
    new_state.validate(); new_source.arrays(ns)
    rho1, flux1, p1, pi1 = photon_moments(new_photons)
    for name, actual, expected in (
            ('rho', new_state.rho[photon_sector], rho1),
            ('flux', new_state.flux[photon_sector], flux1),
            ('p', new_source.pressure[photon_sector], p1),
            ('pi', new_source.pi[photon_sector], pi1)):
        _match(actual, expected, abs(rho1), 'updated photon '+name)
    new_population = PopulationStock(identity, nu1, nl1, population.applied | {key})
    new_line = replace(line, n_u_m3=nu1, n_l_m3=nl1)
    population_scale = line.N
    energy_scale = math.fsum(abs(x) for x in state.rho) + abs(drho)
    before = core.constraints(state.pack())
    after = core.constraints(new_state.pack())
    constraint_scale = (3*state.h**2 + np.sum(state.sigma**2) + np.sum(state.n**2)
                        + 6*np.dot(state.a, state.a) + energy_scale)
    residuals = dict(
        atom_number_over_population=math.fsum((nu1, nl1, -line.N))/population_scale,
        upper_transfer_over_population=(population.n_u_m3-nu1-D)/population_scale,
        owner_endpoint_relative=endpoint_residual,
        total_energy_over_gross=(math.fsum(new_state.rho)-math.fsum(state.rho))/energy_scale if energy_scale else 0.,
        constraint_change_over_gross=float(np.max(np.abs(after-before)))/constraint_scale,
        photon_initial_consistency=consistency, emitted_packet=packet_residuals)
    if max(abs(residuals[k]) for k in ('atom_number_over_population',
           'upper_transfer_over_population', 'total_energy_over_gross', 'constraint_change_over_gross')) > ROUND_FACTOR:
        raise ArithmeticError('floating conservation residual exceeds gross-scale tolerance')
    return dict(state=new_state, source=new_source, population=new_population,
        photons=new_photons, line=new_line, ledger=ledger, residuals=residuals,
        constraints_before=before, constraints_after=after,
        tolerance=dict(relative=ROUND_FACTOR, photon_gross_scale=photon_scale,
                       population_gross_scale=population_scale, energy_gross_scale=energy_scale,
                       constraint_gross_scale=float(constraint_scale)),
        physical_transfer_key=key, pi_kind='STATE_STRESS_NOT_PIRATE',
        thermal_recoil_J_m3=0., ionization_yield=0., electron_yield=0.)
