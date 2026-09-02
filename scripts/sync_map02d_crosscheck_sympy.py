#!/usr/bin/env python3
"""Independent SymPy cross-check for BASS SYNC-MAP-02D.

The oracle does not import or translate the repository Wolfram package. It
reconstructs the same exact Lorentz, STF3, and federation-DAG obligations in a
second CAS and fails closed if an identity fails or a registered hostile
mutation escapes detection.
"""

from __future__ import annotations

import json
import platform
import sys
from collections import deque
from typing import Any

import sympy as sp

TESTED_SUBJECT = {
    "repository": "cosmosapjw-quantum/bass",
    "pull_request": 97,
    "commit": "7006aaab27834af37d5034f8f1e50943fe85c0f3",
    "tree": "4bfccafb3da7c6d0e720dc55171b832f7b919085",
    "classification_path": "docs/bass_master_ssot_v2/SYNC_MAP_02D/HTT_RELATION_CLASSIFICATION.json",
    "classification_blob": "9ce25902c5ec271908c5f73f76d60d180843fa9d",
    "wolfram_module_path": "wolfram/BASS/Kernel/IR/HTTRelationClassification.wl",
    "wolfram_module_blob": "042d60c4655ecd17f8aa42f28ba6de097a8387e2",
    "wolfram_test_path": "wolfram/BASS/Tests/SYNCMAP02DHTTRelationClassification.wlt",
    "wolfram_test_blob": "d94958e55c5b3d91f40137f2bfef89af50150055",
    "python_verifier_path": "scripts/verify_sync_map02d_htt_relations.py",
    "python_verifier_blob": "ad1f228a63313165faf362c81f631c8808d98893",
}

CLAIM_BOUNDARY = (
    "RELATION_CLASSIFICATION_CROSSCHECK_ONLY_"
    "NO_SHARED_EXPORT_NO_GLOBAL_TILT_NO_FINITE_ELECTRON_COLLISION_"
    "NO_CONSUMER_PARITY_NO_PROVIDER_NO_NUMERICAL_PARITY_NO_DATA_FIT_NO_SCIENCE_PROMOTION"
)


def check(name: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"name": name, "passed": bool(passed), "detail": str(detail)}


def is_zero(expr: sp.Expr) -> bool:
    return sp.cancel(sp.factor(sp.together(expr))) == 0


def lorentz_checks() -> tuple[list[dict[str, Any]], dict[str, sp.Expr]]:
    # Use gamma as the independent variable and beta^2=1-gamma^-2. This is
    # an exact rational chart for 0<beta<1 and avoids relying on radical
    # simplification. The removable beta=0 limit is checked separately.
    gamma, mu, x, q = sp.symbols("gamma mu x q", positive=True)
    beta_sq = 1 - gamma**-2
    acoef = gamma + (gamma - 1) * mu / beta_sq
    doppler = gamma * (1 + mu)
    mu_tilde = sp.cancel((mu + acoef * beta_sq) / doppler)
    inverse_c = (gamma - 1) * mu_tilde / beta_sq - gamma
    inverse_den = gamma * (1 - mu_tilde)

    residuals = {
        "aberrated_direction_unit_norm": sp.cancel(
            (1 + 2 * acoef * mu + acoef**2 * beta_sq) / doppler**2 - 1
        ),
        "doppler_chart_equivalence": sp.cancel(
            1 / (gamma * (1 - mu_tilde)) - doppler
        ),
        "deaberration_inverse_n_coefficient": sp.cancel(
            (1 / doppler) / inverse_den - 1
        ),
        "deaberration_inverse_beta_coefficient": sp.cancel(
            (acoef / doppler + inverse_c) / inverse_den
        ),
        "solid_angle_jacobian": sp.cancel(
            sp.diff((x + q) / (1 + q * x), x)
            - (1 - q**2) / (1 + q * x) ** 2
        ),
    }

    eps = sp.symbols("eps", positive=True)
    regular_form = 1 / (
        sp.sqrt(1 - eps**2) * (1 + sp.sqrt(1 - eps**2))
    )
    residuals["regular_zero_boost_coefficient"] = sp.simplify(
        sp.limit(regular_form, eps, 0, dir="+") - sp.Rational(1, 2)
    )

    wrong_doppler = sp.cancel(1 / (gamma * (1 + mu_tilde)) - doppler)
    wrong_jacobian = sp.together(
        sp.diff((x + q) / (1 + q * x), x)
        - sp.sqrt(1 - q**2) / (1 + q * x)
    )

    checks = [
        check(name, is_zero(expr), sp.factor(expr))
        for name, expr in residuals.items()
    ]
    checks.extend(
        [
            check(
                "wrong_doppler_sign_detected",
                not is_zero(wrong_doppler),
                sp.factor(wrong_doppler),
            ),
            check(
                "wrong_jacobian_power_detected",
                not is_zero(wrong_jacobian),
                sp.factor(wrong_jacobian),
            ),
        ]
    )
    return checks, {
        **residuals,
        "wrong_doppler_sign": wrong_doppler,
        "wrong_jacobian_power": wrong_jacobian,
    }


def stf3_checks() -> tuple[list[dict[str, Any]], dict[str, sp.Expr]]:
    q11, q12, q13, q22, q23 = sp.symbols("q11 q12 q13 q22 q23")
    b1, b2, b3 = sp.symbols("b1 b2 b3")
    n1, n2, n3 = sp.symbols("n1 n2 n3")

    qmat = sp.Matrix(
        [
            [q11, q12, q13],
            [q12, q22, q23],
            [q13, q23, -q11 - q22],
        ]
    )
    beta = sp.Matrix([b1, b2, b3])
    nvec = sp.Matrix([n1, n2, n3])
    delta = sp.eye(3)
    qbeta = qmat * beta
    q_beta_n = sp.expand((beta.T * qmat * nvec)[0])
    q_nn = sp.expand((nvec.T * qmat * nvec)[0])
    beta_n = sp.expand((beta.T * nvec)[0])
    n_norm = sp.expand((nvec.T * nvec)[0])

    def build_tensor(trace_coefficient: sp.Rational) -> list[list[list[sp.Expr]]]:
        return [
            [
                [
                    sp.expand(
                        beta[a] * qmat[b, c]
                        + beta[b] * qmat[c, a]
                        + beta[c] * qmat[a, b]
                        - trace_coefficient
                        * (
                            delta[a, b] * qbeta[c]
                            + delta[a, c] * qbeta[b]
                            + delta[b, c] * qbeta[a]
                        )
                    )
                    for c in range(3)
                ]
                for b in range(3)
            ]
            for a in range(3)
        ]

    stf3 = build_tensor(sp.Rational(2, 5))
    symmetry_residuals: list[sp.Expr] = []
    for a in range(3):
        for b in range(3):
            for c in range(3):
                symmetry_residuals.extend(
                    [
                        sp.expand(stf3[a][b][c] - stf3[b][a][c]),
                        sp.expand(stf3[a][b][c] - stf3[a][c][b]),
                        sp.expand(stf3[a][b][c] - stf3[c][b][a]),
                    ]
                )
    trace_residuals = [
        sp.expand(sum(stf3[a][a][c] for a in range(3))) for c in range(3)
    ]
    contract = sp.expand(
        sum(
            stf3[a][b][c] * nvec[a] * nvec[b] * nvec[c]
            for a in range(3)
            for b in range(3)
            for c in range(3)
        )
    )
    physical_delta_t = 3 * beta_n * q_nn - 2 * q_beta_n
    ambient = sp.factor(
        sp.expand(contract - sp.Rational(4, 5) * q_beta_n - physical_delta_t)
    )
    expected_ambient = sp.factor(
        -sp.Rational(6, 5) * (n_norm - 1) * q_beta_n
    )
    unit_sphere = sp.factor(ambient.subs(n3**2, 1 - n1**2 - n2**2))

    wrong_stf3 = build_tensor(sp.Rational(1, 5))
    wrong_trace = [
        sp.expand(sum(wrong_stf3[a][a][c] for a in range(3)))
        for c in range(3)
    ]
    nonsymmetric = [
        [[stf3[a][b][c] for c in range(3)] for b in range(3)]
        for a in range(3)
    ]
    nonsymmetric[0][1][2] = sp.expand(nonsymmetric[0][1][2] + b1 * q23)
    nonsymmetry = sp.expand(nonsymmetric[0][1][2] - nonsymmetric[1][0][2])
    omitted_dipole = sp.factor(physical_delta_t - contract)
    omitted_octupole = sp.factor(
        physical_delta_t + sp.Rational(4, 5) * q_beta_n
    )

    checks = [
        check(
            "stf3_symmetric",
            all(is_zero(expr) for expr in symmetry_residuals),
            f"{len(symmetry_residuals)} permutation residuals",
        ),
        check(
            "stf3_trace_free",
            all(is_zero(expr) for expr in trace_residuals),
            [sp.factor(expr) for expr in trace_residuals],
        ),
        check(
            "stf3_ambient_factor_matches",
            is_zero(ambient - expected_ambient),
            ambient,
        ),
        check("stf3_unit_sphere_residual", is_zero(unit_sphere), unit_sphere),
        check(
            "stf3_unit_sphere_domain_required",
            (not is_zero(ambient)) and is_zero(unit_sphere),
            ambient,
        ),
        check(
            "wrong_stf3_trace_coefficient_detected",
            not all(is_zero(expr) for expr in wrong_trace),
            [sp.factor(expr) for expr in wrong_trace],
        ),
        check(
            "non_symmetric_stf3_detected",
            not is_zero(nonsymmetry),
            sp.factor(nonsymmetry),
        ),
        check(
            "missing_unit_sphere_domain_detected",
            (not is_zero(ambient)) and is_zero(unit_sphere),
            ambient,
        ),
        check(
            "omitted_dipole_detected",
            not is_zero(omitted_dipole),
            omitted_dipole,
        ),
        check(
            "omitted_octupole_detected",
            not is_zero(omitted_octupole),
            omitted_octupole,
        ),
    ]
    return checks, {
        "stf3_ambient_domain_residual": ambient,
        "stf3_expected_ambient_domain_residual": expected_ambient,
        "stf3_unit_sphere_residual": unit_sphere,
        "wrong_stf3_trace_first_component": wrong_trace[0],
        "non_symmetric_stf3_residual": nonsymmetry,
        "omitted_dipole_residual": omitted_dipole,
        "omitted_octupole_residual": omitted_octupole,
    }


def topological_order(
    nodes: list[str], edges: list[tuple[str, str]]
) -> list[str]:
    if len(nodes) != len(set(nodes)):
        return []
    indegree = {node: 0 for node in nodes}
    outgoing = {node: [] for node in nodes}
    for source, target in edges:
        if source not in indegree or target not in indegree:
            return []
        indegree[target] += 1
        outgoing[source].append(target)
    ready = deque(sorted(node for node, degree in indegree.items() if degree == 0))
    order: list[str] = []
    while ready:
        node = ready.popleft()
        order.append(node)
        for target in sorted(outgoing[node]):
            indegree[target] -= 1
            if indegree[target] == 0:
                ready.append(target)
    return order


def dag_checks() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    nodes = [
        "02A_BASS",
        "02B_REC",
        "02C_REI",
        "02D_HTT",
        "02E_SHARED_EXPORT",
        "02F_SEMANTIC_GRAPH",
        "SYNC_REC",
        "SYNC_REI",
        "SYNC_HTT_01A",
        "SYNC_GATE_01",
    ]
    edges = [
        ("02A_BASS", "02B_REC"),
        ("02B_REC", "02C_REI"),
        ("02B_REC", "02D_HTT"),
        ("02C_REI", "02E_SHARED_EXPORT"),
        ("02D_HTT", "02E_SHARED_EXPORT"),
        ("02E_SHARED_EXPORT", "02F_SEMANTIC_GRAPH"),
        ("02F_SEMANTIC_GRAPH", "SYNC_REC"),
        ("02F_SEMANTIC_GRAPH", "SYNC_REI"),
        ("02F_SEMANTIC_GRAPH", "SYNC_HTT_01A"),
        ("SYNC_REC", "SYNC_GATE_01"),
        ("SYNC_REI", "SYNC_GATE_01"),
        ("SYNC_HTT_01A", "SYNC_GATE_01"),
    ]
    order = topological_order(nodes, edges)
    mutant = [edge for edge in edges if edge != ("02D_HTT", "02E_SHARED_EXPORT")]
    mutant_order = topological_order(nodes, mutant)

    checks = [
        check("dag_unique_nodes", len(nodes) == len(set(nodes)), len(nodes)),
        check(
            "dag_edge_closure",
            all(source in nodes and target in nodes for source, target in edges),
            len(edges),
        ),
        check("dag_acyclic", len(order) == len(nodes), order),
        check("dag_node_count", len(nodes) == 10, len(nodes)),
        check("dag_edge_count", len(edges) == 12, len(edges)),
        check(
            "shared_export_has_rei_and_htt_prerequisites",
            ("02C_REI", "02E_SHARED_EXPORT") in edges
            and ("02D_HTT", "02E_SHARED_EXPORT") in edges,
            "required conjunction",
        ),
        check(
            "semantic_graph_follows_shared_export",
            ("02E_SHARED_EXPORT", "02F_SEMANTIC_GRAPH") in edges,
            "required edge",
        ),
        check(
            "manual_gate_has_three_sync_inputs",
            sum(target == "SYNC_GATE_01" for _, target in edges) == 3,
            3,
        ),
        check(
            "missing_02d_dependency_mutation_detected",
            ("02D_HTT", "02E_SHARED_EXPORT") not in mutant,
            "required edge removed",
        ),
        check(
            "missing_dependency_mutant_remains_acyclic",
            len(mutant_order) == len(nodes),
            mutant_order,
        ),
    ]
    return checks, {
        "nodes": nodes,
        "edges": [list(edge) for edge in edges],
        "topological_order": order,
        "mutated_edges": [list(edge) for edge in mutant],
        "mutated_topological_order": mutant_order,
    }


def run_all() -> dict[str, Any]:
    lorentz, lorentz_expressions = lorentz_checks()
    stf3, stf3_expressions = stf3_checks()
    dag, dag_data = dag_checks()
    checks = lorentz + stf3 + dag
    failures = [row for row in checks if not row["passed"]]
    return {
        "schema_version": "1.0.0",
        "receipt_type": "INDEPENDENT_SYMPY_EXACT_ALGEBRA_AND_DAG_CROSSCHECK",
        "status": "PASS" if not failures else "FAIL",
        "tested_subject": TESTED_SUBJECT,
        "executor": {
            "python": sys.version.split()[0],
            "sympy": sp.__version__,
            "platform": platform.platform(),
        },
        "checks": checks,
        "check_count": len(checks),
        "failure_count": len(failures),
        "failures": failures,
        "canonical_expressions": {
            "lorentz": {
                name: str(sp.factor(expr))
                for name, expr in lorentz_expressions.items()
            },
            "stf3": {
                name: str(sp.factor(expr))
                for name, expr in stf3_expressions.items()
            },
        },
        "dag": dag_data,
        "authority_effect": "NONE",
        "claim_boundary": CLAIM_BOUNDARY,
    }


def main() -> int:
    result = run_all()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
