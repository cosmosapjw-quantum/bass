"""Portable test oracle for the bounded BASS-3 generic-vector host path.

This file adapts only the numerical formulas needed by the focused parity
tests.  Its frozen upstream owners are the scientific-oracle commit
``58d649d438415def3e646d8eee8d0e1f3159ed7f`` and these source SHA-256 values:

* paired carrier: ``0a46342eefce177c4bd1a41fd24bb95ea2bf964f2efdc06eb7836940eef3530f``;
* rate/dual: ``6ca8de5d0fa98c2cc59844afc47143489231e4ec8862e054dd2120f03e183491``;
* bundle differential: ``92ca1196e097acc7f352e2749fa17ae878c032ac9c1f378a95addecc2c6b6b78``;
* projector/Kato audit: ``05dd474ab9a531ac5e751e058d9d858eed2f0bd66912e1219f86f5ccd1b7a480``.

It is test-only and does not participate in production dispatch.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import pi

import numpy as np


IDENTITY_MAX = 2e-10
FINITE_DIFFERENCE_PROJECTOR_MAX = 2e-7
GLOBAL_SCALAR_MAX = 2e-12
MUTATION_MIN = 1e-10
SO3_MAX = 2e-10


def lebedev26() -> tuple[np.ndarray, np.ndarray]:
    a = 1.0 / np.sqrt(3.0)
    b = 1.0 / np.sqrt(2.0)
    directions: list[np.ndarray] = []
    weights: list[float] = []
    for axis in range(3):
        for sign in (-1.0, 1.0):
            value = np.zeros(3)
            value[axis] = sign
            directions.append(value)
            weights.append(4.0 * pi / 21.0)
    for zero in range(3):
        live = [axis for axis in range(3) if axis != zero]
        for sign0 in (-1.0, 1.0):
            for sign1 in (-1.0, 1.0):
                value = np.zeros(3)
                value[live[0]] = sign0 * b
                value[live[1]] = sign1 * b
                directions.append(value)
                weights.append(16.0 * pi / 105.0)
    for x in (-1.0, 1.0):
        for y in (-1.0, 1.0):
            for z in (-1.0, 1.0):
                directions.append(np.array([x * a, y * a, z * a]))
                weights.append(9.0 * pi / 70.0)
    return np.asarray(directions), np.asarray(weights)


def _validate(e_rest: np.ndarray, w_rest: np.ndarray, beta: np.ndarray) -> None:
    if e_rest.ndim != 2 or e_rest.shape[1] != 3:
        raise ValueError("e_rest must have shape (N,3)")
    if w_rest.shape != (len(e_rest),):
        raise ValueError("w_rest must have shape (N,)")
    if not np.isfinite(e_rest).all() or not np.isfinite(w_rest).all():
        raise ValueError("quadrature must be finite")
    if np.max(np.abs(np.linalg.norm(e_rest, axis=1) - 1.0), initial=0.0) > 3e-13:
        raise ValueError("directions must be unit vectors")
    if np.any(w_rest <= 0.0):
        raise ValueError("weights must be positive")
    if beta.shape != (3,) or not np.isfinite(beta).all() or float(beta @ beta) >= 1.0:
        raise ValueError("beta must be a finite subluminal three-vector")


def projector_screen(directions: np.ndarray) -> np.ndarray:
    return np.eye(3)[None, :, :] - np.einsum(
        "ai,aj->aij", directions, directions
    )


def pack9(tensors: np.ndarray) -> np.ndarray:
    symmetric = 0.5 * (tensors + tensors.swapaxes(1, 2))
    antisymmetric = 0.5 * (tensors - tensors.swapaxes(1, 2))
    return np.stack(
        [
            symmetric[:, 0, 0],
            symmetric[:, 1, 1],
            symmetric[:, 2, 2],
            symmetric[:, 0, 1],
            symmetric[:, 0, 2],
            symmetric[:, 1, 2],
            antisymmetric[:, 1, 2],
            antisymmetric[:, 2, 0],
            antisymmetric[:, 0, 1],
        ],
        axis=1,
    )


def unpack9(values: np.ndarray) -> np.ndarray:
    packed = np.asarray(values, dtype=float).reshape(-1, 9)
    tensors = np.zeros((len(packed), 3, 3))
    tensors[:, 0, 0] = packed[:, 0]
    tensors[:, 1, 1] = packed[:, 1]
    tensors[:, 2, 2] = packed[:, 2]
    tensors[:, 0, 1] = packed[:, 3] + packed[:, 8]
    tensors[:, 1, 0] = packed[:, 3] - packed[:, 8]
    tensors[:, 0, 2] = packed[:, 4] - packed[:, 7]
    tensors[:, 2, 0] = packed[:, 4] + packed[:, 7]
    tensors[:, 1, 2] = packed[:, 5] + packed[:, 6]
    tensors[:, 2, 1] = packed[:, 5] - packed[:, 6]
    return tensors


@dataclass(frozen=True)
class OracleBundle:
    e_rest: np.ndarray
    w_rest: np.ndarray
    beta: np.ndarray
    beta_dot: np.ndarray
    gamma: float
    e_normal: np.ndarray
    e_normal_dot: np.ndarray
    doppler: np.ndarray
    doppler_dot: np.ndarray
    direction_factor: np.ndarray
    direction_factor_dot: np.ndarray
    w_normal: np.ndarray
    w_normal_dot: np.ndarray
    screen_map: np.ndarray
    equilibrium: np.ndarray
    equilibrium_dot: np.ndarray
    normalized_left: np.ndarray
    normalized_left_dot: np.ndarray
    projector: np.ndarray
    projector_dot: np.ndarray


def paired_bundle(
    e_rest: np.ndarray,
    w_rest: np.ndarray,
    beta: np.ndarray,
    beta_dot: np.ndarray,
) -> OracleBundle:
    e0 = np.asarray(e_rest, dtype=float)
    w0 = np.asarray(w_rest, dtype=float)
    b = np.asarray(beta, dtype=float)
    db = np.asarray(beta_dot, dtype=float)
    _validate(e0, w0, b)
    if db.shape != (3,) or not np.isfinite(db).all():
        raise ValueError("beta_dot must be a finite three-vector")

    beta2 = float(b @ b)
    gamma = float(1.0 / np.sqrt(1.0 - beta2))
    gamma_dot = float(gamma**3 * (b @ db))
    scalar = e0 @ b
    scalar_dot = e0 @ db
    h = gamma * gamma / (gamma + 1.0)
    h_dot = gamma * (gamma + 2.0) / (gamma + 1.0) ** 2 * gamma_dot
    coefficient = gamma + h * scalar
    coefficient_dot = gamma_dot + h_dot * scalar + h * scalar_dot
    denominator = gamma * (1.0 + scalar)
    denominator_dot = gamma_dot * (1.0 + scalar) + gamma * scalar_dot
    e = (e0 + coefficient[:, None] * b[None, :]) / denominator[:, None]
    de = (
        (
            coefficient_dot[:, None] * b[None, :]
            + coefficient[:, None] * db[None, :]
        )
        / denominator[:, None]
        - e * (denominator_dot / denominator)[:, None]
    )
    doppler = 1.0 / denominator
    doppler_dot = -denominator_dot / denominator**2
    q = 1.0 - e @ b
    q_dot = -(de @ b + e @ db)
    w = w0 * doppler**2
    w_dot = 2.0 * w * doppler_dot / doppler

    screen = projector_screen(e)
    screen_dot = -(
        np.einsum("ai,aj->aij", de, e) + np.einsum("ai,aj->aij", e, de)
    )
    projected_beta = np.einsum("aij,j->ai", screen, b)
    screen_map = (
        screen
        + h * np.einsum("i,ak->aik", b, projected_beta)
        + gamma * np.einsum("ai,ak->aik", e0, projected_beta)
    )

    equilibrium_tensor = 0.5 * doppler[:, None, None] ** (-4.0) * screen
    equilibrium_dot_tensor = (
        -2.0
        * doppler[:, None, None] ** (-5.0)
        * doppler_dot[:, None, None]
        * screen
        + 0.5 * doppler[:, None, None] ** (-4.0) * screen_dot
    )
    r = pack9(equilibrium_tensor).ravel()
    dr = pack9(equilibrium_dot_tensor).ravel()
    left_node = w * q / (4.0 * pi)
    left_node_dot = (w_dot * q + w * q_dot) / (4.0 * pi)
    raw_left = np.zeros((len(e0), 9))
    raw_left[:, :3] = left_node[:, None]
    raw_left_dot = np.zeros((len(e0), 9))
    raw_left_dot[:, :3] = left_node_dot[:, None]
    raw_left = raw_left.ravel()
    raw_left_dot = raw_left_dot.ravel()
    normalization = float(raw_left @ r)
    normalization_dot = float(raw_left_dot @ r + raw_left @ dr)
    a = raw_left / normalization
    da = (
        raw_left_dot / normalization
        - raw_left * normalization_dot / normalization**2
    )
    projector = np.outer(r, a)
    projector_dot = np.outer(dr, a) + np.outer(r, da)
    return OracleBundle(
        e_rest=e0,
        w_rest=w0,
        beta=b,
        beta_dot=db,
        gamma=gamma,
        e_normal=e,
        e_normal_dot=de,
        doppler=doppler,
        doppler_dot=doppler_dot,
        direction_factor=q,
        direction_factor_dot=q_dot,
        w_normal=w,
        w_normal_dot=w_dot,
        screen_map=screen_map,
        equilibrium=r,
        equilibrium_dot=dr,
        normalized_left=a,
        normalized_left_dot=da,
        projector=projector,
        projector_dot=projector_dot,
    )


def collision_action(bundle: OracleBundle, alpha: float, values: np.ndarray) -> np.ndarray:
    tensors = unpack9(values)
    doppler = bundle.doppler
    transformed = doppler[:, None, None] ** 4 * np.einsum(
        "aik,akl,ajl->aij", bundle.screen_map, tensors, bundle.screen_map
    )
    rest_weights = bundle.w_normal / doppler**2
    moment = np.einsum("a,aij->ij", rest_weights, transformed)
    rest_screen = projector_screen(bundle.e_rest)
    gain = (3.0 / (8.0 * pi)) * np.einsum(
        "aik,kl,alj->aij", rest_screen, moment, rest_screen
    )
    collision_rest = gain - transformed
    pulled = np.einsum(
        "aki,akl,alj->aij",
        bundle.screen_map,
        collision_rest,
        bundle.screen_map,
    )
    shape = (
        bundle.direction_factor[:, None, None]
        * doppler[:, None, None] ** (-4.0)
        * pulled
    )
    return alpha * bundle.gamma * pack9(shape).ravel()


def collision_matrix(bundle: OracleBundle, alpha: float) -> np.ndarray:
    size = 9 * len(bundle.e_rest)
    identity = np.eye(size)
    return np.column_stack(
        [collision_action(bundle, alpha, identity[:, column]) for column in range(size)]
    )


def finite_difference_projector(
    e_rest: np.ndarray,
    w_rest: np.ndarray,
    beta: np.ndarray,
    beta_dot: np.ndarray,
    step: float = 1e-6,
) -> np.ndarray:
    zero = np.zeros(3)
    plus = paired_bundle(e_rest, w_rest, beta + step * beta_dot, zero).projector
    minus = paired_bundle(e_rest, w_rest, beta - step * beta_dot, zero).projector
    return (plus - minus) / (2.0 * step)


def rotation_matrix(axis: np.ndarray, angle: float) -> np.ndarray:
    direction = np.asarray(axis, dtype=float)
    direction /= np.linalg.norm(direction)
    x, y, z = direction
    cross = np.array([[0.0, -z, y], [z, 0.0, -x], [-y, x, 0.0]])
    return np.eye(3) + np.sin(angle) * cross + (1.0 - np.cos(angle)) * (cross @ cross)


def rotate_state(values: np.ndarray, rotation: np.ndarray) -> np.ndarray:
    tensors = unpack9(values)
    return pack9(
        np.einsum("ij,ajk,lk->ail", rotation, tensors, rotation)
    ).ravel()
