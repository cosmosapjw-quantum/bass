#!/usr/bin/env python3
"""Fail-closed verifier for the BASS BG-02 implementation registry/source."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

EXPECTED_PARENT = "80d271cc528e1a0ffa813ecd3e3fb7610f3fa755"
EXPECTED_TREE = "3fd8818938eaa0988988c6927cff799455a7a31d"
EXPECTED_DESIGN = "ef6d51aad709555737617e2021ba50c553c90b6c"
EXPECTED_IDS = [
    "BASS.BG.EINSTEIN_RESIDUAL.001",
    "BASS.BG.HAMILTONIAN_PROJECTION.001",
    "BASS.BG.MOMENTUM_PROJECTION.001",
    "BASS.BG.SPATIAL_TRACE_PROJECTION.001",
    "BASS.BG.SPATIAL_PSTF_PROJECTION.001",
    "BASS.BG.HAMILTONIAN_HSIGMA.001",
    "BASS.BG.EXPANSION_RATE_RAW.001",
    "BASS.BG.EXPANSION_RATE_ADM.001",
    "BASS.BG.EXPANSION_RATE_RAYCHAUDHURI.001",
    "BASS.BG.SHEAR_RATE_LIE.001",
    "BASS.BG.SHEAR_RATE_PROJECTED.001",
    "BASS.BG.HOMOGENEOUS_SCALAR_CURVATURE.001",
    "BASS.BG.HOMOGENEOUS_MOMENTUM.001",
    "BASS.BG.EXCEPTIONAL_VI_MOMENTUM_CARRIER.001",
]
EXTERNAL_IDS = {
    "BASS.GEO.CONTRACTED_GAUSS.001",
    "BASS.GEO.EXTRINSIC_CURVATURE_SHEAR_SPLIT.001",
    "BASS.GEO.SPATIAL_SCALAR.001",
    "BASS.GEO.CODAZZI.001",
    "BASS.GEO.NORMAL_ACCELERATION.001",
    "BASS.GEO.NORMAL_DERIVATIVE_DECOMPOSITION.001",
    "BASS.GEO.SPATIAL_RICCI.001",
    "BASS.GEO.LEVI_CIVITA_CONNECTION.001",
    "BASS.GEO.STRUCTURE_CONSTANTS.001",
}
PUBLIC_APIS = [
    "EinsteinResidualTensor",
    "EinsteinProjectionRegistry",
    "HamiltonianProjection",
    "MomentumProjection",
    "SpatialTraceProjection",
    "SpatialPSTFProjection",
    "SpatialTraceRate",
    "ADMTraceRate",
    "RaychaudhuriRate",
    "ShearLieRate",
    "ShearProjectedRate",
]
FORBIDDEN_CLAIMS = {
    "CONSTRAINT_PROPAGATION_VERIFIED",
    "BACKGROUND_NUMERICAL_EVOLUTION",
    "PROVIDER_ADMISSION",
    "SCIENCE_VALIDITY",
    "PASS_RF04",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def verify(registry: dict[str, Any], source: str, init_source: str) -> dict[str, Any]:
    require(registry.get("schema_version") == "1.0.0", "schema mismatch")
    require(registry.get("repository_scope") == "BASS_ONLY", "scope mismatch")
    require(registry.get("scientific_parent_commit") == EXPECTED_PARENT, "parent mismatch")
    require(registry.get("scientific_parent_tree") == EXPECTED_TREE, "parent tree mismatch")
    require(registry.get("design_authority_commit") == EXPECTED_DESIGN, "design mismatch")

    rows = registry.get("formulas", [])
    ids = [row.get("formula_id") for row in rows]
    require(registry.get("formula_count") == 14, "formula count mismatch")
    require(ids == EXPECTED_IDS, "formula ID/order mismatch")
    require(len(ids) == len(set(ids)), "duplicate formula ID")
    require(all(row.get("dimension") == "L^-2" for row in rows), "dimension mismatch")

    known = set(ids) | EXTERNAL_IDS
    dangling = sorted({dep for row in rows for dep in row.get("depends_on", []) if dep not in known})
    require(not dangling, f"dangling dependencies: {dangling}")
    require(all(str(row.get("implementation_api", "")).startswith("BASS`Background`") for row in rows), "implementation API mismatch")

    require(source.count("G_ab + Lambda g_ab - kappa_G T_ab") == 1, "single residual authority mismatch")
    require("Hres -> 0" not in source, "Hamiltonian surface projection detected")
    require(not re.search(r"(?<![A-Za-z])kappa(?![A-Za-zG_])", source), "bare GR coupling name detected")
    require("Koszul" not in source, "second connection derivation marker detected")
    require("ONFScalarCurvature" in source or "ConnectionToLockedGammaOrder" in source, "locked curvature route missing")
    require(init_source.count('"Background", "EinsteinProjection.wl"') == 1, "loader multiplicity mismatch")
    require(all(f"{api}::usage" in source for api in PUBLIC_APIS), "public API missing")

    guards = registry.get("connection_order_guards", {})
    require(guards.get("Bianchi_V") == {"locked": -6, "wrong": 4, "diagnostic_power": "REQUIRED"}, "Bianchi V guard mismatch")
    require(guards.get("Bianchi_II") == {"locked": -0.5, "wrong": 1.5, "diagnostic_power": "REQUIRED"}, "Bianchi II guard mismatch")
    require(guards.get("I_IX_ONLY_IS_INSUFFICIENT") is True, "insufficient witness firewall missing")

    require(registry.get("state_projection_policy", {}).get("projects_Hres_to_zero") is False, "off-shell policy weakened")
    require(FORBIDDEN_CLAIMS.issubset(set(registry.get("withheld_claims", []))), "claim firewall weakened")
    require(registry.get("required_native_replay", {}).get("status") == "PENDING", "native replay falsely promoted")

    return {
        "schema_version": "1.0.0",
        "stage_id": "BG_02_EINSTEIN_PROJECTION_SOURCE_VERIFIER",
        "repository_scope": "BASS_ONLY",
        "formula_count": len(rows),
        "dependency_edges": sum(len(row.get("depends_on", [])) for row in rows),
        "public_api_count": len(PUBLIC_APIS),
        "native_xact_status": "PENDING",
        "status": "PASS_SOURCE_GREEN_CANDIDATE",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("docs/bass_master_ssot_v2/BG_02_IMPLEMENTATION/BG_02_IMPLEMENTATION_REGISTRY.json"))
    parser.add_argument("--source", type=Path, default=Path("wolfram/BASS/Kernel/Background/EinsteinProjection.wl"))
    parser.add_argument("--init", type=Path, default=Path("wolfram/BASS/Kernel/init.wl"))
    args = parser.parse_args()
    try:
        registry = json.loads(args.input.read_text(encoding="utf-8"))
        result = verify(
            registry,
            args.source.read_text(encoding="utf-8"),
            args.init.read_text(encoding="utf-8"),
        )
    except (OSError, json.JSONDecodeError, ValueError, TypeError, KeyError) as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, sort_keys=True))
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
