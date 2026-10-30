"""KM2E reproducible S0/S1/S2 source-inclusive ZIP archives with raw physical data."""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED

ROOT=Path(__file__).resolve().parents[2]
HERE=ROOT/"research/dual_lane_km2e_20261030"
OLD=ROOT/"research/dual_lane_km2c_20261028"
PREV=ROOT/"research/dual_lane_km2d_20261030"
SOURCE=[
  "code/curved_tilt.py",
  "vendor/polarization.py","vendor/polarized_dictionary.py",
  "vendor/source_memory.py","vendor/tilted_collision.py",
  "vendor/tilted_history.py","vendor/km2b_fixtures.py",
  "vendor/rest_volterra.py",
]
PHYSICAL_COLS=[
    "n_theta","u","beta_x","beta_y","beta_z","rest_density_ratio",
    "nu_rest_Tstar","rho_gamma","rho_electron_normal",
    "rho_total","q_total_x","q_total_y","q_total_z",
    "source_M_xx","source_M_xy","source_M_zz","raw_force_gap_0",
]
WORK_COLS=[
    "n_theta","u","geometry_energy_rate","geometry_momentum_x",
    "geometry_momentum_y","geometry_momentum_z","raw_force_gap_0",
    "raw_force_gap_x","raw_force_gap_y","raw_force_gap_z",
]


def serialize_csv(fields,rows):
    f=io.StringIO()
    writer=csv.DictWriter(f,fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)
    return f.getvalue().encode("utf-8")


def raw_physical_rows(physics):
    rows=[]; work=[]
    for n,case in sorted(physics["cases"].items(),key=lambda a:int(a[0])):
        for x in case["physical_5epoch_records"]:
            rows.append({
                "n_theta":n,"u":x["u"],
                "beta_x":x["beta"][0],"beta_y":x["beta"][1],"beta_z":x["beta"][2],
                "rest_density_ratio":x["rest_density_ratio"],
                "nu_rest_Tstar":x["nu_rest_Tstar"],"rho_gamma":x["rho_gamma"],
                "rho_electron_normal":x["rho_electron_normal"],
                "rho_total":x["rho_total"],
                **{f"q_total_{letter}":x["q_total"][i] for i,letter in enumerate("xyz")},
                "source_M_xx":x["original_source_electron_M"][0][0],
                "source_M_xy":x["original_source_electron_M"][0][1],
                "source_M_zz":x["original_source_electron_M"][2][2],
                "raw_force_gap_0":x["discrete_force_gap"][0],
            })
        for x in case["normal_time_work"]["time_rows"]:
            work.append({
                "n_theta":n,"u":x["u"],
                "geometry_energy_rate":x["geometry_energy_rate"],
                **{f"geometry_momentum_{letter}":x["geometry_momentum_rate"][i] for i,letter in enumerate("xyz")},
                "raw_force_gap_0":x["discrete_force_gap"][0],
                **{f"raw_force_gap_{letter}":x["discrete_force_gap"][i+1] for i,letter in enumerate("xyz")},
            })
    return serialize_csv(PHYSICAL_COLS,rows), serialize_csv(WORK_COLS,work)


def package(stage,out,result=None):
    if stage not in ("S0","S1","S2"):
        raise ValueError("Stage S0/S1/S2 only")
    files={
        "research/dual_lane_km2e_20261030/S0_THEORY_KO.md":(HERE/"S0_THEORY_KO.md").read_bytes(),
    }
    # Both newly developed and directly inherited original science, independently
    # extractable from the archive. Never substitute production source.
    for name in SOURCE:
        files["original_KM2C/"+name]=(OLD/name).read_bytes()
    files["original_KM2D/accelerating_tilt.py"]=(PREV/"accelerating_tilt.py").read_bytes()
    if stage in ("S1","S2"):
        if result is None or not result.is_file():
            raise FileNotFoundError("Actual science JSON is required before S1/S2 packaging")
        physics=json.loads(result.read_text())
        if physics["upper_dag"]!="9/15" or physics["km2"]!="PARTIAL":
            raise ValueError("Authoritative scientific DAG changed")
        samples,works=raw_physical_rows(physics)
        files.update({
            "research/dual_lane_km2e_20261030/coupled_electron_photon.py":(HERE/"coupled_electron_photon.py").read_bytes(),
            "research/dual_lane_km2e_20261030/tests/test_coupled_physics.py":(HERE/"tests/test_coupled_physics.py").read_bytes(),
            "research/dual_lane_km2e_20261030/package_artifacts.py":(HERE/"package_artifacts.py").read_bytes(),
            "results/real_full_physical_science.json":result.read_bytes(),
            "results/normal_photon_and_electron_5epoch.csv":samples,
            "results/normal_total_stress_energy_work_GL24.csv":works,
        })
    if stage=="S2":
        for filename in ("S2_FINAL_REPORT_KO.md","DAG_DELTA.json","HANDOFF_NEXT_KO.txt","DELIVERY_RECEIPTS.json"):
            p=HERE/filename
            if p.exists():
                files["research/dual_lane_km2e_20261030/"+filename]=p.read_bytes()
    meta={
        "schema":"bass.km2e.original_photon_cold_electron_evolution_backup.v1",
        "stage":stage,
        "immutable_parent_pr274":"8993bdf97c5aca2961a7d2e1df08bd4119899670",
        "parent_KM2D_blob":"b599d3842e843d8de1de1499b73e6849374bf8f8",
        "physical_model":"Full original polarized KM2 photon carrier + homogeneous cold electron dust momentum & number, reciprocal Thomson; prescribed Bianchi I only",
        "upper_dag":"9/15","km2":"PARTIAL","production_ready":False,
        "member_sha256":{}
    }
    out.parent.mkdir(parents=True,exist_ok=True)
    with ZipFile(out,"w",compression=ZIP_DEFLATED,compresslevel=6) as z:
        for filename,data in sorted(files.items()):
            z.writestr(filename,data)
            meta["member_sha256"][filename]=hashlib.sha256(data).hexdigest()
        z.writestr("MANIFEST.json",json.dumps(meta,indent=2,sort_keys=True)+"\n")
    with ZipFile(out) as z:
        if z.testzip() is not None:raise RuntimeError("ZIP CRC FAIL")
        manifest=json.loads(z.read("MANIFEST.json"))
        for filename,digest in manifest["member_sha256"].items():
            if hashlib.sha256(z.read(filename)).hexdigest()!=digest:
                raise RuntimeError("ZIP payload member SHA mismatch "+filename)
    print("KM2E_STAGE_ARCHIVE",json.dumps({
        "stage":stage,"outer_container_not_yet_artifact":str(out),
        "inner_bytes":out.stat().st_size,
        "inner_sha256":hashlib.sha256(out.read_bytes()).hexdigest(),
        "payload_members":len(meta["member_sha256"]),
        "zip_crc":"PASS","member_SHA256":"PASS","upper_dag":"9/15",
    },sort_keys=True),flush=True)


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--stage",required=True,choices=("S0","S1","S2"))
    ap.add_argument("--output",type=Path,required=True)
    ap.add_argument("--results",type=Path)
    args=ap.parse_args()
    package(args.stage,args.output,args.results)
