#!/usr/bin/env python3
"""Build the BASS-only SYNC-MAP-02E-R1 hardened formula export.

The parent PR #99 export is preserved byte-for-byte.  This generator produces a
superseding full registry with regular zero-boost aberration, a formally typed
blackbody weighted pullback, physical ray length ``s=c*t``, and explicit
geodesic-normal structural specializations.

Only Python's standard library is used so the exact artifact can be regenerated
on an offline local clone.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

EXPECTED_PARENT_REGISTRY_HASH = (
    "16f699043a7420c6e62abdad02434a216075ce55f69583b5051965ea53db5612"
)
EXPECTED_PARENT_HEAD = "e1467825c8f4c5e3f47df5da5b8a6202e8f96f30"
FORMULA_IDS = [
    "BASS.FRAME.ABERRATED_DIRECTION.001",
    "BASS.FRAME.BLACKBODY_TEMPERATURE_PULLBACK.001",
    "BASS.FRAME.DOPPLER_FACTOR.001",
    "BASS.FRAME.SOLID_ANGLE_JACOBIAN.001",
    "BASS.PHOTON.DIRECTION_FLOW.001",
    "BASS.PHOTON.ENERGY_DRIFT.001",
]
SEMANTIC_DROP_KEYS = {
    "schema_version",
    "formula_id",
    "authority_theorem",
    "provenance",
}


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_object(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


def semantic_projection(equation_ir: dict[str, Any]) -> dict[str, Any]:
    return {
        key: copy.deepcopy(value)
        for key, value in equation_ir.items()
        if key not in SEMANTIC_DROP_KEYS
    }


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def by_formula_id(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = data.get("formulas", [])
    result = {row.get("formula_id"): row for row in rows}
    require(None not in result, "formula without formula_id")
    require(len(result) == len(rows), "duplicate formula_id")
    return result


def replace_formula_metadata(
    record: dict[str, Any],
    *,
    dependencies: list[str],
    dependency_roles: list[dict[str, str]],
    external_dependencies: list[str],
    structural_specializations: list[dict[str, str]],
) -> None:
    record["dependencies"] = dependencies
    record["dependency_roles"] = dependency_roles
    record["external_dependencies"] = external_dependencies
    record["structural_specializations"] = structural_specializations
    targets = record.pop("consumer_repositories", [])
    record["declared_consumer_targets"] = targets
    record["status"] = "SEMANTIC_HARDENING_CANDIDATE_LOCAL_REPLAY_REQUIRED"


def patch_doppler(record: dict[str, Any]) -> None:
    ir = record["equation_ir"]
    ir["schema_version"] = "1.1.0"
    ir["mathematical_kind"] = "EQUATION"
    ir["target"] = "D_beta(n_sky)=gamma*(1+beta_dot_n_sky)"
    ir["domain"]["zero_boost"] = "direct evaluation"
    ir["known_limits"] = [
        "propagation-direction chart: D_beta(e)=gamma*(1-beta_dot_e)"
    ]
    replace_formula_metadata(
        record,
        dependencies=[],
        dependency_roles=[],
        external_dependencies=[],
        structural_specializations=[],
    )


def patch_aberration(record: dict[str, Any]) -> None:
    ir = record["equation_ir"]
    ir["schema_version"] = "1.1.0"
    ir["mathematical_kind"] = "BASE_MAP"
    ir["authority_theorem"] = (
        "Exact finite local-observer aberration map with a regular zero-boost coefficient"
    )
    ir["target"] = "A_beta(n_sky)^a"
    ir["assumptions"] = [
        item
        for item in ir["assumptions"]
        if "(gamma-1)/beta_squared" not in item
    ] + ["chi_beta = gamma^2/(gamma+1)"]
    ir["domain"]["zero_boost"] = "direct evaluation without 0/0"
    ir["terms"] = [
        {
            "input": (
                "[n_sky^a+(gamma+(gamma^2/(gamma+1))*beta_dot_n_sky)*"
                "beta^a]/doppler_factor_source(n_sky)"
            ),
            "coefficient": {"type": "integer", "value": 1},
        }
    ]
    ir["known_limits"] = [
        "A_beta^(-1)=A_(-beta) with source and target charts exchanged",
        (
            "(gamma-1)/beta_squared = gamma^2/(gamma+1) away from zero; "
            "the regular right-hand side gives 1/2 at beta=0"
        ),
    ]
    ir["base_map_orientation"] = "SOURCE_SKY_TO_TARGET_SKY"
    ir["inverse_map_for_target_evaluation"] = "A_(-beta)"
    replace_formula_metadata(
        record,
        dependencies=["BASS.FRAME.DOPPLER_FACTOR.001"],
        dependency_roles=[
            {
                "formula_id": "BASS.FRAME.DOPPLER_FACTOR.001",
                "role": "NORMALIZATION_REQUIRED",
            }
        ],
        external_dependencies=[],
        structural_specializations=[],
    )


def patch_blackbody(record: dict[str, Any]) -> None:
    ir = record["equation_ir"]
    ir["schema_version"] = "1.1.0"
    ir["mathematical_kind"] = "WEIGHTED_SECTION_PUSHFORWARD"
    ir["authority_theorem"] = (
        "Exact Doppler-weight-one thermodynamic blackbody-temperature weighted pullback"
    )
    ir["representation"] = "local-observer-Lorentz-sky-weighted-section"
    ir["assumptions"] = [
        "nu_tilde = doppler_factor_source(n_sky)*nu",
        "h_P and k_B retained",
        "temperature_source(n_sky) > 0",
        "doppler_factor_source(n_sky) > 0",
        "spin_weight = 0",
        "doppler_weight = 1",
    ]
    ir["domain"] = {
        "spectrum": "Planck blackbody",
        "observable": "absolute thermodynamic temperature",
        "source_base": "CELESTIAL_SPHERE(u)",
        "target_base": "CELESTIAL_SPHERE(u_tilde)",
    }
    ir["terms"] = [
        {
            "input": (
                "doppler_factor_target(n_sky_tilde)*temperature_source("
                "inverse_aberration_beta(n_sky_tilde))"
            ),
            "coefficient": {"type": "integer", "value": 1},
        }
    ]
    ir["structural_zero_rules"] = [
        "beta = 0 implies temperature_tilde(n_sky)=temperature_source(n_sky)",
        (
            "Pullback[A_beta,temperature_tilde]="
            "doppler_factor_source*temperature_source"
        ),
    ]
    ir["branch_predicates"] = [
        (
            "blackbody thermodynamic temperature only; generic frequency-dependent "
            "intensity and spectral distortions are excluded"
        ),
        (
            "solid-angle Jacobian is a measure/harmonic theorem, not a pointwise "
            "temperature multiplier"
        ),
    ]
    ir["known_limits"] = [
        (
            "h_P*nu_tilde/(k_B*temperature_tilde)="
            "h_P*nu/(k_B*temperature_source)"
        ),
        "infinitesimal axial generator: G_1 T=x*T-(1-x^2)*dT/dx",
    ]
    ir["operator_ir"] = {
        "source_bundle": {
            "base": "CELESTIAL_SPHERE(u)",
            "fiber": "POSITIVE_REAL_KELVIN",
            "spin_weight": 0,
            "doppler_weight": 1,
        },
        "target_bundle": {
            "base": "CELESTIAL_SPHERE(u_tilde)",
            "fiber": "POSITIVE_REAL_KELVIN",
            "spin_weight": 0,
            "doppler_weight": 1,
        },
        "base_map": {
            "formula_id": "BASS.FRAME.ABERRATED_DIRECTION.001",
            "symbol": "A_beta",
            "direction": "SOURCE_TO_TARGET",
            "target_evaluation_uses": "INVERSE_MAP",
        },
        "fiber_weight": {
            "formula_id": "BASS.FRAME.DOPPLER_FACTOR.001",
            "symbol": "D_beta",
            "exponent": 1,
        },
        "defining_equation": {
            "lhs": "Pullback[A_beta,temperature_tilde]",
            "rhs": "doppler_factor_source*temperature_source",
        },
        "solved_equation": {
            "lhs": "temperature_tilde",
            "rhs": (
                "Pullback[Inverse[A_beta],"
                "doppler_factor_source*temperature_source]"
            ),
        },
        "composition_order": [
            "INVERSE_BASE_MAP_PULLBACK",
            "TARGET_CHART_DOPPLER_MULTIPLICATION",
        ],
    }
    replace_formula_metadata(
        record,
        dependencies=[
            "BASS.FRAME.ABERRATED_DIRECTION.001",
            "BASS.FRAME.DOPPLER_FACTOR.001",
        ],
        dependency_roles=[
            {
                "formula_id": "BASS.FRAME.ABERRATED_DIRECTION.001",
                "role": "BASE_MAP_REQUIRED",
            },
            {
                "formula_id": "BASS.FRAME.DOPPLER_FACTOR.001",
                "role": "FIBER_WEIGHT_REQUIRED",
            },
        ],
        external_dependencies=[],
        structural_specializations=[],
    )


def patch_solid_angle(record: dict[str, Any]) -> None:
    ir = record["equation_ir"]
    ir["schema_version"] = "1.1.0"
    ir["mathematical_kind"] = "MEASURE_PUSHFORWARD"
    ir["representation"] = "local-observer-Lorentz-sky-measure"
    ir["terms"] = [
        {
            "input": "doppler_factor_source(n_sky)^(-2)*dOmega",
            "coefficient": {"type": "integer", "value": 1},
        }
    ]
    ir["branch_predicates"] = [
        "full-sky exact Jacobian; masks and estimator response are excluded",
        "not a direct dependency of pointwise blackbody-temperature evaluation",
    ]
    replace_formula_metadata(
        record,
        dependencies=[
            "BASS.FRAME.ABERRATED_DIRECTION.001",
            "BASS.FRAME.DOPPLER_FACTOR.001",
        ],
        dependency_roles=[
            {
                "formula_id": "BASS.FRAME.ABERRATED_DIRECTION.001",
                "role": "BASE_MAP_JACOBIAN_REQUIRED",
            },
            {
                "formula_id": "BASS.FRAME.DOPPLER_FACTOR.001",
                "role": "JACOBIAN_WEIGHT_REQUIRED",
            },
        ],
        external_dependencies=[],
        structural_specializations=[],
    )


def photon_specialization() -> list[dict[str, str]]:
    return [
        {
            "formula_id": "BASS.GEO.NORMAL_ACCELERATION.001",
            "role": "SPECIALIZES_UNDER_ZERO",
            "value": "A_normal^a=0",
        }
    ]


def harden_photon_common(ir: dict[str, Any]) -> None:
    ir["schema_version"] = "1.1.0"
    ir["assumptions"] = [
        item
        for item in ir["assumptions"]
        if "ray_parameter" not in item
        and "normal_congruence_acceleration" not in item
    ] + [
        "ray_parameter s = c*t has dimension L",
        "normal_congruence_acceleration A_normal^a = 0",
    ]
    ir["domain"]["frame"] = "geodesic normal orthonormal tetrad"
    ir["domain"]["ray_parameter"] = "physical length s=c*t"


def patch_direction_flow(record: dict[str, Any]) -> None:
    ir = record["equation_ir"]
    harden_photon_common(ir)
    ir["mathematical_kind"] = "PHASE_SPACE_VECTOR_FIELD"
    ir["authority_theorem"] = (
        "Exact homogeneous celestial-sphere photon direction flow in the geodesic normal frame"
    )
    ir["target"] = "V^a = d e^a/ds"
    if not any("aB^a is the Bianchi structure vector" in x for x in ir["assumptions"]):
        ir["assumptions"].append(
            "aB^a is the Bianchi structure vector and is not A_normal^a"
        )
    ir["branch_predicates"] = [
        (
            "all eleven public Bianchi branches and exceptional VI_-1/9 on "
            "declared physical ONF charts"
        ),
        (
            "polarization screen-basis transport is excluded and owned by a later "
            "BASS photon node"
        ),
    ]
    ir["known_limits"] = [
        "FLRW invariant-frame limit V^a = 0",
        "proper-time runtime adapter V_t^a=c*V_s^a",
    ]
    ir["screen_basis_transport_status"] = "EXCLUDED_NEXT_BASS_NODE"
    replace_formula_metadata(
        record,
        dependencies=[],
        dependency_roles=[],
        external_dependencies=[
            "BASS.GEO.EXTRINSIC_CURVATURE_SHEAR_SPLIT.001",
            "BASS.GEO.SPATIAL_PROJECTOR.001",
            "BASS.GEO.LEVI_CIVITA_CONNECTION.001",
            "BASS.GEO.STRUCTURE_CONSTANTS.001",
        ],
        structural_specializations=photon_specialization(),
    )


def patch_energy_drift(record: dict[str, Any]) -> None:
    ir = record["equation_ir"]
    harden_photon_common(ir)
    ir["mathematical_kind"] = "PHASE_SPACE_SCALAR_DRIFT"
    ir["authority_theorem"] = (
        "Exact homogeneous null-geodesic photon-energy drift in the geodesic normal frame"
    )
    ir["target"] = "R = d ln(epsilon_gamma)/ds"
    ir["branch_predicates"] = [
        "all eleven public Bianchi branches on their declared physical ONF charts",
        (
            "the general accelerated-observer term -A_normal_a*e^a is excluded "
            "by the declared geodesic-normal specialization"
        ),
    ]
    ir["known_limits"] = [
        "FLRW limit R = -H_geom",
        "Minkowski limit R = 0",
        "proper-time runtime adapter R_t=c*R_s",
    ]
    replace_formula_metadata(
        record,
        dependencies=[],
        dependency_roles=[],
        external_dependencies=[
            "BASS.GEO.EXTRINSIC_CURVATURE_SHEAR_SPLIT.001"
        ],
        structural_specializations=photon_specialization(),
    )


def rebuild_edges(data: dict[str, Any]) -> None:
    internal: list[dict[str, str]] = []
    external: list[dict[str, str]] = []
    for record in data["formulas"]:
        formula_id = record["formula_id"]
        for dependency in record["dependencies"]:
            internal.append(
                {"from": formula_id, "to": dependency, "relation": "depends_on"}
            )
        for dependency in record["external_dependencies"]:
            external.append(
                {"from": formula_id, "to": dependency, "relation": "depends_on"}
            )
        for specialization in record["structural_specializations"]:
            external.append(
                {
                    "from": formula_id,
                    "to": specialization["formula_id"],
                    "relation": specialization["role"],
                    "value": specialization["value"],
                }
            )
    data["internal_dependency_edges"] = sorted(
        internal, key=lambda row: (row["from"], row["to"], row["relation"])
    )
    data["external_dependency_edges"] = sorted(
        external,
        key=lambda row: (
            row["from"],
            row["to"],
            row["relation"],
            row.get("value", ""),
        ),
    )


def rebuild_hashes(data: dict[str, Any]) -> None:
    for record in data["formulas"]:
        projection = semantic_projection(record["equation_ir"])
        record["semantic_projection"] = projection
        record["semantic_hash"] = sha256_object(projection)

    projection_rows = []
    for record in sorted(data["formulas"], key=lambda row: row["formula_id"]):
        projection_rows.append(
            {
                "formula_id": record["formula_id"],
                "semantic_hash": record["semantic_hash"],
                "dependencies": record["dependencies"],
                "dependency_roles": record["dependency_roles"],
                "external_dependencies": record["external_dependencies"],
                "structural_specializations": record["structural_specializations"],
                "declared_consumer_targets": record["declared_consumer_targets"],
            }
        )
    registry_projection = {
        "formulas": projection_rows,
        "internal_dependency_edges": data["internal_dependency_edges"],
        "external_dependency_edges": data["external_dependency_edges"],
    }
    data["registry_semantic_projection"] = registry_projection
    data["registry_semantic_hash"] = sha256_object(registry_projection)


def build(parent: dict[str, Any]) -> dict[str, Any]:
    require(
        parent.get("registry_semantic_hash") == EXPECTED_PARENT_REGISTRY_HASH,
        "unexpected PR #99 parent registry hash",
    )
    parent_map = by_formula_id(parent)
    require(set(parent_map) == set(FORMULA_IDS), "unexpected parent formula set")

    data = copy.deepcopy(parent)
    data["schema_version"] = "1.1.0"
    data["program_id"] = "BASS-MASTER-SSOT-V2"
    data["stage_id"] = "SYNC_MAP_02E_R1_SEMANTIC_HARDENING"
    data["repository_scope"] = "BASS_ONLY"
    data["status"] = "PASS_CANDIDATE_LOCAL_REPLAY_REQUIRED"
    data["source_parent"] = {
        "pull_request": 99,
        "commit": EXPECTED_PARENT_HEAD,
        "superseded_registry_semantic_hash": EXPECTED_PARENT_REGISTRY_HASH,
    }
    data["canonicalization"] = {
        "algorithm": (
            "UTF-8 compact JSON with recursively lexicographically sorted object keys"
        ),
        "semantic_projection_drops": sorted(SEMANTIC_DROP_KEYS),
        "hash": "SHA-256 lowercase hexadecimal",
    }
    data["conventions"].update(
        {
            "angular_multipole_symbol": "ell",
            "ray_length_symbol": "s=c*t",
            "normal_acceleration_symbol": "A_normal^a",
            "bianchi_structure_vector_symbol": "aB^a",
        }
    )

    records = by_formula_id(data)
    patch_doppler(records["BASS.FRAME.DOPPLER_FACTOR.001"])
    patch_aberration(records["BASS.FRAME.ABERRATED_DIRECTION.001"])
    patch_blackbody(records["BASS.FRAME.BLACKBODY_TEMPERATURE_PULLBACK.001"])
    patch_solid_angle(records["BASS.FRAME.SOLID_ANGLE_JACOBIAN.001"])
    patch_direction_flow(records["BASS.PHOTON.DIRECTION_FLOW.001"])
    patch_energy_drift(records["BASS.PHOTON.ENERGY_DRIFT.001"])

    data["formulas"] = [records[formula_id] for formula_id in FORMULA_IDS]
    data["formula_count"] = len(FORMULA_IDS)
    rebuild_edges(data)
    rebuild_hashes(data)

    data.pop("consumer_bindings", None)
    data["declared_consumer_targets"] = {
        row["formula_id"]: row["declared_consumer_targets"]
        for row in data["formulas"]
    }
    data["removed_legacy_fields"] = ["consumer_bindings"]
    data["hardening_obligations"] = {
        "zero_boost_regularization": "gamma^2/(gamma+1)",
        "blackbody_base_map_dependency": (
            "BASS.FRAME.ABERRATED_DIRECTION.001"
        ),
        "blackbody_fiber_weight_dependency": "BASS.FRAME.DOPPLER_FACTOR.001",
        "photon_ray_parameter": "s=c*t",
        "geodesic_normal_specialization": "A_normal^a=0",
        "screen_transport": "EXCLUDED_NEXT_BASS_NODE",
    }
    data["coverage"] = {
        "included": [
            "BASS-owned finite local-observer Doppler and aberration theorem",
            "BASS-owned blackbody weighted pullback",
            "BASS-owned solid-angle Jacobian",
            "BASS-owned homogeneous photon energy and direction characteristics",
        ],
        "excluded": [
            "REC, REI, or HTT source modification",
            "cross-repository software parity",
            "BASS background numerical provider",
            "global matter-frame tilt",
            "finite-electron-tilt collision",
            "polarization screen-basis transport",
            "mask beam estimator and likelihood runtime",
        ],
    }
    data["next_stage"] = {
        "node": "SYNC_MAP_02F_R2_NORMAL_ANCESTRY_RECOMPOSITION",
        "status": "BLOCKED_UNTIL_LOCAL_REPLAY_AND_READBACK",
    }
    data["claim_boundary"] = [
        "BASS_OWNER_FORMULA_HARDENING_ONLY",
        "NO_CROSS_REPOSITORY_SOURCE_MUTATION",
        "NO_CONSUMER_PARITY",
        "NO_BACKGROUND_PROVIDER",
        "NO_GLOBAL_TILT",
        "NO_SCREEN_TRANSPORT",
        "NO_NUMERICAL_OR_SCIENCE_PROMOTION",
    ]
    data.pop("wolfram_oracle", None)
    data.pop("scispace_role_lock", None)
    return data


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    parent_bytes = args.input.read_bytes()
    parent = json.loads(parent_bytes.decode("utf-8"))
    output = build(parent)
    output_bytes = json.dumps(
        output, ensure_ascii=False, indent=2, sort_keys=True
    ).encode("utf-8") + b"\n"

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(output_bytes)

    receipt = {
        "schema_version": "1.0.0",
        "stage_id": "SYNC_MAP_02E_R1_LOCAL_BUILD_RECEIPT",
        "repository_scope": "BASS_ONLY",
        "parent_path": args.input.as_posix(),
        "parent_sha256": sha256_bytes(parent_bytes),
        "parent_registry_semantic_hash": EXPECTED_PARENT_REGISTRY_HASH,
        "output_path": args.output.as_posix(),
        "output_sha256": sha256_bytes(output_bytes),
        "output_registry_semantic_hash": output["registry_semantic_hash"],
        "formula_semantic_hashes": {
            row["formula_id"]: row["semantic_hash"]
            for row in output["formulas"]
        },
        "formula_count": output["formula_count"],
        "status": "BUILT_NOT_YET_WOLFRAM_REPLAYED",
    }
    args.receipt.write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(receipt, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
