"""Build a temporary Cargo Rust bridge against the *actual owner crate*, read-only.

No file inside rei_bianchi is touched. Cargo target and manifest live outside
the owner repo and the bridge passes exact frozen scenario parameters as CLI.
The actual checked owner source SHA is part of each receipt.
"""
from __future__ import annotations
import csv,hashlib,io,json,os,subprocess,tempfile
from pathlib import Path
import numpy as np
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from axbi_provider import Background,Family,_read_lock

SOURCE_SHA="65f10dced178aa85bb1c92da0b35350a0eec2d3d3de05630c900b5df4ec1e254"
GEOMETRY_SHA="0c0bb17168b36a67af6e3e2a3ada835bc77db3dbc73d06e13075f6019ec11289"

def read_owner(repo:Path):
    repo=repo.expanduser().resolve()
    crate=repo/"rust/rei_microphysics"
    src=crate/"src/axbi_background.rs"
    g=crate/"src/bianchi_i.rs"
    if hashlib.sha256(src.read_bytes()).hexdigest()!=SOURCE_SHA:
        raise RuntimeError("RUST_OWNER_SOURCE_CHANGED_NO_PARITY_AUTHORITY")
    if hashlib.sha256(g.read_bytes()).hexdigest()!=GEOMETRY_SHA:
        raise RuntimeError("RUST_OWNER_GEOMETRY_CHANGED_NO_PARITY_AUTHORITY")
    head=subprocess.check_output(["git","-C",str(repo),"rev-parse","HEAD"],text=True).strip()
    return crate,head

def independent_rust_parity(repo:Path,output:Path,buildroot:Path,panels:int=4096):
    if output.exists():raise FileExistsError(output)
    crate,head=read_owner(repo)
    buildroot=buildroot.resolve()
    if buildroot.is_relative_to(repo.resolve()):
        raise ValueError("Rust build must not touch owner directory")
    lock=_read_lock();cos=lock["cosmology"];clk=lock["clock"]
    with tempfile.TemporaryDirectory(prefix="bass_axbi_rei_rust_bridge_") as tmp:
        root=Path(tmp)
        (root/"src").mkdir()
        manifest=f'''[package]
name="bass_axbi_rei_rust_bridge"
version="0.1.0"
edition="2021"
[dependencies]
rei_microphysics={{path="{crate.as_posix()}"}}
'''
        (root/"Cargo.toml").write_text(manifest)
        (root/"src/main.rs").write_bytes((HERE/"rust_bridge/src/main.rs").read_bytes())
        env=os.environ.copy()
        env["CARGO_TARGET_DIR"]=str(buildroot)
        env.setdefault("CARGO_BUILD_JOBS","2")
        env["CARGO_NET_OFFLINE"]="true"
        cmd=["cargo","run","--release","--offline","--manifest-path",str(root/"Cargo.toml"),"--",
             str(cos["H0_per_s"]),str(cos["Omega_m"]),str(cos["Omega_r"]),
             str(cos["Omega_lambda"]),str(clk["a_ref"]),str(clk["a_end"]),str(panels)]
        p=subprocess.run(cmd,text=True,capture_output=True,env=env)
    if p.returncode!=0:
        raise RuntimeError(f"ACTUAL_REI_RUST_BUILD_OR_EXEC_FAILED:{p.stderr[-2000:]}")
    rows=list(csv.DictReader(io.StringIO(p.stdout)))
    if len(rows)!=30:raise RuntimeError(f"owner Rust row count !=30 {len(rows)}")
    out=[]
    for r in rows:
        q=float(r["q"]);family=r["family"];a=float(r["a"])
        py=Background(Family(q,family)).at_a(a)
        t=float(r["t_s"]);b=float(r["b"])
        dtime=abs(py["proper_elapsed_s"]-t)
        trel=dtime/max(1,abs(t))
        db=abs(py["b"]-b)
        dh=abs(py["H_mean_per_s"]/float(r["H_mean"])-1)
        ds=abs(py["shear_s_per_s"]-float(r["s"]))
        dgeo=max(abs(py["a_perp"]-float(r["a_perp"])),abs(py["a_parallel"]-float(r["a_parallel"])))
        out.append({"family":family,"q":q,"fraction":float(r["fraction"]),"a":a,
                    "rust_t_s":t,"python_t_s":py["proper_elapsed_s"],
                    "rust_b":b,"python_b":py["b"],
                    "abs_dt_s":dtime,"relative_dt":trel,"absolute_db":db,
                    "relative_H":dh,"absolute_s_s":ds,"abs_geometry":dgeo})
    tmax=max(x["relative_dt"] for x in out)
    bmax=max(x["absolute_db"] for x in out)
    if tmax>4e-11 or bmax>2e-10:
        raise ArithmeticError(f"REAL_REI_RUST_BACKGROUND_MISMATCH time:{tmax} b:{bmax}")
    obj={"schema":"bass.rei.axbi.rust_actual_source_parity.v1","owner_git_HEAD":head,
         "original_rust_sha256":SOURCE_SHA,"original_geometry_sha256":GEOMETRY_SHA,
         "rust_actual_command_type":"cargo run --release --offline from TEMP Cargo project with path dependency and separate target; original owner sources read-only",
         "cargo_exit_code":0,"panels":panels,"case_count":6,"rows_count":len(out),
         "max_relative_proper_time_diff":tmax,"max_abs_b_diff":bmax,
         "max_H_relative_diff":max(x["relative_H"] for x in out),
         "max_a_geometry_abs_diff":max(x["abs_geometry"] for x in out),
         "rust_stdout_sha256":hashlib.sha256(p.stdout.encode()).hexdigest(),
         "rust_stderr_sha256":hashlib.sha256(p.stderr.encode()).hexdigest(),
         "source_contract":"real owner AxbiBackground, no assumed provider defaults",
         "production_REI_science_admission":"NOT_ISSUED",
         "rows":out}
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(obj,indent=2)+"\n")
    print(json.dumps({k:v for k,v in obj.items() if k!="rows"},indent=2))
    return obj

if __name__=="__main__":
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument("--rei-repo",type=Path,required=True)
    parser.add_argument("--target-dir",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    independent_rust_parity(args.rei_repo,args.output,args.target_dir)
