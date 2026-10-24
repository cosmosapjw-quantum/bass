"""Hydrogen-frame radiative source adapters for PR-05C2C1B.

Two objects are deliberately separated:

``OriginalHyRecVirtualSpikeSource``
    A source-identical distributional adapter for the October-2012 HyRec
    ``Dtau/Dfeq/Dfplus -> Dfminus`` update.  It acts on the signed spectral
    distortion and carries exact C-source provenance.

``IsotropicEinsteinLineSource``
    A positive paired-rate physical line model implementing the v0.65 scalar,
    unpolarized hydrogen-frame source-isotropy axiom.  It is a theory-contract
    adapter, not a claim that original HyRec stores these coefficients in this
    decomposed form.
"""
from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np
from scipy.constants import c, h, k

from full_bianchi_hyrec.recoil.original_hyrec_physical_flux import (
    OriginalHyRecTrajectorySnapshot,
    physical_log_mode_factor_per_H,
)


HYREC_SOURCE_FILE = "HyRec/hydrogen.c"
HYREC_SPIKE_SOURCE_LINES = (521, 524, 525, 780, 781, 787, 789)


def _readonly(array: np.ndarray) -> np.ndarray:
    result = np.array(array, dtype=float, copy=True)
    result.setflags(write=False)
    return result


@dataclass(frozen=True)
class OriginalHyRecVirtualSourceAdapter:
    """Compatibility adapter preserving the sealed v0.66 source contract."""

    source_function: np.ndarray
    tau_flrw: np.ndarray
    gamma_s_inv: np.ndarray
    mode_factor_per_H: np.ndarray
    x1s: float
    H_s_inv: float

    def __post_init__(self) -> None:
        arrays = {}
        for name in ("source_function", "tau_flrw", "gamma_s_inv", "mode_factor_per_H"):
            value = np.asarray(getattr(self, name), dtype=float)
            if value.ndim != 1 or not np.all(np.isfinite(value)):
                raise ValueError(f"{name} must be a finite one-dimensional array")
            arrays[name] = value.copy()
        size = len(arrays["source_function"])
        if any(len(value) != size for value in arrays.values()):
            raise ValueError("source-adapter array lengths differ")
        if np.any(arrays["tau_flrw"] < 0.0) or np.any(arrays["gamma_s_inv"] <= 0.0):
            raise ValueError("optical depths/rates must be nonnegative/positive")
        if np.any(arrays["mode_factor_per_H"] <= 0.0):
            raise ValueError("mode factor must be positive")
        for name, value in arrays.items():
            value.setflags(write=False)
            object.__setattr__(self, name, value)
        if self.x1s <= 0.0 or self.H_s_inv <= 0.0:
            raise ValueError("x1s and H must be positive")

    @classmethod
    def from_snapshot(
        cls, snapshot: OriginalHyRecTrajectorySnapshot
    ) -> "OriginalHyRecVirtualSourceAdapter":
        mode_factor = physical_log_mode_factor_per_H(snapshot)
        reconstructed_tau = snapshot.x1s * snapshot.Gamma_s_inv / (
            snapshot.H_s_inv * mode_factor
        )
        residual = np.max(
            np.abs(reconstructed_tau - snapshot.Dtau)
            / np.maximum(np.abs(snapshot.Dtau), 1.0e-300)
        )
        if residual > 5.0e-12:
            raise FloatingPointError(f"source tau relation failed: {residual}")
        return cls(
            source_function=snapshot.Dfeq,
            tau_flrw=snapshot.Dtau,
            gamma_s_inv=snapshot.Gamma_s_inv,
            mode_factor_per_H=mode_factor,
            x1s=float(snapshot.x1s),
            H_s_inv=float(snapshot.H_s_inv),
        )


def apply_escape_transfer(
    incoming: np.ndarray, source_function: np.ndarray, optical_depth: np.ndarray
) -> np.ndarray:
    """Preserve the v0.66 source-locked virtual-bin transfer map."""

    incoming = np.asarray(incoming, dtype=float)
    source = np.asarray(source_function, dtype=float)
    tau = np.asarray(optical_depth, dtype=float)
    if incoming.shape != source.shape or incoming.shape != tau.shape:
        raise ValueError("incoming/source/tau shape mismatch")
    if np.any(tau < 0.0) or not np.all(np.isfinite(incoming + source + tau)):
        raise ValueError("invalid source transfer inputs")
    return incoming + (source - incoming) * (-np.expm1(-tau))


def directional_optical_depth(
    adapter: OriginalHyRecVirtualSourceAdapter,
    *,
    redshift_rate_s_inv: float,
) -> np.ndarray:
    """Preserve the v0.66 monotone-branch optical-depth rescaling."""

    rate = float(redshift_rate_s_inv)
    if not math.isfinite(rate) or rate >= 0.0:
        raise ValueError("redshift_rate_s_inv must be finite and negative on this branch")
    return adapter.tau_flrw * adapter.H_s_inv / (-rate)


def one_photon_paired_action(
    *,
    occupation: float,
    upper_population: float,
    lower_population: float,
    degeneracy_ratio: float,
    spontaneous_rate_s_inv: float,
) -> float:
    """Preserve the v0.66 scalar paired one-photon action."""

    f = float(occupation)
    xu = float(upper_population)
    xl = float(lower_population)
    g = float(degeneracy_ratio)
    rate = float(spontaneous_rate_s_inv)
    if min(f, xu, xl, g, rate) < 0.0 or not all(
        map(math.isfinite, (f, xu, xl, g, rate))
    ):
        raise ValueError("one-photon paired inputs must be finite and nonnegative")
    return rate * (xu * (1.0 + f) - g * xl * f)


def one_photon_planck_null_residual(
    *,
    frequency_Hz: float,
    temperature_K: float,
    lower_population: float,
    degeneracy_ratio: float,
    spontaneous_rate_s_inv: float,
) -> float:
    """Preserve the v0.66 detailed-balance residual helper."""

    z = math.exp(-h * float(frequency_Hz) / (k * float(temperature_K)))
    upper = float(lower_population) * float(degeneracy_ratio) * z
    planck = z / (1.0 - z)
    action = one_photon_paired_action(
        occupation=planck,
        upper_population=upper,
        lower_population=lower_population,
        degeneracy_ratio=degeneracy_ratio,
        spontaneous_rate_s_inv=spontaneous_rate_s_inv,
    )
    scale = max(abs(spontaneous_rate_s_inv * lower_population), 1.0e-300)
    return abs(action) / scale


@dataclass(frozen=True)
class OriginalHyRecVirtualSpikeSource:
    """Vectorized exact adapter for the canonical virtual-spike update."""

    tau_flrw: np.ndarray
    equilibrium_departure: np.ndarray
    H_s_inv: float
    source_file: str = HYREC_SOURCE_FILE
    source_lines: tuple[int, ...] = HYREC_SPIKE_SOURCE_LINES

    def __post_init__(self) -> None:
        tau = np.asarray(self.tau_flrw, dtype=float)
        equilibrium = np.asarray(self.equilibrium_departure, dtype=float)
        if tau.ndim != 1 or equilibrium.shape != tau.shape:
            raise ValueError("tau_flrw and equilibrium_departure must be equal 1-D arrays")
        if not np.all(np.isfinite(tau)) or np.any(tau < 0.0):
            raise ValueError("tau_flrw must be finite and nonnegative")
        if not np.all(np.isfinite(equilibrium)):
            raise ValueError("equilibrium_departure must be finite")
        hubble = float(self.H_s_inv)
        if not (math.isfinite(hubble) and hubble > 0.0):
            raise ValueError("H_s_inv must be positive and finite")
        object.__setattr__(self, "tau_flrw", _readonly(tau))
        object.__setattr__(self, "equilibrium_departure", _readonly(equilibrium))
        object.__setattr__(self, "H_s_inv", hubble)

    def directional_optical_depth(
        self,
        *,
        minus_dlognu_dt_s_inv: np.ndarray,
    ) -> np.ndarray:
        speed = np.asarray(minus_dlognu_dt_s_inv, dtype=float)
        if speed.shape != self.tau_flrw.shape or not np.all(np.isfinite(speed)):
            raise ValueError("frequency-speed array must match tau_flrw and be finite")
        if np.any(speed == 0.0):
            raise ValueError("frequency-speed zero requires event localization")
        return self.tau_flrw * self.H_s_inv / np.abs(speed)

    def apply(
        self,
        *,
        incoming: np.ndarray,
        minus_dlognu_dt_s_inv: np.ndarray,
    ) -> np.ndarray:
        values = np.asarray(incoming, dtype=float)
        if values.shape != self.tau_flrw.shape or not np.all(np.isfinite(values)):
            raise ValueError("incoming must match tau_flrw and be finite")
        tau = self.directional_optical_depth(
            minus_dlognu_dt_s_inv=minus_dlognu_dt_s_inv
        )
        absorbed = -np.expm1(-tau)
        result = values + (self.equilibrium_departure - values) * absorbed
        return _readonly(result)

    def jvp(
        self,
        *,
        incoming: np.ndarray,
        minus_dlognu_dt_s_inv: np.ndarray,
        d_incoming: np.ndarray,
        d_equilibrium_departure: np.ndarray,
        d_tau_flrw: np.ndarray,
        d_H_s_inv: float,
        d_minus_dlognu_dt_s_inv: np.ndarray,
    ) -> np.ndarray:
        incoming = np.asarray(incoming, dtype=float)
        speed = np.asarray(minus_dlognu_dt_s_inv, dtype=float)
        d_incoming = np.asarray(d_incoming, dtype=float)
        d_equilibrium = np.asarray(d_equilibrium_departure, dtype=float)
        d_tau_flrw = np.asarray(d_tau_flrw, dtype=float)
        d_speed = np.asarray(d_minus_dlognu_dt_s_inv, dtype=float)
        expected = self.tau_flrw.shape
        for name, value in (
            ("incoming", incoming),
            ("speed", speed),
            ("d_incoming", d_incoming),
            ("d_equilibrium_departure", d_equilibrium),
            ("d_tau_flrw", d_tau_flrw),
            ("d_frequency_speed", d_speed),
        ):
            if value.shape != expected or not np.all(np.isfinite(value)):
                raise ValueError(f"{name} must match tau_flrw and be finite")
        tau = self.directional_optical_depth(minus_dlognu_dt_s_inv=speed)
        transmission = np.exp(-tau)
        absorbed = -np.expm1(-tau)
        d_tau = (
            self.H_s_inv / np.abs(speed) * d_tau_flrw
            + tau * float(d_H_s_inv) / self.H_s_inv
            - tau * d_speed / speed
        )
        result = (
            transmission * d_incoming
            + absorbed * d_equilibrium
            + (self.equilibrium_departure - incoming) * transmission * d_tau
        )
        return _readonly(result)


@dataclass(frozen=True)
class IsotropicEinsteinLineSource:
    """Positive paired one-photon source in the hydrogen rest frame."""

    A_ul_s_inv: float
    profile_Hz_inv: float
    frequency_Hz: float
    nH_m3: float
    upper_population: float
    lower_population: float
    upper_degeneracy: float
    lower_degeneracy: float

    def __post_init__(self) -> None:
        positive = (
            "A_ul_s_inv",
            "profile_Hz_inv",
            "frequency_Hz",
            "nH_m3",
            "upper_degeneracy",
            "lower_degeneracy",
        )
        nonnegative = ("upper_population", "lower_population")
        for name in positive:
            value = float(getattr(self, name))
            if not (math.isfinite(value) and value > 0.0):
                raise ValueError(f"{name} must be positive and finite")
            object.__setattr__(self, name, value)
        for name in nonnegative:
            value = float(getattr(self, name))
            if not (math.isfinite(value) and value >= 0.0):
                raise ValueError(f"{name} must be nonnegative and finite")
            object.__setattr__(self, name, value)

    @property
    def phase_space_prefactor_s_inv(self) -> float:
        return c**3 * self.nH_m3 / (8.0 * math.pi * self.frequency_Hz**2)

    @property
    def emission_s_inv(self) -> float:
        return (
            self.phase_space_prefactor_s_inv
            * self.A_ul_s_inv
            * self.profile_Hz_inv
            * self.upper_population
        )

    @property
    def absorption_s_inv(self) -> float:
        return (
            self.phase_space_prefactor_s_inv
            * self.A_ul_s_inv
            * self.profile_Hz_inv
            * (self.upper_degeneracy / self.lower_degeneracy)
            * self.lower_population
        )

    @property
    def affine_opacity_s_inv(self) -> float:
        """Net coefficient in ``df/dt = emission - affine_opacity*f``."""
        return self.absorption_s_inv - self.emission_s_inv

    def occupation_action(self, occupation: float) -> float:
        value = float(occupation)
        if not (math.isfinite(value) and value >= 0.0):
            raise ValueError("occupation must be nonnegative and finite")
        return self.emission_s_inv * (1.0 + value) - self.absorption_s_inv * value

    def directional_action(self, occupation: np.ndarray) -> np.ndarray:
        values = np.asarray(occupation, dtype=float)
        if not np.all(np.isfinite(values)) or np.any(values < 0.0):
            raise ValueError("directional occupation must be nonnegative and finite")
        return _readonly(
            self.emission_s_inv * (1.0 + values)
            - self.absorption_s_inv * values
        )

    def planck_null_residual(self, *, temperature_K: float) -> float:
        temperature = float(temperature_K)
        if not (math.isfinite(temperature) and temperature > 0.0):
            raise ValueError("temperature_K must be positive and finite")
        z = math.exp(-h * self.frequency_Hz / (k * temperature))
        return self.occupation_action(z / (1.0 - z))


__all__ = [
    "OriginalHyRecVirtualSourceAdapter",
    "apply_escape_transfer",
    "directional_optical_depth",
    "one_photon_paired_action",
    "one_photon_planck_null_residual",
    "OriginalHyRecVirtualSpikeSource",
    "IsotropicEinsteinLineSource",
]
