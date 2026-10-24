"""HYREC common-measure projection of the scalar COM--KHW event kernel.

This module is the PR-04 bridge between the positive event measure closed in
PR-03 and frequency-jump moments suitable for a native-HYREC adapter.  It does
*not* fit a normalization to HYREC.  For each already-released production edge
it uses the durable PR-03 scalar conductance as the zeroth-moment mass and
computes conditional jump moments from the same first-principles event kernel.

Conventions
-----------
* metric signature ``(-,+,+,+)`` (the local scalar projection is evaluated in
  the hydrogen tetrad);
* ordinary frequency ``nu`` in Hz, never angular frequency;
* ``Delta nu = nu_target - nu_source``;
* the photon energy transfer is ``h Delta nu`` and the atomic transfer is its
  negative on the same event;
* ``c``, ``h`` and ``k_B`` are retained explicitly;
* the common event tensors have units ``m^-3 s^-1 Hz^r``;
* source-conditioned moments have units ``Hz^r s^-1``.

The exact zero-transfer coherent identity is excluded from the same-cell
``Gamma_jump`` measure.  It cancels from the collision action and contributes
zero to every moment of positive order.
"""
from __future__ import annotations

from dataclasses import dataclass
import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Iterable, Mapping

import numpy as np
from scipy.constants import electron_volt
from scipy.special import xlogy

from . import pair_cell_conductance as PCC


COMMON_MODE_FACTOR = 8.0 * math.pi * PCC.dnu / PCC.c**3
MOMENT_MAX = 4

# The moment ratios are smoother than the resonant conductance itself because
# the exact durable C0 mass is supplied by PR-03.  These positive quadrature
# lanes are therefore deliberately smaller than the expensive v0.50 C0 lane,
# while the reference lane remains an independent refinement.
MOMENT_LANES: Mapping[str, Mapping[str, int | float]] = {
    "production": {
        "ob": 10,
        "om": 48,
        "of": 14,
        "nb": 16,
        "nl": 48,
        "nv": 16,
        "nf": 12,
        "nu": 20,
        "nu_pole": 56,
        "ny": 24,
        "ymax": 9.0,
    },
    "reference": {
        "ob": 18,
        "om": 96,
        "of": 28,
        "nb": 28,
        "nl": 80,
        "nv": 26,
        "nf": 22,
        "nu": 30,
        "nu_pole": 88,
        "ny": 36,
        "ymax": 10.0,
    },
}

# Same-cell conditional moments are more sensitive to the narrow resonant mean
# coordinate in the outer core cells.  Keep the economical production angular
# rule, but use the refined mean/pole/y rules that independently reduce the
# M2/M4 conditional-ratio error below 2e-6 at both core boundaries.
SAME_MOMENT_LANES: Mapping[str, Mapping[str, int | float]] = {
    "production": {
        **MOMENT_LANES["production"],
        "nu": 30,
        "nu_pole": 88,
        "ny": 36,
        "ymax": 10.0,
    },
    "reference": MOMENT_LANES["reference"],
}

HYREC2_SOURCE_COMMIT = "09e8243d0e08edd3603a94dfbc445ae06cafe139"
HYREC2_SOURCE_BLOBS = {
    "hydrogen.c": "233f174bfb1758fa910866310340ae1bfad703db",
    "hydrogen.h": "088b34a699efe5d6d3aefb158229e9fb83d9a586",
    "Alpha_inf.dat": "75b551fa1059984065d1569ee9c6ce654e2f058f",
    "R_inf.dat": "220d432db0bc763157202db8001819460d5638c3",
    "two_photon_tables.dat": "df04635e8fd5ed03481547a7967a14030d90a79b",
}
HYREC2_NVIRT = 311
HYREC2_NSUBLYA = 140
HYREC2_NDIFF = 80
HYREC2_DIFFUSION_START = HYREC2_NSUBLYA - HYREC2_NDIFF // 2
HYREC2_DIFFUSION_STOP = HYREC2_DIFFUSION_START + HYREC2_NDIFF


@dataclass(frozen=True)
class CommonMeasureMoments:
    """Discrete positive common event measure and jump tensors.

    ``frequency_moments_x[r,target,source]`` uses the dimensionless Doppler
    coordinate jump ``Delta x``.  ``frequency_moments_hz`` carries the same
    tensors multiplied by ``Doppler_width_Hz**r``.
    """

    intervals_x: np.ndarray
    labels: np.ndarray
    mode_measure_m3: np.ndarray
    equilibrium_weight_m3: np.ndarray
    frequency_moments_x: np.ndarray
    frequency_moments_hz: np.ndarray
    same_cell_jump_moments_x: np.ndarray
    Doppler_width_Hz: float
    nu_abs_Hz: float
    temperature_K: float
    source: str

    def __post_init__(self) -> None:
        intervals = np.asarray(self.intervals_x, dtype=float)
        labels = np.asarray(self.labels)
        mode = np.asarray(self.mode_measure_m3, dtype=float)
        equilibrium = np.asarray(self.equilibrium_weight_m3, dtype=float)
        moments_x = np.asarray(self.frequency_moments_x, dtype=float)
        moments_hz = np.asarray(self.frequency_moments_hz, dtype=float)
        same = np.asarray(self.same_cell_jump_moments_x, dtype=float)
        n = len(intervals)
        if intervals.shape != (n, 2) or labels.shape != (n,):
            raise ValueError("interval/label shape mismatch")
        if mode.shape != (n,) or equilibrium.shape != (n,):
            raise ValueError("measure shape mismatch")
        if np.any(mode <= 0.0) or np.any(equilibrium <= 0.0):
            raise ValueError("mode and equilibrium measures must be positive")
        if moments_x.shape != (MOMENT_MAX + 1, n, n):
            raise ValueError("frequency_moments_x must have shape (5,n,n)")
        if moments_hz.shape != moments_x.shape:
            raise ValueError("Hz and x moment tensors must have equal shape")
        if same.shape != (MOMENT_MAX + 1, n):
            raise ValueError("same-cell moment shape mismatch")
        if np.min(moments_x[0]) < -1e-30:
            raise ValueError("zeroth common-measure tensor must be nonnegative")
        parity = np.asarray([1.0, -1.0, 1.0, -1.0, 1.0])[:, None, None]
        scale_x = np.max(np.abs(moments_x), axis=(1, 2)) + 1e-300
        parity_residual = np.max(
            np.abs(moments_x - parity * np.swapaxes(moments_x, 1, 2))
            / scale_x[:, None, None]
        )
        if parity_residual > 5e-13:
            raise ValueError("common-measure exchange parity is inconsistent")
        diagonal = np.diagonal(moments_x, axis1=1, axis2=2)
        diagonal_scale = np.maximum(np.abs(same), 1e-300)
        if np.max(np.abs(diagonal - same) / diagonal_scale) > 5e-13:
            raise ValueError("same-cell registry must equal the tensor diagonal")
        scale_by_order = np.maximum(
            np.max(np.abs(moments_x), axis=(1, 2)), 1.0e-300
        )
        for order in range(MOMENT_MAX + 1):
            exchange = moments_x[order] - ((-1) ** order) * moments_x[order].T
            if np.max(np.abs(exchange)) > 5.0e-12 * scale_by_order[order]:
                raise ValueError(f"moment order {order} violates exchange parity")
        if np.max(np.abs(np.diag(moments_x[1]))) > 5.0e-14 * scale_by_order[1]:
            raise ValueError("same-cell first moment must vanish")
        if np.max(np.abs(np.diag(moments_x[3]))) > 5.0e-14 * scale_by_order[3]:
            raise ValueError("same-cell third moment must vanish")
        if np.min(moments_x[2]) < -5.0e-15 * scale_by_order[2]:
            raise ValueError("second common-measure moment must be nonnegative")
        if np.min(moments_x[4]) < -5.0e-15 * scale_by_order[4]:
            raise ValueError("fourth common-measure moment must be nonnegative")
        if not np.isfinite(self.Doppler_width_Hz) or self.Doppler_width_Hz <= 0:
            raise ValueError("Doppler width must be positive")
        powers = self.Doppler_width_Hz ** np.arange(MOMENT_MAX + 1)
        scale = np.maximum(np.abs(moments_hz), 1e-300)
        residual = np.max(
            np.abs(moments_hz - moments_x * powers[:, None, None]) / scale
        )
        if residual > 5e-13:
            raise ValueError("Hz/x moment conversion is inconsistent")
        for array in (
            intervals,
            labels,
            mode,
            equilibrium,
            moments_x,
            moments_hz,
            same,
        ):
            array.setflags(write=False)
        object.__setattr__(self, "intervals_x", intervals)
        object.__setattr__(self, "labels", labels)
        object.__setattr__(self, "mode_measure_m3", mode)
        object.__setattr__(self, "equilibrium_weight_m3", equilibrium)
        object.__setattr__(self, "frequency_moments_x", moments_x)
        object.__setattr__(self, "frequency_moments_hz", moments_hz)
        object.__setattr__(self, "same_cell_jump_moments_x", same)

    @property
    def state_count(self) -> int:
        return int(len(self.intervals_x))

    @property
    def activity_z(self) -> np.ndarray:
        return self.equilibrium_weight_m3 / self.mode_measure_m3

    def source_conditioned_moments(
        self,
        occupation: np.ndarray | None = None,
    ) -> np.ndarray:
        """Return ``Gamma,M1,...,M4`` for every source state.

        If ``occupation`` is supplied, each target contribution is multiplied
        by the exact Bose final-state factor ``1+f_target``.  The zeroth row is
        the active redistribution rate; diagonal coherent identity events are
        absent by construction.
        """
        if occupation is None:
            stimulation = np.ones(self.state_count)
        else:
            occupation = np.asarray(occupation, dtype=float)
            if occupation.shape != (self.state_count,):
                raise ValueError("occupation shape mismatch")
            if np.any(occupation < 0.0) or not np.all(np.isfinite(occupation)):
                raise ValueError("occupation must be finite and nonnegative")
            stimulation = 1.0 + occupation
        weighted = self.frequency_moments_hz * stimulation[None, :, None]
        return weighted.sum(axis=1) / self.equilibrium_weight_m3[None, :]

    def source_conditioned_jvp(self, direction: np.ndarray) -> np.ndarray:
        """Exact JVP with respect to the target occupation vector."""
        direction = np.asarray(direction, dtype=float)
        if direction.shape != (self.state_count,):
            raise ValueError("direction shape mismatch")
        return (
            self.frequency_moments_hz * direction[None, :, None]
        ).sum(axis=1) / self.equilibrium_weight_m3[None, :]

    def recoil_power_per_source_W(self, occupation: np.ndarray | None = None) -> np.ndarray:
        """Atomic recoil power per source photon, ``-h M1`` in watts."""
        return -PCC.h * self.source_conditioned_moments(occupation)[1]

    def fixed_stimulation_jump_generator(
        self,
        occupation: np.ndarray | None = None,
    ) -> np.ndarray:
        """Column-conservative positive jump generator for a frozen Bose field.

        This generator is a projection diagnostic, not a replacement for the
        nonlinear PR-02 collision update.  Off-diagonal target/source rates are
        ``C0[target,source] (1+f_target) / Pi_source``.  Same-cell active events
        contribute to jump moments but not to state-to-state population flow.
        """
        if occupation is None:
            stimulation = np.ones(self.state_count)
        else:
            occupation = np.asarray(occupation, dtype=float)
            if occupation.shape != (self.state_count,):
                raise ValueError("occupation shape mismatch")
            if np.any(occupation < 0.0) or not np.all(np.isfinite(occupation)):
                raise ValueError("occupation must be finite and nonnegative")
            stimulation = 1.0 + occupation
        rates = (
            self.frequency_moments_hz[0]
            * stimulation[:, None]
            / self.equilibrium_weight_m3[None, :]
        ).copy()
        np.fill_diagonal(rates, 0.0)
        if np.min(rates) < -1e-30:
            raise RuntimeError("fixed-stimulation jump rates lost positivity")
        generator = rates
        generator[np.diag_indices(self.state_count)] = -np.sum(rates, axis=0)
        return generator

    def backward_euler_jump_step(
        self,
        population: np.ndarray,
        dt_s: float,
        occupation: np.ndarray | None = None,
    ) -> np.ndarray:
        """Unconditionally positive fixed-stimulation projection step."""
        population = np.asarray(population, dtype=float)
        if population.shape != (self.state_count,):
            raise ValueError("population shape mismatch")
        if np.any(population < 0.0) or not np.all(np.isfinite(population)):
            raise ValueError("population must be finite and nonnegative")
        if not np.isfinite(dt_s) or dt_s <= 0.0:
            raise ValueError("dt_s must be positive")
        generator = self.fixed_stimulation_jump_generator(occupation)
        updated = np.linalg.solve(
            np.eye(self.state_count) - float(dt_s) * generator,
            population,
        )
        return np.real_if_close(updated, tol=1000).astype(float)

    @classmethod
    def from_npz(cls, path: str | Path) -> "CommonMeasureMoments":
        """Load the canonical v0.51 durable NPZ schema."""
        return load_common_measure_npz(Path(path))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_interval(interval: Iterable[float]) -> tuple[float, float]:
    left, right = map(float, interval)
    if not np.isfinite(left) or not np.isfinite(right) or right <= left:
        raise ValueError("interval must be finite and ordered")
    if PCC.nu_abs + left * PCC.dnu <= 0.0:
        raise ValueError("frequency interval must remain positive")
    return left, right


def interval_nodes(interval: Iterable[float], order: int) -> tuple[np.ndarray, np.ndarray]:
    left, right = validate_interval(interval)
    nodes, weights = PCC.leggauss(int(order))
    return (
        0.5 * (right - left) * nodes + 0.5 * (right + left),
        0.5 * (right - left) * weights,
    )


def interval_mode_measure_m3(interval: Iterable[float], *, order: int = 96) -> float:
    x, weights = interval_nodes(interval, order)
    nu = PCC.nu_abs + x * PCC.dnu
    return COMMON_MODE_FACTOR * float(np.dot(weights, nu**2))


def interval_equilibrium_weight_m3(
    interval: Iterable[float], *, order: int = 96
) -> float:
    x, weights = interval_nodes(interval, order)
    nu = PCC.nu_abs + x * PCC.dnu
    return COMMON_MODE_FACTOR * float(
        np.dot(weights, nu**2 * np.exp(-PCC.beta * PCC.h * nu))
    )


def _density(
    x_target: np.ndarray,
    x_source: np.ndarray,
    mu: float,
    *,
    amplitude_lane: str,
) -> np.ndarray:
    nu_source = PCC.nu_abs + x_source * PCC.dnu
    nu_target = PCC.nu_abs + x_target * PCC.dnu
    return (
        PCC.const_exact
        * np.exp(
            -PCC.beta * PCC.h * nu_source
            + PCC.logSmj(nu_source, nu_target, mu)
        )
        * nu_source
        * nu_target
        * PCC.exact_amp2(
            nu_source,
            nu_target,
            mu,
            amplitude_lane=amplitude_lane,
        )
    )


def _moment_vector(delta_x: np.ndarray, maximum: int = MOMENT_MAX) -> np.ndarray:
    return np.stack([delta_x**power for power in range(maximum + 1)], axis=0)


def _tensor_frequency_moments(
    target: tuple[float, float],
    source: tuple[float, float],
    mu: float,
    *,
    order: int,
    amplitude_lane: str,
) -> np.ndarray:
    x_source_1d, source_weights = interval_nodes(source, order)
    x_target_1d, target_weights = interval_nodes(target, order)
    x_source = np.broadcast_to(x_source_1d, (order, order))
    x_target = np.broadcast_to(x_target_1d[:, None], (order, order))
    weights = target_weights[:, None] * source_weights[None, :]
    density = _density(
        x_target,
        x_source,
        mu,
        amplitude_lane=amplitude_lane,
    )
    moments = _moment_vector(x_target - x_source)
    return np.asarray(
        [float(np.sum(weights * density * moments[r])) for r in range(MOMENT_MAX + 1)]
    )


def _uv_frequency_moments(
    target: tuple[float, float],
    source: tuple[float, float],
    mu: float,
    *,
    nb: int,
    nl: int,
    nv: int,
    amplitude_lane: str,
    local_half: float = 0.08,
) -> np.ndarray:
    target_left, target_right = validate_interval(target)
    source_left, source_right = validate_interval(source)
    u_min = 0.5 * (target_left + source_left)
    u_max = 0.5 * (target_right + source_right)
    pole_scale = PCC.gamma / PCC.dnu
    breakpoints = [
        u_min,
        u_max,
        0.5 * (target_left + source_right),
        0.5 * (target_right + source_left),
    ]
    if u_min < 0.0 < u_max:
        width = min(local_half, 0.45 * (u_max - u_min))
        breakpoints += [max(u_min, -width), 0.0, min(u_max, width)]
    breakpoints = sorted(
        set(
            round(float(value), 15)
            for value in breakpoints
            if u_min - 1e-14 <= value <= u_max + 1e-14
        )
    )

    u_nodes: list[float] = []
    u_weights: list[float] = []
    for left, right in zip(breakpoints[:-1], breakpoints[1:]):
        if right - left < 1e-14:
            continue
        tangent = (
            u_min < 0.0 < u_max
            and abs(left) <= local_half + 1e-14
            and abs(right) <= local_half + 1e-14
        )
        if tangent:
            nodes, weights = PCC.leggauss(nl)
            theta_left = math.atan(left / pole_scale)
            theta_right = math.atan(right / pole_scale)
            theta = (
                0.5 * (theta_right - theta_left) * nodes
                + 0.5 * (theta_right + theta_left)
            )
            values = pole_scale * np.tan(theta)
            transformed = (
                0.5
                * (theta_right - theta_left)
                * weights
                * pole_scale
                / np.cos(theta) ** 2
            )
        else:
            nodes, weights = PCC.leggauss(nb)
            values = 0.5 * (right - left) * nodes + 0.5 * (right + left)
            transformed = 0.5 * (right - left) * weights
        u_nodes.extend(values.tolist())
        u_weights.extend(transformed.tolist())

    v_nodes, v_weights = PCC.leggauss(nv)
    total = np.zeros(MOMENT_MAX + 1)
    for u_value, u_weight in zip(u_nodes, u_weights):
        v_min = max(target_left - u_value, u_value - source_right)
        v_max = min(target_right - u_value, u_value - source_left)
        if v_max <= v_min:
            continue
        v = 0.5 * (v_max - v_min) * v_nodes + 0.5 * (v_max + v_min)
        weights = 0.5 * (v_max - v_min) * v_weights
        x_target = u_value + v
        x_source = u_value - v
        density = _density(
            x_target,
            x_source,
            mu,
            amplitude_lane=amplitude_lane,
        )
        powers = _moment_vector(x_target - x_source)
        # dx_t dx_s = 2 du dv.
        total += 2.0 * u_weight * np.asarray(
            [float(np.dot(weights, density * powers[r])) for r in range(MOMENT_MAX + 1)]
        )
    return total


def _crosses_resonance_mean(
    target: tuple[float, float], source: tuple[float, float]
) -> bool:
    return 0.5 * (target[0] + source[0]) < 0.0 < 0.5 * (
        target[1] + source[1]
    )


def _touching_intervals(
    target: tuple[float, float], source: tuple[float, float]
) -> bool:
    return abs(target[1] - source[0]) < 1e-14 or abs(source[1] - target[0]) < 1e-14


def integrate_disjoint_frequency_moments_x(
    target: Iterable[float],
    source: Iterable[float],
    *,
    lane: str = "production",
    amplitude_lane: str = "full",
) -> np.ndarray:
    """Integrate ``C^(r)=integral (Delta x)^r dC`` for a disjoint pair.

    The result includes the physical common photon-mode factor and therefore
    has units ``m^-3 s^-1`` for every dimensionless-x moment row.
    """
    if lane not in MOMENT_LANES:
        raise ValueError("lane must be 'production' or 'reference'")
    target = validate_interval(target)
    source = validate_interval(source)
    if max(target[0], source[0]) < min(target[1], source[1]):
        raise ValueError("pair intervals must not overlap")
    parameters = MOMENT_LANES[lane]
    total = np.zeros(MOMENT_MAX + 1)

    def accumulate(mu: float, angular_weight: float, *, force_uv: bool = False) -> None:
        nonlocal total
        use_uv = force_uv or _crosses_resonance_mean(target, source) or (
            mu > 0.995 and _touching_intervals(target, source)
        )
        if use_uv:
            frequency = _uv_frequency_moments(
                target,
                source,
                mu,
                nb=int(parameters["nb"]),
                nl=int(parameters["nl"]),
                nv=int(parameters["nv"]),
                amplitude_lane=amplitude_lane,
            )
        else:
            frequency = _tensor_frequency_moments(
                target,
                source,
                mu,
                order=int(parameters["nf"]),
                amplitude_lane=amplitude_lane,
            )
        phase = 0.75 * (1.0 + mu**2)
        total += angular_weight * phase * frequency

    nodes, weights = PCC.leggauss(int(parameters["ob"]))
    c_max = math.sqrt(0.005)
    c_values = 0.5 * c_max * (nodes + 1.0)
    c_weights = 0.5 * c_max * weights
    for c_value, weight in zip(c_values, c_weights):
        mu = -1.0 + 2.0 * c_value**2
        accumulate(float(mu), float(2.0 * c_value * weight), force_uv=True)

    nodes, weights = PCC.leggauss(int(parameters["om"]))
    lower, upper = -0.99, 0.999
    mus = 0.5 * (upper - lower) * nodes + 0.5 * (upper + lower)
    mweights = 0.25 * (upper - lower) * weights
    for mu, weight in zip(mus, mweights):
        accumulate(float(mu), float(weight))

    nodes, weights = PCC.leggauss(int(parameters["of"]))
    t_max = math.sqrt(0.001)
    t_values = 0.5 * t_max * (nodes + 1.0)
    t_weights = 0.5 * t_max * weights
    for t_value, weight in zip(t_values, t_weights):
        mu = 1.0 - t_value**2
        accumulate(float(mu), float(t_value * weight))

    result = COMMON_MODE_FACTOR * total
    if not np.all(np.isfinite(result)) or result[0] <= 0.0:
        raise FloatingPointError("invalid disjoint common-measure moments")
    return result


def conservative_conditional_moment_projection(
    raw_moments_x: np.ndarray,
    durable_conductance_m3_s: float,
) -> np.ndarray:
    """Use the durable C0 mass and direct conditional moment ratios.

    This is a conservation projection, not a fitted normalization: the supplied
    mass is the same PR-03 event integral already accepted by the collision
    network.  No HYREC output or adjustable parameter enters the operation.
    """
    raw = np.asarray(raw_moments_x, dtype=float)
    durable = float(durable_conductance_m3_s)
    if raw.shape != (MOMENT_MAX + 1,) or raw[0] <= 0.0:
        raise ValueError("raw moment vector must have a positive zeroth mass")
    if not np.isfinite(durable) or durable <= 0.0:
        raise ValueError("durable conductance must be positive")
    result = durable * raw / raw[0]
    result[0] = durable
    return result


def _u_rule_interval(
    interval: tuple[float, float], regular_order: int, pole_order: int
) -> tuple[np.ndarray, np.ndarray]:
    left, right = validate_interval(interval)
    pole_scale = PCC.gamma / PCC.dnu
    local_half = min(0.08, 0.45 * (right - left))
    breakpoints = [left, right]
    if left < 0.0 < right:
        breakpoints += [max(left, -local_half), 0.0, min(right, local_half)]
    breakpoints = sorted(set(round(value, 15) for value in breakpoints))
    values: list[float] = []
    output_weights: list[float] = []
    for a, b in zip(breakpoints[:-1], breakpoints[1:]):
        if b - a < 1e-14:
            continue
        tangent = (
            left < 0.0 < right
            and abs(a) <= local_half + 1e-14
            and abs(b) <= local_half + 1e-14
        )
        if tangent:
            nodes, weights = PCC.leggauss(pole_order)
            theta_a = math.atan(a / pole_scale)
            theta_b = math.atan(b / pole_scale)
            theta = 0.5 * (theta_b - theta_a) * nodes + 0.5 * (
                theta_b + theta_a
            )
            u = pole_scale * np.tan(theta)
            w = (
                0.5
                * (theta_b - theta_a)
                * weights
                * pole_scale
                / np.cos(theta) ** 2
            )
        else:
            nodes, weights = PCC.leggauss(regular_order)
            u = 0.5 * (b - a) * nodes + 0.5 * (b + a)
            w = 0.5 * (b - a) * weights
        values.extend(u.tolist())
        output_weights.extend(w.tolist())
    return np.asarray(values), np.asarray(output_weights)


def _same_interval_frequency_moments(
    interval: tuple[float, float],
    mu: float,
    *,
    parameters: Mapping[str, int | float],
    amplitude_lane: str,
) -> np.ndarray:
    s = math.sqrt(max(0.0, (1.0 - mu) / 2.0))
    if s == 0.0:
        return np.zeros(MOMENT_MAX + 1)
    left, right = validate_interval(interval)
    u_values, u_weights = _u_rule_interval(
        interval,
        int(parameters["nu"]),
        int(parameters["nu_pole"]),
    )
    y_nodes, y_weights = PCC.leggauss(int(parameters["ny"]))
    y_max_global = float(parameters["ymax"])
    total = np.zeros(MOMENT_MAX + 1)
    for u, u_weight in zip(u_values, u_weights):
        half_width = min(u - left, right - u)
        if half_width <= 0.0:
            continue
        y_max = min(y_max_global, half_width / s)
        if y_max <= 0.0:
            continue
        y = y_max * y_nodes
        weights = y_max * y_weights
        v = s * y
        x_target = u + v
        x_source = u - v
        density = _density(
            x_target,
            x_source,
            mu,
            amplitude_lane=amplitude_lane,
        )
        powers = _moment_vector(x_target - x_source)
        # dx_t dx_s = 2 du dv = 2 s du dy.
        total += 2.0 * s * u_weight * np.asarray(
            [float(np.dot(weights, density * powers[r])) for r in range(MOMENT_MAX + 1)]
        )
    return total


def integrate_same_interval_jump_moments_x(
    interval: Iterable[float],
    *,
    lane: str = "production",
    amplitude_lane: str = "full",
) -> np.ndarray:
    """Positive active same-cell jump measure through fourth order.

    The exact coherent forward identity at ``Delta x=0`` is absent.  Odd
    moments vanish exactly by target/source exchange symmetry and are set to
    signed zero after the numerical parity audit.
    """
    if lane not in MOMENT_LANES:
        raise ValueError("lane must be 'production' or 'reference'")
    interval = validate_interval(interval)
    parameters = SAME_MOMENT_LANES[lane]
    total = np.zeros(MOMENT_MAX + 1)

    def accumulate(mu: float, angular_weight: float) -> None:
        nonlocal total
        frequency = _same_interval_frequency_moments(
            interval,
            mu,
            parameters=parameters,
            amplitude_lane=amplitude_lane,
        )
        total += angular_weight * 0.75 * (1.0 + mu**2) * frequency

    nodes, weights = PCC.leggauss(int(parameters["ob"]))
    c_max = math.sqrt(0.005)
    c_values = 0.5 * c_max * (nodes + 1.0)
    c_weights = 0.5 * c_max * weights
    for c_value, weight in zip(c_values, c_weights):
        mu = -1.0 + 2.0 * c_value**2
        accumulate(float(mu), float(2.0 * c_value * weight))

    nodes, weights = PCC.leggauss(int(parameters["om"]))
    lower, upper = -0.99, 0.999
    mus = 0.5 * (upper - lower) * nodes + 0.5 * (upper + lower)
    mweights = 0.25 * (upper - lower) * weights
    for mu, weight in zip(mus, mweights):
        accumulate(float(mu), float(weight))

    nodes, weights = PCC.leggauss(int(parameters["of"]))
    t_max = math.sqrt(0.001)
    t_values = 0.5 * t_max * (nodes + 1.0)
    t_weights = 0.5 * t_max * weights
    for t_value, weight in zip(t_values, t_weights):
        mu = 1.0 - t_value**2
        accumulate(float(mu), float(t_value * weight))

    result = COMMON_MODE_FACTOR * total
    odd_scale = max(abs(result[0]), abs(result[2]), abs(result[4]), 1e-300)
    if max(abs(result[1]), abs(result[3])) > 5e-10 * odd_scale:
        raise FloatingPointError("same-cell odd moment parity failed")
    result[1] = 0.0
    result[3] = 0.0
    if result[0] <= 0.0 or result[2] < 0.0 or result[4] < 0.0:
        raise FloatingPointError("same-cell jump measure lost positivity")
    return result


def build_oriented_tensor(
    pair_vectors_x: Mapping[tuple[int, int], np.ndarray],
    same_cell_vectors_x: Mapping[int, np.ndarray],
    state_count: int,
) -> np.ndarray:
    """Assemble oriented moment tensors with exact exchange parity."""
    tensor = np.zeros((MOMENT_MAX + 1, int(state_count), int(state_count)))
    for (a, b), values in pair_vectors_x.items():
        if not (0 <= a < b < state_count):
            raise ValueError("pair keys must use canonical a<b ordering")
        values = np.asarray(values, dtype=float)
        if values.shape != (MOMENT_MAX + 1,):
            raise ValueError("pair moment vector shape mismatch")
        tensor[:, a, b] = values
        tensor[:, b, a] = values * np.asarray([1, -1, 1, -1, 1])
    for state, values in same_cell_vectors_x.items():
        values = np.asarray(values, dtype=float)
        if values.shape != (MOMENT_MAX + 1,):
            raise ValueError("same-cell moment vector shape mismatch")
        tensor[:, state, state] = values
    return tensor


def native_diffusion_centres_from_csv(path: Path) -> dict[str, np.ndarray]:
    """Read the durable 80-bin HYREC diffusion snapshot.

    The CSV contains native virtual-state energies in eV and the primitive
    adjacent ``Aup``/``Adn`` rates.  These rates are retained as a diagnostic
    only: in HYREC they enter an escape-compressed real/virtual Schur system
    and are not directly equal to photon per-source COM--KHW rates.
    """
    rows: list[dict[str, float]] = []
    with Path(path).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rows.append({key: float(value) for key, value in row.items()})
    if len(rows) != HYREC2_NDIFF:
        raise ValueError("native diffusion CSV must contain 80 rows")
    virtual_index = np.asarray([int(row["virtual_index"]) for row in rows], dtype=int)
    if not np.array_equal(
        virtual_index, np.arange(HYREC2_DIFFUSION_START, HYREC2_DIFFUSION_STOP)
    ):
        raise ValueError("unexpected native diffusion index registry")
    energy_eV = np.asarray([row["Eb_eV"] for row in rows], dtype=float)
    frequency_Hz = energy_eV * electron_volt / PCC.h
    x = (frequency_Hz - PCC.nu_abs) / PCC.dnu
    return {
        "virtual_index": virtual_index,
        "energy_eV": energy_eV,
        "frequency_Hz": frequency_Hz,
        "x": x,
        "Aup_s_inv": np.asarray([row["Aup_s_inv"] for row in rows]),
        "Adn_s_inv": np.asarray([row["Adn_s_inv"] for row in rows]),
        "detailed_balance_target": np.asarray([row["target"] for row in rows]),
        "detailed_balance_reconstructed": np.asarray(
            [row["reconstructed"] for row in rows]
        ),
    }


def native_voronoi_intervals(
    centres_x: np.ndarray,
    *,
    window: tuple[float, float] = (-21.25, 21.25),
    split_line_centre: bool = True,
) -> np.ndarray:
    """Voronoi cells of native HYREC centres clipped to the production window."""
    centres = np.asarray(centres_x, dtype=float)
    if centres.ndim != 1 or len(centres) < 2 or np.any(np.diff(centres) <= 0):
        raise ValueError("centres must be a strictly increasing vector")
    left, right = validate_interval(window)
    midpoints = 0.5 * (centres[:-1] + centres[1:])
    edges = np.concatenate(([-np.inf], midpoints, [np.inf]))
    intervals: list[tuple[float, float]] = []
    for index in range(len(centres)):
        a = max(left, float(edges[index]))
        b = min(right, float(edges[index + 1]))
        if b <= a:
            continue
        if split_line_centre and a < 0.0 < b:
            intervals.extend(((a, 0.0), (0.0, b)))
        else:
            intervals.append((a, b))
    output = np.asarray(intervals, dtype=float)
    if len(output) == 0 or abs(output[0, 0] - left) > 1e-12 or abs(output[-1, 1] - right) > 1e-12:
        raise ValueError("native Voronoi cells do not cover the requested window")
    if np.max(np.abs(output[:-1, 1] - output[1:, 0])) > 1e-12:
        raise ValueError("native Voronoi cells are not contiguous")
    return output


def raw_native_adjacent_jump_moments(
    native: Mapping[str, np.ndarray],
) -> np.ndarray:
    """Diagnostic Kramers--Moyal moments of primitive Aup/Adn rates.

    This is deliberately named ``raw_native``: it is not a physical
    common-measure parity target until the HYREC virtual-state/escape map is
    applied in PR-05.
    """
    frequency = np.asarray(native["frequency_Hz"], dtype=float)
    up = np.asarray(native["Aup_s_inv"], dtype=float)
    down = np.asarray(native["Adn_s_inv"], dtype=float)
    n = len(frequency)
    output = np.zeros((MOMENT_MAX + 1, n))
    for i in range(n):
        if i + 1 < n and up[i] > 0:
            delta = frequency[i + 1] - frequency[i]
            output[:, i] += up[i] * delta ** np.arange(MOMENT_MAX + 1)
        if i - 1 >= 0 and down[i] > 0:
            delta = frequency[i - 1] - frequency[i]
            output[:, i] += down[i] * delta ** np.arange(MOMENT_MAX + 1)
    return output


def write_source_lock(path: Path, *, evidence: Mapping[str, object]) -> None:
    payload = {
        "classification": "PR04_HYREC_COMMON_MEASURE_SOURCE_LOCK",
        "frequency_convention": {
            "coordinate": "ordinary frequency nu",
            "unit": "Hz",
            "increment": "Delta_nu = nu_target - nu_source",
            "energy_increment": "Delta_E_gamma = h Delta_nu",
            "atomic_recoil_increment": "Delta_E_atom = -h Delta_nu",
        },
        "common_measure": {
            "C_r_units": "m^-3 s^-1 Hz^r",
            "source_conditioned_M_r_units": "Hz^r s^-1",
            "Gamma": "M_0 active redistributive rate; coherent identity excluded",
            "normalization_policy": "PR03 durable C0 mass plus direct conditional moment ratios; no HYREC fit",
        },
        "hyrec_original": {
            "role": "historical full time-dependent radiative-transfer reference",
            "release": "October 2012 stable version listed by the official HyRec page",
            "status": "REFERENCE_ONLY_NOT_A_PR04_EXECUTION_DEPENDENCY",
            "archive_bytes_or_sha256": "NOT_RETRIEVED_IN_NETWORK_ISOLATED_RUNTIME",
        },
        "hyrec2": {
            "repository": "nanoomlee/HYREC-2",
            "commit": HYREC2_SOURCE_COMMIT,
            "blob_sha1": HYREC2_SOURCE_BLOBS,
            "native_state": "(2s,2p)+311 virtual photon states",
            "landmarks": {
                "NVIRT": HYREC2_NVIRT,
                "NSUBLYA": HYREC2_NSUBLYA,
                "NDIFF": HYREC2_NDIFF,
                "diffusion_zero_based": [
                    HYREC2_DIFFUSION_START,
                    HYREC2_DIFFUSION_STOP - 1,
                ],
            },
            "role": "exact pinned FULL-mode operator/convention source and later production-parity target; SWIFT corrections are not the anisotropic kernel",
        },
        "native_rate_firewall": {
            "status": "RAW_RATE_DIRECT_EQUALITY_REJECTED_BY_VARIABLE_MISMATCH",
            "reason": "Aup/Adn populate the virtual-state T matrix and escape-compressed diagonal; they are not direct photon per-source rates",
            "next_resolution": "PR05 RadiationFeedback/native virtual-state adapter",
        },
        "evidence": dict(evidence),
    }
    Path(path).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


@dataclass(frozen=True)
class ScalarBoseAction:
    """Finite-volume scalar Bose collision action on the common measure.

    ``number_action_m3_s`` is the action on cell photon number density and
    ``occupation_action_s_inv`` is the corresponding action on occupation.
    The entropy/free-energy production is evaluated with the thermodynamic
    force ``psi_i=log[f_i/(1+f_i)]-log(z_i)`` and is nonpositive.
    """

    occupation_action_s_inv: np.ndarray
    number_action_m3_s: np.ndarray
    number_residual_m3_s: float
    entropy_production_m3_s: float
    photon_power_W_m3: float
    atom_power_W_m3: float
    energy_ledger_residual_W_m3: float
    gross_pair_flux_m3_s: float
    minimum_occupation: float


@dataclass(frozen=True)
class ScalarBoseJVP:
    occupation_action_jvp_s_inv: np.ndarray
    number_action_jvp_m3_s: np.ndarray
    number_residual_jvp_m3_s: float
    photon_power_jvp_W_m3: float
    atom_power_jvp_W_m3: float


@dataclass(frozen=True)
class ScalarImplicitStep:
    occupation: np.ndarray
    converged: bool
    newton_iterations: int
    dt_s: float
    residual_relative: float
    minimum_occupation: float
    explicit_trial_minimum: float
    number_before_m3: float
    number_after_m3: float
    number_relative_change: float
    free_energy_before_m3: float
    free_energy_after_m3: float
    free_energy_change_m3: float


def _validate_scalar_occupation(
    moments: CommonMeasureMoments, occupation: np.ndarray
) -> np.ndarray:
    f = np.asarray(occupation, dtype=float)
    if f.shape != (moments.state_count,):
        raise ValueError("occupation shape mismatch")
    if np.any(f <= 0.0) or not np.all(np.isfinite(f)):
        raise ValueError("occupation must be finite and strictly positive")
    return f


def scalar_bose_free_energy_m3(
    moments: CommonMeasureMoments, occupation: np.ndarray
) -> float:
    """Discrete Bose free energy (up to an irrelevant additive constant).

    Its derivative with respect to the cell number density is
    ``log[f/(1+f)]-log(z)``.  The return value has units ``m^-3``.
    """
    f = _validate_scalar_occupation(moments, occupation)
    z = moments.activity_z
    density = (
        xlogy(f, f)
        - xlogy(1.0 + f, 1.0 + f)
        - f * np.log(z)
    )
    return float(np.dot(moments.mode_measure_m3, density))


def scalar_bose_photon_number_m3(
    moments: CommonMeasureMoments, occupation: np.ndarray
) -> float:
    f = _validate_scalar_occupation(moments, occupation)
    return float(np.dot(moments.mode_measure_m3, f))


def apply_scalar_bose_operator(
    moments: CommonMeasureMoments, occupation: np.ndarray
) -> ScalarBoseAction:
    """Apply the conservative nonlinear scalar Bose edge operator.

    For every unordered pair ``i<j`` the number flux into ``i`` is

    ``S_ij (1+f_i)(1+f_j) (phi_j-phi_i)``,

    with ``phi_i=f_i/[z_i(1+f_i)]`` and ``z_i=Pi_i/g_i``.  The same event
    supplies the first frequency moment and therefore the photon/atom energy
    ledger.  No geometry or HYREC output normalization enters this operator.
    """
    f = _validate_scalar_occupation(moments, occupation)
    g = moments.mode_measure_m3
    z = moments.activity_z
    C0 = moments.frequency_moments_hz[0]
    C1 = moments.frequency_moments_hz[1]
    phi = f / (z * (1.0 + f))
    number = np.zeros_like(f)
    photon_power = 0.0
    gross = 0.0
    for i in range(moments.state_count):
        for j in range(i + 1, moments.state_count):
            S = float(C0[i, j])
            if S <= 0.0:
                continue
            bose = (1.0 + f[i]) * (1.0 + f[j])
            activity_difference = phi[j] - phi[i]
            flux = S * bose * activity_difference
            number[i] += flux
            number[j] -= flux
            gross += abs(flux)

            # C1[i,j] is the common-measure moment for j -> i and the
            # reverse oriented moment is exactly -C1[i,j].
            forward_minus_reverse = (
                f[j] * (1.0 + f[i]) / z[j]
                - f[i] * (1.0 + f[j]) / z[i]
            )
            photon_power += PCC.h * float(C1[i, j]) * forward_minus_reverse

    occupation_action = number / g
    number_residual = float(np.sum(number))
    psi = np.log(phi)
    entropy_production = float(np.dot(psi, number))
    atom_power = -photon_power
    return ScalarBoseAction(
        occupation_action_s_inv=occupation_action,
        number_action_m3_s=number,
        number_residual_m3_s=number_residual,
        entropy_production_m3_s=entropy_production,
        photon_power_W_m3=float(photon_power),
        atom_power_W_m3=float(atom_power),
        energy_ledger_residual_W_m3=float(photon_power + atom_power),
        gross_pair_flux_m3_s=float(gross),
        minimum_occupation=float(np.min(f)),
    )


def apply_scalar_bose_jvp(
    moments: CommonMeasureMoments,
    occupation: np.ndarray,
    direction: np.ndarray,
) -> ScalarBoseJVP:
    """Exact Fréchet derivative of :func:`apply_scalar_bose_operator`."""
    f = _validate_scalar_occupation(moments, occupation)
    df = np.asarray(direction, dtype=float)
    if df.shape != f.shape or not np.all(np.isfinite(df)):
        raise ValueError("direction shape mismatch or nonfinite entries")
    g = moments.mode_measure_m3
    z = moments.activity_z
    C0 = moments.frequency_moments_hz[0]
    C1 = moments.frequency_moments_hz[1]
    phi = f / (z * (1.0 + f))
    dphi = df / (z * (1.0 + f) ** 2)
    number = np.zeros_like(f)
    photon_power = 0.0
    for i in range(moments.state_count):
        for j in range(i + 1, moments.state_count):
            S = float(C0[i, j])
            if S <= 0.0:
                continue
            A = (1.0 + f[i]) * (1.0 + f[j])
            dA = df[i] * (1.0 + f[j]) + (1.0 + f[i]) * df[j]
            dflux = S * (
                dA * (phi[j] - phi[i]) + A * (dphi[j] - dphi[i])
            )
            number[i] += dflux
            number[j] -= dflux

            d_forward_minus_reverse = (
                df[j] * (1.0 + f[i]) / z[j]
                + f[j] * df[i] / z[j]
                - df[i] * (1.0 + f[j]) / z[i]
                - f[i] * df[j] / z[i]
            )
            photon_power += (
                PCC.h * float(C1[i, j]) * d_forward_minus_reverse
            )
    atom_power = -photon_power
    return ScalarBoseJVP(
        occupation_action_jvp_s_inv=number / g,
        number_action_jvp_m3_s=number,
        number_residual_jvp_m3_s=float(np.sum(number)),
        photon_power_jvp_W_m3=float(photon_power),
        atom_power_jvp_W_m3=float(atom_power),
    )


def scalar_bose_equilibrium_family(
    moments: CommonMeasureMoments, activity: float = 1.0
) -> np.ndarray:
    """Return the exact discrete Bose--Einstein null family.

    ``activity*z_i`` must stay below one.  The dilute physical line state is
    obtained for activity of order unity because ``z_i`` is tiny.
    """
    q = float(activity)
    qz = q * moments.activity_z
    if q <= 0.0 or np.any(qz >= 1.0):
        raise ValueError("activity must be positive with activity*z_i < 1")
    return qz / (1.0 - qz)


def implicit_scalar_bose_step(
    moments: CommonMeasureMoments,
    occupation_old: np.ndarray,
    *,
    dt_s: float,
    relative_tolerance: float = 2.0e-12,
    maximum_iterations: int = 30,
) -> ScalarImplicitStep:
    """Backward Euler in log occupation with an exact dense JVP Jacobian.

    The logarithmic variable guarantees strict positivity.  The state count is
    only 17 in PR-04A, so forming the exact dense Jacobian from the analytic
    JVP is deterministic and more transparent than a preconditioned Krylov
    solve at this stage.
    """
    old = _validate_scalar_occupation(moments, occupation_old).copy()
    dt = float(dt_s)
    if not np.isfinite(dt) or dt <= 0.0:
        raise ValueError("dt_s must be finite and positive")
    y = np.log(old)
    scale = max(float(np.linalg.norm(old)), 1.0e-300)
    explicit_trial = old + dt * apply_scalar_bose_operator(
        moments, old
    ).occupation_action_s_inv
    converged = False
    residual_relative = math.inf
    iterations = 0

    def residual(current_y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        current_f = np.exp(np.clip(current_y, -745.0, 700.0))
        action = apply_scalar_bose_operator(
            moments, current_f
        ).occupation_action_s_inv
        return current_f - old - dt * action, current_f

    for iterations in range(1, int(maximum_iterations) + 1):
        r, f = residual(y)
        residual_relative = float(np.linalg.norm(r) / scale)
        if residual_relative < relative_tolerance:
            converged = True
            break
        jacobian = np.empty((moments.state_count, moments.state_count))
        for column in range(moments.state_count):
            dy = np.zeros(moments.state_count)
            dy[column] = 1.0
            df = f * dy
            jvp = apply_scalar_bose_jvp(
                moments, f, df
            ).occupation_action_jvp_s_inv
            jacobian[:, column] = df - dt * jvp
        try:
            step = np.linalg.solve(jacobian, -r)
        except np.linalg.LinAlgError as exc:
            raise RuntimeError("implicit common-measure Jacobian is singular") from exc
        base_norm = float(np.linalg.norm(r))
        accepted = False
        alpha = 1.0
        for _ in range(24):
            trial_y = y + alpha * step
            trial_r, _ = residual(trial_y)
            if np.linalg.norm(trial_r) < base_norm:
                y = trial_y
                accepted = True
                break
            alpha *= 0.5
        if not accepted:
            raise RuntimeError("implicit common-measure Newton line search failed")

    final_r, final_f = residual(y)
    residual_relative = float(np.linalg.norm(final_r) / scale)
    if residual_relative < relative_tolerance:
        converged = True
    before_number = scalar_bose_photon_number_m3(moments, old)
    after_number = scalar_bose_photon_number_m3(moments, final_f)
    before_free = scalar_bose_free_energy_m3(moments, old)
    after_free = scalar_bose_free_energy_m3(moments, final_f)
    return ScalarImplicitStep(
        occupation=final_f,
        converged=bool(converged),
        newton_iterations=int(iterations),
        dt_s=dt,
        residual_relative=residual_relative,
        minimum_occupation=float(np.min(final_f)),
        explicit_trial_minimum=float(np.min(explicit_trial)),
        number_before_m3=before_number,
        number_after_m3=after_number,
        number_relative_change=float(
            abs(after_number - before_number) / (abs(before_number) + 1.0e-300)
        ),
        free_energy_before_m3=before_free,
        free_energy_after_m3=after_free,
        free_energy_change_m3=float(after_free - before_free),
    )


def save_common_measure_npz(
    path: Path,
    moments: CommonMeasureMoments,
    **extra: np.ndarray | float | str,
) -> None:
    payload: dict[str, np.ndarray] = {
        "classification": np.asarray("PR04A_HYREC_COMMON_MEASURE"),
        "state_intervals_x": moments.intervals_x,
        "state_labels": moments.labels,
        "mode_measure_m3": moments.mode_measure_m3,
        "equilibrium_weight_m3": moments.equilibrium_weight_m3,
        "frequency_moments_x_m3_sInv": moments.frequency_moments_x,
        "frequency_moments_Hz_m3_sInv": moments.frequency_moments_hz,
        "same_cell_jump_moments_x_m3_sInv": moments.same_cell_jump_moments_x,
        "Doppler_width_Hz": np.asarray(moments.Doppler_width_Hz),
        "nu_abs_Hz": np.asarray(moments.nu_abs_Hz),
        "temperature_K": np.asarray(moments.temperature_K),
        "source": np.asarray(moments.source),
    }
    for key, value in extra.items():
        payload[str(key)] = np.asarray(value)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path, **payload)


def load_common_measure_npz(path: Path) -> CommonMeasureMoments:
    with np.load(path, allow_pickle=False) as data:
        return CommonMeasureMoments(
            intervals_x=data["state_intervals_x"],
            labels=data["state_labels"],
            mode_measure_m3=data["mode_measure_m3"],
            equilibrium_weight_m3=data["equilibrium_weight_m3"],
            frequency_moments_x=data["frequency_moments_x_m3_sInv"],
            frequency_moments_hz=data["frequency_moments_Hz_m3_sInv"],
            same_cell_jump_moments_x=data["same_cell_jump_moments_x_m3_sInv"],
            Doppler_width_Hz=float(data["Doppler_width_Hz"]),
            nu_abs_Hz=float(data["nu_abs_Hz"]),
            temperature_K=float(data["temperature_K"]),
            source=str(data["source"].item()),
        )
