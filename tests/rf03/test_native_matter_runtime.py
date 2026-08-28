from __future__ import annotations

import importlib
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest


MODEL_ID = "explicit_gamma_law_tilted_perfect_fluid_v1"


def _native():
    return importlib.import_module("bianchi_rustcore")


def _context():
    sigma = np.array(
        [[0.07, -0.02, 0.01], [-0.02, -0.04, 0.03], [0.01, 0.03, -0.03]],
        dtype=np.float64,
    )
    n = np.array(
        [[0.2, 0.03, -0.01], [0.03, -0.1, 0.04], [-0.01, 0.04, 0.05]],
        dtype=np.float64,
    )
    a = np.array([0.04, -0.03, 0.02], dtype=np.float64)
    r = np.array([-0.02, 0.01, 0.03], dtype=np.float64)
    return sigma, n, a, r, 0.41


def _oracle_force(gamma: float, state: np.ndarray) -> np.ndarray:
    from bianchi.matter.fluid import TiltedFluid, dOmega, dv_general, sources

    sigma, n, a, r, q = _context()
    fluid = TiltedFluid.of(gamma, state[0], state[1:])
    src = sources(fluid, sigma, a)
    return np.concatenate(
        (
            np.atleast_1d(np.asarray(dOmega(fluid, src, q), dtype=np.float64)),
            np.asarray(dv_general(fluid, src, sigma, n, a, r), dtype=np.float64),
        )
    )


def test_rf03_native_symbols_are_present() -> None:
    native = _native()
    required = {
        "rf03_matter_force",
        "rf03_matter_force_jvp",
        "rf03_matter_integrate",
        "rf03_matter_integrate_history",
        "rf03_tilt_invariants",
        "RF03ModelError",
        "RF03DomainError",
        "RF03InputError",
    }
    assert required <= set(dir(native))


def test_force_matches_frozen_python_source() -> None:
    state = np.array([0.37, 0.13, -0.08, 0.04], dtype=np.float64)
    sigma, n, a, r, q = _context()

    observed = np.asarray(
        _native().rf03_matter_force(
            MODEL_ID, 1.31, state, sigma, n, a, r, q, 2.7255
        ),
        dtype=np.float64,
    )

    np.testing.assert_allclose(observed, _oracle_force(1.31, state), rtol=2e-13, atol=2e-14)


def test_analytic_jvp_matches_jax_directional_derivative() -> None:
    import jax
    import jax.numpy as jnp

    from bianchi.matter.fluid import TiltedFluid, dOmega, dv_general, sources

    state = np.array([0.42, -0.11, 0.06, 0.09], dtype=np.float64)
    direction = np.array([0.07, 0.03, -0.02, 0.04], dtype=np.float64)
    sigma, n, a, r, q = _context()

    def oracle(x):
        fluid = TiltedFluid.of(1.27, x[0], x[1:])
        src = sources(fluid, sigma, a)
        return jnp.concatenate(
            (jnp.atleast_1d(dOmega(fluid, src, q)), dv_general(fluid, src, sigma, n, a, r))
        )

    expected_force, expected_jvp = jax.jvp(
        oracle, (jnp.asarray(state),), (jnp.asarray(direction),)
    )
    force, jvp = _native().rf03_matter_force_jvp(
        MODEL_ID, 1.27, state, direction, sigma, n, a, r, q, 1.0e4
    )

    np.testing.assert_allclose(force, expected_force, rtol=2e-13, atol=2e-14)
    np.testing.assert_allclose(jvp, expected_jvp, rtol=3e-12, atol=3e-13)


def test_force_and_jvp_randomized_parity_preserves_nonsymmetric_context_order() -> None:
    import jax
    import jax.numpy as jnp

    from bianchi.matter.fluid import TiltedFluid, dOmega, dv_general, sources

    rng = np.random.default_rng(20260828)
    native = _native()
    for _ in range(12):
        gamma = float(rng.uniform(0.08, 2.0))
        state = np.concatenate(([rng.uniform(0.02, 0.9)], rng.normal(scale=0.16, size=3)))
        direction = rng.normal(scale=0.09, size=4)
        sigma = rng.normal(scale=0.12, size=(3, 3))
        n = rng.normal(scale=0.15, size=(3, 3))
        a = rng.normal(scale=0.08, size=3)
        r = rng.normal(scale=0.07, size=3)
        q = float(rng.uniform(-0.3, 1.4))

        def oracle(x):
            fluid = TiltedFluid.of(gamma, x[0], x[1:])
            src = sources(fluid, sigma, a)
            return jnp.concatenate(
                (
                    jnp.atleast_1d(dOmega(fluid, src, q)),
                    dv_general(fluid, src, sigma, n, a, r),
                )
            )

        expected_force, expected_jvp = jax.jvp(
            oracle, (jnp.asarray(state),), (jnp.asarray(direction),)
        )
        observed_force, observed_jvp = native.rf03_matter_force_jvp(
            MODEL_ID,
            gamma,
            np.ascontiguousarray(state),
            np.ascontiguousarray(direction),
            np.ascontiguousarray(sigma),
            np.ascontiguousarray(n),
            np.ascontiguousarray(a),
            np.ascontiguousarray(r),
            q,
            3.0,
        )
        np.testing.assert_allclose(observed_force, expected_force, rtol=8e-13, atol=8e-14)
        np.testing.assert_allclose(observed_jvp, expected_jvp, rtol=8e-12, atol=8e-13)


def test_t_gamma_is_read_only_for_force_and_jvp() -> None:
    state = np.array([0.29, 0.08, 0.03, -0.05], dtype=np.float64)
    direction = np.array([-0.03, 0.04, 0.01, 0.02], dtype=np.float64)
    sigma, n, a, r, q = _context()
    native = _native()

    cold = native.rf03_matter_force_jvp(
        MODEL_ID, 1.4, state, direction, sigma, n, a, r, q, 1.0e-9
    )
    hot = native.rf03_matter_force_jvp(
        MODEL_ID, 1.4, state, direction, sigma, n, a, r, q, 1.0e12
    )

    assert np.array_equal(np.asarray(cold[0]), np.asarray(hot[0]))
    assert np.array_equal(np.asarray(cold[1]), np.asarray(hot[1]))


@pytest.mark.parametrize(
    ("model_id", "gamma", "state", "error_name"),
    [
        ("constant_w", 1.2, [0.3, 0.0, 0.0, 0.0], "RF03ModelError"),
        (None, 1.2, [0.3, 0.0, 0.0, 0.0], "RF03ModelError"),
        (MODEL_ID, 0.0, [0.3, 0.0, 0.0, 0.0], "RF03DomainError"),
        (MODEL_ID, 2.01, [0.3, 0.0, 0.0, 0.0], "RF03DomainError"),
        (MODEL_ID, 1.2, [-0.1, 0.0, 0.0, 0.0], "RF03DomainError"),
        (MODEL_ID, 1.2, [0.3, 1.0, 0.0, 0.0], "RF03DomainError"),
        (MODEL_ID, 1.2, [0.3, np.nan, 0.0, 0.0], "RF03DomainError"),
    ],
)
def test_model_and_physical_domain_fail_typed(model_id, gamma, state, error_name) -> None:
    sigma, n, a, r, q = _context()
    native = _native()
    error_type = getattr(native, error_name)

    with pytest.raises(error_type):
        native.rf03_matter_force(
            model_id, gamma, np.asarray(state, dtype=np.float64), sigma, n, a, r, q, None
        )


def test_model_selector_rejects_before_any_numeric_coercion() -> None:
    native = _native()

    class MustNotCoerce:
        def __float__(self):
            raise AssertionError("numeric coercion preceded model selection")

        def __array__(self, *_args, **_kwargs):
            raise AssertionError("array coercion preceded model selection")

    poison = MustNotCoerce()
    with pytest.raises(native.RF03ModelError):
        native.rf03_matter_force(
            "constant_w", poison, poison, poison, poison, poison, poison, poison, poison
        )

    from bianchi.matter import gamma_law_rust

    with pytest.raises(gamma_law_rust.RF03ModelSelectionError):
        gamma_law_rust.force(
            model_id="constant_w",
            gamma=poison,
            state=poison,
            Sigma=poison,
            N=poison,
            A=poison,
            R=poison,
            q=poison,
        )

    class MustNotCompare:
        def __eq__(self, _other):
            raise AssertionError("model equality preceded the string type check")

    with pytest.raises(gamma_law_rust.RF03ModelSelectionError):
        gamma_law_rust.force(
            model_id=MustNotCompare(),
            gamma=poison,
            state=poison,
            Sigma=poison,
            N=poison,
            A=poison,
            R=poison,
            q=poison,
        )


def test_zero_tilt_known_limit_and_invariants() -> None:
    native = _native()
    state = np.array([0.25, 0.0, 0.0, 0.0], dtype=np.float64)
    zero3 = np.zeros(3, dtype=np.float64)
    zero33 = np.zeros((3, 3), dtype=np.float64)
    q = 0.37
    gamma = 4.0 / 3.0

    force = np.asarray(
        native.rf03_matter_force(
            MODEL_ID, gamma, state, zero33, zero33, zero3, zero3, q, None
        )
    )
    expected_domega = state[0] * (2.0 * q - (3.0 * gamma - 2.0))
    np.testing.assert_array_equal(force[1:], np.zeros(3))
    assert force[0] == pytest.approx(expected_domega, rel=0.0, abs=2e-16)

    invariants = native.rf03_tilt_invariants(state[0], state[1:])
    assert invariants["u_norm_residual"] == pytest.approx(0.0, abs=2e-16)
    assert invariants["density_margin"] == state[0]
    assert invariants["tilt_margin"] == 1.0


def test_production_python_adapter_never_calls_source_oracle(monkeypatch) -> None:
    from bianchi.matter import fluid
    from bianchi.matter import gamma_law_rust

    def forbidden(*_args, **_kwargs):
        raise AssertionError("silent Python force fallback was reached")

    monkeypatch.setattr(fluid, "sources", forbidden)
    sigma, n, a, r, q = _context()
    observed = gamma_law_rust.force(
        model_id=MODEL_ID,
        gamma=1.3,
        state=np.array([0.3, 0.02, 0.01, -0.04]),
        Sigma=sigma,
        N=n,
        A=a,
        R=r,
        q=q,
        T_gamma=2.7,
        development_override=True,
    )
    assert np.isfinite(observed).all()


def test_fixed_context_integrator_cools_with_source_consistent_log_slope() -> None:
    native = _native()
    zero3 = np.zeros(3, dtype=np.float64)
    zero33 = np.zeros((3, 3), dtype=np.float64)
    result = native.rf03_matter_integrate(
        MODEL_ID,
        4.0 / 3.0,
        np.array([0.5, 0.0, 0.0, 0.0]),
        zero33,
        zero33,
        zero3,
        zero3,
        0.5,
        1.0,
        400,
        2.7,
    )
    times = np.asarray(result["times"])
    states = np.asarray(result["states"])
    slope = np.polyfit(times, np.log(states[:, 0]), 1)[0]

    assert result["status"] == "COMPLETE"
    assert result["state_order"] == ("Omega", "v1", "v2", "v3")
    assert slope == pytest.approx(-1.0, abs=2e-10)
    np.testing.assert_allclose(states[:, 1:], 0.0, rtol=0.0, atol=0.0)


def test_integrator_reports_typed_physical_domain_terminal() -> None:
    native = _native()
    zero3 = np.zeros(3, dtype=np.float64)
    zero33 = np.zeros((3, 3), dtype=np.float64)
    result = native.rf03_matter_integrate(
        MODEL_ID,
        2.0,
        np.array([0.2, 0.9, 0.0, 0.0]),
        zero33,
        zero33,
        zero3,
        zero3,
        0.0,
        1.0,
        20,
        None,
    )
    states = np.asarray(result["states"])

    assert result["status"] == "RF03_DOMAIN_TERMINATION"
    assert "tilt" in result["terminal_detail"]
    assert np.isfinite(states).all()
    assert np.all(np.sum(states[:, 1:] ** 2, axis=1) < 1.0)


def _class_a_context_history(states: np.ndarray, gamma: float):
    sp, sm, n1, n2, n3 = states.T
    sigma = np.zeros((len(states), 3, 3), dtype=np.float64)
    sigma[:, 0, 0] = -2.0 * sp
    sigma[:, 1, 1] = sp + np.sqrt(3.0) * sm
    sigma[:, 2, 2] = sp - np.sqrt(3.0) * sm
    n = np.zeros_like(sigma)
    n[:, 0, 0], n[:, 1, 1], n[:, 2, 2] = n1, n2, n3
    zeros = np.zeros((len(states), 3), dtype=np.float64)
    sigma2 = sp * sp + sm * sm
    curvature = (
        n1 * n1
        + n2 * n2
        + n3 * n3
        - 2.0 * (n1 * n2 + n2 * n3 + n3 * n1)
    ) / 12.0
    omega = 1.0 - sigma2 - curvature
    q = 2.0 * sigma2 + 0.5 * (3.0 * gamma - 2.0) * omega
    return sigma, n, zeros, zeros.copy(), q, omega


def test_rf02c_background_history_composes_with_native_matter_without_callback() -> None:
    native = _native()
    gamma = 1.3
    times = np.linspace(0.0, 0.2, 201, dtype=np.float64)
    background, ok = native.integrate_background(
        "class_a",
        np.array([0.05, -0.03, 0.1, 0.08, 0.06], dtype=np.float64),
        times,
        gamma,
        0.0,
        1.0e-10,
        1.0e-12,
    )
    background = np.asarray(background)
    sigma, n, a, r, q, omega = _class_a_context_history(background, gamma)
    initial = np.array([omega[0], 0.0, 0.0, 0.0], dtype=np.float64)

    cold = native.rf03_matter_integrate_history(
        MODEL_ID, gamma, initial, times, sigma, n, a, r, q, np.full(len(times), 1.0e-9)
    )
    hot = native.rf03_matter_integrate_history(
        MODEL_ID, gamma, initial, times, sigma, n, a, r, q, np.full(len(times), 1.0e9)
    )
    matter = np.asarray(cold["states"])

    assert ok
    assert cold["status"] == "COMPLETE"
    assert native.rf02c_execution_identity() == native.qg_geometry_identity()
    assert np.array_equal(matter, np.asarray(hot["states"]))
    assert np.max(np.abs(matter[:, 0] - omega)) <= 2.0e-8
    np.testing.assert_array_equal(matter[:, 1:], np.zeros((len(times), 3)))


def test_one_thread_and_four_thread_states_failure_codes_and_order_are_identical() -> None:
    code = r'''
import json
import numpy as np
import bianchi_rustcore as native
z3=np.zeros(3, dtype=np.float64); z33=np.zeros((3,3), dtype=np.float64)
model="explicit_gamma_law_tilted_perfect_fluid_v1"
def run(state, gamma, q, t_end, nsteps):
    result=native.rf03_matter_integrate(
        model,gamma,np.array(state,dtype=np.float64),z33,z33,z3,z3,q,t_end,nsteps,None)
    states=np.asarray(result["states"], dtype=np.float64)
    return {
        "status":result["status"],
        "terminal_index":result["terminal_index"],
        "terminal_detail":result["terminal_detail"],
        "shape":list(states.shape),
        "hex":states.tobytes().hex(),
    }
print(json.dumps({
    "pool":native.rayon_thread_pool_size(),
    "complete":run([0.3,0.1,-0.04,0.02],1.4,0.35,0.4,160),
    "domain":run([0.2,0.9,0.0,0.0],2.0,0.0,1.0,20),
}, sort_keys=True))
'''

    def run(threads: int):
        env = os.environ.copy()
        env["RAYON_NUM_THREADS"] = str(threads)
        completed = subprocess.run(
            [sys.executable, "-c", code],
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        return json.loads(completed.stdout)

    one = run(1)
    four = run(4)
    assert one["pool"] == 1
    assert four["pool"] == 4
    assert one["complete"] == four["complete"]
    assert one["domain"] == four["domain"]
    assert one["complete"]["status"] == "COMPLETE"
    assert one["domain"]["status"] == "RF03_DOMAIN_TERMINATION"
    assert one["domain"]["terminal_detail"] is not None


def test_rf03_tilt_adapters_are_owned_outside_root_lib() -> None:
    root = Path(__file__).resolve().parents[2]
    root_lib = (root / "_rustcore/src/lib.rs").read_text(encoding="utf-8")
    tilt_adapter = (root / "_rustcore/src/python/rf03_tilt.rs").read_text(
        encoding="utf-8"
    )
    for symbol in ("th_integrate", "th_rhs", "th_force_and_matrix"):
        assert f"fn {symbol}" not in root_lib
        assert f"fn {symbol}" in tilt_adapter


def test_rf03_freeze_inventories_inherited_closure_and_thermo_scope() -> None:
    root = Path(__file__).resolve().parents[2]
    freeze = json.loads(
        (root / "artifacts/rust_first_runtime/rf03/SCHEMA_AND_ROUTE_FREEZE.json").read_text(
            encoding="utf-8"
        )
    )
    assert freeze["inherited_tilt_closure"]["modes"] == [
        "frozen",
        "ratio",
        "ratio_scalar",
        "zero",
        "phys_sqrt",
        "phys_5w",
        "phys_interp",
    ]
    assert freeze["inherited_tilt_closure"]["native_symbols"] == [
        "th_integrate",
        "th_rhs",
        "th_force_and_matrix",
    ]
    assert freeze["inherited_thermodynamics"]["new_tilted_temperature_formula"] == "NONE"
    assert freeze["inherited_thermodynamics"]["native_sources"] == [
        "_rustcore/src/thermo/dof.rs",
        "_rustcore/src/thermo/dof_table.rs",
        "_rustcore/src/thermo/fd.rs",
    ]
