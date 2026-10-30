"""CE1-AA source-complete staged physics artifacts with SHA256 and ZIP CRC.

Stages: S0 original mathematical source before the MPFR run;
S1 original input+program+raw MPFR evidence; S2 S1 plus final report/handoff.
No BASS production or original source mutation.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT=Path(__file__).resolve().parents[2]
HERE=ROOT/"research/ce1aa_20261030"
INPUT=ROOT/"research/ce1y_20261030/input"
DATA=ROOT/"research/ce1y_20261030/data"


def build(stage: str, out: Path, result: Path | None):
    if stage not in ("S0","S1","S2"):
        raise ValueError("unknown physical stage")
    files={"research/ce1aa_20261030/S0_THEORY_KO.md":HERE/"S0_THEORY_KO.md"}
    if stage in ("S1","S2"):
        if result is None or not result.is_file():
            raise FileNotFoundError("actual directed MPFR192 program result required")
        files.update({
            "research/ce1aa_20261030/two_epoch_mpfr.py":HERE/"two_epoch_mpfr.py",
            "research/ce1aa_20261030/tests/test_two_epoch_mpfr.py":HERE/"tests/test_two_epoch_mpfr.py",
            "research/ce1aa_20261030/package_artifacts.py":HERE/"package_artifacts.py",
            "results/real_directed_mpfr192_two_epoch.json":result,
            "parent_source/SCIENCE_RESULTS.json":DATA/"SCIENCE_RESULTS.json",
            "parent_source/real_time_mpfr.json":INPUT/"real_time_mpfr.json",
            "parent_source/l4_source_and_transfer.json":INPUT/"l4_source_and_transfer.json",
        })
        for n in (6,8):
            for steps in (4,8,16):
                name=f"GL{n}_STEPS{steps}"
                files[f"original_BASS_Rust_sky/{name}.csv"]=INPUT/f"{name}_BASS_RUST_SKY.csv"
                files[f"original_two_time_K4/{name}.csv"]=DATA/f"{name}_two_time_K4_1681.csv"
    if stage=="S2":
        for name in ("DAG_DELTA.json","S2_FINAL_REPORT_KO.md","HANDOFF_NEXT_KO.txt"):
            f=HERE/name
            if f.exists():
                files[f"research/ce1aa_20261030/{name}"]=f
    out.parent.mkdir(parents=True,exist_ok=True)
    m={
        "schema":"bass.ce1aa.original_bass_mpfr_stage_archive.v1",
        "stage":stage,
        "parent_PR272_head":"cd597ace92dabafa71a59779242910c3cbcd21c7",
        "original_source_sha256":"022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035",
        "original_Rust_blob":"a29b12b5e7b0d529bddaf9eac53cfdb984ddaa84",
        "upper_dag":"9/15",
        "ce1":"PARTIAL",
        "production_ready":False,
        "files_sha256":{},
    }
    with ZipFile(out,"w",compression=ZIP_DEFLATED,compresslevel=6) as z:
        for name,p in sorted(files.items()):
            raw=p.read_bytes()
            z.writestr(name,raw)
            m["files_sha256"][name]=hashlib.sha256(raw).hexdigest()
        z.writestr("MANIFEST.json",json.dumps(m,indent=2,sort_keys=True)+"\n")
    with ZipFile(out) as z:
        if z.testzip() is not None:
            raise RuntimeError("ZIP CRC fail")
        manifest=json.loads(z.read("MANIFEST.json"))
        for name,digest in manifest["files_sha256"].items():
            if hashlib.sha256(z.read(name)).hexdigest()!=digest:
                raise RuntimeError("member hash mismatch "+name)
    print(json.dumps({"stage":stage,"path":str(out),"size_bytes":out.stat().st_size,
                      "sha256":hashlib.sha256(out.read_bytes()).hexdigest(),
                      "member_count":len(files),"zip_crc":"PASS","member_sha":"PASS",
                      "upper_dag":"9/15"},sort_keys=True),flush=True)


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--stage",choices=("S0","S1","S2"),required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--results",type=Path)
    v=p.parse_args()
    build(v.stage,v.output,v.results)
