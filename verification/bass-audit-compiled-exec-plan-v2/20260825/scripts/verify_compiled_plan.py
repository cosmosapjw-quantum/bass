#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, re, sys
from pathlib import Path

HEX40=re.compile(r"^[0-9a-f]{40}$")
ROOT=Path(sys.argv[1] if len(sys.argv)>1 else ".").resolve()

def load_json(p): return json.loads((ROOT/p).read_text(encoding="utf-8"))
def load_jsonl(p):
    out=[]
    for n,line in enumerate((ROOT/p).read_text(encoding="utf-8").splitlines(),1):
        if line.strip(): out.append(json.loads(line))
    return out

def fail(msg):
    print("FAIL:",msg,file=sys.stderr); raise SystemExit(1)

plan=load_json("AUDIT_COMPILED_EXEC_PLAN.json")
contract=load_json("PR_CONTRACTS/BASS-AC-01.json")
review=load_json("FRESH_CONTEXT_REVIEW_CONTRACT.json")
state=load_json("CURRENT_STATE.json")
threats=load_jsonl("P0_P1_THREAT_CATALOGUE.jsonl")
claims=load_jsonl("SCIENCE_CLAIM_LEDGER.jsonl")
tasks=load_jsonl("FUTURE_DAG.jsonl")

if plan.get("new_theory_allowed") is not False: fail("new theory must be forbidden")
if not HEX40.match(plan.get("base_sha", "")): fail("invalid plan base_sha")
if contract.get("base_sha") != plan.get("base_sha"): fail("contract/base mismatch")
if contract.get("schema") != "audit-compiled-pr/v1": fail("wrong contract schema")
if not contract["scope"].get("allowed_paths"): fail("allowed_paths empty")
if not contract["scope"].get("forbidden_paths"): fail("forbidden_paths empty")
if review.get("fresh_context_required") is not True or review.get("reviewer_may_modify") is not False: fail("review gate not independent read-only")
if review["pass_condition"].get("P0") != 0 or review["pass_condition"].get("P1") != 0: fail("review permits P0/P1")

seen=set()
for t in threats:
    if t["id"] in seen: fail("duplicate threat "+t["id"])
    seen.add(t["id"])
    if t.get("severity") not in {"P0","P1"}: fail("threat severity not P0/P1")
    d=t.get("detection") or {}
    if d.get("type") not in {"test","command","stop_gate"}: fail("missing mechanical detector "+t["id"])
    if d["type"]=="test" and not d.get("target"): fail("test target missing "+t["id"])
    if d["type"]=="command" and not d.get("command"): fail("command missing "+t["id"])
    if d["type"]=="stop_gate" and not d.get("gate"): fail("stop gate missing "+t["id"])

for fm in contract["failure_modes"]:
    if fm.get("severity") in {"P0","P1"} and not fm.get("required_detection"): fail("failure mode lacks detector "+fm.get("id","?"))
for inv in contract["invariants"]:
    if inv.get("severity_if_violated") in {"P0","P1"} and not (inv.get("mechanical_check") or inv.get("stop_gate")): fail("invariant lacks mechanical check "+inv.get("id","?"))

for c in claims:
    if c["status"] not in {"SUPPORTED_WITH_SCOPE","SUPPORTED_BOUNDED"} and not c.get("required_evidence"): fail("noncomplete claim lacks required evidence "+c["id"])

ready=[t for t in tasks if t.get("status")=="READY"]
if [t["id"] for t in ready] != ["BASS-AC-01_ARTIFACT_IDENTITY_GUARD"]: fail("exactly AC-01 must be READY")
if state["node"]["status"] != "BLOCKED_INPUT_REQUIRED": fail("science lane must remain blocked")
if plan["merge_gate"] != {"P0":0,"P1":0,"evidence_bundle_complete":True,"fresh_context_review":True}: fail("merge gate drift")


# Manifest coverage and cache hygiene
manifest_lines=(ROOT/"MANIFEST.sha256").read_text(encoding="utf-8").splitlines()
manifest_paths=[]
for line in manifest_lines:
    if not line.strip(): continue
    try:
        digest, rel=line.split("  ",1)
    except ValueError:
        fail("malformed MANIFEST.sha256 line")
    manifest_paths.append(rel)
actual=[]
for fp in ROOT.rglob("*"):
    if fp.is_file() and fp.name != "MANIFEST.sha256":
        rel=fp.relative_to(ROOT).as_posix()
        if "__pycache__" in fp.parts or fp.suffix==".pyc": fail("generated cache contamination "+rel)
        actual.append(rel)
if sorted(manifest_paths)!=sorted(actual):
    missing=sorted(set(manifest_paths)-set(actual)); extra=sorted(set(actual)-set(manifest_paths))
    fail(f"manifest coverage mismatch missing={missing} extra={extra}")

print(f"BASS_AUDIT_COMPILED_PLAN_VERIFY_PASS threats={len(threats)} claims={len(claims)} tasks={len(tasks)} invariants={len(contract['invariants'])} failure_modes={len(contract['failure_modes'])}")
