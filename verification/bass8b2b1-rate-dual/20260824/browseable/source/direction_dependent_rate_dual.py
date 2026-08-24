"""BASS-8B.2B.1 direction-dependent rate/dual binding."""
from __future__ import annotations

from dataclasses import dataclass
import math
import re
from typing import Any

import numpy as np

from electron_state_binding import DerivativeSide, HashRef
from generic_vector_paired_carrier import (
    collision,
    left_functional as carrier_left_functional,
    moving_projector,
    paired_from_rest,
    wrong_left_without_direction_factor,
)

C_LIGHT_M_S = 299_792_458.0
SIGMA_T_M2 = 6.6524587e-29
E2_ELECTRON_RATE_OWNER_SHA256 = "27fe46756023380078fc503e8fe2ea5e976504314e206f55613d06af61f4be1a"
BASS8B2A_STATE_JET_SOURCE_SHA256 = (
    "31ff41590b3083c825a1faa7efd04bfa168d0a9ae6add08ba3f6c5c1a444db62"
)
BASS8B2B0_CARRIER_SOURCE_SHA256 = "0a46342eefce177c4bd1a41fd24bb95ea2bf964f2efdc06eb7836940eef3530f"
_SHA256 = re.compile(r"[0-9a-f]{64}\Z")


def _finite(value: Any, name: str) -> float:
    out = float(value)
    if not math.isfinite(out):
        raise ValueError(f"{name} must be finite")
    return out


def _sha(value: Any, name: str) -> str:
    out = str(value)
    if _SHA256.fullmatch(out) is None:
        raise ValueError(f"{name} must be lowercase 64-hex SHA-256")
    return out


def _readonly_array(value: Any) -> np.ndarray:
    out = np.array(value, dtype=float, copy=True)
    out.setflags(write=False)
    return out


@dataclass(frozen=True, slots=True)
class RateDualAuthority:
    e2_rate_owner_sha256: str
    electron_state_jet_source_sha256: str
    carrier_source_sha256: str
    sigma_t_m2: float
    c_m_s: float
    frame_map: str = "electron_from_normal"
    time_variable: str = "q_hubble_time_tau"

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "e2_rate_owner_sha256",
            _sha(self.e2_rate_owner_sha256, "e2_rate_owner_sha256"),
        )
        object.__setattr__(
            self,
            "electron_state_jet_source_sha256",
            _sha(
                self.electron_state_jet_source_sha256,
                "electron_state_jet_source_sha256",
            ),
        )
        object.__setattr__(
            self,
            "carrier_source_sha256",
            _sha(self.carrier_source_sha256, "carrier_source_sha256"),
        )
        if _finite(self.sigma_t_m2, "sigma_t_m2") <= 0.0:
            raise ValueError("sigma_t_m2 must be positive")
        if _finite(self.c_m_s, "c_m_s") <= 0.0:
            raise ValueError("c_m_s must be positive")
        if self.frame_map != "electron_from_normal":
            raise ValueError("rate frame must be electron_from_normal")
        if self.time_variable != "q_hubble_time_tau":
            raise ValueError("time variable must be q_hubble_time_tau")

    @classmethod
    def frozen_project_authority(cls) -> "RateDualAuthority":
        return cls(
            E2_ELECTRON_RATE_OWNER_SHA256,
            BASS8B2A_STATE_JET_SOURCE_SHA256,
            BASS8B2B0_CARRIER_SOURCE_SHA256,
            SIGMA_T_M2,
            C_LIGHT_M_S,
        )


@dataclass(frozen=True, slots=True)
class NormalHubbleRateJet:
    tau: float
    H_normal_s: float
    dH_normal_s_dtau: float
    derivative_side: DerivativeSide
    coordinate_sha256: str
    provenance: HashRef

    def __post_init__(self) -> None:
        object.__setattr__(self, "tau", _finite(self.tau, "tau"))
        H = _finite(self.H_normal_s, "H_normal_s")
        if H <= 0.0:
            raise ValueError("H_normal_s must be positive")
        object.__setattr__(self, "H_normal_s", H)
        object.__setattr__(
            self,
            "dH_normal_s_dtau",
            _finite(self.dH_normal_s_dtau, "dH_normal_s_dtau"),
        )
        if not isinstance(self.derivative_side, DerivativeSide):
            raise TypeError("derivative_side must be a DerivativeSide")
        object.__setattr__(
            self,
            "coordinate_sha256",
            _sha(self.coordinate_sha256, "coordinate_sha256"),
        )
        if not isinstance(self.provenance, HashRef):
            raise TypeError("provenance must be a HashRef")


class VacuumProjectorUndefinedError(RuntimeError):
    """Raised when a nontrivial collision projector is requested at exact vacuum."""


@dataclass(frozen=True, slots=True)
class CollisionOffRateDualBinding:
    tau: float
    derivative_side: DerivativeSide
    authority: RateDualAuthority
    coordinate_sha256: str
    electron_binding_sha256: str
    electron_schedule_payload_sha256: str
    collision_off_reason: str
    hubble_provenance: HashRef
    nu_tau: np.ndarray
    collision_off: bool = True
    beta: None = None

    def apply_full_generator(self, y: np.ndarray) -> np.ndarray:
        return np.zeros_like(np.asarray(y, dtype=float))

    def left_functional(self, y: np.ndarray) -> float:
        raise VacuumProjectorUndefinedError(
            "the electron-frame left functional is undefined on the vacuum quotient"
        )

    def project(self, y: np.ndarray) -> np.ndarray:
        raise VacuumProjectorUndefinedError(
            "the nontrivial collision projector is not identifiable at exact vacuum"
        )

    def authority_metadata(self) -> dict[str, Any]:
        return {
            "schema": "bass.direction_dependent_rate_dual/v1",
            "metric_signature": "(-,+,+,+)",
            "time_variable": self.authority.time_variable,
            "frame_map": self.authority.frame_map,
            "e2_rate_owner_sha256": self.authority.e2_rate_owner_sha256,
            "electron_state_jet_source_sha256": self.authority.electron_state_jet_source_sha256,
            "carrier_source_sha256": self.authority.carrier_source_sha256,
            "coordinate_sha256": self.coordinate_sha256,
            "electron_binding_sha256": self.electron_binding_sha256,
            "electron_schedule_payload_sha256": self.electron_schedule_payload_sha256,
            "hubble_provenance": {
                "source_id": self.hubble_provenance.source_id,
                "source_sha256": self.hubble_provenance.source_sha256,
            },
            "derivative_side": self.derivative_side.value,
            "collision_off_reason": self.collision_off_reason,
            "collision_off_velocity_quotient": True,
            "direction_dependent_rate_dual_bound": False,
            "moving_bundle_differential_bound": False,
            "projector_left_full_audit_bound": False,
            "authority_row_promoted": False,
            "production_runtime_wired": False,
        }


@dataclass(frozen=True, slots=True)
class RateDualBinding:
    tau: float
    derivative_side: DerivativeSide
    authority: RateDualAuthority
    coordinate_sha256: str
    electron_binding_sha256: str
    electron_schedule_payload_sha256: str
    electron_closure: str
    hubble_provenance: HashRef
    proper_density_m3: float
    dproper_density_dtau: float
    H_normal_s: float
    dH_normal_s_dtau: float
    gamma: float
    dgamma_dtau: float
    e_normal: np.ndarray
    de_normal_dtau: np.ndarray
    w_normal: np.ndarray
    beta: np.ndarray
    dbeta_dtau: np.ndarray
    doppler: np.ndarray
    ddoppler_dtau: np.ndarray
    direction_factor: np.ndarray
    ddirection_factor_dtau: np.ndarray
    scalar_opacity_per_hubble: float
    dscalar_opacity_per_hubble_dtau: float
    nu_tau: np.ndarray
    dnu_tau_dtau: np.ndarray
    shape_left_node_weights: np.ndarray
    full_left_node_weights: np.ndarray
    global_generator_scale: float
    dglobal_generator_scale_dtau: float
    collision_off: bool = False

    def apply_full_generator(self, y: np.ndarray) -> np.ndarray:
        return self.global_generator_scale * collision(
            self.e_normal, self.w_normal, self.beta, y
        )

    def left_functional(self, y: np.ndarray) -> float:
        return carrier_left_functional(
            self.e_normal, self.w_normal, self.beta, y
        )

    def project(self, y: np.ndarray) -> np.ndarray:
        return moving_projector(
            self.e_normal, self.w_normal, self.beta, y
        )

    def authority_metadata(self) -> dict[str, Any]:
        return {
            "schema": "bass.direction_dependent_rate_dual/v1",
            "metric_signature": "(-,+,+,+)",
            "time_variable": self.authority.time_variable,
            "frame_map": self.authority.frame_map,
            "e2_rate_owner_sha256": self.authority.e2_rate_owner_sha256,
            "electron_state_jet_source_sha256": self.authority.electron_state_jet_source_sha256,
            "carrier_source_sha256": self.authority.carrier_source_sha256,
            "coordinate_sha256": self.coordinate_sha256,
            "electron_binding_sha256": self.electron_binding_sha256,
            "electron_schedule_payload_sha256": self.electron_schedule_payload_sha256,
            "electron_closure": self.electron_closure,
            "hubble_provenance": {
                "source_id": self.hubble_provenance.source_id,
                "source_sha256": self.hubble_provenance.source_sha256,
            },
            "derivative_side": self.derivative_side.value,
            "direction_dependent_rate_dual_bound": True,
            "global_scalar_opacity_cancels_from_normalized_projector": True,
            "direction_factor_remains_in_left_dual": True,
            "moving_bundle_differential_bound": False,
            "projector_left_full_audit_bound": False,
            "authority_row_promoted": False,
            "production_runtime_wired": False,
        }

    def rate_mutations(self) -> dict[str, np.ndarray]:
        alpha = self.scalar_opacity_per_hubble
        return {
            "omit_gamma": alpha * self.direction_factor,
            "omit_direction_factor": np.full_like(
                self.nu_tau, alpha * self.gamma
            ),
            "double_doppler": alpha * self.doppler**2,
        }

    def left_without_direction_factor(self, y: np.ndarray) -> float:
        return wrong_left_without_direction_factor(
            self.e_normal, self.w_normal, y
        )

    @staticmethod
    def _node_scale(y: np.ndarray, factor: np.ndarray) -> np.ndarray:
        values = np.asarray(y, dtype=float).reshape(-1, 9)
        if len(values) != len(factor):
            raise ValueError("state size does not match the angular carrier")
        return (values * np.asarray(factor)[:, None]).ravel()

    def apply_mutated_generator(self, y: np.ndarray, mutation: str) -> np.ndarray:
        shape_with_q = collision(self.e_normal, self.w_normal, self.beta, y)
        if mutation == "omit_gamma":
            return (self.global_generator_scale / self.gamma) * shape_with_q
        if mutation == "omit_direction_factor":
            shape_without_q = self._node_scale(
                shape_with_q, 1.0 / self.direction_factor
            )
            return self.global_generator_scale * shape_without_q
        if mutation == "double_doppler":
            return self._node_scale(
                self.global_generator_scale * shape_with_q, self.doppler
            )
        raise ValueError(f"unknown hostile mutation: {mutation}")


def _paired_direction_jet(
    e_rest: np.ndarray,
    beta: np.ndarray,
    dbeta: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, float, float]:
    """Return inverse-aberrated normal nodes and their exact Q-time tangent.

    The regular coefficient ``(gamma-1)/|beta|^2`` is evaluated as
    ``gamma^2/(gamma+1)``, so the beta->0 limit is explicit and finite.
    """
    e0 = np.asarray(e_rest, dtype=float)
    beta2 = float(beta @ beta)
    gamma = float(1.0 / math.sqrt(1.0 - beta2))
    dgamma = float(gamma**3 * (beta @ dbeta))
    s = e0 @ beta
    ds = e0 @ dbeta
    h = gamma * gamma / (gamma + 1.0)
    dh = gamma * (gamma + 2.0) / (gamma + 1.0) ** 2 * dgamma
    A = gamma + h * s
    dA = dgamma + dh * s + h * ds
    F = gamma * (1.0 + s)
    dF = dgamma * (1.0 + s) + gamma * ds
    numerator = e0 + A[:, None] * beta[None, :]
    e = numerator / F[:, None]
    de = (
        (dA[:, None] * beta[None, :] + A[:, None] * dbeta[None, :])
        / F[:, None]
        - e * (dF / F)[:, None]
    )
    return e, de, gamma, dgamma


def bind_direction_dependent_rate_dual(
    electron_binding: Any,
    hubble_jet: NormalHubbleRateJet,
    *,
    e_rest: np.ndarray,
    w_rest: np.ndarray,
    authority: RateDualAuthority,
) -> RateDualBinding | CollisionOffRateDualBinding:
    if not isinstance(hubble_jet, NormalHubbleRateJet):
        raise TypeError("hubble_jet must be a NormalHubbleRateJet")
    if not isinstance(authority, RateDualAuthority):
        raise TypeError("authority must be a RateDualAuthority")
    if authority != RateDualAuthority.frozen_project_authority():
        raise ValueError("rate/dual authority does not match the frozen project owner set")
    if getattr(electron_binding, "coordinate_sha256", None) != hubble_jet.coordinate_sha256:
        raise ValueError("electron and Hubble jets must share the same coordinate authority")

    jet = getattr(electron_binding, "jet", None)
    if jet is None:
        state = getattr(electron_binding, "state", None)
        if getattr(state, "closure", None) != "collision-off":
            raise ValueError("missing ElectronStateJet is allowed only for CollisionOff")
        zeros = np.zeros(len(np.asarray(e_rest)), dtype=float)
        zeros.setflags(write=False)
        return CollisionOffRateDualBinding(
            tau=hubble_jet.tau,
            derivative_side=hubble_jet.derivative_side,
            authority=authority,
            coordinate_sha256=hubble_jet.coordinate_sha256,
            electron_binding_sha256=_sha(
                electron_binding.binding_sha256,
                "electron_binding.binding_sha256",
            ),
            electron_schedule_payload_sha256=_sha(
                state.schedule_payload_sha256,
                "state.schedule_payload_sha256",
            ),
            collision_off_reason=str(state.reason),
            hubble_provenance=hubble_jet.provenance,
            nu_tau=zeros,
        )
    if float(jet.tau) != hubble_jet.tau:
        raise ValueError("electron and Hubble jets must have identical tau")
    if jet.derivative_side is not hubble_jet.derivative_side:
        raise ValueError("electron and Hubble jets must use the same derivative side")

    beta = np.asarray(jet.beta_normal, dtype=float)
    if beta.shape != (3,) or not np.isfinite(beta).all():
        raise ValueError("beta_normal must be a finite length-3 vector")
    beta2 = float(beta @ beta)
    if beta2 >= 1.0:
        raise ValueError("beta_normal must satisfy |beta|<1")
    density = _finite(jet.proper_density_m3, "proper_density_m3")
    if density <= 0.0:
        raise ValueError("proper_density_m3 must be positive")
    state = getattr(electron_binding, "state", None)
    if _finite(getattr(state, "proper_density_m3", math.nan), "state.proper_density_m3") != density:
        raise ValueError("state/jet density mismatch")
    state_beta = np.asarray(getattr(state, "beta_normal", ()), dtype=float)
    if state_beta.shape != (3,) or not np.array_equal(
        state_beta, np.asarray(jet.beta_normal, dtype=float)
    ):
        raise ValueError("state/jet beta mismatch")
    dbeta = np.asarray(jet.dbeta_normal_dtau, dtype=float)
    if dbeta.shape != (3,) or not np.isfinite(dbeta).all():
        raise ValueError("dbeta_normal_dtau must be a finite length-3 vector")
    ddensity = _finite(jet.dproper_density_dtau, "dproper_density_dtau")

    alpha = density * authority.sigma_t_m2 * authority.c_m_s / hubble_jet.H_normal_s
    dalpha = alpha * (
        ddensity / density
        - hubble_jet.dH_normal_s_dtau / hubble_jet.H_normal_s
    )
    e, w, doppler = paired_from_rest(e_rest, w_rest, beta)
    e_formula, de, gamma, dgamma = _paired_direction_jet(e_rest, beta, dbeta)
    if np.max(np.abs(e - e_formula), initial=0.0) > 3e-13:
        raise AssertionError("paired node formula disagrees with carrier aberration")
    q = 1.0 - e @ beta
    dq = -(de @ beta + e @ dbeta)
    dD = dgamma * q + gamma * dq
    nu = alpha * doppler
    dnu = dalpha * doppler + alpha * dD
    global_scale = alpha * gamma
    dglobal_scale = dalpha * gamma + alpha * dgamma
    shape_left_node_weights = w * q**2 / (4.0 * math.pi)
    full_left_node_weights = w * q / (4.0 * math.pi)
    return RateDualBinding(
        tau=float(jet.tau),
        derivative_side=jet.derivative_side,
        authority=authority,
        coordinate_sha256=hubble_jet.coordinate_sha256,
        electron_binding_sha256=_sha(
            electron_binding.binding_sha256,
            "electron_binding.binding_sha256",
        ),
        electron_schedule_payload_sha256=_sha(
            jet.schedule_payload_sha256,
            "jet.schedule_payload_sha256",
        ),
        electron_closure=str(jet.closure),
        hubble_provenance=hubble_jet.provenance,
        proper_density_m3=density,
        dproper_density_dtau=ddensity,
        H_normal_s=hubble_jet.H_normal_s,
        dH_normal_s_dtau=hubble_jet.dH_normal_s_dtau,
        gamma=gamma,
        dgamma_dtau=dgamma,
        e_normal=_readonly_array(e),
        de_normal_dtau=_readonly_array(de),
        w_normal=_readonly_array(w),
        beta=_readonly_array(beta),
        dbeta_dtau=_readonly_array(dbeta),
        doppler=_readonly_array(doppler),
        ddoppler_dtau=_readonly_array(dD),
        direction_factor=_readonly_array(q),
        ddirection_factor_dtau=_readonly_array(dq),
        scalar_opacity_per_hubble=alpha,
        dscalar_opacity_per_hubble_dtau=dalpha,
        nu_tau=_readonly_array(nu),
        dnu_tau_dtau=_readonly_array(dnu),
        shape_left_node_weights=_readonly_array(shape_left_node_weights),
        full_left_node_weights=_readonly_array(full_left_node_weights),
        global_generator_scale=global_scale,
        dglobal_generator_scale_dtau=dglobal_scale,
    )
