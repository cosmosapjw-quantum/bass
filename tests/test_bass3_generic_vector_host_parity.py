"""Focused BASS-3 parity and hostile-mutation tests.

The native path is deliberately opt-in and the portable oracle is test-only.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
import sys

import numpy as np
import pytest

import bianchi_rustcore as native

sys.path.insert(0, str(Path(__file__).with_name("oracles")))
import bass3_generic_vector_oracle as oracle  # noqa: E402


ORACLE_PATH = Path(oracle.__file__)
ORACLE_ADAPTER_SHA256 = "8bec0834403d7be672fbac995231309a096ddf42ed4a9b6432a2973134e534f8"
INPUT_BYTES_SHA256 = "c852798cf7c1acdb965e07280490cc55ab2b07d771d8a83f55604f5b6d81713a"
BETA = np.array([0.31, -0.27, 0.19])
BETA_DOT = np.array([-0.023, 0.017, 0.029])
ALPHA = 0.73


def _inputs() -> tuple[np.ndarray, np.ndarray]:
    directions, weights = oracle.lebedev26()
    return np.ascontiguousarray(directions), np.ascontiguousarray(weights)


def _input_bytes_sha256() -> str:
    directions, weights = _inputs()
    digest = hashlib.sha256()
    for value in (directions, weights, BETA, BETA_DOT, np.array([ALPHA])):
        digest.update(np.ascontiguousarray(value, dtype="<f8").tobytes())
    return digest.hexdigest()


def _host(
    beta: np.ndarray = BETA,
    beta_dot: np.ndarray = BETA_DOT,
    alpha: float = ALPHA,
    *,
    directions: np.ndarray | None = None,
    weights: np.ndarray | None = None,
    enabled: bool = True,
) -> dict:
    default_directions, default_weights = _inputs()
    return native.generic_vector_host(
        default_directions if directions is None else directions,
        default_weights if weights is None else weights,
        np.ascontiguousarray(beta, dtype=float),
        np.ascontiguousarray(beta_dot, dtype=float),
        float(alpha),
        enabled=enabled,
    )


def _max_abs(value: np.ndarray) -> float:
    return float(np.max(np.abs(value), initial=0.0))


def _relative(value: np.ndarray, *scales: float) -> float:
    return _max_abs(value) / max(1.0, *map(float, scales))


def _residuals(result: dict) -> dict[str, float]:
    collision = np.asarray(result["collision"])
    equilibrium = np.asarray(result["equilibrium"])
    left = np.asarray(result["normalized_left"])
    projector = np.asarray(result["projector"])
    projector_dot = np.asarray(result["projector_dot"])
    kato = np.asarray(result["kato"])
    identity = np.eye(len(equilibrium))
    complement = identity - projector
    return {
        "right_null": _relative(collision @ equilibrium, _max_abs(collision) * _max_abs(equilibrium)),
        "left_null": _relative(left @ collision, np.linalg.norm(left, 1) * _max_abs(collision)),
        "normalization": abs(float(left @ equilibrium) - 1.0),
        "projector_idempotence": _relative(projector @ projector - projector, _max_abs(projector)),
        "collision_projector_right": _relative(collision @ projector, _max_abs(collision) * _max_abs(projector)),
        "projector_collision_left": _relative(projector @ collision, _max_abs(projector) * _max_abs(collision)),
        "projector_tangent": _relative(projector @ projector_dot + projector_dot @ projector - projector_dot, _max_abs(projector_dot)),
        "kato_commutator": _relative(kato @ projector - projector @ kato - projector_dot, _max_abs(kato), _max_abs(projector_dot)),
        "kato_range_block": _relative(projector @ kato @ projector, _max_abs(kato)),
        "kato_kernel_block": _relative(complement @ kato @ complement, _max_abs(kato)),
    }


def _assert_vacuum_contract(result: dict) -> None:
    if not result["collision_off"]:
        raise AssertionError("exact vacuum must switch collision off")
    if any(result[name] is not None for name in ("projector", "projector_dot", "kato")):
        raise AssertionError("exact vacuum selected a nontrivial collision projector")
    if np.count_nonzero(result["collision"]):
        raise AssertionError("exact vacuum collision operator must be exactly zero")


def test_frozen_oracle_and_immutable_input_bytes_are_bound() -> None:
    assert hashlib.sha256(ORACLE_PATH.read_bytes()).hexdigest() == ORACLE_ADAPTER_SHA256
    assert _input_bytes_sha256() == INPUT_BYTES_SHA256


def test_route_is_default_off_before_native_execution() -> None:
    from bianchi import backend
    from bianchi import q

    assert not hasattr(backend, "generic_vector_host")
    assert "generic_vector_host" not in q.__all__
    with pytest.raises(native.GenericVectorHostDisabledError):
        _host(enabled=False)


def test_generic_non_collinear_host_matches_frozen_oracle_and_invariants() -> None:
    directions, weights = _inputs()
    expected = oracle.paired_bundle(directions, weights, BETA, BETA_DOT)
    result = _host()
    expected_collision = oracle.collision_matrix(expected, ALPHA)
    finite_difference = oracle.finite_difference_projector(
        directions, weights, BETA, BETA_DOT
    )

    assert result["schema"] == "bass.generic-vector-host/v1"
    assert result["route_default"] == "OFF"
    assert result["collision_off"] is False
    np.testing.assert_allclose(result["e_normal"], expected.e_normal, rtol=0.0, atol=2e-12)
    np.testing.assert_allclose(result["w_normal"], expected.w_normal, rtol=0.0, atol=2e-12)
    np.testing.assert_allclose(result["doppler"], expected.doppler, rtol=0.0, atol=2e-12)
    np.testing.assert_allclose(result["direction_factor"], expected.direction_factor, rtol=0.0, atol=2e-12)
    np.testing.assert_allclose(result["node_rate"], ALPHA * expected.doppler, rtol=0.0, atol=2e-12)
    np.testing.assert_allclose(result["equilibrium"], expected.equilibrium, rtol=0.0, atol=2e-12)
    np.testing.assert_allclose(result["normalized_left"], expected.normalized_left, rtol=0.0, atol=2e-12)
    np.testing.assert_allclose(result["projector"], expected.projector, rtol=0.0, atol=2e-12)
    np.testing.assert_allclose(result["collision"], expected_collision, rtol=0.0, atol=2e-12)
    np.testing.assert_allclose(
        result["projector_dot"],
        finite_difference,
        rtol=0.0,
        atol=oracle.FINITE_DIFFERENCE_PROJECTOR_MAX,
    )
    expected_kato = finite_difference @ expected.projector - expected.projector @ finite_difference
    np.testing.assert_allclose(
        result["kato"], expected_kato, rtol=0.0, atol=oracle.FINITE_DIFFERENCE_PROJECTOR_MAX
    )
    assert max(_residuals(result).values()) <= oracle.IDENTITY_MAX


def test_rotated_so3_equivalent_case_executes_covariantly() -> None:
    directions, weights = _inputs()
    rotation = oracle.rotation_matrix(np.array([0.4, -0.3, 0.7]), 0.61)
    rotated = _host(
        rotation @ BETA,
        rotation @ BETA_DOT,
        directions=np.ascontiguousarray(directions @ rotation.T),
        weights=weights,
    )
    base = _host()
    np.testing.assert_allclose(
        rotated["e_normal"], base["e_normal"] @ rotation.T, rtol=0.0, atol=oracle.SO3_MAX
    )
    for key in ("doppler", "direction_factor", "w_normal", "node_rate"):
        np.testing.assert_allclose(rotated[key], base[key], rtol=0.0, atol=oracle.SO3_MAX)
    state = np.linspace(-0.9, 1.1, 9 * len(directions))
    rotated_state = oracle.rotate_state(state, rotation)
    for key in ("collision", "projector", "projector_dot", "kato"):
        lhs = rotated[key] @ rotated_state
        rhs = oracle.rotate_state(base[key] @ state, rotation)
        assert _relative(lhs - rhs, _max_abs(lhs), _max_abs(rhs)) <= oracle.SO3_MAX
    assert max(_residuals(rotated).values()) <= oracle.IDENTITY_MAX


def test_global_scalar_rescaling_changes_only_rate_data() -> None:
    base = _host()
    factor = 7.0
    scaled = _host(alpha=factor * ALPHA)
    np.testing.assert_allclose(scaled["collision"], factor * base["collision"], rtol=0.0, atol=oracle.GLOBAL_SCALAR_MAX)
    np.testing.assert_allclose(scaled["node_rate"], factor * base["node_rate"], rtol=0.0, atol=oracle.GLOBAL_SCALAR_MAX)
    for key in ("equilibrium", "normalized_left", "projector", "projector_dot", "kato"):
        np.testing.assert_array_equal(scaled[key], base[key])


def test_near_vacuum_nonzero_opacity_executes_without_selecting_vacuum() -> None:
    near = _host(alpha=1e-14)
    base = _host()
    assert near["collision_off"] is False
    assert np.count_nonzero(near["collision"]) > 0
    np.testing.assert_allclose(
        near["collision"] / 1e-14,
        base["collision"] / ALPHA,
        rtol=0.0,
        atol=oracle.GLOBAL_SCALAR_MAX,
    )
    np.testing.assert_array_equal(near["projector"], base["projector"])


def test_exact_vacuum_is_collision_off_without_nontrivial_projector() -> None:
    result = _host(alpha=0.0)
    _assert_vacuum_contract(result)
    assert result["vacuum_disposition"] == "COLLISION_OFF_NO_NONTRIVIAL_PROJECTOR"
    assert result["beta_quotiented"] is True


def test_mutation_omit_q_from_paired_left_dual_is_detected() -> None:
    result = _host()
    raw = np.zeros((len(result["w_normal"]), 9))
    raw[:, :3] = (np.asarray(result["w_normal"]) / (4.0 * np.pi))[:, None]
    raw = raw.ravel()
    equilibrium = np.asarray(result["equilibrium"])
    wrong_left = raw / float(raw @ equilibrium)
    wrong_projector = np.outer(equilibrium, wrong_left)
    assert _max_abs(wrong_projector - result["projector"]) > oracle.MUTATION_MIN


def test_mutation_apply_q_twice_as_rate_factor_is_detected() -> None:
    result = _host()
    wrong = np.repeat(result["direction_factor"], 9)[:, None] * result["collision"]
    assert _max_abs(wrong - result["collision"]) > oracle.MUTATION_MIN


def test_mutation_omit_gamma_from_global_rate_is_detected() -> None:
    result = _host()
    wrong = result["collision"] / float(result["gamma"])
    assert _max_abs(wrong - result["collision"]) > oracle.MUTATION_MIN


def test_mutation_keep_left_dual_fixed_while_beta_changes_is_detected() -> None:
    result = _host()
    wrong = np.outer(result["equilibrium_dot"], result["normalized_left"])
    assert _max_abs(wrong - result["projector_dot"]) > oracle.MUTATION_MIN


def test_mutation_reverse_kato_commutator_sign_is_detected() -> None:
    result = _host()
    wrong = -np.asarray(result["kato"])
    defect = wrong @ result["projector"] - result["projector"] @ wrong - result["projector_dot"]
    assert _max_abs(defect) > oracle.MUTATION_MIN


def test_mutation_select_nontrivial_projector_at_exact_vacuum_is_detected() -> None:
    result = dict(_host(alpha=0.0))
    size = int(result["state_size"])
    result["projector"] = np.eye(size)
    with pytest.raises(AssertionError, match="selected a nontrivial"):
        _assert_vacuum_contract(result)
