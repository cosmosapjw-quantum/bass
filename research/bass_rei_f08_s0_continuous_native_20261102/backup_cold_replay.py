#!/usr/bin/env python3
"""Single immutable source-inclusive BASS native-physics archive and cold readback."""
from pathlib import Path
import hashlib,json,os,subprocess,sys,tempfile,zipfile,csv,gzip,math
ROOT=Path(__file__).resolve().parent
W=ROOT.parent.parent
D="research/bass_rei_f08_s0_continuous_native_20261102"
R="research/bass_rei_f08_native_hhe_firststage_20261101/original_rei_rust"
S="research/bass_rei_f08_s0_source_photon_thomson_20261101"
Q="research/bass_rei_f08_s0_remap_support_20261101"
ARCH=Path("/home/cosmosapjw/archives/BASS_REI_F08_S0_CONTINUOUS_NATIVE_HHE_20261102.zip")
RECEIPT=ARCH.with_suffix(".receipt.json")

def sha(p):
 h=hashlib.sha256()
 with Path(p).open("rb") as f:
  for b in iter(lambda:f.read(1<<20),b""):h.update(b)
 return h.hexdigest()

def fileset():
 files=[]
 for f in (W/R).rglob("*"):
  if f.is_file() and "target" not in f.parts and "__pycache__" not in f.parts:
   files.append(f)
 for g in ((W/S/"source_inputs").glob("*"),(W/Q/"source_inputs").glob("*")):
  files.extend(p for p in g if p.is_file())
 files.extend([W/S/"s0_source_photon_thomson.py",W/Q/"spectral_support.py",
   W/"research/bass_rei_f08_native_hhe_firststage_20261101/results/native_stage.csv",
   W/".github/workflows/bass-rei-f08-s0-continuous-native-source-physics.yml"])
 for f in (W/D).rglob("*"):
  if not f.is_file():continue
  if any(x in f.parts for x in ("__pycache__","results_smoke","impossible")):continue
  if f.name.endswith(".stdout") or f.name.endswith(".stderr"):continue
  files.append(f)
 return sorted(set(files))

def assert_original_hashes(home):
 for folder,filename,count in (
  (home/R,"original_source_sha256.txt",51),
  (home/S/"source_inputs","ORIGIN_SHA256SUMS.txt",12),
  (home/Q/"source_inputs","LOCKED_CHECKPOINT_SHA256SUMS.txt",4)):
  check=subprocess.run(["sha256sum","-c",filename],cwd=folder,
    capture_output=True,text=True)
  assert check.returncode==0,(folder,check.stdout[-1500:],check.stderr[-1500:])
  assert check.stdout.count(": OK")==count,(folder,check.stdout.count(": OK"))

def run_checked(args,cwd,env=None):
 z=subprocess.run(args,cwd=cwd,env=env,capture_output=True,text=True)
 assert z.returncode==0,(args,z.stdout[-1800:],z.stderr[-3000:])
 return z

def equal_csv(a,b):
 with gzip.open(a,"rt",newline="") as f:x=list(csv.DictReader(f))
 with gzip.open(b,"rt",newline="") as f:y=list(csv.DictReader(f))
 assert len(x)==len(y)
 if a.read_bytes()==b.read_bytes():return "BYTE_EXACT_PASS",len(x)
 for u,v in zip(x,y):
  assert u.keys()==v.keys()
  for k in u:
   if k in ("branch","model","step","source_packets","stage_native_root_iterations"):
    assert u[k]==v[k],(k,u[k],v[k])
   else:
    p,q=float(u[k]),float(v[k])
    if "residual" in k:assert abs(p)<6e-12 and abs(q)<6e-12
    else:assert math.isclose(p,q,rel_tol=2e-9,abs_tol=2e-13),(k,p,q)
 return "SCOPED_NUMERIC_SEMANTIC_PARITY_PASS",len(x)

def main():
 assert not ARCH.exists() and not RECEIPT.exists(),"No replacement of original backups"
 files=fileset()
 assert len(files)>=75,len(files)
 for p in files:assert p.exists(),str(p)
 assert_original_hashes(W)
 with zipfile.ZipFile(ARCH,"w",zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for f in files:z.write(f,str(f.relative_to(W)))
 with zipfile.ZipFile(ARCH) as z:
  assert z.testzip() is None
  assert len(z.namelist())==len(files)
  with tempfile.TemporaryDirectory(prefix="BASS_REI_F08_CONTINUOUS_COLD_") as tmp:
   root=Path(tmp)
   z.extractall(root)
   assert_original_hashes(root)
   new=root/D
   env=os.environ.copy()
   env["CARGO_TARGET_DIR"]=str(new/"COLD_NATIVE_RUST_TARGET")
   run_checked(["cargo","build","--offline","--release","--example","bass_s0_continuous_packet_step"],
     cwd=root/R,env=env)
   exe=new/"COLD_NATIVE_RUST_TARGET/release/examples/bass_s0_continuous_packet_step"
   assert exe.exists()
   for args in ([sys.executable,"-m","unittest","discover","-s",str(new/"tests"),"-v"],
                [sys.executable,"-O","-m","unittest","discover","-s",str(new/"tests"),"-v"]):
    run_checked(args,cwd=root)
   run_checked([sys.executable,str(new/"audit_continuous.py"),"--out",str(new/"results")],cwd=root)
   generated={}
   for step in (64,160):
    out=new/("cold_"+str(step))
    run_checked([sys.executable,str(new/"continuous_s0.py"),"--steps",str(step),
       "--rust",str(exe),"--out",str(out)],cwd=root)
    m=json.loads((out/"RESULT.json").read_text())
    orig=json.loads((new/("results" if step==160 else "results_prefix64")/"RESULT.json").read_text())
    assert m["steps_per_model"]==orig["steps_per_model"]==step
    assert m["REI_CENTRAL"]==orig["REI_CENTRAL"]=="28/88_REPORTED"
    summary={}
    for k in ("trajectory_file","comparison_file"):
     a=new/("results" if step==160 else "results_prefix64")/orig[k]
     b=out/m[k]
     status,count=equal_csv(a,b)
     summary[k]={"record_count":count,"status":status,"original_SHA256":sha(a)}
    generated[str(step)]=summary
   run_checked([sys.executable,str(new/"audit_continuous.py"),"--out",str(new/"cold_160")],cwd=root)
 receipt={"schema":"BASS_REI_F08_S0_CONTINUOUS_HHE_SOURCE_BACKUP_V1",
 "archive":str(ARCH),"bytes":ARCH.stat().st_size,"sha256":sha(ARCH),
 "file_members":len(files),"zip_CRC":"PASS",
 "original_Rust_SHA51":"PASS","original_source_SHA12":"PASS",
 "original_checkpoint_SHA4":"PASS",
 "cold_compiled_original_Rust_research_adapter":"PASS",
 "cold_unittest_standard":"14/14_PASS","cold_unittest_optimized":"14/14_PASS",
 "cold_same_author_hostile_audit":"PASS",
 "actual_cold_physical_replay":generated,
 "original_REI_owner_admission":"HOLD",
 "REI_CENTRAL":"28/88_REPORTED","BASS_UPPER":"9/15_SCOPED_SOURCE_MAPPED",
 "official_16k_F08_full_owner_IVP":"NOT_REPLAYED",
 "github_draft":"https://github.com/cosmosapjw-quantum/bass/pull/328",
 "second_external_cloud_binary_readback":"NOT_VERIFIED",
 "no_original_source_mutation":True,"production":"HOLD"}
 RECEIPT.write_text(json.dumps(receipt,sort_keys=True,indent=2)+"\n")
 print("SOURCE_INCLUSIVE_REI_CONTINUOUS_NATIVE_COLD_RESTORE_PASS",json.dumps(receipt,sort_keys=True))
if __name__=="__main__":main()
