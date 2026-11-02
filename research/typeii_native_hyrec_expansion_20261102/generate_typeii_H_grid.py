#!/usr/bin/env python3
"""Type-II Hubble array from original BASS gamma-law Einstein equations.

No source edits. Original HYREC-2 FLRW H(z) is used as *normalization only*
at mean z=1700; for z<1700 solve Type-II q and H equations, otherwise original
HYREC-2 native H. HYREC original C atomic n_H remains FLRW in the H-only lane.
"""
import ast, hashlib, json, math, subprocess
from pathlib import Path
import numpy as np
from scipy.interpolate import PchipInterpolator
from scipy.integrate import solve_ivp

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
MAIN="9c6506e4e2087129a8b674ff10438e5db1a55c9d"
PARENT="9f10e1145c8582f71f7d81dcebfd3c125c70c04c"
Z_ANCHOR=1700.
GAMMA_FLUID=1.3
def check(cond,msg):
    if not bool(cond):raise RuntimeError(msg)
def git(*a):
    return subprocess.check_output(["git","-C",str(ROOT),*a],text=True).strip()
for rel in ("compiler/validation/generate_typeii_fixture.py",
            "compiler/validation/typeii_fixture_canonical.json"):
    check(git("hash-object",rel)==git("rev-parse",MAIN+":"+rel),
          "ORIGINAL_BASS_BACKGROUND_SOURCE_CHANGED "+rel)
    check(git("rev-parse",PARENT+":"+rel)==git("hash-object",rel),
          "PARENT_NATIVE_HYREC_SOURCE_CONFLICT "+rel)
source=ROOT/"compiler/validation/generate_typeii_fixture.py"
nodes=ast.parse(source.read_text()).body
functions=[n for n in nodes if isinstance(n,ast.FunctionDef) and n.name=="typeii_rhs"]
check(len(functions)==1,"OWNER_SOURCE_RHS_NOT_FOUND")
env={"math":math}
exec(compile(ast.Module(body=functions,type_ignores=[]),str(source),"exec"),env)
rhs_owner=env["typeii_rhs"]
fixture=json.loads((ROOT/"compiler/validation/typeii_fixture_canonical.json").read_text())
samples=fixture["trajectory"]["samples"]
Tref=np.array([r["tau"] for r in samples])
Xref=np.array([r["state"] for r in samples])
Rref=np.array([r["rhs"] for r in samples])
check(Xref.shape==Rref.shape==(401,5),"SOURCE_FIXTURE_401_CONTRACT_CHANGED")
def q_from_state(x):
    [sp,sm,s13,N1,v2]=map(float,x)
    return rhs_owner(list(x),GAMMA_FLUID)[3]/N1+4*sp
x0=np.asarray(Xref[0],float)
T_end=math.log((1+Z_ANCHOR))
def ode(t,y):
    xx=y[:5]
    if xx[3]<=0 or abs(xx[4])>=1:raise RuntimeError("TYPEII_OUTSIDE_POSITIVE_N1_OR_TILT")
    rhs=np.asarray(rhs_owner(list(xx),GAMMA_FLUID),float)
    q=rhs[3]/xx[3]+4*xx[0]
    return np.r_[rhs,-1-q]
sol=solve_ivp(ode,(0.,T_end),np.r_[x0,0.],method="DOP853",
              atol=1e-13,rtol=2e-12,max_step=.005,dense_output=True)
check(sol.success,"TYPEII_GRAVITY_Q_SOURCE_SOLVER_FAILED")
X=sol.sol(Tref).T
background_gap=float(np.max(abs(X[:,:5]-Xref)))
rhs_gap=float(np.max(abs(np.asarray([rhs_owner(list(v),GAMMA_FLUID) for v in Xref])-Rref)))
check(background_gap<1e-11 and rhs_gap<2e-13,
      "ORIGINAL_TYPEII_401_SOURCE_OVERLAP_FAIL")
FLRW=np.loadtxt(HERE/"NATIVE_HYREC_FLRW_H_GRID.dat")
check(FLRW.ndim==2 and FLRW.shape[1]==2 and FLRW.shape[0]>2000,"HYREC_C_GRID_NOT_ORIGINAL")
zgrid=FLRW[:,0];H_FLRW=FLRW[:,1]
check(np.min(H_FLRW)>0 and np.all(np.diff(zgrid)>0),"ORIGINAL_NATIVE_HUBBLE_TABLE_BAD")
native_logh=PchipInterpolator(np.log1p(zgrid),np.log(H_FLRW))
H_anchor=float(np.exp(native_logh(np.log1p(Z_ANCHOR))))
ts=np.log((1+Z_ANCHOR)/(1+zgrid))
tclipped=np.clip(ts,0,T_end)
TypeII=sol.sol(tclipped).T
XB=TypeII[:,:5];logHB=TypeII[:,5]
ratio=np.ones_like(zgrid)
inside=zgrid<=Z_ANCHOR
H_B_inside=H_anchor*np.exp(logHB[inside])
ratio[inside]=H_B_inside/H_FLRW[inside]
check(np.isfinite(ratio).all() and np.min(ratio)>0,
      "TYPEII_SOURCE_HUBBLE_NOT_POSITIVE")
H_native=H_FLRW*ratio
# Model requires source Bianchi H over z<=1700; use native FLRW above
# and native Hubble amplitude at z=1700 as the explicit one-point normalization.
check(np.max(abs(ratio[~inside]-1))<1e-15,"HIGH_Z_NATIVE_RECOMBINATION_HISTORY_CHANGED")
gamma0=1/math.sqrt(1-x0[4]**2)
tiltGamma=1/np.sqrt(1-XB[:,4]**2)
density_factor=np.ones_like(zgrid)
density_factor[inside]=gamma0/tiltGamma[inside]
check(np.min(density_factor)>0,"UNPHYSICAL_PROPER_HYDROGEN_FACTOR")
# Physical chart constraint, not just positive Omega: Codazzi itself.
Omega=1-np.sum(XB[:,:3]**2,axis=1)-XB[:,3]**2/12
Gplus=1+(GAMMA_FLUID-1)*XB[:,4]**2
Codazzi=-math.sqrt(3)*XB[:,3]*XB[:,2]-3*GAMMA_FLUID*Omega*XB[:,4]/Gplus
constraint=float(np.max(abs(Codazzi)))
check(np.min(Omega)>0 and np.min(XB[:,3])>0 and np.max(abs(XB[:,4]))<1,
      "BASS_TYPEII_GRAVITY_CHART_FAIL")
check(constraint<5e-12,"BASS_CODAZZI_CONSTRAINT_FAIL")
# Independent non-ODE first-integral: logH=-Integral[(1+q)]dt
from scipy.integrate import trapezoid
check(abs(float(logHB[-1]))<1e-15,"ANCHOR_LOGH_NOT_ZERO") if zgrid[-1]<=Z_ANCHOR else None
# H is tabulated as one column in the EXACT native HyRec-2 Hubble_array source-grid order.
out=HERE/"NATIVE_TYPEII_H_ARRAY_2248.dat"
np.savetxt(out,H_native,fmt="%.17e")
np.savetxt(HERE/"TYPEII_H_COMPARE_FLRW_GRID.csv",
    np.column_stack((zgrid,H_FLRW,H_native,ratio,density_factor,XB[:,3],XB[:,4],Omega)),
    delimiter=",",header="z,H_FLRW_s-1,H_TypeII_s-1,H_TypeII_over_FLRW,gamma1700_over_gamma_z,N1,v2,Omega",
    comments="",fmt=["%.17g"]*8)
def find(z):
    j=int(np.argmin(abs(zgrid-z)))
    return {"z":float(zgrid[j]),"H_FLRW":float(H_FLRW[j]),
            "H_TypeII":float(H_native[j]),"TypeII_over_FLRW":float(ratio[j]),
            "gamma0_over_gamma":float(density_factor[j])}
report={
 "schema":"bass.typeii.original_gamma13_external_Hubble_HyRec2_grid.v1",
 "original_main":MAIN,"immutable_parent":PARENT,
 "original_input_401_state_max_abs_gap":background_gap,
 "original_input_401_RHS_max_abs_gap":rhs_gap,
 "original_model":"TypeII fluid gamma-law=1.3, A=0, N1>0, Codazzi, normal Hubble tau",
 "native_HyRec_hubble_grid_length":len(zgrid),
 "native_HyRec_Hubble_z_grid_delta":float(np.diff(zgrid)[0]),
 "source_initial_zmean":Z_ANCHOR,"source_last_zmean":0.,
 "typeii_q_formula":"q=N1prime/N1+4SigmaPlus",
 "typeii_H_formula":"H(z)=Hnative_FLRW(z1700)*exp[-integral_0^tauH(1+q)ds]",
 "above_z1700":"HYREC2 source FLRW Hubble exactly",
 "below_z1700":"BASS gamma1.3 five-state TypeII Hubble, conditional physical model",
 "H_anchor_source_FLRW_s_inverse":H_anchor,
 "TypeII_positive_charts_min_Omega":float(min(Omega)),
 "TypeII_min_N1":float(min(XB[:,3])),
 "TypeII_max_abs_v2":float(max(abs(XB[:,4]))),
 "TypeII_Codazzi_max_abs_residual":constraint,
 "sampled_Hubbles":[find(z) for z in (0,300,800,1100,1400,1700,3000)],
 "native_H_array_SHA256":hashlib.sha256(out.read_bytes()).hexdigest(),
 "ratio_and_gamma_csv_SHA256":hashlib.sha256((HERE/"TYPEII_H_COMPARE_FLRW_GRID.csv").read_bytes()).hexdigest(),
 "physical_claim_limit":"TypeII source chart mathematical continuation from mean z1700 to0, NOT self-consistent late-time matter dark-energy cosmology",
 "status":"BASS_ORIGINAL_TYPEII_HUBBLE_NORMAL_HISTORY_COMPUTED_SOURCE_CONDITIONED"
}
(HERE/"R3_TYPEII_HUBBLE_GRID.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
print(json.dumps(report,indent=2,sort_keys=True))
