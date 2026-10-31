"""S0/S1/S2 original-BASS-source complete KM2L physical archive with SHA/CRC readback."""
from __future__ import annotations
import argparse,hashlib,json,os,zipfile
from pathlib import Path
from research.dual_lane_km2l_20261031.thomson_lya import original_source_guards

ROOT=Path(__file__).resolve().parents[2]
UNIT="research/dual_lane_km2l_20261031"
BASE=(
  UNIT+"/S0_THEORY_KO.md", UNIT+"/thomson_lya.py",
  UNIT+"/tests/test_thomson_lya.py", UNIT+"/make_plots.py",
  UNIT+"/hostile_saved_audit.py", UNIT+"/generate_report.py",
  UNIT+"/ARCHIVE_BUILD.py", UNIT+"/DAG_DELTA.json",
  ".github/workflows/km2l-unscattered-thomson.yml",
)
# Include original KM2K parent direct Python import dependencies.
# It is source-complete, no user-native older P8 source rewriting.
ORIGINAL_IMPORTED=(
  "research/dual_lane_km2c_20261028/vendor/polarization.py",
  "research/dual_lane_km2c_20261028/vendor/polarized_dictionary.py",
  "research/dual_lane_km2c_20261028/vendor/km2b_fixtures.py",
)

def archive(stage,dest):
    if stage not in {"S0","S1","S2"}:raise ValueError("unknown bounded stage")
    roots=original_source_guards()
    paths=set(BASE)|set(ORIGINAL_IMPORTED)
    for p in roots:
        paths.add(("research/dual_lane_km2i_20261031/" + p)
                  if p.startswith("source_data/") else p)
    if stage in {"S1","S2"}:
        paths.update(str(x.relative_to(ROOT)) for x in (ROOT/UNIT/"results").glob("*")
                     if x.is_file() and not x.name.startswith("HOSTILE"))
        paths.update(str(x.relative_to(ROOT)) for x in (ROOT/UNIT/"figures").glob("*") if x.is_file())
    if stage=="S2":
        paths.update((UNIT+"/results/HOSTILE_SAVED_THOMSON_AUDIT.json",
                      UNIT+"/S2_FINAL_REPORT_KO.md",
                      UNIT+"/HANDOFF_NEXT_KO.txt"))
    members={}
    for name in sorted(paths):
        f=ROOT/name
        if not f.is_file():raise FileNotFoundError("SOURCE_BACKUP_REQUIRED "+name)
        data=f.read_bytes()
        members[name]={"sha256":hashlib.sha256(data).hexdigest(),"bytes":len(data)}
    manifest={"schema":"bass.km2l.source_complete.v1",
              "source_git_head":os.getenv("GITHUB_SHA","local_unattested"),
              "parent_head":"e216d708890c8321d2f6a2e146e60e7e01cea1ce",
              "stage":stage,"upper_dag":"9/15","km2":"PARTIAL",
              "production_ready":False,"source_blobs":roots,"members":members}
    dest=Path(dest);dest.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(dest,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for name in sorted(members):z.write(ROOT/name,arcname=name)
        z.writestr("MANIFEST.json",json.dumps(manifest,sort_keys=True,indent=2)+"\n")
    with zipfile.ZipFile(dest) as z:
        if z.testzip() is not None:raise ArithmeticError("ZIP_CRC_FAILED")
        read=json.loads(z.read("MANIFEST.json"))
        for n,a in read["members"].items():
            if hashlib.sha256(z.read(n)).hexdigest()!=a["sha256"]:
                raise ArithmeticError("STORED_SOURCE_SHA_MISMATCH "+n)
    print("KM2L_BACKUP",stage,"members",len(members),
          "bytes",dest.stat().st_size,
          "sha256",hashlib.sha256(dest.read_bytes()).hexdigest(),flush=True)
    return manifest

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--stage",required=True,choices=["S0","S1","S2"])
    p.add_argument("--output",required=True,type=Path)
    a=p.parse_args();archive(a.stage,a.output)
