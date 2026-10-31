"""KM2O: replay source-owned actual GL12/16 second polarized Thomson gain at u=.25.

Source is immutable original KM2N stage-S2 GitHub Actions archived Einstein/P8/Peebles
first-scattered physical ray/screen fields. No new owner IVP or gravity double count.
This deterministic endpoint replay is a source-locked subset of the full 5-epoch
KM2O physical research package, NOT temporal evolution of J2.
"""
from __future__ import annotations
import argparse,hashlib,json,math
from pathlib import Path
import numpy as np
from research.dual_lane_km2n_20261031.once_scattered import remap_logfreq_source_tensor
from tilted_collision import TiltedThomson

PARENT_HEAD="4137f942d2a95999f4e6627b71042e98f7afc1b7"
ROOT=Path(__file__).resolve().parents[2]
SOURCES={
 12:"ee6d0972a165a515494cfd310e8367cf85886b7ba18da8bb0bb3b34c8f7da8b0",
 16:"3ebce3e3f1f77d2d75452d87dab664e716eda469664cc14cbb489275b02716d5",
}
def source_checksum(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def endpoint(grid):
    if grid not in SOURCES:raise ValueError("only original GL12 or GL16")
    home=ROOT/"research/dual_lane_km2n_20261031/results"
    ledger=home/f"KM2N_FIRST_SOURCE_LEDGER_GL{grid}.npz"
    initial=home/f"KM2N_ONCE_POL_SCREEN_GL{grid}_U40.npz"
    if source_checksum(ledger)!=SOURCES[grid]:raise ArithmeticError("immutable owner source data SHA mismatch")
    with np.load(ledger,allow_pickle=False) as z, np.load(initial,allow_pickle=False) as q:
        X1=q["screen_spectral_first_one"].copy()
        n=z["n"][40].copy();w=z["w"][40].copy()
        E=z["E"][40].copy();F=z["F"][40].copy()
        D=z["D"][40].copy();nu=float(z["nu"][40])
    N=len(n)
    if X1.shape!=(N,1200,2,2) or np.min(w)<=0 or np.min(D)<=0:
        raise ArithmeticError("invalid original positive spectral source")
    A=np.column_stack((np.ones(N),-n))
    gamma_p=np.linalg.lstsq(A,D,rcond=None)[0]
    gamma=float(gamma_p[0]);beta=gamma_p[1:]/gamma
    if not np.linalg.norm(beta)<1:raise ArithmeticError("invalid physical baryon tilt")
    op=TiltedThomson(n,w,beta)
    if max(np.max(abs(op.D-D)),np.max(abs(np.einsum("nij,nja->nia",op.S,E)-F)))>1e-9:
        raise ArithmeticError("original P8 screen/boost identity changed")
    Xe,gap1=remap_logfreq_source_tensor(X1,np.log(D))
    Xe=Xe*D[:,None,None,None]**4
    we=w/D**2
    Me=np.einsum("n,nia,nbac,njc->bij",we,F,Xe,F,optimize=True)
    G=3/(8*math.pi)*np.einsum("nia,bij,njc->nbac",F,Me,F,optimize=True)
    rest_in=float(np.einsum("n,nb->",we,np.trace(Xe,axis1=2,axis2=3)))
    rest_out=float(np.einsum("n,nb->",we,np.trace(G,axis1=2,axis2=3)))
    restgap=abs(rest_out/rest_in-1)
    if restgap>=5e-6:raise ArithmeticError("electron-rest source energy violation")
    X2,gap2=remap_logfreq_source_tensor(nu*D[:,None,None,None]**(-3)*G,-np.log(D))
    bol=X2.sum(axis=1)
    tr=np.trace(bol,axis1=1,axis2=2)
    energy=float(w@tr)
    loss=float(w@(nu*D*np.trace(X1.sum(axis=1),axis1=1,axis2=2)))
    J1=np.einsum("nia,nab,njb->nij",E,X1.sum(axis=1),E,optimize=True)
    expected=nu*D*np.trace(op.gain(J1),axis1=1,axis2=2)
    parity=float(np.max(abs(tr-expected))/max(float(abs(expected).max()),1e-300))
    if parity>2e-8 or max(gap1,gap2)>3e-11:
        raise ArithmeticError("original P8 or frequency source parity failed")
    tr2=np.einsum("nij,nji->n",bol,bol)
    pol=np.sqrt(np.maximum(0,2*tr2-tr**2))/np.maximum(tr,1e-300)
    pmean=float((w*tr)@pol/energy)
    if not 0<=pmean<=1:raise ArithmeticError("negative or super-polarized source")
    y=np.linspace(-.5+1/2400,.5-1/2400,1200)
    hist=np.einsum("n,nb->b",w,np.trace(X2,axis1=2,axis2=3))
    centroid=float(np.dot(hist,y)/energy)
    return {"GL":grid,"u":.25,"original_source_ledger_SHA256":SOURCES[grid],
       "second_gain_rate":energy,"first_loss_rate":loss,
       "mean_linear_polarization":pmean,"normal_frequency_centroid":centroid,
       "rest_elastic_relative_error":restgap,"original_P8_gain_parity":parity,
       "source_bin_count":len(hist),"new_Einstein_IVPs":0,"upper_DAG":"9/15"}

if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--output",required=True,type=Path)
    a=ap.parse_args();a.output.parent.mkdir(parents=True,exist_ok=True)
    obj={"source_parent_HEAD":PARENT_HEAD,"records":[endpoint(12),endpoint(16)],
         "production_ready":False,"merge_ready":False,"new_upper_completed":0}
    a.output.write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n")
    for r in obj["records"]:
        print("KM2O_ENDPOINT_REPLAY",r["GL"],r["second_gain_rate"],r["mean_linear_polarization"],r["original_P8_gain_parity"],flush=True)
