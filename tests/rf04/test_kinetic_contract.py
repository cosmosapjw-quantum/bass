"""RF-04 public/native kinetic contract.

The production fixture is deliberately non-degenerate Type II and uses an
angular rule that resolves the complete ``l=2`` subspace.  The six-axis rule is
retained only as a negative control; it must never drive a physics claim.

The Python layer is API/configuration only.  Trajectory and batch calls remain
owned by the three frozen native RF-04 symbols.
"""
from __future__ import annotations

import importlib
import json
from types import SimpleNamespace

import numpy as np


SCHEMA_ID = "bass-rf04-typeii-public-route/v1"
SCHEMA_SHA256 = "be2c73e07e5a8179c10ec4aab058915b79b1d7ab87fc624d65e5e0d34d94d097"
SCI_AUTH_HEAD = "1298c2ef8cc8eaca8edcd99332653c8a1cbc1c86"
SCI_AUTH_TREE = "37edaaea720a3197881b94bc39413787db091432"
SCI_AUTH_MANIFEST_SHA256 = (
    "9c646d7fa43463484e832349f0a4ae9c3728dc1d68a2370504facdc41aad9b9f"
)
ROUTES = {
    "kinetic.typeii.execution_identity_v1": ("rf04_typeii_execution_identity_v1",),
    "kinetic.typeii.trajectory_v1": (
        "rf04_typeii_trajectory_v1",
        "rf04_typeii_execution_identity_v1",
    ),
    "kinetic.typeii.batch_v1": (
        "rf04_typeii_batch_v1",
        "rf04_typeii_execution_identity_v1",
    ),
}
EXCEPTIONS = {
    "RF04InputError",
    "RF04CapabilityError",
    "RF04PhysicalDomainError",
    "RF04CertificateError",
    "RF04MemberError",
}


def _native():
    return importlib.import_module("bianchi_rustcore")


def _angular_grid() -> tuple[np.ndarray, np.ndarray]:
    """Return the established 26-node Lebedev rule used by Type-II audits."""

    pi = np.pi
    a = 1.0 / np.sqrt(3.0)
    b = 1.0 / np.sqrt(2.0)
    directions: list[list[float]] = []
    weights: list[float] = []
    for axis in range(3):
        for sign in (-1.0, 1.0):
            direction = np.zeros(3)
            direction[axis] = sign
            directions.append(direction.tolist())
            weights.append(4.0 * pi / 21.0)
    for zero_axis in range(3):
        live_axes = [axis for axis in range(3) if axis != zero_axis]
        for sign0 in (-1.0, 1.0):
            for sign1 in (-1.0, 1.0):
                direction = np.zeros(3)
                direction[live_axes[0]] = sign0 * b
                direction[live_axes[1]] = sign1 * b
                directions.append(direction.tolist())
                weights.append(16.0 * pi / 105.0)
    for sign0 in (-1.0, 1.0):
        for sign1 in (-1.0, 1.0):
            for sign2 in (-1.0, 1.0):
                directions.append([sign0 * a, sign1 * a, sign2 * a])
                weights.append(9.0 * pi / 70.0)
    return (
        np.ascontiguousarray(directions, dtype=np.float64),
        np.ascontiguousarray(weights, dtype=np.float64),
    )


def _six_axis_negative_control_grid() -> tuple[np.ndarray, np.ndarray]:
    directions = np.asarray(
        [
            [1.0, 0.0, 0.0],
            [-1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, -1.0, 0.0],
            [0.0, 0.0, 1.0],
            [0.0, 0.0, -1.0],
        ],
        dtype=np.float64,
    )
    weights = np.full(6, 4.0 * np.pi / 6.0, dtype=np.float64)
    return directions, weights


def _l2_design(directions: np.ndarray) -> np.ndarray:
    x, y, z = directions.T
    return np.column_stack(
        (x * x - y * y, 2.0 * z * z - x * x - y * y, x * y, x * z, y * z)
    )


def _fourth_moment(directions: np.ndarray, weights: np.ndarray) -> np.ndarray:
    return np.einsum(
        "n,ni,nj,nk,nl->ijkl",
        weights,
        directions,
        directions,
        directions,
        directions,
    )


def _isotropic_fourth_moment() -> np.ndarray:
    delta = np.eye(3)
    return (4.0 * np.pi / 15.0) * (
        np.einsum("ij,kl->ijkl", delta, delta)
        + np.einsum("ik,jl->ijkl", delta, delta)
        + np.einsum("il,jk->ijkl", delta, delta)
    )


def _background(v: float = 0.08, steps: int = 2) -> tuple[np.ndarray, ...]:
    """Non-degenerate, stage-varying aligned Type-II background samples."""

    index = np.arange(steps, dtype=np.float64)
    q1 = np.column_stack(
        (
            0.25 + 0.004 * index,
            0.05 - 0.003 * index,
            1.0 / 30.0 + 0.002 * index,
            0.80 - 0.010 * index,
            v + 0.006 * index,
        )
    )
    mid = q1 + np.asarray([0.003, -0.002, 0.0015, -0.006, 0.0025])
    q3 = q1 + np.asarray([0.007, -0.004, 0.0035, -0.013, 0.0055])
    opacity = 0.18 + 0.015 * index
    step_size = 8.0e-4 + 1.0e-4 * index
    return tuple(
        np.ascontiguousarray(value, dtype=np.float64)
        for value in (q1, mid, q3, opacity, step_size)
    )


def _route_arguments(initial: np.ndarray, *, v: float = 0.08) -> tuple[object, ...]:
    directions, weights = _angular_grid()
    q1, mid, q3, opacity, step_size = _background(v)
    return (
        np.ascontiguousarray(initial, dtype=np.float64),
        directions,
        weights,
        q1,
        mid,
        q3,
        opacity,
        step_size,
        1.3,
        1.0,
        1,
    )


def _trajectory(
    initial: np.ndarray,
    *,
    carrier: str = "scalar_intensity_v1",
    quadrature_route: str = "paired_rest_to_normal_reference_v1",
    v: float = 0.08,
):
    return _native().rf04_typeii_trajectory_v1(
        *_route_arguments(initial, v=v),
        carrier,
        quadrature_route,
    )


def _tangent_frame(direction: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    seed = np.zeros(3)
    seed[int(np.argmin(np.abs(direction)))] = 1.0
    u = seed - np.dot(seed, direction) * direction
    u /= np.linalg.norm(u)
    return u, np.cross(direction, u)


def _pack9(matrix: np.ndarray) -> np.ndarray:
    return np.asarray(
        [
            matrix[0, 0],
            matrix[1, 1],
            matrix[2, 2],
            0.5 * (matrix[0, 1] + matrix[1, 0]),
            0.5 * (matrix[0, 2] + matrix[2, 0]),
            0.5 * (matrix[1, 2] + matrix[2, 1]),
            0.5 * (matrix[1, 2] - matrix[2, 1]),
            0.5 * (matrix[2, 0] - matrix[0, 2]),
            0.5 * (matrix[0, 1] - matrix[1, 0]),
        ],
        dtype=np.float64,
    )


def _unpack9(packed: np.ndarray) -> np.ndarray:
    return np.asarray(
        [
            [packed[0], packed[3] + packed[8], packed[4] - packed[7]],
            [packed[3] - packed[8], packed[1], packed[5] + packed[6]],
            [packed[4] + packed[7], packed[5] - packed[6], packed[2]],
        ],
        dtype=np.float64,
    )


def _physical_polarized_state(directions: np.ndarray) -> np.ndarray:
    """A transverse, realizable state with non-zero Q, U, and V."""

    rows: list[np.ndarray] = []
    for direction in directions:
        u, v = _tangent_frame(direction)
        intensity = 1.0 + 0.12 * direction[0] - 0.07 * direction[1] * direction[2]
        stokes_q = 0.18 * intensity * (direction[0] ** 2 - direction[1] ** 2)
        stokes_u = 0.12 * intensity * (2.0 * direction[0] * direction[1])
        stokes_v = 0.08 * intensity * direction[2]
        matrix = (
            0.5 * intensity * (np.outer(u, u) + np.outer(v, v))
            + 0.5 * stokes_q * (np.outer(u, u) - np.outer(v, v))
            + 0.5 * stokes_u * (np.outer(u, v) + np.outer(v, u))
            - 0.5 * stokes_v * (np.outer(u, v) - np.outer(v, u))
        )
        rows.append(_pack9(matrix))
    return np.ascontiguousarray(np.concatenate(rows), dtype=np.float64)


def _polarized_metrics(
    directions: np.ndarray, state: np.ndarray
) -> tuple[float, float]:
    minimum_eigenvalue = np.inf
    maximum_screen_leakage = 0.0
    for direction, packed in zip(directions, state.reshape(-1, 9), strict=True):
        matrix = _unpack9(packed)
        projector = np.eye(3) - np.outer(direction, direction)
        projected = projector @ matrix @ projector
        maximum_screen_leakage = max(
            maximum_screen_leakage,
            float(np.max(np.abs(_pack9(matrix) - _pack9(projected)))),
        )
        u, v = _tangent_frame(direction)
        a = float(u @ projected @ u)
        d = float(v @ projected @ v)
        uv = float(u @ projected @ v)
        vu = float(v @ projected @ u)
        symmetric = 0.5 * (uv + vu)
        antisymmetric = 0.5 * (uv - vu)
        discriminant = np.sqrt(
            (a - d) ** 2 + 4.0 * (symmetric**2 + antisymmetric**2)
        )
        minimum_eigenvalue = min(minimum_eigenvalue, 0.5 * (a + d - discriminant))
    return float(minimum_eigenvalue), maximum_screen_leakage


def _anisotropic_scalar_state(directions: np.ndarray) -> np.ndarray:
    x, y, z = directions.T
    return np.ascontiguousarray(
        1.0
        + 0.18 * x * y
        - 0.13 * y * z
        + 0.09 * x * z
        + 0.05 * (x * x - y * y),
        dtype=np.float64,
    )


def test_rf04_physics_grid_resolves_l2_and_fourth_moments() -> None:
    directions, weights = _angular_grid()
    np.testing.assert_allclose(np.linalg.norm(directions, axis=1), 1.0, atol=3.0e-16)
    assert np.linalg.matrix_rank(_l2_design(directions), tol=1.0e-13) == 5
    np.testing.assert_allclose(
        _fourth_moment(directions, weights),
        _isotropic_fourth_moment(),
        atol=4.0e-15,
        rtol=0.0,
    )


def test_six_axis_rule_is_explicitly_only_a_negative_control() -> None:
    directions, weights = _six_axis_negative_control_grid()
    assert np.linalg.matrix_rank(_l2_design(directions), tol=1.0e-13) == 2
    error = np.max(
        np.abs(_fourth_moment(directions, weights) - _isotropic_fourth_moment())
    )
    assert error > 1.0


def test_rf04_background_fixture_is_non_degenerate_and_stage_varying() -> None:
    q1, mid, q3, _, _ = _background(steps=3)
    assert np.all(np.abs(q1[:, :4]) > 0.0)
    assert np.all(np.abs(q1[:, 4]) > 0.0)
    assert np.unique(q1, axis=0).shape[0] == 3
    assert not np.array_equal(q1, mid)
    assert not np.array_equal(mid, q3)
    assert not np.array_equal(q1, q3)


def test_rf04_frozen_native_symbols_and_typed_exceptions_exist() -> None:
    native = _native()
    assert {symbol for symbols in ROUTES.values() for symbol in symbols} <= set(dir(native))
    assert EXCEPTIONS <= set(dir(native))


def test_rf04_execution_identity_is_canonical_and_authority_bound() -> None:
    raw = _native().rf04_typeii_execution_identity_v1()
    assert isinstance(raw, str)
    assert raw == json.dumps(json.loads(raw), sort_keys=True, separators=(",", ":"))
    identity = json.loads(raw)
    assert identity["identity_schema"] == "bass-rf04-typeii-execution-identity/v1"
    assert identity["public_route_schema_sha256"] == SCHEMA_SHA256
    assert identity["sci_auth_head"] == SCI_AUTH_HEAD
    assert identity["sci_auth_tree"] == SCI_AUTH_TREE
    assert identity["sci_auth_manifest_sha256"] == SCI_AUTH_MANIFEST_SHA256
    assert identity["certificate_scope"] == "PROJECTED_RESIDUAL_ONLY_NOT_GLOBAL_FORWARD_ERROR"
    assert set(identity["carrier_capabilities"]) == {
        "scalar_intensity_v1",
        "polarized_rank9_v1",
    }
    assert set(identity["quadrature_capabilities"]) == {
        "paired_rest_to_normal_reference_v1",
        "fixed_grid_raw_v1",
        "fixed_grid_ap_corrected_v1",
    }


def test_rf04_backend_routes_are_native_only_and_exact() -> None:
    from bianchi import backend_policy

    for route_id, symbols in ROUTES.items():
        capability = backend_policy.ROUTE_CAPABILITIES[route_id]
        assert capability.required_symbols == symbols
        assert capability.python_oracle_supported is False
        record = backend_policy.PUBLIC_ROUTE_INVENTORY[route_id]
        assert record.supported_state.value == "native_required"
        assert record.explicit_oracle_state.value == "unsupported"
        assert record.outside_native_domain_state.value == "unsupported"


def test_rf04_public_python_routes_call_the_exact_native_boundary(monkeypatch) -> None:
    """Catch a wrapper that computes, falls back, or calls a legacy native symbol."""

    from bianchi import kinetic

    selections: list[str] = []
    native_calls: list[tuple[str, tuple[object, ...]]] = []
    identity_result = "identity-sentinel"
    trajectory_result = object()
    batch_result = object()

    class FakeNative:
        def rf04_typeii_execution_identity_v1(self):
            native_calls.append(("rf04_typeii_execution_identity_v1", ()))
            return identity_result

        def rf04_typeii_trajectory_v1(self, *arguments):
            native_calls.append(("rf04_typeii_trajectory_v1", arguments))
            return trajectory_result

        def rf04_typeii_batch_v1(self, *arguments):
            native_calls.append(("rf04_typeii_batch_v1", arguments))
            return batch_result

        def __getattr__(self, name: str):
            raise AssertionError(f"public RF-04 wrapper requested forbidden symbol {name!r}")

    native = FakeNative()

    def select_backend(route_id: str, *args, **kwargs):
        del args, kwargs
        selections.append(route_id)
        return SimpleNamespace(native_module=native)

    monkeypatch.setattr(kinetic, "select_backend", select_backend)
    directions, _ = _angular_grid()
    scalar = _anisotropic_scalar_state(directions)
    trajectory_arguments = _route_arguments(scalar)
    batch_arguments = _route_arguments(np.stack((scalar, scalar[::-1])))

    assert kinetic.typeii_execution_identity_v1() == identity_result
    assert (
        kinetic.typeii_trajectory_v1(
            *trajectory_arguments,
            "scalar_intensity_v1",
            "paired_rest_to_normal_reference_v1",
        )
        is trajectory_result
    )
    assert (
        kinetic.typeii_batch_v1(
            *batch_arguments,
            "scalar_intensity_v1",
            "paired_rest_to_normal_reference_v1",
        )
        is batch_result
    )
    assert selections == list(ROUTES)
    assert [name for name, _ in native_calls] == [
        "rf04_typeii_execution_identity_v1",
        "rf04_typeii_trajectory_v1",
        "rf04_typeii_batch_v1",
    ]
    trajectory_call = native_calls[1][1]
    batch_call = native_calls[2][1]
    assert len(trajectory_call) == len(trajectory_arguments) + 2
    assert len(batch_call) == len(batch_arguments) + 2
    assert all(
        observed is expected
        for observed, expected in zip(
            trajectory_call[:-2], trajectory_arguments, strict=True
        )
    )
    assert all(
        observed is expected
        for observed, expected in zip(batch_call[:-2], batch_arguments, strict=True)
    )
    assert trajectory_call[-2:] == (
        "scalar_intensity_v1",
        "paired_rest_to_normal_reference_v1",
    )
    assert batch_call[-2:] == (
        "scalar_intensity_v1",
        "paired_rest_to_normal_reference_v1",
    )


def test_rf04_scalar_trajectory_has_exact_schema_and_observable_invariants() -> None:
    directions, _ = _angular_grid()
    initial = _anisotropic_scalar_state(directions)
    result = _trajectory(initial)
    assert result["schema_id"] == SCHEMA_ID
    assert result["route_id"] == "kinetic.typeii.trajectory_v1"
    history = np.asarray(result["radiation_history"])
    assert history.shape == (3, len(directions))
    np.testing.assert_array_equal(history[0], initial)
    assert not np.array_equal(history[-1], history[0])
    assert np.all(np.isfinite(history))
    assert np.all(np.min(history, axis=1) >= 0.0)
    diagnostics = result["diagnostics"]
    for name in (
        "equilibrium_null_residual",
        "left_invariant_drift",
        "projected_residual_estimate",
        "projector_idempotence_residual",
        "right_kernel_residual",
    ):
        values = np.asarray(diagnostics[name])
        assert values.shape == (2,)
        assert np.all(np.isfinite(values))
    positivity = np.asarray(diagnostics["positivity_margin"])
    assert positivity.shape == (3,)
    np.testing.assert_allclose(
        positivity, np.min(history, axis=1), atol=2.0e-14, rtol=2.0e-14
    )
    assert json.loads(result["execution_identity"])["certificate_scope"] == (
        "PROJECTED_RESIDUAL_ONLY_NOT_GLOBAL_FORWARD_ERROR"
    )


def test_rf04_polarized_iq_uv_path_preserves_realizability_and_screen() -> None:
    directions, _ = _angular_grid()
    initial = _physical_polarized_state(directions)
    initial_matrices = initial.reshape(-1, 9)
    assert np.max(np.abs(initial_matrices[:, 3:6])) > 1.0e-3
    assert np.max(np.abs(initial_matrices[:, 6:9])) > 1.0e-3
    result = _trajectory(initial, carrier="polarized_rank9_v1")
    diagnostics = result["diagnostics"]
    history = np.asarray(result["radiation_history"])
    assert history.shape == (3, 9 * len(directions))
    np.testing.assert_array_equal(history[0], initial)
    assert not np.array_equal(history[-1], history[0])

    observed = np.asarray([_polarized_metrics(directions, row) for row in history])
    minimum_eigenvalue = np.asarray(diagnostics["minimum_coherency_eigenvalue"])
    screen_leakage = np.asarray(diagnostics["screen_leakage"])
    assert minimum_eigenvalue.shape == screen_leakage.shape == (3,)
    np.testing.assert_allclose(
        minimum_eigenvalue, observed[:, 0], atol=3.0e-13, rtol=2.0e-12
    )
    np.testing.assert_allclose(
        screen_leakage, observed[:, 1], atol=3.0e-13, rtol=2.0e-12
    )
    assert np.all(observed[:, 0] >= -2.0e-12)
    assert np.max(observed[:, 1]) < 1.0e-10


def test_rf04_batch_rows_equal_individual_native_trajectories_in_input_order() -> None:
    native = _native()
    directions, weights = _angular_grid()
    q1, mid, q3, opacity, step_size = _background()
    first = _anisotropic_scalar_state(directions)
    second = np.ascontiguousarray(0.75 + 0.31 * first[::-1])
    initial = np.ascontiguousarray(np.stack((first, second)), dtype=np.float64)
    result = native.rf04_typeii_batch_v1(
        initial,
        directions,
        weights,
        q1,
        mid,
        q3,
        opacity,
        step_size,
        1.3,
        1.0,
        1,
        "scalar_intensity_v1",
        "paired_rest_to_normal_reference_v1",
    )
    expected = np.stack(
        (
            np.asarray(_trajectory(first)["radiation_history"])[-1],
            np.asarray(_trajectory(second)["radiation_history"])[-1],
        )
    )
    final = np.asarray(result["final_radiation"])
    assert result["schema_id"] == SCHEMA_ID
    assert result["route_id"] == "kinetic.typeii.batch_v1"
    assert final.shape == (2, len(directions))
    assert not np.array_equal(expected[0], expected[1])
    np.testing.assert_array_equal(final, expected)
    np.testing.assert_array_equal(np.asarray(result["member_status"]), [0, 0])
    np.testing.assert_array_equal(np.asarray(result["member_completed_steps"]), [2, 2])
    assert tuple(result["member_error_code"]) == (None, None)
