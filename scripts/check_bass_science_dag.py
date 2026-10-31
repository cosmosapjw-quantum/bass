#!/usr/bin/env python3
"""Validate BASS 15-node physics portfolio scope counters (not scientific truth)."""
import copy
import json
import sys
from pathlib import Path

DEFAULT = Path(__file__).resolve().parents[1] / "docs/development/BASS_PHYSICS_UPPER_DAG_20261101.json"
SCOPES = {"SOURCE_MAPPED", "SCOPED_COMPLETE", "PARTIAL", "FUTURE", "DEFERRED", "COMPLETE_FULL"}

def check(dag):
    errors = []
    nodes = dag.get("nodes", [])
    by_id = {n.get("id"): n for n in nodes}
    upper = dag.get("upper", {})
    if dag.get("schema") != "bass.physics_upper.portfolio.v1":
        errors.append("wrong schema")
    if len(nodes) != 15 or len(by_id) != 15 or upper.get("total") != 15:
        errors.append("expected 15 unique original upper nodes")
    if sum(len(n.get("depends_on", [])) for n in nodes) != 21 or upper.get("historical_edge_count") != 21:
        errors.append("expected 21 original edges")
    if sum(bool(n.get("legacy_counted")) for n in nodes) != 9 or upper.get("historical_scoped_or_source_mapped_count") != 9:
        errors.append("expected qualified legacy 9/15")
    if upper.get("overall_physics_fraction") is not None:
        errors.append("full physical completion fraction cannot be manufactured")
    if upper.get("genuinely_full_physical_completed_count") is not None:
        errors.append("full completion has not been independently admitted in this snapshot")
    if "DO_NOT_REWRITE" not in dag.get("authorities", {}).get("root_DAG_json", ""):
        errors.append("root ACCEL02 identity lost")
    grey, black = set(), set()
    def visit(identifier):
        if identifier in grey:
            errors.append("cycle at " + identifier)
            return
        if identifier in black:
            return
        node = by_id.get(identifier)
        if node is None:
            errors.append("missing node " + str(identifier))
            return
        grey.add(identifier)
        admission = node.get("admission")
        if admission not in SCOPES:
            errors.append("unknown admission " + str(admission))
        for dependency in node.get("depends_on", []):
            parent = by_id.get(dependency)
            if parent is None:
                errors.append("missing dependency " + str(dependency))
                continue
            if admission == "COMPLETE_FULL" and parent.get("admission") != "COMPLETE_FULL":
                errors.append("false full closure " + identifier + " -> " + dependency)
            if admission == "SCOPED_COMPLETE" and parent.get("admission") in {"PARTIAL", "FUTURE", "DEFERRED"}:
                if not node.get("qualified_dependencies", {}).get(dependency):
                    errors.append("unqualified partial-parent scope " + identifier + " -> " + dependency)
            visit(dependency)
        grey.remove(identifier)
        black.add(identifier)
    for node in nodes:
        visit(node.get("id"))
    return errors

def self_test(dag):
    assert not check(dag), check(dag)
    bad = copy.deepcopy(dag)
    bad["nodes"][0]["depends_on"] = ["OB-1"]
    assert any("cycle" in e for e in check(bad))
    bad = copy.deepcopy(dag)
    bad["upper"]["historical_scoped_or_source_mapped_count"] = 10
    assert any("legacy" in e for e in check(bad))
    bad = copy.deepcopy(dag)
    next(n for n in bad["nodes"] if n["id"] == "KM-3").pop("qualified_dependencies")
    assert any("partial-parent" in e for e in check(bad))
    bad = copy.deepcopy(dag)
    next(n for n in bad["nodes"] if n["id"] == "KM-3")["admission"] = "COMPLETE_FULL"
    assert any("full closure" in e for e in check(bad))
    return 4

if __name__ == "__main__":
    file = Path(sys.argv[1]) if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else DEFAULT
    payload = json.loads(file.read_text(encoding="utf-8"))
    errors = check(payload)
    if errors:
        print("FAIL\n" + "\n".join(errors), file=sys.stderr)
        raise SystemExit(1)
    tests = self_test(payload) if "--self-test" in sys.argv else 0
    print(f"PASS: 15 upper nodes, 21 edges, scoped/source-mapped 9/15, negative controls {tests}/4; no scientific validation implied")
