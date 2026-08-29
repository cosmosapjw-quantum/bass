"""Independent formula-level checks for G-POL-LIOUVILLE-II-A.

This file deliberately does not import the Rust implementation.  It checks the
screen-tensor transport identities using an independent NumPy route.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np


def cross_matrix(vector: np.ndarray) -> np.ndarray:
    x, y, z = vector
    return np.array([[0.0, -z, y], [z, 0.0, -x], [-y, x, 0.0]])


def coefficients(
    e: np.ndarray,
    expansion: float,
    sigma: np.ndarray,
    n_tensor: np.ndarray,
    a_vector: np.ndarray,
    omega_triad: np.ndarray,
):
    e = e / np.linalg.norm(e)
    sigma_e = sigma @ e
    sigma_ee = float(e @ sigma_e)
    v_shear = -sigma_e + sigma_ee * e
    w = (
        omega_triad
        + np.cross(a_vector, e)
        + n_tensor @ e
        - 0.5 * np.trace(n_tensor) * e
    )
    angular_velocity = w + np.cross(e, v_shear)
    direction_rate = np.cross(angular_velocity, e)
    log_energy_rate = -(expansion + sigma_ee)
    return direction_rate, log_energy_rate, angular_velocity, float(e @ w)


def screen_state(e: np.ndarray, seed: np.ndarray) -> np.ndarray:
    e = e / np.linalg.norm(e)
    projector = np.eye(3) - np.outer(e, e)
    matrix = projector @ seed @ projector
    return matrix


def test_direction_flow_and_screen_generator_identities() -> None:
    rng = np.random.default_rng(0xB455)
    for _ in range(256):
        e = rng.normal(size=3)
        e /= np.linalg.norm(e)
        raw_sigma = rng.normal(size=(3, 3))
        sigma = 0.5 * (raw_sigma + raw_sigma.T)
        sigma -= np.trace(sigma) * np.eye(3) / 3.0
        raw_n = rng.normal(size=(3, 3))
        n_tensor = 0.5 * (raw_n + raw_n.T)
        a_vector = rng.normal(size=3)
        omega_triad = rng.normal(size=3)
        direction_rate, _, angular_velocity, _ = coefficients(
            e, 0.7, sigma, n_tensor, a_vector, omega_triad
        )
        sigma_e = sigma @ e
        sigma_ee = float(e @ sigma_e)
        expected = (
            -sigma_e
            + sigma_ee * e
            - a_vector
            + float(a_vector @ e) * e
            + np.cross(n_tensor @ e, e)
            + np.cross(omega_triad, e)
        )
        np.testing.assert_allclose(direction_rate, expected, rtol=0.0, atol=3e-14)
        np.testing.assert_allclose(
            cross_matrix(angular_velocity) @ e,
            expected,
            rtol=0.0,
            atol=3e-14,
        )
        assert abs(float(e @ direction_rate)) < 3e-14


def test_screen_constraint_and_trace_are_preserved_by_rotation_part() -> None:
    rng = np.random.default_rng(0xC0FFEE)
    for _ in range(128):
        e = rng.normal(size=3)
        e /= np.linalg.norm(e)
        seed = rng.normal(size=(3, 3))
        coherency = screen_state(e, seed)
        raw_sigma = rng.normal(size=(3, 3))
        sigma = 0.5 * (raw_sigma + raw_sigma.T)
        sigma -= np.trace(sigma) * np.eye(3) / 3.0
        raw_n = rng.normal(size=(3, 3))
        n_tensor = 0.5 * (raw_n + raw_n.T)
        direction_rate, redshift, angular_velocity, _ = coefficients(
            e,
            0.8,
            sigma,
            n_tensor,
            rng.normal(size=3),
            rng.normal(size=3),
        )
        generator = cross_matrix(angular_velocity)
        rotation_rhs = generator @ coherency + coherency @ generator.T
        total_rhs = rotation_rhs + 4.0 * redshift * coherency
        np.testing.assert_allclose(
            direction_rate @ coherency + e @ total_rhs,
            np.zeros(3),
            rtol=0.0,
            atol=8e-14,
        )
        assert abs(float(np.trace(rotation_rhs))) < 8e-14


def test_omitting_screen_twist_is_detected_when_direction_is_fixed() -> None:
    e = np.array([0.0, 0.0, 1.0])
    omega = 0.7
    coherency = np.diag([1.0, 0.0, 0.0])
    direction_rate, _, angular_velocity, screen_rate = coefficients(
        e,
        0.0,
        np.zeros((3, 3)),
        np.zeros((3, 3)),
        np.zeros(3),
        np.array([0.0, 0.0, omega]),
    )
    np.testing.assert_allclose(direction_rate, np.zeros(3), atol=0.0, rtol=0.0)
    assert screen_rate == omega
    generator = cross_matrix(angular_velocity)
    full_rhs = generator @ coherency + coherency @ generator.T
    omitted_rhs = np.zeros((3, 3))
    assert np.linalg.norm(full_rhs - omitted_rhs) > 0.9


def test_typeii_adapter_formula() -> None:
    sigma_p, sigma_m, sigma_13, n1 = 0.21, -0.04, 0.07, 0.83
    sqrt3 = np.sqrt(3.0)
    sigma = np.array(
        [
            [-2.0 * sigma_p, 0.0, sqrt3 * sigma_13],
            [0.0, sigma_p + sqrt3 * sigma_m, 0.0],
            [sqrt3 * sigma_13, 0.0, sigma_p - sqrt3 * sigma_m],
        ]
    )
    n_tensor = np.diag([n1, 0.0, 0.0])
    omega_triad = np.array([0.0, sqrt3 * sigma_13, 0.0])
    e = np.array([0.31, -0.52, 0.79])
    e /= np.linalg.norm(e)
    _, redshift, _, screen_rate = coefficients(
        e, 1.0, sigma, n_tensor, np.zeros(3), omega_triad
    )
    expected_screen = sqrt3 * sigma_13 * e[1] + n1 * e[0] ** 2 - 0.5 * n1
    expected_redshift = -(1.0 + float(e @ sigma @ e))
    assert abs(screen_rate - expected_screen) < 2e-15
    assert abs(redshift - expected_redshift) < 2e-15


def test_independent_coordinate_bianchi_ii_oracle() -> None:
    from compiler.validation.typeii_polarized_liouville_coordinate_oracle import compute_receipt

    receipt = compute_receipt()
    errors = receipt["cross_errors"]
    assert errors["direction_max_abs"] < 3e-12
    assert errors["log_energy_abs"] < 3e-13
    assert errors["spatial_transport_max_abs"] < 3e-12
    coordinate = receipt["coordinate"]
    assert abs(coordinate["coordinate_final_time"] - 1.25) < 3e-13
    assert abs(coordinate["null_residual"]) < 2e-11
    assert coordinate["orthogonality_defect"] < 3e-12
    assert coordinate["determinant_defect"] < 3e-12


def test_propagation_direction_and_boost_dipole_sign_anchor() -> None:
    from compiler.validation.typeii_polarized_liouville_coordinate_oracle import (
        observer_energy_factor,
    )

    # e is future-directed photon propagation, not the observer's sky line of
    # sight.  A +x observer chases a +x photon and measures the smaller energy.
    speed = 0.1
    velocity = np.array([speed, 0.0, 0.0])
    forward = observer_energy_factor(np.array([1.0, 0.0, 0.0]), velocity)
    backward = observer_energy_factor(np.array([-1.0, 0.0, 0.0]), velocity)
    assert forward < backward
    bolometric_ratio = forward**-4 / backward**-4
    expected_ratio = ((1.0 + speed) / (1.0 - speed)) ** 4
    assert abs(bolometric_ratio - expected_ratio) < 3e-15


def test_coordinate_oracle_preserves_oriented_basis_free_screen() -> None:
    from compiler.validation.typeii_polarized_liouville_coordinate_oracle import (
        E0,
        compute_receipt,
        tangent_frame,
    )

    coordinate = compute_receipt()["coordinate"]
    final_direction = np.asarray(coordinate["direction"])
    rotation = np.asarray(coordinate["spatial_transport"])
    first, second = tangent_frame(E0)
    final_first = rotation @ first
    final_second = rotation @ second
    np.testing.assert_allclose(rotation @ E0, final_direction, rtol=0.0, atol=3e-12)
    handedness = float(np.dot(np.cross(final_first, final_second), final_direction))
    assert handedness > 1.0 - 4e-12


def test_rust_coordinate_golden_is_numerically_bound_to_generator() -> None:
    from compiler.validation.typeii_polarized_liouville_coordinate_oracle import (
        RUST_GOLDEN_TOLERANCES,
        compute_receipt,
        rust_golden_errors,
    )

    root = Path(__file__).resolve().parents[2]
    rust_source = (
        root / "runtime/rust/typeii/tests/typeii_polarized_liouville_unit.rs"
    ).read_text()
    errors = rust_golden_errors(compute_receipt(), rust_source)
    for name, error in errors.items():
        assert error <= RUST_GOLDEN_TOLERANCES[name], f"{name}={error}"


def test_rust_golden_parser_ignores_commented_declarations() -> None:
    from compiler.validation.typeii_polarized_liouville_coordinate_oracle import (
        compute_receipt,
        format_rust_golden,
        rust_golden_errors,
    )

    receipt = compute_receipt()
    golden = format_rust_golden(receipt)
    commented_correct = "\n".join(f"// {line}" for line in golden.splitlines())
    block_commented_correct = f"/*\n{golden}\n*/"
    string_embedded_correct = f'const DECOY: &str = r#"\n{golden}\n"#;'
    live_wrong = """
const COORDINATE_ORACLE_DIRECTION: [f64; 3] = [0.0, 0.0, 0.0];
const COORDINATE_ORACLE_LOG_ENERGY_SHIFT: f64 = 0.0;
const COORDINATE_ORACLE_SPATIAL_TRANSPORT: [[f64; 3]; 3] =
    [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]];
"""
    decoys = "\n".join(
        (commented_correct, block_commented_correct, string_embedded_correct)
    )
    errors = rust_golden_errors(receipt, decoys + live_wrong)
    assert errors["direction_max_abs"] > 0.4
    assert errors["log_energy_abs"] > 0.08
    assert errors["spatial_transport_max_abs"] > 0.9

    try:
        rust_golden_errors(receipt, live_wrong + live_wrong)
    except ValueError as error:
        assert "duplicate Rust coordinate-oracle constant" in str(error)
    else:
        raise AssertionError("duplicate live Rust golden declarations were accepted")


def _levi_civita() -> np.ndarray:
    eps = np.zeros((3, 3, 3))
    for i in range(3):
        for j in range(3):
            for k in range(3):
                eps[i, j, k] = (i - j) * (j - k) * (k - i) / 2.0
    return eps


def _rotation_coefficients_direct(
    expansion: float,
    sigma: np.ndarray,
    triad_rotation: np.ndarray,
    n_tensor: np.ndarray,
    a_vector: np.ndarray,
) -> np.ndarray:
    """Construct Gamma^a_bc from commutators, independently of `coefficients`."""
    eps = _levi_civita()
    commutator = np.zeros((4, 4, 4))
    deformation = expansion * np.eye(3) + sigma + np.einsum(
        "abc,c->ab", eps, triad_rotation
    )
    for a in range(3):
        for b in range(3):
            commutator[1 + b, 0, 1 + a] = -deformation[a, b]
            commutator[1 + b, 1 + a, 0] = deformation[a, b]
    for c in range(3):
        for i in range(3):
            for j in range(3):
                value = sum(eps[i, j, d] * n_tensor[d, c] for d in range(3))
                if c == j:
                    value += a_vector[i]
                if c == i:
                    value -= a_vector[j]
                commutator[1 + c, 1 + i, 1 + j] = value
    eta = np.diag([-1.0, 1.0, 1.0, 1.0])
    lowered = np.einsum("ad,dbc->abc", eta, commutator)
    gamma_lowered = 0.5 * (
        -lowered
        - np.einsum("bca->abc", lowered)
        + np.einsum("cab->abc", lowered)
    )
    np.testing.assert_allclose(
        gamma_lowered + np.einsum("bac->abc", gamma_lowered),
        np.zeros_like(gamma_lowered),
        rtol=0.0,
        atol=3e-14,
    )
    return np.einsum("ad,dbc->abc", eta, gamma_lowered)


def test_closed_generator_matches_direct_ricci_rotation_coefficients() -> None:
    rng = np.random.default_rng(0xB1A2C3)
    for _ in range(128):
        e = rng.normal(size=3)
        e /= np.linalg.norm(e)
        seed = rng.normal(size=3)
        screen = seed - float(seed @ e) * e
        screen /= np.linalg.norm(screen)
        raw_sigma = rng.normal(size=(3, 3))
        sigma = 0.5 * (raw_sigma + raw_sigma.T)
        sigma -= np.trace(sigma) * np.eye(3) / 3.0
        raw_n = rng.normal(size=(3, 3))
        n_tensor = 0.5 * (raw_n + raw_n.T)
        a_vector = rng.normal(size=3)
        triad_rotation = rng.normal(size=3)
        expansion = float(rng.normal())

        closed_direction, closed_redshift, angular_velocity, _ = coefficients(
            e, expansion, sigma, n_tensor, a_vector, triad_rotation
        )
        gamma = _rotation_coefficients_direct(
            expansion, sigma, triad_rotation, n_tensor, a_vector
        )
        momentum = np.concatenate([[1.0], e])
        momentum_rate = -np.einsum("abc,b,c->a", gamma, momentum, momentum)
        direct_redshift = float(momentum_rate[0])
        direct_direction = momentum_rate[1:] - direct_redshift * e

        four_screen = np.concatenate([[0.0], screen])
        transported = -np.einsum("abc,b,c->a", gamma, four_screen, momentum)
        direct_screen = transported[1:] - transported[0] * e
        closed_screen = np.cross(angular_velocity, screen)

        np.testing.assert_allclose(
            closed_direction, direct_direction, rtol=0.0, atol=7e-14
        )
        assert abs(closed_redshift - direct_redshift) < 7e-14
        np.testing.assert_allclose(
            closed_screen, direct_screen, rtol=0.0, atol=7e-14
        )
