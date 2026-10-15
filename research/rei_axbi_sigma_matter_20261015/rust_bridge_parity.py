"""Run source-locked native rei_microphysics BackgroundPoint/GeometrySnapshot bridge.

The actual original REI Rust crate is a read-only path dependency compiled
with an external Cargo target; no current owner AX08 process/config is touched.
"""
from __future__ import annotations
import csv,hashlib,json,os,subprocess,tempfile
from pathlib import Path
from sigma_matter import LOCK_SHA,radiation
HERE=Path(__file__).resolve().parent
SHA_AXBI="65f10dced178aa85bb1c92da0b35350a0eec2d3d3de05630c900b5df4ec1e254"
SHA_GEOM="0c0bb17168b36a67af6e3e2a3ada835bc77db3dbc73d06e13075f6019ec11289"
def run(repo:Path,target:Path,output:Path):
    if output.exists():raise FileExistsError(output)
    repo=repo.resolve()
    crate=repo/"rust/rei_microphysics"
    for f,sha in [(crate/"src/axbi_background.rs",SHA_AXBI),(crate/"src/bianchi_i.rs",SHA_GEOM)]:
        if hashlib.sha256(f.read_bytes()).hexdigest()!=sha:raise RuntimeError(f"ORIGINAL_REI_SOURCE_IDENTITY_MISMATCH:{f}")
    lock=radiation._read_lock()
    assert radiation.LOCK_SHA==LOCK_SHA
    p=HERE/"evidence/SIGMA_MATTER_TABLES/AX03_SIGMA_MASSIVE_HISTORIES.csv"
    c=lock["cosmology"];k=lock["clock"]
    with tempfile.TemporaryDirectory(prefix="bass_rei_sigma_matter_native_") as tmp:
        root=Path(tmp);(root/"src").mkdir()
        (root/"src/main.rs").write_bytes((HERE/"rust_rei_matter_bridge.rs").read_bytes())
        (root/"Cargo.toml").write_text('[package]\nname="bass_axbi_sigma_matter_bridge"\nversion="0.1.0"\nedition="2021"\n[dependencies]\nrei_microphysics={path="'+crate.as_posix()+'"}\n')
        env=os.environ.copy();env["CARGO_NET_OFFLINE"]="true";env["CARGO_TARGET_DIR"]=str(target.resolve())
        cmd=["cargo","run","--release","--offline","--manifest-path",str(root/"Cargo.toml"),
            "--",str(p.resolve()),str(c["H0_per_s"]),str(c["Omega_m"]),str(c["Omega_r"]),str(c["Omega_lambda"]),str(k["a_ref"]),str(k["a_end"])]
        run=subprocess.run(cmd,text=True,capture_output=True,env=env)
        if run.returncode!=0:raise RuntimeError("REAL_RUST_REI_BRIDGE_FAILED:"+run.stderr[-2500:])
        success=json.loads(run.stdout)
        negative=[]
        lines=p.read_text().splitlines()
        keys=lines[0].split(",")
        for which,bad in [("H_mean_per_s",1.05),("Pi_m_J_m3",1.9),("Sigma",1.2)]:
            new=list(lines)
            dat=new[2401].split(",")
            idx=keys.index(which)
            original=float(dat[idx])
            if original==0. and which=="Pi_m_J_m3":
                # Choose the first genuinely nonzero matter kinetic row.
                chosen=next(i for i,line in enumerate(lines[1:],1) if abs(float(line.split(",")[idx]))>1e-20)
                dat=lines[chosen].split(",")
                original=float(dat[idx]);lineindex=chosen
            else:lineindex=2401
            dat[idx]=repr(original*bad)
            new[lineindex]=",".join(dat)
            corrupted=root/(which+".csv");corrupted.write_text("\n".join(new)+"\n")
            args=[str(x) for x in cmd[-7:]];args[0]=str(corrupted)
            check=subprocess.run([str(target.resolve()/"release/bass_axbi_sigma_matter_bridge"),*args],capture_output=True,text=True)
            if check.returncode==0 or "AXBI_SIGMA_MASSIVE_REJECT" not in check.stderr:
                raise RuntimeError("RUST_MUTATION_WAS_NOT_REJECTED:"+which)
            negative.append({"field":which,"exit_code":check.returncode,"message":check.stderr.strip().splitlines()[-1]})
    result={"schema":"bass.rei.axbi.source_native_sigma_matter_bridge.v1",
      "actual_REI_git_SHA":subprocess.check_output(["git","-C",str(repo),"rev-parse","HEAD"],text=True).strip(),
      "original_AXBI_SHA256":SHA_AXBI,"original_Bianchi_geometry_SHA256":SHA_GEOM,
      "native_bridge_Rust_sha256":hashlib.sha256((HERE/"rust_rei_matter_bridge.rs").read_bytes()).hexdigest(),
      "public_history_sha256":hashlib.sha256(p.read_bytes()).hexdigest(),
      "cargo_positive_exit_code":0,"result":success,"negative_controls":negative,
      "source_identity":"original unchanged rei_microphysics crate, parent q stressfree comparator",
      "no_owner_source_mutation":True,"no_native_EoR_solver_launched":True,
      "coupled_chemistry_science_admission":"NOT_ISSUED"}
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2)[:2300])
    return result
if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser();p.add_argument("--repo",type=Path,required=True)
    p.add_argument("--target",type=Path,required=True);p.add_argument("--out",type=Path,required=True)
    a=p.parse_args();run(a.repo,a.target,a.out)
