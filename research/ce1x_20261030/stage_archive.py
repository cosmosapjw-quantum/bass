"""CE1-X reproducible S0/S1/S2 ZIP files with SHA256 member manifest."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/"research/ce1x_20261030"


def digest(x:bytes)->str:
    return hashlib.sha256(x).hexdigest()


def make(stage,folder):
    folder=Path(folder)
    folder.mkdir(parents=True,exist_ok=True)
    s0={"research/ce1x_20261030/S0_THEORY_KO.md":BASE/"S0_THEORY_KO.md",
        "research/ce1x_20261030/certify_l4.py":BASE/"certify_l4.py"}
    s1={
        **s0,
        "research/ce1x_20261030/rust_l4_parity.py":BASE/"rust_l4_parity.py",
        "research/ce1x_20261030/tests/test_l4.py":BASE/"tests/test_l4.py",
        "research/ce1x_20261030/stage_archive.py":BASE/"stage_archive.py",
        ".github/workflows/ce1x-l4-certificate.yml":ROOT/".github/workflows/ce1x-l4-certificate.yml",
        "results/real_time_mpfr.json":folder/"real_time_mpfr.json",
        "results/l4_source_and_transfer.json":folder/"l4_source_and_transfer.json",
        "results/rust_l4.json":folder/"rust_l4.json",
        "checkpoints/S0.zip":folder/"BASS_CE1X_S0.zip"}
    s2={
        **s1,
        "checkpoints/S1.zip":folder/"BASS_CE1X_S1.zip",
        "research/ce1x_20261030/S2_REPORT_KO.md":folder/"S2_REPORT_KO.md",
        "research/ce1x_20261030/HANDOFF_NEXT_KO.txt":folder/"HANDOFF_NEXT_KO.txt",
        "research/ce1x_20261030/DAG_DELTA.json":folder/"DAG_DELTA.json"}
    if stage=="S2":
        source=json.loads((folder/"l4_source_and_transfer.json").read_text())
        rust=json.loads((folder/"rust_l4.json").read_text())
        out=[
            "# CE1-X | BASS native Rust and exact-rational l4 sky cross-kernel",
            "",
            "Original positive six-cell, massless collisionless expanding diagonal Bianchi I Lambda0.",
            "Proper u=t/Tstar on [0,.08], metric (-,+,+,+), original h target 1e-5.",
            "Three reflection-even l4 components are a40,a42,a44.",
            "Source bound uses exact Q(sqrt2,pi) moments to total degree14, K12 binomial tail",
            "and exact binary64 GL6/GL8 stored ray non-unit correction.",
            "",
            "| Source | source-only K4 upper | 4-panel full K4 upper | 8-panel | 16-panel |",
            "|---|---:|---:|---:|---:|"]
        for n in (6,8):
            v=source["cases"][str(n)]
            m=v["time_path_cases"]
            out.append("| GL"+str(n)+" | "+v["source_only_cross_kernel_error_ceil_27"]+
                    " | "+" | ".join(m[str(k)]["total_cross_kernel_upper_ceil_27"] for k in (4,8,16))+" |")
        out.extend([
            "",
            "The full bound is source K4 plus 246 times the freshly recertified",
            "full-time MPFR192 RK4/Hermite logscale error of the EXACT same stored path.",
            "It is uniform for any two proper-time epochs within the scoped horizon.",
            "Six native BASS Rust trajectories each had 41 sky snapshots and were",
            "independently compared with NumPy Condon-Shortley l4 harmonics.",
            "The Rust binary64 comparison is NOT an MPFR interval certificate.",
            "Numerical DOP853 observational-sky data from PR269 are NOT certified",
            "by the separate original MPFR RK4/Hermite geometry path.",
            "",
            "Original top DAG 9/15, CE1 PARTIAL. Independent distinct-author R6/C9",
            "and formal all-program MPFR/Rust proofs NOT_RUN. No automatic merge",
            "or production/CMB T/Q/U observational promotion.",
        ])
        (folder/"S2_REPORT_KO.md").write_text("\n".join(out)+"\n")
        handoff=[
          "$physmath-research-loop","PROJECT=BASS",
          "REPO=cosmosapjw-quantum/bass",
          "UNIT=CE1X_L4_EXACT_SOURCE_TWO_TIME_MPFR_RUST",
          "PARENT_PR=268",
          "PARENT_HEAD=c4d303ebd8294df8a4b564b140b88fc8e57b0e67",
          "SIBLING_REFERENCE_PR=269","UPPER_DAG=9/15","CE1=PARTIAL",
          "ORIGINAL_PHYSICS_SIX_POSITIVE_CELLS_SHA=022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035",
          "BASS_NATIVE_RUST_BLOB=a29b12b5e7b0d529bddaf9eac53cfdb984ddaa84",
          "RUSTC=1.94.1",
          "L4_REAL_COMPONENTS=a40,a42,a44",
          "SOURCE_MOMENT_DEGREE=14",
          "SOURCE_K12_EXACT_RATIONAL=true",
          "MPFR192_RK4_HERMITE_4_8_16=FRESH_IN_CI",
          "PRODUCTION_READY=false","MERGE_READY=false","AUTO_NEXT=false",
        ]
        for n in (6,8):
            v=source["cases"][str(n)]
            handoff.append("GL"+str(n)+"_SOURCE_ONLY_K4="+v["source_only_cross_kernel_error_ceil_27"])
            for k in (4,8,16):
                handoff.append("GL"+str(n)+"_STEPS"+str(k)+"_K4_TOTAL="+
                               v["time_path_cases"][str(k)]["total_cross_kernel_upper_ceil_27"])
        handoff.extend([
          "READ_FIRST:",
          "research/ce1x_20261030/S0_THEORY_KO.md",
          "research/ce1x_20261030/certify_l4.py",
          "research/ce1x_20261030/S2_REPORT_KO.md",
          "research/ce1x_20261030/HANDOFF_NEXT_KO.txt",
          "research/ce1x_20261030/DELIVERY_RECEIPTS.json",
          "NEXT:",
          "1. Verify final PR HEAD CI and all staged Git Drive Dropbox identities.",
          "2. Retain GL6/GL8 exact l4 source bounds and matched MPFR geometry carriers.",
          "3. Use original BASS Rust as physical differential, not MPFR certificate.",
          "4. Select genuine incomplete observational interface or distinct-author R6/C9.",
          "5. Do not transfer MPFR proof to unverified DOP853 or temperature/CMB likelihood.",
          "6. Keep original top DAG 9/15 until actual parent admission; no auto merge.",
          "STOP_AFTER_ONE_BOUNDED_UNIT=true",
        ])
        (folder/"HANDOFF_NEXT_KO.txt").write_text("\n".join(handoff)+"\n")
        (folder/"DAG_DELTA.json").write_text(json.dumps({
            "unit":"CE1X","upper_dag":{"completed":9,"total":15,"edges":21,"ce1":"PARTIAL"},
            "new_top_nodes_completed":0,
            "exact_l4_source_results":source,
            "native_rust_scoped_results":rust,
            "production_ready":False,"merge_ready":False,"auto_next":False,
            "distinct_author_R6_C9":"NOT_RUN","formal_program_proof":"NOT_RUN"},indent=2)+"\n")
    use={"S0":s0,"S1":s1,"S2":s2}[stage]
    members={key:p.read_bytes() for key,p in use.items()}
    if stage in ("S1","S2"):
        for file in sorted((folder/"rust_raw").glob("*_BASS_RUST_SKY.csv")):
            members["results/raw_rust/"+file.name]=file.read_bytes()
    manifest={k:digest(v) for k,v in members.items()}
    members["MANIFEST_SHA256.json"]=(json.dumps(manifest,indent=2)+"\n").encode()
    output=folder/("BASS_CE1X_"+stage+".zip")
    with zipfile.ZipFile(output,"w",zipfile.ZIP_DEFLATED) as z:
        for name,payload in members.items():
            z.writestr(name,payload)
    with zipfile.ZipFile(output) as z:
        assert z.testzip() is None
        assert all(digest(z.read(name))==value for name,value in manifest.items())
    print("CE1X_"+stage+"_ZIP_PASS",str(output),output.stat().st_size,
          digest(output.read_bytes()),len(members),flush=True)


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--stage",choices=["S0","S1","S2"],required=True)
    p.add_argument("--output",required=True)
    args=p.parse_args()
    make(args.stage,args.output)
