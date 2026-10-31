#!/usr/bin/env python3
"""Small structural mission-mapping checker. Not a physics or central-DAG acceptance test."""
from __future__ import annotations
import copy
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
DAG = ROOT / "docs/development/REI_IGM_MISSION_DAG_20261101.json"
ALLOWED = {"SCOPED_ACCEPTED", "OPEN", "BLOCKED_UPSTREAM", "NOT_STARTED", "NOT_ADMITTED"}
REQUIRED = [
    "REI_R2C_LOCAL_MICROSTEP", "REI_FIRST_CANONICAL_INTERVAL",
    "REI_B2C2B_HISTORY", "REI_B2C2C_FRONT", "REI_B2D_MOMENT_CLOSURE",
    "REI_B2E_FLRW_INTERFACE", "BASS_REI_CLOCK_SOURCE_BRIDGE",
    "REI_C0_BIANCHI_I_COUPLING", "REI_DIRECTIONAL_TAU_VISIBILITY",
]

def validate(d: dict) -> None:
    if d.get("schema") != "bass.rei_igm_mission_dependency_overlay.v1":
        raise ValueError("wrong DAG schema")
    if d.get("scope", {}).get("program_id") != "REI_BIANCHI_IGM_PROGRAM_ONLY":
        raise ValueError("REI-specific policy cannot override BASS-native mission")
    if "BASS_NATIVE_TYPEII_MAINLINE" not in d.get("scope", {}).get("does_not_override", []):
        raise ValueError("BASS Type-II autonomy not preserved")
    auth = d["authority"]
    if auth["root_DAG_json"] != "UNTOUCHED_OTHER_ACCEL02_OWNER":
        raise ValueError("wrong authority for root DAG")
    if not re.fullmatch(r"[a-f0-9]{40}", auth["base_commit"]):
        raise ValueError("unlocked BASS head")
    if not re.fullmatch(r"[a-f0-9]{40}", auth["rei_main_commit"]):
        raise ValueError("unlocked REI main")
    p = d["progress_snapshots"]
    ce = p["bass_ce1"]
    if (ce["completed"], ce["total"], ce["edges"], ce["newly_completed_by_ce1al_to_ce1aq"]) != (9, 15, 21, 0):
        raise ValueError("unsubstantiated BASS canonical progress change")
    if ce["imported_to_rei"]:
        raise ValueError("unverified CE1->REI promotion")
    if p["rei_main_D0"]["completed_first_canonical_interval"]:
        raise ValueError("first REI interval not yet certified")
    if p["rei_f4_reported"]["relation"] != "NOT_RECONCILED_TO_REI_MAIN_D0_OR_BASS_CE1":
        raise ValueError("foreign DAG status conflated")
    nodes = d["nodes"]
    ids = [n["id"] for n in nodes]
    if len(ids) != len(set(ids)) or set(ids) != set(REQUIRED):
        raise ValueError("DAG node identities missing/duplicated")
    by_id = {n["id"]: n for n in nodes}
    for n in nodes:
        if n["status"] not in ALLOWED:
            raise ValueError("invalid node state")
        if not n["owner"] or not n["physical_deliverable"]:
            raise ValueError("missing owner/physical deliverable")
        for dep in n["depends_on"]:
            if dep not in by_id or dep == n["id"]:
                raise ValueError("unknown/self dependent node")
    visiting, visited = set(), set()
    def visit(i):
        if i in visiting:
            raise ValueError("cyclic mission DAG")
        if i in visited:
            return
        visiting.add(i)
        for j in by_id[i]["depends_on"]:
            visit(j)
        visiting.remove(i)
        visited.add(i)
    for i in ids:
        visit(i)
    route = d["critical_path_ids"]
    if route != [x for x in REQUIRED if x != "BASS_REI_CLOCK_SOURCE_BRIDGE"]:
        raise ValueError("central mission route changed")
    for first, second in zip(route, route[1:]):
        if first not in by_id[second]["depends_on"]:
            raise ValueError("unjustified shortcut to later mission node")
    if set(by_id["REI_C0_BIANCHI_I_COUPLING"]["depends_on"]) != {
        "REI_B2E_FLRW_INTERFACE", "BASS_REI_CLOCK_SOURCE_BRIDGE"
    }:
        raise ValueError("BASS-to-REI equivalence bridge bypassed")
    if d["next_action"]["default_id"] != "REI_FIRST_CANONICAL_INTERVAL":
        raise ValueError("scope drift to side project")
    if d["next_action"]["production"] != "HOLD" or d["next_action"]["merge"] != "HOLD" or d["next_action"]["auto_next"] is not False:
        raise ValueError("unauthorized production/merge/auto-next")
    if any(item["accepted_upstream"] or item["canonical_delta"] != 0
           for item in d["auxiliary_lanes"] if "canonical_delta" in item):
        raise ValueError("auxiliary lane false promotion")
    if any(x["accepted_upstream"] for x in d["auxiliary_lanes"]):
        raise ValueError("cross-model source import unverified")

def self_test(d):
    validate(d)
    cases = []
    a = copy.deepcopy(d); a["progress_snapshots"]["bass_ce1"]["completed"] = 10
    cases.append(a)
    a = copy.deepcopy(d); a["progress_snapshots"]["bass_ce1"]["imported_to_rei"] = True
    cases.append(a)
    a = copy.deepcopy(d); a["nodes"][-1]["depends_on"] = ["REI_R2C_LOCAL_MICROSTEP"]
    cases.append(a)
    a = copy.deepcopy(d); a["nodes"][1]["depends_on"] = ["REI_FIRST_CANONICAL_INTERVAL"]
    cases.append(a)
    a = copy.deepcopy(d); a["next_action"]["default_id"] = "REI_C0_BIANCHI_I_COUPLING"
    cases.append(a)
    a = copy.deepcopy(d); a["auxiliary_lanes"][0]["accepted_upstream"] = True
    cases.append(a)
    a = copy.deepcopy(d); a["next_action"]["merge"] = "APPROVED"
    cases.append(a)
    a = copy.deepcopy(d); a["scope"]["program_id"] = "ALL_BASS_TASKS"
    cases.append(a)
    for case in cases:
        try:
            validate(case)
        except ValueError:
            continue
        raise AssertionError("negative mission-drift mutant went undetected")
    return len(cases)

if __name__ == "__main__":
    d = json.loads(DAG.read_text(encoding="utf-8"))
    validate(d)
    count = self_test(d) if "--self-test" in sys.argv else 0
    print(f"REI_IGM_MISSION_DAG_STRUCTURAL_PASS nodes={len(d['nodes'])} "
          f"critical_path={len(d['critical_path_ids'])} rejected_mutants={count} "
          "central_physics_claim=NOT_TESTED")
