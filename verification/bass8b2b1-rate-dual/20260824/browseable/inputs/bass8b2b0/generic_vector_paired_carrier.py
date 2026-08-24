"""Generic-vector paired rest-to-normal cold-Thomson discrete witness.

This is a bounded research witness, not production code and not continuum
finite-tilt authority. It generalizes the already validated axis-aligned Type-II
paired-grid formulas to an arbitrary dimensionless electron velocity beta.

Conventions:
- metric signature (-,+,+,+);
- beta = v/c, |beta|<1;
- e is the photon propagation direction in the normal tetrad;
- e_rest is the electron-rest-frame direction;
- D = E_rest/E_normal = gamma*(1-beta.e);
- dOmega_rest = dOmega_normal/D**2;
- each physical node carries a Hermitian screen tensor J=P(e)JP(e), four real
  degrees of freedom; rank-9 is only an ambient real embedding.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import pi
from typing import Callable

import numpy as np

Array = np.ndarray


def _beta(value: Array) -> Array:
    b = np.asarray(value, dtype=float)
    if b.shape != (3,) or not np.isfinite(b).all():
        raise ValueError("beta must be a finite shape-(3,) vector")
    b2 = float(b @ b)
    if b2 >= 1.0:
        raise ValueError("beta must satisfy |beta|<1")
    return b


def _directions(value: Array) -> Array:
    e = np.asarray(value, dtype=float)
    if e.ndim != 2 or e.shape[1] != 3 or not np.isfinite(e).all():
        raise ValueError("directions must be a finite (N,3) array")
    if np.max(np.abs(np.linalg.norm(e, axis=1) - 1.0), initial=0.0) > 3e-13:
        raise ValueError("directions must be unit vectors")
    return e


def projector_screen(e: Array) -> Array:
    e = _directions(e)
    return np.eye(3)[None, :, :] - np.einsum("ai,aj->aij", e, e)


def aberrate(e: Array, beta: Array) -> tuple[Array, Array]:
    """Map normal-frame directions to the frame moving with velocity beta."""
    e = _directions(e)
    b = _beta(beta)
    b2 = float(b @ b)
    if b2 == 0.0:
        return e.copy(), np.ones(len(e))
    gamma = 1.0 / np.sqrt(1.0 - b2)
    be = e @ b
    doppler = gamma * (1.0 - be)
    coeff = ((gamma - 1.0) * be / b2 - gamma)
    ep = (e + coeff[:, None] * b[None, :]) / doppler[:, None]
    ep /= np.linalg.norm(ep, axis=1)[:, None]
    return ep, doppler


def screen_map(e: Array, beta: Array) -> tuple[Array, Array, Array]:
    """Return the canonical ambient tensor map normal -> electron rest."""
    e = _directions(e)
    b = _beta(beta)
    P = projector_screen(e)
    b2 = float(b @ b)
    if b2 == 0.0:
        return P, e.copy(), np.ones(len(e))
    gamma = 1.0 / np.sqrt(1.0 - b2)
    ep, doppler = aberrate(e, b)
    Pb = np.einsum("aij,j->ai", P, b)
    W0 = -gamma * Pb
    Wsp = P + ((gamma - 1.0) / b2) * np.einsum("i,ak->aik", b, Pb)
    psp = ep * doppler[:, None]
    # Matches the canonical Type-II reference formula, now with generic beta.
    S = Wsp - np.einsum("ai,ak->aik", psp, W0 / doppler[:, None])
    return S, ep, doppler


def pack9(J: Array) -> Array:
    J = np.asarray(J, dtype=float)
    if J.ndim != 3 or J.shape[1:] != (3, 3):
        raise ValueError("J must have shape (N,3,3)")
    S = 0.5 * (J + J.swapaxes(1, 2))
    A = 0.5 * (J - J.swapaxes(1, 2))
    return np.stack(
        [
            S[:, 0, 0], S[:, 1, 1], S[:, 2, 2],
            S[:, 0, 1], S[:, 0, 2], S[:, 1, 2],
            A[:, 1, 2], A[:, 2, 0], A[:, 0, 1],
        ],
        axis=1,
    )


def unpack9(y: Array) -> Array:
    y = np.asarray(y, dtype=float).reshape(-1, 9)
    J = np.zeros((len(y), 3, 3), dtype=float)
    J[:, 0, 0] = y[:, 0]
    J[:, 1, 1] = y[:, 1]
    J[:, 2, 2] = y[:, 2]
    J[:, 0, 1] = y[:, 3] + y[:, 8]
    J[:, 1, 0] = y[:, 3] - y[:, 8]
    J[:, 0, 2] = y[:, 4] - y[:, 7]
    J[:, 2, 0] = y[:, 4] + y[:, 7]
    J[:, 1, 2] = y[:, 5] + y[:, 6]
    J[:, 2, 1] = y[:, 5] - y[:, 6]
    return J


def lebedev26() -> tuple[Array, Array]:
    a = 1.0 / np.sqrt(3.0)
    b = 1.0 / np.sqrt(2.0)
    pts: list[Array] = []
    weights: list[float] = []
    for k in range(3):
        for sign in (-1.0, 1.0):
            x = np.zeros(3)
            x[k] = sign
            pts.append(x)
            weights.append(4.0 * pi / 21.0)
    for zero in range(3):
        idx = [i for i in range(3) if i != zero]
        for s1 in (-1.0, 1.0):
            for s2 in (-1.0, 1.0):
                x = np.zeros(3)
                x[idx[0]] = s1 * b
                x[idx[1]] = s2 * b
                pts.append(x)
                weights.append(16.0 * pi / 105.0)
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            for sz in (-1.0, 1.0):
                pts.append(np.array([sx * a, sy * a, sz * a]))
                weights.append(9.0 * pi / 70.0)
    return np.asarray(pts), np.asarray(weights)


def paired_from_rest(e_rest: Array, w_rest: Array, beta: Array) -> tuple[Array, Array, Array]:
    """Construct the moving normal grid paired one-to-one with a rest grid."""
    e_rest = _directions(e_rest)
    w_rest = np.asarray(w_rest, dtype=float)
    if w_rest.shape != (len(e_rest),) or np.any(w_rest <= 0.0):
        raise ValueError("rest weights must be positive and match directions")
    e_normal, _ = aberrate(e_rest, -_beta(beta))
    recovered, doppler = aberrate(e_normal, beta)
    if np.max(np.abs(recovered - e_rest), initial=0.0) > 2e-12:
        raise AssertionError("inverse aberration failed")
    w_normal = w_rest * doppler**2
    return e_normal, w_normal, doppler


def equilibrium(e_normal: Array, beta: Array) -> Array:
    _, doppler = aberrate(e_normal, beta)
    J = 0.5 * doppler[:, None, None] ** (-4.0) * projector_screen(e_normal)
    return pack9(J).ravel()


def collision(e_normal: Array, w_normal: Array, beta: Array, y: Array) -> Array:
    """Dimensionless cold-Thomson shape including normal-time relative flux.

    A dimensional or Hubble-normalized scalar opacity multiplies this action
    outside this bounded witness.
    """
    e = _directions(e_normal)
    w = np.asarray(w_normal, dtype=float)
    b = _beta(beta)
    if w.shape != (len(e),):
        raise ValueError("weights must match directions")
    J = unpack9(y)
    if len(J) != len(e):
        raise ValueError("state size does not match directions")
    S, e_rest, doppler = screen_map(e, b)
    J_rest = doppler[:, None, None] ** 4 * np.einsum(
        "aik,akl,ajl->aij", S, J, S
    )
    w_rest = w / doppler**2
    moment = np.einsum("a,aij->ij", w_rest, J_rest)
    P_rest = projector_screen(e_rest)
    gain = (3.0 / (8.0 * pi)) * np.einsum(
        "aik,kl,alj->aij", P_rest, moment, P_rest
    )
    C_rest = gain - J_rest
    q = 1.0 - e @ b
    C_normal = q[:, None, None] * doppler[:, None, None] ** (-4.0) * np.einsum(
        "aki,akl,alj->aij", S, C_rest, S
    )
    return pack9(C_normal).ravel()


def left_functional(e_normal: Array, w_normal: Array, beta: Array, y: Array) -> float:
    e = _directions(e_normal)
    w = np.asarray(w_normal, dtype=float)
    b = _beta(beta)
    J = unpack9(y)
    q = 1.0 - e @ b
    return float(np.sum(w * q * np.trace(J, axis1=1, axis2=2)) / (4.0 * pi))


def wrong_left_without_direction_factor(e_normal: Array, w_normal: Array, y: Array) -> float:
    J = unpack9(y)
    return float(np.sum(np.asarray(w_normal) * np.trace(J, axis1=1, axis2=2)) / (4.0 * pi))


def moving_projector(e_normal: Array, w_normal: Array, beta: Array, y: Array) -> Array:
    r = equilibrium(e_normal, beta)
    den = left_functional(e_normal, w_normal, beta, r)
    if den == 0.0:
        raise ZeroDivisionError("equilibrium normalization vanished")
    return r * left_functional(e_normal, w_normal, beta, y) / den


def matrix_of(apply: Callable[[Array], Array], n: int) -> Array:
    eye = np.eye(n)
    return np.column_stack([apply(eye[:, j]) for j in range(n)])


def tangent_basis(e: Array) -> tuple[Array, Array]:
    e = np.asarray(e, dtype=float)
    k = int(np.argmin(np.abs(e)))
    a = np.zeros(3)
    a[k] = 1.0
    u = a - float(a @ e) * e
    u /= np.linalg.norm(u)
    v = np.cross(e, u)
    return u, v


def stokes_to_pack(e: Array, z: Array) -> Array:
    e = _directions(e)
    z = np.asarray(z, dtype=float).reshape(len(e), 4)
    tensors = []
    for ei, (I, Q, U, V) in zip(e, z):
        u, v = tangent_basis(ei)
        tensors.append(
            0.5 * I * (np.outer(u, u) + np.outer(v, v))
            + 0.5 * Q * (np.outer(u, u) - np.outer(v, v))
            + 0.5 * U * (np.outer(u, v) + np.outer(v, u))
            + 0.5 * V * (np.outer(u, v) - np.outer(v, u))
        )
    return pack9(np.asarray(tensors)).ravel()


def pack_to_stokes(e: Array, y: Array) -> Array:
    e = _directions(e)
    out: list[float] = []
    for ei, J in zip(e, unpack9(y)):
        u, v = tangent_basis(ei)
        S = 0.5 * (J + J.T)
        A = 0.5 * (J - J.T)
        out.extend(
            [
                float(u @ S @ u + v @ S @ v),
                float(u @ S @ u - v @ S @ v),
                float(2.0 * u @ S @ v),
                float(2.0 * u @ A @ v),
            ]
        )
    return np.asarray(out)


def physical_collision_matrix(e: Array, w: Array, beta: Array) -> Array:
    n = 4 * len(e)
    return matrix_of(
        lambda z: pack_to_stokes(e, collision(e, w, beta, stokes_to_pack(e, z))),
        n,
    )


def rotation_matrix(axis: Array, angle: float) -> Array:
    axis = np.asarray(axis, dtype=float)
    axis /= np.linalg.norm(axis)
    x, y, z = axis
    K = np.array([[0.0, -z, y], [z, 0.0, -x], [-y, x, 0.0]])
    return np.eye(3) + np.sin(angle) * K + (1.0 - np.cos(angle)) * (K @ K)


def rotate_state(y: Array, R: Array) -> Array:
    J = unpack9(y)
    return pack9(np.einsum("ij,ajk,lk->ail", R, J, R)).ravel()


@dataclass(frozen=True)
class Metrics:
    right_null: float
    left_null: float
    projector_idempotence: float
    spectral_nullity: int
    spectral_gap: float
    max_imag_eigenvalue: float


def metrics(beta: Array, seed: int = 1234) -> Metrics:
    e_rest, w_rest = lebedev26()
    e, w, _ = paired_from_rest(e_rest, w_rest, beta)
    r = equilibrium(e, beta)
    rng = np.random.default_rng(seed)
    y = rng.normal(size=9 * len(e))
    cy = collision(e, w, beta, y)
    py = moving_projector(e, w, beta, y)
    ppy = moving_projector(e, w, beta, py)
    C = physical_collision_matrix(e, w, beta)
    eig = np.linalg.eigvals(C)
    nullity = int(np.count_nonzero(np.abs(eig) < 5e-10))
    nz = np.abs(eig[np.abs(eig) >= 5e-10])
    gap = float(np.min(nz)) if len(nz) else 0.0
    return Metrics(
        right_null=float(np.max(np.abs(collision(e, w, beta, r)))),
        left_null=float(abs(left_functional(e, w, beta, cy))),
        projector_idempotence=float(np.max(np.abs(ppy - py))),
        spectral_nullity=nullity,
        spectral_gap=gap,
        max_imag_eigenvalue=float(np.max(np.abs(eig.imag))),
    )
