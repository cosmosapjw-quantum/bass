from __future__ import annotations

import numpy as np

from generic_vector_paired_carrier import (
    aberrate,
    collision,
    equilibrium,
    left_functional,
    lebedev26,
    metrics,
    moving_projector,
    paired_from_rest,
    rotation_matrix,
    rotate_state,
    wrong_left_without_direction_factor,
)


def test_zero_tilt_recovery():
    e0, w0 = lebedev26()
    e, w, D = paired_from_rest(e0, w0, np.zeros(3))
    assert np.max(np.abs(e-e0)) == 0.0
    assert np.max(np.abs(w-w0)) == 0.0
    assert np.max(np.abs(D-1.0)) == 0.0


def test_generic_vector_right_left_and_projector():
    beta = np.array([0.17, -0.09, 0.11])
    beta *= 0.23 / np.linalg.norm(beta)
    m = metrics(beta)
    assert m.right_null < 2e-13
    assert m.left_null < 2e-13
    assert m.projector_idempotence < 2e-13
    assert m.spectral_nullity == 1
    assert m.spectral_gap > 0.1
    assert m.max_imag_eigenvalue < 2e-12


def test_so3_covariance():
    e0, w0 = lebedev26()
    beta = np.array([0.13, -0.07, 0.16])
    e, w, _ = paired_from_rest(e0, w0, beta)
    rng = np.random.default_rng(31)
    y = rng.normal(size=9*len(e))
    R = rotation_matrix(np.array([0.2, -0.4, 0.7]), 0.91)
    er = e @ R.T
    br = R @ beta
    yr = rotate_state(y, R)
    lhs = collision(er, w, br, yr)
    rhs = rotate_state(collision(e, w, beta, y), R)
    assert np.max(np.abs(lhs-rhs)) < 2e-12
    pl = moving_projector(er, w, br, yr)
    pr = rotate_state(moving_projector(e, w, beta, y), R)
    assert np.max(np.abs(pl-pr)) < 2e-12


def test_typeii_axis_is_restriction_of_generic_vector():
    e0, w0 = lebedev26()
    v = 0.19
    beta = np.array([0.0, v, 0.0])
    e, w, _ = paired_from_rest(e0, w0, beta)
    recovered, _ = aberrate(e, beta)
    assert np.max(np.abs(recovered-e0)) < 2e-13
    m = metrics(beta)
    assert m.right_null < 2e-13
    assert m.left_null < 2e-13


def test_omitting_direction_factor_breaks_left_invariant():
    e0, w0 = lebedev26()
    beta = np.array([0.2, -0.11, 0.06])
    e, w, _ = paired_from_rest(e0, w0, beta)
    rng = np.random.default_rng(7)
    y = rng.normal(size=9*len(e))
    cy = collision(e, w, beta, y)
    good = abs(left_functional(e, w, beta, cy))
    bad = abs(wrong_left_without_direction_factor(e, w, cy))
    assert good < 2e-13
    assert bad > 1e-6


def test_fixed_normal_grid_is_negative_control_at_finite_tilt():
    e, w = lebedev26()
    beta = np.array([0.0, 0.2, 0.0])
    residual = np.max(np.abs(collision(e, w, beta, equilibrium(e, beta))))
    assert residual > 1e-7
