"""Production runtime integration for nonlinear anisotropic Bose collision.

This module is the PR-02 bridge between the chart-independent
:class:`~full_bianchi_hyrec.background.snapshot.BackgroundSnapshot` interface
and the current scalar collision network.  PR-03/v0.50 supplies the
full bound-plus-continuum COM--KHW moments; geometry selects and populates
the angular frame adapter and never modifies atomic amplitudes or moments.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import math
from pathlib import Path
from typing import Mapping

import numpy as np
from scipy.constants import c, k, physical_constants
from scipy.integrate import lebedev_rule
from scipy.sparse.linalg import LinearOperator, gmres

from full_bianchi_hyrec.background.characteristics import (
    aberrate_direction,
    doppler_coordinate_speed,
    hydrogen_frame_characteristic,
    normal_frame_characteristic,
)
from full_bianchi_hyrec.background.snapshot import BackgroundSnapshot

from .nonlinear_bose_release import (
    BoseActionResult,
    HarmonicGrid,
    apply_nonlinear_bose_jvp,
    apply_nonlinear_bose_operator,
    bose_free_energy,
    bose_photon_number,
)


ADAPTIVE_GRID_ORDER: Mapping[int, int] = {12: 29, 20: 41, 24: 53}


@dataclass(frozen=True)
class CollisionNetwork:
    state_intervals: np.ndarray
    state_labels: np.ndarray
    pair_moments: np.ndarray
    same_cell_rates: np.ndarray
    mode_measure: np.ndarray
    equilibrium_weight: np.ndarray
    momentum_scale: np.ndarray
    inherited_release_policy: Mapping[str, int]

    def __post_init__(self):
        intervals = np.asarray(self.state_intervals, dtype=float)
        labels = np.asarray(self.state_labels).astype(str)
        pair = np.asarray(self.pair_moments, dtype=float)
        same = np.asarray(self.same_cell_rates, dtype=float)
        mode = np.asarray(self.mode_measure, dtype=float)
        equilibrium = np.asarray(self.equilibrium_weight, dtype=float)
        momentum = np.asarray(self.momentum_scale, dtype=float)
        n_state = len(labels)

        if intervals.shape != (n_state, 2):
            raise ValueError("state_intervals shape mismatch")
        if np.any(intervals[:, 1] <= intervals[:, 0]):
            raise ValueError("state intervals must have positive width")
        if len(set(labels.tolist())) != n_state:
            raise ValueError("state labels must be unique")
        if pair.ndim != 3 or pair.shape[1:] != (n_state, n_state):
            raise ValueError("pair moment shape mismatch")
        if same.ndim != 2 or same.shape[1] != n_state:
            raise ValueError("same-cell rate shape mismatch")
        if mode.shape != (n_state,) or equilibrium.shape != (n_state,):
            raise ValueError("frequency measure shape mismatch")
        if momentum.shape != (n_state,):
            raise ValueError("momentum scale shape mismatch")
        if np.any(mode <= 0) or np.any(equilibrium <= 0) or np.any(momentum <= 0):
            raise ValueError("network measures must be strictly positive")
        pair_scale = np.max(np.abs(pair)) + 1e-300
        if np.max(np.abs(pair - np.swapaxes(pair, 1, 2))) > 1e-12 * pair_scale:
            raise ValueError("pair moments must be symmetric")
        if np.min(pair[0]) < -1e-30:
            raise ValueError("scalar pair conductance must be nonnegative")

        for name, array in (
            ("state_intervals", intervals),
            ("state_labels", labels),
            ("pair_moments", pair),
            ("same_cell_rates", same),
            ("mode_measure", mode),
            ("equilibrium_weight", equilibrium),
            ("momentum_scale", momentum),
        ):
            array = array.copy()
            array.setflags(write=False)
            object.__setattr__(self, name, array)
        object.__setattr__(
            self,
            "inherited_release_policy",
            {str(key): int(value) for key, value in self.inherited_release_policy.items()},
        )

    @property
    def n_state(self) -> int:
        return int(len(self.state_labels))

    @property
    def centers(self) -> np.ndarray:
        return 0.5 * (self.state_intervals[:, 0] + self.state_intervals[:, 1])

    @property
    def activity_weight(self) -> np.ndarray:
        return self.equilibrium_weight / self.mode_measure

    @classmethod
    def from_npz(cls, path: str | Path) -> "CollisionNetwork":
        with np.load(path, allow_pickle=False) as data:
            states = data["release_states"].astype(str)
            ells = data["release_ell"].astype(int)
            return cls(
                state_intervals=data["state_intervals"],
                state_labels=data["state_labels"],
                pair_moments=data["pair_moments_m3_sInv"],
                same_cell_rates=data["same_cell_rates_sInv"],
                mode_measure=data["mode_measure_m3"],
                equilibrium_weight=data["equilibrium_weight_m3"],
                momentum_scale=data["momentum_scale"],
                inherited_release_policy=dict(zip(states.tolist(), ells.tolist())),
            )

    def boundary_pair_moments(self) -> np.ndarray:
        """Return only interior-to-near/far boundary conductance moments."""

        labels = self.state_labels.astype(str)
        interior = np.asarray([label.startswith("I") for label in labels])
        boundary = ~interior
        mask = np.logical_or(
            interior[:, None] & boundary[None, :],
            boundary[:, None] & interior[None, :],
        )
        return self.pair_moments * mask[None, :, :]


@dataclass(frozen=True)
class LineBoundaryConfig:
    nu_abs_Hz: float
    Doppler_width_Hz: float
    x_red: float = -10.25
    x_blue: float = 10.25
    D0_nu_abs_Hz_s: float = 0.0
    D0_log_Doppler_width_s_inv: float = 0.0
    D0_x_red_s_inv: float = 0.0
    D0_x_blue_s_inv: float = 0.0

    def __post_init__(self):
        if self.nu_abs_Hz <= 0 or self.Doppler_width_Hz <= 0:
            raise ValueError("line frequency and Doppler width must be positive")
        if self.x_red >= self.x_blue:
            raise ValueError("x_red must be below x_blue")

    @classmethod
    def lyman_alpha(
        cls,
        *,
        temperature_K: float = 3000.0,
        x_red: float = -10.25,
        x_blue: float = 10.25,
    ) -> "LineBoundaryConfig":
        if temperature_K <= 0:
            raise ValueError("temperature_K must be positive")
        wavelength_m = 1215.6701e-10
        nu_abs = c / wavelength_m
        hydrogen_mass = physical_constants["atomic mass constant"][0] * 1.00782503223
        width = nu_abs * math.sqrt(2.0 * k * temperature_K / hydrogen_mass) / c
        return cls(
            nu_abs_Hz=nu_abs,
            Doppler_width_Hz=width,
            x_red=x_red,
            x_blue=x_blue,
        )


@dataclass(frozen=True)
class AngularPolicyDecision:
    ell_max: int
    policy: str
    beta_norm: float
    normalized_shear_squared: float
    red_directional_crossing: bool
    blue_directional_crossing: bool
    characteristic_crossing: bool
    threshold_shear_squared: float


@dataclass(frozen=True)
class BoseRuntimeState:
    snapshot: BackgroundSnapshot
    policy: AngularPolicyDecision
    grid: HarmonicGrid
    direction_normal: np.ndarray
    direction_hydrogen: np.ndarray
    doppler_factor: np.ndarray
    R_hydrogen_s_inv: np.ndarray
    D0_direction_hydrogen_s_inv: np.ndarray
    red_speed_s_inv: np.ndarray | None
    blue_speed_s_inv: np.ndarray | None
    frame_roundtrip_residual: float


@dataclass(frozen=True)
class RuntimeBoseResult:
    runtime_state: BoseRuntimeState
    full_action: BoseActionResult
    boundary_action: BoseActionResult
    full_group_number_action: Mapping[str, float]
    boundary_group_number_action: Mapping[str, float]
    Q_gamma_normal: np.ndarray
    Q_atom_normal: np.ndarray
    four_force_hydrogen_residual: float
    four_force_normal_residual: float


@dataclass(frozen=True)
class ImplicitBoseStepResult:
    occupation: np.ndarray
    converged: bool
    newton_iterations: int
    total_gmres_iterations: int
    dt_s: float
    residual_relative: float
    minimum_occupation: float
    explicit_trial_minimum: float
    number_before: float
    number_after: float
    number_relative_change: float
    free_energy_before: float
    free_energy_after: float
    free_energy_change: float


@lru_cache(maxsize=len(ADAPTIVE_GRID_ORDER))
def positive_harmonic_grid(ell_max: int) -> HarmonicGrid:
    """Return the locked positive-weight harmonic-exact angular grid.

    The returned :class:`HarmonicGrid` is immutable and cached because its
    spherical-harmonic analysis matrix is expensive to reconstruct.
    """

    try:
        order = ADAPTIVE_GRID_ORDER[int(ell_max)]
    except KeyError as exc:
        raise ValueError("ell_max must be one of 12, 20, 24") from exc
    points, weights = lebedev_rule(order)
    if np.any(weights <= 0):
        raise RuntimeError(f"Lebedev order {order} contains nonpositive weights")
    return HarmonicGrid.from_directions(
        points.T,
        weights / (4.0 * math.pi),
        ell_max=int(ell_max),
    )


def boost_four_normal_to_hydrogen(four_vector, beta_H) -> np.ndarray:
    """Lorentz boost from the normal tetrad to the hydrogen tetrad.

    Components use the same ``(time, spatial)`` normalization, so factors of
    ``c`` remain in the caller's definition of the four-vector rather than
    being silently set to one here.
    """

    vector = np.asarray(four_vector, dtype=float)
    beta = np.asarray(beta_H, dtype=float)
    if vector.shape != (4,) or beta.shape != (3,):
        raise ValueError("four_vector and beta_H shape mismatch")
    beta2 = float(beta @ beta)
    if beta2 >= 1.0:
        raise ValueError("|beta_H| must be below one")
    if beta2 < 1e-28:
        return vector.copy()
    gamma = 1.0 / math.sqrt(1.0 - beta2)
    spatial = vector[1:]
    beta_dot = float(beta @ spatial)
    time = gamma * (vector[0] - beta_dot)
    transformed_spatial = spatial + (
        (gamma - 1.0) * beta_dot / beta2 - gamma * vector[0]
    ) * beta
    return np.concatenate(([time], transformed_spatial))


def boost_four_hydrogen_to_normal(four_vector, beta_H) -> np.ndarray:
    """Inverse Lorentz boost from the hydrogen tetrad to the normal tetrad."""

    vector = np.asarray(four_vector, dtype=float)
    beta = np.asarray(beta_H, dtype=float)
    if vector.shape != (4,) or beta.shape != (3,):
        raise ValueError("four_vector and beta_H shape mismatch")
    beta2 = float(beta @ beta)
    if beta2 >= 1.0:
        raise ValueError("|beta_H| must be below one")
    if beta2 < 1e-28:
        return vector.copy()
    gamma = 1.0 / math.sqrt(1.0 - beta2)
    spatial = vector[1:]
    beta_dot = float(beta @ spatial)
    time = gamma * (vector[0] + beta_dot)
    transformed_spatial = spatial + (
        (gamma - 1.0) * beta_dot / beta2 + gamma * vector[0]
    ) * beta
    return np.concatenate(([time], transformed_spatial))


def _frame_arrays(snapshot: BackgroundSnapshot, grid: HarmonicGrid):
    normal_direction = np.empty_like(grid.directions)
    hydrogen_direction = np.empty_like(grid.directions)
    doppler = np.empty(grid.n_angle)
    R_hydrogen = np.empty(grid.n_angle)
    D0_direction_hydrogen = np.empty_like(grid.directions)
    maximum_roundtrip = 0.0

    for index, direction_H in enumerate(grid.directions):
        direction_n = aberrate_direction(-snapshot.beta_H, direction_H)
        normal = normal_frame_characteristic(snapshot, direction_n)
        hydrogen = hydrogen_frame_characteristic(snapshot, normal)
        normal_direction[index] = direction_n
        hydrogen_direction[index] = hydrogen.direction_hydrogen
        doppler[index] = hydrogen.doppler_factor
        R_hydrogen[index] = hydrogen.R_hydrogen_s_inv
        D0_direction_hydrogen[index] = hydrogen.D0_direction_hydrogen_s_inv
        maximum_roundtrip = max(
            maximum_roundtrip,
            float(np.linalg.norm(hydrogen.direction_hydrogen - direction_H)),
        )
    return (
        normal_direction,
        hydrogen_direction,
        doppler,
        R_hydrogen,
        D0_direction_hydrogen,
        maximum_roundtrip,
    )


def _boundary_speeds(R_hydrogen, config: LineBoundaryConfig | None):
    if config is None:
        return None, None
    red = doppler_coordinate_speed(
        R_hydrogen,
        config.x_red,
        nu_abs_Hz=config.nu_abs_Hz,
        Doppler_width_Hz=config.Doppler_width_Hz,
        D0_nu_abs_Hz_s=config.D0_nu_abs_Hz_s,
        D0_log_Doppler_width_s_inv=config.D0_log_Doppler_width_s_inv,
        D0_x_boundary_s_inv=config.D0_x_red_s_inv,
    )
    blue = doppler_coordinate_speed(
        R_hydrogen,
        config.x_blue,
        nu_abs_Hz=config.nu_abs_Hz,
        Doppler_width_Hz=config.Doppler_width_Hz,
        D0_nu_abs_Hz_s=config.D0_nu_abs_Hz_s,
        D0_log_Doppler_width_s_inv=config.D0_log_Doppler_width_s_inv,
        D0_x_boundary_s_inv=config.D0_x_blue_s_inv,
    )
    return np.asarray(red, dtype=float), np.asarray(blue, dtype=float)


def _mixed_sign(values: np.ndarray | None, tolerance: float) -> bool:
    if values is None:
        return False
    scale = max(float(np.max(np.abs(values))), 1e-300)
    threshold = tolerance * scale
    return bool(np.min(values) < -threshold and np.max(values) > threshold)


def prepare_runtime_state(
    snapshot: BackgroundSnapshot,
    *,
    boundary: LineBoundaryConfig | None = None,
    force_ell_max: int | None = None,
    tilt_tolerance: float = 1e-10,
    shear_squared_threshold: float = 0.15,
    crossing_tolerance: float = 1e-12,
) -> BoseRuntimeState:
    """Select an adaptive positive-weight grid and build the frame map.

    The policy is fail-closed toward the higher angular release:

    * any red/blue directional sign crossing -> ``L=24``;
    * otherwise finite tilt -> ``L=12``;
    * otherwise nonlinear even shear with Sigma^2 above the locked threshold
      -> ``L=20``;
    * otherwise -> ``L=12``.
    """

    trial_grid = positive_harmonic_grid(12)
    trial = _frame_arrays(snapshot, trial_grid)
    trial_red, trial_blue = _boundary_speeds(trial[3], boundary)
    beta_norm = float(np.linalg.norm(snapshot.beta_H))
    shear_squared = float(
        np.trace(snapshot.sigma_s_inv @ snapshot.sigma_s_inv)
        / (6.0 * snapshot.H_s_inv**2)
    )
    red_crossing = _mixed_sign(trial_red, crossing_tolerance)
    blue_crossing = _mixed_sign(trial_blue, crossing_tolerance)
    characteristic_crossing = _mixed_sign(trial[3], crossing_tolerance)

    if force_ell_max is not None:
        ell_max = int(force_ell_max)
        if ell_max not in ADAPTIVE_GRID_ORDER:
            raise ValueError("force_ell_max must be one of 12, 20, 24")
        policy = "forced"
    elif red_crossing or blue_crossing:
        ell_max = 24
        policy = "directional_crossing"
    elif beta_norm > tilt_tolerance:
        ell_max = 12
        policy = "finite_or_mixed_tilt"
    elif shear_squared > shear_squared_threshold:
        ell_max = 20
        policy = "nonlinear_even_shear"
    else:
        ell_max = 12
        policy = "baseline_or_high_occupation"

    grid = trial_grid if ell_max == 12 else positive_harmonic_grid(ell_max)
    arrays = trial if ell_max == 12 else _frame_arrays(snapshot, grid)
    red_speed, blue_speed = (
        (trial_red, trial_blue)
        if ell_max == 12
        else _boundary_speeds(arrays[3], boundary)
    )
    decision = AngularPolicyDecision(
        ell_max=ell_max,
        policy=policy,
        beta_norm=beta_norm,
        normalized_shear_squared=shear_squared,
        red_directional_crossing=red_crossing,
        blue_directional_crossing=blue_crossing,
        characteristic_crossing=characteristic_crossing,
        threshold_shear_squared=float(shear_squared_threshold),
    )
    return BoseRuntimeState(
        snapshot=snapshot,
        policy=decision,
        grid=grid,
        direction_normal=arrays[0],
        direction_hydrogen=arrays[1],
        doppler_factor=arrays[2],
        R_hydrogen_s_inv=arrays[3],
        D0_direction_hydrogen_s_inv=arrays[4],
        red_speed_s_inv=red_speed,
        blue_speed_s_inv=blue_speed,
        frame_roundtrip_residual=float(arrays[5]),
    )


def _group_number_action(number_action, network: CollisionNetwork, grid: HarmonicGrid):
    per_state = np.sum(number_action * grid.weights[None, :], axis=1)
    labels = network.state_labels.astype(str)
    groups = {
        "interior": np.asarray([label.startswith("I") for label in labels]),
        "near_red": np.asarray([label.startswith("NR") for label in labels]),
        "near_blue": np.asarray([label.startswith("NB") for label in labels]),
        "far_red": np.asarray([label.startswith("FR") for label in labels]),
        "far_blue": np.asarray([label.startswith("FB") for label in labels]),
    }
    result = {name: float(np.sum(per_state[mask])) for name, mask in groups.items()}
    result["total"] = float(np.sum(per_state))
    return result


class BoseCollisionRuntime:
    def __init__(self, network: CollisionNetwork):
        self.network = network

    def prepare(
        self,
        snapshot: BackgroundSnapshot,
        *,
        boundary: LineBoundaryConfig | None = None,
        force_ell_max: int | None = None,
    ) -> BoseRuntimeState:
        return prepare_runtime_state(
            snapshot,
            boundary=boundary,
            force_ell_max=force_ell_max,
        )

    def evaluate(
        self,
        state: BoseRuntimeState,
        occupation,
    ) -> RuntimeBoseResult:
        f = np.asarray(occupation, dtype=float)
        full = apply_nonlinear_bose_operator(
            f,
            mode_measure=self.network.mode_measure,
            equilibrium_weight=self.network.equilibrium_weight,
            pair_moments=self.network.pair_moments,
            same_cell_rates=self.network.same_cell_rates,
            grid=state.grid,
            photon_momentum_scale=self.network.momentum_scale,
        )
        boundary = apply_nonlinear_bose_operator(
            f,
            mode_measure=self.network.mode_measure,
            equilibrium_weight=self.network.equilibrium_weight,
            pair_moments=self.network.boundary_pair_moments(),
            same_cell_rates=np.zeros_like(self.network.same_cell_rates),
            grid=state.grid,
            photon_momentum_scale=self.network.momentum_scale,
        )
        q_gamma_normal = boost_four_hydrogen_to_normal(
            full.Q_gamma, state.snapshot.beta_H
        )
        q_atom_normal = boost_four_hydrogen_to_normal(
            full.Q_atom, state.snapshot.beta_H
        )
        return RuntimeBoseResult(
            runtime_state=state,
            full_action=full,
            boundary_action=boundary,
            full_group_number_action=_group_number_action(
                full.number_action, self.network, state.grid
            ),
            boundary_group_number_action=_group_number_action(
                boundary.number_action, self.network, state.grid
            ),
            Q_gamma_normal=q_gamma_normal,
            Q_atom_normal=q_atom_normal,
            four_force_hydrogen_residual=float(
                np.linalg.norm(full.Q_gamma + full.Q_atom)
            ),
            four_force_normal_residual=float(
                np.linalg.norm(q_gamma_normal + q_atom_normal)
            ),
        )

    def implicit_step(
        self,
        state: BoseRuntimeState,
        occupation,
        *,
        dt_s: float,
        nonlinear_rtol: float = 2e-10,
        max_newton: int = 12,
        gmres_rtol: float = 2e-8,
        gmres_restart: int = 35,
        gmres_maxiter: int = 120,
    ) -> ImplicitBoseStepResult:
        return implicit_bose_step(
            occupation,
            dt_s=dt_s,
            network=self.network,
            grid=state.grid,
            nonlinear_rtol=nonlinear_rtol,
            max_newton=max_newton,
            gmres_rtol=gmres_rtol,
            gmres_restart=gmres_restart,
            gmres_maxiter=gmres_maxiter,
        )


def implicit_residual_jvp(
    occupation,
    log_perturbation,
    *,
    dt_s,
    network: CollisionNetwork,
    grid: HarmonicGrid,
) -> np.ndarray:
    f = np.asarray(occupation, dtype=float)
    du = np.asarray(log_perturbation, dtype=float)
    if f.shape != du.shape:
        raise ValueError("log perturbation shape mismatch")
    df = f * du
    action_jvp = apply_nonlinear_bose_jvp(
        f,
        df,
        mode_measure=network.mode_measure,
        equilibrium_weight=network.equilibrium_weight,
        pair_moments=network.pair_moments,
        same_cell_rates=network.same_cell_rates,
        grid=grid,
    ).occupation_action_jvp
    return df - float(dt_s) * action_jvp


def implicit_bose_step(
    occupation,
    *,
    dt_s: float,
    network: CollisionNetwork,
    grid: HarmonicGrid,
    nonlinear_rtol: float = 2e-10,
    max_newton: int = 12,
    gmres_rtol: float = 2e-8,
    gmres_restart: int = 35,
    gmres_maxiter: int = 120,
) -> ImplicitBoseStepResult:
    """Backward-Euler collision update in log occupation variables.

    ``f=exp(u)`` makes every accepted Newton iterate strictly positive.  Exact
    number conservation follows from the collision left null once the
    backward-Euler residual is solved; no clipping or post-step renormalization
    is applied.
    """

    old = np.asarray(occupation, dtype=float)
    if dt_s <= 0 or not np.isfinite(dt_s):
        raise ValueError("dt_s must be finite and positive")
    if old.shape != (network.n_state, grid.n_angle):
        raise ValueError("occupation shape mismatch")
    if np.any(old <= 0) or not np.all(np.isfinite(old)):
        raise ValueError("strictly positive finite occupation required")

    old_action = apply_nonlinear_bose_operator(
        old,
        mode_measure=network.mode_measure,
        equilibrium_weight=network.equilibrium_weight,
        pair_moments=network.pair_moments,
        same_cell_rates=network.same_cell_rates,
        grid=grid,
        photon_momentum_scale=network.momentum_scale,
    )
    explicit_trial = old + dt_s * old_action.occupation_action
    number_before = bose_photon_number(
        old, mode_measure=network.mode_measure, grid=grid
    )
    free_before = bose_free_energy(
        old,
        mode_measure=network.mode_measure,
        equilibrium_weight=network.equilibrium_weight,
        grid=grid,
    )

    log_f = np.log(old)
    reference_scale = max(float(np.max(np.abs(old))), 1e-300)
    total_gmres_iterations = 0
    converged = False
    final_relative = math.inf

    for newton_iteration in range(max_newton + 1):
        f = np.exp(log_f)
        action = apply_nonlinear_bose_operator(
            f,
            mode_measure=network.mode_measure,
            equilibrium_weight=network.equilibrium_weight,
            pair_moments=network.pair_moments,
            same_cell_rates=network.same_cell_rates,
            grid=grid,
            photon_momentum_scale=network.momentum_scale,
        )
        residual = f - old - dt_s * action.occupation_action
        residual_norm = float(np.max(np.abs(residual)))
        final_relative = residual_norm / reference_scale
        if final_relative <= nonlinear_rtol:
            converged = True
            break
        if newton_iteration == max_newton:
            break

        shape = f.shape
        size = f.size

        def matvec(flat_direction):
            direction = np.asarray(flat_direction, dtype=float).reshape(shape)
            return implicit_residual_jvp(
                f,
                direction,
                dt_s=dt_s,
                network=network,
                grid=grid,
            ).ravel()

        operator = LinearOperator((size, size), matvec=matvec, dtype=float)
        inverse_diagonal = 1.0 / np.maximum(f.ravel(), 1e-300)
        preconditioner = LinearOperator(
            (size, size),
            matvec=lambda value: inverse_diagonal * value,
            dtype=float,
        )
        iteration_counter = [0]

        def callback(_):
            iteration_counter[0] += 1

        step, info = gmres(
            operator,
            -residual.ravel(),
            M=preconditioner,
            rtol=gmres_rtol,
            atol=0.0,
            restart=gmres_restart,
            maxiter=gmres_maxiter,
            callback=callback,
            callback_type="pr_norm",
        )
        total_gmres_iterations += iteration_counter[0]
        if info != 0 or not np.all(np.isfinite(step)):
            raise RuntimeError(f"GMRES failed in implicit Bose step (info={info})")

        step = step.reshape(shape)
        accepted = False
        damping = 1.0
        for _ in range(18):
            trial_log = log_f + damping * step
            if np.max(trial_log) > 700.0 or np.min(trial_log) < -745.0:
                damping *= 0.5
                continue
            trial_f = np.exp(trial_log)
            trial_action = apply_nonlinear_bose_operator(
                trial_f,
                mode_measure=network.mode_measure,
                equilibrium_weight=network.equilibrium_weight,
                pair_moments=network.pair_moments,
                same_cell_rates=network.same_cell_rates,
                grid=grid,
                photon_momentum_scale=network.momentum_scale,
            )
            trial_residual = (
                trial_f - old - dt_s * trial_action.occupation_action
            )
            trial_norm = float(np.max(np.abs(trial_residual)))
            if trial_norm < residual_norm * (1.0 - 1e-4 * damping):
                log_f = trial_log
                accepted = True
                break
            damping *= 0.5
        if not accepted:
            raise RuntimeError("Newton line search failed in implicit Bose step")

    if not converged:
        raise RuntimeError(
            f"implicit Bose step failed to converge: residual={final_relative:.3e}"
        )

    updated = np.exp(log_f)
    number_after = bose_photon_number(
        updated, mode_measure=network.mode_measure, grid=grid
    )
    free_after = bose_free_energy(
        updated,
        mode_measure=network.mode_measure,
        equilibrium_weight=network.equilibrium_weight,
        grid=grid,
    )
    number_relative = abs(number_after - number_before) / max(
        abs(number_before), 1e-300
    )
    return ImplicitBoseStepResult(
        occupation=updated,
        converged=True,
        newton_iterations=newton_iteration,
        total_gmres_iterations=total_gmres_iterations,
        dt_s=float(dt_s),
        residual_relative=final_relative,
        minimum_occupation=float(np.min(updated)),
        explicit_trial_minimum=float(np.min(explicit_trial)),
        number_before=number_before,
        number_after=number_after,
        number_relative_change=float(number_relative),
        free_energy_before=free_before,
        free_energy_after=free_after,
        free_energy_change=float(free_after - free_before),
    )
