"""Immutable, source-inclusive KM-2D S0/S1/S2 physics evidence ZIPs."""
from __future__ import annotations

import argparse, hashlib, json, csv
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT=Path(__file__).resolve().parents[2]
HERE=ROOT/"research/dual_lane_km2d_20261030"
OLD=ROOT/"research/dual_lane_km2c_20261028"
SOURCE=[
    "code/curved_tilt.py",
    "vendor/polarization.py",
    "vendor/polarized_dictionary.py",
    "vendor/source_memory.py",
    "vendor/tilted_collision.py",
    "vendor/tilted_history.py",
    "vendor/km2b_fixtures.py",
    "vendor/rest_volterra.py",
]
FIELDS=["panels","u","Mzz_direct","Mzz_volterra","Mxy_direct","Mxy_volterra",
        "max_carrier_abs_error","max_source_abs_error","rho_direct","C_direct"]

def physical_rows_csv(result):
    import io
    f=io.StringIO()
    w=csv.DictWriter(f,fieldnames=FIELDS)
    w.writeheader()
    for panels,obs in sorted(result["cases"].items(),key=lambda kv:int(kv[0])):
        for row in obs["source_rows"]:
            w.writerow({key:panels if key=="panels" else row[key] for key in FIELDS})
    return f.getvalue().encode("utf-8")

def build(stage,output,result_file=None):
    if stage not in ("S0","S1","S2"):
        raise ValueError("S0/S1/S2 only")
    files={"research/dual_lane_km2d_20261030/S0_THEORY_KO.md":
            (HERE/"S0_THEORY_KO.md").read_bytes()}
    for relative in SOURCE:
        files[f"original_KM2C_immutable/{relative}"]=(OLD/relative).read_bytes()
    if stage in ("S1","S2"):
        if result_file is None or not result_file.exists():
            raise FileNotFoundError("Verified physical science JSON is required")
        results=json.loads(result_file.read_text())
        if results["upper_DAG"]!="9/15" or results["KM2"]!="PARTIAL":
            raise ValueError("Upper DAG authority changed")
        files.update({
            "research/dual_lane_km2d_20261030/accelerating_tilt.py":
                (HERE/"accelerating_tilt.py").read_bytes(),
            "research/dual_lane_km2d_20261030/tests/test_accelerating_tilt.py":
                (HERE/"tests/test_accelerating_tilt.py").read_bytes(),
            "research/dual_lane_km2d_20261030/package_artifacts.py":
                (HERE/"package_artifacts.py").read_bytes(),
            "results/physical_science.json":result_file.read_bytes(),
            "results/physical_angular_moments.csv":physical_rows_csv(results),
        })
    if stage=="S2":
        for name in ("S2_FINAL_REPORT_KO.md","HANDOFF_NEXT_KO.txt","DAG_DELTA.json"):
            p=HERE/name
            if p.exists():
                files[f"research/dual_lane_km2d_20261030/{name}"]=p.read_bytes()
    manifest={
        "schema":"bass.km2d.physical_stage_archive.v1",
        "stage":stage,
        "repo":"cosmosapjw-quantum/bass",
        "parent_PR273_head":"48e6c979c49a49ff6854a9555fe97a9690d86d16",
        "source_code_bass_KM2C_git_blob":"05aade3aab7e9a32c11608882c943e4d3cb6f379",
        "scientific_scope":"time-varying externally prescribed beta normal-time cold Thomson Bianchi I; no Einstein feedback",
        "upper_dag":"9/15","KM2":"PARTIAL","production_ready":False,
        "member_sha256":{},
    }
    output.parent.mkdir(parents=True,exist_ok=True)
    with ZipFile(output,"w",ZIP_DEFLATED,compresslevel=6) as f:
        for name,data in sorted(files.items()):
            f.writestr(name,data)
            manifest["member_sha256"][name]=hashlib.sha256(data).hexdigest()
        f.writestr("MANIFEST.json",json.dumps(manifest,indent=2,sort_keys=True)+"\n")
    with ZipFile(output) as f:
        if f.testzip():
            raise RuntimeError("ZIP CRC failure")
        saved=json.loads(f.read("MANIFEST.json"))
        for name,digest in saved["member_sha256"].items():
            if hashlib.sha256(f.read(name)).hexdigest()!=digest:
                raise RuntimeError("ZIP inner SHA mismatch "+name)
    print("KM2D_STAGE_ZIP",json.dumps({
        "stage":stage,"bytes":output.stat().st_size,"sha256":hashlib.sha256(output.read_bytes()).hexdigest(),
        "member_count":len(manifest["member_sha256"]),"zip_crc":"PASS","member_SHA256":"PASS",
        "upper_dag":"9/15"},sort_keys=True),flush=True)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--stage",required=True,choices=["S0","S1","S2"])
    p.add_argument("--output",required=True,type=Path)
    p.add_argument("--results",type=Path)
    a=p.parse_args()
    build(a.stage,a.output,a.results)
