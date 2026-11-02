#!/usr/bin/env python3
"""Independent original Type-II five-state + 26 photon geodesic integration to mean z=300.

External HYREC-2 H/He FLRW ionization history supplies a scalar x_e(z_mean).
This is a conditional finite-observer redshift z=300 attenuation/last-event kernel,
NOT a Type-II-native atomic history or full photon-scattering Boltzmann calculation.
"""
from __future__ import annotations
import ast,csv,hashlib,json,math,subprocess
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import PchipInterpolator,CubicHermiteSpline

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PARENT="0bee79382753d95c610f5e86431f9e7c318c27d5"
ORIGINAL="9c6506e4e2087129a8b674ff10438e5db1a55c9d"
def check(ok,reason):
    if not bool(ok):raise RuntimeError(reason)
def git(*a):return subprocess.check_output(["git","-C",str(ROOT),*a],text=True).strip()
def hashfile(p):return hashlib.sha256(p.read_bytes()).hexdigest()
source=ROOT/"compiler/validation/generate_typeii_fixture.py"
check(git("hash-object",str(source.relative_to(ROOT)))==
      git("rev-parse",ORIGINAL+":"+str(source.relative_to(ROOT))),
      "SOURCE_BACKGROUND_NOT_IMMUTABLE")
t=ast.parse(source.read_text())
func=[x for x in t.body if isinstance(x,ast.FunctionDef) and x.name=="typeii_rhs"]
check(len(func)==1,"TYPEII_ORIGINAL_RHS_NOT_FOUND")
environment={"math":math}
exec(compile(ast.Module(body=func,type_ignores=[]),str(source),"exec"),environment)
rhs=environment["typeii_rhs"]
original_fixture=json.loads((ROOT/"compiler/validation/typeii_fixture_canonical.json").read_text())["trajectory"]["samples"]
oldT=np.array([s["tau"] for s in original_fixture])
oldX=np.array([s["state"] for s in original_fixture])
check(oldX.shape==(401,5) and np.max(abs(np.diff(oldT)-.0005))<1e-13,
      "ORIGINAL_TYPEII_401_SOURCE_UNRECOGNIZED")
photon_src=ROOT/"research/typeii_liouville_optdepth_20261101/PHOTON_RAYS_401X26.csv"
check(hashfile(photon_src)=="9f1400588d39ba3a61020542e14b0e372c8e9be1af130f8c64ed8829b23ad217",
      "PARENT_401X26_NORMAL_RAYS_DRIFT")
oldR=np.zeros((26,401,3));oldLogE=np.zeros((26,401));seen=np.zeros((26,401),bool)
with photon_src.open(newline="") as f:
 for r in csv.DictReader(f):
    j=int(r["ray_id"]);i=int(round(float(r["tau_H"])/.0005))
    check(0<=j<26 and 0<=i<401 and not seen[j,i],"SOURCE_RAY_INDEX_DUPLICATION")
    seen[j,i]=True
    oldR[j,i]=[float(r["n_x"]),float(r["n_y"]),float(r["n_z"])]
    oldLogE[j,i]=float(r["ln_E_normal"])
check(np.all(seen),"SOURCE_RAY_MISSING")
initial_rays=oldR[:,0,:]
sqrt3=math.sqrt(3)
T0=0.; Tfinal=math.log(1701/301)
def system(t,y):
    st=y[:5]
    dr=np.asarray(rhs(list(st),1.3),float)
    sp,sm,s13,N1,v=st
    if N1<=0 or not np.isfinite(N1):
        raise RuntimeError("EXIT_PHYSICAL_N1_CHART")
    dec=dr[3]/N1+4*sp
    rates=y[6:].reshape((26,4))
    nx,ny,nz=rates[:,0],rates[:,1],rates[:,2]
    Ry=sqrt3*s13
    sx=-2*sp*nx+Ry*nz
    sy=(sp+sqrt3*sm)*ny
    sz=Ry*nx+(sp-sqrt3*sm)*nz
    snn=nx*sx+ny*sy+nz*sz
    dnx=-sx+snn*nx+Ry*nz
    dny=-sy+snn*ny-N1*nx*nz
    dnz=-sz+snn*nz-Ry*nx+N1*nx*ny
    raydot=np.stack((dnx,dny,dnz,-1-snn),axis=1)
    return np.r_[dr,-(1+dec),raydot.ravel()]
initialH=1.0520008349779968e-13
y0=np.r_[oldX[0],np.log(initialH),np.column_stack((initial_rays,np.zeros(26))).ravel()]
sol=solve_ivp(system,(T0,Tfinal),y0,method="DOP853",atol=5e-14,rtol=3e-12,
              max_step=.003,dense_output=True)
check(sol.success,"TYPEII_RECOMBINATION_WINDOW_GEODESIC_ODE_FAILED")
# Build time grid including ALL original fixture knots for exact source overlap and
# enough additional resolution to capture the recombination optical-depth turnover.
newtime=np.arange(0,Tfinal,.002)
time=np.unique(np.r_[newtime,oldT,Tfinal])
full=sol.sol(time)
X=full[:5].T;logH=full[5];geo=full[6:].T.reshape((len(time),26,4))
nn=geo[:,:,:3].transpose(1,0,2) # (26,t,3)
energy=geo[:,:,3].T
omega=1-np.sum(X[:,[0,1,2]]**2,axis=1)-X[:,3]**2/12
check(np.min(omega)>0 and np.min(X[:,3])>0 and np.max(abs(X[:,4]))<1,
      "TYPEII_EXTENDED_BACKGROUND_OUTSIDE_PHYSICAL_CHART")
normerr=float(np.max(abs(np.linalg.norm(nn,axis=2)-1)))
check(normerr<5e-10,"TYPEII_EXTENDED_GEODESIC_UNIT_NORM_DRIFT")
ref=sol.sol(oldT)
bger=float(np.max(abs(ref[:5].T-oldX)))
parentn=ref[6:].T.reshape((401,26,4))
rayerr=float(np.max(abs(parentn[:,:,:3].transpose((1,0,2))-oldR)))
Eerr=float(np.max(abs(parentn[:,:,3].T-oldLogE)))
check(bger<3e-10 and rayerr<3e-9 and Eerr<3e-9,
      "TYPEII_SOURCE_401_REPRODUCTION_FAILURE")
# Actual original HYREC2 data source, with strict numerical artifact locking.
source_report=json.loads((HERE/"HYREC2_NATIVE_SOURCE_REPORT.json").read_text())
zXe=HERE/"HYREC2_FLRW_XE_TM_8000.dat"
check(hashfile(zXe)==source_report["published_output_sha256"],"HYREC2_NATIVE_TABULATED_HISTORY_DRIFT")
table=np.loadtxt(zXe)
check(table.shape==(8000,3),"HYREC2_NATIVE_TABLE_MISMATCH")
xe=PchipInterpolator(np.log1p(table[::-1,0]),table[::-1,1],extrapolate=False)
Tm=PchipInterpolator(np.log1p(table[::-1,0]),table[::-1,2],extrapolate=False)
nH0=11.223846333047e-6*.0224*(1-.245)
g0=1/math.sqrt(1-X[0,4]**2)
N0=nH0*1701**3*g0
sc=6.6524587e-25*2.99792458e10

def geometry(t):
    f=sol.sol(t)
    s=np.asarray(t)
    v=f[4];H=np.exp(f[5]);zmean=1701*np.exp(-s)-1
    if np.min(zmean)<1 or np.max(zmean)>8000 or np.min(H)<=0:
        raise RuntimeError("PHYSICAL_H_OR_HYREC_EXTRAPOLATED")
    electron_frac=xe(np.log1p(zmean))
    W=sc*electron_frac*N0*np.exp(-3*s)/H
    rays=f[6:].reshape((26,4,-1)) if np.ndim(s)!=0 else f[6:].reshape((26,4))
    ny=rays[:,1,:] if np.ndim(s)!=0 else rays[:,1]
    q=1-v*ny
    return W,q,electron_frac,zmean,Tm(np.log1p(zmean)),ny

from numpy.polynomial.legendre import leggauss
def attenuation(order):
    points,weights=leggauss(order)
    tau=np.zeros((26,len(time)))
    even=np.zeros(len(time));odd=np.zeros(len(time))
    for k,(a,b) in enumerate(zip(time[:-1],time[1:])):
        zz=a+.5*(b-a)*(points+1)
        w,q,xe_t,red,tm,ny=geometry(zz)
        if np.min(w)<=0 or np.min(q)<=0:raise RuntimeError("NONPOSITIVE_THOMSON_HAZARD")
        rates=w[None,:]*q
        tau[:,k+1]=tau[:,k]+.5*(b-a)*(rates@weights)
        vv=sol.sol(zz)[4]
        even[k+1]=even[k]+.5*(b-a)*np.dot(weights,w)
        odd[k+1]=odd[k]+.5*(b-a)*np.dot(weights,w*vv)
    return tau,even,odd
depth,even,odd=attenuation(8)
depth16,_,_=attenuation(16)
err_gl=float(max(abs(depth-depth16).flat))
check(err_gl<1e-7,"TYPEII_EXTENDED_GAUSS_CONVERGENCE_FAIL")
axp=next(k for k in range(26) if np.max(abs(initial_rays[k]-[0,1,0]))<1e-14)
axm=next(k for k in range(26) if np.max(abs(initial_rays[k]-[0,-1,0]))<1e-14)
axerr=float(max(np.max(abs(depth[axp]-(even-odd))),np.max(abs(depth[axm]-(even+odd)))))
check(axerr<1e-10,"EXTENDED_AXIS_ODDEVEN_IDENTITY_FAIL")
# Formal finite-observer z=300 line-of-sight attenuation (not full radiative-transfer gain).
future=depth[:,-1,None]-depth
W_at,flux_at,xe_at,z_at,tm_at,ny_at=geometry(time)
hazard=W_at[None,:]*flux_at
screen=hazard*np.exp(-future)
jmax=np.argmax(screen,axis=1)
peaks=np.array([z_at[j] for j in jmax])
# For normalization, test actual line-of-sight survival mass by a second
# dedicated solution-free interval quadrature with a Hermite primitive.
from scipy.interpolate import CubicHermiteSpline
prefix=CubicHermiteSpline(time,depth,hazard,axis=1)
xi,wi=leggauss(8)
mass=np.zeros(26)
for a,b in zip(time[:-1],time[1:]):
    xx=a+.5*(b-a)*(xi+1)
    w,q,_,_,_,_=geometry(xx)
    fut=depth[:,-1,None]-prefix(xx)
    mass+=.5*(b-a)*((w[None,:]*q*np.exp(-fut))@wi)
expected=-np.expm1(-depth[:,-1])
norm_gap=float(max(abs(mass-expected)))
check(norm_gap<8e-8,"FINITE_OBSERVER_KERNEL_MASS_NOT_NORMALIZED")
# Single source-contained physical record, with separation of models and science gates.
summary={
 "schema":"bass.typeii.extended_to_mean_z300_native_hyrec2_window.26ray.v1",
 "source_TypeII":"original source five-state gamma-law ODE, Bianchi II photon Liouville",
 "external_HyRec":"original FLRW H/He x_e and T_m; not native TypeII recombination",
 "model_limit":"prescribed gamma-law TypeII plus conserved hydrogen current and FLRW native H/He x_e on mean z",
 "original_fixture_rows":401,
 "extended_time_samples":len(time),
 "new_time_domain":[T0,Tfinal],"new_mean_z_final":300.,
 "extends_past_original_fixture":True,
 "source_background_401_max_gap":bger,
 "source_ray_direction_401_max_gap":rayerr,
 "source_ray_logEnergy_401_max_gap":Eerr,
 "max_extended_null_direction_norm_error":normerr,
 "min_background_Omega":float(min(omega)),
 "min_N1":float(min(X[:,3])),
 "max_abs_tilt_v2":float(max(abs(X[:,4]))),
 "endpoint_TypeII_state":X[-1].tolist(),
 "endpoint_H_s_inv":float(np.exp(logH[-1])),
 "native_HyRec_xe_at_z300":float(xe(np.log1p(300.))),
 "finite_window_26ray_depth_min":float(min(depth[:,-1])),
 "finite_window_26ray_depth_max":float(max(depth[:,-1])),
 "finite_window_depth_plus_axial":float(depth[axp,-1]),
 "finite_window_depth_minus_axial":float(depth[axm,-1]),
 "finite_window_depth_asymmetry":float((depth[axm,-1]-depth[axp,-1])/(depth[axm,-1]+depth[axp,-1])),
 "source_axial_odd_even_gap":axerr,
 "8_vs_16_Gauss_max_depth_gap":err_gl,
 "finite_z300_last_event_peak_mean_z_min":float(min(peaks)),
 "finite_z300_last_event_peak_mean_z_max":float(max(peaks)),
 "finite_z300_last_event_peak_mean_z_axial_plus":float(peaks[axp]),
 "finite_z300_last_event_peak_mean_z_axial_minus":float(peaks[axm]),
 "finite_z300_last_event_mass_normalization_gap":norm_gap,
 "not_a_CMB_visibility_prediction":"finite source interval, no scattering gain, angle rerouting, coupled Einstein atom model or today-observer propagation",
 "claim":"SOURCE_CONDITIONAL_HYREC2_BIANCHI_GEODESIC_EXTENDED_RECOMBINATION_WINDOW_NUMERICALLY_CHECKED"
}
(HERE/"EXTENDED_RECOMB_WINDOW_RESULT.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
with (HERE/"EXTENDED_TYPEII_HYREC2_RAY_26.csv").open("w",newline="") as f:
    writer=csv.writer(f,lineterminator="\n")
    writer.writerow(["ray","tau_H","z_mean_not_observed","n_x","n_y","n_z",
                     "ln_E_normal","H_s_inv","HyRec_xe_FLRW","HyRec_Tm_K_FLRW",
                     "Thomson_hazard","cumulative_depth","future_depth_to_z300","last_event_kernel_to_z300"])
    for j in range(26):
        for k,t in enumerate(time):
            writer.writerow([j]+[format(float(x),".17g") for x in
                [t,z_at[k],*nn[j,k],energy[j,k],math.exp(logH[k]),xe_at[k],tm_at[k],
                 hazard[j,k],depth[j,k],future[j,k],screen[j,k]]])
print(json.dumps(summary,indent=2,sort_keys=True))
