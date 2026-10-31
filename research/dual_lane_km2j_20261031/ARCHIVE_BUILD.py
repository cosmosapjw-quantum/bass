"""Source-complete scoped archive of original immutable BASS inputs and KM2J run."""
from __future__ import annotations
import argparse,hashlib,json,os,zipfile
from pathlib import Path
from research.dual_lane_km2j_20261031.coupled_chem_p8 import guard_all

ROOT=Path(__file__).resolve().parents[2]
DIR=Path(__file__).resolve().parent
UNIT="research/dual_lane_km2j_20261031"
BASE=(
  UNIT+"/S0_THEORY_KO.md",
  UNIT+"/coupled_chem_p8.py",
  UNIT+"/tests/test_coupled_chem_p8.py",
  UNIT+"/make_plots.py",
  UNIT+"/ARCHIVE_BUILD.py",
  ".github/workflows/km2j-coupled-chem-p8.yml",
)
RESULT=UNIT+"/results/KM2J_COUPLED_PHYSICS_2GRID.json"
FIG=UNIT+"/figures"

def make(stage,out):
    sources=guard_all()
    paths=set(sources)|set(BASE)
    if stage in ("S1","S2"):
        paths.add(RESULT)
        paths.update(str(p.relative_to(ROOT)) for p in (ROOT/FIG).glob("*") if p.is_file())
    if stage=="S2":
        paths.add(UNIT+"/S2_FINAL_REPORT_KO.md")
        paths.add(UNIT+"/HANDOFF_NEXT_KO.txt")
        paths.add(UNIT+"/DAG_DELTA.json")
    records={}
    for rel in sorted(paths):
        f=ROOT/rel
        if not f.is_file():raise FileNotFoundError(f"not source complete {rel}")
        b=f.read_bytes()
        records[rel]={"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)}
    manifest={"schema":"bass.km2j.source_complete.v1",
              "parent_head":"8e3cf0ac1eab96142494903ed940e27d1b66e380",
              "stage":stage,"github_run_sha":os.environ.get("GITHUB_SHA","local_not_attested"),
              "sources":records,"source_guards":sources,
              "upper_dag":"9/15","KM2":"PARTIAL","production_ready":False}
    out=Path(out);out.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(out,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for rel in sorted(records):z.write(ROOT/rel,arcname=rel)
        z.writestr("MANIFEST.json",json.dumps(manifest,indent=2,sort_keys=True)+"\n")
    with zipfile.ZipFile(out) as z:
        if z.testzip() is not None:raise ArithmeticError("source archive CRC failure")
        got=json.loads(z.read("MANIFEST.json"))
        for name,item in got["sources"].items():
            if hashlib.sha256(z.read(name)).hexdigest()!=item["sha256"]:
                raise ArithmeticError(f"source archive payload SHA failed {name}")
    print("KM2J_BACKUP",stage,"paths",len(records),"archive_bytes",out.stat().st_size,
          "sha256",hashlib.sha256(out.read_bytes()).hexdigest(),flush=True)
    return manifest

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--stage",choices=("S0","S1","S2"),required=True)
    ap.add_argument("--output",type=Path,required=True)
    a=ap.parse_args();make(a.stage,a.output)
