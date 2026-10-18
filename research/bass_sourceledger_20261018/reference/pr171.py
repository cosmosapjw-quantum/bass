"""Same-clock bolometric control for the frozen native REI AXBI source.

This is deliberately a *boundary* calculation.  It reads the numerical model
implemented by REI PR150's ``AxbiSource`` and expresses its energy injection
in the BASS PR170 source convention,

    S(x) = j_proper(x) / H(x),  x = ln(a/a_ref).

``S`` and ``j_proper`` are bolometric energy densities (eV cm^-3 per dx and
eV cm^-3 s^-1); they are not photon number rates.  The calculation does not
put this energy into a BASS background, does not infer photo-rates from U/M,
and does not create a REI checkpoint.  Those operations require a separately
bound REI owner run.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import math
import sys
from typing import Iterable

import numpy as np
from numpy.polynomial.legendre import leggauss

MPC_CM = 3.085677581491367e24
SOURCE_ID = "MD14_Z002_FESC_BB50K_13P6_100_V1"
ENERGY_EDGES_EV = (13.6, 24.59, 54.42, 100.0)
NATIVE_SOURCE_COMMIT = "0e25846433170d0f420c4cda44a0bedbf02cd177"
NATIVE_SOURCE_SHA256 = "606e3c2ec367dd9951ebbf2f53486f2232b49c0218896d66d8dc13dd5ee83bfe"
NATIVE_TRANSPORT_SHA256 = "9d2d97881ca7b9b58d68dbeffad937e16ca8af237b3d9ba01de0fb5e00b67aa7"


@dataclass(frozen=True)
class BolometricControl:
    zbar: float
    a: float
    h_per_s: float
    n_h0_cm3: float
    comoving_photons_per_s_cmpc3: float
    proper_photons_cm3_s: float
    proper_n_h_cm3: float
    # The first value is the actual transport quadrature representation.  The
    # second is AxbiSource's Simpson construction used only to form fractions.
    transport_mean_energy_ev: float
    source_simpson_mean_energy_ev: float
    j_proper_ev_cm3_s: float
    s_bass_ev_cm3_per_dln_a: float
    rei_energy_per_h_ev_per_dln_a: float
    rei_volume_energy_ev_cm3_per_dln_a: float
    relative_bolometric_difference: float
    spectral_fraction_sum: float
    angular_fraction_sum: float


def _positive(value: float, tag: str) -> float:
    # Rust AxbiSource::positive requires f64::is_normal(), rejecting zero and
    # subnormal source densities before they can overflow a per-H conversion.
    if not math.isfinite(value) or value < sys.float_info.min:
        raise ValueError(tag)
    return value


def _shape(energy_ev: np.ndarray | float) -> np.ndarray | float:
    # Same BB50k number-shape as rust/rei_microphysics/src/axbi_sources.rs.
    k_t_ev = 8.617333262145e-5 * 50000.0
    y = np.asarray(energy_ev, dtype=float)
    return y * y / np.expm1(y / k_t_ev)


def _simpson(lo: float, hi: float, n: int, energy_moment: bool) -> float:
    if n <= 0 or n % 2:
        raise ValueError("SIMPSON_EVEN_SUBDIVISIONS")
    grid = np.linspace(lo, hi, n + 1)
    values = _shape(grid) * (grid if energy_moment else 1.0)
    weights = np.ones(n + 1)
    weights[1:-1:2] = 4.0
    weights[2:-1:2] = 2.0
    return float((hi - lo) / n * np.dot(weights, values) / 3.0)


# Literal PR150 axbi_covariant_transport.rs X8/W8.  It is intentionally not
# replaced by numpy's generator: the control tracks the native association.
_X8 = (-0.9602898564975363, -0.7966664774136267, -0.5255324099163290,
       -0.1834346424956498, 0.1834346424956498, 0.5255324099163290,
       0.7966664774136267, 0.9602898564975363)
_W8 = (0.1012285362903763, 0.2223810344533745, 0.3137066458778873,
       0.3626837833783619, 0.3626837833783619, 0.3137066458778873,
       0.2223810344533745, 0.1012285362903763)


def _transport_moments(lo: float, hi: float) -> tuple[float, float]:
    center, half = 0.5 * (lo + hi), 0.5 * (hi - lo)
    energies = np.array([center + half * x for x in _X8])
    weights = np.array(_W8) * half
    return float(np.dot(weights, _shape(energies))), float(np.dot(weights, _shape(energies) * energies))


def spectral_cells(cells_per_segment: int = 16) -> list[tuple[float, float, float, float]]:
    """Return (lo, hi, number fraction, cell mean energy), matching AxbiSource."""
    if not 1 <= cells_per_segment <= 1024:
        raise ValueError("NATIVE_ENERGY_SUBDIVISION_DOMAIN")
    raw: list[tuple[float, float, float, float]] = []
    for lo0, hi0 in zip(ENERGY_EDGES_EV[:-1], ENERGY_EDGES_EV[1:]):
        for i in range(cells_per_segment):
            lo = lo0 * (hi0 / lo0) ** (i / cells_per_segment)
            hi = lo0 * (hi0 / lo0) ** ((i + 1) / cells_per_segment)
            count = _simpson(lo, hi, 32, False)
            energy = _simpson(lo, hi, 32, True)
            raw.append((lo, hi, count, energy))
    norm = _positive(sum(x[2] for x in raw), "NATIVE_SPECTRAL_NORMALIZATION")
    return [(lo, hi, count / norm, energy / count) for lo, hi, count, energy in raw]


def angular_fractions(n_mu: int = 8) -> np.ndarray:
    """Native source count fractions: Gauss--Legendre weights divided by two."""
    if n_mu not in (8, 16, 32):
        raise ValueError("NATIVE_ANGULAR_QUADRATURE_DOMAIN")
    _, weights = leggauss(n_mu)
    return weights * 0.5


def mean_source_energy_ev(cells_per_segment: int = 16) -> float:
    return float(sum(frac * energy for _, _, frac, energy in spectral_cells(cells_per_segment)))


def transport_mean_energy_ev(cells_per_segment: int = 16, transport_cells: int = 128) -> float:
    """Represented native energy after PR150's GL8 grid intersections.

    ``AxbiSource`` obtains count fractions with Simpson.  ``inject`` divides
    those fractions by GL8 source norms, then deposits GL8 moments in each
    intersection with the log transport grid.  This function follows that
    exact two-stage prescription at reference scale one.  It still is a
    Python control, rather than an observed Rust SourceLedger.
    """
    if not 8 <= transport_cells <= 1024:
        raise ValueError("NATIVE_TRANSPORT_CELL_DOMAIN")
    edges = np.array([13.6 * (512.0 / 13.6) ** (i / transport_cells) for i in range(transport_cells + 1)])
    total_energy = 0.0
    for lo0, hi0, fraction, _ in spectral_cells(cells_per_segment):
        norm, _ = _transport_moments(lo0, hi0)
        for lo_grid, hi_grid in zip(edges[:-1], edges[1:]):
            lo, hi = max(lo0, float(lo_grid)), min(hi0, float(hi_grid))
            if hi > lo:
                _, u = _transport_moments(lo, hi)
                total_energy += fraction * u / norm
    return total_energy


def native_emission_rate(zbar: float, n_h0_cm3: float, escape_fraction: float = 0.2) -> tuple[float, float, float]:
    """REI AxbiSource.at_redshift quantities: comoving, proper, and per-H rate."""
    if not 4.0 <= zbar <= 20.0:
        raise ValueError("NATIVE_REDSHIFT_SUPPORT")
    _positive(n_h0_cm3, "NATIVE_COMOVING_NH")
    if not 0.0 < escape_fraction <= 1.0:
        raise ValueError("NATIVE_ESCAPE_FRACTION")
    _positive(escape_fraction, "NATIVE_ESCAPE_FRACTION")
    zp = 1.0 + zbar
    sfr = 0.015 * zp**2.7 / (1.0 + (zp / 2.9) ** 5.6)
    log_yield = 1.0 / (0.00038 * 0.002**0.227 + 0.01858) - math.log10(2.55)
    comoving = _positive(escape_fraction * 10.0**log_yield * sfr, "NATIVE_COMOVING_EMISSIVITY")
    per_comoving_cm3 = _positive(comoving / MPC_CM**3, "NATIVE_PER_COMOVING_EMISSIVITY")
    proper_rate = _positive(per_comoving_cm3 * zp**3, "NATIVE_PROPER_EMISSIVITY")
    per_h_rate = _positive(per_comoving_cm3 / n_h0_cm3, "NATIVE_PER_H_EMISSIVITY")
    return comoving, proper_rate, per_h_rate


def same_clock_bolometric_control(
    *, zbar: float, h_per_s: float, n_h0_cm3: float, escape_fraction: float = 0.2,
    cells_per_segment: int = 16, n_mu: int = 8,
) -> BolometricControl:
    """Compare BASS S=j/H with REI injection over the same proper Hubble time."""
    _positive(h_per_s, "BASS_H_PER_S")
    comoving, proper_rate, per_h_rate = native_emission_rate(zbar, n_h0_cm3, escape_fraction)
    source_mean_energy = mean_source_energy_ev(cells_per_segment)
    transport_mean_energy = transport_mean_energy_ev(cells_per_segment)
    j_proper = _positive(proper_rate * transport_mean_energy, "NATIVE_PROPER_ENERGY_EMISSIVITY")
    s_bass = _positive(j_proper / h_per_s, "BASS_BOLOMETRIC_SOURCE")
    a = 1.0 / (1.0 + zbar)
    proper_n_h = _positive(n_h0_cm3 / a**3, "NATIVE_PROPER_NH")
    # REI inject() receives dt_s.  Set dt=1/H only for this same-clock control.
    rei_energy_per_h = _positive(per_h_rate * transport_mean_energy / h_per_s, "NATIVE_ENERGY_PER_H")
    rei_volume_energy = _positive(rei_energy_per_h * proper_n_h, "NATIVE_VOLUME_ENERGY")
    denominator = max(abs(s_bass), abs(rei_volume_energy), np.finfo(float).tiny)
    return BolometricControl(
        zbar=zbar, a=a, h_per_s=h_per_s, n_h0_cm3=n_h0_cm3,
        comoving_photons_per_s_cmpc3=comoving, proper_photons_cm3_s=proper_rate,
        proper_n_h_cm3=proper_n_h, transport_mean_energy_ev=transport_mean_energy,
        source_simpson_mean_energy_ev=source_mean_energy,
        j_proper_ev_cm3_s=j_proper, s_bass_ev_cm3_per_dln_a=s_bass,
        rei_energy_per_h_ev_per_dln_a=rei_energy_per_h,
        rei_volume_energy_ev_cm3_per_dln_a=rei_volume_energy,
        relative_bolometric_difference=abs(s_bass - rei_volume_energy) / denominator,
        spectral_fraction_sum=float(sum(x[2] for x in spectral_cells(cells_per_segment))),
        angular_fraction_sum=float(np.sum(angular_fractions(n_mu))),
    )


def controls(rows: Iterable[tuple[float, float]], n_h0_cm3: float) -> list[dict[str, float]]:
    """Serializable controls for (zbar,H/s) rows; no photon-rate reconstruction."""
    return [asdict(same_clock_bolometric_control(zbar=z, h_per_s=h, n_h0_cm3=n_h0_cm3)) for z, h in rows]
