#!/usr/bin/env python3
"""Read-only capture of real original S0 native interval parents at chosen source ticks.

Changes no original Rust, F08 history, or physics formula. Uses BASS PR328 engine,
and makes immutable I/O receipts for interval-root experiments.
"""
import argparse,hashlib,json,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
UP=ROOT.parent
sys.path.insert(0,str(UP/"bass_rei_f08_s0_continuous_native_20261102"))
import continuous_s0 as C
from spectral_support import original_checkpoint
from s0_source_photon_thomson import source_histories

def sha(p):
    h=hashlib.sha256()
    with Path(p).open("rb") as f:
        for a in iter(lambda:f.read(1<<20),b""):h.update(a)
    return h.hexdigest()

def capture(out:Path,exe:Path,steps:int,ticks):
    out.mkdir(parents=True,exist_ok=True)
    h=source_histories()
    ref={b:{"h":h[b],"owner":original_checkpoint(b)} for b in ("S0_BI","S0_FLRW")}
    original=C.native_one
    tag={"branch":None,"kind":None}
    saved=[]
    def intercepted(exe0,inp,out0,stage,items):
        result=original(exe0,inp,out0,stage,items)
        step=round(stage["t0"]/C.DT)+1
        if step in ticks:
            fn=f'{tag["branch"]}__{tag["kind"]}__step{step:03d}.txt'
            dest=out/fn
            assert not dest.exists(),"immutable capture destination"
            shutil.copyfile(inp,dest)
            saved.append({"branch":tag["branch"],"mode":tag["kind"],"step":step,
               "file":fn,"SHA256":sha(dest),"source_packet_records":len(items),
               "parent_xHII":stage["gas"]["x"][0],
               "parent_w_ev_per_H":stage["gas"]["w"],
               "input_photon_n_per_H":sum(z[2] for z in items),
               "native_next_xHII":result["gas"]["x"][0],
               "native_next_T_K":result["temp"]})
        return result
    C.native_one=intercepted
    try:
        for branch in ("S0_BI","S0_FLRW"):
            for kind in ("CHARACTERISTIC","ORIGINAL_HAT"):
                tag["branch"]=branch;tag["kind"]=kind
                C.evolve(branch,kind,steps,exe,out,ref[branch])
    finally:
        C.native_one=original
    assert len(saved)==len(ticks)*4,(len(saved),len(ticks)*4)
    manifest={"schema":"BASS_REI_F08_S0_CONTINUOUS_NATIVE_ROOT_SNAPSHOT_V1",
       "science_parent_PR328":"b23c6915aeaeedbabbc8e90ffab74f2afa96c1e6",
       "original_Rust_coupled_primary_SHA256":"915d0a898100a54d04a525227e7fbeb870e321fcc14aaa91afd61352b6d4cf4b",
       "original_source":"F08_S0_13.7EV_INITIAL_AND_CONTINUOUS",
       "steps_total_each_model":steps,"captured_steps":sorted(ticks),
       "physics_source_condition":"GAS_AND_PHOTONS_CONTINUOUSLY_SELF_EVOLVED",
       "snapshots":sorted(saved,key=lambda x:(x["step"],x["branch"],x["mode"]))}
    (out/"CAPTURE.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"snapshots":len(saved),"total_source_packet_records":sum(x["source_packet_records"] for x in saved),"max_step":steps,"capture_sha256":sha(out/"CAPTURE.json")},sort_keys=True))
    return manifest

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=ROOT/"inputs")
    p.add_argument("--exe",type=Path,required=True)
    p.add_argument("--steps",type=int,default=160)
    p.add_argument("--ticks",default="1,8,64,160")
    a=p.parse_args()
    wanted={int(x) for x in a.ticks.split(",")}
    assert min(wanted)>=1 and max(wanted)<=a.steps and a.steps<=160
    capture(a.out,a.exe,a.steps,wanted)
