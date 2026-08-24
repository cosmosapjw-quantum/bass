"""Independent 4-vector oracle for the BASS-8B.1E frame adapter.

This audit intentionally does not import the production Doppler or screen-map
implementations.  It constructs the full Lorentz matrix, transforms the photon
four-vector, and gauge-restores three screen representatives directly.  The
test suite passes the production module into :func:`run` and compares paths.
"""
from __future__ import annotations

import numpy as np


ETA = np.diag([-1.0, 1.0, 1.0, 1.0])


def _boost(beta):
    beta = np.asarray(beta, float)
    b2 = float(beta @ beta)
    if b2 >= 1.0:
        raise ValueError("oracle beta must be subluminal")
    if b2 == 0.0:
        return np.eye(4)
    gamma = 1.0 / np.sqrt(1.0 - b2)
    out = np.eye(4)
    out[0, 0] = gamma
    out[0, 1:] = -gamma * beta
    out[1:, 0] = -gamma * beta
    out[1:, 1:] += (gamma - 1.0) * np.outer(beta, beta) / b2
    return out


def _frame(beta_source, beta_target):
    return _boost(beta_target) @ _boost(-np.asarray(beta_source, float))


def photon(energy, direction, beta_source, beta_target):
    """Direct full-matrix photon transformation (single ray)."""
    transform = _frame(beta_source, beta_target)
    p = np.asarray(energy, float) * np.r_[1.0, np.asarray(direction, float)]
    out = transform @ p
    return float(out[0]), out[1:] / out[0], float(out[0] / energy)


def polarization_shape(shape, direction, beta_source, beta_target):
    """Direct screen-representative transformation (single ray)."""
    transform = _frame(beta_source, beta_target)
    direction = np.asarray(direction, float)
    p = transform @ np.r_[1.0, direction]
    target_direction = p[1:] / p[0]

    source_projector = np.eye(3) - np.outer(direction, direction)
    representatives = np.zeros((4, 3))
    representatives[1:] = source_projector
    moved = transform @ representatives
    screen_map = moved[1:] - np.outer(p[1:] / p[0], moved[0])

    target_projector = np.eye(3) - np.outer(target_direction, target_direction)
    carrier = screen_map @ np.asarray(shape, float) @ screen_map.T
    carrier = target_projector @ carrier @ target_projector
    carrier /= np.trace(carrier)
    return carrier, target_direction, float(p[0])


def run(adapter, *, n=400, seed=20260823, vmax=0.85):
    """Hostile randomized comparison against the production adapter."""
    rng = np.random.default_rng(seed)
    maxima = {
        "metric": 0.0,
        "inverse": 0.0,
        "gamma": 0.0,
        "photon_energy": 0.0,
        "photon_direction": 0.0,
        "photon_roundtrip": 0.0,
        "polarization": 0.0,
        "polarization_roundtrip": 0.0,
        "screen_leak": 0.0,
        "trace": 0.0,
        "wigner_spatial_asymmetry": 0.0,
    }
    for _ in range(int(n)):
        beta_source = rng.normal(size=3)
        beta_source *= rng.uniform(0.0, vmax) / np.linalg.norm(beta_source)
        beta_target = rng.normal(size=3)
        beta_target *= rng.uniform(0.0, vmax) / np.linalg.norm(beta_target)
        direction = rng.normal(size=3)
        direction /= np.linalg.norm(direction)
        energy = float(np.exp(rng.uniform(-12.0, 12.0)))

        matrix = adapter.frame_matrix(beta_source, beta_target)
        inverse = adapter.frame_matrix(beta_target, beta_source)
        maxima["metric"] = max(
            maxima["metric"], float(np.max(np.abs(matrix.T @ ETA @ matrix - ETA)))
        )
        maxima["inverse"] = max(
            maxima["inverse"], float(np.max(np.abs(inverse @ matrix - np.eye(4))))
        )
        maxima["gamma"] = max(
            maxima["gamma"],
            abs(float(matrix[0, 0]) - adapter.relative_gamma(beta_source, beta_target)),
        )
        maxima["wigner_spatial_asymmetry"] = max(
            maxima["wigner_spatial_asymmetry"],
            float(np.max(np.abs(matrix[1:, 1:] - matrix[1:, 1:].T))),
        )

        expected_energy, expected_direction, _ = photon(
            energy, direction, beta_source, beta_target
        )
        got_energy, got_direction, _ = adapter.transform_photon(
            energy, direction, beta_source, beta_target
        )
        maxima["photon_energy"] = max(
            maxima["photon_energy"], abs(got_energy / expected_energy - 1.0)
        )
        maxima["photon_direction"] = max(
            maxima["photon_direction"],
            float(np.max(np.abs(got_direction - expected_direction))),
        )
        back_energy, back_direction, _ = adapter.transform_photon(
            got_energy, got_direction, beta_target, beta_source
        )
        maxima["photon_roundtrip"] = max(
            maxima["photon_roundtrip"],
            abs(back_energy / energy - 1.0),
            float(np.max(np.abs(back_direction - direction))),
        )

        projector = np.eye(3) - np.outer(direction, direction)
        seed_matrix = rng.normal(size=(3, 3))
        shape = projector @ seed_matrix @ seed_matrix.T @ projector
        shape /= np.trace(shape)
        expected_shape, expected_e, _ = polarization_shape(
            shape, direction, beta_source, beta_target
        )
        got_shape, got_e, _ = adapter.transform_polarization_shape(
            shape, direction, beta_source, beta_target
        )
        maxima["polarization"] = max(
            maxima["polarization"],
            float(np.max(np.abs(got_shape - expected_shape))),
            float(np.max(np.abs(got_e - expected_e))),
        )
        back_shape, back_e, _ = adapter.transform_polarization_shape(
            got_shape, got_e, beta_target, beta_source
        )
        maxima["polarization_roundtrip"] = max(
            maxima["polarization_roundtrip"],
            float(np.max(np.abs(back_shape - shape))),
            float(np.max(np.abs(back_e - direction))),
        )
        maxima["screen_leak"] = max(
            maxima["screen_leak"],
            float(np.max(np.abs(got_shape @ got_e))),
        )
        maxima["trace"] = max(maxima["trace"], abs(float(np.trace(got_shape)) - 1.0))
    return maxima

