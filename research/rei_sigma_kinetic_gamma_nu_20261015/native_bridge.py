"""Actual source-pinned native REI BackgroundPoint bridge, including negative controls."""
from __future__ import annotations
import argparse,hashlib,json,os,subprocess,tempfile
from pathlib import Path
from joint_kinetic import source_lock,sha256_file,AX03_SOURCE_SHA,verify_original_sources
HERE=Path(__file__).resolve().parent
OWN_REI_SHA="65f10dced178aa85bb1c92da0b35350a0eec2d3d3de05630c900b5df4ec1e254"
OWN_GEOMETRY_SHA="0c0bb17168b36a67af6e3e2a3ada835bc77db3dbc73d06e13075f6019ec11289"

def run(repo:Path,output:Path,target:Path):
    if output.exists():raise FileExistsError(output)
    verify_original_sources()
    repo=repo.resolve();target=target.resolve()
    if target.is_relative_to(repo):
        raise ValueError("keep cargo build outside original REI owner")
    crate=repo/"rust/rei_microphysics"
    for file,sha in [("axbi_background.rs",OWN_REI_SHA),("bianchi_i.rs",OWN_GEOMETRY_SHA)]:
        p=crate/"src"/file
        if sha256_file(p)!=sha:raise RuntimeError("ORIGINAL_REI_RUST_SOURCE_CHANGED:"+file)
    c=source_lock()
    csv=HERE/"evidence/JOINT_CAMPAIGN/REI_GAMMANU_MASSIVE_BACKGROUND.csv"
    source_sha=sha256_file(csv)
    with tempfile.TemporaryDirectory(prefix="bass_rei_joint_kinetic_") as tmp:
        r=Path(tmp);(r/"src").mkdir()
        (r/"src/main.rs").write_bytes((HERE/"rust_rei_joint.rs").read_bytes())
        (r/"Cargo.toml").write_text(
          '[package]\nname="bass_rei_gamma_nu_massive_native"\nversion="0.1.0"\nedition="2021"\n'
          '[dependencies]\nrei_microphysics={path="'+str(crate)+'"}\n')
        env=os.environ.copy();env["CARGO_NET_OFFLINE"]="true"
        env["CARGO_TARGET_DIR"]=str(target)
        arg=[str(csv),str(c.h0),str(c.omega_m),str(c.omega_lambda),str(c.aref)]
        cmd=["cargo","run","--release","--offline","--manifest-path",str(r/"Cargo.toml"),"--",*arg]
        p=subprocess.run(cmd,env=env,capture_output=True,text=True)
        if p.returncode!=0:raise RuntimeError("REAL_REI_CRATE_TYPE_BRIDGE_FAILED:"+p.stderr[-4000:])
        rec=json.loads(p.stdout)
        if rec["rows"]!=3208 or rec["cases"]!=8:
            raise ValueError("BASS_REI_JOINT_TABLE_MISMATCH")
        exe=target/"release/bass_rei_gamma_nu_massive_native"
        lines=csv.read_text().splitlines()
        head=lines[0].split(",")
        failures=[]
        for field,scale,index in [
           ("H_mean_per_s",1.05,401*3+2),
           ("pi_massive_J_m3",1.8,401*3+2),
           ("Sigma",1.4,401*5+2),
           ("gamma_number_N0",1.001,401*4+2)]:
            mutated=lines.copy()
            i=head.index(field)
            parts=mutated[index].split(",")
            value=float(parts[i])
            if not value:raise RuntimeError("NEGATIVE_TEST_SELECT_NONZERO_PHYSICS_SOURCE:"+field)
            parts[i]=repr(value*scale)
            mutated[index]=",".join(parts)
            tmpfile=r/(field+".csv")
            tmpfile.write_text("\n".join(mutated)+"\n")
            neg=subprocess.run([str(exe),str(tmpfile),*arg[1:]],capture_output=True,text=True)
            if neg.returncode==0 or "AXBI_JOINT_KINETIC_REJECT:" not in neg.stderr:
                raise AssertionError(f"RUST_NATIVE_FALSE_PASS:{field}:{neg.returncode}")
            failures.append({"mutated_field":field,"rejection":neg.stderr.strip().splitlines()[-1],
                             "exit_code":neg.returncode})
    if sha256_file(csv)!=source_sha:raise AssertionError("SOURCE_CSV_MUTATED")
    receipt={"schema":"bass.rei.axbi.gamma_nu_massive_native_bridge.v1",
       "original_Rust_AXBI_sha256":OWN_REI_SHA,
       "original_Rust_geometry_sha256":OWN_GEOMETRY_SHA,
       "native_bridge_rust_source_sha256":sha256_file(HERE/"rust_rei_joint.rs"),
       "public_background_csv_sha256":source_sha,
       "original_user_REI_source_git_head":subprocess.check_output(["git","-C",str(repo),"rev-parse","HEAD"],text=True).strip(),
       "cargo_original_Rust_rei_microphysics_type_check":True,
       "cargo_positive_exit_code":0,
       "physical_checker_output":rec,
       "negative_inputs":failures,
       "original_source_checkout_mutated":False,
       "actual_native_chemistry_Einstein_solver_modified":False,
       "science_source_model":"initial Sigma+gamma+masslessnu+FD96 massive, one-way actual AX08 electron opacity"}
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(receipt,indent=2)+"\n")
    print(json.dumps({k:v for k,v in receipt.items() if k not in ("negative_inputs",)},indent=2)[:2300])
    print("REJECTIONS",failures)
    return receipt

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--repo",type=Path,required=True)
    p.add_argument("--target",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    run(a.repo,a.out,a.target)
