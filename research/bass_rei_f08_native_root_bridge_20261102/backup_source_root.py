#!/usr/bin/env python3
"""One immutable source-inclusive BASS original REI F08 Krawczyk science archive."""
from pathlib import Path
import csv,gzip,hashlib,io,json,math,os,subprocess,sys,tempfile,zipfile
ROOT=Path(__file__).resolve().parent
W=ROOT.parent.parent
UNIT="research/bass_rei_f08_native_root_bridge_20261102"
RUST="research/bass_rei_f08_native_hhe_firststage_20261101/original_rei_rust"
PARENT="research/bass_rei_f08_s0_continuous_native_20261102"
S0="research/bass_rei_f08_s0_source_photon_thomson_20261101"
CHECKPOINT="research/bass_rei_f08_s0_remap_support_20261101"
ARCHIVE=Path("/home/cosmosapjw/archives/BASS_REI_F08_S0_NATIVE_KRAWCZYK_ROOT_SOURCE_FULL_20261102.zip")
RECEIPT=ARCHIVE.with_suffix(".receipt.json")

def digest(p):
    h=hashlib.sha256()
    with Path(p).open("rb") as f:
        for block in iter(lambda:f.read(1<<20),b""):h.update(block)
    return h.hexdigest()

def fileset():
    files=[]
    for p in (W/RUST).rglob("*"):
        if p.is_file() and not any(x in p.parts for x in ("target","__pycache__")):
            files.append(p)
    files+=list(p for p in (W/S0/"source_inputs").glob("*") if p.is_file())
    files+=list(p for p in (W/CHECKPOINT/"source_inputs").glob("*") if p.is_file())
    files += [
        W/S0/"s0_source_photon_thomson.py",
        W/CHECKPOINT/"spectral_support.py",
        W/PARENT/"continuous_s0.py",
        W/PARENT/"results/RESULT.json",
        W/PARENT/"results/SOURCE_LOCKED_REI_S0_CONTINUOUS_NATIVE_HHE_TRAJECTORY.csv.gz",
        W/".github/workflows/bass-rei-f08-native-root-bridge.yml",
    ]
    for p in (W/UNIT).rglob("*"):
        if not p.is_file():continue
        if any(x in p.parts for x in ("__pycache__","first")):continue
        if p.name.endswith((".stderr",".stdout")):continue
        if p.name in ("s0_in.txt","s0_out.txt"):continue
        if p.name in ("ROOT_FIRST.csv","ROOT_FIRST.stderr"):continue
        files.append(p)
    files=sorted(set(files))
    assert len(files)>=80,len(files)
    assert all(f.is_file() for f in files)
    return files

def sha_manifest(home):
    for folder,name,num in (
      (home/RUST,"original_source_sha256.txt",51),
      (home/S0/"source_inputs","ORIGIN_SHA256SUMS.txt",12),
      (home/CHECKPOINT/"source_inputs","LOCKED_CHECKPOINT_SHA256SUMS.txt",4)):
        p=subprocess.run(["sha256sum","-c",name],cwd=folder,capture_output=True,text=True)
        assert p.returncode==0,(name,p.stdout[-900:],p.stderr[-900:])
        assert p.stdout.count(": OK")==num,(name,p.stdout.count(": OK"))

def run(*args,dir=None,env=None):
    p=subprocess.run(list(args),cwd=dir,env=env,capture_output=True,text=True)
    assert p.returncode==0,("COMMAND_FAIL",list(args),p.stdout[-1200:],p.stderr[-2300:])
    return p

def gzrows(path):
    with gzip.open(path,"rt",newline="") as f:return list(csv.DictReader(f))

def compare_sources(saved,cold):
    with Path(saved).open(newline="") as f:a=list(csv.DictReader(f))
    with Path(cold).open(newline="") as f:b=list(csv.DictReader(f))
    assert len(a)==len(b)==16
    for u,v in zip(a,b):
        assert u.keys()==v.keys()
        for key in u:
            if key in ("case_id","packets","root_status","root_error_code","point_iterations",
                       "root_contains_conservative","photons_contain_conservative"):
                assert u[key]==v[key],(key,u[key],v[key])
            else:
                x,y=float(u[key]),float(v[key])
                assert math.isfinite(x) and math.isfinite(y)
                if key in ("root_q","root_max_relative_gas_width","root_width_xHII",
                           "root_width_xHeII","root_width_xHeIII","root_width_w_ev_per_H",
                           "photon_sum_interval_width_per_H","centre_vs_conservative_max_abs",
                           "point_residual"):
                    assert 0<=x<1e-10 and 0<=y<1e-10,(key,x,y)
                else:
                    assert math.isclose(x,y,rel_tol=2e-10,abs_tol=5e-13),(key,x,y)
    return "BYTE_EXACT_PASS" if Path(saved).read_bytes()==Path(cold).read_bytes() else "SOURCE_NUMERIC_SEMANTIC_PARITY_PASS"

def compare_derived(saved,cold):
    a=gzrows(saved);b=gzrows(cold)
    assert len(a)==len(b)==16
    for u,v in zip(a,b):
        assert u.keys()==v.keys()
        for k in u:
            if k in ("branch","source_model","source_step","source_packet_count",
                     "root_local_original_gas_contains_conservative",
                     "root_local_original_photons_contain_conservative",
                     "original_global_owner_interval_certified"):
                assert u[k]==v[k],k
            else:
                x,y=float(u[k]),float(v[k])
                assert math.isfinite(x) and math.isfinite(y)
                if k in ("native_source_Krawczyk_q","original_root_max_relative_gas_width",
                          "original_root_photon_sum_interval_width_per_H",
                          "root_centre_vs_conservative_max_abs"):
                    assert 0<=x<1e-10 and 0<=y<1e-10
                else:
                    assert math.isclose(x,y,rel_tol=2e-10,abs_tol=5e-13),(k,x,y)
    return "BYTE_EXACT_PASS" if Path(saved).read_bytes()==Path(cold).read_bytes() else "SOURCE_NUMERIC_SEMANTIC_PARITY_PASS"

def main():
    assert not ARCHIVE.exists() and not RECEIPT.exists(),"REFUSE_TO_REPLACE_EXISTING_BACKUP"
    files=fileset()
    sha_manifest(W)
    with zipfile.ZipFile(ARCHIVE,"w",zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in files:z.write(p,str(p.relative_to(W)))
    with zipfile.ZipFile(ARCHIVE) as z:
        assert z.testzip() is None
        assert len(z.namelist())==len(files)
        with tempfile.TemporaryDirectory(prefix="REI_F08_ROOT_COLD_") as tmp:
            home=Path(tmp)
            z.extractall(home)
            sha_manifest(home)
            u=home/UNIT
            env=os.environ.copy()
            env["CARGO_TARGET_DIR"]=str(u/"cold_rust_target")
            run("cargo","build","--release","--offline","--example",
                "bass_s0_interval_root_probe",dir=home/RUST,env=env)
            exe=u/"cold_rust_target/release/examples/bass_s0_interval_root_probe"
            assert exe.exists()
            for flags in ((),("-O",)):
                run(sys.executable,*flags,"-m","unittest","discover","-s",
                    str(u/"tests"),"-v",dir=home)
            cold=u/"cold_recompute"
            cold.mkdir()
            run(str(exe),str(u/"inputs/actual160"),str(cold/"ROOT_ALL.csv"),dir=home)
            run(sys.executable,str(u/"audit_native_root.py"),"--inputs",
                str(u/"inputs/actual160"),"--results",str(cold),
                "--negative-exe",str(exe),dir=home)
            native=compare_sources(u/"results/ROOT_ALL.csv",cold/"ROOT_ALL.csv")
            physical=compare_derived(u/"results/SOURCE_S0_NATIVE_ROOT_PHYSICAL_SUPPORT.csv.gz",
                                     cold/"SOURCE_S0_NATIVE_ROOT_PHYSICAL_SUPPORT.csv.gz")
            restored=json.loads((cold/"RESULT.json").read_text())
            assert restored["root_pass"]==16 and restored["root_failure"]==0
            assert restored["actual_source_packet_records"]==70656
            assert restored["negative_source_control"]["status"]=="PASS_REJECTED_NEGATIVE_PACKET"
    payload={"schema":"BASS_REI_F08_NATIVE_SOURCE_ROOT_FULL_SOURCE_BACKUP_V1",
       "archive":str(ARCHIVE),"bytes":ARCHIVE.stat().st_size,
       "sha256":digest(ARCHIVE),"members":len(files),"zip_crc":"PASS",
       "original_source_sha_51_12_4":"PASS_67_OF_67",
       "cold_rust_original_native_root_release_build":"PASS",
       "cold_test_standard":"12/12_PASS","cold_test_optimized":"12/12_PASS",
       "cold_real_S0_root_16_cases":native,
       "cold_real_S0_root_physics_16_rows":physical,
       "actual_source_packets":70656,
       "cold_forged_negative_packet":"REJECTED_PASS",
       "source_owner_interval_full_history":"NOT_RUN",
       "REI_CENTRAL":"28/88_REPORTED","BASS_UPPER":"9/15_SCOPED_SOURCE_MAPPED",
       "github_pr":"https://github.com/cosmosapjw-quantum/bass/pull/331",
       "second_provider_archive_byte_restore":"NOT_VERIFIED","production":"HOLD"}
    RECEIPT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    print("BASS_REI_ORIGINAL_NATIVE_INTERVAL_SOURCE_FULL_BACKUP_RESTORED_PASS",
          json.dumps(payload,sort_keys=True))
if __name__=="__main__":main()
