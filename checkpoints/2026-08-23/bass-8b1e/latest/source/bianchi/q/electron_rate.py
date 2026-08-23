"""Cold-Thomson relative-flux and prescribed electron schedules.

This is a bounded collision-context authority.  It deliberately does not wire
the result into ``Collision.v_b``, a solver loop, or the Rust ABI.

Conventions
-----------

* metric ``(-,+,+,+)``;
* ``n_e_free`` is electron-rest-frame proper density in SI ``m^-3``;
* directions are photon propagation directions in the named observer frame;
* ``rate_per_fluid_time_s`` uses fluid-observer ray time;
* ``rate_per_normal_time_s`` uses normal-congruence ray time;
* only the normal-time rate may be divided by the Q solver's normal-frame
  Hubble scalar.

For a future-directed ray,

``d optical_depth / dt_source = n_e* sigma_T c (E_e/E_source)``.

The electron energy ratio is the relative-flux factor and occurs exactly once.
It is not an intensity ``D^4`` or solid-angle ``D^-2`` transformation.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import re
from typing import Iterable

import numpy as np

from bianchi.q.electron import (
    C_LIGHT_M_S,
    ColdElectronTestField,
    normalized_four_velocity,
    transform_photon,
)
from bianchi.thermo.history_api import C_CM_S, SIGMA_T_CM2


CM2_TO_M2 = 1.0e-4
CM3_TO_M3 = 1.0e6
M3_TO_CM3 = 1.0e-6
SIGMA_T_M2 = SIGMA_T_CM2 * CM2_TO_M2
_SHA256 = re.compile(r"[0-9a-f]{64}")


class VacuumElectronFrameError(ValueError):
    """Raised when a representative-dependent electron frame is requested at vacuum."""


def _finite_nonnegative(value, name: str) -> tuple[np.ndarray, bool]:
    out = np.asarray(value, dtype=float)
    scalar = out.ndim == 0
    if not np.isfinite(out).all() or np.any(out < 0.0):
        raise ValueError(f"{name} must be finite and non-negative")
    return out, scalar


def density_cm3_to_m3(value):
    """Convert an electron **proper** density from ``cm^-3`` to ``m^-3``.

    This is not an ionization-history frame adapter.  Generic H2 callers must
    not pass a fluid-frame density here and then apply a second Lorentz factor.
    """
    density, scalar = _finite_nonnegative(value, "proper density in cm^-3")
    with np.errstate(over="ignore", invalid="ignore"):
        out = density * CM3_TO_M3
    if not np.isfinite(out).all():
        raise ValueError("proper-density cm^-3 to m^-3 conversion overflowed")
    return float(out) if scalar else out


def density_m3_to_cm3(value):
    """Convert an electron proper density from ``m^-3`` to ``cm^-3``."""
    density, scalar = _finite_nonnegative(value, "proper density in m^-3")
    with np.errstate(over="ignore", invalid="ignore"):
        out = density * M3_TO_CM3
    if not np.isfinite(out).all():
        raise ValueError("proper-density m^-3 to cm^-3 conversion overflowed")
    return float(out) if scalar else out


def _directions(value) -> tuple[np.ndarray, tuple[int, ...], bool]:
    out = np.asarray(value, dtype=float)
    single = out.ndim == 1
    if out.ndim < 1 or out.shape[-1] != 3:
        raise ValueError(f"direction must have final shape 3, got {out.shape}")
    if not np.isfinite(out).all():
        raise ValueError("direction must be finite")
    flat = out.reshape(-1, 3)
    norms = np.linalg.norm(flat, axis=1)
    if np.any(np.abs(norms - 1.0) > 2.0e-12):
        raise ValueError("photon directions must be unit vectors")
    return out, out.shape[:-1], single


def _zeros_for_directions(leading: tuple[int, ...], single: bool):
    out = np.zeros(leading, dtype=float)
    return float(out) if single else out


def _positive_hubble(value: float) -> float:
    out = float(value)
    if not np.isfinite(out) or out <= 0.0:
        raise ValueError("H_normal_s must be finite and positive")
    return out


@dataclass(frozen=True, slots=True)
class ElectronCollisionContext:
    """Direction-dependent opacity of one instantaneous electron state."""

    electron: ColdElectronTestField

    def __post_init__(self):
        if not isinstance(self.electron, ColdElectronTestField):
            raise TypeError("electron must be a ColdElectronTestField")

    def relative_flux_factor(self, direction_fluid, beta_fluid):
        """Return ``D_{e<-f}=E_e/E_f`` for a non-vacuum state.

        At exact vacuum the electron velocity is quotiented, hence a Doppler
        factor depending on a retained representative is not a physical
        collision-context observable.
        """
        _directions(direction_fluid)
        if self.electron.n_e_free == 0.0:
            raise VacuumElectronFrameError(
                "electron relative-flux factor is undefined on the vacuum quotient"
            )
        _, _, doppler = self.electron.fluid_to_electron_photon(
            1.0, direction_fluid, beta_fluid
        )
        return doppler

    def rest_opacity_per_second(self) -> float:
        """Return the scalar electron-rest opacity ``n_e* sigma_T c``.

        This is the only valid input to a consumer that applies the
        relative-flux factor internally (for example
        ``matter.collision_moving.collision_rate_density``).  It contains no
        observer-direction Doppler factor.
        """
        if self.electron.n_e_free == 0.0:
            return 0.0
        return float(
            self.electron.n_e_free * SIGMA_T_M2 * self.electron.c_m_s
        )

    def rate_per_fluid_time_s(self, direction_fluid, beta_fluid):
        """Return ``d optical_depth/dt_f`` in ``s^-1``.

        ``t_f`` is local fluid-observer ray time, not coordinate time and not
        the Q solver's normal-congruence time.
        """
        _, leading, single = _directions(direction_fluid)
        # Validate the named observer even though its relation to the vacuum
        # electron representative is quotiented.
        normalized_four_velocity(beta_fluid)
        if self.electron.n_e_free == 0.0:
            return _zeros_for_directions(leading, single)
        doppler = self.relative_flux_factor(direction_fluid, beta_fluid)
        return self.rest_opacity_per_second() * doppler

    def rate_per_normal_time_s(self, direction_normal):
        """Return ``d optical_depth/dt_normal`` in ``s^-1``.

        This accepts a direction in the normal tetrad directly.  It does not
        reinterpret the normal observer as the fluid observer, so a comoving
        electron state may still have a direction-dependent normal-time rate.
        """
        _, leading, single = _directions(direction_normal)
        if self.electron.n_e_free == 0.0:
            return _zeros_for_directions(leading, single)
        _, _, doppler = transform_photon(
            1.0, direction_normal, np.zeros(3), self.electron.beta_normal
        )
        return self.rest_opacity_per_second() * doppler

    def rate_per_normal_hubble_time(self, direction_normal, H_normal_s):
        """Return dimensionless ``nu_tau=(d optical_depth/dt_normal)/H_normal``."""
        hubble = _positive_hubble(H_normal_s)
        return self.rate_per_normal_time_s(direction_normal) / hubble

    def authority_metadata(self) -> dict:
        return {
            "schema": "bass.electron_collision_context/v1",
            "density_semantics": "electron_rest_frame_proper_density",
            "density_unit": "m^-3",
            "cross_section_owner": "bianchi.thermo.history_api.SIGMA_T_CM2",
            "cross_section_m2": SIGMA_T_M2,
            "fluid_rate": "n_e* sigma_T c D_e<-f",
            "normal_rate": "n_e* sigma_T c D_e<-normal",
            "solver_hubble_rate": "normal_rate/H_normal",
            "relative_flux_power": 1,
            "vacuum_policy": "collision_off_velocity_quotient",
            "cold_thomson_status": (
                "DECLARED_COLD_THOMSON_ASSUMPTION / ENERGY_DOMAIN_UNVERIFIED"
            ),
            "production_runtime_wired": False,
            "authority_row_promoted": False,
        }


@dataclass(frozen=True, slots=True)
class ElectronScheduleProvenance:
    """Required upstream locator for a prescribed electron schedule."""

    source_id: str
    source_sha256: str

    def __post_init__(self):
        source_id = str(self.source_id).strip()
        source_hash = str(self.source_sha256)
        if not source_id:
            raise ValueError("schedule source_id must be non-empty")
        if _SHA256.fullmatch(source_hash) is None:
            raise ValueError("schedule source_sha256 must be lowercase 64-hex")
        object.__setattr__(self, "source_id", source_id)


@dataclass(frozen=True, slots=True)
class ElectronScheduleTrajectoryView:
    """Immutable, canonical read seam for bounded trajectory authorities.

    The view exposes the interpolation owner rather than resampling it.  An
    independent schedule supplies its number-current knots; a comoving
    schedule supplies only proper-density knots and therefore cannot be
    mistaken for an independently prescribed electron velocity.
    """

    coordinate_kind: str
    nodes_ascending: tuple[float, ...]
    interpolation: str
    number_current_nodes: tuple[tuple[float, float, float, float], ...] | None
    density_nodes_m3: tuple[float, ...] | None
    source_id: str
    source_sha256: str
    schedule_payload_sha256: str
    c_m_s: float


def _schedule_arrays(tau_nodes, density_m3):
    tau = np.asarray(tau_nodes, dtype=float)
    density, _ = _finite_nonnegative(density_m3, "n_e_free")
    if tau.ndim != 1 or tau.size < 2:
        raise ValueError("schedule tau nodes must be a one-dimensional array of length >= 2")
    if density.shape != tau.shape:
        raise ValueError("schedule density must have the same shape as tau nodes")
    if not np.isfinite(tau).all() or not np.all(np.diff(tau) > 0.0):
        raise ValueError("schedule tau nodes must be finite and strictly increasing")
    density = np.array(density, copy=True)
    # IEEE -0.0 and +0.0 are the same vacuum density.  Canonicalize before
    # payload hashing so a nonphysical sign bit cannot split provenance.
    density[density == 0.0] = 0.0
    return np.array(tau, copy=True), density


def _provenance(value) -> ElectronScheduleProvenance:
    if not isinstance(value, ElectronScheduleProvenance):
        raise TypeError("provenance must be an ElectronScheduleProvenance")
    return value


def _positive_c(value) -> float:
    out = float(value)
    if not np.isfinite(out) or out <= 0.0:
        raise ValueError("c_m_s must be finite and positive")
    return out


def _payload_hash(kind: str, arrays: Iterable[np.ndarray], c_m_s: float) -> str:
    digest = hashlib.sha256()
    digest.update(b"bass.electron_schedule_payload/v1\0")
    digest.update(kind.encode("ascii") + b"\0")
    digest.update(b"coordinate=hubble_time_tau\0")
    digest.update(b"tetrad_gauge=declared_normal_tetrad\0")
    digest.update(b"density=electron_proper_m^-3\0")
    for value in arrays:
        canonical = np.ascontiguousarray(np.asarray(value, dtype="<f8"))
        digest.update(str(canonical.shape).encode("ascii") + b"\0")
        digest.update(canonical.tobytes())
    digest.update(np.asarray([c_m_s], dtype="<f8").tobytes())
    return digest.hexdigest()


def _sample_index_weight(tau_nodes: np.ndarray, tau: float) -> tuple[int, float]:
    query = float(tau)
    if not np.isfinite(query):
        raise ValueError("schedule tau query must be finite")
    lo, hi = float(tau_nodes[0]), float(tau_nodes[-1])
    if query < lo or query > hi:
        raise ValueError(f"tau={query} is outside closed schedule support [{lo}, {hi}]")
    if query == hi:
        return len(tau_nodes) - 2, 1.0
    index = int(np.searchsorted(tau_nodes, query, side="right") - 1)
    index = max(index, 0)
    weight = (query - tau_nodes[index]) / (tau_nodes[index + 1] - tau_nodes[index])
    return index, float(weight)


def _validate_span(tau_nodes: np.ndarray, start: float, end: float):
    first = float(start)
    last = float(end)
    if not np.isfinite(first) or not np.isfinite(last) or last < first:
        raise ValueError("schedule span must be finite and ordered")
    lo, hi = float(tau_nodes[0]), float(tau_nodes[-1])
    if first < lo or last > hi:
        raise ValueError(f"requested span [{first}, {last}] exceeds [{lo}, {hi}]")
    return first, last


class PrescribedIndependentElectronSchedule:
    """Finite-domain H2 schedule, linear in ``N_e^A=n_e* U_e^A``.

    Components at all knots are declared in the project's normal-tetrad gauge.
    Linear current interpolation is a frozen modeling choice: it preserves the
    vacuum quotient and future timelikeness, but it is gauge dependent and may
    make the reconstructed proper density exceed both endpoint densities for
    counter-streaming endpoints.  It is not an AD/JVP or residual-U(1) claim.
    """

    def __init__(
        self,
        tau_nodes,
        n_e_free_m3,
        beta_normal,
        *,
        provenance: ElectronScheduleProvenance,
        c_m_s: float = C_LIGHT_M_S,
        _input_density_unit: str = "m^-3",
    ):
        tau, density = _schedule_arrays(tau_nodes, n_e_free_m3)
        beta = np.array(beta_normal, dtype=float, copy=True)
        if beta.shape != (len(tau), 3):
            raise ValueError("beta_normal must have shape (number_of_tau_nodes, 3)")
        if not np.isfinite(beta).all():
            raise ValueError("schedule beta_normal must be finite")
        # Quotient vacuum representatives from both dynamics and payload
        # identity.  Two tables that differ only by beta where n_e*=0 are the
        # same prescribed physical current.
        beta[density == 0.0] = 0.0
        velocities = np.asarray([normalized_four_velocity(row) for row in beta])
        current = density[:, None] * velocities
        # Erase all exact-vacuum representatives before any interpolation.
        current[density == 0.0] = 0.0
        for value in (tau, density, beta, current):
            value.setflags(write=False)
        self._tau = tau
        self._density = density
        self._beta = beta
        self._current = current
        self.provenance = _provenance(provenance)
        self.c_m_s = _positive_c(c_m_s)
        self.input_density_unit = str(_input_density_unit)
        self.payload_sha256 = _payload_hash(
            "independent_linear_number_current_v1", (tau, density, beta), self.c_m_s
        )

    @classmethod
    def from_proper_cm3(
        cls,
        tau_nodes,
        n_e_proper_cm3,
        beta_normal,
        *,
        provenance: ElectronScheduleProvenance,
        c_m_s: float = C_LIGHT_M_S,
    ):
        """Build from **electron proper** density expressed in ``cm^-3``.

        This does not adapt generic legacy ``x_e n_H`` fluid-frame history to
        H2.  Such a density-frame adapter remains deliberately unimplemented.
        """
        return cls(
            tau_nodes,
            density_cm3_to_m3(n_e_proper_cm3),
            beta_normal,
            provenance=provenance,
            c_m_s=c_m_s,
            _input_density_unit="proper_cm^-3->m^-3",
        )

    @property
    def support(self):
        return float(self._tau[0]), float(self._tau[-1])

    def trajectory_view(self) -> ElectronScheduleTrajectoryView:
        """Return immutable knots without changing interpolation semantics."""
        if not np.isfinite(self._current).all():
            raise ValueError("electron number-current knots must be finite")
        return ElectronScheduleTrajectoryView(
            coordinate_kind="q_hubble_time_tau",
            nodes_ascending=tuple(float(value) for value in self._tau),
            interpolation="linear_number_current_v1",
            number_current_nodes=tuple(
                tuple(float(component) for component in row)
                for row in self._current
            ),
            density_nodes_m3=None,
            source_id=self.provenance.source_id,
            source_sha256=self.provenance.source_sha256,
            schedule_payload_sha256=self.payload_sha256,
            c_m_s=self.c_m_s,
        )

    def validate_span(self, start, end):
        return _validate_span(self._tau, start, end)

    def at(self, tau) -> ColdElectronTestField:
        if np.ndim(tau) != 0:
            raise ValueError("schedule at() accepts one scalar tau")
        index, weight = _sample_index_weight(self._tau, tau)
        current = (1.0 - weight) * self._current[index] + weight * self._current[index + 1]
        if np.array_equal(current, np.zeros(4)):
            return ColdElectronTestField.independent(
                0.0, (0.0, 0.0, 0.0), c_m_s=self.c_m_s
            )
        temporal = float(current[0])
        spatial = np.asarray(current[1:], dtype=float)
        if not np.isfinite(current).all() or temporal <= 0.0:
            raise ValueError("interpolated electron current is not finite future-directed")
        spatial_norm = float(np.linalg.norm(spatial))
        norm_squared = (temporal - spatial_norm) * (temporal + spatial_norm)
        tolerance = 64.0 * np.finfo(float).eps * temporal * temporal
        if norm_squared < -tolerance:
            raise ValueError("interpolated electron current is spacelike")
        if norm_squared <= 0.0:
            raise ValueError("positive interpolated electron current became null numerically")
        beta = spatial / temporal
        if float(beta @ beta) >= 1.0:
            raise ValueError("interpolated electron beta is not subluminal")
        density = float(np.sqrt(norm_squared))
        return ColdElectronTestField.independent(
            density, beta, c_m_s=self.c_m_s
        )

    def authority_metadata(self) -> dict:
        return {
            "schema": "bass.prescribed_independent_electron_schedule/v1",
            "coordinate": "hubble_time_tau",
            "tau_origin": "caller_declared_q_solver_tau_origin",
            "tetrad_gauge": "declared_normal_tetrad_components",
            "interpolation": "linear_number_current",
            "interpolation_version": 1,
            "density_semantics": "electron_rest_frame_proper_density",
            "density_unit": "m^-3",
            "input_density_unit": self.input_density_unit,
            "vacuum_policy": "collision_off_velocity_quotient",
            "source_id": self.provenance.source_id,
            "source_sha256": self.provenance.source_sha256,
            "payload_sha256": self.payload_sha256,
            "legacy_history_density_adapter": False,
            "residual_u1_descended": False,
            "ad_jvp_certified": False,
            "validity_boundary": (
                "DECLARED_COLD_THOMSON_ASSUMPTION / ENERGY_DOMAIN_UNVERIFIED; "
                "electron-frame photon-energy support is not certified, so "
                "Klein-Nishina/recoil corrections remain outside this gate"
            ),
            "production_runtime_wired": False,
            "authority_row_promoted": False,
        }


class PrescribedComovingElectronSchedule:
    """Finite-domain H1 density schedule evaluated with the live fluid beta.

    No independent electron velocity is interpolated.  Positive-density calls
    construct ``u_e=u_fluid`` exactly.  At exact vacuum the equality constraint
    is vacuous and the canonical zero-current independent state is returned.
    """

    def __init__(
        self,
        tau_nodes,
        n_e_free_m3,
        *,
        provenance: ElectronScheduleProvenance,
        c_m_s: float = C_LIGHT_M_S,
        _input_density_unit: str = "m^-3",
    ):
        tau, density = _schedule_arrays(tau_nodes, n_e_free_m3)
        tau.setflags(write=False)
        density.setflags(write=False)
        self._tau = tau
        self._density = density
        self.provenance = _provenance(provenance)
        self.c_m_s = _positive_c(c_m_s)
        self.input_density_unit = str(_input_density_unit)
        self.payload_sha256 = _payload_hash(
            "comoving_linear_proper_density_v1", (tau, density), self.c_m_s
        )

    @classmethod
    def from_proper_cm3(
        cls,
        tau_nodes,
        n_e_proper_cm3,
        *,
        provenance: ElectronScheduleProvenance,
        c_m_s: float = C_LIGHT_M_S,
    ):
        return cls(
            tau_nodes,
            density_cm3_to_m3(n_e_proper_cm3),
            provenance=provenance,
            c_m_s=c_m_s,
            _input_density_unit="proper_cm^-3->m^-3",
        )

    @property
    def support(self):
        return float(self._tau[0]), float(self._tau[-1])

    def trajectory_view(self) -> ElectronScheduleTrajectoryView:
        """Return density knots; live fluid velocity remains a separate input."""
        return ElectronScheduleTrajectoryView(
            coordinate_kind="q_hubble_time_tau",
            nodes_ascending=tuple(float(value) for value in self._tau),
            interpolation="linear_proper_density_live_fluid_beta",
            number_current_nodes=None,
            density_nodes_m3=tuple(float(value) for value in self._density),
            source_id=self.provenance.source_id,
            source_sha256=self.provenance.source_sha256,
            schedule_payload_sha256=self.payload_sha256,
            c_m_s=self.c_m_s,
        )

    def validate_span(self, start, end):
        return _validate_span(self._tau, start, end)

    def at(self, tau, *, beta_fluid) -> ColdElectronTestField:
        if np.ndim(tau) != 0:
            raise ValueError("schedule at() accepts one scalar tau")
        index, weight = _sample_index_weight(self._tau, tau)
        density = float(
            (1.0 - weight) * self._density[index] + weight * self._density[index + 1]
        )
        if density == 0.0:
            return ColdElectronTestField.independent(
                0.0, (0.0, 0.0, 0.0), c_m_s=self.c_m_s
            )
        return ColdElectronTestField.comoving(
            density, beta_fluid, c_m_s=self.c_m_s
        )

    def authority_metadata(self) -> dict:
        return {
            "schema": "bass.prescribed_comoving_electron_schedule/v1",
            "coordinate": "hubble_time_tau",
            "tau_origin": "caller_declared_q_solver_tau_origin",
            "interpolation": "linear_proper_density_live_fluid_beta",
            "density_semantics": "electron_proper_equals_fluid_frame_on_H1",
            "density_unit": "m^-3",
            "input_density_unit": self.input_density_unit,
            "positive_density_closure": "u_e_equals_live_u_fluid_exactly",
            "vacuum_closure": "undefined_on_velocity_quotient",
            "vacuum_policy": "collision_off_velocity_quotient",
            "source_id": self.provenance.source_id,
            "source_sha256": self.provenance.source_sha256,
            "payload_sha256": self.payload_sha256,
            "legacy_history_density_adapter": False,
            "ad_jvp_certified": False,
            "production_runtime_wired": False,
            "authority_row_promoted": False,
        }


__all__ = [
    "C_CM_S",
    "CM2_TO_M2",
    "CM3_TO_M3",
    "ElectronCollisionContext",
    "ElectronScheduleProvenance",
    "ElectronScheduleTrajectoryView",
    "M3_TO_CM3",
    "PrescribedComovingElectronSchedule",
    "PrescribedIndependentElectronSchedule",
    "SIGMA_T_CM2",
    "SIGMA_T_M2",
    "VacuumElectronFrameError",
    "density_cm3_to_m3",
    "density_m3_to_cm3",
]
