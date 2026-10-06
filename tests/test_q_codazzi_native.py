"""Wrapper validation plus real binding tests, with no substitute extension.

The integration test requires a rebuilt policy-accepted extension and fails
(rather than skipping or claiming success) when it is unavailable.
"""
import numpy as np
import pytest
from bianchi.q.diagnostics import codazzi_residual_native


@pytest.mark.parametrize("which,value", [
    (0, np.zeros(9)), (1, np.zeros((1, 9))), (2, np.zeros((3, 1))),
    (3, np.zeros(2)), (0, np.full((3, 3), np.nan)),
    (1, np.full((3, 3), np.inf)), (2, [0, -np.inf, 0]), (3, [0, np.nan, 0]),
])
def test_invalid_inputs_fail_before_native_loading(which, value):
    args = [np.zeros((3, 3)), np.zeros((3, 3)), np.zeros(3), np.zeros(3)]
    args[which] = value
    with pytest.raises(ValueError):
        codazzi_residual_native(*args)


def test_real_native_binding_codazzi():
    s = np.array([[1., 2., 3.], [2., -3., 4.], [3., 4., 2.]])
    n = np.diag([1., 3., 7.])
    # Independent analytic result: 3*S@[2,-1,3] + [-16,18,-4] - q.
    np.testing.assert_allclose(codazzi_residual_native(s, n, [2., -1., 3.], [1., 2., 3.]),
                               [10., 73., 17.], rtol=0, atol=1e-14)
    np.testing.assert_allclose(codazzi_residual_native(s, n, [0., 0., 0.]), [-16., 18., -4.])


def test_real_qstate_native_diagnostic_matches_jax_oracle():
    from bianchi.q import sphere
    from bianchi.q.coupled import QState
    sph = sphere.sphere(8, 16)
    sigma = np.array([[0.1, 0.02, -0.03], [0.02, -0.04, 0.05], [-0.03, 0.05, -0.06]])
    state = QState(sph, sigma, np.diag([0.2, 0.4, 0.7]), [0.02, -0.01, 0.03])
    state.lG = 0.1 * state.qhat[:, 0]  # nonzero flux tests normalization/sign
    # This must call the separately named JAX oracle, not compare native aliases.
    np.testing.assert_allclose(state.codazzi_residual(), state.codazzi_residual_python_oracle(),
                               rtol=1e-12, atol=1e-12)


def test_qstate_default_codazzi_works_without_importing_optional_stacks():
    """Exercise the real default public route in a fresh process, not an alias."""
    import subprocess
    import sys
    code = r'''
import sys
import numpy as np
from bianchi.q import sphere, comoving as CM
from bianchi.q.coupled import QState
sigma = np.array([[0.1, 0.02, -0.03], [0.02, -0.04, 0.05], [-0.03, 0.05, -0.06]])
n = np.diag([0.2, 0.4, 0.7])
a = np.array([0.02, -0.01, 0.03])
state = QState(sphere.sphere(8, 16), sigma, n, a)
state.lG = 0.1 * state.qhat[:, 0]
actual = state.codazzi_residual()
_, e, _, lw = state.geometry()
ln_rho, q_over_rho, _ = CM.moments_log(lw, state.lG, e)
omega = np.exp(ln_rho - np.log(3.0) - 2.0 * state.lnH)
# Independent diagonal-N formula for the epsilon contraction.
epsilon_term = np.array([(n[1,1]-n[2,2])*sigma[1,2],
                         (n[2,2]-n[0,0])*sigma[0,2],
                         (n[0,0]-n[1,1])*sigma[0,1]])
expected = 3.0 * sigma @ a + epsilon_term - 3.0 * omega * q_over_rho
np.testing.assert_allclose(actual, expected, rtol=1e-12, atol=1e-12)
np.testing.assert_array_equal(actual, state.codazzi_residual_native())
assert not any(name.split('.')[0] in {'jax', 'jaxlib', 'scipy'} for name in sys.modules)
'''
    result = subprocess.run([sys.executable, "-c", code], text=True, capture_output=True)
    assert result.returncode == 0, result.stdout + result.stderr
