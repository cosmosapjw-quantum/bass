#!/usr/bin/env python3
"""Original source TypeII 26 photon rays with newly native HYREC2 atom H and proper nH.

Input photon directions are original BASS Liouville geodesics, not invented
angular labels. Four kinetic histories are compared at the SAME original BASS
TypeII geometric H, same tilted conserved normal hydrogen current and same
photon directions. Conditional finite observer zmean=300, not observed CMB.
"""
import ast,csv,hashlib,json,math,subprocess
from pathlib import Path
import numpy as np
from scipy.interpolate import PchipInterpolator,CubicHermiteSpline
from scipy.integrate import solve_ivp
from numpy.polynomial.legendre import leggauss
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PR330="9f10e1145c8582f71f7d81dcebfd3c125c70c04c"
ORIGINAL="9c6506e4e2087129a8b674ff10438e5db1a55c9d"
parent=ROOT/"research/typeii_hyrec2_history_20261102"
def check(ok,reason):
    if not bool(ok):raise RuntimeError(reason)
def git(*a):
    return subprocess.check_output(["git","-C",str(ROOT),*a],text=True).strip()
def sha(x):return hashlib.sha256(Path(x).read_bytes()).hexdigest()
paths=["research/typeii_hyrec2_history_20261102/EXTENDED_TYPEII_HYREC2_RAY_26.csv",
       "compiler/validation/typeii_fixture_canonical.json",
       "compiler/validation/generate_typeii_fixture.py"]
for path in paths:
    check(git("hash-object",path)==git("rev-parse",PR330+":"+path),
          "PARENT_BASS_SOURCE_IDENTITY_MISMATCH "+path)
reports=json.loads((HERE/"R4_NATIVE_TYPEII_H_AND_PROPER_NH_RESULTS.json").read_text())
histories={
 "FLRW_atomic":parent/"HYREC2_FLRW_XE_TM_8000.dat",
 "TypeII_H_only":HERE/"NATIVE_TYPEII_HUBBLE_HHE_ATOMIC_XE_TM_8000.dat",
 "FLRW_H_TypeII_proper_nH":HERE/"NATIVE_FLRW_H_AND_TYPEII_PROPER_NH_XE_TM_8000.dat",
 "TypeII_H_and_proper_nH":HERE/"NATIVE_TYPEII_H_AND_PROPER_NH_XE_TM_8000.dat"
}
target="TypeII_H_and_proper_nH"
check(sha(histories[target])==reports["published_combined_sha256"],
      "NATIVE_KINETIC_HPLUSNH_OUTPUT_DRIFT")
curves={}
for key,file in histories.items():
    raw=np.loadtxt(file)
    check(raw.shape==(8000,3) and np.all(np.isfinite(raw)) and np.min(raw[:,1:])>0,
          "INVALID_NATIVE_HYREC2_XE_T_HISTORY_"+key)
    curves[key]=PchipInterpolator(np.log1p(raw[::-1,0]),raw[::-1,1],
                        extrapolate=False)
# Full 1167 x 26 actual source geodesics from PR330, read only.
original_rays=parent/"EXTENDED_TYPEII_HYREC2_RAY_26.csv"
with original_rays.open(newline="") as f:rawrows=list(csv.DictReader(f))
nrecords=len(rawrows)
check(nrecords%26==0 and nrecords>30000,"ORIGINAL_EXTENDED_RAY_RECORDS_MISSING")
N=nrecords//26
times=np.array([float(rawrows[k]["tau_H"]) for k in range(N)])
check(N==1167 and np.all(np.diff(times)>0),"ORIGINAL_SOURCE_EXTENDED_TIMES_MISMATCH")
ray_x=np.zeros((26,N,3))
H_parent=np.zeros(N)
zmean=np.zeros(N)
for j in range(26):
    for k in range(N):
        row=rawrows[j*N+k]
        check(int(row["ray"])==j and abs(float(row["tau_H"])-times[k])<2e-14,
              "ORIGINAL_SOURCE_RAY_IDENTITY_BROKEN")
        ray_x[j,k]=[float(row["n_x"]),float(row["n_y"]),float(row["n_z"])]
        if j==0:
            H_parent[k]=float(row["H_s_inv"])
            zmean[k]=float(row["z_mean_not_observed"])
check(max(abs(zmean-(1701*np.exp(-times)-1)))<4e-11,"MEAN_TAUH_TO_Z_NOT_REPRODUCED")
# Source original gamma-law RHS exact body, not duplicated approximate equations.
sourcepath=ROOT/"compiler/validation/generate_typeii_fixture.py"
module=ast.parse(sourcepath.read_text())
functions=[x for x in module.body if isinstance(x,ast.FunctionDef) and x.name=="typeii_rhs"]
check(len(functions)==1,"ORIGINAL_TYPEII_SOURCE_RHS_NOT_FOUND")
ns={"math":math}
exec(compile(ast.Module(body=functions,type_ignores=[]),str(sourcepath),"exec"),ns)
rhs=ns["typeii_rhs"]
fixture=json.loads((ROOT/"compiler/validation/typeii_fixture_canonical.json").read_text())
x0=np.array(fixture["trajectory"]["samples"][0]["state"],float)
bg=solve_ivp(lambda t,x:rhs(list(x),1.3),
             (0,float(times[-1])),x0,method="DOP853",dense_output=True,
             rtol=2e-12,atol=1e-13,max_step=.004)
check(bg.success,"ORIGINAL_BASS_TYPEII_BACKGROUND_INTEGRATOR_FAILED")
st=bg.sol(times).T
# Independent source state validation at original 401 knots.
tf=np.array([r["tau"] for r in fixture["trajectory"]["samples"]])
xf=np.array([r["state"] for r in fixture["trajectory"]["samples"]])
source_overlap=float(np.max(abs(bg.sol(tf).T-xf)))
check(source_overlap<1e-11,"BASS_SOURCE_ORIGINAL_401_GRAVITY_DRIFT")
v=st[:,4];gam=1/np.sqrt(1-v*v);gamma0=float(gam[0])
sp,sm,s13,n1=(st[:,i][None,:] for i in (0,1,2,3))
nx,ny,nz=(ray_x[:,:,i] for i in range(3))
shear_nn=(-2*sp*nx*nx+(sp+math.sqrt(3)*sm)*ny*ny+
          (sp-math.sqrt(3)*sm)*nz*nz+2*math.sqrt(3)*s13*nx*nz)
dny=(shear_nn-(sp+math.sqrt(3)*sm))*ny-n1*nx*nz
NY=CubicHermiteSpline(times,ny,dny,axis=1)
# Native HYREC-2 exact H(z1700) anchor; source BASS H path is parent H
# with only the physical boundary-normalization correction.
hsource=json.loads((HERE/"R3_TYPEII_HUBBLE_GRID.json").read_text())
Hanch=float(hsource["H_anchor_source_FLRW_s_inverse"])
Hold=float(H_parent[0])
Hcorrect=H_parent*(Hanch/Hold)
logHs=PchipInterpolator(times,np.log(Hcorrect))
# The original source q/H ODE generated 2248-grid H(z); source continuity
# is cross-checked with the rescaled ray-owner H at internal discrete points.
source_grid=np.loadtxt(HERE/"TYPEII_H_COMPARE_FLRW_GRID.csv",delimiter=",",skiprows=1)
loc=PchipInterpolator(np.log1p(source_grid[:,0]),np.log(source_grid[:,2]))
support=np.linspace(0.1,float(times[-1]),250)
Hdiff=float(np.max(abs(np.exp(loc(np.log1p(1701*np.exp(-support)-1)))/
         np.exp(logHs(support))-1)))
check(Hdiff<5e-5,"SOURCE_HUBBLE_OWNER_AND_NATIVE_EXTERNAL_GRID_INCONSISTENT")
# Hydrogen class A conserved NORMAL current, with original HYREC YHe
# reference normalization. Same nH/hubble source for all four atomic models.
native_model=json.loads((parent/"HYREC2_NATIVE_SOURCE_REPORT.json").read_text())
obh2=native_model["input_cosmology"]["Omega_b_h2"]
YHe=native_model["input_cosmology"]["YHe"]
nH0=11.223846333047e-6*obh2*(1-YHe) # cgs cm^-3
N_H0=nH0*1701**3*gamma0
sigma_cgs=6.6524587e-25
c_cgs=29979245800.
axis_plus=next(j for j in range(26) if max(abs(ray_x[j,0]-[0,1,0]))<1e-14)
axis_minus=next(j for j in range(26) if max(abs(ray_x[j,0]-[0,-1,0]))<1e-14)
def phys(t):
    t=np.asarray(t,float)
    check(np.isfinite(t).all() and np.min(t)>=0 and np.max(t)<=times[-1],
          "OPACITY_TIME_OUTSIDE_SOURCE_BASS_DOMAIN")
    z=1701*np.exp(-t)-1
    vt=bg.sol(t)[4]
    G=1/np.sqrt(1-vt*vt)
    W=sigma_cgs*c_cgs*N_H0*np.exp(-3*t)/np.exp(logHs(t))
    nHrest=N_H0*np.exp(-3*t)/G
    return z,vt,G,W,nHrest
def integrate(order):
    xi,wi=leggauss(order)
    vals={name:np.zeros((26,N),float) for name in curves}
    odd=np.zeros(N);even=np.zeros(N)
    for k,(lo,hi) in enumerate(zip(times[:-1],times[1:])):
        t=lo+.5*(hi-lo)*(xi+1)
        z,vt,G,W,nH=phys(t)
        dirs=NY(t)
        q=1-vt[None,:]*dirs
        check(np.min(q)>0,"THOMSON_RELATIVE_FLUX_NONPOSITIVE")
        for name,xe in curves.items():
            xeval=xe(np.log1p(z))
            check(np.isfinite(xeval).all() and np.min(xeval)>0,"XE_NOT_IN_HYREC_DOMAIN")
            step=(W*xeval)[None,:]*q
            vals[name][:,k+1]=vals[name][:,k]+.5*(hi-lo)*(step@wi)
        refx=curves[target](np.log1p(z))
        even[k+1]=even[k]+.5*(hi-lo)*np.dot(wi,W*refx)
        odd[k+1]=odd[k]+.5*(hi-lo)*np.dot(wi,W*refx*vt)
    return vals,even,odd
depth,even,odd=integrate(8)
depth16,_,_=integrate(16)
quadgap=max(float(np.max(abs(depth[n]-depth16[n]))) for n in curves)
check(quadgap<5e-7,"KINETIC_OPACITY_8_16_GAUSS_CONVERGENCE_FAIL")
for name in curves:
    check(np.min(np.diff(depth[name],axis=1))>=0,"NEGATIVE_THOMSON_OPACITY_"+name)
result=depth[target]
axisgap=float(max(np.max(abs(result[axis_plus]-(even-odd))),
                  np.max(abs(result[axis_minus]-(even+odd)))))
check(axisgap<5e-10,"BASS_TYPEII_AXIAL_OPACITY_IDENTITY_FAIL")
# Actual BASS ColdElectronTestField source parity on 5*26 representative points.
import sys
sys.path.insert(0,str(ROOT))
from bianchi.q.electron import ColdElectronTestField,transform_photon
maxD=maxrate=0.
for k in [0,100,250,600,N-1]:
    z,vt,G,W,nrest=phys(times[k])
    xev=float(curves[target](np.log1p(z)))
    field=ColdElectronTestField.comoving(float(nrest*xev*1e6),
                                        (0.,float(vt),0.),c_m_s=299792458.)
    _,_,D=transform_photon(1.,ray_x[:,k,:],np.zeros(3),
                         np.array([0.,float(vt),0.]))
    want=1/np.sqrt(1-vt*vt)*(1-vt*ray_x[:,k,1])
    maxD=max(maxD,float(np.max(abs(D-want))))
    H=float(np.exp(logHs(times[k])))
    from_owner=field.n_e_free*6.6524587e-29*299792458.*D/H
    ours=float(W*xev)*(1-vt*ray_x[:,k,1])
    maxrate=max(maxrate,float(np.max(abs(from_owner/ours-1))))
check(maxD<3e-15 and maxrate<4e-15,"ORIGINAL_ELECTRON_C_SOURCE_NOT_MATCHED")
# Finite-observer zmean=300 CONDITIONAL last-event kernel per actual normal ray.
rate_nodes=np.empty_like(result)
z_node,v_node,G_node,W_node,nHrest_node=phys(times)
for j in range(26):
    rate_nodes[j]=W_node*curves[target](np.log1p(z_node))*(1-v_node*ny[j])
future=result[:,-1,None]-result
kernel=rate_nodes*np.exp(-future)
peak_indices=np.argmax(kernel,axis=1)
peak_z=zmean[peak_indices]
asym=((result[axis_minus,-1]-result[axis_plus,-1])/
      (result[axis_minus,-1]+result[axis_plus,-1]))
check(abs(asym-odd[-1]/even[-1])<3e-13,"TYPEII_BARYON_ODD_EVEN_ASYMMETRY_FAIL")
with (HERE/"TYPEII_ATOMIC_THOMSON_EXTENDED_26RAY.csv").open("w",newline="") as f:
    wr=csv.writer(f,lineterminator="\n")
    wr.writerow(["ray_id","tau_H","z_mean","n_y",
       "hazard_full_native_TypeII_H_plus_proper_nH",
       "depth_native_TypeII_H_plus_proper_nH",
       "depth_native_TypeII_H_only",
       "depth_external_FLRW_atomic",
       "future_depth_to_z300",
       "last_event_kernel_to_z300"])
    for j in range(26):
        for k,t in enumerate(times):
            wr.writerow([j]+[format(float(vv),".17g") for vv in
            [t,zmean[k],ny[j,k],rate_nodes[j,k],
            result[j,k],depth["TypeII_H_only"][j,k],
            depth["FLRW_atomic"][j,k],future[j,k],kernel[j,k]]])
def values(name):
    x=depth[name][:,-1]
    return {"plus":float(x[axis_plus]),"minus":float(x[axis_minus]),
            "range":[float(np.min(x)),float(np.max(x))],
            "asym":float((x[axis_minus]-x[axis_plus])/(x[axis_minus]+x[axis_plus]))}
summ={
 "schema":"bass.TypeII_actual_native_HyRec2_atomic_H_proper_Hn_26rays_z300.v1",
 "source_C_models_2x2":"original native atom x_e computed with FLRW or TypeII H and original or proper conserved H nucleus",
 "original_TypeII_5_state_fixture_401_overlap_max_abs":source_overlap,
 "extended_source_rays":26,
 "extended_source_times":N,
 "physical_end_mean_redshift":300.,
 "source_Hubble_normalization_1700_s_inv":Hanch,
 "TypeII_H_from_C_grid_vs_source_ray_H_max_rel_gap":Hdiff,
 "original_source_BASS_26ray_geometry_identity":git("hash-object",paths[0]),
 "HYREC_native_combined_xe_sha256":sha(histories[target]),
 "native_HyRec_C_corrected_for_hydrogen_density":True,
 "atomic_nHrest_formula":"nH0_HYREC(1+zmean)^3 Gamma(1700)/Gamma(zmean)",
 "photon_opacity_formula":"sigma_T c x_e nHnormal / H_TypeII * (1-v n_y)",
 "four_actual_native_atomic_history_lanes":{n:values(n) for n in curves},
 "physical_plus_minus_axes":[axis_plus,axis_minus],
 "full_native_atomic_HplusNH_depth_odd_even_gap":axisgap,
 "full_native_atomic_HplusNH_asymmetry":float(asym),
 "Gauss_8_vs_16_max_abs_all_lanes":quadgap,
 "original_BASS_electron_owner_D_max_abs_gap":maxD,
 "original_BASS_electron_owner_thomson_cgs_SI_max_relative_gap":maxrate,
 "conditional_z300_attenuation_kernel_peak_z_range":[float(min(peak_z)),float(max(peak_z))],
 "conditional_z300_attenuation_kernel_plus_peak_z":float(peak_z[axis_plus]),
 "conditional_z300_attenuation_kernel_minus_peak_z":float(peak_z[axis_minus]),
 "claim":"NATIVE_HYREC2_TYPEII_H_AND_CONSERVED_PROPER_NH_ATOM_KINETICS_COUPLED_TO_GENUINE_BASS_26_NORMAL_RAYS",
 "scope_limit":"source-conditioned TypeII gamma-law background, non-FLRW CMB line radiation not included, no re-solved metric baryon backreaction, not observed z0 CMB"
}
(HERE/"R5_SOURCE_ATOMIC_TYPEII_PHOTON_RESULTS.json").write_text(json.dumps(summ,indent=2,sort_keys=True)+"\n")
print(json.dumps(summ,indent=2,sort_keys=True))
