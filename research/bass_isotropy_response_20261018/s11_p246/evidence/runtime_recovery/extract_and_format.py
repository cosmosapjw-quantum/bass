#!/usr/bin/env python3
"""Restore the exact published Rust toolchain subset after filesystem reset."""
import datetime as dt
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import tarfile
import time

BASE = Path("/workspace/scratch/14e1021f8231")
ARCHIVE = BASE/"runtime_s11_recovery/rust-1.94.1.tar.xz"
DEST = BASE/"runtime_s11/rust"
RECEIPT = BASE/"runtime_s11_recovery/EXTRACTION_FORMAT_RECEIPT.json"
EXPECTED_ARCHIVE = "294b3d81fa72e62581276290c60c81eb8b58498d333d422ca1dfc432877d0c40"
COMPONENTS = {"rustc", "rust-std-x86_64-unknown-linux-gnu", "rustfmt-preview"}
ARCHIVE_ROOT = "rust-1.94.1-x86_64-unknown-linux-gnu"
SOURCE = BASE/"bass_work/research/bass_isotropy_response_20261018/s11_p246/rust"
EXPECTED_SOURCE = {
    "projector.rs": "a14817cd39f903d7ca8e258965dd5e100b64a8181e26301481f2f2c85b2dc510",
    "cli.rs": "e1e6c1ad82611b0df92b7531fae5d8a195463d8f86d42749f49d9fe75fe66c2b",
}
def digest(path):
    h=hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda:stream.read(1<<20),b""): h.update(block)
    return h.hexdigest()
def run(command):
    r=subprocess.run(command,capture_output=True,text=True)
    return {"command":command,"exit_code":r.returncode,"stdout":r.stdout,"stderr":r.stderr}
started=time.monotonic()
record={
    "schema":"bass.s11.runtime_interruption_recovery.v1",
    "status":"in_progress",
    "started_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
    "archive":{"path":str(ARCHIVE),"bytes":ARCHIVE.stat().st_size,"sha256":digest(ARCHIVE)},
    "destination":str(DEST),"components":sorted(COMPONENTS),
    "selected_members":[],"excluded_component_root_metadata":[],
    "baseline_campaign_replays":0,"science_validation_runs":0,
    "prior_smoke_receipt":"lost with filesystem; not reused as durable evidence",
}
assert record["archive"]["sha256"]==EXPECTED_ARCHIVE
assert not DEST.is_symlink()
DEST.mkdir(parents=True,exist_ok=True)
assert not any(DEST.iterdir()),"destination is not empty; refusing overwrite"
dest_resolved=DEST.resolve()
try:
    with tarfile.open(ARCHIVE,"r|xz") as tf:
        for member in tf:
            archive_path=PurePosixPath(member.name)
            if archive_path.is_absolute() or ".." in archive_path.parts:
                raise ValueError(f"unsafe archive path: {member.name}")
            parts=archive_path.parts
            if not parts or parts[0]!=ARCHIVE_ROOT: raise ValueError("unexpected archive root")
            if len(parts)<3 or parts[1] not in COMPONENTS: continue
            relative=PurePosixPath(*parts[2:])
            if len(relative.parts)==1 and member.isfile():
                record["excluded_component_root_metadata"].append({"name":member.name,"bytes":member.size})
                continue
            target=DEST.joinpath(*relative.parts)
            if not target.resolve(strict=False).is_relative_to(dest_resolved):
                raise ValueError(f"destination escapes runtime root: {member.name}")
            # This pinned subset has no links. Reject all archive links rather
            # than allowing a later member to create an escape through a chain.
            if member.issym() or member.islnk(): raise ValueError(f"archive link rejected: {member.name}")
            if member.isdir():
                target.mkdir(parents=True,exist_ok=True)
                os.chmod(target,member.mode & 0o777)
                continue
            if not member.isfile(): raise ValueError(f"nonregular member rejected: {member.name}")
            target.parent.mkdir(parents=True,exist_ok=True)
            source=tf.extractfile(member)
            if source is None: raise ValueError(f"missing regular bytes: {member.name}")
            h=hashlib.sha256()
            count=0
            with target.open("xb") as output:
                while True:
                    block=source.read(1<<20)
                    if not block:break
                    h.update(block);output.write(block);count+=len(block)
            if count!=member.size:raise ValueError(f"truncated member: {member.name}")
            os.chmod(target,member.mode & 0o777)
            record["selected_members"].append({
                "archive_path":member.name,"relative_path":str(relative),
                "bytes":count,"sha256":h.hexdigest(),"mode":oct(member.mode & 0o777),
            })
    record["path_and_link_checks"]="all selected members relative/in-root, no traversal, no selected links, only regular files/directories; create-only extraction"
    record["extracted_file_bytes"]=sum(m["bytes"] for m in record["selected_members"])
    record["extracted_files"]=len(record["selected_members"])
    record["version_probes"]=[
        run([str(DEST/"bin/rustc"),"-vV"]),
        run([str(DEST/"bin/rustfmt"),"--version"]),
    ]
    if any(r["exit_code"] for r in record["version_probes"]):raise RuntimeError("runtime version probe failed")
    record["source_before_format"]={name:{"bytes":(SOURCE/name).stat().st_size,"sha256":digest(SOURCE/name)} for name in EXPECTED_SOURCE}
    record["format"]=run([str(DEST/"bin/rustfmt"),"--edition","2021",str(SOURCE/"projector.rs"),str(SOURCE/"cli.rs")])
    if record["format"]["exit_code"]:raise RuntimeError("rustfmt failed")
    record["source_after_format"]={name:{"bytes":(SOURCE/name).stat().st_size,"sha256":digest(SOURCE/name),"expected_prior_sha256":expected,"matches_prior":digest(SOURCE/name)==expected} for name,expected in EXPECTED_SOURCE.items()}
    record["status"]="PASS_EXACT_SOURCE_RECOVERY" if all(v["matches_prior"] for v in record["source_after_format"].values()) else "SOURCE_HASH_MISMATCH"
except Exception as exc:
    record["status"]="RECOVERY_FAILED"
    record["error"]=repr(exc)
    raise
finally:
    record["finished_utc"]=dt.datetime.now(dt.timezone.utc).isoformat()
    record["wall_s"]=time.monotonic()-started
    RECEIPT.write_text(json.dumps(record,indent=2)+"\n")
    print(json.dumps({k:v for k,v in record.items() if k!="selected_members"},indent=2),flush=True)

