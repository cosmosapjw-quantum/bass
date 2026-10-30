"""Immutable zipped CE1-Z physics checkpoints with CRC and per-member SHA256.

S0 is generated before the scientific program, S1 after the real six-case run,
S2 after scoped tests; GitHub Actions retains each raw stage archive separately.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT=Path(__file__).resolve().parents[2]
SELF=ROOT/"research/ce1z_20261030"
PARENT=ROOT/"research/ce1y_20261030"


def create(stage: str, out: Path, results: Path | None):
    assert stage in {"S0", "S1", "S2"}
    files={
      "research/ce1z_20261030/S0_THEORY_KO.md": SELF/"S0_THEORY_KO.md",
    }
    if stage in {"S1","S2"}:
        assert results is not None and results.is_file()
        files.update({
          "research/ce1z_20261030/gram_spectrum.py": SELF/"gram_spectrum.py",
          "research/ce1z_20261030/package_artifacts.py": SELF/"package_artifacts.py",
          "research/ce1z_20261030/tests/test_gram_spectrum.py": SELF/"tests/test_gram_spectrum.py",
          "results/gram_spectrum.json": results,
          "source/SCIENCE_RESULTS.json": PARENT/"data/SCIENCE_RESULTS.json",
        })
        for n in (6,8):
            for s in (4,8,16):
                tag=f"GL{n}_STEPS{s}"
                files[f"original_BASS_Rust_sky/{tag}.csv"]=PARENT/f"input/{tag}_BASS_RUST_SKY.csv"
                files[f"two_time_K4/{tag}.csv"]=PARENT/f"data/{tag}_two_time_K4_1681.csv"
    if stage=="S2":
        for name in ("DAG_DELTA.json","S2_FINAL_REPORT_KO.md","HANDOFF_NEXT_KO.txt"):
            p=SELF/name
            if p.exists():
                files[f"research/ce1z_20261030/{name}"]=p
    out.parent.mkdir(parents=True, exist_ok=True)
    manifest={"schema":"bass.ce1z.science_archive.v1",
              "stage":stage,
              "source_SHA256":"022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035",
              "BASS_Rust_git_blob":"a29b12b5e7b0d529bddaf9eac53cfdb984ddaa84",
              "parent_PR271_head":"9cf562496cb753fe831e684ccf0b4dd54f5c5d94",
              "upper_dag":"9/15","ce1":"PARTIAL","production_ready":False,
              "sha256_members":{}}
    with ZipFile(out,"w",compression=ZIP_DEFLATED,compresslevel=6) as z:
        for key,path in sorted(files.items()):
            data=path.read_bytes()
            manifest["sha256_members"][key]=hashlib.sha256(data).hexdigest()
            z.writestr(key,data)
        z.writestr("MANIFEST.json",json.dumps(manifest,indent=2,sort_keys=True)+"\n")
    with ZipFile(out) as z:
        if z.testzip() is not None: raise RuntimeError("ZIP CRC fail")
        m=json.loads(z.read("MANIFEST.json"))
        for key,h in m["sha256_members"].items():
            if hashlib.sha256(z.read(key)).hexdigest()!=h:
                raise RuntimeError(f"source member SHA mismatch: {key}")
    print(json.dumps({"stage":stage,"path":str(out),"bytes":out.stat().st_size,
      "sha256":hashlib.sha256(out.read_bytes()).hexdigest(),
      "members":len(manifest["sha256_members"]),"crc":"PASS"},sort_keys=True),flush=True)

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--stage",choices=["S0","S1","S2"],required=True)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--results",type=Path)
    opt=parser.parse_args()
    create(opt.stage,opt.output,opt.results)
