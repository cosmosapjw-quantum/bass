"""Instantaneous cold-Thomson energy and collision-consumer authority.

This bounded module answers two deliberately narrow questions:

1. Does a provenance-bound, hard photon-energy support satisfy a caller-owned
   total Klein--Nishina rate budget for an exactly cold delta-electron state?
2. Does a named collision consumer receive rest opacity or an observer-ray
   rate, with the relative-flux factor applied exactly once?

It does not certify a polarized differential kernel, a finite-temperature
Maxwell--Juttner tail, a trajectory-wide energy bound, or any production Q/Rust
collision exponential.  Metric convention is ``(-,+,+,+)``; energies are SI
joules, temperatures kelvin, and velocities are dimensionless ``v/c``.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, localcontext
import enum
import hashlib
import re

import numpy as np

from bianchi.physical.units import (
    BOLTZMANN_CONSTANT_J_K,
    C_LIGHT_M_S,
    ELECTRON_REST_ENERGY_J,
)
from bianchi.q.electron import ColdElectronTestField
from bianchi.q.electron_rate import ElectronCollisionContext


_SHA256 = re.compile(r"[0-9a-f]{64}")
_SERIES_COEFFICIENTS = (
    1.0,
    -2.0,
    26.0 / 5.0,
    -133.0 / 10.0,
    1144.0 / 35.0,
    -544.0 / 7.0,
    3784.0 / 21.0,
    -6148.0 / 15.0,
    151552.0 / 165.0,
    -111872.0 / 55.0,
    637952.0 / 143.0,
)
_DEFICIT_SERIES_COEFFICIENTS = tuple(
    0.0 if index == 0 else -coefficient
    for index, coefficient in enumerate(_SERIES_COEFFICIENTS)
)
_KN_SERIES_MAX_X = 1.0e-3
_AUTHORITY_DECIMAL_PRECISION = 80


class EnergyBoundKind(enum.Enum):
    HARD_FINITE = "hard_finite"
    BOLOMETRIC = "bolometric"
    UNKNOWN = "unknown"
    EFFECTIVE_TAIL = "effective_tail"


class ColdThomsonStatus(enum.Enum):
    CERTIFIED_COLD_DELTA = "certified_cold_delta_for_requested_budget"
    VACUOUS_COLLISION_OFF = "vacuous_collision_off"
    UNVERIFIED_ENERGY_SUPPORT = "unverified_energy_support"
    UNVERIFIED_FINITE_TEMPERATURE_TAIL = "unverified_finite_temperature_tail"
    UNVERIFIED_NUMERIC_DOMAIN = "unverified_numeric_domain"
    REJECTED_TOTAL_CROSS_SECTION_BUDGET = "rejected_total_cross_section_budget"
    REJECTED_TEMPERATURE_POLICY = "rejected_temperature_policy"


class CollisionConsumerKind(enum.Enum):
    APPLIES_RELATIVE_FLUX = "applies_relative_flux_internally"
    EXPECTS_OBSERVER_RAY_RATE = "expects_observer_ray_rate"
    SCALAR_Q_KERNEL_UNRESOLVED = "scalar_q_kernel_generator_unresolved"


class CollisionConsumerId(enum.Enum):
    MATTER_COLLISION_MOVING = "bianchi.matter.collision_moving.collision_rate_density"
    EXTERNAL_OBSERVER_RAY = "external.single_observer_ray"
    Q_SCALAR_KERNEL = "bianchi.q.scalar_collision_kernel"


class UnresolvedCollisionConsumerError(RuntimeError):
    """Raised when a scalar consumer has no derived direction-dependent generator."""


def _nonempty(value, name: str) -> str:
    out = str(value).strip()
    if not out:
        raise ValueError(f"{name} must be non-empty")
    if "\0" in out:
        raise ValueError(f"{name} must not contain NUL")
    return out


def _finite_nonnegative_scalar(value, name: str) -> float:
    out = float(value)
    if not np.isfinite(out) or out < 0.0:
        raise ValueError(f"{name} must be finite and non-negative")
    return 0.0 if out == 0.0 else out


@dataclass(frozen=True, slots=True)
class AuthorityProvenance:
    source_id: str
    source_sha256: str

    def __post_init__(self):
        object.__setattr__(self, "source_id", _nonempty(self.source_id, "source_id"))
        digest = str(self.source_sha256)
        if _SHA256.fullmatch(digest) is None:
            raise ValueError("source_sha256 must be lowercase 64-hex")
        object.__setattr__(self, "source_sha256", digest)


def _require_provenance(value) -> AuthorityProvenance:
    if not isinstance(value, AuthorityProvenance):
        raise TypeError("provenance must be an AuthorityProvenance")
    return value


def _payload_token(item) -> bytes:
    if item is None:
        return b"none"
    if isinstance(item, enum.Enum):
        return ("enum:" + str(item.value)).encode("utf-8")
    if isinstance(item, (float, np.floating)):
        value = float(item)
        if value == 0.0:
            value = 0.0
        return ("float:" + value.hex()).encode("ascii")
    if isinstance(item, bool):
        return b"bool:1" if item else b"bool:0"
    return ("text:" + str(item)).encode("utf-8")


def _payload_hash(schema: str, parts) -> str:
    digest = hashlib.sha256()
    header = schema.encode("ascii")
    digest.update(len(header).to_bytes(8, "big") + header)
    for item in parts:
        token = _payload_token(item)
        digest.update(len(token).to_bytes(8, "big") + token)
    return digest.hexdigest()


@dataclass(frozen=True, slots=True)
class PhotonEnergyBound:
    """Instantaneous photon-energy support in one explicitly named frame."""

    kind: EnergyBoundKind
    max_energy_j: float | None
    source_frame: str
    event_id: str
    provenance: AuthorityProvenance
    tail_metric: str | None = None
    tail_error_bound: float | None = None

    def __post_init__(self):
        if not isinstance(self.kind, EnergyBoundKind):
            raise TypeError("kind must be an EnergyBoundKind")
        object.__setattr__(self, "source_frame", _nonempty(self.source_frame, "source_frame"))
        object.__setattr__(self, "event_id", _nonempty(self.event_id, "event_id"))
        _require_provenance(self.provenance)

        if self.kind in {EnergyBoundKind.HARD_FINITE, EnergyBoundKind.EFFECTIVE_TAIL}:
            energy = _finite_nonnegative_scalar(self.max_energy_j, "max_energy_j")
            object.__setattr__(self, "max_energy_j", energy)
        elif self.max_energy_j is not None:
            raise ValueError("bolometric/unknown support cannot carry a finite maximum")

        if self.kind is EnergyBoundKind.EFFECTIVE_TAIL:
            object.__setattr__(self, "tail_metric", _nonempty(self.tail_metric, "tail_metric"))
            tail = _finite_nonnegative_scalar(self.tail_error_bound, "tail_error_bound")
            if tail >= 1.0:
                raise ValueError("tail_error_bound must be < 1")
            object.__setattr__(self, "tail_error_bound", tail)
        elif self.tail_metric is not None or self.tail_error_bound is not None:
            raise ValueError("tail metadata is only valid for EFFECTIVE_TAIL")

    @classmethod
    def hard_finite_j(cls, max_energy_j, *, source_frame, event_id, provenance):
        return cls(
            EnergyBoundKind.HARD_FINITE, max_energy_j, source_frame, event_id,
            provenance
        )

    @classmethod
    def bolometric(cls, *, source_frame, event_id, provenance):
        return cls(
            EnergyBoundKind.BOLOMETRIC, None, source_frame, event_id, provenance
        )

    @classmethod
    def unknown(cls, *, source_frame, event_id, provenance):
        return cls(
            EnergyBoundKind.UNKNOWN, None, source_frame, event_id, provenance
        )

    @classmethod
    def effective_tail_j(
        cls,
        max_energy_j,
        *,
        source_frame,
        event_id,
        tail_metric,
        tail_error_bound,
        provenance,
    ):
        return cls(
            EnergyBoundKind.EFFECTIVE_TAIL,
            max_energy_j,
            source_frame,
            event_id,
            provenance,
            tail_metric,
            tail_error_bound,
        )

    @property
    def payload_sha256(self) -> str:
        return _payload_hash(
            "bass.photon_energy_bound/v1",
            (
                self.kind.value,
                self.max_energy_j,
                self.source_frame,
                self.event_id,
                self.tail_metric,
                self.tail_error_bound,
                self.provenance.source_id,
                self.provenance.source_sha256,
            ),
        )


@dataclass(frozen=True, slots=True)
class ColdThomsonBudget:
    """Caller-owned diagnostic budget; not a global project acceptance ceiling."""

    max_total_cross_section_relative_error: float
    max_theta_e: float
    provenance: AuthorityProvenance

    def __post_init__(self):
        total_cross_section_relative_error = _finite_nonnegative_scalar(
            self.max_total_cross_section_relative_error,
            "max_total_cross_section_relative_error",
        )
        if total_cross_section_relative_error >= 1.0:
            raise ValueError("max_total_cross_section_relative_error must be < 1")
        theta = _finite_nonnegative_scalar(self.max_theta_e, "max_theta_e")
        _require_provenance(self.provenance)
        object.__setattr__(
            self,
            "max_total_cross_section_relative_error",
            total_cross_section_relative_error,
        )
        object.__setattr__(self, "max_theta_e", theta)

    @property
    def payload_sha256(self) -> str:
        return _payload_hash(
            "bass.cold_thomson_budget/v1",
            (
                self.max_total_cross_section_relative_error,
                self.max_theta_e,
                "relative_error_denominator=sigma_T",
                "norm=stationary_electron_total_cross_section",
                self.provenance.source_id,
                self.provenance.source_sha256,
            ),
        )


@dataclass(frozen=True, slots=True)
class ElectronTemperatureAuthority:
    temperature_k: float
    event_id: str
    provenance: AuthorityProvenance

    def __post_init__(self):
        object.__setattr__(
            self,
            "temperature_k",
            _finite_nonnegative_scalar(self.temperature_k, "temperature_k"),
        )
        object.__setattr__(self, "event_id", _nonempty(self.event_id, "event_id"))
        _require_provenance(self.provenance)

    @property
    def payload_sha256(self) -> str:
        return _payload_hash(
            "bass.electron_temperature_authority/v1",
            (
                self.temperature_k,
                "unit=K",
                self.event_id,
                self.provenance.source_id,
                self.provenance.source_sha256,
            ),
        )


@dataclass(frozen=True, slots=True)
class ElectronStateAuthority:
    electron: ColdElectronTestField
    event_id: str
    provenance: AuthorityProvenance

    def __post_init__(self):
        if not isinstance(self.electron, ColdElectronTestField):
            raise TypeError("electron must be a ColdElectronTestField")
        if self.electron.c_m_s != C_LIGHT_M_S:
            raise ValueError("SI validity authority requires exact SI c")
        object.__setattr__(self, "event_id", _nonempty(self.event_id, "event_id"))
        _require_provenance(self.provenance)

    @property
    def payload_sha256(self) -> str:
        return _payload_hash(
            "bass.electron_state_authority/v1",
            (
                self.electron.n_e_free,
                *self.electron.beta_normal,
                self.electron.closure,
                self.electron.c_m_s,
                self.event_id,
                self.provenance.source_id,
                self.provenance.source_sha256,
            ),
        )


@dataclass(frozen=True, slots=True)
class DopplerBounds:
    minimum: float
    maximum: float
    relative_gamma: float


def _beta_binary64(value, name: str) -> tuple[np.ndarray, tuple[Decimal, ...]]:
    out = np.asarray(value, dtype=float)
    if out.shape != (3,):
        raise ValueError(f"{name} must have shape (3,), got {out.shape}")
    if not np.isfinite(out).all():
        raise ValueError(f"{name} must be finite")
    exact = tuple(Decimal.from_float(float(component)) for component in out)
    with localcontext() as context:
        context.prec = _AUTHORITY_DECIMAL_PRECISION
        norm2 = sum((component * component for component in exact), Decimal(0))
    if norm2 >= Decimal(1):
        raise ValueError(f"|{name}| must be < 1")
    return out, exact


@dataclass(frozen=True, slots=True)
class ObserverFrameAuthority:
    beta_normal: tuple[float, float, float]
    frame_id: str
    event_id: str
    provenance: AuthorityProvenance

    def __post_init__(self):
        values, _ = _beta_binary64(self.beta_normal, "beta_normal")
        canonical = tuple(0.0 if float(value) == 0.0 else float(value) for value in values)
        object.__setattr__(self, "beta_normal", canonical)
        object.__setattr__(self, "frame_id", _nonempty(self.frame_id, "frame_id"))
        object.__setattr__(self, "event_id", _nonempty(self.event_id, "event_id"))
        _require_provenance(self.provenance)

    @property
    def payload_sha256(self) -> str:
        return _payload_hash(
            "bass.observer_frame_authority/v1",
            (
                *self.beta_normal,
                self.frame_id,
                self.event_id,
                "binary64_exact_decimal80_relative_gamma",
                self.provenance.source_id,
                self.provenance.source_sha256,
            ),
        )


def all_sky_doppler_bounds(beta_source, beta_electron) -> DopplerBounds:
    """Exact unit-sphere extrema of ``E_e/E_source`` for two observers.

    Each supplied binary64 velocity component is promoted exactly with
    :meth:`Decimal.from_float`, then the invariant is evaluated at 80 decimal
    digits.  This prevents a nearly comoving ultrarelativistic pair from
    rounding ``Gamma`` below one.  ``D_min=1/D_max`` avoids the cancellation in
    ``Gamma-sqrt(Gamma^2-1)``.
    """
    source_float, source = _beta_binary64(beta_source, "beta_source")
    electron_float, electron = _beta_binary64(beta_electron, "beta_electron")
    if np.array_equal(source_float, electron_float):
        return DopplerBounds(1.0, 1.0, 1.0)
    with localcontext() as context:
        context.prec = _AUTHORITY_DECIMAL_PRECISION
        one = Decimal(1)
        source_norm = sum((value * value for value in source), Decimal(0))
        electron_norm = sum((value * value for value in electron), Decimal(0))
        scalar_product = sum(
            (left * right for left, right in zip(source, electron)), Decimal(0)
        )
        numerator = one - scalar_product
        denominator = ((one - source_norm) * (one - electron_norm)).sqrt()
        gamma = numerator / denominator
        if gamma < one:
            raise ArithmeticError("80-digit relative gamma fell below one")
        radical = ((gamma - one) * (gamma + one)).sqrt()
        maximum = gamma + radical
        minimum = one / maximum
    return DopplerBounds(float(minimum), float(maximum), float(gamma))


def _unit_direction_decimal(value) -> tuple[Decimal, Decimal, Decimal]:
    out = np.asarray(value, dtype=float)
    if out.shape != (3,):
        raise ValueError(f"direction_source must have shape (3,), got {out.shape}")
    if not np.isfinite(out).all():
        raise ValueError("direction_source must be finite")
    exact = tuple(Decimal.from_float(float(component)) for component in out)
    with localcontext() as context:
        context.prec = _AUTHORITY_DECIMAL_PRECISION
        norm = sum((component * component for component in exact), Decimal(0)).sqrt()
        if norm == 0 or abs(norm - Decimal(1)) > Decimal("2e-12"):
            raise ValueError("direction_source must be unit within 2e-12")
        return tuple(component / norm for component in exact)


def _decimal_boost_matrix(beta):
    one = Decimal(1)
    zero = Decimal(0)
    norm2 = sum((component * component for component in beta), zero)
    if norm2 == zero:
        return tuple(
            tuple(one if row == column else zero for column in range(4))
            for row in range(4)
        )
    gamma = one / (one - norm2).sqrt()
    matrix = [[zero for _ in range(4)] for _ in range(4)]
    matrix[0][0] = gamma
    for index in range(3):
        matrix[0][index + 1] = -gamma * beta[index]
        matrix[index + 1][0] = -gamma * beta[index]
    for row in range(3):
        for column in range(3):
            matrix[row + 1][column + 1] = (
                (one if row == column else zero)
                + (gamma - one) * beta[row] * beta[column] / norm2
            )
    return tuple(tuple(row) for row in matrix)


def exact_observer_doppler_factor(direction_source, beta_source, beta_electron) -> float:
    """Return one-ray ``E_e/E_source`` with controlled Decimal arithmetic.

    Directions accepted within the public ``2e-12`` norm tolerance are first
    canonically normalized, so every accepted ray remains inside the analytic
    all-sky envelope.
    """
    _, source = _beta_binary64(beta_source, "beta_source")
    _, electron = _beta_binary64(beta_electron, "beta_electron")
    direction = _unit_direction_decimal(direction_source)
    with localcontext() as context:
        context.prec = _AUTHORITY_DECIMAL_PRECISION
        target_boost = _decimal_boost_matrix(electron)
        source_inverse = _decimal_boost_matrix(tuple(-value for value in source))
        time_row = tuple(
            sum(
                (target_boost[0][middle] * source_inverse[middle][column]
                 for middle in range(4)),
                Decimal(0),
            )
            for column in range(4)
        )
        factor = time_row[0] + sum(
            (time_row[index + 1] * direction[index] for index in range(3)),
            Decimal(0),
        )
        if factor <= 0:
            raise ArithmeticError("future photon Doppler factor is not positive")
        return float(factor)


def klein_nishina_total_ratio(x):
    """Return stationary-electron ``sigma_KN(x)/sigma_T`` for ``x>=0``.

    A Wolfram-derived rational series through ``x^10`` removes catastrophic
    cancellation near zero.  The complementary expression is evaluated from
    the exact supplied binary64 value with the stdlib Decimal engine at the
    same fixed precision as the Doppler authority, then rounded once to
    binary64.  This does not depend on platform-specific ``longdouble`` width.
    """
    values = np.asarray(x, dtype=float)
    scalar = values.ndim == 0
    if not np.isfinite(values).all() or np.any(values < 0.0):
        raise ValueError("x must be finite and non-negative")
    out = np.empty_like(values)
    small = values <= _KN_SERIES_MAX_X
    if np.any(small):
        xs = values[small]
        result = np.full_like(xs, _SERIES_COEFFICIENTS[-1])
        for coefficient in reversed(_SERIES_COEFFICIENTS[:-1]):
            result = result * xs + coefficient
        out[small] = result
    if np.any(~small):
        large_values = np.ravel(values[~small])
        rounded = []
        with localcontext() as context:
            context.prec = _AUTHORITY_DECIMAL_PRECISION
            one = Decimal(1)
            two = Decimal(2)
            three = Decimal(3)
            prefactor = three / Decimal(4)
            for value in large_values:
                xd = Decimal.from_float(float(value))
                logarithm = (one + two * xd).ln()
                ratio = prefactor * (
                    (one + xd) / xd**3
                    * (two * xd * (one + xd) / (one + two * xd) - logarithm)
                    + logarithm / (two * xd)
                    - (one + three * xd) / (one + two * xd) ** 2
                )
                rounded.append(float(ratio))
        out[~small] = np.asarray(rounded, dtype=float).reshape(out[~small].shape)
    return float(out) if scalar else out


def klein_nishina_total_deficit(x):
    """Return ``(sigma_T-sigma_KN)/sigma_T`` without subtractive loss.

    In particular, nonzero ``x`` below binary64 epsilon still produces a
    positive deficit, so a zero total-cross-section budget passes only at
    exact ``x=0``.
    """
    values = np.asarray(x, dtype=float)
    scalar = values.ndim == 0
    if not np.isfinite(values).all() or np.any(values < 0.0):
        raise ValueError("x must be finite and non-negative")
    out = np.empty_like(values)
    small = values <= _KN_SERIES_MAX_X
    if np.any(small):
        xs = values[small]
        result = np.full_like(xs, _DEFICIT_SERIES_COEFFICIENTS[-1])
        for coefficient in reversed(_DEFICIT_SERIES_COEFFICIENTS[:-1]):
            result = result * xs + coefficient
        out[small] = result
    if np.any(~small):
        large_values = np.ravel(values[~small])
        rounded = []
        with localcontext() as context:
            context.prec = _AUTHORITY_DECIMAL_PRECISION
            one = Decimal(1)
            two = Decimal(2)
            three = Decimal(3)
            prefactor = three / Decimal(4)
            for value in large_values:
                xd = Decimal.from_float(float(value))
                logarithm = (one + two * xd).ln()
                ratio = prefactor * (
                    (one + xd) / xd**3
                    * (two * xd * (one + xd) / (one + two * xd) - logarithm)
                    + logarithm / (two * xd)
                    - (one + three * xd) / (one + two * xd) ** 2
                )
                rounded.append(float(one - ratio))
        out[~small] = np.asarray(rounded, dtype=float).reshape(out[~small].shape)
    return float(out) if scalar else out


@dataclass(frozen=True, slots=True)
class ColdThomsonCertificate:
    status: ColdThomsonStatus
    certified: bool
    valid_for_requested_budget: bool
    declared_scalar_predicates_pass: bool
    total_cross_section_pass: bool | None
    temperature_policy_pass: bool | None
    doppler_min: float | None
    doppler_max: float | None
    source_energy_max_j: float | None
    electron_energy_max_j: float | None
    x_max: float | None
    theta_e: float | None
    klein_nishina_ratio: float | None
    total_cross_section_relative_deficit: float | None
    reasons: tuple[str, ...]
    electron_state: ElectronStateAuthority
    energy_bound: PhotonEnergyBound
    budget: ColdThomsonBudget
    temperature_authority: ElectronTemperatureAuthority
    source_frame: ObserverFrameAuthority

    @property
    def payload_sha256(self) -> str:
        return _payload_hash(
            "bass.cold_thomson_certificate_payload/v1",
            (
                self.status,
                self.certified,
                self.valid_for_requested_budget,
                self.declared_scalar_predicates_pass,
                self.total_cross_section_pass,
                self.temperature_policy_pass,
                self.doppler_min,
                self.doppler_max,
                self.source_energy_max_j,
                self.electron_energy_max_j,
                self.x_max,
                self.theta_e,
                self.klein_nishina_ratio,
                self.total_cross_section_relative_deficit,
                *self.reasons,
                self.electron_state.payload_sha256,
                self.energy_bound.payload_sha256,
                self.budget.payload_sha256,
                self.temperature_authority.payload_sha256,
                self.source_frame.payload_sha256,
                "constants=CODATA2022_SI",
                BOLTZMANN_CONSTANT_J_K,
                ELECTRON_REST_ENERGY_J,
                C_LIGHT_M_S,
                "doppler=binary64_exact_decimal80",
                "kn=binary64_exact_series_x10_then_decimal80",
                _KN_SERIES_MAX_X,
            ),
        )

    def authority_metadata(self) -> dict:
        return {
            "schema": "bass.cold_thomson_certificate/v1",
            "status": self.status.value,
            "certified_for_requested_budget": self.certified,
            "valid_for_requested_budget": self.valid_for_requested_budget,
            "declared_scalar_predicates_pass": self.declared_scalar_predicates_pass,
            "claim_scope": "stationary_electron_total_cross_section_only",
            "relative_error": "(sigma_T-sigma_KN)/sigma_T",
            "temperature_policy": "theta_e=k_B*T_e/(m_e*c^2)",
            "finite_temperature_tail_certified": False,
            "polarized_differential_kernel_certified": False,
            "source_frame": self.energy_bound.source_frame,
            "event_id": self.energy_bound.event_id,
            "temporal_scope": "instantaneous_same_event_only",
            "angular_scope": "full_unit_sphere_conservative_for_restricted_support",
            "electron_state_sha256": self.electron_state.payload_sha256,
            "energy_bound_sha256": self.energy_bound.payload_sha256,
            "budget_sha256": self.budget.payload_sha256,
            "temperature_authority_sha256": self.temperature_authority.payload_sha256,
            "source_frame_sha256": self.source_frame.payload_sha256,
            "certificate_payload_sha256": self.payload_sha256,
            "constants_profile": "CODATA2022_SI",
            "doppler_numeric_semantics": "binary64_exact_decimal80",
            "project_acceptance_ceiling_frozen": False,
            "production_runtime_wired": False,
            "authority_row_promoted": False,
        }


def _certificate(
    *, status, certified, declared_pass, cross_section_pass, temperature_pass, bounds,
    source_energy, electron_energy, x_max, theta, ratio, deficit, reasons,
    electron_state, energy_bound, budget, temperature_authority, source_frame
):
    return ColdThomsonCertificate(
        status=status,
        certified=certified,
        # Fail-closed generic gate: finite-temperature diagnostic predicates
        # may pass without making this flag true.
        valid_for_requested_budget=certified,
        declared_scalar_predicates_pass=declared_pass,
        total_cross_section_pass=cross_section_pass,
        temperature_policy_pass=temperature_pass,
        doppler_min=None if bounds is None else bounds.minimum,
        doppler_max=None if bounds is None else bounds.maximum,
        source_energy_max_j=source_energy,
        electron_energy_max_j=electron_energy,
        x_max=x_max,
        theta_e=theta,
        klein_nishina_ratio=ratio,
        total_cross_section_relative_deficit=deficit,
        reasons=tuple(reasons),
        electron_state=electron_state,
        energy_bound=energy_bound,
        budget=budget,
        temperature_authority=temperature_authority,
        source_frame=source_frame,
    )


def certify_cold_thomson(
    electron_state,
    energy_bound,
    budget,
    temperature_authority,
    source_frame,
) -> ColdThomsonCertificate:
    """Evaluate one instantaneous, provenance-bound cold-Thomson request."""
    if not isinstance(electron_state, ElectronStateAuthority):
        raise TypeError("electron_state must be an ElectronStateAuthority")
    if not isinstance(energy_bound, PhotonEnergyBound):
        raise TypeError("energy_bound must be a PhotonEnergyBound")
    if not isinstance(budget, ColdThomsonBudget):
        raise TypeError("budget must be a ColdThomsonBudget")
    if not isinstance(temperature_authority, ElectronTemperatureAuthority):
        raise TypeError(
            "temperature_authority must be an ElectronTemperatureAuthority"
        )
    if not isinstance(source_frame, ObserverFrameAuthority):
        raise TypeError("source_frame must be an ObserverFrameAuthority")
    events = {
        electron_state.event_id,
        energy_bound.event_id,
        temperature_authority.event_id,
        source_frame.event_id,
    }
    if len(events) != 1:
        raise ValueError("electron, energy, temperature, and frame event_id must match")
    if energy_bound.source_frame != source_frame.frame_id:
        raise ValueError("energy-bound source_frame must match observer frame_id")
    electron = electron_state.electron

    # Vacuum quotients the electron velocity and temperature.  It is a
    # collision-off result, never a positive Thomson-domain certification.
    if electron.n_e_free == 0.0:
        return _certificate(
            status=ColdThomsonStatus.VACUOUS_COLLISION_OFF,
            certified=False,
            declared_pass=False,
            cross_section_pass=None,
            temperature_pass=None,
            bounds=None,
            source_energy=None,
            electron_energy=None,
            x_max=None,
            theta=None,
            ratio=None,
            deficit=None,
            reasons=("zero_electron_proper_density",),
            electron_state=electron_state,
            energy_bound=energy_bound,
            budget=budget,
            temperature_authority=temperature_authority,
            source_frame=source_frame,
        )

    temperature = temperature_authority.temperature_k
    theta = temperature * BOLTZMANN_CONSTANT_J_K / ELECTRON_REST_ENERGY_J
    temperature_pass = theta <= budget.max_theta_e
    bounds = all_sky_doppler_bounds(source_frame.beta_normal, electron.beta_normal)

    if energy_bound.kind is not EnergyBoundKind.HARD_FINITE:
        return _certificate(
            status=ColdThomsonStatus.UNVERIFIED_ENERGY_SUPPORT,
            certified=False,
            declared_pass=False,
            cross_section_pass=None,
            temperature_pass=temperature_pass,
            bounds=bounds,
            source_energy=None,
            electron_energy=None,
            x_max=None,
            theta=theta,
            ratio=None,
            deficit=None,
            reasons=(f"{energy_bound.kind.value}_is_not_a_hard_support",),
            electron_state=electron_state,
            energy_bound=energy_bound,
            budget=budget,
            temperature_authority=temperature_authority,
            source_frame=source_frame,
        )

    source_energy = energy_bound.max_energy_j
    with np.errstate(over="ignore", under="ignore", invalid="ignore"):
        electron_energy = source_energy * bounds.maximum
        x_max = electron_energy / ELECTRON_REST_ENERGY_J
    if (source_energy > 0.0 and x_max == 0.0) or not np.isfinite(x_max):
        reason = (
            "positive_energy_ratio_underflow"
            if x_max == 0.0
            else "boosted_energy_ratio_overflow"
        )
        return _certificate(
            status=ColdThomsonStatus.UNVERIFIED_NUMERIC_DOMAIN,
            certified=False,
            declared_pass=False,
            cross_section_pass=None,
            temperature_pass=temperature_pass,
            bounds=bounds,
            source_energy=source_energy,
            electron_energy=(electron_energy if np.isfinite(electron_energy) else None),
            x_max=None,
            theta=theta,
            ratio=None,
            deficit=None,
            reasons=(reason,),
            electron_state=electron_state,
            energy_bound=energy_bound,
            budget=budget,
            temperature_authority=temperature_authority,
            source_frame=source_frame,
        )
    ratio = klein_nishina_total_ratio(x_max)
    deficit = klein_nishina_total_deficit(x_max)
    cross_section_pass = (
        deficit <= budget.max_total_cross_section_relative_error
    )
    declared_pass = cross_section_pass and temperature_pass

    if not cross_section_pass:
        status = ColdThomsonStatus.REJECTED_TOTAL_CROSS_SECTION_BUDGET
        reasons = ("total_cross_section_budget_exceeded",)
    elif not temperature_pass:
        status = ColdThomsonStatus.REJECTED_TEMPERATURE_POLICY
        reasons = ("declared_theta_e_policy_exceeded",)
    elif temperature > 0.0:
        status = ColdThomsonStatus.UNVERIFIED_FINITE_TEMPERATURE_TAIL
        reasons = ("finite_temperature_distribution_tail_not_bounded",)
    else:
        status = ColdThomsonStatus.CERTIFIED_COLD_DELTA
        reasons = ("hard_energy_support_within_requested_total_rate_budget",)

    certified = status is ColdThomsonStatus.CERTIFIED_COLD_DELTA
    return _certificate(
        status=status,
        certified=certified,
        declared_pass=declared_pass,
        cross_section_pass=cross_section_pass,
        temperature_pass=temperature_pass,
        bounds=bounds,
        source_energy=source_energy,
        electron_energy=electron_energy,
        x_max=x_max,
        theta=theta,
        ratio=ratio,
        deficit=deficit,
        reasons=reasons,
        electron_state=electron_state,
        energy_bound=energy_bound,
        budget=budget,
        temperature_authority=temperature_authority,
        source_frame=source_frame,
    )


@dataclass(frozen=True, slots=True)
class RestOpacityPerSecond:
    value_per_s: float

    def __post_init__(self):
        object.__setattr__(
            self,
            "value_per_s",
            _finite_nonnegative_scalar(self.value_per_s, "rest opacity per second"),
        )


@dataclass(frozen=True, slots=True)
class ObserverRayRatePerSecond:
    value_per_s: float
    relative_flux_factor: float | None

    def __post_init__(self):
        object.__setattr__(
            self,
            "value_per_s",
            _finite_nonnegative_scalar(self.value_per_s, "observer rate per second"),
        )
        if self.relative_flux_factor is not None:
            factor = float(self.relative_flux_factor)
            if not np.isfinite(factor) or factor <= 0.0:
                raise ValueError("relative_flux_factor must be finite and positive")
            object.__setattr__(self, "relative_flux_factor", factor)


@dataclass(frozen=True, slots=True)
class ElectronCollisionConsumerContract:
    context: ElectronCollisionContext

    def __post_init__(self):
        if not isinstance(self.context, ElectronCollisionContext):
            raise TypeError("context must be an ElectronCollisionContext")
        if self.context.electron.c_m_s != C_LIGHT_M_S:
            raise ValueError("PerSecond consumer contract requires exact SI c")

    @staticmethod
    def consumer_kind(consumer) -> CollisionConsumerKind:
        if not isinstance(consumer, CollisionConsumerId):
            raise TypeError("consumer must be a CollisionConsumerId")
        if consumer is CollisionConsumerId.MATTER_COLLISION_MOVING:
            return CollisionConsumerKind.APPLIES_RELATIVE_FLUX
        if consumer is CollisionConsumerId.EXTERNAL_OBSERVER_RAY:
            return CollisionConsumerKind.EXPECTS_OBSERVER_RAY_RATE
        return CollisionConsumerKind.SCALAR_Q_KERNEL_UNRESOLVED

    def validate_input(self, consumer, value):
        kind = self.consumer_kind(consumer)
        if kind is CollisionConsumerKind.SCALAR_Q_KERNEL_UNRESOLVED:
            raise UnresolvedCollisionConsumerError(
                "the direction-dependent source-time generator does not reduce "
                "to the unresolved scalar Q collision-rate input"
            )
        expected = (
            RestOpacityPerSecond
            if kind is CollisionConsumerKind.APPLIES_RELATIVE_FLUX
            else ObserverRayRatePerSecond
        )
        if not isinstance(value, expected):
            raise TypeError(
                f"{consumer.value} requires {expected.__name__}, got {type(value).__name__}"
            )
        return value

    def input_for(
        self,
        consumer,
        *,
        direction_source=None,
        beta_source=None,
    ):
        kind = self.consumer_kind(consumer)
        if kind is CollisionConsumerKind.SCALAR_Q_KERNEL_UNRESOLVED:
            raise UnresolvedCollisionConsumerError(
                "the direction-dependent source-time generator does not reduce "
                "to the unresolved scalar Q collision-rate input"
            )
        rest = RestOpacityPerSecond(self.context.rest_opacity_per_second())
        if kind is CollisionConsumerKind.APPLIES_RELATIVE_FLUX:
            if direction_source is not None or beta_source is not None:
                raise ValueError("internal-relative-flux consumers accept rest opacity only")
            return self.validate_input(consumer, rest)
        if direction_source is None or beta_source is None:
            raise ValueError("observer-rate consumer requires direction_source and beta_source")
        # Source-ray validity is not quotiented at electron vacuum.  Validate
        # it before the collision-off short circuit.
        _beta_binary64(beta_source, "beta_source")
        _unit_direction_decimal(direction_source)
        if self.context.electron.n_e_free == 0.0:
            # The frame representative is quotiented at vacuum.
            return self.validate_input(consumer, ObserverRayRatePerSecond(0.0, None))
        factor = exact_observer_doppler_factor(
            direction_source,
            beta_source,
            self.context.electron.beta_normal,
        )
        return self.validate_input(
            consumer,
            ObserverRayRatePerSecond(rest.value_per_s * float(factor), float(factor)),
        )

    def authority_metadata(self) -> dict:
        return {
            "schema": "bass.electron_collision_consumer_contract/v1",
            "internal_relative_flux_input": "rest_opacity_n_e_sigma_T_c",
            "observer_input": "rest_opacity_times_D_e_from_source",
            "relative_flux_power": 1,
            "matter_collision_moving": {
                "consumer_id": CollisionConsumerId.MATTER_COLLISION_MOVING.value,
                "kind": CollisionConsumerKind.APPLIES_RELATIVE_FLUX.value,
            },
            "external_observer_ray": {
                "consumer_id": CollisionConsumerId.EXTERNAL_OBSERVER_RAY.value,
                "kind": CollisionConsumerKind.EXPECTS_OBSERVER_RAY_RATE.value,
            },
            "scalar_q_kernel": {
                "consumer_id": CollisionConsumerId.Q_SCALAR_KERNEL.value,
                "kind": CollisionConsumerKind.SCALAR_Q_KERNEL_UNRESOLVED.value,
            },
            "runtime_signature_type_enforced": False,
            "production_runtime_wired": False,
        }


__all__ = [
    "AuthorityProvenance",
    "BOLTZMANN_CONSTANT_J_K",
    "ColdThomsonBudget",
    "ColdThomsonCertificate",
    "ColdThomsonStatus",
    "CollisionConsumerId",
    "CollisionConsumerKind",
    "DopplerBounds",
    "ELECTRON_REST_ENERGY_J",
    "ElectronCollisionConsumerContract",
    "ElectronStateAuthority",
    "ElectronTemperatureAuthority",
    "EnergyBoundKind",
    "ObserverRayRatePerSecond",
    "ObserverFrameAuthority",
    "PhotonEnergyBound",
    "RestOpacityPerSecond",
    "UnresolvedCollisionConsumerError",
    "all_sky_doppler_bounds",
    "certify_cold_thomson",
    "exact_observer_doppler_factor",
    "klein_nishina_total_ratio",
    "klein_nishina_total_deficit",
]
