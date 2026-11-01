#!/usr/bin/env python3
"""BASS Sachs/Jacobi observer response on exact original REI F08 S0 source.

A separate BASS ray/beam consumer. Original REI source files are unmodified,
and the metric is deliberately prescribed Bianchi I, NOT Einstein-constrained.
Units c cm/s; H s^-1; time s; lengths cm and Mpc.
"""
from __future__ import annotations
import argparse, csv, gzip, hashlib, io, json, math
from pathlib import Path
import numpy as np
from numpy.polynomial.legendre import leggauss

HERE=Path(__file__).resolve().parent
SOURCE=HERE/"source"
OUT=HERE/"results"
C=29979245800.0
MPC=3.085677581491367e24
HMEAN=1.e-14
TOBS=1.e13
S0_BI=(1.01e-14, 0.99e-14, 1.e-14)
EXPECTED_SOURCE_SHA={
 "ORIGINAL_F08_S0_BIANCHI_THOMSON_SKY.csv.gz":"41fb767cc6c826047abf3799164f9e5b6a970c9dc879566147ad036226e4588d",
 "science_scenario_v1.json":"c83d2d43adda663707f99af2b45576eb4478cd94d3440a21fd21eaed32b5f2c1",
 "S0_BI-electron_density.csv.gz":"663911291bea564d314e1d46df9750c03a39fd5d9404eca6a7485776d894f723",
 "S0_FLRW-electron_density.csv.gz":"0b81cae87d6f90888d1d3def1995cd8d029625d1cc1dd11bffab94e8d30e7efa",
 "SOURCE_PROVENANCE.json":"6e6a9e729b4a6b5bbaa3f041991b91e39d141456a7501e59a3cbb127fe618ea4",
}
REI_HEAD="1605236b8172db411d862caa219322d6af6953b1"
REI_PAIR_ID="0a2bec874a5aa1b12f882033a08497b913b44447148b50b6082093bb354868e8"
QUAD_ORDER=48
GRIDS={(8,16),(16,32),(32,64)}
WINDOWS={.25,.5,.75,.95}

def sha(path):
 h=hashlib.sha256()
 with Path(path).open("rb") as f:
  for part in iter(lambda:f.read(1<<20),b""):h.update(part)
 return h.hexdigest()

def validate_source(src=SOURCE):
 for name,expected in EXPECTED_SOURCE_SHA.items():
  if sha(src/name)!=expected:raise ValueError("REI F08 source SHA mismatch "+name)
 scenario=json.loads((src/"science_scenario_v1.json").read_text())
 provenance=json.loads((src/"SOURCE_PROVENANCE.json").read_text())
 if provenance.get("source_pair_id")!=REI_PAIR_ID:raise ValueError("original matched source pair differs")
 if scenario["source"]["family"]!="S0" or scenario["background"]["tilt"]!=[0.,0.,0.]:
  raise ValueError("not the original no-tilt REI F08 source")
 if tuple(scenario["background"]["pairs"]["BIANCHI_I"]["H_per_s"])!=S0_BI:
  raise ValueError("prescribed H_i differ from original REI F08 S0")
 if scenario["background"]["H_mean_per_s"]!=HMEAN or scenario["time"]["t_end_s"]!=TOBS:
  raise ValueError("original proper clock differs")
 if scenario["constants"]["c_cm_s"]!=C:raise ValueError("original speed of light differs")
 if provenance["original_F08_return"]["scientific_admission"]!="HOLD":
  raise ValueError("F08 source admission changed without evidence")
 with gzip.open(src/"S0_BI-electron_density.csv.gz","rt") as f:
  rows=list(csv.DictReader(f))
 if len(rows)!=16001 or float(rows[0]["normal_time_s"])!=0 or float(rows[-1]["normal_time_s"])!=TOBS:
  raise ValueError("wrong original 16001 electron history")
 with gzip.open(src/"ORIGINAL_F08_S0_BIANCHI_THOMSON_SKY.csv.gz","rt") as f:
  sky=list(csv.DictReader(f))
 if len(sky)!=10752:raise ValueError("original 10752 rays missing")
 for row in sky:
  if (int(row["angular_nmu"]),int(row["angular_nphi"])) not in GRIDS:raise ValueError("unexpected source angular grid")
  if float(row["window_fraction"]) not in WINDOWS:raise ValueError("unexpected original source window")
  if abs(sum(float(row[k])**2 for k in ("nx","ny","nz"))-1)>3e-14:raise ValueError("nonunit observed ray")
  if float(row["tau_BI"])<0 or float(row["tau_FLRW"])<0:raise ValueError("negative original optical depth")
 return sky

def basis(n):
 """Orthonormal θ/φ basis in the original observed normal-frame sky."""
 n=np.asarray(n,float)
 mu=n[:,2]
 phi=np.arctan2(n[:,1],n[:,0])
 ss=np.sqrt(np.maximum(0.,1-mu**2))
 e_theta=np.column_stack((mu*np.cos(phi),mu*np.sin(phi),-ss))
 e_phi=np.column_stack((-np.sin(phi),np.cos(phi),np.zeros(len(n))))
 if np.max(abs(np.sum(e_theta*n,axis=1)))>2e-14:raise ValueError("not an observed transverse frame")
 return np.stack((e_theta,e_phi),axis=-1)

def beam(H,n,te,tobs=TOBS,order=QUAD_ORDER):
 """Exact path-direction Jacobi integral with finite Gaussian time quadrature.

 Return DA in units c/Hmean, screen axis ratio and two eigen-DA axes.
 Source-constant-z emission clock derivative is longitudinal and screen-projected away.
 """
 H=np.asarray(H,float); n=np.asarray(n,float); te=np.asarray(te,float)
 if H.shape!=(3,) or n.ndim!=2 or n.shape[1]!=3 or te.shape!=(len(n),):raise ValueError("Sachs input shape")
 if np.any(H<=0) or np.any(te<0) or np.any(te>=tobs) or np.max(abs(np.linalg.norm(n,axis=1)-1))>1e-10:
  raise ValueError("invalid Sachs source domain")
 q,w=leggauss(order)
 Delta=tobs-te
 t=te[:,None]+(q[None,:]+1)*Delta[:,None]/2
 ai=np.exp((t[:,:,None]-tobs)*H[None,None,:])
 inva2=ai**(-2)
 wph=np.sqrt(np.sum((n[:,None,:]**2)*inva2,axis=-1))
 E=basis(n)
 # J_iA = int [e_Ai/(a_i^2 omega) - n_i/a_i^2 * (sum n_j e_Aj/a_j^2)/omega^3] c dt.
 ne=np.einsum("ni,nq i,niA->nqA",n,inva2,E,optimize=True)
 term1=inva2[:,:,:,None]*E[:,None,:,:]/wph[:,:,None,None]
 term2=(n[:,None,:,None]*inva2[:,:,:,None]*ne[:,:,None,:])/wph[:,:,None,None]**3
 Jdim=(HMEAN*Delta/2)[:,None,None]*np.einsum("q,nqiA->niA",w,term1-term2,optimize=True)
 ais=np.exp((te[:,None]-tobs)*H[None,:])
 qs=(n/ais)
 qs/=np.linalg.norm(qs,axis=1)[:,None]
 Jphysical=ais[:,:,None]*Jdim
 screen=Jphysical-qs[:,:,None]*np.einsum("ni,niA->nA",qs,Jphysical)[:,None,:]
 gram=np.einsum("niA,niB->nAB",screen,screen,optimize=True)
 lamb=np.linalg.eigvalsh(gram)
 if not np.all(np.isfinite(lamb)) or np.min(lamb)<=0:raise ArithmeticError("source beam has non-positive area")
 DA_dim=(np.prod(lamb,axis=-1))**.25
 axes=np.sqrt(lamb)
 ratio=axes[:,1]/axes[:,0]
 return DA_dim,ratio,axes,gram

def directional_lookback(H,n,z,tobs=TOBS):
 """Solve observer-relative redshift in the exact original source metric."""
 from scipy.optimize import brentq
 H=np.asarray(H);n=np.asarray(n)
 target=np.log1p(z)
 def f(d):return .5*np.log(np.dot(n*n,np.exp(2*H*d)))-target
 if f(0)>=0 or f(tobs)<0:raise ValueError("redshift outside original S0 support")
 return brentq(f,0,tobs,xtol=.02)

def source_sky_to_optical_rows(sky,order=QUAD_ORDER):
 by={}
 for i,row in enumerate(sky):
  key=(float(row["window_fraction"]),int(row["angular_nmu"]),int(row["angular_nphi"]))
  by.setdefault(key,[]).append((i,row))
 out=[None]*len(sky)
 stats=[]
 for key,items in sorted(by.items()):
  ids=[a for a,_ in items]; rec=[b for _,b in items]
  n=np.array([[float(r[k]) for k in ("nx","ny","nz")] for r in rec])
  te=np.array([float(r["emission_time_s"]) for r in rec])
  z=np.array([float(r["relative_redshift"]) for r in rec])
  d,axis,axes,_=beam(S0_BI,n,te,order=order)
  base=z/(1+z) # FLRW de Sitter normalised by c/Hmean
  ratio=d/base
  tau=np.array([float(r["tau_BI"]) for r in rec])
  tau_f=np.array([float(r["tau_FLRW"]) for r in rec])
  flux=np.exp(-(tau-tau_f))/(ratio**2) # etherington DL cancels fixed observed z
  dm=-2.5*np.log10(flux)
  # both the BASS beam geometry and REI opacity history refer to SAME S0 source/metric and emission clock
  red=np.sqrt(np.sum(n*n*np.exp(2*np.asarray(S0_BI)[None,:]*(TOBS-te)[:,None]),axis=1))-1
  if np.max(abs(red-z))>4e-14:raise ArithmeticError("REI/BASS identical source redshift failed")
  if np.any(d<=0) or np.any(flux<=0):raise ValueError("invalid source observable")
  for i,rr,dd,aa,fl,mag in zip(ids,rec,ratio,axis,flux,dm):
   r=dict(rr)
   r.update({"DA_BI_cm":float(dd*float(rr["relative_redshift"])/(1+float(rr["relative_redshift"]))*C/HMEAN),
             "DA_BI_over_FLRW":float(dd),
             "DA_FLRW_cm":float(float(rr["relative_redshift"])/(1+float(rr["relative_redshift"]))*C/HMEAN),
             "DL_BI_Mpc":float(dd*float(rr["relative_redshift"])*(1+float(rr["relative_redshift"]))*C/HMEAN/MPC),
             "screen_major_minor_axis_ratio":float(aa),
             "conditional_screened_flux_ratio_BI_over_FLRW":float(fl),
             "conditional_delta_magnitude_BI_minus_FLRW":float(mag)})
   # corrected physical units: ratio dd multiplies base; for DA_BI ratio * base is correct.
   out[i]=r
  stats.append({"window_fraction":key[0],"n_mu":key[1],"n_phi":key[2],
   "rays":len(rec),"z_relative":float(z[0]),
   "DA_BI_over_FLRW_mean":float(np.mean(ratio)),"DA_BI_over_FLRW_min":float(np.min(ratio)),
   "DA_BI_over_FLRW_max":float(np.max(ratio)),
   "screen_axis_ratio_mean":float(np.mean(axis)),"screen_axis_ratio_max":float(np.max(axis)),
   "conditional_screened_flux_ratio_mean":float(np.mean(flux)),
   "conditional_delta_mag_min":float(np.min(dm)),"conditional_delta_mag_max":float(np.max(dm)),
   "tau_BI_mean_reused":float(np.mean(tau)),
   "source_matched_DA_vs_tau_angular_pearson":float(np.corrcoef(np.log(ratio),tau-tau_f)[0,1]),
   "rms_geometric_magnitude_over_thomson_magnitude":float(
     np.sqrt(np.mean((5*np.log10(ratio))**2))/
     max(np.sqrt(np.mean(((2.5/np.log(10))*(tau-tau_f))**2)),1e-300)),
   "log_DA_quadrupole_diag":[float(np.mean((np.log(ratio)-np.mean(np.log(ratio)))*(n[:,j]**2-1./3))) for j in range(3)],
   "tau_quadrupole_diag":[float(np.mean(((tau-tau_f)-np.mean(tau-tau_f))*(n[:,j]**2-1./3))) for j in range(3)]})
 return out,stats

def write_gzip(path,rows):
 keys=list(rows[0]);path.parent.mkdir(parents=True,exist_ok=True)
 with path.open("wb") as f:
  with gzip.GzipFile(filename="",mode="wb",compresslevel=6,mtime=0,fileobj=f) as gf:
   with io.TextIOWrapper(gf,encoding="utf8",newline="") as io_: 
    writer=csv.DictWriter(io_,fieldnames=keys);writer.writeheader();writer.writerows(rows)

def run(src=SOURCE,out=OUT,order=QUAD_ORDER):
 global SOURCE
 sky=validate_source(src)
 out=Path(out);out.mkdir(parents=True,exist_ok=True)
 rows,stats=source_sky_to_optical_rows(sky,order)
 assert len(rows)==10752
 write_gzip(out/"BASS_REI_F08_S0_SOURCE_MATCHED_SACHS_OBSERVABLES.csv.gz",rows)
 result={"schema":"bass.rei_igm.f08_s0_matched_sachs_optics.v1","source_owner_repo":"cosmosapjw-quantum/rei_bianchi",
  "source_pr":349,"source_head":REI_HEAD,"source_pair_id":REI_PAIR_ID,
  "BASS_source":"source-owned exact null Jacobi area for prescribed same F08 S0 Bianchi-I metric and proper-clock",
  "metric":"ds2=-c2dt2+sum ai(t)^2 dxi^2, ai(t_o)=1","H_per_s":S0_BI,"observer_time_s":TOBS,
  "source_sha256":EXPECTED_SOURCE_SHA,"num_physical_ray_rows":len(rows),
  "source_conditioned_electron_tau_reused":True,"source_emission_equivalence_to_KM2":False,
  "new_source_rei_ivps":0,"new_bass_einstein_ivps":0,
  "quadrature_order":order,"physical_outputs":stats,"REI_central":"28/88_REPORTED","BASS_upper":"9/15_SCOPED",
  "canonical_delta":0,"production":"HOLD","merge":"HOLD","auto_next":False,
  "disclaimers":["Original F08 S0 one-cell isotropic emissivity and prescribed metric are not CMB and not self-consistent Einstein equations",
   "The conditional screened standard-candle flux ratio assumes no scattering gain and no host luminosity evolution",
   "No automatic transplant of KM2 Lyalpha polarization / electron history or CE1AS massless source",
   "This is finite angular/time grid, not an interval-certified continuum light cone or observational bound",
   "REI F05 canonical first interval and F09 atomic domain both remain BLOCKED"]}
 (out/"BASS_REI_F08_S0_MATCHED_SACHS_RESULT.json").write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
 print("REI_F08_S0_MATCHED_SACHS",len(rows),json.dumps([x for x in stats if (x['n_mu'],x['n_phi'])==(32,64)],sort_keys=True))
 return result

if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--source",type=Path,default=SOURCE);p.add_argument("--output",type=Path,default=OUT);p.add_argument("--order",type=int,default=QUAD_ORDER)
 a=p.parse_args();run(a.source,a.output,a.order)
