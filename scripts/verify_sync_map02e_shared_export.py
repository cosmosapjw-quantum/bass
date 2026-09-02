#!/usr/bin/env python3
"""Fail-closed verifier for the SYNC-MAP-02E six-formula export.

This validates exact formula identity, convention-sensitive signatures,
dependency closure, scope firewalls, and semantic hashes.  It does not prove
consumer implementation parity, numerical accuracy, provider admission, or
scientific validity.
"""
from __future__ import annotations

from collections import defaultdict, deque
import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
EXPORT_PATH = (
    ROOT
    / "docs"
    / "bass_master_ssot_v2"
    / "SYNC_MAP_02E"
    / "BASS_SHARED_FRAME_PHOTON_EXPORT.json"
)

EXPECTED_FORMULA_IDS = {
    "BASS.FRAME.ABERRATED_DIRECTION.001",
    "BASS.FRAME.BLACKBODY_TEMPERATURE_PULLBACK.001",
    "BASS.FRAME.DOPPLER_FACTOR.001",
    "BASS.FRAME.SOLID_ANGLE_JACOBIAN.001",
    "BASS.PHOTON.DIRECTION_FLOW.001",
    "BASS.PHOTON.ENERGY_DRIFT.001",
}
EXPECTED_PREDECESSORS = {
    "sync_map_02b": "f1eab555b42ebfaa3aa9d4021e097750aa0dfd96",
    "sync_map_02c": "9e39e2468b9efec05f33b9945de02fe2c8c6a66d",
    "sync_map_02d": "7006aaab27834af37d5034f8f1e50943fe85c0f3",
}
EXPECTED_INTERNAL_EDGES = {
    (
        "BASS.FRAME.ABERRATED_DIRECTION.001",
        "BASS.FRAME.DOPPLER_FACTOR.001",
        "depends_on",
    ),
    (
        "BASS.FRAME.SOLID_ANGLE_JACOBIAN.001",
        "BASS.FRAME.DOPPLER_FACTOR.001",
        "depends_on",
    ),
    (
        "BASS.FRAME.BLACKBODY_TEMPERATURE_PULLBACK.001",
        "BASS.FRAME.DOPPLER_FACTOR.001",
        "depends_on",
    ),
    (
        "BASS.FRAME.BLACKBODY_TEMPERATURE_PULLBACK.001",
        "BASS.FRAME.ABERRATED_DIRECTION.001",
        "depends_on",
    ),
}
EXPECTED_EXTERNAL_EDGES = {
    (
        "BASS.PHOTON.ENERGY_DRIFT.001",
        "BASS.GEO.EXTRINSIC_CURVATURE_SHEAR_SPLIT.001",
        "depends_on",
    ),
    (
        "BASS.PHOTON.DIRECTION_FLOW.001",
        "BASS.GEO.STRUCTURE_CONSTANTS.001",
        "depends_on",
    ),
    (
        "BASS.PHOTON.DIRECTION_FLOW.001",
        "BASS.GEO.EXTRINSIC_CURVATURE_SHEAR_SPLIT.001",
        "depends_on",
    ),
}
ALLOWED_CONSUMER_MODES = [
    "PINNED_IMPORT",
    "INDEPENDENT_ORACLE",
    "ADAPTER_SPECIALIZATION",
]
FORBIDDEN_INCLUDED_SCOPE = {
    "finite electron tilt",
    "global matter tilt",
    "recombination",
    "reionization",
    "numerical solver",
    "hierarchy truncation",
    "likelihood",
    "inference",
}


class ValidationError(ValueError):
    """A typed contract failure for this bounded export."""


def _fail(message: str) -> None:
    raise ValidationError(message)


def load_export(path: Path = EXPORT_PATH) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValidationError(f"cannot load shared export: {exc}") from exc
    if not isinstance(value, dict):
        _fail("shared export must be a JSON object")
    return value


def _canonical_json(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("ascii")


def _semantic_projection(ir: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in ir.items()
        if key not in {"schema_version", "formula_id", "authority_theorem", "provenance"}
    }


def _semantic_hash(ir: dict[str, Any]) -> str:
    return hashlib.sha256(_canonical_json(_semantic_projection(ir))).hexdigest()


def _contains_float(value: object) -> bool:
    if isinstance(value, float):
        return True
    if isinstance(value, dict):
        return any(_contains_float(key) or _contains_float(child) for key, child in value.items())
    if isinstance(value, (list, tuple)):
        return any(_contains_float(child) for child in value)
    return False


def _exact_integer_ast(value: object, expected: int) -> bool:
    return value == {"type": "integer", "value": expected}


def _edge_tuple(edge: object) -> tuple[str, str, str]:
    if not isinstance(edge, dict) or set(edge) != {"from", "to", "relation"}:
        _fail("dependency edge must have closed from/to/relation keys")
    source = edge["from"]
    target = edge["to"]
    relation = edge["relation"]
    if not all(isinstance(item, str) and item for item in (source, target, relation)):
        _fail("dependency edge values must be nonempty strings")
    return source, target, relation


def _require_acyclic(internal_edges: list[dict[str, Any]]) -> None:
    adjacency: dict[str, list[str]] = defaultdict(list)
    indegree = {formula_id: 0 for formula_id in EXPECTED_FORMULA_IDS}
    for raw_edge in internal_edges:
        source, target, relation = _edge_tuple(raw_edge)
        if relation != "depends_on":
            _fail("internal dependency relation must be depends_on")
        if source not in indegree or target not in indegree:
            _fail("internal dependency has a foreign endpoint")
        adjacency[source].append(target)
        indegree[target] += 1
    queue = deque(sorted(node for node, degree in indegree.items() if degree == 0))
    visited = 0
    while queue:
        node = queue.popleft()
        visited += 1
        for child in adjacency[node]:
            indegree[child] -= 1
            if indegree[child] == 0:
                queue.append(child)
    if visited != len(indegree):
        _fail("internal dependency graph contains a cycle")


def _formula_map(formulas: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for formula in formulas:
        if not isinstance(formula, dict):
            _fail("formula records must be objects")
        formula_id = formula.get("formula_id")
        if not isinstance(formula_id, str) or not formula_id:
            _fail("formula record has no formula_id")
        if formula_id in result:
            _fail("six-formula union contains a duplicate formula_id")
        result[formula_id] = formula
    return result


def _require_formula_signatures(formulas: dict[str, dict[str, Any]]) -> None:
    def terms(formula_id: str) -> list[dict[str, Any]]:
        ir = formulas[formula_id].get("equation_ir")
        if not isinstance(ir, dict):
            _fail(f"{formula_id} has no equation_ir")
        value = ir.get("terms")
        if not isinstance(value, list):
            _fail(f"{formula_id} terms must be a list")
        return value

    doppler = terms("BASS.FRAME.DOPPLER_FACTOR.001")
    if len(doppler) != 1 or doppler[0].get("input") != "gamma*(1+beta_dot_n_sky)":
        _fail("Doppler signature does not use the outward-sky plus sign")
    if not _exact_integer_ast(doppler[0].get("coefficient"), 1):
        _fail("Doppler signature coefficient is not exact +1")

    aberration = terms("BASS.FRAME.ABERRATED_DIRECTION.001")
    expected_aberration = (
        "[n_sky+(gamma+gamma^2*beta_dot_n_sky/(gamma+1))*beta]"
        "/doppler_factor"
    )
    if len(aberration) != 1 or aberration[0].get("input") != expected_aberration:
        _fail("aberrated-direction signature is not the regular outward-sky map")

    solid_angle = terms("BASS.FRAME.SOLID_ANGLE_JACOBIAN.001")
    if len(solid_angle) != 1 or solid_angle[0].get("input") != "doppler_factor^(-2)*dOmega":
        _fail("solid-angle signature must carry Doppler power -2")

    temperature = terms("BASS.FRAME.BLACKBODY_TEMPERATURE_PULLBACK.001")
    if (
        len(temperature) != 1
        or temperature[0].get("input")
        != "doppler_factor*temperature(n_sky_of_n_sky_tilde)"
    ):
        _fail("temperature-pullback signature must have Doppler weight +1")

    energy = terms("BASS.PHOTON.ENERGY_DRIFT.001")
    if (
        len(energy) != 2
        or [term.get("input") for term in energy]
        != ["H_geom", "sigma_ab*e^a*e^b"]
        or not all(_exact_integer_ast(term.get("coefficient"), -1) for term in energy)
    ):
        _fail("energy-drift signature must be -H_geom-sigma_ab e^a e^b")

    direction = terms("BASS.PHOTON.DIRECTION_FLOW.001")
    expected_inputs = [
        "(sigma_bc*e^b*e^c+aB_b*e^b)*e^a",
        "sigma^a_b*e^b",
        "aB^a",
        "epsilon^a_bc*Omega_triad^b*e^c",
        "epsilon^a_bc*e^b*nB^c_d*e^d",
    ]
    expected_coefficients = [1, -1, -1, 1, -1]
    if (
        len(direction) != 5
        or [term.get("input") for term in direction] != expected_inputs
        or not all(
            _exact_integer_ast(term.get("coefficient"), coefficient)
            for term, coefficient in zip(direction, expected_coefficients, strict=True)
        )
    ):
        _fail("direction-flow signature is missing the radial compensator or has sign drift")


def validate_export(export: dict[str, Any]) -> dict[str, Any]:
    if _contains_float(export):
        _fail("inexact floating-point values are forbidden in formula authority")
    if export.get("schema_version") != "1.0.0":
        _fail("wrong schema version")
    if export.get("stage_id") != "SYNC_MAP_02E_SHARED_FRAME_PHOTON_EXPORT":
        _fail("wrong stage ID")
    if export.get("owner") != "bass":
        _fail("shared export owner must be bass")

    predecessors = export.get("predecessors")
    if not isinstance(predecessors, dict):
        _fail("predecessors must be an object")
    if predecessors.get("sync_map_02d", {}).get("commit") == (
        "06aa29f78c26bcafeb60d85b719a4d3aa5c4c2e8"
    ):
        _fail("stale HTT predecessor is forbidden")
    for key, expected_commit in EXPECTED_PREDECESSORS.items():
        record = predecessors.get(key)
        if not isinstance(record, dict) or record.get("commit") != expected_commit:
            _fail(f"stale or missing predecessor: {key}")

    formulas = export.get("formulas")
    if not isinstance(formulas, list) or len(formulas) != 6:
        _fail("six-formula union is required")
    mapped = _formula_map(formulas)
    if set(mapped) != EXPECTED_FORMULA_IDS:
        _fail("six-formula union has the wrong formula IDs")

    _require_formula_signatures(mapped)

    internal_edges = export.get("internal_dependency_edges")
    external_edges = export.get("external_dependency_edges")
    if not isinstance(internal_edges, list):
        _fail("internal dependency list is missing")
    if not isinstance(external_edges, list):
        _fail("external dependency list is missing")
    _require_acyclic(internal_edges)
    actual_internal = {_edge_tuple(edge) for edge in internal_edges}
    actual_external = {_edge_tuple(edge) for edge in external_edges}
    if actual_internal != EXPECTED_INTERNAL_EDGES:
        _fail("internal dependency set does not match the six-formula contract")
    if actual_external != EXPECTED_EXTERNAL_EDGES:
        _fail("external dependency set does not match the geometry contract")

    dependencies_by_formula: dict[str, set[str]] = defaultdict(set)
    for source, target, _ in actual_internal | actual_external:
        dependencies_by_formula[source].add(target)

    for formula_id, formula in mapped.items():
        if formula.get("owner") != "bass":
            _fail("formula owner mismatch")
        if formula.get("authority_effect") != "AUTHORITATIVE_DERIVATION":
            _fail("formula authority effect mismatch")
        if formula.get("status") != "SYMBOLIC_VERIFIED_FORMULA_EXPORT":
            _fail("formula status mismatch")
        if formula.get("allowed_consumer_modes") != ALLOWED_CONSUMER_MODES:
            _fail("consumer-mode contract mismatch")
        if set(formula.get("dependencies", [])) != dependencies_by_formula[formula_id]:
            _fail("formula dependency projection mismatch")
        ir = formula.get("equation_ir")
        if not isinstance(ir, dict) or ir.get("formula_id") != formula_id:
            _fail("EquationIR formula identity mismatch")
        required_ir = {
            "schema_version",
            "formula_id",
            "authority_theorem",
            "target",
            "free_indices",
            "representation",
            "assumptions",
            "domain",
            "dimensions",
            "terms",
            "structural_zero_rules",
            "branch_predicates",
            "known_limits",
            "provenance",
        }
        if set(ir) != required_ir:
            _fail("EquationIR keys are not closed")
        for term in ir["terms"]:
            if not isinstance(term, dict) or set(term) != {"input", "coefficient"}:
                _fail("EquationIR term keys are not closed")
            coefficient = term["coefficient"]
            if not (
                isinstance(coefficient, dict)
                and set(coefficient) == {"type", "value"}
                and coefficient["type"] == "integer"
                and isinstance(coefficient["value"], int)
                and not isinstance(coefficient["value"], bool)
            ):
                _fail("EquationIR coefficient is not an exact integer AST")
        observed_hash = formula.get("semantic_hash")
        if observed_hash != _semantic_hash(ir):
            _fail("semantic hash drift detected")

    coverage = export.get("coverage")
    if not isinstance(coverage, dict):
        _fail("coverage is missing")
    included = coverage.get("included")
    if not isinstance(included, list) or not all(isinstance(item, str) for item in included):
        _fail("coverage included list is invalid")
    included_text = "\n".join(item.lower() for item in included)
    if any(forbidden in included_text for forbidden in FORBIDDEN_INCLUDED_SCOPE):
        _fail("scope firewall forbids downstream physics in the shared formula export")

    if export.get("claim_boundary") != (
        "SIX_FORMULA_EQUATIONIR_EXPORT_ONLY_NO_CONSUMER_EQUIVALENCE_"
        "FINITE_TILT_GLOBAL_TILT_BACKGROUND_PROVIDER_OR_SCIENCE_PROMOTION"
    ):
        _fail("claim boundary mismatch")

    return {
        "status": "PASS",
        "formula_count": len(formulas),
        "internal_dependency_edges": len(internal_edges),
        "external_dependency_edges": len(external_edges),
        "semantic_hashes": {
            formula_id: mapped[formula_id]["semantic_hash"]
            for formula_id in sorted(mapped)
        },
        "claim_effect": "NONE",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("path", nargs="?", type=Path, default=EXPORT_PATH)
    args = parser.parse_args()
    try:
        report = validate_export(load_export(args.path))
    except ValidationError as exc:
        if args.as_json:
            print(json.dumps({"status": "FAIL", "error": str(exc)}, sort_keys=True))
        else:
            print(f"FAIL: {exc}")
        return 1
    if args.as_json:
        print(json.dumps(report, sort_keys=True))
    else:
        print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
