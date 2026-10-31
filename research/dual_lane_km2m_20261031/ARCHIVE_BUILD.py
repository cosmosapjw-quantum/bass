"""Stage S0/S1/S2 original P8 physics source-complete KM2M archive, exact SHA and ZIP CRC."""
from __future__ import annotations
import argparse,hashlib,json,os,zipfile
from pathlib import Path

from research.dual_lane_km2m_20261031.first_gain import source_guards

ROOT=Path(__file__).resolve().parents[2]
UNIT="research/dual_lane_km2m_20261031"
BASE=(
 UNIT+"/S0_THEORY_KO.md",UNIT+"/first_gain.py",
 UNIT+"/tests/test_first_gain.py",UNIT+"/hostile_saved_audit.py",
 UNIT+"/make_plots.py",UNIT+"/generate_report.py",
 UNIT+"/ARCHIVE_BUILD.py",UNIT+"/DAG_DELTA.json",
 ".github/workflows/km2m-polarized-first-gain.yml",
)
ORIGINAL_VENDOR=(
 "research/dual_lane_km2c_20261028/vendor/polarization.py",
 "research/dual_lane_km2c_20261028/vendor/polarized_dictionary.py",
 "research/dual_lane_km2c_20261028/vendor/km2b_fixtures.py",
)
def run(stage,dest):
    if stage not in {"S0","S1","S2"}:
        raise ValueError("unknown bounded research stage")
    owners=source_guards()
    names=set(BASE)|set(ORIGINAL_VENDOR)
    for p in owners:
        if p.startswith("source_data/"):
            names.add("research/dual_lane_km2i_20261031/"+p)
        else:names.add(p)
    if stage in ("S1","S2"):
        names.update(str(x.relative_to(ROOT)) for x in (ROOT/UNIT/"results").glob("*")
                     if x.is_file() and not x.name.startswith("HOSTILE_"))
        names.update(str(x.relative_to(ROOT)) for x in (ROOT/UNIT/"figures").glob("*")
                     if x.is_file())
    if stage=="S2":
        names.update([UNIT+"/results/HOSTILE_SAVED_FIRST_GAIN_AUDIT.json",
                      UNIT+"/S2_FINAL_REPORT_KO.md",UNIT+"/HANDOFF_NEXT_KO.txt"])
    member={}
    for name in sorted(names):
        f=ROOT/name
        if not f.is_file():raise FileNotFoundError("SOURCExPHYSICS_NOT_COMPLETE "+name)
        b=f.read_bytes()
        member[name]={"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)}
    manifest={"schema":"bass.km2m.original_first_polarized_gain.source_complete.v1",
              "source_HEAD":os.getenv("GITHUB_SHA","LOCAL_NOT_REMOTE_ATTESTED"),
              "immutable_parent_HEAD":"8a1e09f6176166595b33810d3ce0c1f18afb245f",
              "stage":stage,"upper_dag":"9/15","KM2":"PARTIAL",
              "production_ready":False,"source_blobs":owners,"members":member}
    dest=Path(dest);dest.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(dest,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for name in sorted(member):
            z.write(ROOT/name,arcname=name)
        z.writestr("MANIFEST.json",json.dumps(manifest,sort_keys=True,indent=2)+"\n")
    with zipfile.ZipFile(dest,"r") as z:
        if z.testzip() is not None:raise ArithmeticError("ARCHIVE_CRC_FAILURE")
        data=json.loads(z.read("MANIFEST.json"))
        for name,m in data["members"].items():
            if hashlib.sha256(z.read(name)).hexdigest()!=m["sha256"]:
                raise ArithmeticError("ARCHIVE_SOURCE_SHA256_MISMATCH "+name)
    print("KM2M_BACKUP",stage,"members",len(member),"bytes",
          dest.stat().st_size,"sha256",
          hashlib.sha256(dest.read_bytes()).hexdigest(),flush=True)
    return manifest

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--stage",required=True,choices=["S0","S1","S2"])
    p.add_argument("--output",required=True,type=Path)
    a=p.parse_args();run(a.stage,a.output)
