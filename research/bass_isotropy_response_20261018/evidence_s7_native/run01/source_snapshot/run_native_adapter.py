"""Compile and measure the bounded new-source adapter against exact REI blobs.

No Cargo dependencies, production mutation, SSH, or user file transfer. When
no verified source path is given, fetch the 57 small pinned public source files.
"""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import resource
import shutil
import subprocess
import time
import urllib.request

ROOT=Path(__file__).resolve().parent
REI_SHA="0e25846433170d0f420c4cda44a0bedbf02cd177"
SOURCE_ID="MD14_Z002_FESC_BB50K_13P6_100_V1"
NEW_FILES=("native_adapter.rs","native_probe.rs","balance.rs","balance_p24.rs")
RAM=16*1024**3
DISK=4*1024**3

def digest(b):return hashlib.sha256(b).hexdigest()
def blob(b):return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
def verify_blob(raw,entry):
    if len(raw)!=entry["size"] or blob(raw)!=entry["sha"] or digest(raw)!=entry["sha256"]:
        raise ValueError("IMMUTABLE_SOURCE_IDENTITY:"+entry["path"])
    return raw

def verify_owner(source_root,manifest):
    total=0
    for entry in manifest["files"]:
        raw=(source_root/entry["path"]).read_bytes();verify_blob(raw,entry);total+=len(raw)
    if total>64*1024**2:raise ValueError("SOURCE_STAGE_BYTES")
    paths={entry["path"] for entry in manifest["files"]}
    for entry in manifest["files"]:
        if not entry["path"].endswith(".rs"):continue
        text=(source_root/entry["path"]).read_text()
        for name in re.findall(r'\binclude(?:_str|_bytes)?!\s*\(\s*"([^"\n]+)"\s*\)',text,re.S):
            target=os.path.normpath(str(Path(entry["path"]).parent/name))
            if target not in paths:raise ValueError("LITERAL_INCLUDE_DEPENDENCY:"+target)
    return {"files":len(paths),"bytes":total,"all_git_blob_sha_and_sha256_match":True}

def stage_owner(destination,manifest,repo=None,workers=4):
    destination.mkdir()
    def fetch(entry):
        path=entry["path"]
        if repo:
            p=subprocess.run(["git","-C",str(repo),"show",REI_SHA+":"+path],capture_output=True,timeout=60)
            if p.returncode:raise RuntimeError("PINNED_GIT_READ_FAILED:"+path)
            raw=p.stdout
        else:
            url="https://raw.githubusercontent.com/"+manifest["repo"]+"/"+REI_SHA+"/"+path
            with urllib.request.urlopen(url,timeout=30) as response:raw=response.read(64*1024**2+1)
        verify_blob(raw,entry)
        return path,raw
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for path,raw in pool.map(fetch,manifest["files"]):
            target=destination/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
    return verify_owner(destination,manifest)

def validate_measurements(path):
    def invalid(v):raise ValueError("NONFINITE_NATIVE_JSON:"+v)
    records=[json.loads(line,parse_constant=invalid) for line in path.read_text().splitlines() if line.strip()]
    if not records or records[-1].get("schema")!="bass.angular.native.s3.complete.v1":
        raise ValueError("MISSING_NATIVE_COMPLETION")
    complete=records.pop()
    if complete.get("rows")!=20 or len(records)!=20 or complete.get("owner_commit")!=REI_SHA or complete.get("source_id")!=SOURCE_ID:
        raise ValueError("NATIVE_COMPLETION_IDENTITY")
    expected={(n,96,b,mode) for n in (8,16,32) for b in (-0.3,0.0,0.3) for mode in ("P2","P2P4")}
    expected|={(8,24,0.3,mode) for mode in ("P2","P2P4")}
    found=set();max_derivative=0.0
    for r in records:
        key=(r["n_mu"],r["n_energy"],r["b_birth"],r["mode"])
        if key not in expected or key in found or r.get("schema")!="bass.angular.native.s3.v1":raise ValueError("NATIVE_CASE_IDENTITY")
        found.add(key)
        if any(not math.isfinite(v) for v in r.values() if isinstance(v,(int,float))):raise ValueError("NONFINITE_NATIVE_NUMBER")
        if r["inventory_n"]<=0 or r["inventory_u"]<=0 or r["min_weight"]<=0:raise ValueError("NATIVE_POSITIVITY")
        if abs(r["weight_p2"])>3e-15 or (r["mode"]=="P2P4" and abs(r["weight_p4"])>3e-15):raise ValueError("NATIVE_WEIGHT_MOMENT")
        if abs(r["ledger_n_residual"])/r["inventory_n"]>1e-11 or abs(r["ledger_u_residual"])/r["inventory_u"]>1e-11:
            raise ValueError("NATIVE_SOURCE_LEDGER")
        expected_derivative=-8/5-10/7*r["energy_p2"]+36/35*r["energy_p4"]
        if abs(r["derivative_legendre"]-expected_derivative)>1e-14:raise ValueError("NATIVE_ENERGY_MOMENT_MAPPING")
        derivative=abs(r["derivative_central"]-expected_derivative)
        max_derivative=max(max_derivative,derivative)
        if derivative>1e-8:raise ValueError("NATIVE_COLLISIONLESS_DERIVATIVE")
    if found!=expected:raise ValueError("NATIVE_CASE_MATRIX")
    return {"rows":20,"new_native_tests":7,"max_derivative_absolute_residual":max_derivative,
            "max_abs_photon_vs_source_relative":max(abs(r["photon_vs_source_relative"]) for r in records),
            "max_abs_energy_vs_source_moment_relative":max(abs(r["energy_vs_source_moment_relative"]) for r in records),
            "max_abs_energy_p2_after_P2P4":max(abs(r["energy_p2"]) for r in records if r["mode"]=="P2P4"),
            "max_abs_energy_p4_after_P2P4":max(abs(r["energy_p4"]) for r in records if r["mode"]=="P2P4"),
            "interpretation":"Finite-bin spectral moment defects measured independently of constrained angular weights."}

def run(out,owner_root=None,rei_repo=None,rustc=None,workers=4,timeout=1800):
    if not 1<=workers<=16 or not 1<=timeout<=1800:raise ValueError("EXECUTION_LIMIT")
    if out.exists():raise FileExistsError(out)
    out.mkdir(parents=True)
    started=time.monotonic();deadline=started+timeout
    receipt={"schema":"bass.angular.native.s3.execution.v1","started_utc":datetime.now(timezone.utc).isoformat(),
             "owner_commit":REI_SHA,"limits":{"additional_workers":workers,"native_threads":1,"ram_bytes":RAM,"disk_bytes":DISK,"job_seconds":timeout},
             "commands":[],"status":"STARTED","admission":"NEW_SOURCE_ANGULAR_ADAPTER_ONLY"}
    before={name:digest((ROOT/name).read_bytes()) for name in NEW_FILES}
    receipt["implementation_sha256"]=before
    receipt["runner_sha256"]=digest(Path(__file__).read_bytes())
    receipt["owner_manifest_sha256"]=digest((ROOT/"native_owner_manifest.json").read_bytes())
    def save():
        receipt["elapsed_seconds"]=time.monotonic()-started
        (out/"RETURN_NATIVE_ADAPTER.json").write_text(json.dumps(receipt,indent=2,allow_nan=False)+"\n")
    def limit():
        resource.setrlimit(resource.RLIMIT_AS,(RAM,RAM));resource.setrlimit(resource.RLIMIT_FSIZE,(DISK,DISK))
    def command(label,args):
        left=deadline-time.monotonic()
        if left<=0:raise TimeoutError("JOB_SECONDS")
        env=os.environ.copy();env.update({"RUST_TEST_THREADS":"1","OMP_NUM_THREADS":"1","OPENBLAS_NUM_THREADS":"1"})
        t=time.monotonic()
        try:
            proc=subprocess.run(list(map(str,args)),capture_output=True,timeout=min(left,1800),env=env,preexec_fn=limit)
        except subprocess.TimeoutExpired as exc:
            (out/(label+".stdout")).write_bytes(exc.stdout or b"")
            (out/(label+".stderr")).write_bytes(exc.stderr or b"")
            receipt["commands"].append({"label":label,"args":list(map(str,args)),"exit_code":None,
                                       "timed_out":True,"seconds":time.monotonic()-t})
            save();raise
        (out/(label+".stdout")).write_bytes(proc.stdout);(out/(label+".stderr")).write_bytes(proc.stderr)
        receipt["commands"].append({"label":label,"args":list(map(str,args)),"exit_code":proc.returncode,"seconds":time.monotonic()-t})
        save()
        if proc.returncode:raise RuntimeError("COMMAND_FAILED:"+label)
        return proc.stdout.decode(errors="replace")
    try:
        manifest=json.loads((ROOT/"native_owner_manifest.json").read_text())
        if manifest["commit"]!=REI_SHA:raise ValueError("OWNER_MANIFEST_COMMIT")
        if owner_root:
            owner_root=owner_root.resolve();receipt["source_mode"]="EXISTING_EXACT_SOURCE_READBACK"
            receipt["owner_verification"]=verify_owner(owner_root,manifest)
        else:
            if rei_repo is None:
                candidate=ROOT.parents[2]/"rei_bianchi"
                if (candidate/".git").exists():rei_repo=candidate
            owner_root=out/"owner_source"
            receipt["source_mode"]="PINNED_GIT_BLOBS" if rei_repo else "PINNED_RAW_GITHUB_BLOBS"
            receipt["owner_verification"]=stage_owner(owner_root,manifest,rei_repo,workers)
        aggregate_inputs=sorted(
            [["owner/"+entry["path"],entry["sha256"]] for entry in manifest["files"]]+
            [["adapter/"+name,value] for name,value in before.items()])
        aggregate_payload=json.dumps(aggregate_inputs,separators=(",",":"),ensure_ascii=False).encode()
        receipt["native_source_aggregate"]={
            "recipe":"SHA256 of UTF-8 compact JSON sorted [[logical_path, file_SHA256], ...]",
            "files":len(aggregate_inputs),"sha256":digest(aggregate_payload)}
        (out/"NATIVE_SOURCE_AGGREGATE.json").write_text(json.dumps({
            **receipt["native_source_aggregate"],"inputs":aggregate_inputs},indent=2)+"\n")
        compiler=rustc or shutil.which("rustc")
        if not compiler:raise FileNotFoundError("COMPILER_MISSING:rustc")
        receipt["rustc_version"]=command("compiler_version",[compiler,"-Vv"])
        work=out/"build";work.mkdir()
        for name in NEW_FILES:(work/name).write_bytes((ROOT/name).read_bytes())
        rlib=work/"librei_microphysics.rlib"
        command("compile_owner",[compiler,"--crate-name","rei_microphysics","--crate-type","rlib","--edition=2021","-O","-C","codegen-units=1",owner_root/"rust/rei_microphysics/src/lib.rs","-o",rlib])
        common=[compiler,"--edition=2021","-O","-C","codegen-units=1",work/"native_probe.rs","--extern","rei_microphysics="+str(rlib)]
        command("compile_changed_tests",common+["--test","-o",work/"native_tests"])
        testlog=command("changed_native_tests",[work/"native_tests","native_tests::","--nocapture","--test-threads=1"])
        if not re.search(r"test result: ok\. 7 passed; 0 failed;",testlog):raise ValueError("NATIVE_TEST_COUNT")
        command("compile_changed_probe",common+["-o",work/"native_probe"])
        command("measure_changed_adapter",[work/"native_probe",out/"NATIVE_ADAPTER.jsonl"])
        receipt["validation"]=validate_measurements(out/"NATIVE_ADAPTER.jsonl")
        receipt["native_output_sha256"]=digest((out/"NATIVE_ADAPTER.jsonl").read_bytes())
        receipt["artifact_sha256"]={f.name:digest(f.read_bytes()) for f in (work/"native_probe",work/"native_tests",rlib)}
        if before!={name:digest((ROOT/name).read_bytes()) for name in NEW_FILES}:raise ValueError("IMPLEMENTATION_CHANGED_DURING_RUN")
        verify_owner(owner_root,manifest)
        bytes_used=sum(p.stat().st_size for p in out.rglob("*") if p.is_file())
        if bytes_used>DISK:raise RuntimeError("DISK_LIMIT")
        receipt["disk_bytes_used"]=bytes_used
        receipt["children_peak_rss_kib_linux"]=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
        receipt["status"]="PASS_NATIVE_ADAPTER_SCOPED"
        receipt["remaining"]= ["continuum angular accuracy","full source-age or reactive history","native finite-bin spectral refinement certification","Einstein feedback","REI production / full EoR"]
    except Exception as e:
        receipt["status"]="FAILED";receipt["failure_type"]=type(e).__name__;receipt["failure"]=str(e)
        save();raise
    save();return receipt

def main():
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,required=True)
    p.add_argument("--owner-root",type=Path);p.add_argument("--rei-repo",type=Path)
    p.add_argument("--rustc");p.add_argument("--workers",type=int,default=4);p.add_argument("--timeout",type=int,default=1800)
    a=p.parse_args();r=run(a.out.resolve(),a.owner_root,a.rei_repo,a.rustc,a.workers,a.timeout)
    print(json.dumps({"status":r["status"],"rows":r["validation"]["rows"],"seconds":r["elapsed_seconds"]}))
if __name__=="__main__":main()
