"""RF-04 public/native kinetic contract.

These tests intentionally bind only the frozen Type-II aligned reference lane.
The Python layer is API/configuration only; every trajectory and batch call is
owned by the three native RF-04 symbols.
"""
from __future__ import annotations

import importlib
import json
from pathlib import Path

import numpy as np


SCHEMA_ID = "bass-rf04-typeii-public-route/v1"
SCHEMA_SHA256 = "be2c73e07e5a8179c10ec4aab058915b79b1d7ab87fc624d65e5e0d34d94d097"
SCI_AUTH_HEAD = "1298c2ef8cc8eaca8edcd99332653c8a1cbc1c86"
SCI_AUTH_TREE = "37edaaea720a3197881b94bc39413787db091432"
SCI_AUTH_MANIFEST_SHA256 = (
    "9c646d7fa43463484e832349f0a4ae9c3728dc1d68a2370504facdc41aad9b9f"
)
ROUTES = {
    "kinetic.typeii.execution_identity_v1": (
        "rf04_typeii_execution_identity_v1",
    ),
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


def _six_point_grid() -> tuple[np.ndarray, np.ndarray]:
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


def _background(v: float = 0.0, steps: int = 2) -> tuple[np.ndarray, ...]:
    row = np.asarray([0.0, 0.0, 0.0, 0.0, v], dtype=np.float64)
    q1 = np.ascontiguousarray(np.repeat(row[None, :], steps, axis=0))
    mid = q1.copy()
    q3 = q1.copy()
    opacity = np.ascontiguousarray(np.full(steps, 0.2, dtype=np.float64))
    step_size = np.ascontiguousarray(np.full(steps, 1.0e-3, dtype=np.float64))
    return q1, mid, q3, opacity, step_size


def _trajectory(
    initial: np.ndarray,
    *,
    carrier: str = "scalar_intensity_v1",
    quadrature_route: str = "paired_rest_to_normal_reference_v1",
    v: float = 0.0,
):
    directions, weights = _six_point_grid()
    q1, mid, q3, opacity, step_size = _background(v)
    return _native().rf04_typeii_trajectory_v1(
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
        carrier,
        quadrature_route,
    )


def _physical_unpolarized_state(directions: np.ndarray) -> np.ndarray:
    rows: list[float] = []
    for direction in directions:
        projector = np.eye(3) - np.outer(direction, direction)
        rows.extend(
            [
                projector[0, 0],
                projector[1, 1],
                projector[2, 2],
                projector[0, 1],
                projector[0, 2],
                projector[1, 2],
                0.0,
                0.0,
                0.0,
            ]
        )
    return np.asarray(rows, dtype=np.float64)


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


def test_rf04_public_python_routes_are_thin_native_owners() -> None:
    from bianchi import kinetic

    assert kinetic.typeii_execution_identity_v1.__module__ == "bianchi.kinetic"
    assert kinetic.typeii_trajectory_v1.__module__ == "bianchi.kinetic"
    assert kinetic.typeii_batch_v1.__module__ == "bianchi.kinetic"
    source = Path(kinetic.__file__).read_text(encoding="utf-8")
    assert "qe_evolve" not in source
    assert "qe_ensemble" not in source
    assert "python_oracle" not in source


def test_rf04_scalar_trajectory_has_exact_schema_and_bounded_diagnostics() -> None:
    result = _trajectory(np.ones(6, dtype=np.float64))
    assert result["schema_id"] == SCHEMA_ID
    assert result["route_id"] == "kinetic.typeii.trajectory_v1"
    history = np.asarray(result["radiation_history"])
    assert history.shape == (3, 6)
    np.testing.assert_array_equal(history[0], np.ones(6))
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
    assert np.all(positivity >= 0.0)
    assert np.max(np.asarray(diagnostics["right_kernel_residual"])) < 2.0e-13
    assert np.max(np.asarray(diagnostics["projector_idempotence_residual"])) < 3.0e-13
    assert json.loads(result["execution_identity"])["certificate_scope"] == (
        "PROJECTED_RESIDUAL_ONLY_NOT_GLOBAL_FORWARD_ERROR"
    )


def test_rf04_polarized_iq_uv_capability_stays_physical() -> None:
    directions, _ = _six_point_grid()
    initial = _physical_unpolarized_state(directions)
    result = _trajectory(initial, carrier="polarized_rank9_v1")
    diagnostics = result["diagnostics"]
    assert np.asarray(result["radiation_history"]).shape == (3, 54)
    minimum_eigenvalue = np.asarray(diagnostics["minimum_coherency_eigenvalue"])
    screen_leakage = np.asarray(diagnostics["screen_leakage"])
    assert minimum_eigenvalue.shape == screen_leakage.shape == (3,)
    assert np.all(minimum_eigenvalue >= -2.0e-12)
    assert np.max(screen_leakage) < 1.0e-10


def test_rf04_batch_preserves_input_order_and_success_shape() -> None:
    native = _native()
    directions, weights = _six_point_grid()
    q1, mid, q3, opacity, step_size = _background()
    initial = np.ascontiguousarray(
        np.stack((np.ones(6), np.linspace(0.8, 1.3, 6))), dtype=np.float64
    )
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
    assert result["schema_id"] == SCHEMA_ID
    assert result["route_id"] == "kinetic.typeii.batch_v1"
    assert np.asarray(result["final_radiation"]).shape == (2, 6)
    np.testing.assert_array_equal(np.asarray(result["member_status"]), [0, 0])
    np.testing.assert_array_equal(np.asarray(result["member_completed_steps"]), [2, 2])
    assert tuple(result["member_error_code"]) == (None, None)
