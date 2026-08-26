#!/usr/bin/env python3
"""Execute the bounded BASS-3 generic-vector native-host parity corpus."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import subprocess
import sys

import numpy as np

import bianchi_rustcore as native


BASE_SHA = "445e50184823e58401a8212ceaaf736e72bb35f2"
ORACLE_AUTHORITY_COMMIT = "58d649d438415def3e646d8eee8d0e1f3159ed7f"
ORACLE_ADAPTER_SHA256 = "8bec0834403d7be672fbac995231309a096ddf42ed4a9b6432a2973134e534f8"
INPUT_BYTES_SHA256 = "c852798cf7c1acdb965e07280490cc55ab2b07d771d8a83f55604f5b6d81713a"
BETA = np.array([0.31, -0.27, 0.19])
BETA_DOT = np.array([-0.023, 0.017, 0.029])
ALPHA = 0.73

CHANGED_PATHS = [
    "_rustcore/src/kinetic/generic_vector.rs",
    "_rustcore/src/kinetic/mod.rs",
    "_rustcore/src/lib.rs",
    "_rustcore/src/python/generic_vector.rs",
    "_rustcore/src/python/mod.rs",
    "artifacts/rust_first_runtime/bass3/EXECUTION_EVIDENCE.json",
    "artifacts/rust_first_runtime/bass3/GREEN.log",
    "artifacts/rust_first_runtime/bass3/RED.log",
    "artifacts/rust_first_runtime/bass3/RED_ENVIRONMENT_ATTEMPT.log",
    "tests/oracles/bass3_generic_vector_oracle.py",
    "tests/test_bass3_generic_vector_host_parity.py",
    "tools/audit/run_bass3_generic_vector_host_parity.py",
]


def _load_oracle(root: Path):
    path = root / "tests/oracles/bass3_generic_vector_oracle.py"
    if hashlib.sha256(path.read_bytes()).hexdigest() != ORACLE_ADAPTER_SHA256:
        raise RuntimeError("portable oracle adapter byte identity changed")
    spec = importlib.util.spec_from_file_location("bass3_execution_oracle", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("portable oracle adapter cannot be loaded")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _input_hash(directions: np.ndarray, weights: np.ndarray) -> str:
    digest = hashlib.sha256()
    for value in (directions, weights, BETA, BETA_DOT, np.array([ALPHA])):
        digest.update(np.ascontiguousarray(value, dtype="<f8").tobytes())
    return digest.hexdigest()


def _host(
    directions: np.ndarray,
    weights: np.ndarray,
    beta: np.ndarray,
    beta_dot: np.ndarray,
    alpha: float,
):
    return native.generic_vector_host(
        np.ascontiguousarray(directions),
        np.ascontiguousarray(weights),
        np.ascontiguousarray(beta),
        np.ascontiguousarray(beta_dot),
        float(alpha),
        enabled=True,
    )


def _max_abs(value) -> float:
    return float(np.max(np.abs(np.asarray(value)), initial=0.0))


def _relative(value, *scales: float) -> float:
    return _max_abs(value) / max(1.0, *map(float, scales))


def _residuals(result: dict) -> dict[str, float]:
    collision = np.asarray(result["collision"])
    equilibrium = np.asarray(result["equilibrium"])
    left = np.asarray(result["normalized_left"])
    projector = np.asarray(result["projector"])
    projector_dot = np.asarray(result["projector_dot"])
    kato = np.asarray(result["kato"])
    complement = np.eye(len(equilibrium)) - projector
    return {
        "C_r": _relative(collision @ equilibrium, _max_abs(collision) * _max_abs(equilibrium)),
        "aT_C": _relative(left @ collision, np.linalg.norm(left, 1) * _max_abs(collision)),
        "aT_r_minus_1": abs(float(left @ equilibrium) - 1.0),
        "P2_minus_P": _relative(projector @ projector - projector, _max_abs(projector)),
        "C_P": _relative(collision @ projector, _max_abs(collision) * _max_abs(projector)),
        "P_C": _relative(projector @ collision, _max_abs(projector) * _max_abs(collision)),
        "projector_tangent": _relative(projector @ projector_dot + projector_dot @ projector - projector_dot, _max_abs(projector_dot)),
        "kato_commutator": _relative(kato @ projector - projector @ kato - projector_dot, _max_abs(kato), _max_abs(projector_dot)),
        "P_K_P": _relative(projector @ kato @ projector, _max_abs(kato)),
        "Q_K_Q": _relative(complement @ kato @ complement, _max_abs(kato)),
    }


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def execute(root: Path) -> dict:
    head = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=root, text=True
    ).strip()
    _require(head == BASE_SHA, f"execution must begin at {BASE_SHA}, observed {head}")
    oracle = _load_oracle(root)
    directions, weights = oracle.lebedev26()
    directions = np.ascontiguousarray(directions)
    weights = np.ascontiguousarray(weights)
    _require(_input_hash(directions, weights) == INPUT_BYTES_SHA256, "input bytes changed")

    try:
        native.generic_vector_host(
            directions, weights, BETA, BETA_DOT, ALPHA
        )
    except native.GenericVectorHostDisabledError as error:
        default_off = {
            "status": "PASS",
            "exception": type(error).__name__,
            "message": str(error),
        }
    else:
        raise RuntimeError("generic-vector host route was not default-off")

    generic = _host(directions, weights, BETA, BETA_DOT, ALPHA)
    reference = oracle.paired_bundle(directions, weights, BETA, BETA_DOT)
    reference_collision = oracle.collision_matrix(reference, ALPHA)
    reference_projector_dot = oracle.finite_difference_projector(
        directions, weights, BETA, BETA_DOT
    )
    parity = {
        "collision": _max_abs(generic["collision"] - reference_collision),
        "projector": _max_abs(generic["projector"] - reference.projector),
        "projector_dot_fd": _max_abs(
            generic["projector_dot"] - reference_projector_dot
        ),
        "equilibrium": _max_abs(generic["equilibrium"] - reference.equilibrium),
        "left": _max_abs(generic["normalized_left"] - reference.normalized_left),
    }
    _require(parity["collision"] <= oracle.GLOBAL_SCALAR_MAX, "collision parity failed")
    _require(parity["projector"] <= oracle.GLOBAL_SCALAR_MAX, "projector parity failed")
    _require(
        parity["projector_dot_fd"] <= oracle.FINITE_DIFFERENCE_PROJECTOR_MAX,
        "projector-dot finite-difference parity failed",
    )
    generic_residuals = _residuals(generic)
    _require(max(generic_residuals.values()) <= oracle.IDENTITY_MAX, "generic invariants failed")

    rotation = oracle.rotation_matrix(np.array([0.4, -0.3, 0.7]), 0.61)
    rotated_beta = rotation @ BETA
    rotated_beta_dot = rotation @ BETA_DOT
    rotated = _host(
        np.ascontiguousarray(directions @ rotation.T),
        weights,
        rotated_beta,
        rotated_beta_dot,
        ALPHA,
    )
    state = np.linspace(-0.9, 1.1, 9 * len(directions))
    rotated_state = oracle.rotate_state(state, rotation)
    so3 = {
        key: _relative(
            rotated[key] @ rotated_state
            - oracle.rotate_state(generic[key] @ state, rotation),
            _max_abs(rotated[key] @ rotated_state),
        )
        for key in ("collision", "projector", "projector_dot", "kato")
    }
    _require(max(so3.values()) <= oracle.SO3_MAX, "SO(3) covariance failed")

    scalar_factor = 7.0
    scalar = _host(directions, weights, BETA, BETA_DOT, scalar_factor * ALPHA)
    scalar_residuals = {
        "collision": _max_abs(scalar["collision"] - scalar_factor * generic["collision"]),
        "node_rate": _max_abs(scalar["node_rate"] - scalar_factor * generic["node_rate"]),
        "projector": _max_abs(scalar["projector"] - generic["projector"]),
        "projector_dot": _max_abs(scalar["projector_dot"] - generic["projector_dot"]),
        "kato": _max_abs(scalar["kato"] - generic["kato"]),
    }
    _require(max(scalar_residuals.values()) <= oracle.GLOBAL_SCALAR_MAX, "global scalar separation failed")

    near_alpha = 1e-14
    near = _host(directions, weights, BETA, BETA_DOT, near_alpha)
    _require(not near["collision_off"], "near vacuum was collapsed to exact vacuum")
    _require(np.count_nonzero(near["collision"]) > 0, "near-vacuum collision vanished")
    near_residuals = _residuals(near)
    _require(max(near_residuals.values()) <= oracle.IDENTITY_MAX, "near-vacuum invariants failed")

    vacuum = _host(directions, weights, BETA, BETA_DOT, 0.0)
    _require(vacuum["collision_off"], "exact vacuum did not switch collision off")
    _require(np.count_nonzero(vacuum["collision"]) == 0, "vacuum collision is nonzero")
    _require(
        all(vacuum[name] is None for name in ("projector", "projector_dot", "kato")),
        "exact vacuum selected a nontrivial projector",
    )

    raw_wrong_left = np.zeros((len(weights), 9))
    raw_wrong_left[:, :3] = (np.asarray(generic["w_normal"]) / (4.0 * np.pi))[:, None]
    raw_wrong_left = raw_wrong_left.ravel()
    wrong_left = raw_wrong_left / float(raw_wrong_left @ generic["equilibrium"])
    wrong_projector = np.outer(generic["equilibrium"], wrong_left)
    twice_q = np.repeat(generic["direction_factor"], 9)[:, None] * generic["collision"]
    omit_gamma = generic["collision"] / float(generic["gamma"])
    frozen_left = np.outer(generic["equilibrium_dot"], generic["normalized_left"])
    wrong_kato = -np.asarray(generic["kato"])
    wrong_kato_defect = wrong_kato @ generic["projector"] - generic["projector"] @ wrong_kato - generic["projector_dot"]
    mutation_defects = {
        "omit_q_from_paired_left_dual": _max_abs(wrong_projector - generic["projector"]),
        "apply_q_twice_as_rate_factor": _max_abs(twice_q - generic["collision"]),
        "omit_gamma_from_global_rate": _max_abs(omit_gamma - generic["collision"]),
        "keep_left_dual_fixed_while_beta_changes": _max_abs(frozen_left - generic["projector_dot"]),
        "reverse_kato_commutator_sign": _max_abs(wrong_kato_defect),
        "select_nontrivial_projector_at_exact_vacuum": float("inf"),
    }
    _require(
        all(value > oracle.MUTATION_MIN for value in mutation_defects.values()),
        "one or more hostile mutations escaped detection",
    )

    envelope = {
        "maximum_identity_residual": max(
            max(generic_residuals.values()), max(near_residuals.values())
        ),
        "maximum_host_oracle_operator_residual": max(parity.values()),
        "maximum_so3_residual": max(so3.values()),
        "maximum_global_scalar_residual": max(scalar_residuals.values()),
        "minimum_mutation_defect": min(mutation_defects.values()),
    }
    return {
        "schema": "bass-generic-vector-host-parity-execution/v1",
        "verdict": "PASS_GENERIC_VECTOR_HOST_PARITY",
        "active_base_sha": BASE_SHA,
        "implementation_commit": {
            "binding": "Git commit containing this self-excluding evidence file",
            "literal_sha_excluded": True,
            "reason": "a Git commit cannot contain its own final SHA without self-reference",
        },
        "oracle": {
            "authority_commit": ORACLE_AUTHORITY_COMMIT,
            "adapter_sha256": ORACLE_ADAPTER_SHA256,
            "immutable_input_bytes_sha256": INPUT_BYTES_SHA256,
            "identity_class": "immutable source/input",
        },
        "changed_paths": CHANGED_PATHS,
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "native_module": str(native.__file__),
        },
        "route": {
            "default": "OFF",
            "explicit_opt_in_required": True,
            "default_off_probe": default_off,
            "existing_production_path_replaced": False,
            "classifier_authorized": False,
            "user_facing_production_claim": False,
        },
        "executed_cases": {
            "generic_non_collinear": {"beta": BETA.tolist(), "beta_dot": BETA_DOT.tolist(), "alpha": ALPHA},
            "rotated_so3": {"beta": rotated_beta.tolist(), "beta_dot": rotated_beta_dot.tolist(), "angle": 0.61},
            "global_scalar_rescaling": {"factor": scalar_factor},
            "near_vacuum_nonzero_opacity": {"alpha": near_alpha, "collision_off": False},
            "exact_vacuum": {
                "alpha": 0.0,
                "collision_off": True,
                "projector_selected": False,
                "disposition": vacuum["vacuum_disposition"],
            },
        },
        "thresholds": {
            "identity_max": oracle.IDENTITY_MAX,
            "finite_difference_projector_max": oracle.FINITE_DIFFERENCE_PROJECTOR_MAX,
            "global_scalar_max": oracle.GLOBAL_SCALAR_MAX,
            "so3_max": oracle.SO3_MAX,
            "mutation_min": oracle.MUTATION_MIN,
        },
        "numerical_residual_envelope": envelope,
        "generic_case_residuals": generic_residuals,
        "host_oracle_parity": parity,
        "so3_residuals": so3,
        "global_scalar_residuals": scalar_residuals,
        "mutation_detections": {
            name: {
                "classification": (
                    "VACUUM_PROJECTOR_SELECTION_REJECTED"
                    if name == "select_nontrivial_projector_at_exact_vacuum"
                    else "SCIENTIFIC_OPERATOR_AGREEMENT_FAIL"
                ),
                "defect": ("Infinity" if not np.isfinite(defect) else defect),
                "detected": True,
            }
            for name, defect in mutation_defects.items()
        },
        "skipped_checks": {
            "full_repository_suite": "outside the requested smallest affected set",
            "historical_campaigns": "durable evidence reused; no invalidation predicate",
            "sympy_wolfram_xact": "no formula-authority task and no symbolic rerun authorized",
            "fitting_classifier_runtime_cutover": "explicitly outside BASS-3 scope",
            "performance_benchmark": "no performance claim",
        },
        "claim_boundaries": {
            "bounded_finite_discrete_carrier_only": True,
            "continuum_finite_tilt_theorem": False,
            "authority_promoted": False,
            "runtime_default_changed": False,
            "classifier_authorized": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    receipt = execute(root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(receipt, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print("PASS_GENERIC_VECTOR_HOST_PARITY")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
