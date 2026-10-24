"""Canonical original-HyRec two-photon/Raman adapters.

This module separates two claims that must not be conflated.

``OriginalHyRecTwoPhotonRamanTable`` and
``CanonicalTwoPhotonRamanCoupling`` transcribe the October-2012 HyRec table
reader and the real--virtual coefficients in ``hydrogen.c``.  They operate in
HyRec's source units: energies and radiation temperature are in eV and the
integrated-bin coefficients are rates in ``s^-1``.

``PhysicalTwoPhotonRamanBin`` is the scalar, unpolarized positive paired-rate
physics contract used when an angle-resolved radiation field is evolved.  It
implements the two-photon and Raman gain/loss factors, but it is not relabelled
as an independently stored original-HyRec coefficient.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
from io import StringIO
import math
from pathlib import Path
from types import MappingProxyType
from typing import Literal, Mapping
import zipfile

import numpy as np

from full_bianchi_hyrec.recoil.original_hyrec_native import (
    NVIRT,
    ORIGINAL_HYREC_ARCHIVE_SHA256,
)


TWO_PHOTON_TABLE_SHA256 = (
    "93d23871e21c40f5b72a6ef9acf3eb7be054735c8aee9401e455736c1d9d8cf9"
)
TWO_PHOTON_MEMBER = "HyRec/two_photon_tables.dat"
HYREC_SOURCE_FILE = "HyRec/hydrogen.c"
HYREC_HEADER_FILE = "HyRec/hydrogen.h"
HYREC_PARAMETER_FILE = "HyRec/hyrec_params.h"
HYREC_SOURCE_LINES = (
    270,
    278,
    279,
    280,
    281,
    282,
    283,
    287,
    288,
    289,
    290,
    293,
    299,
    300,
    302,
    303,
    305,
    306,
    308,
    309,
    310,
    467,
    469,
    470,
    472,
    473,
    475,
    476,
    477,
)

NSUBLYA = 140
NSUBLYB = 271
L2S_1S_S_INV = 8.2206
A2S_THRESHOLD_EV = 10.198714553953742
A3S3D_THRESHOLD_EV = 12.087365397278509
A4S4D_THRESHOLD_EV = 12.748393192442178
E32_EV = A3S3D_THRESHOLD_EV - A2S_THRESHOLD_EV
E42_EV = A4S4D_THRESHOLD_EV - A2S_THRESHOLD_EV

ChannelName = Literal["2s", "3s3d", "4s4d"]
ProcessName = Literal["two_photon", "raman"]


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _readonly(value: np.ndarray, shape: tuple[int, ...], name: str) -> np.ndarray:
    array = np.asarray(value, dtype=float)
    if array.shape != shape:
        raise ValueError(f"{name} must have shape {shape}, got {array.shape}")
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} contains nonfinite values")
    result = np.array(array, copy=True)
    result.setflags(write=False)
    return result


def _x_exp_over_expm1(x: np.ndarray) -> np.ndarray:
    """Return ``x exp(x)/expm1(x)`` with its regular small-x limit."""

    x = np.asarray(x, dtype=float)
    result = np.empty_like(x)
    small = np.abs(x) < 1.0e-5
    xs = x[small]
    result[small] = 1.0 + xs / 2.0 + xs * xs / 12.0 - xs**4 / 720.0
    regular = ~small
    result[regular] = x[regular] * np.exp(x[regular]) / np.expm1(x[regular])
    return result


def _inverse_abs_expm1(delta_eV: np.ndarray, temperature_eV: float) -> tuple[np.ndarray, np.ndarray]:
    x = np.asarray(delta_eV, dtype=float) / float(temperature_eV)
    denominator = np.abs(np.expm1(x))
    if np.any(denominator == 0.0):
        raise ValueError("a virtual-state centre lies exactly on a transition threshold")
    inverse = 1.0 / denominator
    dlog_inverse_dlog_temperature = _x_exp_over_expm1(x)
    return inverse, dlog_inverse_dlog_temperature


@dataclass(frozen=True)
class CanonicalTwoPhotonRamanCoupling:
    """Source-identical real/virtual coefficients from ``populateTS_2photon``."""

    radiation_temperature_eV: float
    fsR: float
    meR: float
    real_to_virtual_s_inv: np.ndarray
    virtual_to_real_s_inv: np.ndarray
    d_real_to_virtual_d_log_temperature_s_inv: np.ndarray
    d_virtual_to_real_d_log_temperature_s_inv: np.ndarray
    source_hashes: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("radiation_temperature_eV", "fsR", "meR"):
            value = float(getattr(self, name))
            if not (math.isfinite(value) and value > 0.0):
                raise ValueError(f"{name} must be positive and finite")
            object.__setattr__(self, name, value)
        for name in (
            "real_to_virtual_s_inv",
            "virtual_to_real_s_inv",
            "d_real_to_virtual_d_log_temperature_s_inv",
            "d_virtual_to_real_d_log_temperature_s_inv",
        ):
            object.__setattr__(
                self,
                name,
                _readonly(getattr(self, name), (2, NVIRT), name),
            )
        if np.any(self.real_to_virtual_s_inv < 0.0) or np.any(
            self.virtual_to_real_s_inv < 0.0
        ):
            raise ValueError("canonical transition rates must be nonnegative")
        object.__setattr__(
            self,
            "source_hashes",
            MappingProxyType({str(k): str(v) for k, v in self.source_hashes.items()}),
        )

    @property
    def Tvr_offdiag_s_inv(self) -> np.ndarray:
        return _readonly(-self.real_to_virtual_s_inv, (2, NVIRT), "Tvr")

    @property
    def Trv_offdiag_s_inv(self) -> np.ndarray:
        return _readonly(-self.virtual_to_real_s_inv, (2, NVIRT), "Trv")

    @property
    def Trr_diagonal_addition_s_inv(self) -> np.ndarray:
        result = np.sum(self.real_to_virtual_s_inv, axis=1)
        result.setflags(write=False)
        return result

    @property
    def coefficient_vector_s_inv(self) -> np.ndarray:
        result = np.concatenate(
            (self.real_to_virtual_s_inv.ravel(), self.virtual_to_real_s_inv.ravel())
        )
        result.setflags(write=False)
        return result

    def jvp(
        self,
        *,
        d_log_radiation_temperature: float = 0.0,
        d_log_fsR: float = 0.0,
        d_log_meR: float = 0.0,
    ) -> np.ndarray:
        directions = np.asarray(
            [d_log_radiation_temperature, d_log_fsR, d_log_meR], dtype=float
        )
        if not np.all(np.isfinite(directions)):
            raise ValueError("log-parameter directions must be finite")
        scale_direction = 8.0 * directions[1] + directions[2]
        d_real = (
            directions[0] * self.d_real_to_virtual_d_log_temperature_s_inv
            + scale_direction * self.real_to_virtual_s_inv
        )
        d_virtual = (
            directions[0] * self.d_virtual_to_real_d_log_temperature_s_inv
            + scale_direction * self.virtual_to_real_s_inv
        )
        result = np.concatenate((d_real.ravel(), d_virtual.ravel()))
        result.setflags(write=False)
        return result


@dataclass(frozen=True)
class OriginalHyRecTwoPhotonRamanTable:
    """Byte-locked October-2012 two-photon/Raman integrated-bin table."""

    energy_eV: np.ndarray
    integrated_rates_s_inv: np.ndarray
    source_hashes: Mapping[str, str]
    archive_path: Path
    source_file: str = HYREC_SOURCE_FILE
    source_lines: tuple[int, ...] = HYREC_SOURCE_LINES

    def __post_init__(self) -> None:
        object.__setattr__(self, "energy_eV", _readonly(self.energy_eV, (NVIRT,), "energy_eV"))
        object.__setattr__(
            self,
            "integrated_rates_s_inv",
            _readonly(self.integrated_rates_s_inv, (4, NVIRT), "integrated_rates_s_inv"),
        )
        if np.any(np.diff(self.energy_eV) <= 0.0):
            raise ValueError("virtual-state energies must be strictly increasing")
        if np.any(self.integrated_rates_s_inv < 0.0):
            raise ValueError("integrated rates must be nonnegative")
        archive = Path(self.archive_path)
        if not archive.is_file():
            raise FileNotFoundError(archive)
        object.__setattr__(self, "archive_path", archive)
        object.__setattr__(
            self,
            "source_hashes",
            MappingProxyType({str(k): str(v) for k, v in self.source_hashes.items()}),
        )

    @classmethod
    def from_archive(cls, path: str | Path) -> "OriginalHyRecTwoPhotonRamanTable":
        archive = Path(path)
        if _sha256_file(archive) != ORIGINAL_HYREC_ARCHIVE_SHA256:
            raise ValueError("original-HyRec archive SHA-256 mismatch")
        with zipfile.ZipFile(archive) as handle:
            data = handle.read(TWO_PHOTON_MEMBER)
        if _sha256_bytes(data) != TWO_PHOTON_TABLE_SHA256:
            raise ValueError("two_photon_tables.dat SHA-256 mismatch")
        raw = np.loadtxt(StringIO(data.decode("ascii")), dtype=float)
        if raw.shape != (NVIRT, 5):
            raise ValueError(f"unexpected two-photon table shape {raw.shape}")
        rates = np.asarray(raw[:, 1:].T, dtype=float)
        normalization = L2S_1S_S_INV / float(np.sum(rates[1, :NSUBLYA]))
        rates[1, :NSUBLYA] *= normalization
        return cls(
            energy_eV=raw[:, 0],
            integrated_rates_s_inv=rates,
            source_hashes={
                "HyRec_Oct2012.zip": ORIGINAL_HYREC_ARCHIVE_SHA256,
                "two_photon_tables.dat": TWO_PHOTON_TABLE_SHA256,
            },
            archive_path=archive,
        )

    @property
    def A1s_s_inv(self) -> np.ndarray:
        return self.integrated_rates_s_inv[0]

    @property
    def A2s_s_inv(self) -> np.ndarray:
        return self.integrated_rates_s_inv[1]

    @property
    def A3s3d_s_inv(self) -> np.ndarray:
        return self.integrated_rates_s_inv[2]

    @property
    def A4s4d_s_inv(self) -> np.ndarray:
        return self.integrated_rates_s_inv[3]

    def process_kind(self, channel: ChannelName, index: int) -> ProcessName:
        if not 0 <= int(index) < NVIRT:
            raise IndexError(index)
        threshold = {
            "2s": A2S_THRESHOLD_EV,
            "3s3d": A3S3D_THRESHOLD_EV,
            "4s4d": A4S4D_THRESHOLD_EV,
        }.get(channel)
        if threshold is None:
            raise ValueError(f"unknown channel {channel!r}")
        return "two_photon" if self.energy_eV[int(index)] < threshold else "raman"

    def evaluate_canonical_coupling(
        self,
        *,
        radiation_temperature_eV: float,
        fsR: float = 1.0,
        meR: float = 1.0,
    ) -> CanonicalTwoPhotonRamanCoupling:
        temperature = float(radiation_temperature_eV)
        fs_ratio = float(fsR)
        mass_ratio = float(meR)
        if not (math.isfinite(temperature) and temperature > 0.0):
            raise ValueError("radiation_temperature_eV must be positive and finite")
        if not (math.isfinite(fs_ratio) and fs_ratio > 0.0):
            raise ValueError("fsR must be positive and finite")
        if not (math.isfinite(mass_ratio) and mass_ratio > 0.0):
            raise ValueError("meR must be positive and finite")
        scale = fs_ratio**8 * mass_ratio
        energy = self.energy_eV

        inv2, dlog2 = _inverse_abs_expm1(energy - A2S_THRESHOLD_EV, temperature)
        rate2 = scale * self.A2s_s_inv * inv2
        d_rate2 = rate2 * dlog2

        inv3, dlog3 = _inverse_abs_expm1(energy - A3S3D_THRESHOLD_EV, temperature)
        boltz3 = math.exp(-E32_EV / temperature) / 3.0
        rate3 = scale * self.A3s3d_s_inv * boltz3 * inv3
        d_rate3 = rate3 * (E32_EV / temperature + dlog3)

        inv4, dlog4 = _inverse_abs_expm1(energy - A4S4D_THRESHOLD_EV, temperature)
        boltz4 = math.exp(-E42_EV / temperature) / 3.0
        rate4 = scale * self.A4s4d_s_inv * boltz4 * inv4
        d_rate4 = rate4 * (E42_EV / temperature + dlog4)

        real_to_virtual = np.vstack((rate2, rate3 + rate4))
        d_real = np.vstack((d_rate2, d_rate3 + d_rate4))
        x21 = (energy - A2S_THRESHOLD_EV) / temperature
        ratio2 = np.exp(x21)
        ratio2p = 3.0 * ratio2
        virtual_to_real = np.vstack((rate2 * ratio2, (rate3 + rate4) * ratio2p))
        d_virtual = np.vstack(
            (
                ratio2 * (d_rate2 - x21 * rate2),
                ratio2p * (d_rate3 + d_rate4 - x21 * (rate3 + rate4)),
            )
        )
        return CanonicalTwoPhotonRamanCoupling(
            radiation_temperature_eV=temperature,
            fsR=fs_ratio,
            meR=mass_ratio,
            real_to_virtual_s_inv=real_to_virtual,
            virtual_to_real_s_inv=virtual_to_real,
            d_real_to_virtual_d_log_temperature_s_inv=d_real,
            d_virtual_to_real_d_log_temperature_s_inv=d_virtual,
            source_hashes=self.source_hashes,
        )


@dataclass(frozen=True)
class PhysicalTwoPhotonRamanBin:
    """Positive paired scalar source for one tracked photon-frequency bin.

    ``two_photon`` uses ``nu_companion + nu_tracked = nu_transition``.
    ``raman`` uses ``nu_tracked = nu_transition + nu_companion``.  The returned
    action is the net production rate of tracked photons per hydrogen atom.
    """

    process: ProcessName
    integrated_rate_s_inv: float
    transition_frequency_Hz: float
    companion_frequency_Hz: float
    tracked_frequency_Hz: float
    upper_population: float
    ground_population: float
    upper_to_ground_degeneracy_ratio: float

    def __post_init__(self) -> None:
        if self.process not in ("two_photon", "raman"):
            raise ValueError("process must be 'two_photon' or 'raman'")
        for name in (
            "integrated_rate_s_inv",
            "transition_frequency_Hz",
            "companion_frequency_Hz",
            "tracked_frequency_Hz",
            "upper_to_ground_degeneracy_ratio",
        ):
            value = float(getattr(self, name))
            if not (math.isfinite(value) and value > 0.0):
                raise ValueError(f"{name} must be positive and finite")
            object.__setattr__(self, name, value)
        for name in ("upper_population", "ground_population"):
            value = float(getattr(self, name))
            if not (math.isfinite(value) and value >= 0.0):
                raise ValueError(f"{name} must be nonnegative and finite")
            object.__setattr__(self, name, value)
        if self.process == "two_photon":
            residual = self.companion_frequency_Hz + self.tracked_frequency_Hz - self.transition_frequency_Hz
        else:
            residual = self.transition_frequency_Hz + self.companion_frequency_Hz - self.tracked_frequency_Hz
        scale = max(
            self.transition_frequency_Hz,
            self.companion_frequency_Hz,
            self.tracked_frequency_Hz,
        )
        if abs(residual) > 2.0e-13 * scale:
            raise ValueError("frequencies violate the selected process energy relation")

    def paired_rates(
        self,
        *,
        companion_occupation: float,
        tracked_occupation: float,
    ) -> tuple[float, float]:
        fc = float(companion_occupation)
        ft = float(tracked_occupation)
        if not (math.isfinite(fc) and fc >= 0.0 and math.isfinite(ft) and ft >= 0.0):
            raise ValueError("occupations must be nonnegative and finite")
        rate = self.integrated_rate_s_inv
        if self.process == "two_photon":
            forward = rate * self.upper_population * (1.0 + fc) * (1.0 + ft)
            reverse = (
                rate
                * self.upper_to_ground_degeneracy_ratio
                * self.ground_population
                * fc
                * ft
            )
        else:
            forward = rate * self.upper_population * fc * (1.0 + ft)
            reverse = (
                rate
                * self.upper_to_ground_degeneracy_ratio
                * self.ground_population
                * (1.0 + fc)
                * ft
            )
        return float(forward), float(reverse)

    def net_action(self, companion_occupation: float, tracked_occupation: float) -> float:
        forward, reverse = self.paired_rates(
            companion_occupation=companion_occupation,
            tracked_occupation=tracked_occupation,
        )
        return forward - reverse

    def jvp(
        self,
        *,
        companion_occupation: float,
        tracked_occupation: float,
        d_integrated_rate_s_inv: float,
        d_upper_population: float,
        d_ground_population: float,
        d_companion_occupation: float,
        d_tracked_occupation: float,
    ) -> float:
        values = np.asarray(
            [
                companion_occupation,
                tracked_occupation,
                d_integrated_rate_s_inv,
                d_upper_population,
                d_ground_population,
                d_companion_occupation,
                d_tracked_occupation,
            ],
            dtype=float,
        )
        if not np.all(np.isfinite(values)):
            raise ValueError("JVP values must be finite")
        fc = float(companion_occupation)
        ft = float(tracked_occupation)
        if fc < 0.0 or ft < 0.0:
            raise ValueError("occupations must be nonnegative")
        rate = self.integrated_rate_s_inv
        upper = self.upper_population
        ground = self.ground_population
        ratio = self.upper_to_ground_degeneracy_ratio
        dr = float(d_integrated_rate_s_inv)
        du = float(d_upper_population)
        dg = float(d_ground_population)
        dfc = float(d_companion_occupation)
        dft = float(d_tracked_occupation)
        if self.process == "two_photon":
            forward_factor = upper * (1.0 + fc) * (1.0 + ft)
            reverse_factor = ratio * ground * fc * ft
            d_forward_factor = (
                du * (1.0 + fc) * (1.0 + ft)
                + upper * dfc * (1.0 + ft)
                + upper * (1.0 + fc) * dft
            )
            d_reverse_factor = ratio * (
                dg * fc * ft + ground * dfc * ft + ground * fc * dft
            )
        else:
            forward_factor = upper * fc * (1.0 + ft)
            reverse_factor = ratio * ground * (1.0 + fc) * ft
            d_forward_factor = (
                du * fc * (1.0 + ft)
                + upper * dfc * (1.0 + ft)
                + upper * fc * dft
            )
            d_reverse_factor = ratio * (
                dg * (1.0 + fc) * ft
                + ground * dfc * ft
                + ground * (1.0 + fc) * dft
            )
        return dr * (forward_factor - reverse_factor) + rate * (
            d_forward_factor - d_reverse_factor
        )


__all__ = [
    "A2S_THRESHOLD_EV",
    "A3S3D_THRESHOLD_EV",
    "A4S4D_THRESHOLD_EV",
    "CanonicalTwoPhotonRamanCoupling",
    "OriginalHyRecTwoPhotonRamanTable",
    "PhysicalTwoPhotonRamanBin",
    "TWO_PHOTON_TABLE_SHA256",
]
