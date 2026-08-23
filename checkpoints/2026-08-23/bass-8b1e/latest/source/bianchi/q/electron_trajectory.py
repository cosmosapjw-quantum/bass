"""Finite-trajectory cold-Thomson support and orientation authority.

This module lifts the instantaneous :mod:`bianchi.q.electron_validity` gate
onto a closed interval of dimensionless Q Hubble time.  It is intentionally a
bounded Python authority: it does not generate a direction-dependent Q
collision operator and it is not wired into a production solver or Rust ABI.

Conventions
-----------

* metric ``(-,+,+,+)``;
* ``tau_Q`` increases to the physical future and ``dt/dtau_Q=1/H_normal``;
* canonical arrays are strictly increasing even when a solver traverses them
  in reverse;
* photon energy is joules, temperature kelvin, ``H_normal`` is ``s^-1``;
* ``nu_tau=d optical_depth/dtau_Q`` is non-negative and dimensionless;
* only exact identity bindings to ``q_hubble_time_tau`` are accepted here.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, localcontext
import enum
from fractions import Fraction
import hashlib
import math
import re

import numpy as np

from bianchi.physical.units import (
    BOLTZMANN_CONSTANT_J_K,
    C_LIGHT_M_S,
    ELECTRON_REST_ENERGY_J,
)
from bianchi.q import electron_rate as ER
from bianchi.q import electron_validity as EV


_SHA256 = re.compile(r"[0-9a-f]{64}")
_DECIMAL_PRECISION = 100
_FLOAT_EPSILON = Fraction(1, 2**52)
_MIN_BINARY64_SUBNORMAL = Fraction(1, 2**1074)
_ROUNDING_SAFETY = 64
_MAX_SAFE_CURRENT_TEMPORAL = Fraction.from_float(
    math.sqrt(np.finfo(float).max) / 4.0
)
_MIN_SAFE_CURRENT_TEMPORAL = Fraction.from_float(
    16.0 * math.sqrt(np.nextafter(0.0, np.inf))
)
_CERTIFICATE_FACTORY_TOKEN = object()


class _NumericDomainUnverified(ValueError):
    """The live binary64 evaluator could not be enclosed rigorously."""


def _nonempty(value, name: str) -> str:
    out = str(value).strip()
    if not out or "\0" in out:
        raise ValueError(f"{name} must be non-empty and contain no NUL")
    return out


def _require_provenance(value) -> EV.AuthorityProvenance:
    if not isinstance(value, EV.AuthorityProvenance):
        raise TypeError("provenance must be an AuthorityProvenance")
    return value


def _hash(schema: str, parts) -> str:
    digest = hashlib.sha256()
    digest.update(schema.encode("ascii") + b"\0")
    for part in parts:
        if isinstance(part, enum.Enum):
            token = f"enum:{part.value}".encode("utf-8")
        elif isinstance(part, (float, np.floating)):
            value = 0.0 if float(part) == 0.0 else float(part)
            token = f"float:{value.hex()}".encode("ascii")
        elif isinstance(part, bool):
            token = b"bool:1" if part else b"bool:0"
        elif part is None:
            token = b"none"
        else:
            token = f"text:{part}".encode("utf-8")
        digest.update(len(token).to_bytes(8, "big") + token)
    return digest.hexdigest()


def _nodes(values) -> tuple[float, ...]:
    out = np.asarray(values, dtype=float)
    if out.ndim != 1 or out.size < 2:
        raise ValueError("trajectory nodes must be one-dimensional with length >= 2")
    if not np.isfinite(out).all():
        raise ValueError("trajectory nodes must be finite and strictly increasing")
    for left, right in zip(out[:-1], out[1:]):
        width = float(right) - float(left)
        if not np.isfinite(width) or width <= 0.0:
            raise ValueError(
                "trajectory node intervals must be finite positive binary64 values"
            )
    return tuple(float(value) for value in out)


def _nonnegative_values(values, nodes, name: str, *, positive=False):
    out = np.asarray(values, dtype=float)
    if out.shape != (len(nodes),) or not np.isfinite(out).all():
        raise ValueError(f"{name} values must be finite and match trajectory nodes")
    if np.any(out <= 0.0) if positive else np.any(out < 0.0):
        qualifier = "positive" if positive else "non-negative"
        raise ValueError(f"{name} values must be {qualifier}")
    if positive and np.any(out < np.finfo(float).tiny):
        raise ValueError(
            f"{name} values must be normal positive binary64 values"
        )
    out[out == 0.0] = 0.0
    return tuple(float(value) for value in out)


def _index_weight(nodes: tuple[float, ...], tau: float) -> tuple[int, float]:
    query = float(tau)
    if not np.isfinite(query):
        raise ValueError("tau query must be finite")
    if query < nodes[0] or query > nodes[-1]:
        raise ValueError(
            f"tau={query} lies outside closed support [{nodes[0]}, {nodes[-1]}]"
        )
    if query == nodes[-1]:
        return len(nodes) - 2, 1.0
    index = int(np.searchsorted(nodes, query, side="right") - 1)
    index = max(index, 0)
    weight = (query - nodes[index]) / (nodes[index + 1] - nodes[index])
    return index, float(weight)


def _scalar_at(nodes, values, tau) -> float:
    index, weight = _index_weight(nodes, tau)
    return float((1.0 - weight) * values[index] + weight * values[index + 1])


def _vector_at(nodes, values, tau) -> tuple[float, ...]:
    index, weight = _index_weight(nodes, tau)
    left = np.asarray(values[index], dtype=float)
    right = np.asarray(values[index + 1], dtype=float)
    out = (1.0 - weight) * left + weight * right
    return tuple(float(value) for value in out)


@dataclass(frozen=True, slots=True)
class QHubbleTimeCoordinate:
    """Provenance-bound identity coordinate used by this bounded authority."""

    origin_event: str
    provenance: EV.AuthorityProvenance
    coordinate_kind: str = "q_hubble_time_tau"
    mapping: str = "identity"
    unit: str = "dimensionless"
    future_direction: int = 1

    def __post_init__(self):
        object.__setattr__(self, "origin_event", _nonempty(self.origin_event, "origin_event"))
        _require_provenance(self.provenance)
        if self.coordinate_kind != "q_hubble_time_tau":
            raise ValueError("E4 accepts only q_hubble_time_tau")
        if self.mapping != "identity":
            raise ValueError("E4 accepts only an explicit identity coordinate binding")
        if self.unit != "dimensionless" or self.future_direction != 1:
            raise ValueError("tau_Q must be dimensionless and future increasing")

    @property
    def payload_sha256(self) -> str:
        return _hash(
            "bass.q_hubble_time_coordinate/v1",
            (
                self.coordinate_kind,
                self.origin_event,
                self.mapping,
                self.unit,
                self.future_direction,
                "dt_phys/dtau_Q=1/H_normal",
                self.provenance.source_id,
                self.provenance.source_sha256,
            ),
        )


@dataclass(frozen=True, slots=True)
class ElectronScheduleBinding:
    """Bind one immutable schedule payload to one explicit Q-time origin."""

    schedule: object
    coordinate: QHubbleTimeCoordinate
    provenance: EV.AuthorityProvenance
    schedule_payload_sha256: str
    view: ER.ElectronScheduleTrajectoryView = field(init=False, repr=False)

    def __post_init__(self):
        if not isinstance(
            self.schedule,
            (ER.PrescribedIndependentElectronSchedule, ER.PrescribedComovingElectronSchedule),
        ):
            raise TypeError("schedule must be a prescribed electron schedule")
        if not isinstance(self.coordinate, QHubbleTimeCoordinate):
            raise TypeError("coordinate must be a QHubbleTimeCoordinate")
        _require_provenance(self.provenance)
        digest = str(self.schedule_payload_sha256)
        if _SHA256.fullmatch(digest) is None:
            raise ValueError("schedule_payload_sha256 must be lowercase 64-hex")
        view = self.schedule.trajectory_view()
        _nodes(view.nodes_ascending)
        if digest != view.schedule_payload_sha256:
            raise ValueError("declared schedule payload does not match live schedule bytes")
        if view.coordinate_kind != self.coordinate.coordinate_kind:
            raise ValueError("schedule coordinate kind does not match binding")
        if view.c_m_s != C_LIGHT_M_S:
            raise ValueError("trajectory validity authority requires exact SI c")
        object.__setattr__(self, "view", view)

    @classmethod
    def bind(cls, schedule, *, coordinate, provenance):
        return cls(
            schedule=schedule,
            coordinate=coordinate,
            provenance=provenance,
            schedule_payload_sha256=schedule.payload_sha256,
        )

    @property
    def support(self) -> tuple[float, float]:
        return self.view.nodes_ascending[0], self.view.nodes_ascending[-1]

    @property
    def payload_sha256(self) -> str:
        return _hash(
            "bass.electron_schedule_coordinate_binding/v1",
            (
                self.view.interpolation,
                *self.view.nodes_ascending,
                self.view.number_current_nodes,
                self.view.density_nodes_m3,
                self.view.source_id,
                self.view.source_sha256,
                self.schedule_payload_sha256,
                self.coordinate.payload_sha256,
                self.provenance.source_id,
                self.provenance.source_sha256,
            ),
        )


class ScalarProfileKind(enum.Enum):
    PHOTON_ENERGY = "hard_or_declared_photon_energy_support"
    ELECTRON_TEMPERATURE = "electron_temperature"
    NORMAL_HUBBLE = "normal_hubble"
    LOCAL_RAY_RATE = "local_future_ray_rate"


@dataclass(frozen=True, slots=True)
class ScalarTrajectoryProfile:
    """Typed immutable piecewise-linear scalar trajectory."""

    kind: ScalarProfileKind
    tau_nodes: tuple[float, ...]
    values: tuple[float, ...] | None
    coordinate: QHubbleTimeCoordinate
    provenance: EV.AuthorityProvenance
    source_frame: str | None = None
    energy_bound_kind: EV.EnergyBoundKind | None = None

    def __post_init__(self):
        if not isinstance(self.kind, ScalarProfileKind):
            raise TypeError("kind must be a ScalarProfileKind")
        nodes = _nodes(self.tau_nodes)
        object.__setattr__(self, "tau_nodes", nodes)
        if not isinstance(self.coordinate, QHubbleTimeCoordinate):
            raise TypeError("coordinate must be a QHubbleTimeCoordinate")
        _require_provenance(self.provenance)

        if self.kind is ScalarProfileKind.PHOTON_ENERGY:
            if not isinstance(self.energy_bound_kind, EV.EnergyBoundKind):
                raise TypeError("photon-energy profile needs an EnergyBoundKind")
            object.__setattr__(
                self, "source_frame", _nonempty(self.source_frame, "source_frame")
            )
            if self.energy_bound_kind in {
                EV.EnergyBoundKind.HARD_FINITE,
                EV.EnergyBoundKind.EFFECTIVE_TAIL,
            }:
                values = _nonnegative_values(self.values, nodes, "photon energy")
            elif self.values is not None:
                raise ValueError("bolometric/unknown support cannot carry finite maxima")
            else:
                values = None
        else:
            if self.energy_bound_kind is not None or self.source_frame is not None:
                raise ValueError("energy metadata is valid only for photon energy")
            values = _nonnegative_values(
                self.values,
                nodes,
                self.kind.value,
                positive=self.kind is ScalarProfileKind.NORMAL_HUBBLE,
            )
        object.__setattr__(self, "values", values)

    @classmethod
    def hard_photon_energy_j(
        cls, tau_nodes, values, *, source_frame, coordinate, provenance
    ):
        return cls(
            ScalarProfileKind.PHOTON_ENERGY,
            tau_nodes,
            values,
            coordinate,
            provenance,
            source_frame,
            EV.EnergyBoundKind.HARD_FINITE,
        )

    @classmethod
    def bolometric_photon_energy(
        cls, tau_nodes, *, source_frame, coordinate, provenance
    ):
        return cls(
            ScalarProfileKind.PHOTON_ENERGY,
            tau_nodes,
            None,
            coordinate,
            provenance,
            source_frame,
            EV.EnergyBoundKind.BOLOMETRIC,
        )

    @classmethod
    def unknown_photon_energy(
        cls, tau_nodes, *, source_frame, coordinate, provenance
    ):
        return cls(
            ScalarProfileKind.PHOTON_ENERGY,
            tau_nodes,
            None,
            coordinate,
            provenance,
            source_frame,
            EV.EnergyBoundKind.UNKNOWN,
        )

    @classmethod
    def effective_tail_photon_energy_j(
        cls, tau_nodes, values, *, source_frame, coordinate, provenance
    ):
        return cls(
            ScalarProfileKind.PHOTON_ENERGY,
            tau_nodes,
            values,
            coordinate,
            provenance,
            source_frame,
            EV.EnergyBoundKind.EFFECTIVE_TAIL,
        )

    @classmethod
    def electron_temperature_k(cls, tau_nodes, values, *, coordinate, provenance):
        return cls(
            ScalarProfileKind.ELECTRON_TEMPERATURE,
            tau_nodes,
            values,
            coordinate,
            provenance,
        )

    @classmethod
    def normal_hubble_per_s(cls, tau_nodes, values, *, coordinate, provenance):
        return cls(
            ScalarProfileKind.NORMAL_HUBBLE,
            tau_nodes,
            values,
            coordinate,
            provenance,
        )

    @classmethod
    def local_ray_rate_per_tau(cls, tau_nodes, values, *, coordinate, provenance):
        return cls(
            ScalarProfileKind.LOCAL_RAY_RATE,
            tau_nodes,
            values,
            coordinate,
            provenance,
        )

    @property
    def support(self) -> tuple[float, float]:
        return self.tau_nodes[0], self.tau_nodes[-1]

    def at(self, tau) -> float:
        if self.values is None:
            raise ValueError("this photon support has no finite pointwise maximum")
        return _scalar_at(self.tau_nodes, self.values, tau)

    def maximum_on(self, start, end) -> float:
        if self.values is None:
            raise ValueError("this photon support has no finite segment maximum")
        return _scalar_profile_maximum_bound(self, start, end)

    @property
    def payload_sha256(self) -> str:
        return _hash(
            "bass.scalar_trajectory_profile/v1",
            (
                self.kind,
                *self.tau_nodes,
                self.values,
                self.source_frame,
                self.energy_bound_kind,
                self.coordinate.payload_sha256,
                self.provenance.source_id,
                self.provenance.source_sha256,
            ),
        )


class BetaProfileRole(enum.Enum):
    SOURCE_FRAME = "source_frame"
    LIVE_FLUID = "live_fluid"


@dataclass(frozen=True, slots=True)
class BetaTrajectoryProfile:
    """Typed piecewise-linear normal-tetrad velocity profile."""

    role: BetaProfileRole
    tau_nodes: tuple[float, ...]
    beta_normal: tuple[tuple[float, float, float], ...]
    frame_id: str
    coordinate: QHubbleTimeCoordinate
    provenance: EV.AuthorityProvenance

    def __post_init__(self):
        if not isinstance(self.role, BetaProfileRole):
            raise TypeError("role must be a BetaProfileRole")
        nodes = _nodes(self.tau_nodes)
        beta = np.asarray(self.beta_normal, dtype=float)
        if beta.shape != (len(nodes), 3) or not np.isfinite(beta).all():
            raise ValueError("beta profile must be finite with shape (nodes, 3)")
        if np.any(np.einsum("ij,ij->i", beta, beta) >= 1.0):
            raise ValueError("every beta profile node must be subluminal")
        beta[beta == 0.0] = 0.0
        object.__setattr__(self, "tau_nodes", nodes)
        object.__setattr__(
            self,
            "beta_normal",
            tuple(tuple(float(component) for component in row) for row in beta),
        )
        object.__setattr__(self, "frame_id", _nonempty(self.frame_id, "frame_id"))
        if not isinstance(self.coordinate, QHubbleTimeCoordinate):
            raise TypeError("coordinate must be a QHubbleTimeCoordinate")
        _require_provenance(self.provenance)

    @classmethod
    def source_frame(
        cls, tau_nodes, beta_normal, *, frame_id, coordinate, provenance
    ):
        return cls(
            BetaProfileRole.SOURCE_FRAME,
            tau_nodes,
            beta_normal,
            frame_id,
            coordinate,
            provenance,
        )

    @classmethod
    def live_fluid(
        cls, tau_nodes, beta_normal, *, frame_id, coordinate, provenance
    ):
        return cls(
            BetaProfileRole.LIVE_FLUID,
            tau_nodes,
            beta_normal,
            frame_id,
            coordinate,
            provenance,
        )

    @property
    def support(self) -> tuple[float, float]:
        return self.tau_nodes[0], self.tau_nodes[-1]

    def at(self, tau) -> tuple[float, float, float]:
        return _vector_at(self.tau_nodes, self.beta_normal, tau)

    @property
    def payload_sha256(self) -> str:
        return _hash(
            "bass.beta_trajectory_profile/v1",
            (
                self.role,
                *self.tau_nodes,
                self.beta_normal,
                self.frame_id,
                self.coordinate.payload_sha256,
                self.provenance.source_id,
                self.provenance.source_sha256,
            ),
        )


class TrajectoryStatus(enum.Enum):
    CERTIFIED_COLD_DELTA_TRAJECTORY = "certified_cold_delta_trajectory"
    VACUOUS_COLLISION_OFF_TRAJECTORY = "vacuous_collision_off_trajectory"
    UNVERIFIED_ENERGY_SUPPORT = "unverified_energy_support"
    UNVERIFIED_FINITE_TEMPERATURE_TAIL = "unverified_finite_temperature_tail"
    UNVERIFIED_NUMERIC_DOMAIN = "unverified_numeric_domain"
    REJECTED_TOTAL_CROSS_SECTION_BUDGET = "rejected_total_cross_section_budget"
    REJECTED_TEMPERATURE_POLICY = "rejected_temperature_policy"


def _trajectory_outcome(segments, photon_energy_kind):
    nonvacuum = [item for item in segments if not item.vacuum]
    statuses = {item.status for item in nonvacuum}
    if not nonvacuum:
        return (
            TrajectoryStatus.VACUOUS_COLLISION_OFF_TRAJECTORY,
            ("all_requested_segments_are_exact_vacuum",),
        )
    if "unverified_numeric_domain" in statuses:
        return (
            TrajectoryStatus.UNVERIFIED_NUMERIC_DOMAIN,
            ("live_binary64_trajectory_enclosure_not_proved",),
        )
    if "unverified_energy_support" in statuses:
        return (
            TrajectoryStatus.UNVERIFIED_ENERGY_SUPPORT,
            (f"{photon_energy_kind.value}_is_not_a_hard_support",),
        )
    if "rejected_total_cross_section_budget" in statuses:
        return (
            TrajectoryStatus.REJECTED_TOTAL_CROSS_SECTION_BUDGET,
            ("at_least_one_segment_exceeds_total_cross_section_budget",),
        )
    if "rejected_temperature_policy" in statuses:
        return (
            TrajectoryStatus.REJECTED_TEMPERATURE_POLICY,
            ("at_least_one_segment_exceeds_declared_theta_policy",),
        )
    if "unverified_finite_temperature_tail" in statuses:
        return (
            TrajectoryStatus.UNVERIFIED_FINITE_TEMPERATURE_TAIL,
            ("finite_temperature_distribution_tail_not_bounded",),
        )
    return (
        TrajectoryStatus.CERTIFIED_COLD_DELTA_TRAJECTORY,
        ("all_nonvacuum_segments_within_hard_cold_total_rate_budget",),
    )


def _decimal(value: float) -> Decimal:
    return Decimal.from_float(float(value))


def _fraction(value: float) -> Fraction:
    return Fraction.from_float(float(value))


def _fraction_decimal(value: Fraction) -> Decimal:
    with localcontext() as context:
        context.prec = _DECIMAL_PRECISION
        out = Decimal(value.numerator) / Decimal(value.denominator)
        if Fraction(out) < value:
            out = context.next_plus(out)
        return out


def _sqrt_fraction(value: Fraction) -> Decimal:
    if value < 0:
        raise ValueError("authority square root received a negative rational")
    with localcontext() as context:
        context.prec = _DECIMAL_PRECISION
        out = (
            Decimal(value.numerator) / Decimal(value.denominator)
        ).sqrt()
        if Fraction(out) * Fraction(out) < value:
            out = context.next_plus(out)
        return out


def _upward(value: Decimal, *, steps: int = 4) -> float:
    """Round a non-negative Decimal outward to binary64."""
    if not value.is_finite() or value < 0:
        raise ValueError("authority bound is not a finite non-negative real")
    if value == 0:
        return 0.0
    out = float(value)
    if not np.isfinite(out):
        raise ValueError("authority bound overflowed binary64")
    if Decimal.from_float(out) < value:
        out = float(np.nextafter(out, np.inf))
    for _ in range(steps - 1):
        out = float(np.nextafter(out, np.inf))
    return out


def _gamma_beta_decimal(beta) -> Decimal:
    with localcontext() as context:
        context.prec = _DECIMAL_PRECISION
        values = tuple(_decimal(component) for component in beta)
        one = Decimal(1)
        norm2 = sum((value * value for value in values), Decimal(0))
        if norm2 >= one:
            raise ValueError("interpolated beta is not subluminal")
        return one / (one - norm2).sqrt()


def _beta_from_gamma(gamma: Decimal) -> Decimal:
    with localcontext() as context:
        context.prec = _DECIMAL_PRECISION
        one = Decimal(1)
        if gamma < one:
            raise ArithmeticError("gamma bound fell below one")
        return (one - one / (gamma * gamma)).sqrt()


def _minkowski_q(current: tuple[Fraction, ...]) -> Fraction:
    return current[0] * current[0] - sum(
        (value * value for value in current[1:]), Fraction(0)
    )


def _quadratic_minimum(
    a_coef: Fraction, b_coef: Fraction, c_coef: Fraction
) -> Fraction:
    candidates = [c_coef, a_coef + b_coef + c_coef]
    if a_coef != 0:
        root = -b_coef / (2 * a_coef)
        if 0 < root < 1:
            candidates.append(a_coef * root * root + b_coef * root + c_coef)
    return min(candidates)


def _interpolation_error(left: Fraction, right: Fraction) -> Fraction:
    """Conservative absolute enclosure of the live binary64 affine evaluator."""
    return _ROUNDING_SAFETY * (
        _FLOAT_EPSILON * (abs(left) + abs(right))
        + _MIN_BINARY64_SUBNORMAL
    )


def _independent_gamma_bound(current0, current1, tau0, tau1):
    """Bound exact-current and live binary64 reconstructed electron gamma.

    The stationary algebra is exact over the binary64 knot values.  A second
    enclosure covers the multiply/add interpolation and component-wise
    division performed by ``PrescribedIndependentElectronSchedule.at``.
    """
    zero0 = all(value == 0.0 for value in current0)
    zero1 = all(value == 0.0 for value in current1)
    if zero0 and zero1:
        return None, ()

    left = tuple(_fraction(value) for value in current0)
    right = tuple(_fraction(value) for value in current1)
    nonzero = right if zero0 else left
    if zero0 or zero1:
        if any(value != 0 for value in nonzero[1:]):
            raise _NumericDomainUnverified(
                "a moving independent current touches exact vacuum; the binary64 "
                "subnormal transition has no finite certified gamma enclosure"
            )
        if nonzero[0] > _MAX_SAFE_CURRENT_TEMPORAL:
            raise _NumericDomainUnverified(
                "live zero-touching rest-current density may overflow binary64"
            )
        left_tau = float(tau0)
        right_tau = float(tau1)
        if zero0:
            query = float(np.nextafter(left_tau, right_tau))
            minimum_weight = (query - left_tau) / (right_tau - left_tau)
        else:
            query = float(np.nextafter(right_tau, left_tau))
            weight = (query - left_tau) / (right_tau - left_tau)
            minimum_weight = 1.0 - weight
        if not np.isfinite(minimum_weight) or minimum_weight <= 0.0:
            raise _NumericDomainUnverified(
                "zero-touching current has no positive binary64 edge weight"
            )
        minimum_temporal = (
            _fraction(minimum_weight)
            * nonzero[0]
            * (Fraction(1) - 8 * _FLOAT_EPSILON)
            - 8 * _MIN_BINARY64_SUBNORMAL
        )
        if minimum_temporal < _MIN_SAFE_CURRENT_TEMPORAL:
            raise _NumericDomainUnverified(
                "live zero-touching rest-current density may underflow binary64"
            )
        return Decimal(1), ()

    delta = tuple(r - l for l, r in zip(left, right))
    t0, t1 = left[0], delta[0]
    x0, x1 = left[1:], delta[1:]
    c_coef = _minkowski_q(left)
    b_coef = 2 * (
        t0 * t1 - sum((a * b for a, b in zip(x0, x1)), Fraction(0))
    )
    a_coef = t1 * t1 - sum((value * value for value in x1), Fraction(0))
    if left[0] <= 0 or right[0] <= 0 or c_coef <= 0 or _minkowski_q(right) <= 0:
        raise ValueError("electron-current knots must be strictly future timelike")

    constant = 2 * t1 * c_coef - b_coef * t0
    linear = t1 * b_coef - 2 * a_coef * t0
    stationary = []
    if linear != 0:
        root = -constant / linear
        if 0 < root < 1:
            stationary.append(root)

    gamma2_candidates = []
    for weight in (Fraction(0), Fraction(1), *stationary):
        current = tuple(l + weight * d for l, d in zip(left, delta))
        q_value = _minkowski_q(current)
        if current[0] <= 0 or q_value <= 0:
            raise ValueError("linear electron current lost future timelikeness")
        gamma2_candidates.append(current[0] * current[0] / q_value)
    exact_gamma2_max = max(gamma2_candidates)

    q_min = _quadratic_minimum(a_coef, b_coef, c_coef)
    errors = tuple(_interpolation_error(l, r) for l, r in zip(left, right))
    temporal_max = max(left[0], right[0])
    spatial_max = tuple(max(abs(l), abs(r)) for l, r in zip(left[1:], right[1:]))
    q_lower = q_min - 2 * temporal_max * errors[0] - sum(
        (
            2 * maximum * error + error * error
            for maximum, error in zip(spatial_max, errors[1:])
        ),
        Fraction(0),
    )
    if q_lower <= 0:
        raise _NumericDomainUnverified(
            "binary64 interpolation enclosure does not prove a timelike current"
        )
    temporal_upper = temporal_max + errors[0]
    temporal_lower = min(left[0], right[0]) - errors[0]
    if temporal_lower <= 0:
        raise _NumericDomainUnverified(
            "binary64 interpolation enclosure does not prove future direction"
        )
    if temporal_upper > _MAX_SAFE_CURRENT_TEMPORAL:
        raise _NumericDomainUnverified(
            "live current norm/density reconstruction may overflow binary64"
        )
    norm_error = (
        32 * _FLOAT_EPSILON * temporal_upper
        + 64 * _MIN_BINARY64_SUBNORMAL
    )
    live_norm_q_lower = (
        q_lower
        - 2 * temporal_upper * norm_error
        - norm_error * norm_error
    )
    if live_norm_q_lower < 1024 * _MIN_BINARY64_SUBNORMAL:
        raise _NumericDomainUnverified(
            "live current norm/density reconstruction may underflow binary64"
        )
    ratio2_upper = Fraction(1) - q_lower / (temporal_upper * temporal_upper)
    ratio2_upper = max(Fraction(0), ratio2_upper)
    division_factor = Fraction(1) + 8 * _FLOAT_EPSILON
    beta2_upper = (
        ratio2_upper * division_factor * division_factor
        + 256 * _MIN_BINARY64_SUBNORMAL
    )
    if beta2_upper >= 1:
        raise _NumericDomainUnverified(
            "binary64 current division enclosure does not prove subluminality"
        )
    beta2_dot_upper = (
        beta2_upper * (Fraction(1) + 8 * _FLOAT_EPSILON)
        + 64 * _MIN_BINARY64_SUBNORMAL
    )
    if beta2_dot_upper >= 1:
        raise _NumericDomainUnverified(
            "live binary64 beta dot product may round to a non-subluminal value"
        )
    runtime_gamma2_upper = Fraction(1) / (Fraction(1) - beta2_upper)
    return (
        _sqrt_fraction(max(exact_gamma2_max, runtime_gamma2_upper)),
        tuple(float(value) for value in stationary),
    )


def _owner_index(nodes: tuple[float, ...], tau: float) -> int:
    index = int(np.searchsorted(nodes, float(tau), side="right") - 1)
    return min(max(index, 0), len(nodes) - 2)


def _scalar_profile_maximum_bound(profile, start, end) -> float:
    """Outward bound the live binary64 scalar evaluator on a closed span."""
    if profile.values is None:
        raise ValueError("profile has no finite scalar values")
    lo = float(start)
    hi = float(end)
    if not np.isfinite(lo) or not np.isfinite(hi) or hi < lo:
        raise ValueError("scalar maximum span must be finite and ascending")
    if lo < profile.tau_nodes[0] or hi > profile.tau_nodes[-1]:
        raise ValueError("scalar maximum span exceeds profile support")
    knots = [lo]
    knots.extend(value for value in profile.tau_nodes if lo < value < hi)
    knots.append(hi)
    bounds = []
    for cell_start, cell_end in zip(knots[:-1], knots[1:]):
        index = _owner_index(profile.tau_nodes, cell_start)
        if cell_end > profile.tau_nodes[index + 1]:
            raise ArithmeticError("scalar maximum partition crossed an owner cell")
        left = _fraction(profile.values[index])
        right = _fraction(profile.values[index + 1])
        if left == 0 and right == 0:
            bounds.append(Fraction(0))
        else:
            bounds.append(
                max(left, right) + _interpolation_error(left, right)
            )
    upper = max(bounds, default=Fraction(0))
    if upper > Fraction.from_float(np.finfo(float).max):
        raise _NumericDomainUnverified(
            "live scalar interpolation may overflow binary64"
        )
    return _upward(_fraction_decimal(upper)) if upper != 0 else 0.0


def _beta_profile_gamma_bound(profile, start, end) -> Decimal:
    """Enclose the live binary64 profile evaluator on its whole owner cell."""
    index = _owner_index(profile.tau_nodes, start)
    if end > profile.tau_nodes[index + 1]:
        raise ArithmeticError("union segment crossed a beta-profile owner cell")
    left = tuple(_fraction(value) for value in profile.beta_normal[index])
    right = tuple(_fraction(value) for value in profile.beta_normal[index + 1])
    exact_norm2 = max(
        sum((value * value for value in left), Fraction(0)),
        sum((value * value for value in right), Fraction(0)),
    )
    errors = tuple(_interpolation_error(l, r) for l, r in zip(left, right))
    component_max = tuple(max(abs(l), abs(r)) for l, r in zip(left, right))
    norm2_upper = exact_norm2 + sum(
        (
            2 * maximum * error + error * error
            for maximum, error in zip(component_max, errors)
        ),
        Fraction(0),
    )
    if norm2_upper >= 1:
        raise _NumericDomainUnverified(
            "binary64 beta interpolation enclosure does not prove subluminality"
        )
    dot_upper = (
        norm2_upper * (Fraction(1) + 8 * _FLOAT_EPSILON)
        + 64 * _MIN_BINARY64_SUBNORMAL
    )
    if dot_upper >= 1:
        raise _NumericDomainUnverified(
            "live binary64 beta dot product may round to a non-subluminal value"
        )
    return _sqrt_fraction(Fraction(1) / (Fraction(1) - norm2_upper))


def _relative_doppler_upper(gamma_e: Decimal, gamma_s: Decimal) -> tuple[Decimal, Decimal]:
    with localcontext() as context:
        context.prec = _DECIMAL_PRECISION
        one = Decimal(1)
        beta_e = _beta_from_gamma(gamma_e)
        beta_s = _beta_from_gamma(gamma_s)
        relative_gamma = gamma_e * gamma_s * (one + beta_e * beta_s)
        if relative_gamma < one:
            raise ArithmeticError("relative gamma upper bound fell below one")
        doppler = relative_gamma + (
            (relative_gamma - one) * (relative_gamma + one)
        ).sqrt()
        return relative_gamma, doppler


def _schedule_vector_at(view, tau):
    if view.number_current_nodes is None:
        raise TypeError("schedule does not own an independent number current")
    return _vector_at(view.nodes_ascending, view.number_current_nodes, tau)


def _schedule_density_at(view, tau):
    if view.density_nodes_m3 is None:
        raise TypeError("schedule does not own a comoving density")
    return _scalar_at(view.nodes_ascending, view.density_nodes_m3, tau)


def _comoving_density_cell_is_vacuum(view, start, end) -> bool:
    if view.density_nodes_m3 is None:
        raise TypeError("schedule does not own a comoving density")
    index = _owner_index(view.nodes_ascending, start)
    if end > view.nodes_ascending[index + 1]:
        raise ArithmeticError("union segment crossed a density owner cell")
    left = _fraction(view.density_nodes_m3[index])
    right = _fraction(view.density_nodes_m3[index + 1])
    if left == 0 and right == 0:
        return True
    upper = max(left, right) + _interpolation_error(left, right)
    if upper > Fraction.from_float(np.finfo(float).max):
        raise _NumericDomainUnverified(
            "live comoving-density interpolation may overflow binary64"
        )
    return False


@dataclass(frozen=True, slots=True)
class SegmentSupremumWitness:
    tau_start: float
    tau_end: float
    closure: str
    vacuum: bool
    electron_gamma_max_upper: float | None
    electron_gamma_stationary_fractions: tuple[float, ...]
    source_gamma_max_upper: float | None
    relative_gamma_max_upper: float | None
    doppler_max_upper: float | None
    source_energy_max_j: float | None
    electron_energy_max_j: float | None
    x_max_upper: float | None
    temperature_max_k: float | None
    theta_max_upper: float | None
    total_cross_section_relative_deficit_upper: float | None
    status: str

    def __post_init__(self):
        allowed = {
            "vacuum_collision_off",
            "unverified_numeric_domain",
            "unverified_energy_support",
            "rejected_total_cross_section_budget",
            "rejected_temperature_policy",
            "unverified_finite_temperature_tail",
            "certified_cold_delta",
        }
        if self.status not in allowed:
            raise ValueError("unknown segment witness status")
        if self.tau_end <= self.tau_start:
            raise ValueError("segment witness span must be positive and ascending")
        if self.closure not in {"independent", "comoving"}:
            raise ValueError("segment witness closure is invalid")
        if self.vacuum:
            if self.status != "vacuum_collision_off":
                raise ValueError("vacuum segment must be collision-off")
            if any(
                value is not None
                for value in (
                    self.electron_gamma_max_upper,
                    self.source_gamma_max_upper,
                    self.relative_gamma_max_upper,
                    self.doppler_max_upper,
                    self.source_energy_max_j,
                    self.electron_energy_max_j,
                    self.x_max_upper,
                    self.theta_max_upper,
                    self.total_cross_section_relative_deficit_upper,
                )
            ):
                raise ValueError("vacuum segment cannot carry collision bounds")
        elif self.status == "vacuum_collision_off":
            raise ValueError("non-vacuum segment cannot be collision-off")
        if self.status == "certified_cold_delta":
            if self.temperature_max_k != 0.0 or self.theta_max_upper != 0.0:
                raise ValueError("cold-delta certification requires exact zero temperature")
            if any(
                value is None
                for value in (
                    self.electron_gamma_max_upper,
                    self.source_gamma_max_upper,
                    self.relative_gamma_max_upper,
                    self.doppler_max_upper,
                    self.source_energy_max_j,
                    self.electron_energy_max_j,
                    self.x_max_upper,
                    self.total_cross_section_relative_deficit_upper,
                )
            ):
                raise ValueError("cold-delta certification needs complete bounds")
        if (
            self.status == "unverified_finite_temperature_tail"
            and not (self.temperature_max_k is not None and self.temperature_max_k > 0.0)
        ):
            raise ValueError("finite-temperature status requires positive temperature")


@dataclass(frozen=True, slots=True, init=False)
class TrajectoryColdThomsonCertificate:
    status: TrajectoryStatus
    certified: bool
    common_support: tuple[float, float]
    requested_span: tuple[float, float]
    segments: tuple[SegmentSupremumWitness, ...]
    reasons: tuple[str, ...]
    electron_binding: ElectronScheduleBinding
    photon_energy: ScalarTrajectoryProfile
    electron_temperature: ScalarTrajectoryProfile
    source_frame: BetaTrajectoryProfile
    normal_hubble: ScalarTrajectoryProfile
    local_ray_rate: ScalarTrajectoryProfile
    live_fluid_frame: BetaTrajectoryProfile | None
    budget: EV.ColdThomsonBudget

    def __init__(
        self,
        status,
        certified,
        common_support,
        requested_span,
        segments,
        reasons,
        electron_binding,
        photon_energy,
        electron_temperature,
        source_frame,
        normal_hubble,
        local_ray_rate,
        live_fluid_frame,
        budget,
        *,
        _factory_token=None,
    ):
        if _factory_token is not _CERTIFICATE_FACTORY_TOKEN:
            raise TypeError(
                "TrajectoryColdThomsonCertificate is factory-created; "
                "use certify_cold_thomson_trajectory"
            )
        for name, value in (
            ("status", status),
            ("certified", certified),
            ("common_support", common_support),
            ("requested_span", requested_span),
            ("segments", segments),
            ("reasons", reasons),
            ("electron_binding", electron_binding),
            ("photon_energy", photon_energy),
            ("electron_temperature", electron_temperature),
            ("source_frame", source_frame),
            ("normal_hubble", normal_hubble),
            ("local_ray_rate", local_ray_rate),
            ("live_fluid_frame", live_fluid_frame),
            ("budget", budget),
        ):
            object.__setattr__(self, name, value)
        self.__post_init__()

    def __post_init__(self):
        if not isinstance(self.status, TrajectoryStatus):
            raise TypeError("status must be a TrajectoryStatus")
        if type(self.certified) is not bool:
            raise TypeError("certified must be a bool")
        if not isinstance(self.electron_binding, ElectronScheduleBinding):
            raise TypeError("certificate needs an ElectronScheduleBinding")
        if not isinstance(self.photon_energy, ScalarTrajectoryProfile):
            raise TypeError("certificate needs a photon-energy profile")
        if not isinstance(self.electron_temperature, ScalarTrajectoryProfile):
            raise TypeError("certificate needs an electron-temperature profile")
        if not isinstance(self.source_frame, BetaTrajectoryProfile):
            raise TypeError("certificate needs a source-frame beta profile")
        if not isinstance(self.normal_hubble, ScalarTrajectoryProfile):
            raise TypeError("certificate needs a normal-Hubble profile")
        if not isinstance(self.local_ray_rate, ScalarTrajectoryProfile):
            raise TypeError("certificate needs a local-ray-rate profile")
        if not isinstance(self.budget, EV.ColdThomsonBudget):
            raise TypeError("certificate needs a ColdThomsonBudget")
        if not isinstance(self.segments, tuple) or not self.segments:
            raise ValueError("certificate segments must be a non-empty tuple")
        if not all(isinstance(item, SegmentSupremumWitness) for item in self.segments):
            raise TypeError("certificate segments must be SegmentSupremumWitness values")
        if not isinstance(self.reasons, tuple):
            raise TypeError("certificate reasons must be a tuple")

        requested = tuple(float(value) for value in self.requested_span)
        support = tuple(float(value) for value in self.common_support)
        if len(requested) != 2 or requested[1] <= requested[0]:
            raise ValueError("certificate requested span must be positive and ascending")
        if len(support) != 2 or requested[0] < support[0] or requested[1] > support[1]:
            raise ValueError("certificate requested span exceeds common support")
        if self.segments[0].tau_start != requested[0] or self.segments[-1].tau_end != requested[1]:
            raise ValueError("certificate segments do not cover the requested span")
        for left, right in zip(self.segments[:-1], self.segments[1:]):
            if left.tau_end != right.tau_start:
                raise ValueError("certificate segments are not exactly contiguous")

        expected_status, expected_reasons = _trajectory_outcome(
            self.segments, self.photon_energy.energy_bound_kind
        )
        expected_certified = (
            expected_status is TrajectoryStatus.CERTIFIED_COLD_DELTA_TRAJECTORY
        )
        if self.status is not expected_status:
            raise ValueError("certificate status disagrees with segment witnesses")
        if self.certified is not expected_certified:
            raise ValueError("certificate certified flag disagrees with witnesses")
        if self.reasons != expected_reasons:
            raise ValueError("certificate reasons disagree with segment witnesses")

    @property
    def payload_sha256(self) -> str:
        segment_parts = tuple(
            (
                item.tau_start,
                item.tau_end,
                item.closure,
                item.vacuum,
                item.electron_gamma_max_upper,
                item.electron_gamma_stationary_fractions,
                item.source_gamma_max_upper,
                item.relative_gamma_max_upper,
                item.doppler_max_upper,
                item.source_energy_max_j,
                item.electron_energy_max_j,
                item.x_max_upper,
                item.temperature_max_k,
                item.theta_max_upper,
                item.total_cross_section_relative_deficit_upper,
                item.status,
            )
            for item in self.segments
        )
        return _hash(
            "bass.cold_thomson_trajectory_certificate/v1",
            (
                self.status,
                self.certified,
                self.common_support,
                self.requested_span,
                segment_parts,
                self.reasons,
                self.electron_binding.payload_sha256,
                self.photon_energy.payload_sha256,
                self.electron_temperature.payload_sha256,
                self.source_frame.payload_sha256,
                self.normal_hubble.payload_sha256,
                self.local_ray_rate.payload_sha256,
                None if self.live_fluid_frame is None else self.live_fluid_frame.payload_sha256,
                self.budget.payload_sha256,
                IntegrationOrientation.FUTURE_KINETIC_IVP,
                IntegrationOrientation.PAST_LIGHT_CONE_ACCUMULATION,
                "constants=CODATA2022_SI",
                C_LIGHT_M_S,
                BOLTZMANN_CONSTANT_J_K,
                ELECTRON_REST_ENERGY_J,
            ),
        )

    def authority_metadata(self) -> dict:
        return {
            "schema": "bass.cold_thomson_trajectory_certificate/v1",
            "status": self.status.value,
            "coordinate": "q_hubble_time_tau",
            "coordinate_unit": "dimensionless",
            "future_time_relation": "dt_phys/dtau_Q=1/H_normal",
            "array_order": "strictly_increasing",
            "future_kinetic_derivative": "+nu_tau",
            "past_light_cone_derivative": "-nu_tau",
            "claim_scope": "trajectory_total_cross_section_cold_delta_only",
            "finite_temperature_tail_certified": False,
            "polarized_differential_kernel_certified": False,
            "q_collision_generator_wired": False,
            "production_runtime_wired": False,
            "rust_abi_wired": False,
            "authority_row_promoted": False,
            "certificate_payload_sha256": self.payload_sha256,
        }


def _require_kind(profile, expected):
    if not isinstance(profile, ScalarTrajectoryProfile) or profile.kind is not expected:
        raise TypeError(f"profile must have kind {expected.value}")


def _intersection(supports) -> tuple[float, float]:
    lo = max(float(item[0]) for item in supports)
    hi = min(float(item[1]) for item in supports)
    if lo > hi:
        raise ValueError("trajectory inputs have no closed common support")
    return lo, hi


def _union_nodes(start, end, sources) -> tuple[float, ...]:
    values = {float(start), float(end)}
    for nodes in sources:
        values.update(value for value in nodes if start < value < end)
    return tuple(sorted(values))


def certify_cold_thomson_trajectory(
    *,
    electron_binding,
    photon_energy,
    electron_temperature,
    source_frame,
    normal_hubble,
    local_ray_rate,
    budget,
    tau_start,
    tau_end,
    live_fluid_frame=None,
) -> TrajectoryColdThomsonCertificate:
    """Certify one closed Q-time span without extrapolation or time conversion."""
    if not isinstance(electron_binding, ElectronScheduleBinding):
        raise TypeError("electron_binding must be an ElectronScheduleBinding")
    _require_kind(photon_energy, ScalarProfileKind.PHOTON_ENERGY)
    _require_kind(electron_temperature, ScalarProfileKind.ELECTRON_TEMPERATURE)
    _require_kind(normal_hubble, ScalarProfileKind.NORMAL_HUBBLE)
    _require_kind(local_ray_rate, ScalarProfileKind.LOCAL_RAY_RATE)
    if not isinstance(source_frame, BetaTrajectoryProfile) or source_frame.role is not BetaProfileRole.SOURCE_FRAME:
        raise TypeError("source_frame must be a source-frame beta profile")
    if not isinstance(budget, EV.ColdThomsonBudget):
        raise TypeError("budget must be a ColdThomsonBudget")
    if photon_energy.source_frame != source_frame.frame_id:
        raise ValueError("photon-energy frame must match source-frame profile")

    independent = isinstance(
        electron_binding.schedule, ER.PrescribedIndependentElectronSchedule
    )
    if independent:
        if live_fluid_frame is not None:
            raise ValueError("independent electron closure must not consume live fluid beta")
        closure = "independent"
    else:
        if not isinstance(live_fluid_frame, BetaTrajectoryProfile) or live_fluid_frame.role is not BetaProfileRole.LIVE_FLUID:
            raise ValueError("comoving electron closure requires a live-fluid beta profile")
        closure = "comoving"

    coordinate_hash = electron_binding.coordinate.payload_sha256
    profiles = [
        photon_energy,
        electron_temperature,
        source_frame,
        normal_hubble,
        local_ray_rate,
    ]
    if live_fluid_frame is not None:
        profiles.append(live_fluid_frame)
    if any(item.coordinate.payload_sha256 != coordinate_hash for item in profiles):
        raise ValueError("all trajectory inputs must share one coordinate payload hash")

    supports = [electron_binding.support, *(item.support for item in profiles)]
    common_support = _intersection(supports)
    start = float(tau_start)
    end = float(tau_end)
    if not np.isfinite(start) or not np.isfinite(end) or end <= start:
        raise ValueError(
            "trajectory certification needs a finite positive ascending span; "
            "use the instantaneous E3 authority for one event"
        )
    if start < common_support[0] or end > common_support[1]:
        raise ValueError(
            f"requested span [{start}, {end}] exceeds exact common support {common_support}"
        )

    source_nodes = [electron_binding.view.nodes_ascending]
    source_nodes.extend(item.tau_nodes for item in profiles)
    union = _union_nodes(start, end, source_nodes)
    witnesses = []
    for left, right in zip(union[:-1], union[1:]):
        # Evaluate H and the local ray rate so their positivity/domain checks
        # remain part of every union cell even though E4 does not generate nu.
        _scalar_profile_maximum_bound(normal_hubble, left, right)
        _scalar_profile_maximum_bound(local_ray_rate, left, right)

        numeric_domain_reason = None
        if independent:
            owner = _owner_index(electron_binding.view.nodes_ascending, left)
            if right > electron_binding.view.nodes_ascending[owner + 1]:
                raise ArithmeticError("union segment crossed an electron owner cell")
            current0 = electron_binding.view.number_current_nodes[owner]
            current1 = electron_binding.view.number_current_nodes[owner + 1]
            try:
                gamma_e, stationary = _independent_gamma_bound(
                    current0,
                    current1,
                    electron_binding.view.nodes_ascending[owner],
                    electron_binding.view.nodes_ascending[owner + 1],
                )
            except _NumericDomainUnverified as exc:
                gamma_e, stationary = None, ()
                numeric_domain_reason = str(exc)
            vacuum = gamma_e is None
            if numeric_domain_reason is not None:
                vacuum = False
        else:
            try:
                vacuum = _comoving_density_cell_is_vacuum(
                    electron_binding.view, left, right
                )
            except _NumericDomainUnverified as exc:
                vacuum = False
                numeric_domain_reason = str(exc)
            stationary = ()
            try:
                gamma_e = (
                    None
                    if vacuum or numeric_domain_reason is not None
                    else _beta_profile_gamma_bound(live_fluid_frame, left, right)
                )
            except _NumericDomainUnverified as exc:
                gamma_e = None
                numeric_domain_reason = str(exc)

        temperature_max = _scalar_profile_maximum_bound(
            electron_temperature, left, right
        )
        if numeric_domain_reason is not None:
            witnesses.append(
                SegmentSupremumWitness(
                    left,
                    right,
                    closure,
                    False,
                    None,
                    stationary,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    temperature_max,
                    None,
                    None,
                    "unverified_numeric_domain",
                )
            )
            continue
        if vacuum:
            witnesses.append(
                SegmentSupremumWitness(
                    left,
                    right,
                    closure,
                    True,
                    None,
                    stationary,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    temperature_max,
                    None,
                    None,
                    "vacuum_collision_off",
                )
            )
            continue

        with localcontext() as context:
            context.prec = _DECIMAL_PRECISION
            try:
                gamma_s = _beta_profile_gamma_bound(source_frame, left, right)
            except _NumericDomainUnverified:
                witnesses.append(
                    SegmentSupremumWitness(
                        left,
                        right,
                        closure,
                        False,
                        _upward(gamma_e),
                        stationary,
                        None,
                        None,
                        None,
                        None,
                        None,
                        None,
                        temperature_max,
                        None,
                        None,
                        "unverified_numeric_domain",
                    )
                )
                continue
            relative_gamma, doppler = _relative_doppler_upper(gamma_e, gamma_s)
            gamma_e_up = _upward(gamma_e)
            gamma_s_up = _upward(gamma_s)
            relative_up = _upward(relative_gamma)
            doppler_up = _upward(doppler)
            theta_decimal = (
                _decimal(temperature_max)
                * _decimal(BOLTZMANN_CONSTANT_J_K)
                / _decimal(ELECTRON_REST_ENERGY_J)
            )
            theta_up = _upward(theta_decimal)

            source_energy = None
            electron_energy = None
            x_up = None
            deficit_up = None
            segment_status = "unverified_energy_support"
            if photon_energy.energy_bound_kind is EV.EnergyBoundKind.HARD_FINITE:
                source_energy = _scalar_profile_maximum_bound(
                    photon_energy, left, right
                )
                energy_decimal = _decimal(source_energy) * doppler
                x_decimal = energy_decimal / _decimal(ELECTRON_REST_ENERGY_J)
                electron_energy = _upward(energy_decimal)
                x_up = _upward(x_decimal)
                deficit = EV.klein_nishina_total_deficit(x_up)
                deficit_up = (
                    0.0 if deficit == 0.0
                    else float(np.nextafter(deficit, np.inf))
                )
                if deficit_up > budget.max_total_cross_section_relative_error:
                    segment_status = "rejected_total_cross_section_budget"
                elif theta_up > budget.max_theta_e:
                    segment_status = "rejected_temperature_policy"
                elif temperature_max > 0.0:
                    segment_status = "unverified_finite_temperature_tail"
                else:
                    segment_status = "certified_cold_delta"

        witnesses.append(
            SegmentSupremumWitness(
                left,
                right,
                closure,
                False,
                gamma_e_up,
                stationary,
                gamma_s_up,
                relative_up,
                doppler_up,
                source_energy,
                electron_energy,
                x_up,
                temperature_max,
                theta_up,
                deficit_up,
                segment_status,
            )
        )

    status, reasons = _trajectory_outcome(
        tuple(witnesses), photon_energy.energy_bound_kind
    )
    certified = status is TrajectoryStatus.CERTIFIED_COLD_DELTA_TRAJECTORY
    return TrajectoryColdThomsonCertificate(
        status,
        certified,
        common_support,
        (start, end),
        tuple(witnesses),
        reasons,
        electron_binding,
        photon_energy,
        electron_temperature,
        source_frame,
        normal_hubble,
        local_ray_rate,
        live_fluid_frame,
        budget,
        _factory_token=_CERTIFICATE_FACTORY_TOKEN,
    )


class IntegrationOrientation(enum.Enum):
    FUTURE_KINETIC_IVP = "future_kinetic_ivp"
    PAST_LIGHT_CONE_ACCUMULATION = "past_light_cone_accumulation"


@dataclass(frozen=True, slots=True)
class OpticalDepthIntegral:
    orientation: IntegrationOrientation
    tau_start: float
    tau_end: float
    derivative_sign: int
    coordinate_integral: float
    depth_increment: float
    coordinate_payload_sha256: str
    rate_payload_sha256: str

    def __post_init__(self):
        if not isinstance(self.orientation, IntegrationOrientation):
            raise TypeError("orientation must be an IntegrationOrientation")
        values = (
            self.tau_start,
            self.tau_end,
            self.coordinate_integral,
            self.depth_increment,
        )
        if not all(np.isfinite(float(value)) for value in values):
            raise ValueError("optical-depth integral values must be finite")
        if self.orientation is IntegrationOrientation.FUTURE_KINETIC_IVP:
            if self.tau_end < self.tau_start or self.derivative_sign != 1:
                raise ValueError("future optical-depth integral has invalid orientation")
        elif self.tau_end > self.tau_start or self.derivative_sign != -1:
            raise ValueError("past optical-depth integral has invalid orientation")
        if self.coordinate_integral != (
            abs(self.coordinate_integral)
            if self.tau_end >= self.tau_start
            else -abs(self.coordinate_integral)
        ):
            raise ValueError("coordinate integral sign disagrees with traversal")
        if self.depth_increment != self.derivative_sign * self.coordinate_integral:
            raise ValueError("depth increment disagrees with derivative orientation")
        if self.depth_increment < 0.0:
            raise ValueError("depth increment must be non-negative")
        if _SHA256.fullmatch(str(self.coordinate_payload_sha256)) is None:
            raise ValueError("coordinate payload hash must be lowercase SHA-256")
        if _SHA256.fullmatch(str(self.rate_payload_sha256)) is None:
            raise ValueError("rate payload hash must be lowercase SHA-256")


def _piecewise_linear_integral(profile, lo, hi) -> Decimal:
    knots = _union_nodes(lo, hi, [profile.tau_nodes])
    with localcontext() as context:
        context.prec = _DECIMAL_PRECISION
        total = Decimal(0)
        for left, right in zip(knots[:-1], knots[1:]):
            width = _decimal(right) - _decimal(left)
            values = _decimal(profile.at(left)) + _decimal(profile.at(right))
            total += width * values / Decimal(2)
        return total


def integrate_optical_depth(
    local_ray_rate,
    tau_start,
    tau_end,
    orientation,
) -> OpticalDepthIntegral:
    """Integrate one non-negative local rate with a typed orientation.

    ``coordinate_integral`` is the ordinary oriented integral
    ``integral_start^end nu_tau d tau``.  Multiplication by the declared RHS
    sign yields the non-negative ``depth_increment`` in both supported roles.
    """
    _require_kind(local_ray_rate, ScalarProfileKind.LOCAL_RAY_RATE)
    if not isinstance(orientation, IntegrationOrientation):
        raise TypeError("orientation must be an IntegrationOrientation")
    start = float(tau_start)
    end = float(tau_end)
    if not np.isfinite(start) or not np.isfinite(end):
        raise ValueError("integration endpoints must be finite")
    lo, hi = local_ray_rate.support
    if min(start, end) < lo or max(start, end) > hi:
        raise ValueError("integration span exceeds exact local-rate support")
    if orientation is IntegrationOrientation.FUTURE_KINETIC_IVP:
        if end < start:
            raise ValueError("future kinetic traversal requires tau_start <= tau_end")
        derivative_sign = 1
    else:
        if end > start:
            raise ValueError("past-light-cone traversal requires tau_start >= tau_end")
        derivative_sign = -1

    area = _piecewise_linear_integral(local_ray_rate, min(start, end), max(start, end))
    area_up = _upward(area) if area != 0 else 0.0
    coordinate_integral = area_up if end >= start else -area_up
    depth = derivative_sign * coordinate_integral
    if depth < 0:
        raise ArithmeticError("typed optical-depth increment became negative")
    return OpticalDepthIntegral(
        orientation,
        start,
        end,
        derivative_sign,
        coordinate_integral,
        depth,
        local_ray_rate.coordinate.payload_sha256,
        local_ray_rate.payload_sha256,
    )


__all__ = [
    "BetaProfileRole",
    "BetaTrajectoryProfile",
    "ElectronScheduleBinding",
    "IntegrationOrientation",
    "OpticalDepthIntegral",
    "QHubbleTimeCoordinate",
    "ScalarProfileKind",
    "ScalarTrajectoryProfile",
    "SegmentSupremumWitness",
    "TrajectoryColdThomsonCertificate",
    "TrajectoryStatus",
    "certify_cold_thomson_trajectory",
    "integrate_optical_depth",
]
