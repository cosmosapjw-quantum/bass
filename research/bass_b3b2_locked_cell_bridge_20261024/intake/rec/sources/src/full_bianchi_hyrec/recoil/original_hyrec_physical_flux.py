"""Physical logarithmic-frequency edge flux from original HyRec.

This module is the bounded PR-04B2A bridge between the October-2012
original-HyRec real/virtual algebra and a physical photon measure.  It does
*not* identify virtual populations with photon finite-volume cell numbers.
Instead it uses the source-defined incoming, average and outgoing occupation
number distortions across each virtual spike.

Conventions
-----------
* metric signature ``(-,+,+,+)``;
* local frame: hydrogen orthonormal tetrad;
* ordinary frequency ``nu`` in Hz, not angular frequency;
* logarithmic frequency ``y = ln(nu)``;
* cosmological time ``eta = ln(a)``, hence ``d/dt = H d/deta``;
* ``Delta nu = nu_target - nu_source``;
* ``Delta E_gamma = h Delta nu`` and ``Delta E_H = -h Delta nu``;
* original-HyRec source quantities use cgs lengths and eV energies;
* physical spectral density ``N_y = 8 pi nu^3 f_nu/(c^3 n_H)`` has units
  photons per hydrogen atom per ``d ln(nu)``;
* the edge source ``J_b = H A_b (f_b^- - f_b^+)`` has units ``s^-1`` per H,
  with ``A_b = 8 pi nu_b^3/(c^3 n_H)`` dimensionless.

For exact escape functions,

``P_b = (1-exp(-tau_b))/tau_b`` and
``fbar_b = P_b fplus_b + (1-P_b) feq_b``.

Together with ``tau_b=x_1s Gamma_b/(H A_b)``, this gives

``x_1s Gamma_b (feq_b-fbar_b) = H A_b (fminus_b-fplus_b)``.

The October-2012 C implementation uses second-order small-``tau`` branches.
The source branch is reproduced exactly for byte/source parity, while a stable
``expm1`` implementation is provided for production arithmetic.
"""
from __future__ import annotations

from dataclasses import dataclass
import csv
import math
from pathlib import Path
from typing import Iterable

import numpy as np
from scipy.constants import h

from .original_hyrec_native import H_PLANCK_EV_S, NVIRT


SOURCE_HPC_EV_CM = 1.239841874331e-4
SOURCE_SMALL_TAU_CUTOFF = 1.0e-6
MOMENT_MAX = 4


def _readonly_array(value: np.ndarray | Iterable[float], shape: tuple[int, ...], name: str) -> np.ndarray:
    array = np.asarray(value, dtype=float)
    if array.shape != shape:
        raise ValueError(f"{name} must have shape {shape}, got {array.shape}")
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} contains nonfinite entries")
    array = np.array(array, dtype=float, copy=True)
    array.setflags(write=False)
    return array


@dataclass(frozen=True)
class OriginalHyRecBoundarySample:
    """Source-identical free-streaming sample at one PR-04C interface.

    The sample carries both the analytic Planck reference and the signed
    original-HyRec distortion.  Their sum is the positive total occupation
    used for the unresolved boundary packet.  Flux magnitudes are redward
    (toward decreasing ordinary frequency) and are positive scalars; the
    interface direction is supplied separately by the split-domain operator.
    """

    side: str
    interface_x: float
    doppler_width_eV: float
    interface_energy_eV: float
    interface_frequency_Hz: float
    source_index: int
    source_energy_eV: float
    lna_query: float
    history_index_left: int
    history_index_right: int
    interpolation_fraction: float
    history_value_left: float
    history_value_right: float
    distortion_occupation: float
    blackbody_occupation: float
    total_occupation: float
    mode_factor_per_H: float
    distortion_number_flux_per_H_s: float
    reference_number_flux_per_H_s: float
    total_number_flux_per_H_s: float
    distortion_photon_energy_flux_W_per_H: float
    reference_photon_energy_flux_W_per_H: float
    total_photon_energy_flux_W_per_H: float

    def __post_init__(self) -> None:
        if self.side not in {"red", "blue"}:
            raise ValueError("side must be 'red' or 'blue'")
        expected_x = -21.25 if self.side == "red" else 21.25
        if not math.isclose(self.interface_x, expected_x, rel_tol=0.0, abs_tol=1.0e-13):
            raise ValueError("interface x is inconsistent with side")
        scalar_names = (
            "interface_x",
            "doppler_width_eV",
            "interface_energy_eV",
            "interface_frequency_Hz",
            "source_energy_eV",
            "lna_query",
            "interpolation_fraction",
            "history_value_left",
            "history_value_right",
            "distortion_occupation",
            "blackbody_occupation",
            "total_occupation",
            "mode_factor_per_H",
            "distortion_number_flux_per_H_s",
            "reference_number_flux_per_H_s",
            "total_number_flux_per_H_s",
            "distortion_photon_energy_flux_W_per_H",
            "reference_photon_energy_flux_W_per_H",
            "total_photon_energy_flux_W_per_H",
        )
        if not all(math.isfinite(float(getattr(self, name))) for name in scalar_names):
            raise ValueError("boundary sample contains nonfinite values")
        if self.doppler_width_eV <= 0.0:
            raise ValueError("Doppler width must be positive")
        if self.interface_energy_eV <= 0.0 or self.interface_frequency_Hz <= 0.0:
            raise ValueError("interface energy/frequency must be positive")
        if self.source_index < 0 or self.history_index_left < 0:
            raise ValueError("indices must be nonnegative")
        if self.history_index_right != self.history_index_left + 1:
            raise ValueError("history indices must be adjacent")
        if not 0.0 <= self.interpolation_fraction <= 1.0:
            raise ValueError("interpolation fraction must lie in [0,1]")
        if self.source_energy_eV <= self.interface_energy_eV:
            raise ValueError("free-streaming source energy must exceed interface energy")
        if self.blackbody_occupation < 0.0 or self.total_occupation <= 0.0:
            raise ValueError("reference occupation must be nonnegative and total positive")
        if self.mode_factor_per_H <= 0.0:
            raise ValueError("mode factor must be positive")
        if self.reference_number_flux_per_H_s < 0.0 or self.total_number_flux_per_H_s <= 0.0:
            raise ValueError("reference flux must be nonnegative and total flux positive")
        if self.reference_photon_energy_flux_W_per_H < 0.0 or self.total_photon_energy_flux_W_per_H <= 0.0:
            raise ValueError("reference energy flux must be nonnegative and total positive")


def _relative_scalar_residual(first: float, second: float) -> float:
    return abs(float(first) - float(second)) / max(abs(float(first)), abs(float(second)), 1.0e-300)


def boundary_sample_reconstruction_residuals(
    sample: OriginalHyRecBoundarySample,
    *,
    H_s_inv: float,
    nH_cm3: float,
    TR_eV_rescaled: float,
    fsR: float,
    meR: float,
    energy_grid_eV: np.ndarray | Iterable[float],
    check_blackbody: bool = True,
    check_mode_factor: bool = True,
) -> dict[str, float]:
    """Independently reconstruct one source diagnostic boundary sample.

    This routine also enforces that ``source_index`` is the least canonical
    native-table index whose energy is strictly above the physical interface.
    """

    if not math.isfinite(H_s_inv) or H_s_inv <= 0.0:
        raise ValueError("H_s_inv must be positive")
    if not math.isfinite(nH_cm3) or nH_cm3 <= 0.0:
        raise ValueError("nH_cm3 must be positive")
    if not math.isfinite(TR_eV_rescaled) or TR_eV_rescaled <= 0.0:
        raise ValueError("TR_eV_rescaled must be positive")
    if not math.isfinite(fsR) or fsR <= 0.0 or not math.isfinite(meR) or meR <= 0.0:
        raise ValueError("fsR and meR must be positive")
    energy = np.asarray(energy_grid_eV, dtype=float)
    if energy.ndim != 1 or not np.all(np.diff(energy) > 0.0):
        raise ValueError("energy grid must be one-dimensional and increasing")
    above = np.flatnonzero(energy > sample.interface_energy_eV)
    if above.size == 0:
        raise ValueError("no native source exists above interface")
    expected_source = int(above[0])
    if sample.source_index != expected_source:
        raise ValueError(
            f"source index is not minimal: expected {expected_source}, got {sample.source_index}"
        )
    if not math.isclose(
        sample.source_energy_eV,
        float(energy[expected_source]),
        rel_tol=3.0e-14,
        abs_tol=1.0e-15,
    ):
        raise ValueError("source energy does not match native grid")

    interpolation = (
        (1.0 - sample.interpolation_fraction) * sample.history_value_left
        + sample.interpolation_fraction * sample.history_value_right
    )
    frequency = sample.interface_energy_eV * fsR**2 * meR / H_PLANCK_EV_S
    total_occupation = sample.blackbody_occupation + sample.distortion_occupation
    distortion_number = H_s_inv * sample.mode_factor_per_H * sample.distortion_occupation
    reference_number = H_s_inv * sample.mode_factor_per_H * sample.blackbody_occupation
    total_number = H_s_inv * sample.mode_factor_per_H * sample.total_occupation
    if check_blackbody:
        blackbody = 1.0 / np.expm1(sample.interface_energy_eV / TR_eV_rescaled)
    else:
        blackbody = sample.blackbody_occupation
    if check_mode_factor:
        actual_energy_eV = sample.interface_energy_eV * fsR**2 * meR
        wavelength_cm = SOURCE_HPC_EV_CM / actual_energy_eV
        mode_factor = 8.0 * np.pi / (nH_cm3 * wavelength_cm**3)
    else:
        mode_factor = sample.mode_factor_per_H
    distortion_energy = h * sample.interface_frequency_Hz * sample.distortion_number_flux_per_H_s
    reference_energy = h * sample.interface_frequency_Hz * sample.reference_number_flux_per_H_s
    total_energy = h * sample.interface_frequency_Hz * sample.total_number_flux_per_H_s
    return {
        "interpolation": _relative_scalar_residual(interpolation, sample.distortion_occupation),
        "frequency": _relative_scalar_residual(frequency, sample.interface_frequency_Hz),
        "blackbody": _relative_scalar_residual(blackbody, sample.blackbody_occupation),
        "occupation_sum": _relative_scalar_residual(total_occupation, sample.total_occupation),
        "mode_factor": _relative_scalar_residual(mode_factor, sample.mode_factor_per_H),
        "distortion_number": _relative_scalar_residual(distortion_number, sample.distortion_number_flux_per_H_s),
        "reference_number": _relative_scalar_residual(reference_number, sample.reference_number_flux_per_H_s),
        "total_number": _relative_scalar_residual(total_number, sample.total_number_flux_per_H_s),
        "number_sum": _relative_scalar_residual(
            sample.reference_number_flux_per_H_s + sample.distortion_number_flux_per_H_s,
            sample.total_number_flux_per_H_s,
        ),
        "distortion_energy": _relative_scalar_residual(
            distortion_energy, sample.distortion_photon_energy_flux_W_per_H
        ),
        "reference_energy": _relative_scalar_residual(
            reference_energy, sample.reference_photon_energy_flux_W_per_H
        ),
        "total_energy": _relative_scalar_residual(
            total_energy, sample.total_photon_energy_flux_W_per_H
        ),
        "energy_sum": _relative_scalar_residual(
            sample.reference_photon_energy_flux_W_per_H
            + sample.distortion_photon_energy_flux_W_per_H,
            sample.total_photon_energy_flux_W_per_H,
        ),
    }


@dataclass(frozen=True)
class OriginalHyRecBoundaryInstrumentedSnapshot:
    """One full original-HyRec trajectory snapshot plus two interfaces."""

    trajectory: "OriginalHyRecTrajectorySnapshot"
    boundaries: tuple[OriginalHyRecBoundarySample, OriginalHyRecBoundarySample]

    def __post_init__(self) -> None:
        if len(self.boundaries) != 2:
            raise ValueError("boundary snapshot must contain exactly two interfaces")
        if tuple(sample.side for sample in self.boundaries) != ("red", "blue"):
            raise ValueError("boundary interfaces must be ordered red, blue")


@dataclass(frozen=True)
class OriginalHyRecTrajectorySnapshot:
    """One source-identical FULL-mode original-HyRec trajectory snapshot."""

    target_z: float
    z: float
    zstart: float
    iz_local: int
    xe: float
    xHII: float
    x1s: float
    nH_cm3: float
    H_s_inv: float
    TM_eV_rescaled: float
    TR_eV_rescaled: float
    TM_over_TR: float
    fsR: float
    meR: float
    dxHIIdlna: float
    A2p_up_s_inv: float
    A2p_dn_s_inv: float
    Dfplus_Lya: float
    Dfplus_Lyb: float
    Dfminus_Lya: float
    Dfminus_Lyb: float
    Dfminus_Lyg: float
    xr: np.ndarray
    sr: np.ndarray
    Alpha: np.ndarray
    DAlpha: np.ndarray
    Beta: np.ndarray
    Trr: np.ndarray
    energy_eV: np.ndarray
    Dfplus: np.ndarray
    Dfbar: np.ndarray
    Dfminus: np.ndarray
    Dfeq: np.ndarray
    Dtau: np.ndarray
    xv: np.ndarray
    sv: np.ndarray
    Tvv0_s_inv: np.ndarray
    Aup_s_inv: np.ndarray
    Adn_s_inv: np.ndarray
    Gamma_s_inv: np.ndarray
    one_minus_Pi: np.ndarray
    Trv: np.ndarray
    Tvr: np.ndarray
    Tvv: np.ndarray

    def __post_init__(self) -> None:
        scalar_positive = {
            "target_z": self.target_z,
            "z": self.z,
            "zstart": self.zstart,
            "x1s": self.x1s,
            "nH_cm3": self.nH_cm3,
            "H_s_inv": self.H_s_inv,
            "TM_eV_rescaled": self.TM_eV_rescaled,
            "TR_eV_rescaled": self.TR_eV_rescaled,
            "fsR": self.fsR,
            "meR": self.meR,
        }
        for name, value in scalar_positive.items():
            if not math.isfinite(value) or value <= 0.0:
                raise ValueError(f"{name} must be positive and finite")
        if self.iz_local < 0:
            raise ValueError("iz_local must be nonnegative")
        if not math.isclose(self.x1s, 1.0 - self.xHII, rel_tol=3e-15, abs_tol=3e-15):
            raise ValueError("x1s must equal 1-xHII")
        if not math.isclose(
            self.TM_over_TR,
            self.TM_eV_rescaled / self.TR_eV_rescaled,
            rel_tol=3e-15,
            abs_tol=3e-15,
        ):
            raise ValueError("TM_over_TR is inconsistent")

        specifications = {
            "xr": ((2,), self.xr),
            "sr": ((2,), self.sr),
            "Alpha": ((2,), self.Alpha),
            "DAlpha": ((2,), self.DAlpha),
            "Beta": ((2,), self.Beta),
            "Trr": ((2, 2), self.Trr),
            "energy_eV": ((NVIRT,), self.energy_eV),
            "Dfplus": ((NVIRT,), self.Dfplus),
            "Dfbar": ((NVIRT,), self.Dfbar),
            "Dfminus": ((NVIRT,), self.Dfminus),
            "Dfeq": ((NVIRT,), self.Dfeq),
            "Dtau": ((NVIRT,), self.Dtau),
            "xv": ((NVIRT,), self.xv),
            "sv": ((NVIRT,), self.sv),
            "Tvv0_s_inv": ((NVIRT,), self.Tvv0_s_inv),
            "Aup_s_inv": ((NVIRT,), self.Aup_s_inv),
            "Adn_s_inv": ((NVIRT,), self.Adn_s_inv),
            "Gamma_s_inv": ((NVIRT,), self.Gamma_s_inv),
            "one_minus_Pi": ((NVIRT,), self.one_minus_Pi),
            "Trv": ((2, NVIRT), self.Trv),
            "Tvr": ((2, NVIRT), self.Tvr),
            "Tvv": ((3, NVIRT), self.Tvv),
        }
        for name, (shape, value) in specifications.items():
            object.__setattr__(self, name, _readonly_array(value, shape, name))
        if not np.all(np.diff(self.energy_eV) > 0.0):
            raise ValueError("energy_eV must be strictly increasing")
        if np.min(self.Dtau) < 0.0:
            raise ValueError("Dtau must be nonnegative")
        if np.min(self.Gamma_s_inv) <= 0.0:
            raise ValueError("Gamma_s_inv must be positive")
        if np.min(self.one_minus_Pi) < 0.0 or np.max(self.one_minus_Pi) > 1.0:
            raise ValueError("one_minus_Pi must lie in [0,1]")

    @property
    def source_solution(self) -> np.ndarray:
        result = np.concatenate((self.xr, self.xv))
        result.setflags(write=False)
        return result

    @property
    def frequency_Hz(self) -> np.ndarray:
        # The source tabulates today's energy scale and rescales atomic energies
        # by fsR^2 meR.  Project moments use CODATA h explicitly.
        frequency = self.energy_eV * self.fsR**2 * self.meR / H_PLANCK_EV_S
        frequency.setflags(write=False)
        return frequency

    @property
    def blackbody_occupation(self) -> np.ndarray:
        exponent = self.energy_eV / self.TR_eV_rescaled
        occupation = 1.0 / np.expm1(exponent)
        occupation.setflags(write=False)
        return occupation


def parse_original_hyrec_snapshot_csv(path: str | Path) -> OriginalHyRecTrajectorySnapshot:
    """Parse the deterministic PR-04B2A guarded diagnostic CSV."""

    meta: dict[str, float] = {}
    xr = np.zeros(2)
    sr = np.zeros(2)
    alpha = np.zeros(2)
    dalpha = np.zeros(2)
    beta = np.zeros(2)
    trr = np.zeros((2, 2))
    trv = np.zeros((2, NVIRT))
    tvr = np.zeros((2, NVIRT))
    tvv = np.zeros((3, NVIRT))
    virtual = np.zeros((NVIRT, 13))
    seen_virtual: set[int] = set()

    with Path(path).open(newline="", encoding="utf-8") as handle:
        for row in csv.reader(handle):
            if not row:
                continue
            kind = row[0]
            if kind == "META":
                if len(row) != 3:
                    raise ValueError(f"malformed META row: {row}")
                meta[row[1]] = float(row[2])
            elif kind == "REAL":
                if len(row) != 7:
                    raise ValueError(f"malformed REAL row: {row}")
                index = int(row[1])
                xr[index], sr[index], alpha[index], dalpha[index], beta[index] = map(float, row[2:])
            elif kind == "TRR":
                trr[int(row[1]), int(row[2])] = float(row[3])
            elif kind == "TRV":
                trv[int(row[1]), int(row[2])] = float(row[3])
            elif kind == "TVR":
                tvr[int(row[1]), int(row[2])] = float(row[3])
            elif kind == "TVV":
                tvv[int(row[1]), int(row[2])] = float(row[3])
            elif kind == "VIRTUAL":
                if len(row) != 15:
                    raise ValueError(f"malformed VIRTUAL row length {len(row)}")
                index = int(row[1])
                if index in seen_virtual:
                    raise ValueError(f"duplicate virtual index {index}")
                seen_virtual.add(index)
                virtual[index] = np.asarray(row[2:], dtype=float)
            elif kind == "INTERFACE":
                # Parsed by parse_original_hyrec_boundary_snapshot_csv.
                continue
            else:
                raise ValueError(f"unknown snapshot row kind {kind!r}")

    required_meta = {
        "target_z",
        "z",
        "zstart",
        "iz_local",
        "xe",
        "xHII",
        "x1s",
        "nH_cm3",
        "H_sInv",
        "TM_eV_rescaled",
        "TR_eV_rescaled",
        "TM_over_TR",
        "fsR",
        "meR",
        "dxHIIdlna",
        "A2p_up_sInv",
        "A2p_dn_sInv",
        "Dfplus_Lya",
        "Dfplus_Lyb",
        "Dfminus_Lya",
        "Dfminus_Lyb",
        "Dfminus_Lyg",
    }
    missing = sorted(required_meta.difference(meta))
    if missing:
        raise ValueError(f"snapshot is missing metadata: {missing}")
    if seen_virtual != set(range(NVIRT)):
        raise ValueError("snapshot does not contain all virtual states")

    # VIRTUAL columns after the index:
    # E, fplus, fbar, fminus, feq, tau, xv, sv, Tvv0, Aup, Adn,
    # Gamma, one_minus_Pi.
    return OriginalHyRecTrajectorySnapshot(
        target_z=meta["target_z"],
        z=meta["z"],
        zstart=meta["zstart"],
        iz_local=int(round(meta["iz_local"])),
        xe=meta["xe"],
        xHII=meta["xHII"],
        x1s=meta["x1s"],
        nH_cm3=meta["nH_cm3"],
        H_s_inv=meta["H_sInv"],
        TM_eV_rescaled=meta["TM_eV_rescaled"],
        TR_eV_rescaled=meta["TR_eV_rescaled"],
        TM_over_TR=meta["TM_over_TR"],
        fsR=meta["fsR"],
        meR=meta["meR"],
        dxHIIdlna=meta["dxHIIdlna"],
        A2p_up_s_inv=meta["A2p_up_sInv"],
        A2p_dn_s_inv=meta["A2p_dn_sInv"],
        Dfplus_Lya=meta["Dfplus_Lya"],
        Dfplus_Lyb=meta["Dfplus_Lyb"],
        Dfminus_Lya=meta["Dfminus_Lya"],
        Dfminus_Lyb=meta["Dfminus_Lyb"],
        Dfminus_Lyg=meta["Dfminus_Lyg"],
        xr=xr,
        sr=sr,
        Alpha=alpha,
        DAlpha=dalpha,
        Beta=beta,
        Trr=trr,
        energy_eV=virtual[:, 0],
        Dfplus=virtual[:, 1],
        Dfbar=virtual[:, 2],
        Dfminus=virtual[:, 3],
        Dfeq=virtual[:, 4],
        Dtau=virtual[:, 5],
        xv=virtual[:, 6],
        sv=virtual[:, 7],
        Tvv0_s_inv=virtual[:, 8],
        Aup_s_inv=virtual[:, 9],
        Adn_s_inv=virtual[:, 10],
        Gamma_s_inv=virtual[:, 11],
        one_minus_Pi=virtual[:, 12],
        Trv=trv,
        Tvr=tvr,
        Tvv=tvv,
    )


def parse_original_hyrec_boundary_snapshot_csv(
    path: str | Path,
) -> OriginalHyRecBoundaryInstrumentedSnapshot:
    """Parse a PR-04C guarded source snapshot and its two interfaces."""

    trajectory = parse_original_hyrec_snapshot_csv(path)
    samples: list[OriginalHyRecBoundarySample] = []
    with Path(path).open(newline="", encoding="utf-8") as handle:
        for row in csv.reader(handle):
            if not row or row[0] != "INTERFACE":
                continue
            if len(row) != 20:
                raise ValueError(f"malformed INTERFACE row length {len(row)}")
            (
                _,
                side,
                interface_x,
                doppler_width_eV,
                interface_energy_eV,
                source_index,
                source_energy_eV,
                lna_query,
                history_index_left,
                history_index_right,
                interpolation_fraction,
                history_value_left,
                history_value_right,
                distortion_occupation,
                blackbody_occupation,
                total_occupation,
                mode_factor_per_H,
                distortion_number_flux,
                reference_number_flux,
                total_number_flux,
            ) = row
            energy_eV = float(interface_energy_eV)
            frequency_Hz = (
                energy_eV * trajectory.fsR**2 * trajectory.meR / H_PLANCK_EV_S
            )
            distortion_flux = float(distortion_number_flux)
            reference_flux = float(reference_number_flux)
            total_flux = float(total_number_flux)
            samples.append(
                OriginalHyRecBoundarySample(
                    side=side,
                    interface_x=float(interface_x),
                    doppler_width_eV=float(doppler_width_eV),
                    interface_energy_eV=energy_eV,
                    interface_frequency_Hz=frequency_Hz,
                    source_index=int(source_index),
                    source_energy_eV=float(source_energy_eV),
                    lna_query=float(lna_query),
                    history_index_left=int(history_index_left),
                    history_index_right=int(history_index_right),
                    interpolation_fraction=float(interpolation_fraction),
                    history_value_left=float(history_value_left),
                    history_value_right=float(history_value_right),
                    distortion_occupation=float(distortion_occupation),
                    blackbody_occupation=float(blackbody_occupation),
                    total_occupation=float(total_occupation),
                    mode_factor_per_H=float(mode_factor_per_H),
                    distortion_number_flux_per_H_s=distortion_flux,
                    reference_number_flux_per_H_s=reference_flux,
                    total_number_flux_per_H_s=total_flux,
                    distortion_photon_energy_flux_W_per_H=h
                    * frequency_Hz
                    * distortion_flux,
                    reference_photon_energy_flux_W_per_H=h
                    * frequency_Hz
                    * reference_flux,
                    total_photon_energy_flux_W_per_H=h
                    * frequency_Hz
                    * total_flux,
                )
            )
    ordered = tuple(sorted(samples, key=lambda sample: sample.interface_x))
    if len(ordered) != 2:
        raise ValueError(f"expected two INTERFACE rows, found {len(ordered)}")
    return OriginalHyRecBoundaryInstrumentedSnapshot(
        trajectory=trajectory,
        boundaries=(ordered[0], ordered[1]),
    )


def source_escape_factors(tau: np.ndarray | Iterable[float]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Reproduce the October-2012 C small-optical-depth branches.

    Returns ``(P, 1-P, 1-exp(-tau))``.  The latter two quantities are the
    independently truncated source expressions when ``tau <= 1e-6``.
    """

    tau_array = np.asarray(tau, dtype=float)
    if np.any(~np.isfinite(tau_array)) or np.any(tau_array < 0.0):
        raise ValueError("tau must be finite and nonnegative")
    large = tau_array > SOURCE_SMALL_TAU_CUTOFF
    one_minus_exp = tau_array - 0.5 * tau_array**2
    one_minus_exp = np.array(one_minus_exp, copy=True)
    one_minus_exp[large] = -np.expm1(-tau_array[large])
    one_minus_pi = 0.5 * tau_array - tau_array**2 / 6.0
    one_minus_pi = np.array(one_minus_pi, copy=True)
    one_minus_pi[large] = (
        1.0 - (-np.expm1(-tau_array[large])) / tau_array[large]
    )
    probability = 1.0 - one_minus_pi
    return probability, one_minus_pi, one_minus_exp


def stable_escape_factors(tau: np.ndarray | Iterable[float]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Cancellation-safe exact escape factors in float64 arithmetic."""

    tau_array = np.asarray(tau, dtype=float)
    if np.any(~np.isfinite(tau_array)) or np.any(tau_array < 0.0):
        raise ValueError("tau must be finite and nonnegative")
    one_minus_exp = -np.expm1(-tau_array)
    probability = np.ones_like(tau_array)
    nonzero = tau_array != 0.0
    probability[nonzero] = one_minus_exp[nonzero] / tau_array[nonzero]
    one_minus_pi = np.empty_like(tau_array)
    small = tau_array < 0.5
    t = tau_array[small]
    # 1-(1-exp(-t))/t = sum_{n>=1} (-1)^(n+1) t^n/(n+1)!.
    # Fourteen terms keep the entire t<0.5 branch at float64 precision.
    series = np.zeros_like(t)
    power = np.ones_like(t)
    factorial = 1.0
    for n in range(1, 15):
        power *= t
        factorial *= n + 1
        series += ((-1.0) ** (n + 1)) * power / factorial
    one_minus_pi[small] = series
    one_minus_pi[~small] = 1.0 - probability[~small]
    # For small tau, the series is the accurate primary quantity and P=1-(1-P)
    # is safe.  For large tau, preserve the direct expm1/tau evaluation rather
    # than subtracting a number close to one.
    probability[small] = 1.0 - one_minus_pi[small]
    return probability, one_minus_pi, one_minus_exp


def physical_log_mode_factor_per_H(snapshot: OriginalHyRecTrajectorySnapshot) -> np.ndarray:
    """Return ``A_b=8 pi nu_b^3/(c^3 n_H)`` using source cgs constants.

    ``nH_cm3`` times ``lambda_cm^3`` is dimensionless, so ``A_b`` is photons
    per H per unit occupation per ``d ln(nu)``.
    """

    wavelength_cm = SOURCE_HPC_EV_CM / (
        snapshot.energy_eV * snapshot.fsR**2 * snapshot.meR
    )
    factor = 8.0 * np.pi / (snapshot.nH_cm3 * wavelength_cm**3)
    factor.setflags(write=False)
    return factor


def dense_original_hyrec_matrix(snapshot: OriginalHyRecTrajectorySnapshot) -> np.ndarray:
    matrix = np.zeros((2 + NVIRT, 2 + NVIRT), dtype=float)
    matrix[:2, :2] = snapshot.Trr
    matrix[:2, 2:] = snapshot.Trv
    matrix[2:, :2] = snapshot.Tvr.T
    matrix[2:, 2:] = np.diag(snapshot.Tvv[0])
    for index in range(NVIRT):
        if index > 0:
            matrix[2 + index, 2 + index - 1] = snapshot.Tvv[1, index]
        if index < NVIRT - 1:
            matrix[2 + index, 2 + index + 1] = snapshot.Tvv[2, index]
    return matrix


def dense_direct_solution(snapshot: OriginalHyRecTrajectorySnapshot) -> np.ndarray:
    matrix = dense_original_hyrec_matrix(snapshot)
    right_hand_side = np.concatenate((snapshot.sr, snapshot.sv))
    return np.linalg.solve(matrix, right_hand_side)


def structured_schur_solution(snapshot: OriginalHyRecTrajectorySnapshot) -> np.ndarray:
    matrix = dense_original_hyrec_matrix(snapshot)
    virtual = matrix[2:, 2:]
    inverse_tvr = np.linalg.solve(virtual, snapshot.Tvr.T)
    inverse_sv = np.linalg.solve(virtual, snapshot.sv)
    effective_matrix = snapshot.Trr - snapshot.Trv @ inverse_tvr
    effective_source = snapshot.sr - snapshot.Trv @ inverse_sv
    real = np.linalg.solve(effective_matrix, effective_source)
    virtual_solution = inverse_sv - inverse_tvr @ real
    return np.concatenate((real, virtual_solution))


def reconstruct_equilibrium_distortion(
    snapshot: OriginalHyRecTrajectorySnapshot,
    solution: np.ndarray,
) -> np.ndarray:
    solution = np.asarray(solution, dtype=float)
    if solution.shape != (2 + NVIRT,):
        raise ValueError(f"solution must have shape {(2 + NVIRT,)}")
    real = solution[:2]
    virtual = solution[2:]
    numerator = -real[0] * snapshot.Tvr[0] - real[1] * snapshot.Tvr[1]
    numerator = np.array(numerator, copy=True)
    for index in range(NVIRT):
        if index == 0:
            numerator[index] -= virtual[1] * snapshot.Tvv[2, 0]
        elif index == NVIRT - 1:
            numerator[index] -= virtual[NVIRT - 2] * snapshot.Tvv[1, NVIRT - 1]
        else:
            numerator[index] -= (
                virtual[index + 1] * snapshot.Tvv[2, index]
                + virtual[index - 1] * snapshot.Tvv[1, index]
            )
    denominator = (
        snapshot.x1s * snapshot.one_minus_Pi * snapshot.Tvv0_s_inv
    )
    if np.any(denominator == 0.0):
        raise ValueError("snapshot contains a zero equilibrium denominator")
    return numerator / denominator


def outgoing_distortion(
    incoming: np.ndarray,
    equilibrium: np.ndarray,
    tau: np.ndarray,
    *,
    source_branch: bool,
) -> np.ndarray:
    incoming = np.asarray(incoming, dtype=float)
    equilibrium = np.asarray(equilibrium, dtype=float)
    tau = np.asarray(tau, dtype=float)
    if incoming.shape != equilibrium.shape or incoming.shape != tau.shape:
        raise ValueError("incoming, equilibrium and tau must have the same shape")
    factors = source_escape_factors(tau) if source_branch else stable_escape_factors(tau)
    one_minus_exp = factors[2]
    return incoming + one_minus_exp * (equilibrium - incoming)


def average_distortion(
    incoming: np.ndarray,
    equilibrium: np.ndarray,
    tau: np.ndarray,
    *,
    source_branch: bool,
) -> np.ndarray:
    probability = (
        source_escape_factors(tau)[0]
        if source_branch
        else stable_escape_factors(tau)[0]
    )
    return probability * np.asarray(incoming) + (1.0 - probability) * np.asarray(equilibrium)


def transport_edge_flux_per_H_s(
    snapshot: OriginalHyRecTrajectorySnapshot,
    *,
    incoming: np.ndarray | None = None,
    outgoing: np.ndarray | None = None,
) -> np.ndarray:
    incoming_array = snapshot.Dfplus if incoming is None else np.asarray(incoming, dtype=float)
    outgoing_array = snapshot.Dfminus if outgoing is None else np.asarray(outgoing, dtype=float)
    if incoming_array.shape != (NVIRT,) or outgoing_array.shape != (NVIRT,):
        raise ValueError("incoming and outgoing must have shape (NVIRT,)")
    return (
        snapshot.H_s_inv
        * physical_log_mode_factor_per_H(snapshot)
        * (outgoing_array - incoming_array)
    )


def collision_edge_flux_per_H_s(
    snapshot: OriginalHyRecTrajectorySnapshot,
    *,
    equilibrium: np.ndarray | None = None,
    average: np.ndarray | None = None,
) -> np.ndarray:
    equilibrium_array = snapshot.Dfeq if equilibrium is None else np.asarray(equilibrium, dtype=float)
    average_array = snapshot.Dfbar if average is None else np.asarray(average, dtype=float)
    if equilibrium_array.shape != (NVIRT,) or average_array.shape != (NVIRT,):
        raise ValueError("equilibrium and average must have shape (NVIRT,)")
    return snapshot.x1s * snapshot.Gamma_s_inv * (equilibrium_array - average_array)


def structural_edge_flux_per_H_s(
    snapshot: OriginalHyRecTrajectorySnapshot,
    *,
    equilibrium: np.ndarray | None = None,
    incoming: np.ndarray | None = None,
    source_branch: bool = True,
) -> np.ndarray:
    equilibrium_array = snapshot.Dfeq if equilibrium is None else np.asarray(equilibrium, dtype=float)
    incoming_array = snapshot.Dfplus if incoming is None else np.asarray(incoming, dtype=float)
    probability = (
        source_escape_factors(snapshot.Dtau)[0]
        if source_branch
        else stable_escape_factors(snapshot.Dtau)[0]
    )
    return (
        snapshot.x1s
        * snapshot.Gamma_s_inv
        * probability
        * (equilibrium_array - incoming_array)
    )


def spectral_source_moments_Hz(
    edge_flux_per_H_s: np.ndarray,
    frequency_Hz: np.ndarray,
    maximum_order: int = MOMENT_MAX,
) -> np.ndarray:
    """Signed net spectral-source moments, not COM--KHW jump moments."""

    flux = np.asarray(edge_flux_per_H_s, dtype=float)
    frequency = np.asarray(frequency_Hz, dtype=float)
    if flux.shape != frequency.shape:
        raise ValueError("edge flux and frequency must have the same shape")
    if maximum_order < 0:
        raise ValueError("maximum_order must be nonnegative")
    return np.asarray(
        [np.sum(flux * frequency**order) for order in range(maximum_order + 1)],
        dtype=float,
    )


def edge_flux_jvp(
    snapshot: OriginalHyRecTrajectorySnapshot,
    incoming_direction: np.ndarray,
    equilibrium_direction: np.ndarray,
    *,
    source_branch: bool = False,
) -> np.ndarray:
    incoming_direction = np.asarray(incoming_direction, dtype=float)
    equilibrium_direction = np.asarray(equilibrium_direction, dtype=float)
    if incoming_direction.shape != (NVIRT,) or equilibrium_direction.shape != (NVIRT,):
        raise ValueError("directions must have shape (NVIRT,)")
    one_minus_exp = (
        source_escape_factors(snapshot.Dtau)[2]
        if source_branch
        else stable_escape_factors(snapshot.Dtau)[2]
    )
    coefficient = (
        snapshot.H_s_inv
        * physical_log_mode_factor_per_H(snapshot)
        * one_minus_exp
    )
    return coefficient * (equilibrium_direction - incoming_direction)


def central_difference_edge_jvp_residual(
    snapshot: OriginalHyRecTrajectorySnapshot,
    incoming: np.ndarray,
    equilibrium: np.ndarray,
    incoming_direction: np.ndarray,
    equilibrium_direction: np.ndarray,
    epsilon: float = 2.0e-7,
) -> float:
    incoming = np.asarray(incoming, dtype=float)
    equilibrium = np.asarray(equilibrium, dtype=float)
    incoming_direction = np.asarray(incoming_direction, dtype=float)
    equilibrium_direction = np.asarray(equilibrium_direction, dtype=float)
    analytic = edge_flux_jvp(
        snapshot,
        incoming_direction,
        equilibrium_direction,
        source_branch=False,
    )

    def action(source: np.ndarray, target: np.ndarray) -> np.ndarray:
        outgoing = outgoing_distortion(
            source,
            target,
            snapshot.Dtau,
            source_branch=False,
        )
        return transport_edge_flux_per_H_s(
            snapshot,
            incoming=source,
            outgoing=outgoing,
        )

    finite = (
        action(
            incoming + epsilon * incoming_direction,
            equilibrium + epsilon * equilibrium_direction,
        )
        - action(
            incoming - epsilon * incoming_direction,
            equilibrium - epsilon * equilibrium_direction,
        )
    ) / (2.0 * epsilon)
    return relative_inf(finite, analytic)


def backward_euler_edge_relaxation(
    snapshot: OriginalHyRecTrajectorySnapshot,
    occupation: np.ndarray,
    equilibrium_occupation: np.ndarray,
    dt_s: float,
) -> np.ndarray:
    """Positive fixed-coefficient backward-Euler edge relaxation.

    For ``df/dt=lambda_b(f_eq-f)``, the physical normalization gives
    ``lambda_b=H(1-exp(-tau_b))``.  This is a local frozen-snapshot update; it is
    not claimed to replace original HyRec's full trajectory integrator.
    """

    if not math.isfinite(dt_s) or dt_s <= 0.0:
        raise ValueError("dt_s must be positive and finite")
    occupation = np.asarray(occupation, dtype=float)
    equilibrium_occupation = np.asarray(equilibrium_occupation, dtype=float)
    if occupation.shape != (NVIRT,) or equilibrium_occupation.shape != (NVIRT,):
        raise ValueError("occupations must have shape (NVIRT,)")
    if np.min(occupation) < 0.0 or np.min(equilibrium_occupation) < 0.0:
        raise ValueError("occupations must be nonnegative")
    rate = snapshot.H_s_inv * stable_escape_factors(snapshot.Dtau)[2]
    return (occupation + dt_s * rate * equilibrium_occupation) / (1.0 + dt_s * rate)


def same_event_energy_ledger_W_per_H(
    edge_flux_per_H_s: np.ndarray,
    frequency_Hz: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    flux = np.asarray(edge_flux_per_H_s, dtype=float)
    frequency = np.asarray(frequency_Hz, dtype=float)
    if flux.shape != frequency.shape:
        raise ValueError("edge flux and frequency must have the same shape")
    photon = h * frequency * flux
    atom = -photon
    return photon, atom, photon + atom


def relative_inf(first: np.ndarray, second: np.ndarray) -> float:
    first = np.asarray(first, dtype=float)
    second = np.asarray(second, dtype=float)
    numerator = np.linalg.norm(first - second, ord=np.inf)
    denominator = max(
        np.linalg.norm(first, ord=np.inf),
        np.linalg.norm(second, ord=np.inf),
        1.0e-300,
    )
    return float(numerator / denominator)


def save_snapshot_npz(path: str | Path, snapshot: OriginalHyRecTrajectorySnapshot, **extra: np.ndarray | float | str) -> None:
    values: dict[str, np.ndarray | float | int | str] = {
        "classification": "PR04B2A_ORIGINAL_HYREC_PHYSICAL_EDGE_FLUX",
        "target_z": snapshot.target_z,
        "z": snapshot.z,
        "zstart": snapshot.zstart,
        "iz_local": snapshot.iz_local,
        "xe": snapshot.xe,
        "xHII": snapshot.xHII,
        "x1s": snapshot.x1s,
        "nH_cm3": snapshot.nH_cm3,
        "H_sInv": snapshot.H_s_inv,
        "TM_eV_rescaled": snapshot.TM_eV_rescaled,
        "TR_eV_rescaled": snapshot.TR_eV_rescaled,
        "TM_over_TR": snapshot.TM_over_TR,
        "fsR": snapshot.fsR,
        "meR": snapshot.meR,
        "dxHIIdlna": snapshot.dxHIIdlna,
        "A2p_up_sInv": snapshot.A2p_up_s_inv,
        "A2p_dn_sInv": snapshot.A2p_dn_s_inv,
        "xr": snapshot.xr,
        "sr": snapshot.sr,
        "Alpha": snapshot.Alpha,
        "DAlpha": snapshot.DAlpha,
        "Beta": snapshot.Beta,
        "Trr": snapshot.Trr,
        "energy_eV": snapshot.energy_eV,
        "frequency_Hz": snapshot.frequency_Hz,
        "Dfplus": snapshot.Dfplus,
        "Dfbar": snapshot.Dfbar,
        "Dfminus": snapshot.Dfminus,
        "Dfeq": snapshot.Dfeq,
        "Dtau": snapshot.Dtau,
        "xv": snapshot.xv,
        "sv": snapshot.sv,
        "Tvv0_sInv": snapshot.Tvv0_s_inv,
        "Aup_sInv": snapshot.Aup_s_inv,
        "Adn_sInv": snapshot.Adn_s_inv,
        "Gamma_sInv": snapshot.Gamma_s_inv,
        "one_minus_Pi": snapshot.one_minus_Pi,
        "Trv": snapshot.Trv,
        "Tvr": snapshot.Tvr,
        "Tvv": snapshot.Tvv,
    }
    values.update(extra)
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(target.suffix + ".tmp")
    with temporary.open("wb") as handle:
        np.savez_compressed(handle, **values)
    temporary.replace(target)


__all__ = [
    "SOURCE_HPC_EV_CM",
    "SOURCE_SMALL_TAU_CUTOFF",
    "MOMENT_MAX",
    "OriginalHyRecBoundarySample",
    "boundary_sample_reconstruction_residuals",
    "OriginalHyRecBoundaryInstrumentedSnapshot",
    "OriginalHyRecTrajectorySnapshot",
    "parse_original_hyrec_boundary_snapshot_csv",
    "parse_original_hyrec_snapshot_csv",
    "source_escape_factors",
    "stable_escape_factors",
    "physical_log_mode_factor_per_H",
    "dense_original_hyrec_matrix",
    "dense_direct_solution",
    "structured_schur_solution",
    "reconstruct_equilibrium_distortion",
    "outgoing_distortion",
    "average_distortion",
    "transport_edge_flux_per_H_s",
    "collision_edge_flux_per_H_s",
    "structural_edge_flux_per_H_s",
    "spectral_source_moments_Hz",
    "edge_flux_jvp",
    "central_difference_edge_jvp_residual",
    "backward_euler_edge_relaxation",
    "same_event_energy_ledger_W_per_H",
    "relative_inf",
    "save_snapshot_npz",
]
