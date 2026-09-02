#!/usr/bin/env python3
"""Fail-closed structural verifier for the four-repository DAG projection.

This verifier checks governance structure only.  It does not establish formula
semantic equivalence, provider admission, numerical parity, or science validity.
"""
from __future__ import annotations

from collections import Counter, defaultdict, deque
import json
from pathlib import Path
import sys

EXPECTED_REPOS = {
    "cosmosapjw-quantum/bass",
    "cosmosapjw-quantum/rec_bianchi",
    "cosmosapjw-quantum/rei_bianchi",
    "cosmosapjw-quantum/htt_base",
}
EXPECTED_FRONTIER = {
    "FED.MAP02C_REI",
    "BASS.BG02_IMPLEMENT",
    "REC.FACE_SOURCE_AUTHORITY",
    "REI.RUNTIME_BRIDGE_REPAIR",
    "HTT.WU011_TASK7C",
    "HTT.PR315_DETERMINISM",
}
REQUIRED_CLAIM_BOUNDARIES = {
    "NO_PASS_RF04",
    "NO_PASS_REC_PHYSICAL_SPLIT",
    "NO_PASS_FIRST_CANONICAL_INTERVAL",
    "NO_EMPIRICAL_BETA_OR_BOOST_SUBTRACTION",
}


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def main() -> int:
    if len(sys.argv) > 2:
        fail("usage: verify_four_repo_dag_reconciliation.py [DAG_JSON]")
    path = Path(sys.argv[1]) if len(sys.argv) == 2 else Path(
        "docs/bianchi_program/federation/FOUR_REPO_DAG_RECONCILIATION_20260902_R1.json"
    )
    data = json.loads(path.read_text(encoding="utf-8"))

    scope = data.get("scope", {})
    if set(scope.get("repositories", [])) != EXPECTED_REPOS:
        fail("repository set is not the exact four-repository federation")
    for forbidden_true in (
        "automatic_semantic_winner_selection",
        "official_jira_link_mutation",
        "workflow_transition",
        "merge_or_ready_transition",
        "science_claim_promotion",
    ):
        if scope.get(forbidden_true) is not False:
            fail(f"{forbidden_true} must be false")

    nodes = data.get("nodes")
    edges = data.get("edges")
    if not isinstance(nodes, list) or not nodes:
        fail("nodes must be a nonempty list")
    if not isinstance(edges, list) or not edges:
        fail("edges must be a nonempty list")

    node_ids = [node.get("id") for node in nodes]
    duplicate_ids = sorted(key for key, count in Counter(node_ids).items() if count > 1)
    if duplicate_ids:
        fail(f"duplicate node IDs: {duplicate_ids}")
    if any(not isinstance(node_id, str) or not node_id for node_id in node_ids):
        fail("every node requires a nonempty string ID")
    node_set = set(node_ids)

    adjacency: dict[str, list[str]] = defaultdict(list)
    indegree = {node_id: 0 for node_id in node_ids}
    for index, edge in enumerate(edges):
        source = edge.get("from")
        target = edge.get("to")
        if source not in node_set or target not in node_set:
            fail(f"edge {index} has foreign endpoint: {source!r}->{target!r}")
        if source == target:
            fail(f"edge {index} is a self-cycle")
        adjacency[source].append(target)
        indegree[target] += 1

    queue = deque(sorted(node for node, degree in indegree.items() if degree == 0))
    visited: list[str] = []
    while queue:
        source = queue.popleft()
        visited.append(source)
        for target in adjacency[source]:
            indegree[target] -= 1
            if indegree[target] == 0:
                queue.append(target)
    if len(visited) != len(node_set):
        cyclic = sorted(node for node, degree in indegree.items() if degree > 0)
        fail(f"DAG contains a cycle involving: {cyclic}")

    frontier = set(data.get("next_parallel_frontier", []))
    if frontier != EXPECTED_FRONTIER:
        fail(f"unexpected parallel frontier: {sorted(frontier)}")
    if not frontier <= node_set:
        fail("parallel frontier contains foreign nodes")

    claims = set(data.get("claim_boundaries", []))
    missing_claims = sorted(REQUIRED_CLAIM_BOUNDARIES - claims)
    if missing_claims:
        fail(f"missing claim boundaries: {missing_claims}")

    # Load-bearing interaction checks.
    edge_triplets = {
        (edge["from"], edge["to"], edge.get("kind", "")) for edge in edges
    }
    required_edges = {
        ("FED.MAP02A", "FED.MAP02B_REC", "requires_execution"),
        ("FED.MAP02A", "FED.MAP02C_REI", "requires_execution"),
        ("FED.MAP02C_REI", "FED.SHARED_FRAME_PHOTON_EXPORT", "requires_execution"),
        ("REC.PROVIDER_EXPORT", "REI.PROVIDER_EXPORT", "promotion_gate"),
        ("REC.PROVIDER_EXPORT", "BASS.COUPLED_HISTORY", "requires_execution"),
        ("REI.PROVIDER_EXPORT", "BASS.COUPLED_HISTORY", "requires_execution"),
        ("BASS.HTT_EXPORT_BUNDLE", "HTT.BASS_BUNDLE_CONSUMER", "producer_consumer"),
        ("HTT.PR315_DETERMINISM", "HTT.WU011_RELEASE_GATE", "release_gate"),
    }
    missing_edges = sorted(required_edges - edge_triplets)
    if missing_edges:
        fail(f"missing load-bearing edges: {missing_edges}")

    # Prohibit the old producer/consumer conflation and coarse execution blocks.
    if "INT.HTT_BACKGROUND_EXPORT" in node_set:
        fail("legacy conflated HTT export node is forbidden")
    forbidden_edges = {
        ("REC.PROVIDER_EXPORT", "BASS.BG02_IMPLEMENT"),
        ("REI.PROVIDER_EXPORT", "BASS.BG02_IMPLEMENT"),
        ("HTT.PR315_DETERMINISM", "HTT.WU011_TASK7C"),
    }
    present_pairs = {(edge["from"], edge["to"]) for edge in edges}
    bad = sorted(forbidden_edges & present_pairs)
    if bad:
        fail(f"overbroad blocking edges present: {bad}")

    lane_counts = Counter(node.get("lane") for node in nodes)
    print(
        json.dumps(
            {
                "status": "PASS",
                "node_count": len(nodes),
                "edge_count": len(edges),
                "topological_coverage": len(visited),
                "lane_counts": dict(sorted(lane_counts.items())),
                "parallel_frontier": sorted(frontier),
                "claim_effect": "NONE",
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
