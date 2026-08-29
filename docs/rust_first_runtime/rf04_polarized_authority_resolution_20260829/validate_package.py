#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parent
PACKAGE_ID="BASS-RF04-POLARIZED-AUTHORITY-RESOLUTION-20260829-R1"
BASE="4eb8b1d89807b71f6110aafa5b50adfef2bf5433"
BASE_TREE="460b9ab031a12e4a8a63f6f6f623c2c752ae7196"
SOURCE="50b6e9f7a6741b7fd25b0421d2a674b9eb92cdda"
SOURCE_TREE="b32fcc26ca51dcaca9e9225d48b03fe9e02988ed"
PROBE_PACKAGE="25e3f321e16ff7695566e5ba739ba86caa87bb59"
PROBE_TREE="f7d142adabd1bcb8e5c7df4a32371ebf2deafddd"
CONTROL="f18e491f19f45accc8c87eb56b4a24f15a8a3d6c"
CONTROL_TREE="3fd8201a3cb15bf8d882dd28d37bf0c31e8af7e0"
LOCAL_MANIFEST="c05a78d373f3fd87c028e8535404c2b4723aff56c533163d3822355cf3987ea1"
SOURCE_BLOBS={"_rustcore/src/kinetic/rf04_typeii.rs": "71508ebb9b3a5abd3bc403d6a24502ad9de09d39", "generated/rust/typeii/typeii_polarized.rs": "557fc72d893b87bb9aaf55c7d4c85533bf5e0312", "runtime/rust/typeii/tests/typeii_pre_liouville_safety.rs": "6936d2a7116bc9b431c884c7f53b68681983d483", "runtime/rust/typeii/typeii_polarized_liouville.rs": "da6fade06f717ab938b0ec4c712ab239e78c998a", "runtime/rust/typeii/typeii_polarized_remap.rs": "5f7a1e580df3855f07f567fb3baa0e339d52c82e", "runtime/rust/typeii/typeii_polarized_runtime.rs": "a852431274c206cc81b063f9501e46a524bd3765", "runtime/rust/typeii/typeii_polarized_runtime_physical.rs": "03684d7a9ef76be3bb06841af86bb5822574bab3"}
SOURCE_MAP_BLOBS={"docs/rust_first_runtime/rf04_full_polarized_contract_20260829/PACKAGE.json": "2c00a40880f56bb0707a98f08d2a7343fb9055a6", "docs/rust_first_runtime/rf04_full_polarized_contract_20260829/SOURCE_MAP.json": "49897eb6ca7170a8a2437c0ef61eaca5859b3eb2", "docs/rust_first_runtime/rf04_full_polarized_contract_20260829/WORK_UNITS.json": "56ddf3b6c580cf5e8946eae7314fee789a735b81"}
FILES={
 "README.md","PACKAGE.json","MEASURED_CANDIDATES.json",
 "AUTHORITY_DECISIONS.json","PUBLIC_ROUTE_SCHEMA_DELTA_V2.json",
 "WORK_UNITS.json","ACCEPTANCE_MATRIX.json","IMPLEMENTATION_PLAN.md",
 "CODEX_HANDOFF.md","validate_package.py"
}

def fail(message): raise SystemExit("FAIL: "+message)
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def git(repo,*args):
 p=subprocess.run(["git","--no-replace-objects",*args],cwd=repo,text=True,
  stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=45)
 if p.returncode: fail("git "+" ".join(args)+": "+p.stderr.strip())
 return p.stdout.removesuffix("\n")

def local():
 entries={}
 for line in (ROOT/"MANIFEST.sha256").read_text().splitlines():
  if line.strip():
   digest,name=line.split(maxsplit=1)
   if name in entries: fail("duplicate manifest")
   entries[name]=digest
 if set(entries)!=FILES: fail("manifest closure")
 for name,digest in entries.items():
  if sha(ROOT/name)!=digest: fail("digest "+name)

 package=json.loads((ROOT/"PACKAGE.json").read_text())
 measured=json.loads((ROOT/"MEASURED_CANDIDATES.json").read_text())
 decisions=json.loads((ROOT/"AUTHORITY_DECISIONS.json").read_text())
 delta=json.loads((ROOT/"PUBLIC_ROUTE_SCHEMA_DELTA_V2.json").read_text())
 units=json.loads((ROOT/"WORK_UNITS.json").read_text())
 acceptance=json.loads((ROOT/"ACCEPTANCE_MATRIX.json").read_text())

 if package["package_id"]!=PACKAGE_ID: fail("package id")
 if package["execution"]["exact_next_action"]!="RF04-POL-EVIDENCE-00": fail("next action")
 if measured["manifest_sha256"]!=LOCAL_MANIFEST: fail("local manifest binding")
 if measured["probe_gate"]["A2_uniqueness"]!="FAIL": fail("measured uniqueness")
 expected={
  "P1":"RESOLVED",
  "P2":"RESOLVED_BY_INTERFACE_OWNERSHIP_NOT_ALGORITHM_SELECTION",
  "P3":"RESOLVED_DERIVED_NOT_SELECTED",
  "P4":"RESOLVED",
  "P5":"RESOLVED"
 }
 actual={key:value["status"] for key,value in decisions["decisions"].items()}
 if actual!=expected: fail("authority decisions")
 if delta["compatibility"]["scalar_v1"]!="UNCHANGED_AND_RETAINED": fail("scalar compatibility")
 if delta["compatibility"]["polarized_on_v1"]!="CONTINUES_FAIL_CLOSED": fail("v1 firewall")
 expected_units=[
  "RF04-POL-EVIDENCE-00","RF04-POL-SCHEMA-01","RF04-POL-GEOMETRY-02",
  "RF04-POL-COMPOSE-03","RF04-POL-PUBLIC-04","RF04-POL-VERIFY-05",
  "RF04-POL-AUDIT-06","RF04-POL-DELIVER-07"
 ]
 if [item["id"] for item in units["work_units"]]!=expected_units: fail("work-unit order")
 if acceptance["current_claim"]!="NO_PASS_RF04": fail("claim ceiling")
 bindings=package["content_bindings"]
 if bindings["authority_decisions_sha256"]!=sha(ROOT/"AUTHORITY_DECISIONS.json"): fail("decision binding")
 if bindings["route_delta_sha256"]!=sha(ROOT/"PUBLIC_ROUTE_SCHEMA_DELTA_V2.json"): fail("route binding")
 if bindings["measured_candidates_sha256"]!=sha(ROOT/"MEASURED_CANDIDATES.json"): fail("measured binding")

def live(repoarg):
 repo=Path(git(repoarg,"rev-parse","--show-toplevel"))
 for commit,tree,label in [
  (BASE,BASE_TREE,"source-map base"),
  (SOURCE,SOURCE_TREE,"scientific source"),
  (PROBE_PACKAGE,PROBE_TREE,"probe package"),
  (CONTROL,CONTROL_TREE,"control")
 ]:
  if git(repo,"rev-parse",commit+"^{tree}")!=tree: fail(label+" tree")
 if git(repo,"merge-base","--is-ancestor",SOURCE,BASE)!="": pass
 for path,blob in SOURCE_BLOBS.items():
  if git(repo,"rev-parse",SOURCE+":"+path)!=blob: fail("source blob "+path)
 for path,blob in SOURCE_MAP_BLOBS.items():
  if git(repo,"rev-parse",BASE+":"+path)!=blob: fail("source-map blob "+path)
 if git(repo,"rev-parse",CONTROL+":docs/rust_first_runtime/RF04_PUBLIC_ROUTE_SCHEMA_V1.json") !=     "a5a503f96c8d85af265be67ac04fd3ff983d9b33":
  fail("public route schema blob")

if __name__=="__main__":
 ap=argparse.ArgumentParser()
 ap.add_argument("--live",action="store_true")
 ap.add_argument("--repo",default=".")
 args=ap.parse_args()
 local()
 if args.live: live(Path(args.repo))
 print(json.dumps({
  "status":"PASS","package_id":PACKAGE_ID,
  "exact_next_action":"RF04-POL-EVIDENCE-00",
  "decisions":5,"current_claim":"NO_PASS_RF04","live":args.live
 },sort_keys=True))
