"""Cold-electron test-field state and exact observer-frame adapter.

This module adds the *collision carrier* that was previously represented only
by the ambiguous constant ``Collision.v_b``.  It deliberately is not a matter
``Species``: a test field has no Einstein-source methods and therefore cannot
backreact on the Bianchi background by accident.

Conventions
-----------

* metric ``(-,+,+,+)``;
* all stored three-velocities are dimensionless ``beta = v_physical / c``;
* ``n_e_free`` is the non-negative **proper** free-electron density in m^-3;
* the electron distribution is cold (one bulk four-velocity);
* ``c`` is explicit at the physical API boundary and exact SI by default.

The general state is independent.  ``comoving(...)`` constructs the exact
restriction ``u_e = u_fluid`` by copying the fluid beta.  A frame transform
does not change one physical closure into the other: it only re-expresses the
same photon/coherency carrier in the fluid or electron observer frame.

For non-collinear velocities, fluid -> electron is the composition

    fluid -> normal  (boost by -beta_fluid)
    normal -> electron (boost by +beta_electron),

not a boost by ``beta_electron - beta_fluid``.  The existing exact Q-layer
photon aberration and canonical transported-screen maps are composed so their
Wigner/spatial rotation is retained rather than replaced by a new shortcut.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

import numpy as np

from bianchi.q.boost import doppler
from bianchi.q.polstate import boost_shape


# Exact by SI definition since 2019.
C_LIGHT_M_S = 299_792_458.0
_I4 = np.eye(4)


def _beta(value: Iterable[float], name: str = "beta") -> np.ndarray:
    out = np.asarray(value, dtype=float)
    if out.shape != (3,):
        raise ValueError(f"{name} must have shape (3,), got {out.shape}")
    if not np.isfinite(out).all():
        raise ValueError(f"{name} must be finite")
    beta2 = float(out @ out)
    if beta2 >= 1.0:
        raise ValueError(f"|{name}| must be < 1, got squared norm {beta2}")
    return out


def _positive_c(value: float) -> float:
    out = float(value)
    if not np.isfinite(out) or out <= 0.0:
        raise ValueError("c_m_s must be finite and positive")
    return out


def lorentz_factor(beta: Iterable[float]) -> float:
    """Return ``gamma=(1-|beta|^2)^(-1/2)`` after strict validation."""
    b = _beta(beta)
    return float(1.0 / np.sqrt(1.0 - float(b @ b)))


def normalized_four_velocity(beta: Iterable[float]) -> np.ndarray:
    """Return tetrad components ``U=(gamma, gamma*beta)``, ``U.U=-1``."""
    b = _beta(beta)
    gamma = 1.0 / np.sqrt(1.0 - float(b @ b))
    return np.concatenate(([gamma], gamma * b))


def four_velocity(beta: Iterable[float], *, c_m_s: float = C_LIGHT_M_S) -> np.ndarray:
    """Return physical tetrad components ``u=c U``, hence ``u.u=-c^2``."""
    return _positive_c(c_m_s) * normalized_four_velocity(beta)


def lorentz_boost(beta: Iterable[float]) -> np.ndarray:
    """Pure boost mapping source-frame components to a frame moving at beta.

    The sign matches :func:`bianchi.q.boost.doppler`: for a photon,
    ``p'^0 = gamma p^0 (1-beta.dot(n))``.
    """
    b = _beta(beta)
    beta2 = float(b @ b)
    if beta2 == 0.0:
        return _I4.copy()
    gamma = 1.0 / np.sqrt(1.0 - beta2)
    out = _I4.copy()
    out[0, 0] = gamma
    out[0, 1:] = -gamma * b
    out[1:, 0] = -gamma * b
    out[1:, 1:] += ((gamma - 1.0) / beta2) * np.outer(b, b)
    return out


def frame_matrix(beta_source: Iterable[float], beta_target: Iterable[float]) -> np.ndarray:
    """Exact component map from a source observer to a target observer.

    Both velocities are measured in the same normal tetrad.  The ordered
    product is essential for non-collinear velocities; it includes the spatial
    rotation absent from a naive velocity subtraction.
    """
    source = _beta(beta_source, "beta_source")
    target = _beta(beta_target, "beta_target")
    if np.array_equal(source, target):
        return _I4.copy()
    return lorentz_boost(target) @ lorentz_boost(-source)


def relative_gamma(beta_source: Iterable[float], beta_target: Iterable[float]) -> float:
    """Invariant ``Gamma_st=-U_source.U_target`` for ``(-,+,+,+)``."""
    source = _beta(beta_source, "beta_source")
    target = _beta(beta_target, "beta_target")
    if np.array_equal(source, target):
        return 1.0
    gs = 1.0 / np.sqrt(1.0 - float(source @ source))
    gt = 1.0 / np.sqrt(1.0 - float(target @ target))
    return float(gs * gt * (1.0 - float(source @ target)))


def _directions(value) -> tuple[np.ndarray, tuple[int, ...], bool]:
    out = np.asarray(value, dtype=float)
    single = out.ndim == 1
    if out.ndim < 1 or out.shape[-1] != 3:
        raise ValueError(f"direction must have final shape 3, got {out.shape}")
    if not np.isfinite(out).all():
        raise ValueError("direction must be finite")
    leading = out.shape[:-1]
    flat = out.reshape(-1, 3)
    norm = np.linalg.norm(flat, axis=1)
    if np.any(np.abs(norm - 1.0) > 2e-12):
        raise ValueError("photon directions must be unit vectors")
    return flat, leading, single


def _restore_direction(value: np.ndarray, leading: tuple[int, ...], single: bool):
    out = np.asarray(value, float).reshape(leading + (3,))
    return out if not single else out.reshape(3)


def transform_photon(energy, direction, beta_source, beta_target):
    """Transform photon energy/direction between two observer frames.

    Returns ``(energy_target, direction_target, doppler_total)``.  Photon
    momentum is understood as ``p=(E/c, E*n/c)``; the explicit factors of
    ``c`` cancel in the dimensionless Doppler/aberration map.
    """
    source = _beta(beta_source, "beta_source")
    target = _beta(beta_target, "beta_target")
    flat_direction, leading, single = _directions(direction)
    e = np.asarray(energy, dtype=float)
    try:
        e = np.broadcast_to(e, leading).copy()
    except ValueError as exc:
        raise ValueError("energy is not broadcastable to direction shape") from exc
    if not np.isfinite(e).all() or np.any(e <= 0.0):
        raise ValueError("photon energy must be finite and positive")
    if np.array_equal(source, target):
        d = np.ones(leading, dtype=float)
        return (float(e) if single and e.ndim == 0 else e,
                _restore_direction(flat_direction.copy(), leading, single),
                float(d) if single and d.ndim == 0 else d)

    # Existing exact pure-boost authorities; their ordered composition retains
    # the non-collinear spatial rotation.
    if np.any(source):
        d1, middle = doppler(flat_direction, -source)
    else:
        d1, middle = np.ones(len(flat_direction)), flat_direction.copy()
    if np.any(target):
        d2, transformed = doppler(middle, target)
    else:
        d2, transformed = np.ones(len(middle)), middle.copy()
    total = (np.asarray(d1) * np.asarray(d2)).reshape(leading)
    energy_target = e * total
    return (float(energy_target) if single and energy_target.ndim == 0 else energy_target,
            _restore_direction(transformed, leading, single),
            float(total) if single and total.ndim == 0 else total)


def transform_polarization_shape(shape, direction, beta_source, beta_target):
    """Transform the Q-layer normalized screen coherency shape.

    ``shape`` has final axes ``(3,3)``, unit trace, and is transverse to
    ``direction``.  The returned tuple is ``(shape_target, direction_target,
    doppler_total)``.  Intensity is deliberately separate: Mode A receives
    ``D^4`` through :func:`transform_mode_a`.
    """
    source = _beta(beta_source, "beta_source")
    target = _beta(beta_target, "beta_target")
    flat_direction, leading, single = _directions(direction)
    carrier = np.asarray(shape, dtype=float)
    expected = leading + (3, 3)
    if carrier.shape != expected:
        raise ValueError(f"polarization shape must have shape {expected}, got {carrier.shape}")
    if not np.isfinite(carrier).all():
        raise ValueError("polarization shape must be finite")
    flat_carrier = carrier.reshape(-1, 3, 3)
    trace = np.trace(flat_carrier, axis1=1, axis2=2)
    leak = np.einsum("aij,aj->ai", flat_carrier, flat_direction)
    if np.max(np.abs(trace - 1.0), initial=0.0) > 2e-11:
        raise ValueError("polarization shape must have unit trace")
    if np.max(np.abs(leak), initial=0.0) > 2e-11:
        raise ValueError("polarization shape must lie in the photon screen")
    if np.array_equal(source, target):
        d = np.ones(leading, dtype=float)
        out = flat_carrier.copy().reshape(expected)
        return (out if not single else out.reshape(3, 3),
                _restore_direction(flat_direction.copy(), leading, single),
                float(d) if single and d.ndim == 0 else d)

    if np.any(source):
        first, middle, d1 = boost_shape(flat_carrier, -source, flat_direction)
    else:
        first = flat_carrier.copy()
        middle = flat_direction.copy()
        d1 = np.ones(len(flat_direction))
    if np.any(target):
        second, transformed, d2 = boost_shape(first, target, middle)
    else:
        second = first.copy()
        transformed = middle.copy()
        d2 = np.ones(len(middle))
    total = (np.asarray(d1) * np.asarray(d2)).reshape(leading)
    out = np.asarray(second).reshape(expected)
    return (out if not single else out.reshape(3, 3),
            _restore_direction(transformed, leading, single),
            float(total) if single and total.ndim == 0 else total)


def transform_mode_a(log_weight, log_intensity, direction, beta_source, beta_target):
    """Transform exact Mode-A collision inputs between observer frames.

    For the Q carrier ``Ghat=int f p^3 dp``, Lorentz invariance gives
    ``Ghat_target=D^4 Ghat_source`` and ``dOmega_target=dOmega_source/D^2``.
    Returns ``(log_weight_target, log_intensity_target, direction_target, D)``.
    """
    flat_direction, leading, _ = _directions(direction)
    del flat_direction
    lw = np.asarray(log_weight, dtype=float)
    lg = np.asarray(log_intensity, dtype=float)
    try:
        lw = np.broadcast_to(lw, leading).copy()
        lg = np.broadcast_to(lg, leading).copy()
    except ValueError as exc:
        raise ValueError("Mode-A arrays are not broadcastable to direction shape") from exc
    if not np.isfinite(lw).all() or not np.isfinite(lg).all():
        raise ValueError("Mode-A log carriers must be finite")
    _, transformed, d = transform_photon(
        np.ones(leading, dtype=float), direction, beta_source, beta_target
    )
    log_d = np.log(d)
    return lw - 2.0 * log_d, lg + 4.0 * log_d, transformed, d


@dataclass(frozen=True, slots=True)
class ColdElectronTestField:
    """Prescribed cold-electron collision state with no background backreaction."""

    n_e_free: float
    beta_normal: tuple[float, float, float]
    c_m_s: float = C_LIGHT_M_S
    closure: str = field(init=False, default="independent")
    density_unit: str = field(init=False, default="m^-3")

    def __post_init__(self):
        density = float(self.n_e_free)
        if not np.isfinite(density) or density < 0.0:
            raise ValueError("n_e_free must be a finite non-negative proper density")
        beta = _beta(self.beta_normal, "beta_normal")
        object.__setattr__(self, "n_e_free", density)
        object.__setattr__(self, "beta_normal", tuple(float(x) for x in beta))
        object.__setattr__(self, "c_m_s", _positive_c(self.c_m_s))

    @classmethod
    def independent(cls, n_e_free, beta_normal, *, c_m_s=C_LIGHT_M_S):
        """Construct the encompassing independent-electron test-field model."""
        return cls(n_e_free, tuple(_beta(beta_normal, "beta_normal")), c_m_s)

    @classmethod
    def from_physical_velocity(cls, n_e_free, velocity_normal_m_s, *, c_m_s):
        """Construct from a dimensional velocity with an explicit ``c`` boundary."""
        c_value = _positive_c(c_m_s)
        velocity = np.asarray(velocity_normal_m_s, dtype=float)
        if velocity.shape != (3,) or not np.isfinite(velocity).all():
            raise ValueError("velocity_normal_m_s must be a finite shape-(3,) vector")
        return cls.independent(n_e_free, velocity / c_value, c_m_s=c_value)

    @classmethod
    def comoving(cls, n_e_free, beta_fluid, *, c_m_s=C_LIGHT_M_S):
        """Construct the exact ``u_e=u_fluid`` velocity restriction.

        Only the velocity is identified.  ``n_e_free`` remains a separate
        proper-density input; no ionization or composition map is invented.
        The caller must supply an actual fluid-frame representative.  At a
        vacuum stratum where the background quotients that representative out,
        this constructor does not silently manufacture one.
        """
        out = cls(n_e_free, tuple(_beta(beta_fluid, "beta_fluid")), c_m_s)
        object.__setattr__(out, "closure", "comoving-electron")
        return out

    @property
    def cold(self) -> bool:
        return True

    @property
    def test_field(self) -> bool:
        return True

    @property
    def physical_velocity_normal_m_s(self) -> np.ndarray:
        return self.c_m_s * np.asarray(self.beta_normal)

    def normalized_four_velocity(self) -> np.ndarray:
        return normalized_four_velocity(self.beta_normal)

    def four_velocity(self) -> np.ndarray:
        return four_velocity(self.beta_normal, c_m_s=self.c_m_s)

    def is_comoving_with(self, beta_fluid, *, atol=0.0) -> bool:
        fluid = _beta(beta_fluid, "beta_fluid")
        electron = np.asarray(self.beta_normal)
        if atol == 0.0:
            return bool(np.array_equal(electron, fluid))
        return bool(np.allclose(electron, fluid, rtol=0.0, atol=float(atol)))

    def _checked_fluid_beta(self, beta_fluid) -> np.ndarray:
        fluid = _beta(beta_fluid, "beta_fluid")
        if (self.closure == "comoving-electron"
                and not np.array_equal(np.asarray(self.beta_normal), fluid)):
            raise ValueError(
                "comoving-electron state requires beta_fluid == beta_normal exactly"
            )
        return fluid

    def relative_gamma(self, beta_fluid) -> float:
        fluid = self._checked_fluid_beta(beta_fluid)
        return relative_gamma(fluid, self.beta_normal)

    def fluid_to_electron_matrix(self, beta_fluid) -> np.ndarray:
        fluid = self._checked_fluid_beta(beta_fluid)
        return frame_matrix(fluid, self.beta_normal)

    def electron_to_fluid_matrix(self, beta_fluid) -> np.ndarray:
        fluid = self._checked_fluid_beta(beta_fluid)
        return frame_matrix(self.beta_normal, fluid)

    def fluid_to_electron_photon(self, energy, direction, beta_fluid):
        fluid = self._checked_fluid_beta(beta_fluid)
        return transform_photon(energy, direction, fluid, self.beta_normal)

    def electron_to_fluid_photon(self, energy, direction, beta_fluid):
        fluid = self._checked_fluid_beta(beta_fluid)
        return transform_photon(energy, direction, self.beta_normal, fluid)

    def fluid_to_electron_polarization(self, shape, direction, beta_fluid):
        fluid = self._checked_fluid_beta(beta_fluid)
        return transform_polarization_shape(
            shape, direction, fluid, self.beta_normal
        )

    def electron_to_fluid_polarization(self, shape, direction, beta_fluid):
        fluid = self._checked_fluid_beta(beta_fluid)
        return transform_polarization_shape(
            shape, direction, self.beta_normal, fluid
        )

    def fluid_to_electron_mode_a(self, log_weight, log_intensity, direction, beta_fluid):
        fluid = self._checked_fluid_beta(beta_fluid)
        return transform_mode_a(
            log_weight, log_intensity, direction, fluid, self.beta_normal
        )

    def electron_to_fluid_mode_a(self, log_weight, log_intensity, direction, beta_fluid):
        fluid = self._checked_fluid_beta(beta_fluid)
        return transform_mode_a(
            log_weight, log_intensity, direction, self.beta_normal, fluid
        )

    def authority_metadata(self) -> dict:
        """Machine-readable boundary: what this object does and does not own."""
        return {
            "model": "H2_WITH_COMOVING_RESTRICTION",
            "closure": self.closure,
            "cold_electrons": True,
            "test_field": True,
            "background_backreaction": False,
            "density_semantics": "proper_free_electron_density",
            "density_owner": "explicit_input",
            "density_unit": self.density_unit,
            "stored_velocity": "dimensionless_beta_in_normal_tetrad",
            "physical_velocity_boundary": "v_physical=c*beta",
            "time_dependence": "instantaneous_or_external_prescribed_schedule",
            "provenance_required_if_time_dependent": True,
            "vacuum_velocity_quotient": "not_fixed_by_this_adapter",
            "canonical_receipt_complete": False,
            "authority_row_promoted": False,
        }


# Concise public name while retaining the physically explicit class name.
ElectronTestField = ColdElectronTestField


__all__ = [
    "C_LIGHT_M_S",
    "ColdElectronTestField",
    "ElectronTestField",
    "four_velocity",
    "frame_matrix",
    "lorentz_boost",
    "lorentz_factor",
    "normalized_four_velocity",
    "relative_gamma",
    "transform_mode_a",
    "transform_photon",
    "transform_polarization_shape",
]
