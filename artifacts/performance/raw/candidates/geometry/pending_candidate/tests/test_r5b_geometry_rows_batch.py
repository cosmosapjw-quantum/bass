"""Focused contract for batched R5b geometry-row construction."""

import numpy as np
import pytest

from bianchi.matter import tilted_integrate as TI
from bianchi.matter import tilted_rust as TR


_BINARY64_U = 2.0 ** -53
_OPERATION_ORDER_FACTOR = 8.0


def _scalar_geometry_rows(bg, nsteps, dt):
    rows = np.empty((3 * nsteps, TR._GEO_LEN))
    for step in range(nsteps):
        t = step * dt
        for offset, time_value in enumerate((t, t + 0.5 * dt, t + dt)):
            rows[3 * step + offset] = TR.pack_geo(bg.geometry(time_value))
    return rows


def test_zero_steps_has_the_empty_native_row_shape():
    rows = TR.geometry_rows(TI.Background(), 0, 0.001)
    assert rows.shape == (0, TR._GEO_LEN)
    assert rows.dtype == np.dtype(float)


def _assert_direct_rows_match_the_scalar_oracle(background, nsteps, dt):
    expected = _scalar_geometry_rows(background, nsteps, dt)
    actual = TR.geometry_rows(background, nsteps, dt)

    assert actual.shape == expected.shape == (3 * nsteps, TR._GEO_LEN)
    assert np.isfinite(actual).all()
    magnitude = max(1.0, float(np.abs(expected).max()),
                    float(np.abs(actual).max()))
    max_abs_difference = float(np.abs(actual - expected).max())
    limit = _OPERATION_ORDER_FACTOR * _BINARY64_U * magnitude
    assert max_abs_difference <= limit, (max_abs_difference, limit, magnitude)
    assert np.array_equal(actual, expected)


def test_exact_background_direct_rows_match_the_scalar_geometry_oracle():
    """The fixed 8u gate is retained, and current authority is byte-identical."""
    _assert_direct_rows_match_the_scalar_oracle(
        TI.Background(), nsteps=200, dt=0.001)


def test_nondefault_exact_background_rows_are_also_byte_identical():
    background = TI.Background(
        a0=(1.7, 0.8, 1.1),
        H=-0.25,
        sigma_diag=(0.03, 0.01, -0.04),
        v0=(0.31, 0.09, -0.22),
        dv=(-0.02, 0.04, 0.01),
    )
    _assert_direct_rows_match_the_scalar_oracle(
        background, nsteps=40, dt=0.005)


def test_background_subclass_retains_the_scalar_geometry_path():
    class CountingBackground(TI.Background):
        def __init__(self):
            super().__init__()
            self.geometry_calls = 0

        def geometry(self, time_value):
            self.geometry_calls += 1
            return super().geometry(time_value)

    expected = _scalar_geometry_rows(TI.Background(), 4, 0.013)
    background = CountingBackground()
    actual = TR.geometry_rows(background, 4, 0.013)
    assert background.geometry_calls == 12
    assert np.array_equal(actual, expected)


@pytest.mark.skipif(not TR.USE_RUST,
                    reason="bianchi_rustcore R5b kernel unavailable")
def test_short_native_history_matches_the_scalar_geometry_path(monkeypatch):
    """Both geometry paths must stay inside the native whole-loop boundary."""
    class ScalarBackground(TI.Background):
        pass

    def unexpected_python_rhs(*_args, **_kwargs):
        raise AssertionError("short-history comparison used the Python RHS")

    assert TI.rust_available("ratio", jdot_closure=True, n_star=None)
    monkeypatch.setattr(TI, "rhs", unexpected_python_rhs)
    kwargs = dict(mass=1.0, t_end=0.02, nsteps=20, l_max=3, i_max=3,
                  mode="ratio", jdot_closure=True, n_star=None, backend=None)
    batched = TI.integrate(TI.Background(), **kwargs)
    scalar = TI.integrate(ScalarBackground(), **kwargs)

    assert np.array_equal(np.asarray(batched["t"]), np.asarray(scalar["t"]))
    for checkpoint, (batched_state, scalar_state) in enumerate(
            zip(batched["J"], scalar["J"])):
        assert set(batched_state) == set(scalar_state), checkpoint
        batched_rho = abs(float(np.asarray(batched_state[(0, 0)], float)))
        scalar_rho = abs(float(np.asarray(scalar_state[(0, 0)], float)))
        assert np.isfinite(batched_rho) and batched_rho > 0.0
        assert np.isfinite(scalar_rho) and scalar_rho > 0.0
        rho_scale = max(batched_rho, scalar_rho)
        for key in sorted(batched_state):
            batched_value = np.asarray(batched_state[key], float)
            scalar_value = np.asarray(scalar_state[key], float)
            assert batched_value.shape == scalar_value.shape
            assert np.isfinite(batched_value).all()
            assert np.isfinite(scalar_value).all()
            denominator = max(rho_scale,
                              float(np.abs(batched_value).max()),
                              float(np.abs(scalar_value).max()))
            gap = float(np.abs(batched_value - scalar_value).max()) / denominator
            assert gap <= 1e-12, (checkpoint, key, gap, denominator)
