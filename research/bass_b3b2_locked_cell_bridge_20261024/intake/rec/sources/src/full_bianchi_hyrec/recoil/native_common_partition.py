"""Identifiability audit for original-HyRec to 17-cell common measures.

This module implements the bounded PR-04B2B audit.  It deliberately does not
invent a cell partition for the October-2012 original-HyRec tables.  The
canonical tables contain frequency centres and transition rates already
integrated over latent spike widths, whereas the runtime source consumes only
those centres and integrated coefficients.

Conventions
-----------
* metric signature ``(-,+,+,+)``;
* ordinary frequency ``nu`` in Hz;
* dimensionless Doppler coordinate ``x=(nu-nu_Lya)/Delta_nu_D``;
* ``Delta nu = nu_target-nu_source``;
* ``Delta E_gamma=h Delta nu`` and ``Delta E_H=-h Delta nu``;
* ``c``, ``h`` and ``k_B`` remain explicit in upstream physical modules.

The central result is a fail-closed one:

1. a positive measure supported on the v0.51 core ``[-4.25,4.25]`` cannot
   preserve the zeroth and second raw moments of the full native physical edge
   measure, because the native normalized second moment exceeds the sharp
   support bound by many orders of magnitude;
2. after discarding the exterior measure, moments through order four provide
   at most five independent constraints for seventeen target-cell masses, so
   they do not identify a unique positive projection without an additional,
   independently sourced closure;
3. the production and high-resolution original-HyRec tables are separate,
   non-nested integrated-rate lanes and do not supply the missing target-cell
   boundaries or a canonical restriction operator.

These statements block a direct native-to-17-cell equality.  They do not block
coupling the two representations through a conservative split-domain exchange
contract in the next bounded stage.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import io
from pathlib import Path
from typing import Iterable
import zipfile

import numpy as np
from scipy.optimize import linprog

from .original_hyrec_native import H_PLANCK_EV_S


MOMENT_ORDER = 4
CORE_X_MIN = -4.25
CORE_X_MAX = 4.25

PRODUCTION_MEMBER = "HyRec/two_photon_tables.dat"
HIGH_RESOLUTION_MEMBER = "HyRec/two_photon_tables_hires.dat"
PARAMETER_MEMBER = "HyRec/hyrec_params.h"
README_MEMBER = "HyRec/readme.pdf"


@dataclass(frozen=True)
class HyRecTableConfiguration:
    """Immutable source-table configuration from ``hyrec_params.h``."""

    name: str
    member: str
    row_count: int
    nsublya: int
    nsublyb: int
    nvirt: int
    ndiff: int

    @property
    def diffusion_start(self) -> int:
        return self.nsublya - self.ndiff // 2

    @property
    def diffusion_stop(self) -> int:
        return self.nsublya + self.ndiff // 2


PRODUCTION_CONFIGURATION = HyRecTableConfiguration(
    name="production",
    member=PRODUCTION_MEMBER,
    row_count=311,
    nsublya=140,
    nsublyb=271,
    nvirt=311,
    ndiff=80,
)

HIGH_RESOLUTION_CONFIGURATION = HyRecTableConfiguration(
    name="high_resolution_reference",
    member=HIGH_RESOLUTION_MEMBER,
    row_count=1493,
    nsublya=408,
    nsublyb=1323,
    nvirt=1493,
    ndiff=300,
)


@dataclass(frozen=True)
class HyRecIntegratedTable:
    """One byte-locked original-HyRec integrated-rate table."""

    configuration: HyRecTableConfiguration
    sha256: str
    size_bytes: int
    values: np.ndarray

    def __post_init__(self) -> None:
        values = np.asarray(self.values, dtype=float)
        expected = (self.configuration.row_count, 5)
        if values.shape != expected:
            raise ValueError(f"expected table shape {expected}, got {values.shape}")
        if not np.all(np.isfinite(values)):
            raise ValueError("table contains nonfinite values")
        if not np.all(np.diff(values[:, 0]) > 0.0):
            raise ValueError("table energies must be strictly increasing")
        if np.min(values[:, 1:]) < 0.0:
            raise ValueError("integrated transition rates must be nonnegative")
        values = np.array(values, dtype=float, copy=True)
        values.setflags(write=False)
        object.__setattr__(self, "values", values)

    @property
    def energy_eV(self) -> np.ndarray:
        return self.values[:, 0]

    @property
    def integrated_rates_s_inv(self) -> np.ndarray:
        return self.values[:, 1:]

    @property
    def diffusion_indices(self) -> np.ndarray:
        result = np.arange(
            self.configuration.diffusion_start,
            self.configuration.diffusion_stop,
            dtype=int,
        )
        result.setflags(write=False)
        return result

    def frequency_Hz(self, *, fsR: float = 1.0, meR: float = 1.0) -> np.ndarray:
        if not np.isfinite(fsR) or fsR <= 0.0:
            raise ValueError("fsR must be positive")
        if not np.isfinite(meR) or meR <= 0.0:
            raise ValueError("meR must be positive")
        result = self.energy_eV * fsR**2 * meR / H_PLANCK_EV_S
        result.setflags(write=False)
        return result

    def doppler_x(
        self,
        nu_abs_Hz: float,
        Doppler_width_Hz: float,
        *,
        fsR: float = 1.0,
        meR: float = 1.0,
    ) -> np.ndarray:
        if not np.isfinite(nu_abs_Hz) or nu_abs_Hz <= 0.0:
            raise ValueError("nu_abs_Hz must be positive")
        if not np.isfinite(Doppler_width_Hz) or Doppler_width_Hz <= 0.0:
            raise ValueError("Doppler_width_Hz must be positive")
        result = (
            self.frequency_Hz(fsR=fsR, meR=meR) - nu_abs_Hz
        ) / Doppler_width_Hz
        result.setflags(write=False)
        return result


@dataclass(frozen=True)
class MomentAudit:
    """Raw moments of a positive discrete measure in Doppler coordinate."""

    moments: np.ndarray
    normalized_moments: np.ndarray
    support_min: float
    support_max: float
    positive_mass: float

    def __post_init__(self) -> None:
        moments = np.asarray(self.moments, dtype=float)
        normalized = np.asarray(self.normalized_moments, dtype=float)
        if moments.shape != (MOMENT_ORDER + 1,):
            raise ValueError("moments must have shape (5,)")
        if normalized.shape != moments.shape:
            raise ValueError("normalized moment shape mismatch")
        if not np.all(np.isfinite(moments)) or not np.all(np.isfinite(normalized)):
            raise ValueError("moments contain nonfinite values")
        if moments[0] <= 0.0 or self.positive_mass <= 0.0:
            raise ValueError("positive measure must have nonzero mass")
        moments = np.array(moments, copy=True)
        normalized = np.array(normalized, copy=True)
        moments.setflags(write=False)
        normalized.setflags(write=False)
        object.__setattr__(self, "moments", moments)
        object.__setattr__(self, "normalized_moments", normalized)


@dataclass(frozen=True)
class PositiveNullspaceWitness:
    """Two distinct positive cell-mass vectors with identical moments."""

    moment_matrix: np.ndarray
    baseline: np.ndarray
    plus: np.ndarray
    minus: np.ndarray
    null_direction: np.ndarray
    rank: int
    nullity: int
    moment_residual: float
    minimum_weight: float

    def __post_init__(self) -> None:
        matrix = np.asarray(self.moment_matrix, dtype=float)
        baseline = np.asarray(self.baseline, dtype=float)
        plus = np.asarray(self.plus, dtype=float)
        minus = np.asarray(self.minus, dtype=float)
        direction = np.asarray(self.null_direction, dtype=float)
        n = matrix.shape[1]
        if matrix.shape != (MOMENT_ORDER + 1, n):
            raise ValueError("moment matrix must have shape (5,n)")
        for name, vector in {
            "baseline": baseline,
            "plus": plus,
            "minus": minus,
            "null_direction": direction,
        }.items():
            if vector.shape != (n,):
                raise ValueError(f"{name} shape mismatch")
            if not np.all(np.isfinite(vector)):
                raise ValueError(f"{name} contains nonfinite values")
        if np.min(plus) <= 0.0 or np.min(minus) <= 0.0:
            raise ValueError("witness weights must be strictly positive")
        if np.linalg.norm(plus - minus) <= 0.0:
            raise ValueError("witness vectors must be distinct")
        frozen_arrays = []
        for array in (matrix, baseline, plus, minus, direction):
            frozen = np.array(array, copy=True)
            frozen.setflags(write=False)
            frozen_arrays.append(frozen)
        object.__setattr__(self, "moment_matrix", frozen_arrays[0])
        object.__setattr__(self, "baseline", frozen_arrays[1])
        object.__setattr__(self, "plus", frozen_arrays[2])
        object.__setattr__(self, "minus", frozen_arrays[3])
        object.__setattr__(self, "null_direction", frozen_arrays[4])


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def load_integrated_table(
    archive_path: str | Path,
    configuration: HyRecTableConfiguration,
) -> HyRecIntegratedTable:
    """Load one canonical table directly from the byte-locked ZIP archive."""

    archive_path = Path(archive_path)
    with zipfile.ZipFile(archive_path) as archive:
        payload = archive.read(configuration.member)
    values = np.loadtxt(io.BytesIO(payload), dtype=float)
    return HyRecIntegratedTable(
        configuration=configuration,
        sha256=sha256_bytes(payload),
        size_bytes=len(payload),
        values=values,
    )


def nearest_grid_distances(
    source_energy_eV: Iterable[float],
    reference_energy_eV: Iterable[float],
) -> tuple[np.ndarray, np.ndarray]:
    """Return nearest absolute energy differences and reference indices."""

    source = np.asarray(source_energy_eV, dtype=float)
    reference = np.asarray(reference_energy_eV, dtype=float)
    if source.ndim != 1 or reference.ndim != 1:
        raise ValueError("energy grids must be one dimensional")
    if not np.all(np.diff(reference) > 0.0):
        raise ValueError("reference grid must be strictly increasing")
    insertion = np.searchsorted(reference, source)
    distances = np.empty_like(source)
    indices = np.empty(source.shape, dtype=int)
    for i, (energy, position) in enumerate(zip(source, insertion, strict=True)):
        candidates: list[tuple[float, int]] = []
        for j in (position - 1, position):
            if 0 <= j < reference.size:
                candidates.append((abs(reference[j] - energy), int(j)))
        distances[i], indices[i] = min(candidates)
    distances.setflags(write=False)
    indices.setflags(write=False)
    return distances, indices


def raw_positive_moments_x(
    x: Iterable[float],
    weight: Iterable[float],
    *,
    order: int = MOMENT_ORDER,
) -> MomentAudit:
    """Compute raw moments of a finite positive discrete measure."""

    x_array = np.asarray(x, dtype=float)
    weight_array = np.asarray(weight, dtype=float)
    if x_array.ndim != 1 or weight_array.shape != x_array.shape:
        raise ValueError("x and weight must be one-dimensional with equal shape")
    if not np.all(np.isfinite(x_array)) or not np.all(np.isfinite(weight_array)):
        raise ValueError("measure contains nonfinite values")
    if np.min(weight_array) < 0.0:
        raise ValueError("measure weights must be nonnegative")
    mass = float(np.sum(weight_array))
    if mass <= 0.0:
        raise ValueError("measure must have positive mass")
    moments = np.asarray(
        [np.sum(weight_array * x_array**r) for r in range(order + 1)],
        dtype=float,
    )
    return MomentAudit(
        moments=moments,
        normalized_moments=moments / moments[0],
        support_min=float(np.min(x_array[weight_array > 0.0])),
        support_max=float(np.max(x_array[weight_array > 0.0])),
        positive_mass=mass,
    )


def cell_uniform_moment_matrix(
    intervals_x: np.ndarray,
    *,
    order: int = MOMENT_ORDER,
) -> np.ndarray:
    """Moment matrix for a unit-mass uniform measure inside each target cell.

    This is a diagnostic closure, not a claim about the v0.51 intra-cell
    COM--KHW distribution.  It provides a concrete admissible finite-volume
    basis in which the rank deficiency and positivity ambiguity can be
    exhibited constructively.
    """

    intervals = np.asarray(intervals_x, dtype=float)
    if intervals.ndim != 2 or intervals.shape[1] != 2:
        raise ValueError("intervals_x must have shape (n,2)")
    left = intervals[:, 0]
    right = intervals[:, 1]
    widths = right - left
    if np.min(widths) <= 0.0:
        raise ValueError("target intervals must have positive width")
    matrix = np.empty((order + 1, intervals.shape[0]), dtype=float)
    for r in range(order + 1):
        matrix[r] = (
            right ** (r + 1) - left ** (r + 1)
        ) / ((r + 1) * widths)
    return matrix


def cell_centre_moment_matrix(
    intervals_x: np.ndarray,
    *,
    order: int = MOMENT_ORDER,
) -> np.ndarray:
    """Moment matrix for the commonly attempted cell-centre closure."""

    intervals = np.asarray(intervals_x, dtype=float)
    if intervals.ndim != 2 or intervals.shape[1] != 2:
        raise ValueError("intervals_x must have shape (n,2)")
    centres = 0.5 * (intervals[:, 0] + intervals[:, 1])
    return np.vstack([centres**r for r in range(order + 1)])


def positive_nullspace_witness(
    moment_matrix: np.ndarray,
    *,
    safety_fraction: float = 0.2,
) -> PositiveNullspaceWitness:
    """Construct distinct positive vectors with identical constrained moments."""

    matrix = np.asarray(moment_matrix, dtype=float)
    if matrix.ndim != 2:
        raise ValueError("moment_matrix must be two dimensional")
    rows, columns = matrix.shape
    if rows != MOMENT_ORDER + 1:
        raise ValueError("moment_matrix must contain rows r=0,...,4")
    if columns <= rows:
        raise ValueError("witness requires more columns than moment constraints")
    rank = int(np.linalg.matrix_rank(matrix))
    nullity = columns - rank
    if nullity <= 0:
        raise ValueError("moment matrix has no numerical null space")
    _, singular_values, vh = np.linalg.svd(matrix, full_matrices=True)
    tolerance = max(matrix.shape) * np.finfo(float).eps * singular_values[0]
    numerical_rank = int(np.sum(singular_values > tolerance))
    if numerical_rank != rank:
        raise RuntimeError("inconsistent numerical rank estimates")
    direction = vh[rank].copy()
    direction /= np.linalg.norm(direction, ord=np.inf)
    baseline = np.full(columns, 1.0 / columns)
    nonzero = np.abs(direction) > 0.0
    epsilon_max = float(np.min(baseline[nonzero] / np.abs(direction[nonzero])))
    epsilon = safety_fraction * epsilon_max
    plus = baseline + epsilon * direction
    minus = baseline - epsilon * direction
    moment_residual = float(
        max(
            np.linalg.norm(matrix @ plus - matrix @ baseline, ord=np.inf),
            np.linalg.norm(matrix @ minus - matrix @ baseline, ord=np.inf),
            np.linalg.norm(matrix @ (plus - minus), ord=np.inf),
        )
    )
    return PositiveNullspaceWitness(
        moment_matrix=matrix,
        baseline=baseline,
        plus=plus,
        minus=minus,
        null_direction=direction,
        rank=rank,
        nullity=nullity,
        moment_residual=moment_residual,
        minimum_weight=float(min(np.min(plus), np.min(minus))),
    )


def support_second_moment_bound(intervals_x: np.ndarray) -> float:
    """Sharp raw-second-moment bound for positive measures on the target union."""

    intervals = np.asarray(intervals_x, dtype=float)
    if intervals.ndim != 2 or intervals.shape[1] != 2:
        raise ValueError("intervals_x must have shape (n,2)")
    maximum_absolute_x = float(np.max(np.abs(intervals)))
    return maximum_absolute_x**2


def positive_moment_feasibility(
    moment_matrix: np.ndarray,
    normalized_moments: np.ndarray,
) -> tuple[bool, np.ndarray | None, str]:
    """Check nonnegative feasibility for a fixed target-cell basis."""

    matrix = np.asarray(moment_matrix, dtype=float)
    target = np.asarray(normalized_moments, dtype=float)
    if matrix.shape[0] != target.size:
        raise ValueError("moment target size mismatch")
    result = linprog(
        np.zeros(matrix.shape[1]),
        A_eq=matrix,
        b_eq=target,
        bounds=(0.0, None),
        method="highs",
    )
    if not result.success:
        return False, None, str(result.message)
    weights = np.asarray(result.x, dtype=float)
    weights.setflags(write=False)
    return True, weights, str(result.message)


def projectable_support_violation(
    source_audit: MomentAudit,
    intervals_x: np.ndarray,
) -> tuple[bool, float, float]:
    """Return whether source ``m2/m0`` violates the target support bound."""

    bound = support_second_moment_bound(intervals_x)
    normalized_second = float(source_audit.normalized_moments[2])
    return normalized_second > bound, normalized_second, bound
