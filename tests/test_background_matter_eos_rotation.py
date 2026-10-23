"""Normal-frame gamma-law conservation and moving-frame constraint regression.

These tests differentiate the Einstein constraints before any projection.  They
exercise the generic matter chart; no kinetic EOS or tilted-fluid closure is
inferred from a supplied deceleration override.
"""

import numpy as np
import pytest

from bianchi.charts import general_matter as GM
from bianchi import constraint_rates as CR
from bianchi.optional_dependencies import require_jax_x64

jax, jnp = require_jax_x64(feature=__name__)


def _data(gamma=4.0 / 3.0):
    sigma = np.array([[0.21, 0.04, -0.03],
                      [0.04, -0.16, 0.02],
                      [-0.03, 0.02, -0.05]])
    n = GM.jacobi_safe_N(0.6, 0.08, -0.4)
    y, args = GM.on_constraint_surface(sigma, n, 0.12, gamma=gamma)
    y = GM.StateGM.from_packed(y.packed())
    args["Pi"] = np.array([[0.013, -0.004, 0.006],
                           [-0.004, -0.008, 0.003],
                           [0.006, 0.003, -0.005]])
    args["Pi"][2, 2] = -args["Pi"][0, 0] - args["Pi"][1, 1]
    return y, args


def _extended(y, pi):
    return jnp.concatenate([y.packed(), jnp.asarray(
        [pi[0, 0], pi[1, 1], pi[0, 1], pi[0, 2], pi[1, 2]])])


@pytest.mark.parametrize("gamma", [1.0, 4.0 / 3.0, 2.0])
def test_flat_flrw_is_a_fixed_point_for_each_gamma(gamma):
    y = GM.StateGM.of(np.zeros((3, 3)), np.zeros((3, 3)),
                      np.zeros(3), np.zeros(3), 1.0)
    dy = GM.rhs(0.0, y, {"gamma": gamma})
    np.testing.assert_allclose(dy.packed(), 0.0, atol=2e-15, rtol=0.0)


@pytest.mark.parametrize("gamma", [1.0, 4.0 / 3.0, 2.0])
@pytest.mark.parametrize("rotating", [False, True])
def test_class_b_flow_is_tangent_to_all_constraints(gamma, rotating):
    y, args = _data(gamma)
    if rotating:
        args["R"] = np.array([0.2, -0.1, 0.3])
    c = lambda v: GM.constraint_vector(GM.StateGM.from_packed(v), args)
    v = y.packed()
    cv, dcv = jax.jvp(c, (v,), (GM.rhs(0.0, y, args).packed(),))
    np.testing.assert_allclose(cv, 0.0, atol=2e-15, rtol=0.0)
    np.testing.assert_allclose(dcv, 0.0, atol=2e-12, rtol=0.0)


def test_time_dependent_frame_rotation_rotates_every_spatial_index():
    y, args = _data(1.0)
    r = np.array([0.2, -0.1, 0.3])
    # Independent cross-product representation, not the production helper.
    w = np.column_stack([np.cross(r, e) for e in np.eye(3)])
    df = GM.rhs(0.0, y, dict(args, R=r)).packed() - GM.rhs(0.0, y, args).packed()
    expected = GM.StateGM.of(w @ y.Sigma - y.Sigma @ w,
                             w @ y.N - y.N @ w,
                             w @ y.A, w @ y.Q, 0.0).packed()
    np.testing.assert_allclose(df, expected, atol=2e-15, rtol=0.0)


def test_radiation_fermi_rhs_matches_the_historical_fitted_flow():
    y, args = _data()
    old = CR.flow_fn(4.0 / 3.0, CR.CLOSURE_COEFFS)(_extended(y, args["Pi"]))[:18]
    np.testing.assert_array_equal(GM.rhs(0.0, y, args).packed(), old)


@pytest.mark.parametrize("gamma", [1.0, 4.0 / 3.0, 2.0])
def test_explicit_gamma_law_diagnostic_flow_preserves_constraints(gamma):
    y, args = _data(gamma)
    v = _extended(y, args["Pi"])
    f = CR.flow_fn(gamma, CR.CLOSURE_COEFFS, gamma_law=True)
    c = CR.constraint_fn(gamma)
    cv, dcv = jax.jvp(c, (v,), (f(v),))
    np.testing.assert_allclose(cv, 0.0, atol=2e-15, rtol=0.0)
    np.testing.assert_allclose(dcv, 0.0, atol=2e-12, rtol=0.0)


def test_freeze_matter_still_freezes_nonradiation_diagnostic():
    y, args = _data(1.0)
    f = CR.flow_fn(1.0, CR.CLOSURE_COEFFS, freeze_matter=True, gamma_law=True)
    np.testing.assert_array_equal(f(_extended(y, args["Pi"]))[14:], np.zeros(9))


def test_custom_diagnostic_coefficients_keep_their_raw_basis():
    y, args = _data(1.0)
    v = _extended(y, args["Pi"])
    zero = CR.flow_fn(1.0, np.zeros(11))(v)
    np.testing.assert_array_equal(zero[14:], np.zeros(9))
    c = np.zeros(11)
    c[7] = 0.25
    raw = CR.flow_fn(1.0, c)(v)
    np.testing.assert_allclose(raw[17], 0.25 * y.Omega, atol=0.0, rtol=0.0)
    np.testing.assert_array_equal(c, np.array([0., 0., 0., 0., 0., 0., 0., .25, 0., 0., 0.]))


def test_historical_radiation_coefficient_fit_is_preserved():
    np.testing.assert_array_equal(CR.CLOSURE_COEFFS,
        np.array([-2.0, -1.0, 2.0, 3.0, 1.0, 0.0, 0.0,
                  -2.0, 2.0, 2.0 / 3.0, -1.0 / 3.0]))


@pytest.mark.parametrize("gamma", [1.0, 2.0])
def test_default_constraint_amplification_uses_the_gamma_law(gamma):
    y, args = _data(gamma)
    result = CR.amplification_matrix(_extended(y, args["Pi"]), gamma)
    assert result["residual"] < 2e-11, result["residual"]
