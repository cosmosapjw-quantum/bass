#!/usr/bin/env python3
"""Source-aware, standard-library hostile readback of actual original Rust root.

All original Rust 51 + S0 source 12 + photon checkpoint 4 immutable identities
checked. Enclosures are LOCAL to f64 snapshot inputs, not a global source theorem.
"""
from pathlib import Path
import csv,gzip,hashlib,io,json,math,subprocess,tempfile

ROOT=Path(__file__).resolve().parent
SRC=ROOT.parent/"bass_rei_f08_s0_source_photon_thomson_20261101"/"source_inputs"
CHK=ROOT.parent/"bass_rei_f08_s0_remap_support_20261101"/"source_inputs"
RUST=ROOT.parent/"bass_rei_f08_native_hhe_firststage_20261101"/"original_rei_rust"
BASE=ROOT.parent/"bass_rei_f08_s0_continuous_native_20261102"/"results"
BI_H=(1.01e-14,9.9e-15,1e-14)
FLRW_H=(1e-14,1e-14,1e-14)
DT=625000000.
BIRTH=13.7
DATA=ROOT/"inputs/actual160"
RESULTS=ROOT/"results"
EXPECTED_STEPS=(1,8,64,160)

def sha(p):
    h=hashlib.sha256()
    with Path(p).open("rb") as f:
        for blob in iter(lambda:f.read(1<<20),b""):h.update(blob)
    return h.hexdigest()
def original_hashes():
    out={}
    for folder,name,n in ((RUST,"original_source_sha256.txt",51),
                          (SRC,"ORIGIN_SHA256SUMS.txt",12),
                          (CHK,"LOCKED_CHECKPOINT_SHA256SUMS.txt",4)):
        rows=(folder/name).read_text().splitlines()
        assert len(rows)==n,(name,len(rows))
        for x in rows:
            h,p=x.split(maxsplit=1)
            assert sha(folder/p)==h,(name,p)
        out[name]=len(rows)
    assert sha(RUST/"src/coupled_primary.rs")=="915d0a898100a54d04a525227e7fbeb870e321fcc14aaa91afd61352b6d4cf4b"
    assert sha(RUST/"src/atomic_provider.rs")=="b0b572d3940a7a1f740e09d5f43c60236ec61511e8bdbcc68e60395ec7e107d3"
    return out

def load_csv(p):
    with Path(p).open("rt",newline="") as f:return list(csv.DictReader(f))
def load_gz(p):
    with gzip.open(p,"rt",newline="") as f:return list(csv.DictReader(f))
def source_case(path):
    lines=Path(path).read_text().splitlines()
    stage=None;packets=[]
    for ln in lines:
        if not ln or ln.startswith("#"):continue
        t=ln.split("|")
        if t[0]=="S":
            assert len(t)==11 and stage is None
            stage={
                "nH":float(t[1]),"fHe":float(t[2]),"Hmean":float(t[3]),
                "dt":float(t[4]),"x":tuple(float(z) for z in t[5:8]),
                "w":float(t[8]),"escape":float(t[9]),"t0":float(t[10])
            }
        elif t[0]=="P":
            assert len(t)==3
            e,n=map(float,t[1:])
            assert n>0 and e>0 and math.isfinite(e*n)
            packets.append((e,n))
        else:raise AssertionError("source packet schema")
    assert stage is not None and packets
    return stage,packets

def save_csv(path,rows):
    with path.open("wb") as f:
        with gzip.GzipFile(fileobj=f,mode="wb",filename="",mtime=0,compresslevel=6) as g:
            with io.TextIOWrapper(g,encoding="utf8",newline="") as t:
                w=csv.DictWriter(t,fieldnames=list(rows[0]))
                w.writeheader();w.writerows(rows)
    return sha(path)

def audit(directory=DATA,result=RESULTS,negative_exe=None):
    original=original_hashes()
    directory=Path(directory);result=Path(result);result.mkdir(parents=True,exist_ok=True)
    capture=json.loads((directory/"CAPTURE.json").read_text())
    assert capture["science_parent_PR328"]=="b23c6915aeaeedbabbc8e90ffab74f2afa96c1e6"
    assert tuple(capture["captured_steps"])==EXPECTED_STEPS
    assert len(capture["snapshots"])==16
    stage_rows=load_csv(result/"ROOT_ALL.csv")
    assert len(stage_rows)==16
    source_names={x["file"] for x in capture["snapshots"]}
    assert len(source_names)==16
    bycase={x["case_id"]:x for x in stage_rows}
    assert len(bycase)==16
    original_parent=json.loads((BASE/"RESULT.json").read_text())
    previous=load_gz(BASE/original_parent["trajectory_file"])
    parent={(r["branch"],r["model"],int(r["step"])):r for r in previous}
    assert len(parent)==640
    report=[]
    max_error={"source_n":0.,"source_u":0.,"xHII":0.,"xHeII":0.,"xHeIII":0.,"w":0.,
               "source_parent_HII":0.,"source_parent_w":0.}
    for x in capture["snapshots"]:
        p=directory/x["file"]
        assert sha(p)==x["SHA256"]
        stage,packets=source_case(p)
        label=x["branch"];mode=x["mode"];step=x["step"]
        assert label in ("S0_BI","S0_FLRW") and mode in ("CHARACTERISTIC","ORIGINAL_HAT")
        assert step in EXPECTED_STEPS
        case=Path(x["file"]).stem
        r=bycase[case]
        assert r["root_status"]=="PASS",r
        assert r["root_error_code"]=="NONE"
        assert r["root_contains_conservative"]=="true"
        assert r["photons_contain_conservative"]=="true"
        q=float(r["root_q"])
        assert math.isfinite(q) and 0<=q<1
        assert int(r["packets"])==len(packets)==x["source_packet_records"]
        assert int(r["point_iterations"])<=200 and float(r["point_residual"])<1e-15
        for field in ("root_width_xHII","root_width_xHeII","root_width_xHeIII",
                      "root_width_w_ev_per_H","photon_sum_interval_width_per_H",
                      "root_max_relative_gas_width"):
            v=float(r[field])
            assert math.isfinite(v) and v>=0,(case,field,v)
        assert float(r["root_max_relative_gas_width"])<1e-10
        assert math.isclose(float(r["n_H_cm3"]),stage["nH"],rel_tol=1e-13)
        assert stage["dt"]==DT and stage["fHe"]==.083
        assert int(round(stage["t0"]/DT))+1==step
        N=math.fsum(n for e,n in packets)
        U=math.fsum(e*n for e,n in packets)
        max_error["source_n"]=max(max_error["source_n"],abs(N-float(r["Nin_per_H"])))
        max_error["source_u"]=max(max_error["source_u"],abs(U-float(r["Uin_ev_per_H"])))
        assert math.isclose(N,float(r["Nin_per_H"]),rel_tol=5e-13,abs_tol=3e-14)
        assert math.isclose(U,float(r["Uin_ev_per_H"]),rel_tol=5e-13,abs_tol=3e-13)
        final=parent[(label,mode,step)]
        for i,(col,source) in enumerate((("conservative_xHII","xHII"),("conservative_xHeII","xHeII"),("conservative_xHeIII","xHeIII"))):
            v=float(r[col]);p0=float(final[source])
            max_error[col.split("_")[1]]=max(max_error[col.split("_")[1]],abs(v-p0))
            assert abs(v-p0)<5e-14,(case,col,v,p0)
        v=float(r["conservative_w_ev_per_H"])
        max_error["w"]=max(max_error["w"],abs(v-float(final["w_ev_per_H"])))
        assert abs(v-float(final["w_ev_per_H"]))<5e-13
        if step==1:
            assert stage["x"]==(.9,.3,.6)
        else:
            prior=parent[(label,mode,step-1)]
            max_error["source_parent_HII"]=max(max_error["source_parent_HII"],abs(stage["x"][0]-float(prior["xHII"])))
            max_error["source_parent_w"]=max(max_error["source_parent_w"],abs(stage["w"]-float(prior["w_ev_per_H"])))
            assert abs(stage["x"][0]-float(prior["xHII"]))<1e-13
            assert abs(stage["w"]-float(prior["w_ev_per_H"]))<5e-13
        h=BI_H if label=="S0_BI" else FLRW_H
        floor=BIRTH*math.exp(-max(h)*step*DT)
        false_n=math.fsum(n for e,n in packets if e<floor-5e-12)
        frac=false_n/N
        if mode=="CHARACTERISTIC":
            assert frac==0
        else:
            assert frac>0
        report.append({
            "branch":label,"source_model":mode,"source_step":step,
            "source_proper_s":step*DT,"source_packet_count":len(packets),
            "source_photon_N_per_H":N,"source_photon_U_eV_per_H":U,
            "physical_exact_energy_floor_eV":floor,
            "photons_below_physical_floor_per_H":false_n,
            "below_physical_floor_fraction":frac,
            "native_source_Krawczyk_q":q,
            "original_root_max_relative_gas_width":float(r["root_max_relative_gas_width"]),
            "original_root_photon_sum_interval_width_per_H":float(r["photon_sum_interval_width_per_H"]),
            "original_conservative_xHII":float(r["conservative_xHII"]),
            "original_conservative_w_eV_per_H":float(r["conservative_w_ev_per_H"]),
            "root_centre_vs_conservative_max_abs":float(r["centre_vs_conservative_max_abs"]),
            "root_local_original_gas_contains_conservative":True,
            "root_local_original_photons_contain_conservative":True,
            "original_global_owner_interval_certified":False,
        })
    assert len(report)==16
    assert sum(int(x["source_packet_count"]) for x in report)==70656
    assert max_error["source_n"]<1e-12 and max_error["source_u"]<1e-12
    neg={"status":"NOT_RUN"}
    if negative_exe is not None:
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)
            src=directory/"S0_BI__CHARACTERISTIC__step001.txt"
            lines=src.read_text().splitlines()
            for i,line in enumerate(lines):
                if line.startswith("P|"):
                    e,n=line.split("|")[1:]
                    lines[i]="P|"+e+"|-0.00001"
                    break
            (folder/"S0_FORGED_NEGATIVE_PHOTON.txt").write_text("\n".join(lines)+"\n")
            output=folder/"BAD.csv"
            result_proc=subprocess.run([str(negative_exe),str(folder),str(output)],
                capture_output=True,text=True)
            assert result_proc.returncode!=0
            assert "NEGATIVE_OR_ZERO_PHOTON_SOURCE" in result_proc.stderr
            neg={"status":"PASS_REJECTED_NEGATIVE_PACKET",
                 "returncode":result_proc.returncode}
    fn=result/"SOURCE_S0_NATIVE_ROOT_PHYSICAL_SUPPORT.csv.gz"
    digest=save_csv(fn,report)
    data={"schema":"BASS_REI_F08_ORIGINAL_NATIVE_KRAWCZYK_POINT_INPUT_COMPATIBILITY_V1",
          "original_Rust_source_SHA51":"PASS","original_S0_source_SHA12":"PASS",
          "original_S0_photon_checkpoint_SHA4":"PASS",
          "parent_bass_PR328_HEAD":"b23c6915aeaeedbabbc8e90ffab74f2afa96c1e6",
          "original_source_rei_F08_pair":"0a2bec874a5aa1b12f882033a08497b913b44447148b50b6082093bb354868e8",
          "actual_source_root_count":16,"actual_source_packet_records":70656,
          "root_pass":16,"root_failure":0,
          "root_input_parent_enclosure":"EXACT_F64_POINT_NOT_GLOBAL_PROPAGATED_INTERVAL",
          "original_Rust_conservative_point_in_root":"16/16_PASS",
          "original_Rust_conservative_photons_in_root":"16/16_PASS",
          "max_Krawczyk_q":max(x["native_source_Krawczyk_q"] for x in report),
          "max_root_relative_gas_width":max(x["original_root_max_relative_gas_width"] for x in report),
          "root_original_span":"1,8,64,160 original S0 proper steps",
          "source_original_f08_full_owner_admission":"HOLD",
          "source_original_rei_f05_accept_tick":"160/131072",
          "not_F05_tick161_admission":True,
          "REI_CENTRAL":"28/88_REPORTED","BASS_UPPER":"9/15_SCOPED_SOURCE_MAPPED",
          "new_canonical_nodes":0,"new_bass_upper_complete_nodes":0,
          "negative_source_control":neg,
          "source_readback_errors_max":max_error,
          "data_sha256":digest,"data_file":fn.name,
          "source_raw_root_sha256":sha(result/"ROOT_ALL.csv"),
          "source_capture_manifest_sha256":sha(directory/"CAPTURE.json"),
          "root_source_status":"DERIVED_NUMERICALLY_CHECKED_IMPLEMENTATION_VERIFIED_SCOPED",
          "original_interval_propagation":"NOT_RUN",
          "original_full_14_LEDGER_MPRK_SDIRK":"NOT_RUN",
          "production":"HOLD","merging":False}
    (result/"RESULT.json").write_text(json.dumps(data,indent=2,sort_keys=True)+"\n")
    print("ORIGINAL_NATIVE_ROOT_SOURCE_AUDIT_PASS",json.dumps({
        "roots":16,"packets":70656,"max_q":data["max_Krawczyk_q"],
        "max_width":data["max_root_relative_gas_width"],
        "max_error":max_error,"negative":neg,"data_sha":digest},sort_keys=True))
    return data
if __name__=="__main__":
    import argparse
    a=argparse.ArgumentParser()
    a.add_argument("--inputs",type=Path,default=DATA)
    a.add_argument("--results",type=Path,default=RESULTS)
    a.add_argument("--negative-exe",type=Path)
    n=a.parse_args()
    audit(n.inputs,n.results,n.negative_exe)
