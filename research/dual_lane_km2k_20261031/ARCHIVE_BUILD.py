"""KM2K stage source ZIP preserving original KM2J and lower original P8 vendor."""
from __future__ import annotations
import argparse,hashlib,json,os,zipfile
from pathlib import Path
from research.dual_lane_km2k_20261031.escaping_lya import exact_parent_sources

ROOT=Path(__file__).resolve().parents[2]
UNIT="research/dual_lane_km2k_20261031"
SELF=(
    UNIT+"/S0_THEORY_KO.md",UNIT+"/frequency_core.py",
    UNIT+"/escaping_lya.py",UNIT+"/make_plots.py",
    UNIT+"/tests/test_escape_spectra.py",
    UNIT+"/hostile_saved_spectral_audit.py",
    UNIT+"/generate_report.py",UNIT+"/ARCHIVE_BUILD.py",
    UNIT+"/DAG_DELTA.json",".github/workflows/km2k-escaped-lya-spectra.yml",
)
# The parent KM2J S2 ZIP had omitted these *import-required* existing vendor
# sources; preserve them without modifying originals, to permit clean replay.
ADDITIONAL_ORIGINALS=(
    "research/dual_lane_km2c_20261028/vendor/polarization.py",
    "research/dual_lane_km2c_20261028/vendor/polarized_dictionary.py",
    "research/dual_lane_km2c_20261028/vendor/km2b_fixtures.py",
)
def archive(stage,dest):
    s=exact_parent_sources()
    paths=set(SELF)|set(ADDITIONAL_ORIGINALS)
    for p in s:
        if p.startswith("source_data/"):
            paths.add("research/dual_lane_km2i_20261031/"+p)
        else:paths.add(p)
    if stage in ("S1","S2"):
        paths.update(str(p.relative_to(ROOT))
            for p in (ROOT/UNIT/"results").glob("*")
            if p.is_file() and not p.name.startswith("HOSTILE_"))
        paths.update(str(p.relative_to(ROOT))
            for p in (ROOT/UNIT/"figures").glob("*") if p.is_file())
    if stage=="S2":
        paths.update({UNIT+"/results/HOSTILE_INDEPENDENT_SPECTRAL_AUDIT.json",
                      UNIT+"/S2_FINAL_REPORT_KO.md",UNIT+"/HANDOFF_NEXT_KO.txt"})
    manifest={}
    for rel in sorted(paths):
        path=ROOT/rel
        if not path.is_file():raise FileNotFoundError(rel)
        raw=path.read_bytes()
        manifest[rel]={"sha256":hashlib.sha256(raw).hexdigest(),"bytes":len(raw)}
    index={"schema":"bass.km2k.escaped_lya_source_bundle.v1",
           "source_commit":os.getenv("GITHUB_SHA","LOCAL_UNATTESTED"),
           "immutable_parent_HEAD":"63147c01f1b1fd3f0cf698c919db25d9bd2ef80b",
           "stage":stage,"upper_dag":"9/15","km2":"PARTIAL",
           "new_upper_completed":0,"production":False,
           "members":manifest}
    dest=Path(dest);dest.parent.mkdir(exist_ok=True,parents=True)
    with zipfile.ZipFile(dest,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for rel in sorted(paths):z.write(ROOT/rel,arcname=rel)
        z.writestr("MANIFEST.json",json.dumps(index,indent=2,sort_keys=True)+"\n")
    with zipfile.ZipFile(dest,"r") as z:
        if z.testzip() is not None:raise ArithmeticError("SCOPE_SOURCE_ZIP_CRC_FAILED")
        stored=json.loads(z.read("MANIFEST.json"))
        for name,obj in stored["members"].items():
            if hashlib.sha256(z.read(name)).hexdigest()!=obj["sha256"]:
                raise ArithmeticError("SOURCE_ZIP_SHA256_MISMATCH "+name)
    print("KM2K_BACKUP",stage,len(manifest),dest.stat().st_size,
          hashlib.sha256(dest.read_bytes()).hexdigest(),flush=True)
    return index

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--stage",choices=["S0","S1","S2"],required=True)
    ap.add_argument("--output",type=Path,required=True)
    a=ap.parse_args();archive(a.stage,a.output)
