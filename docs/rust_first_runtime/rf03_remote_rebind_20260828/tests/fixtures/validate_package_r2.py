#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, subprocess
from pathlib import Path
from typing import NoReturn

ROOT=Path(__file__).resolve().parent
PACKAGE_ID="BASS-RF03-AUTHORITY-DIRECT-HANDOFF-20260828-R2"
BASE_BRANCH="agent/architecture/rust-first-rf02c-20260826-r1"
BASE_HEAD="dfa17457d402bd441d3fdf786c2d79c529512ee5"
BASE_TREE="9fc67fb0ba10e091e25a14d7e1fac88b77a0241e"
R1_BRANCH="agent/plans/rf03-matter-thermo-tilt-closure-20260828-r1"
R1_HEAD="b7cda09d337906c17821a2b815032c985ff86bdf"
FILES={"README.md","AUTHORITY_CONTRACT.json","WORK_UNITS.json","CODEX_HANDOFF.md","validate_package.py"}
SOURCE_BLOBS={
 "bianchi/matter/fluid.py":"41905ff26914b2a7931ce2281d67b25fbde273b5",
 "bianchi/matter/species.py":"60a683fcdc639ae790cf6f3c723182d26940d21f",
 "bianchi/matter/tilt_admissibility.py":"c384a87c1722bd3c6b9b7e02ea71efe7ec88b676",
 "bianchi/thermo/temperature.py":"4b792b04df072446a5d046524ea5323e4237d7e4",
 "compiler/validation/typeii_fixture_authority.json":"b71372faa7dde85e928802c08c831299ebe99bcd",
 "runtime/rust/typeii/tests/FIXTURE_PROVENANCE.json":"dfee51903025b4c9d3f62f63581271bd3b6a98cb"}

def fail(s:str)->NoReturn: raise SystemExit("FAIL: "+s)
def sha(p:Path)->str: return hashlib.sha256(p.read_bytes()).hexdigest()
def git(repo:Path,*a:str)->str:
 r=subprocess.run(["git",*a],cwd=repo,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 if r.returncode: fail("git "+" ".join(a)+": "+r.stderr.strip())
 return r.stdout.strip()

def local():
 entries={}
 for line in (ROOT/"MANIFEST.sha256").read_text().splitlines():
  if line.strip():
   d,n=line.split(maxsplit=1); entries[n]=d
 if set(entries)!=FILES: fail("manifest closure")
 for n,d in entries.items():
  if sha(ROOT/n)!=d: fail(n+" digest")
 c=json.loads((ROOT/"AUTHORITY_CONTRACT.json").read_text())
 w=json.loads((ROOT/"WORK_UNITS.json").read_text())
 if c.get("package_id")!=PACKAGE_ID or w.get("package_id")!=PACKAGE_ID: fail("package id")
 if w.get("exact_next_action")!="RF03-AUTH-01": fail("next action")
 m=c["production_matter_authority"]
 if m["model_id"]!="explicit_gamma_law_tilted_perfect_fluid_v1": fail("model id")
 if m["state_order"]!=["Omega","v1","v2","v3"]: fail("state order")
 if c["thermodynamics_boundary"]["tilted_temperature_formula"]!="UNDEFINED_AND_NOT_AUTHORIZED": fail("tilted temperature boundary")
 if c["claim_boundary"]["current"]!="NO_PASS_RF03_CLAIM": fail("claim boundary")
 return c

def live(repo:Path):
 repo=Path(git(repo,"rev-parse","--show-toplevel"))
 if git(repo,"rev-parse","--verify",f"origin/{BASE_BRANCH}")!=BASE_HEAD: fail("base head moved")
 if git(repo,"rev-parse",f"{BASE_HEAD}^{{tree}}")!=BASE_TREE: fail("base tree")
 if git(repo,"rev-parse","--verify",f"origin/{R1_BRANCH}")!=R1_HEAD: fail("R1 package moved")
 for p,d in SOURCE_BLOBS.items():
  if git(repo,"rev-parse",f"{BASE_HEAD}:{p}")!=d: fail("source blob "+p)

if __name__=="__main__":
 ap=argparse.ArgumentParser(); ap.add_argument("--live",action="store_true"); ap.add_argument("--repo",default="."); a=ap.parse_args()
 local()
 if a.live: live(Path(a.repo))
 print(json.dumps({"status":"PASS","package_id":PACKAGE_ID,"base_head":BASE_HEAD,"base_tree":BASE_TREE,"exact_next_action":"RF03-AUTH-01","live":a.live},sort_keys=True))
