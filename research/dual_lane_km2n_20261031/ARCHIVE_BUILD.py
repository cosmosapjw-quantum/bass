"""BASS KM2N source-complete S0/S1/S2 exact provenance backup and ZIP readback."""
from __future__ import annotations
import argparse,hashlib,json,os,zipfile
from pathlib import Path
from research.dual_lane_km2n_20261031.once_scattered import source_guards
ROOT=Path(__file__).resolve().parents[2]
UNIT="research/dual_lane_km2n_20261031"
OWNERS=(
 UNIT+"/S0_THEORY_KO.md",UNIT+"/once_scattered.py",
 UNIT+"/tests/test_once_scattered.py",UNIT+"/hostile_saved_audit.py",
 UNIT+"/make_plots.py",UNIT+"/generate_report.py",
 UNIT+"/ARCHIVE_BUILD.py",UNIT+"/DAG_DELTA.json",
 ".github/workflows/km2n-once-scattered.yml",
)
REPLAY_REQUIRED=(
 "research/dual_lane_km2c_20261028/vendor/polarization.py",
 "research/dual_lane_km2c_20261028/vendor/polarized_dictionary.py",
 "research/dual_lane_km2c_20261028/vendor/km2b_fixtures.py",
)

def build(stage,destination):
    if stage not in {"S0","S1","S2"}:raise ValueError("invalid source-owned stage")
    originals=source_guards()
    files=set(OWNERS)|set(REPLAY_REQUIRED)
    for p in originals:
        if p.startswith("source_data/"):
            files.add("research/dual_lane_km2i_20261031/"+p)
        else:files.add(p)
    if stage in {"S1","S2"}:
        files.update(str(x.relative_to(ROOT)) for x in (ROOT/UNIT/"results").glob("*")
                     if x.is_file() and not x.name.startswith("HOSTILE_"))
        files.update(str(x.relative_to(ROOT)) for x in (ROOT/UNIT/"figures").glob("*")
                     if x.is_file())
    if stage=="S2":
        files.update((UNIT+"/results/HOSTILE_SAVED_ONCE_SCATTER_AUDIT.json",
                      UNIT+"/S2_FINAL_REPORT_KO.md",UNIT+"/HANDOFF_NEXT_KO.txt"))
    records={}
    for rel in sorted(files):
        p=ROOT/rel
        if not p.is_file():raise FileNotFoundError("KM2N_REPLAY_SOURCE_MISSING "+rel)
        b=p.read_bytes()
        records[rel]={"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)}
    manifest={"schema":"bass.km2n.retarded_first_thomson_P8_source_complete.v1",
              "stage":stage,"git_source_HEAD":os.environ.get("GITHUB_SHA","LOCAL_UNATTESTED"),
              "immutable_parent_HEAD":"2ff05b8416965af0adc7851a8aa60ec2e51b2fee",
              "upper_dag":"9/15","upper_edges":21,"KM2":"PARTIAL",
              "new_upper_completed":0,"production_ready":False,
              "source_original_Git_blobs":originals,"members":records}
    dest=Path(destination);dest.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(dest,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for rel in sorted(files):z.write(ROOT/rel,arcname=rel)
        z.writestr("MANIFEST.json",json.dumps(manifest,sort_keys=True,indent=2)+"\n")
    with zipfile.ZipFile(dest) as z:
        if z.testzip() is not None:raise ArithmeticError("KM2N_ZIP_CRC_FAIL")
        m=json.loads(z.read("MANIFEST.json"))
        for rel,meta in m["members"].items():
            if hashlib.sha256(z.read(rel)).hexdigest()!=meta["sha256"]:
                raise ArithmeticError("KM2N_ZIP_SOURCE_SHA_MISMATCH "+rel)
    print("KM2N_BACKUP",stage,"FILES",len(records),"BYTES",dest.stat().st_size,
          "SHA256",hashlib.sha256(dest.read_bytes()).hexdigest(),flush=True)
    return manifest

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--stage",choices=["S0","S1","S2"],required=True)
    ap.add_argument("--output",type=Path,required=True)
    a=ap.parse_args();build(a.stage,a.output)
