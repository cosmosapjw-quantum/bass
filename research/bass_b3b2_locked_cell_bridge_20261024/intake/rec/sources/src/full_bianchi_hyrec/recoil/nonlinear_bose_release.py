"""Nonlinear Bose action using zonal harmonic conductance moments.

The collision action is evaluated on positive-weight spherical quadrature
rules.  Frequency-pair conductance is stored in Legendre moments, so zonal
convolutions are diagonal in spherical harmonics while Bose products remain
pointwise in angle.
"""
from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np
from scipy.special import sph_harm_y


@dataclass(frozen=True)
class HarmonicGrid:
    directions: np.ndarray
    weights: np.ndarray
    ell_max: int
    lm: np.ndarray
    synthesis: np.ndarray
    analysis: np.ndarray
    ell_of_mode: np.ndarray
    gram_residual: float

    @property
    def n_angle(self) -> int:
        return int(len(self.weights))

    @classmethod
    def from_directions(cls, directions, weights, *, ell_max):
        d = np.asarray(directions, float)
        w = np.asarray(weights, float)
        if d.ndim != 2 or d.shape[1] != 3:
            raise ValueError("directions must have shape (n,3)")
        if w.shape != (len(d),) or np.any(w <= 0):
            raise ValueError("invalid weights")
        w = w / w.sum()
        if np.max(np.abs(np.linalg.norm(d, axis=1) - 1)) > 1e-12:
            raise ValueError("directions must lie on unit sphere")
        if int(ell_max) < 0:
            raise ValueError("ell_max must be nonnegative")

        theta = np.arccos(np.clip(d[:, 2], -1, 1))
        phi = np.mod(np.arctan2(d[:, 1], d[:, 0]), 2 * math.pi)
        lm = []
        columns = []
        for ell in range(int(ell_max) + 1):
            for m in range(-ell, ell + 1):
                lm.append((ell, m))
                columns.append(
                    math.sqrt(4 * math.pi) * sph_harm_y(ell, m, theta, phi)
                )
        synthesis = np.column_stack(columns)
        raw_analysis = synthesis.conj().T * w[None, :]
        gram = raw_analysis @ synthesis
        identity = np.eye(len(lm))
        residual = float(np.max(np.abs(gram - identity)))
        analysis = (
            raw_analysis
            if residual < 1e-10
            else np.linalg.solve(gram, raw_analysis)
        )
        residual = float(np.max(np.abs(analysis @ synthesis - identity)))
        lm_array = np.asarray(lm, int)
        ell_of_mode = np.asarray([ell for ell, _ in lm], int)
        immutable = (d, w, lm_array, synthesis, analysis, ell_of_mode)
        for array in immutable:
            array.setflags(write=False)
        return cls(
            d,
            w,
            int(ell_max),
            lm_array,
            synthesis,
            analysis,
            ell_of_mode,
            residual,
        )

    def analyze(self, fields):
        f = np.asarray(fields)
        flat = f.reshape((-1, self.n_angle))
        coefficients = (self.analysis @ flat.T).T
        return coefficients.reshape(f.shape[:-1] + (len(self.lm),))

    def synthesize(self, coefficients):
        c = np.asarray(coefficients)
        flat = c.reshape((-1, len(self.lm)))
        fields = (self.synthesis @ flat.T).T
        return np.real_if_close(fields, tol=1000).reshape(
            c.shape[:-1] + (self.n_angle,)
        )

    def partial_ell_fields(self, fields):
        f = np.asarray(fields)
        coefficients = self.analyze(f)
        output = np.zeros(
            f.shape[:-1] + (self.ell_max + 1, self.n_angle), complex
        )
        for ell in range(self.ell_max + 1):
            mask = self.ell_of_mode == ell
            part = coefficients[..., mask].reshape((-1, int(mask.sum())))
            output[..., ell, :] = (
                self.synthesis[:, mask] @ part.T
            ).T.reshape(f.shape[:-1] + (self.n_angle,))
        return np.real_if_close(output, tol=1000)


@dataclass(frozen=True)
class BoseActionResult:
    occupation_action: np.ndarray
    number_action: np.ndarray
    action_coefficients: np.ndarray
    number_residual: float
    entropy_production: float
    Q_gamma: np.ndarray
    Q_atom: np.ndarray
    minimum_occupation: float
    gross_action_scale: float


@dataclass(frozen=True)
class BoseJVPResult:
    """Directional derivative of the nonlinear collision action."""

    occupation_action_jvp: np.ndarray
    number_action_jvp: np.ndarray
    number_residual_jvp: float


def _validated_operator_inputs(
    occupation,
    *,
    mode_measure,
    equilibrium_weight,
    pair_moments,
    same_cell_rates,
    grid,
):
    f = np.asarray(occupation, float)
    g = np.asarray(mode_measure, float)
    pi = np.asarray(equilibrium_weight, float)
    pair = np.asarray(pair_moments, float)
    same = np.asarray(same_cell_rates, float)
    n_state = len(g)

    if f.shape != (n_state, grid.n_angle):
        raise ValueError("occupation shape mismatch")
    if pi.shape != (n_state,) or np.any(g <= 0) or np.any(pi <= 0):
        raise ValueError("invalid measures")
    if np.any(f <= 0) or not np.all(np.isfinite(f)):
        raise ValueError("occupations must be finite and strictly positive")
    if pair.ndim != 3 or pair.shape[1:] != (n_state, n_state):
        raise ValueError("pair moments shape mismatch")
    if same.ndim != 2 or same.shape[1] != n_state:
        raise ValueError("same-cell rate shape mismatch")
    pair_scale = np.max(np.abs(pair)) + 1e-300
    if np.max(np.abs(pair - np.swapaxes(pair, 1, 2))) > 1e-10 * pair_scale:
        raise ValueError("pair moments must be symmetric")
    if np.min(pair[0]) < -1e-30:
        raise ValueError("scalar pair conductances must be nonnegative")
    return f, g, pi, pair, same


def apply_nonlinear_bose_operator_pair_loop(
    occupation,
    *,
    mode_measure,
    equilibrium_weight,
    pair_moments,
    same_cell_rates,
    grid,
    photon_momentum_scale=None,
):
    f, g, pi, pair, same_rates = _validated_operator_inputs(
        occupation,
        mode_measure=mode_measure,
        equilibrium_weight=equilibrium_weight,
        pair_moments=pair_moments,
        same_cell_rates=same_cell_rates,
        grid=grid,
    )
    n_state = len(g)
    z = pi / g
    phi = f / (z[:, None] * (1 + f))

    # Subtract one common chemical-potential activity before every
    # convolution. This exact rearrangement removes catastrophic subtraction
    # for near-Bose-Einstein states with activity q ~ 1/z.
    q_ref = float(np.sum(phi * grid.weights[None, :]) / n_state)
    delta_field = (1 + f) * (phi - q_ref)
    partial_f = grid.partial_ell_fields(f)
    partial_one_plus = partial_f.copy()
    partial_one_plus[:, 0, :] += 1.0
    partial_delta = grid.partial_ell_fields(delta_field)

    ell_max = min(grid.ell_max, pair.shape[0] - 1)
    number_action = np.zeros_like(f)
    gross = 0.0
    for a in range(n_state):
        for b in range(a + 1, n_state):
            moments = pair[: ell_max + 1, a, b]
            if moments[0] <= 0:
                continue
            conv_delta_b = np.tensordot(
                moments, partial_delta[b, : ell_max + 1], axes=(0, 0)
            )
            conv_delta_a = np.tensordot(
                moments, partial_delta[a, : ell_max + 1], axes=(0, 0)
            )
            conv_one_b = np.tensordot(
                moments, partial_one_plus[b, : ell_max + 1], axes=(0, 0)
            )
            conv_one_a = np.tensordot(
                moments, partial_one_plus[a, : ell_max + 1], axes=(0, 0)
            )
            action_a = np.real(
                (1 + f[a])
                * (conv_delta_b - (phi[a] - q_ref) * conv_one_b)
            )
            action_b = np.real(
                (1 + f[b])
                * (conv_delta_a - (phi[b] - q_ref) * conv_one_a)
            )
            number_action[a] += action_a
            number_action[b] += action_b

            # Gross forward+reverse scale is used only to normalize residuals.
            conv_f_b = np.tensordot(
                moments, partial_f[b, : ell_max + 1], axes=(0, 0)
            )
            conv_f_a = np.tensordot(
                moments, partial_f[a, : ell_max + 1], axes=(0, 0)
            )
            gross += float(
                np.sum(
                    grid.weights
                    * (
                        np.abs((1 + f[a]) * conv_f_b / z[b])
                        + np.abs(f[a] * conv_one_b / z[a])
                    )
                )
            )
            gross += float(
                np.sum(
                    grid.weights
                    * (
                        np.abs((1 + f[b]) * conv_f_a / z[a])
                        + np.abs(f[b] * conv_one_a / z[b])
                    )
                )
            )

    ell_same = min(grid.ell_max, same_rates.shape[0] - 1)
    for a in range(n_state):
        same = np.real(
            np.tensordot(
                same_rates[: ell_same + 1, a],
                partial_f[a, : ell_same + 1],
                axes=(0, 0),
            )
        )
        number_action[a] += g[a] * same
        gross += float(g[a] * np.sum(grid.weights * np.abs(same)))

    occupation_action = number_action / g[:, None]
    coefficients = grid.analyze(occupation_action)
    number_residual = float(
        np.sum(number_action * grid.weights[None, :])
    )
    psi = np.log(f / (1 + f)) - np.log(z)[:, None]
    entropy_production = float(
        np.sum(psi * number_action * grid.weights[None, :])
    )
    momentum_scale = (
        np.ones(n_state)
        if photon_momentum_scale is None
        else np.asarray(photon_momentum_scale, float)
    )
    if momentum_scale.shape != (n_state,):
        raise ValueError("photon_momentum_scale shape mismatch")
    weighted = number_action * grid.weights[None, :]
    q0 = float(np.sum(momentum_scale[:, None] * weighted))
    qvec = np.sum(
        momentum_scale[:, None, None]
        * weighted[:, :, None]
        * grid.directions[None, :, :],
        axis=(0, 1),
    )
    q_gamma = np.concatenate(([q0], qvec))
    q_atom = -q_gamma
    return BoseActionResult(
        occupation_action=occupation_action,
        number_action=number_action,
        action_coefficients=coefficients,
        number_residual=number_residual,
        entropy_production=entropy_production,
        Q_gamma=q_gamma,
        Q_atom=q_atom,
        minimum_occupation=float(np.min(f)),
        gross_action_scale=gross,
    )


def apply_nonlinear_bose_jvp_pair_loop(
    occupation,
    perturbation,
    *,
    mode_measure,
    equilibrium_weight,
    pair_moments,
    same_cell_rates,
    grid,
) -> BoseJVPResult:
    """Apply the exact Fréchet derivative to ``perturbation``.

    The derivative follows the activity-reference-subtracted formulation used
    by :func:`apply_nonlinear_bose_operator`; no finite differencing or clipped
    pointwise kernel reconstruction enters the production JVP.
    """

    f, g, pi, pair, same_rates = _validated_operator_inputs(
        occupation,
        mode_measure=mode_measure,
        equilibrium_weight=equilibrium_weight,
        pair_moments=pair_moments,
        same_cell_rates=same_cell_rates,
        grid=grid,
    )
    direction = np.asarray(perturbation, float)
    if direction.shape != f.shape or not np.all(np.isfinite(direction)):
        raise ValueError("perturbation shape mismatch or nonfinite values")

    n_state = len(g)
    z = pi / g
    phi = f / (z[:, None] * (1 + f))
    dphi = direction / (z[:, None] * (1 + f) ** 2)
    q_ref = float(np.sum(phi * grid.weights[None, :]) / n_state)
    dq_ref = float(np.sum(dphi * grid.weights[None, :]) / n_state)

    delta = (1 + f) * (phi - q_ref)
    # Algebraically equivalent to d[(1+f)(phi-q_ref)], but this expression
    # avoids multiplying two large activity-scale terms near equilibrium.
    ddelta = (
        direction / z[:, None]
        - q_ref * direction
        - dq_ref * (1 + f)
    )

    partial_f = grid.partial_ell_fields(f)
    partial_one = partial_f.copy()
    partial_one[:, 0, :] += 1.0
    partial_delta = grid.partial_ell_fields(delta)
    partial_direction = grid.partial_ell_fields(direction)
    partial_ddelta = grid.partial_ell_fields(ddelta)

    ell_max = min(grid.ell_max, pair.shape[0] - 1)
    dnumber_action = np.zeros_like(f)
    for a in range(n_state):
        for b in range(a + 1, n_state):
            moments = pair[: ell_max + 1, a, b]
            if moments[0] <= 0:
                continue

            conv_delta_b = np.tensordot(
                moments, partial_delta[b, : ell_max + 1], axes=(0, 0)
            )
            conv_delta_a = np.tensordot(
                moments, partial_delta[a, : ell_max + 1], axes=(0, 0)
            )
            conv_one_b = np.tensordot(
                moments, partial_one[b, : ell_max + 1], axes=(0, 0)
            )
            conv_one_a = np.tensordot(
                moments, partial_one[a, : ell_max + 1], axes=(0, 0)
            )
            conv_ddelta_b = np.tensordot(
                moments, partial_ddelta[b, : ell_max + 1], axes=(0, 0)
            )
            conv_ddelta_a = np.tensordot(
                moments, partial_ddelta[a, : ell_max + 1], axes=(0, 0)
            )
            conv_direction_b = np.tensordot(
                moments, partial_direction[b, : ell_max + 1], axes=(0, 0)
            )
            conv_direction_a = np.tensordot(
                moments, partial_direction[a, : ell_max + 1], axes=(0, 0)
            )

            residual_a = conv_delta_b - (phi[a] - q_ref) * conv_one_b
            residual_b = conv_delta_a - (phi[b] - q_ref) * conv_one_a
            dresidual_a = (
                conv_ddelta_b
                - (dphi[a] - dq_ref) * conv_one_b
                - (phi[a] - q_ref) * conv_direction_b
            )
            dresidual_b = (
                conv_ddelta_a
                - (dphi[b] - dq_ref) * conv_one_a
                - (phi[b] - q_ref) * conv_direction_a
            )
            dnumber_action[a] += np.real(
                direction[a] * residual_a + (1 + f[a]) * dresidual_a
            )
            dnumber_action[b] += np.real(
                direction[b] * residual_b + (1 + f[b]) * dresidual_b
            )

    ell_same = min(grid.ell_max, same_rates.shape[0] - 1)
    for a in range(n_state):
        same_jvp = np.real(
            np.tensordot(
                same_rates[: ell_same + 1, a],
                partial_direction[a, : ell_same + 1],
                axes=(0, 0),
            )
        )
        dnumber_action[a] += g[a] * same_jvp

    occupation_jvp = dnumber_action / g[:, None]
    number_residual_jvp = float(
        np.sum(dnumber_action * grid.weights[None, :])
    )
    return BoseJVPResult(
        occupation_action_jvp=occupation_jvp,
        number_action_jvp=dnumber_action,
        number_residual_jvp=number_residual_jvp,
    )



@dataclass(frozen=True)
class BoseBatchedJVPResult:
    """Batched directional derivatives of the nonlinear collision action."""

    occupation_action_jvp: np.ndarray
    number_action_jvp: np.ndarray
    number_residual_jvp: np.ndarray


def _vectorized_pair_moments(pair: np.ndarray, ell_max: int) -> np.ndarray:
    """Return active pair moments with all inactive/diagonal pairs zeroed."""

    active = pair[0] > 0.0
    active = active & ~np.eye(active.shape[0], dtype=bool)
    return pair[: ell_max + 1] * active[None, :, :]


def _vectorized_number_action(
    f: np.ndarray,
    g: np.ndarray,
    pi: np.ndarray,
    pair: np.ndarray,
    same_rates: np.ndarray,
    grid: HarmonicGrid,
    *,
    include_gross: bool,
) -> tuple[np.ndarray, float]:
    """Evaluate the pair action by tensor contraction instead of Python loops."""

    n_state = len(g)
    z = pi / g
    phi = f / (z[:, None] * (1.0 + f))
    q_ref = float(np.sum(phi * grid.weights[None, :]) / n_state)
    delta_field = (1.0 + f) * (phi - q_ref)

    partial_f = grid.partial_ell_fields(f)
    partial_one_plus = partial_f.copy()
    partial_one_plus[:, 0, :] += 1.0
    partial_delta = grid.partial_ell_fields(delta_field)

    ell_max = min(grid.ell_max, pair.shape[0] - 1)
    moments = _vectorized_pair_moments(pair, ell_max)
    # target, source, angle.  Each directed target/source contribution is
    # represented exactly once; symmetry of the stored conductance supplies
    # the reverse direction without an explicit unordered-pair Python loop.
    conv_delta = np.einsum(
        "lts,sla->tsa", moments, partial_delta[:, : ell_max + 1, :], optimize=True
    )
    conv_one = np.einsum(
        "lts,sla->tsa", moments, partial_one_plus[:, : ell_max + 1, :], optimize=True
    )
    residual = conv_delta - (phi[:, None, :] - q_ref) * conv_one
    number_action = np.real(
        (1.0 + f)[:, None, :] * residual
    ).sum(axis=1)

    gross = 0.0
    if include_gross:
        conv_f = np.einsum(
            "lts,sla->tsa", moments, partial_f[:, : ell_max + 1, :], optimize=True
        )
        forward = (1.0 + f)[:, None, :] * conv_f / z[None, :, None]
        reverse = f[:, None, :] * conv_one / z[:, None, None]
        gross = float(
            np.sum(
                (np.abs(forward) + np.abs(reverse))
                * grid.weights[None, None, :]
            )
        )

    ell_same = min(grid.ell_max, same_rates.shape[0] - 1)
    same = np.real(
        np.einsum(
            "ls,sla->sa",
            same_rates[: ell_same + 1],
            partial_f[:, : ell_same + 1, :],
            optimize=True,
        )
    )
    number_action += g[:, None] * same
    if include_gross:
        gross += float(
            np.sum(
                g[:, None] * np.abs(same) * grid.weights[None, :]
            )
        )
    return number_action, gross


def apply_nonlinear_bose_action(
    occupation,
    *,
    mode_measure,
    equilibrium_weight,
    pair_moments,
    same_cell_rates,
    grid,
) -> np.ndarray:
    """Return only the occupation action through the optimized hot path.

    Diagnostics such as entropy production, four-force and harmonic output are
    deliberately omitted.  Nonlinear residual evaluations use this function;
    the full operator is evaluated only for accepted states and audit receipts.
    """

    f, g, pi, pair, same_rates = _validated_operator_inputs(
        occupation,
        mode_measure=mode_measure,
        equilibrium_weight=equilibrium_weight,
        pair_moments=pair_moments,
        same_cell_rates=same_cell_rates,
        grid=grid,
    )
    number_action, _ = _vectorized_number_action(
        f, g, pi, pair, same_rates, grid, include_gross=False
    )
    return number_action / g[:, None]


def apply_nonlinear_bose_operator(
    occupation,
    *,
    mode_measure,
    equilibrium_weight,
    pair_moments,
    same_cell_rates,
    grid,
    photon_momentum_scale=None,
):
    """Vectorized production nonlinear Bose operator.

    :func:`apply_nonlinear_bose_operator_pair_loop` remains the intentionally
    slow, structurally independent audit oracle.
    """

    f, g, pi, pair, same_rates = _validated_operator_inputs(
        occupation,
        mode_measure=mode_measure,
        equilibrium_weight=equilibrium_weight,
        pair_moments=pair_moments,
        same_cell_rates=same_cell_rates,
        grid=grid,
    )
    number_action, gross = _vectorized_number_action(
        f, g, pi, pair, same_rates, grid, include_gross=True
    )
    occupation_action = number_action / g[:, None]
    coefficients = grid.analyze(occupation_action)
    number_residual = float(np.sum(number_action * grid.weights[None, :]))
    z = pi / g
    psi = np.log(f / (1.0 + f)) - np.log(z)[:, None]
    entropy_production = float(
        np.sum(psi * number_action * grid.weights[None, :])
    )
    momentum_scale = (
        np.ones(len(g))
        if photon_momentum_scale is None
        else np.asarray(photon_momentum_scale, float)
    )
    if momentum_scale.shape != (len(g),):
        raise ValueError("photon_momentum_scale shape mismatch")
    weighted = number_action * grid.weights[None, :]
    q0 = float(np.sum(momentum_scale[:, None] * weighted))
    qvec = np.sum(
        momentum_scale[:, None, None]
        * weighted[:, :, None]
        * grid.directions[None, :, :],
        axis=(0, 1),
    )
    q_gamma = np.concatenate(([q0], qvec))
    return BoseActionResult(
        occupation_action=occupation_action,
        number_action=number_action,
        action_coefficients=coefficients,
        number_residual=number_residual,
        entropy_production=entropy_production,
        Q_gamma=q_gamma,
        Q_atom=-q_gamma,
        minimum_occupation=float(np.min(f)),
        gross_action_scale=gross,
    )


def apply_nonlinear_bose_jvp_batched(
    occupation,
    perturbations,
    *,
    mode_measure,
    equilibrium_weight,
    pair_moments,
    same_cell_rates,
    grid,
) -> BoseBatchedJVPResult:
    """Apply exact collision JVPs for a batch of perturbations.

    ``perturbations`` has shape ``(batch,n_state,n_angle)``.  This path is
    used for chunked dense-Jacobian assembly and avoids one Python-level
    collision traversal per column.
    """

    f, g, pi, pair, same_rates = _validated_operator_inputs(
        occupation,
        mode_measure=mode_measure,
        equilibrium_weight=equilibrium_weight,
        pair_moments=pair_moments,
        same_cell_rates=same_cell_rates,
        grid=grid,
    )
    directions = np.asarray(perturbations, float)
    if directions.ndim == 2:
        directions = directions[None, ...]
    if directions.ndim != 3 or directions.shape[1:] != f.shape:
        raise ValueError("perturbations must have shape (batch,n_state,n_angle)")
    if not np.all(np.isfinite(directions)):
        raise ValueError("perturbations contain nonfinite values")

    n_state = len(g)
    z = pi / g
    phi = f / (z[:, None] * (1.0 + f))
    dphi = directions / (z[None, :, None] * (1.0 + f)[None, :, :] ** 2)
    q_ref = float(np.sum(phi * grid.weights[None, :]) / n_state)
    dq_ref = np.sum(
        dphi * grid.weights[None, None, :], axis=(1, 2)
    ) / n_state
    delta = (1.0 + f) * (phi - q_ref)
    ddelta = (
        directions / z[None, :, None]
        - q_ref * directions
        - dq_ref[:, None, None] * (1.0 + f)[None, :, :]
    )

    partial_f = grid.partial_ell_fields(f)
    partial_one = partial_f.copy()
    partial_one[:, 0, :] += 1.0
    partial_delta = grid.partial_ell_fields(delta)
    partial_direction = grid.partial_ell_fields(directions)
    partial_ddelta = grid.partial_ell_fields(ddelta)

    ell_max = min(grid.ell_max, pair.shape[0] - 1)
    moments = _vectorized_pair_moments(pair, ell_max)
    conv_delta = np.einsum(
        "lts,sla->tsa", moments, partial_delta[:, : ell_max + 1], optimize=True
    )
    conv_one = np.einsum(
        "lts,sla->tsa", moments, partial_one[:, : ell_max + 1], optimize=True
    )
    conv_ddelta = np.einsum(
        "lts,bsla->btsa",
        moments,
        partial_ddelta[:, :, : ell_max + 1],
        optimize=True,
    )
    conv_direction = np.einsum(
        "lts,bsla->btsa",
        moments,
        partial_direction[:, :, : ell_max + 1],
        optimize=True,
    )
    residual = conv_delta - (phi[:, None, :] - q_ref) * conv_one
    dresidual = (
        conv_ddelta
        - (dphi[:, :, None, :] - dq_ref[:, None, None, None])
        * conv_one[None, :, :, :]
        - (phi[None, :, None, :] - q_ref) * conv_direction
    )
    dnumber = np.real(
        directions[:, :, None, :] * residual[None, :, :, :]
        + (1.0 + f)[None, :, None, :] * dresidual
    ).sum(axis=2)

    ell_same = min(grid.ell_max, same_rates.shape[0] - 1)
    same_jvp = np.real(
        np.einsum(
            "ls,bsla->bsa",
            same_rates[: ell_same + 1],
            partial_direction[:, :, : ell_same + 1],
            optimize=True,
        )
    )
    dnumber += g[None, :, None] * same_jvp
    occupation_jvp = dnumber / g[None, :, None]
    number_residual = np.sum(
        dnumber * grid.weights[None, None, :], axis=(1, 2)
    )
    return BoseBatchedJVPResult(
        occupation_action_jvp=occupation_jvp,
        number_action_jvp=dnumber,
        number_residual_jvp=np.asarray(number_residual, dtype=float),
    )


def apply_nonlinear_bose_jvp(
    occupation,
    perturbation,
    *,
    mode_measure,
    equilibrium_weight,
    pair_moments,
    same_cell_rates,
    grid,
) -> BoseJVPResult:
    """Vectorized exact Fréchet derivative for one perturbation."""

    batched = apply_nonlinear_bose_jvp_batched(
        occupation,
        np.asarray(perturbation, float)[None, ...],
        mode_measure=mode_measure,
        equilibrium_weight=equilibrium_weight,
        pair_moments=pair_moments,
        same_cell_rates=same_cell_rates,
        grid=grid,
    )
    return BoseJVPResult(
        occupation_action_jvp=batched.occupation_action_jvp[0],
        number_action_jvp=batched.number_action_jvp[0],
        number_residual_jvp=float(batched.number_residual_jvp[0]),
    )

def bose_photon_number(occupation, *, mode_measure, grid) -> float:
    f = np.asarray(occupation, float)
    g = np.asarray(mode_measure, float)
    if f.shape != (len(g), grid.n_angle):
        raise ValueError("occupation shape mismatch")
    if np.any(f < 0) or np.any(g <= 0):
        raise ValueError("occupation must be nonnegative and measures positive")
    return float(np.sum(g[:, None] * f * grid.weights[None, :]))


def bose_free_energy(
    occupation,
    *,
    mode_measure,
    equilibrium_weight,
    grid,
) -> float:
    """Discrete Bose free energy whose production is reported by the operator."""

    f = np.asarray(occupation, float)
    g = np.asarray(mode_measure, float)
    pi = np.asarray(equilibrium_weight, float)
    if f.shape != (len(g), grid.n_angle):
        raise ValueError("occupation shape mismatch")
    if np.any(f <= 0) or np.any(g <= 0) or np.any(pi <= 0):
        raise ValueError("strictly positive occupation and measures required")
    z = pi / g
    density = (
        f * np.log(f)
        - (1 + f) * np.log1p(f)
        - f * np.log(z)[:, None]
    )
    return float(np.sum(g[:, None] * density * grid.weights[None, :]))
