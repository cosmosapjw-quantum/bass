#!/usr/bin/env python3
import argparse, hashlib, json, pathlib, subprocess
ROOT=pathlib.Path(__file__).resolve().parent
FILES={"README.md","PACKAGE.json","WORK_UNITS.json","CODEX_HANDOFF.md","GITHUB_ROUNDTRIP_RECEIPT.json","validate_package.py"}
def fail(x): raise SystemExit("FAIL: "+x)
def git(repo,*a):
 r=subprocess.run(["git","--no-replace-objects",*a],cwd=repo,text=True,capture_output=True)
 if r.returncode: fail("git "+" ".join(a)+": "+r.stderr.strip())
 return r.stdout.removesuffix("\n")
def local():
 entries={}
 for line in (ROOT/"MANIFEST.sha256").read_text().splitlines():
  if line.strip():
   h,n=line.split(maxsplit=1); entries[n]=h
 if set(entries)!=FILES: fail("manifest closure")
 for n,h in entries.items():
  if hashlib.sha256((ROOT/n).read_bytes()).hexdigest()!=h: fail(n+" digest")
 p=json.loads((ROOT/"PACKAGE.json").read_text())
 if p["control_authority"]["head"]!="f18e491f19f45accc8c87eb56b4a24f15a8a3d6c" or p["control_authority"]["tree"]!="3fd8201a3cb15bf8d882dd28d37bf0c31e8af7e0": fail("control")
 if p["execution"]["exact_next_action"]!="RF04-RED-01": fail("next")
 if p["legacy_optimization"]["candidate_import"]!="FORBIDDEN": fail("legacy")
def live(repo):
 repo=pathlib.Path(git(repo,"rev-parse","--show-toplevel"))
 if git(repo,"rev-parse","--verify","refs/remotes/origin/agent/plans/rf04-sci-auth-intake-20260828-r1")!="f18e491f19f45accc8c87eb56b4a24f15a8a3d6c": fail("control moved")
 if git(repo,"rev-parse","f18e491f19f45accc8c87eb56b4a24f15a8a3d6c^{tree}")!="3fd8201a3cb15bf8d882dd28d37bf0c31e8af7e0": fail("control tree")
 if git(repo,"rev-parse","4a0e97cbc26a80e1fecbe18799a07207cfd8e556^{tree}")!="3fd8201a3cb15bf8d882dd28d37bf0c31e8af7e0": fail("pre-probe tree")
 if git(repo,"rev-parse","f18e491f19f45accc8c87eb56b4a24f15a8a3d6c:docs/rust_first_runtime/RF04_CURRENT_PACKAGE.json")!="aff7c4270dd9481020836a1d1ad7420dd4f47fb7": fail("pointer")
 if git(repo,"rev-parse","f18e491f19f45accc8c87eb56b4a24f15a8a3d6c:docs/rust_first_runtime/RF04_PUBLIC_ROUTE_SCHEMA_V1.json")!="a5a503f96c8d85af265be67ac04fd3ff983d9b33": fail("schema")
 if git(repo,"rev-parse","--verify","refs/remotes/origin/agent/architecture/rust-first-rf03-20260828-r2")!="6e53664d56694f7a7ad5f65be262302d5c8866b2": fail("RF03 moved")
if __name__=="__main__":
 ap=argparse.ArgumentParser(); ap.add_argument("--live",action="store_true"); ap.add_argument("--repo",default="."); a=ap.parse_args(); local();
 if a.live: live(a.repo)
 print(json.dumps({"status":"PASS","control_head":"f18e491f19f45accc8c87eb56b4a24f15a8a3d6c","control_tree":"3fd8201a3cb15bf8d882dd28d37bf0c31e8af7e0","exact_next_action":"RF04-RED-01","claim":"NO_PASS_RF04","live":a.live},sort_keys=True))
