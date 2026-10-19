#!/usr/bin/env python3
"""Prepare and compile the pinned S9 client; does not execute a history campaign.

Python standard library only. --vigilode-root and --vendor enable a fully offline
build. Without an existing source, download only the hash-listed upstream files.
"""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import time
import urllib.request

HERE = Path(__file__).resolve().parent

def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+"\n")

def digest(data):
    return hashlib.sha256(data).hexdigest()

def verify_file(root, item):
    relative = Path(item["path"])
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError("UPSTREAM_MANIFEST_PATH")
    data = (root/relative).read_bytes()
    blob = hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
    if len(data)!=item["size"] or digest(data)!=item["sha256"] or blob!=item["git_blob"]:
        raise ValueError("UPSTREAM_SOURCE_HASH_MISMATCH: "+str(relative))

def command(command, cwd, env, log, seconds=1800):
    started = time.time()
    with log.open("w") as output:
        process = subprocess.Popen(command, cwd=cwd, env=env, stdout=output,
                                   stderr=subprocess.STDOUT, start_new_session=True)
        try:
            code = process.wait(timeout=seconds)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGTERM)
            try: process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL); process.wait()
            code = 124
    record = {"command":command,"cwd":str(cwd),"exit_code":code,
              "elapsed_seconds":time.time()-started,"log":str(log),
              "log_sha256":digest(log.read_bytes()),"timeout_seconds":seconds}
    print(json.dumps(record), flush=True)
    return record

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-dir", type=Path, required=True)
    parser.add_argument("--vigilode-root", type=Path)
    parser.add_argument("--vendor", type=Path)
    parser.add_argument("--cargo", default=shutil.which("cargo") or "cargo")
    parser.add_argument("--rustc", default=shutil.which("rustc") or "rustc")
    parser.add_argument("--jobs", type=int, default=2)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--test", action="store_true")
    parser.add_argument("--lock-only", action="store_true")
    args = parser.parse_args()
    if not 1<=args.jobs<=16: parser.error("jobs must be in 1..16")
    work = args.work_dir.resolve(); work.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((HERE/"VIGILODE_SOURCE.json").read_text())
    if sum(row["size"] for row in manifest["files"])>20*1024**2:
        raise ValueError("UPSTREAM_SOURCE_DOWNLOAD_BUDGET")
    upstream = work/"vigilode"
    if args.vigilode_root:
        selected = args.vigilode_root.resolve()
        for row in manifest["files"]: verify_file(selected,row)
        if upstream.exists() or upstream.is_symlink():
            if upstream.resolve()!=selected: raise ValueError("RUNTIME_UPSTREAM_PATH_ALREADY_OWNED")
        else: upstream.symlink_to(selected, target_is_directory=True)
        source_transport = "existing hash-verified directory; zero source download"
    else:
        upstream.mkdir(exist_ok=True)
        def fetch(row):
            target = upstream/row["path"]
            if not target.exists():
                url = ("https://raw.githubusercontent.com/"+manifest["repo"]+"/"+
                       manifest["source_commit"]+"/"+row["path"])
                with urllib.request.urlopen(url,timeout=60) as response:
                    data=response.read(row["size"]+1)
                if len(data)!=row["size"]: raise ValueError("UPSTREAM_DOWNLOAD_SIZE")
                target.parent.mkdir(parents=True,exist_ok=True); target.write_bytes(data)
            verify_file(upstream,row)
        with ThreadPoolExecutor(max_workers=min(4,args.jobs)) as pool:
            list(pool.map(fetch,manifest["files"]))
        source_transport = "pinned raw Git files; complete SHA256 and Git-blob readback"
    client = work/"client"/"s9_vigilode"
    client.mkdir(parents=True,exist_ok=True)
    for relative in ["Cargo.toml","Cargo.lock","src/lib.rs","src/main.rs","tests/adapter_contracts.rs"]:
        source=HERE/relative
        if not source.exists():
            if relative=="Cargo.lock": continue
            raise FileNotFoundError(source)
        target=client/relative; target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(source,target)
    owner=HERE.parent/"balance_p24.rs"
    shutil.copyfile(owner,client.parent/"balance_p24.rs")
    env=os.environ.copy()
    env.update({"RUSTC":str(Path(args.rustc).resolve()),"CARGO_HOME":str(work/"cargo_home"),
                "CARGO_TARGET_DIR":str(work/"target"),"CARGO_BUILD_JOBS":str(args.jobs),
                "CARGO_INCREMENTAL":"0","RAYON_NUM_THREADS":"1"})
    (work/"cargo_home").mkdir(exist_ok=True)
    config_dir=client/".cargo"; config_dir.mkdir(exist_ok=True)
    config_path=config_dir/"config.toml"
    if args.vendor:
        # JSON string escaping is valid for this TOML basic path string.
        config_path.write_text('[source.crates-io]\nreplace-with = "offline-vendor"\n'
            '[source.offline-vendor]\ndirectory = '+json.dumps(str(args.vendor.resolve()))+'\n'
            '[net]\noffline = true\n')
    elif config_path.exists():
        raise ValueError("EXISTING_OFFLINE_CONFIG_REQUIRES_EXPLICIT_VENDOR")
    receipt={"schema":"BASS_S9_PREPARATION_V1","vigilode_source":manifest["source_commit"],
        "vigilode_tree":manifest["source_tree"],"source_files_verified":len(manifest["files"]),
        "source_bytes":sum(row["size"] for row in manifest["files"]),"source_transport":source_transport,
        "balance_owner_sha256":digest(owner.read_bytes()),"client":str(client),
        "offline_vendor":str(args.vendor.resolve()) if args.vendor else None,
        "limits":{"workers":args.jobs,"ram_bytes":16*1024**3,"disk_bytes":4*1024**3,"job_seconds":1800},
        "profile":"dev: opt-level=1, debug=0, incremental=false, codegen-units=1",
        "scientific_campaign_executed":False,"commands":[]}
    receipt['client_source_sha256']={relative:digest((client/relative).read_bytes())
        for relative in ['Cargo.toml','Cargo.lock','src/lib.rs','src/main.rs','tests/adapter_contracts.rs']
        if (client/relative).exists()}
    for executable,label in [(args.cargo,"cargo"),(args.rustc,"rustc")]:
        receipt[label+"_version"]=subprocess.check_output([executable,"--version"],env=env,text=True).strip()
    requests=[]
    if args.lock_only or not (client/"Cargo.lock").exists(): requests.append([args.cargo,"generate-lockfile"])
    if args.test: requests.append([args.cargo,"test","--locked","--test","adapter_contracts"])
    if args.build: requests.append([args.cargo,"build","--locked","--bin","bass-s9-vigilode"])
    status=0
    for index,request in enumerate(requests):
        record=command(request,client,env,work/f"prepare_command_{index:02d}.log")
        receipt["commands"].append(record)
        if record["exit_code"]: status=record["exit_code"]; break
    if (client/"Cargo.lock").exists(): receipt["cargo_lock_sha256"]=digest((client/"Cargo.lock").read_bytes())
    binary=work/"target"/"debug"/"bass-s9-vigilode"
    if binary.exists(): receipt["binary"]={"path":str(binary),"sha256":digest(binary.read_bytes())}
    receipt["status"]="prepared" if status==0 else "build_or_test_failure"
    write_json(work/"PREPARATION_RETURN.json",receipt)
    print(json.dumps({"status":receipt["status"],"receipt":str(work/"PREPARATION_RETURN.json")}))
    raise SystemExit(status)

if __name__=="__main__": main()
