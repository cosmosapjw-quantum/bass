"""Hostile RF-04 controls.

Mutation oracles are test-only and never provide a production fallback.
"""
from __future__ import annotations

import importlib
import json
from pathlib import Path

import numpy as np
import pytest

from .test_kinetic_contract import _background, _physical_unpolarized_state, _six_point_grid


def _native():
    return importlib.import_module("bianchi_rustcore")


def _trajectory(initial, carrier, route, *, v=0.1):
    directions, weights = _six_point_grid()
    q1, mid, q3, opacity, step_size = _background(v=v, steps=1)
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
        route,
    )


def _scalar_equilibrium(directions: np.ndarray, v: float, axis: int) -> np.ndarray:
    gamma = 1.0 / np.sqrt(1.0 - v * v)
    return np.asarray((gamma * (1.0 - v * directions[:, axis])) ** -4)


def test_rate_dual_mutation_is_detected() -> None:
    directions, weights = _six_point_grid()
    v = 0.1
    axis = 1
    right = _scalar_equilibrium(directions, v, axis)
    result = _trajectory(right, "scalar_intensity_v1", "fixed_grid_ap_corrected_v1", v=v)
    assert np.max(np.asarray(result["diagnostics"]["right_kernel_residual"])) < 2.0e-13

    # Hostile mutation: drop q(e)=1-v e_axis from the inverse-transpose left rate.
    correct_left = weights * (1.0 - v * directions[:, axis]) / (4.0 * np.pi)
    mutant_left = weights / (4.0 * np.pi)
    probe = np.asarray([0.2, -0.1, 0.4, 0.7, -0.3, 0.9])
    collision = probe - right * np.dot(correct_left, probe) / np.dot(correct_left, right)
    assert abs(np.dot(correct_left, collision)) < 3.0e-15
    assert abs(np.dot(mutant_left, collision)) > 1.0e-4


def test_projector_connection_mutation_is_detected() -> None:
    result = _trajectory(
        np.asarray([0.2, 0.3, 0.5, 0.7, 0.9, 1.1]),
        "scalar_intensity_v1",
        "paired_rest_to_normal_reference_v1",
    )
    assert np.max(np.asarray(result["diagnostics"]["projector_idempotence_residual"])) < 3.0e-13

    directions, weights = _six_point_grid()
    v = 0.1
    right = _scalar_equilibrium(directions, v, 1)
    left = weights * (1.0 - v * directions[:, 1]) / (4.0 * np.pi)
    projector = np.outer(right, left) / np.dot(left, right)
    mutant = np.outer(right, left) / (np.dot(left, right) + 0.1)
    assert np.linalg.norm(projector @ projector - projector) < 2.0e-14
    assert np.linalg.norm(mutant @ mutant - mutant) > 1.0e-3


def test_fixed_grid_route_conflation_mutation_is_detected() -> None:
    directions, _ = _six_point_grid()
    equilibrium = _scalar_equilibrium(directions, 0.1, 1)
    raw = _trajectory(equilibrium, "scalar_intensity_v1", "fixed_grid_raw_v1")
    corrected = _trajectory(
        equilibrium, "scalar_intensity_v1", "fixed_grid_ap_corrected_v1"
    )
    raw_null = np.asarray(raw["diagnostics"]["equilibrium_null_residual"])
    corrected_null = np.asarray(corrected["diagnostics"]["equilibrium_null_residual"])
    assert np.max(raw_null) > 1.0e-5
    assert np.max(corrected_null) < 2.0e-13
    assert not np.array_equal(
        np.asarray(raw["radiation_history"]),
        np.asarray(corrected["radiation_history"]),
    )


def test_nonnormal_global_error_overclaim_mutation_is_detected() -> None:
    identity = json.loads(_native().rf04_typeii_execution_identity_v1())
    assert identity["certificate_scope"] == "PROJECTED_RESIDUAL_ONLY_NOT_GLOBAL_FORWARD_ERROR"
    assert "GLOBAL_FORWARD_ERROR" not in identity.get("certificate_claims", [])

    # A hostile upper-triangular family demonstrates why a residual label cannot
    # be mutated into a global forward-error certificate without an operator bound.
    scale = 1.0e8
    operator = np.asarray([[-1.0, scale], [0.0, -1.0]])
    approximate = np.asarray([0.0, np.exp(-1.0)])
    projected_residual = abs(operator[1] @ approximate + approximate[1])
    actual_first_component = scale * np.exp(-1.0)
    assert projected_residual == 0.0
    assert actual_first_component > 1.0e7


@pytest.mark.parametrize(
    "carrier,route",
    [
        ("stokes4_silent_projection", "paired_rest_to_normal_reference_v1"),
        ("scalar_intensity_v1", "fixed_grid_claimed_ap_without_correction"),
    ],
)
def test_unsupported_carrier_or_route_fails_closed(carrier: str, route: str) -> None:
    initial = np.ones(6 if carrier == "scalar_intensity_v1" else 24)
    with pytest.raises(_native().RF04CapabilityError) as error:
        _trajectory(initial, carrier, route)
    assert "RF04_UNSUPPORTED_CAPABILITY" in str(error.value)


def test_forbidden_legacy_substitution_mutation_is_detected() -> None:
    adapter = Path("_rustcore/src/python/rf04_typeii.rs").read_text(encoding="utf-8")
    public = Path("bianchi/kinetic/__init__.py").read_text(encoding="utf-8")
    combined = adapter + public
    assert "qe_evolve" not in combined
    assert "qe_ensemble" not in combined
    assert "qx_" not in combined
    assert "qp_" not in combined
    assert "python_oracle" not in combined


def test_polarized_nonphysical_member_fails_closed_without_silent_projection() -> None:
    directions, _ = _six_point_grid()
    physical = _physical_unpolarized_state(directions)
    nonphysical = physical.copy()
    nonphysical[0] += 0.25
    with pytest.raises(_native().RF04PhysicalDomainError) as error:
        _trajectory(
            nonphysical,
            "polarized_rank9_v1",
            "paired_rest_to_normal_reference_v1",
            v=0.0,
        )
    assert "RF04_NONPHYSICAL_CARRIER" in str(error.value)
