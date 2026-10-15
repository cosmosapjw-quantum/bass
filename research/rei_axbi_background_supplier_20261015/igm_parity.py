"""Compare H/He nuclei and mean CMB source inputs to actual REI Rust igm_background.

Uses the ORIGINAL native Rust FlatFlrwBackground crate in an isolated Cargo
project; the comparison is at matched scale factors supplied by the Rust code.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,os,subprocess,tempfile
from pathlib import Path
import numpy as np
from axbi_provider import Background,Family,_read_lock
from rust_parity import read_owner

SHA_IGM="ebe5d4ba0a61133512cecfe50791794a50aa22132bcc5189170e5668cbf1871f"
HERE=Path(__file__).resolve().parent

def run(repo:Path,target:Path,output:Path):
    if output.exists():raise FileExistsError(output)
    crate,head=read_owner(repo)
    if hashlib.sha256((crate/'src/igm_background.rs').read_bytes()).hexdigest()!=SHA_IGM:
        raise RuntimeError("ORIGINAL_NATIVE_IGM_SOURCE_CHANGED")
    lock=_read_lock();c=lock["cosmology"];clock=lock["clock"]
    with tempfile.TemporaryDirectory(prefix="bass_rei_igm_bg_") as tmp:
        root=Path(tmp);(root/'src').mkdir()
        (root/'src/main.rs').write_bytes((HERE/'rust_bridge/src/flrw_density.rs').read_bytes())
        (root/'Cargo.toml').write_text('[package]\nname="bass_rei_igm_flrw_bridge"\nversion="0.1.0"\nedition="2021"\n[dependencies]\nrei_microphysics={path="'+crate.as_posix()+'"}\n')
        vals=[c["H0_per_s"],c["Omega_m"],c["Omega_r"],c["Omega_lambda"],
              c["Omega_b"],c["X_He4"],c["Tcmb0_K"],clock["a_ref"],clock["a_end"],11]
        command=['cargo','run','--release','--offline','--manifest-path',str(root/'Cargo.toml'),'--',*[str(x) for x in vals]]
        env=os.environ.copy();env["CARGO_NET_OFFLINE"]="true";env["CARGO_TARGET_DIR"]=str(target.resolve())
        p=subprocess.run(command,env=env,text=True,capture_output=True)
    if p.returncode!=0:raise RuntimeError("NATIVE_REI_IGM_BUILD_OR_RUN_FAILED:"+p.stderr[-1200:])
    parsed=list(csv.DictReader(io.StringIO(p.stdout)))
    assert len(parsed)==11
    local=Background(Family(0.))
    records=[]
    for x in parsed:
        a=float(x["a"]);y=local.at_a(a)
        z={"i":int(x["index"]),"a":a}
        for name,owner,expected in [
          ("H_per_s",float(x["H"]),y["H_flrw_per_s"]),
          ("n_H_cm3",float(x["n_H_cm3"]),y["n_H_cm3"]),
          ("n_He_cm3",float(x["n_He_cm3"]),y["n_He_cm3"]),
          ("Tbar_CMB_K",float(x["Tbar_CMB_K"]),y["Tbar_CMB_K"]),
          ("dt_dln_a_s",float(x["dt_dln_a_s"]),y["dt_dln_a_s"])]:
            z[name+"_relative_diff"]=abs(owner/expected-1)
        records.append(z)
    maxrel=max(v for x in records for k,v in x.items() if k.endswith("_relative_diff"))
    if maxrel>5e-13:raise ArithmeticError("IGM_DENSITY_MASS_CONVENTION_OR_CLOCK_MISMATCH")
    result={"schema":"bass.rei.axbi.igm_source_flrw_Rust_parity.v1",
      "source_owner_git":head,"original_igm_background_sha256":SHA_IGM,
      "original_axbi_source_copy_unchanged":True,
      "cargo_run_offline_actual_native_status":"SUCCESS",
      "rows":records,"max_relative_input_diff":maxrel,
      "physically_interpreted":"n_H, n_He physical nuclei; Tcmb0/a isotropic reference proxy; elapsed clock from AX03 elsewhere, absolute ln(a) is not seconds",
      "owner_source_edits":0,"native_science_run_started":0}
    output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(result,indent=2)+"\n")
    print({k:v for k,v in result.items() if k!="rows"})
    return result

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--rei-repo",type=Path,required=True)
    ap.add_argument("--target-dir",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    a=ap.parse_args();run(a.rei_repo,a.target_dir,a.output)
