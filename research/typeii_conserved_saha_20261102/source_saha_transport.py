#!/usr/bin/env python3
"""BASS original Type-II 401-state, source-owned Saha H equilibrium, current-conserving n_H.

No code copied to production; reads original-SHA locked Saha and TypeII functions
through their AST to bypass an unrelated optional package-wide JAX import.
The electron/baryon fluid is conditionally taken to be the source v2 fluid.
No claim of a full cosmological thermal/Einstein/recombination solution.
"""
from __future__ import annotations
import ast, csv, hashlib, json, math, pathlib, subprocess, sys, types
import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.interpolate import CubicHermiteSpline, CubicSpline
from scipy.integrate import quad

HERE=pathlib.Path(__file__).resolve().parent
ROOT=HERE.parents[1]
MAIN="9c6506e4e2087129a8b674ff10438e5db1a55c9d"
PARENT="97359596c3d640d5ad306e2285b248a5105cf40e"
REF_Z0=1700.0
OM_B_H2=0.0224
OM_M_H2=0.143
LITTLE_H=0.674
FLUID_GAMMA=1.3
SRC=[
 "bianchi/thermo/recombination.py",
 "bianchi/thermo/history_api.py",
 "bianchi/physical/units.py",
 "bianchi/q/electron.py",
 "bianchi/q/electron_rate.py",
 "compiler/validation/generate_typeii_fixture.py",
 "compiler/validation/typeii_fixture_canonical.json",
 "generated/rust/typeii/typeii_background.rs",
]
def fail(message):raise RuntimeError(message)
def check(cond,message):
    if not bool(cond):fail(message)
def git(*args):
    return subprocess.check_output(["git","-C",str(ROOT),*args],text=True).strip()
for src in SRC:
    check(git("hash-object",src)==git("rev-parse",MAIN+":"+src),
          "ORIGINAL_SOURCE_BYTE_DRIFT "+src)
original=json.loads((ROOT/"research/typeii_host_preflight_20261101/SOURCE_LOCK.json").read_text())
for path,sha in original["original_git_blobs_sha1"].items():
    check(git("hash-object",path)==sha,"ORIGINAL_NINE_SOURCE_BLOBS_DRIFT "+path)
base_csv=ROOT/"research/typeii_liouville_optdepth_20261101/PHOTON_RAYS_401X26.csv"
expected_hash="9f1400588d39ba3a61020542e14b0e372c8e9be1af130f8c64ed8829b23ad217"
check(hashlib.sha256(base_csv.read_bytes()).hexdigest()==expected_hash,"PARENT_RAY_BYTE_DRIFT")

# Compile exact source FUNCTION AST nodes, excluding package imports that transit JAX.
# This executes the source mathematical bodies without replacing them with surrogates.
def literal(path,name):
    parsed=ast.parse((ROOT/path).read_text())
    nodes=[node for node in parsed.body
       if isinstance(node,ast.Assign) and len(node.targets)==1
       and isinstance(node.targets[0],ast.Name) and node.targets[0].id==name]
    check(len(nodes)==1,"SOURCE_LITERAL_NOT_UNIQUE_"+name)
    return ast.literal_eval(nodes[0].value)
rec_path="bianchi/thermo/recombination.py"
units_path="bianchi/physical/units.py"
history_path="bianchi/thermo/history_api.py"
U=types.SimpleNamespace(
    KB_EV_K=literal(units_path,"KB_EV_K"),
    T_CMB_K=literal(units_path,"T_CMB_K"),
    MPC_KM=literal(units_path,"MPC_KM"),
)
src_saha=ast.parse((ROOT/rec_path).read_text())
saha_nodes=[node for node in src_saha.body
            if isinstance(node,ast.FunctionDef)
            and node.name in ("_saha_xe","saha_xe")]
check(len(saha_nodes)==2,"ORIGINAL_SAHA_FUNCTION_AST_NOT_FOUND")
saha_ns={"np":np,"U":U,
        "_EION_H":literal(rec_path,"_EION_H"),
        "_NB0_PER_OBH2":literal(rec_path,"_NB0_PER_OBH2")}
exec(compile(ast.Module(body=saha_nodes,type_ignores=[]),
             str(ROOT/rec_path),"exec"),saha_ns)
source_saha=saha_ns["_saha_xe"]
source_saha_flrw=saha_ns["saha_xe"]
source_n_H=ast.parse((ROOT/history_path).read_text())
nHfun=[node for node in source_n_H.body
       if isinstance(node,ast.FunctionDef) and node.name=="n_H_cm3"]
check(len(nHfun)==1,"SOURCE_NH_FUNCTION_NOT_FOUND")
nh_ns={"np":np,"REC":types.SimpleNamespace(_NB0_PER_OBH2=saha_ns["_NB0_PER_OBH2"])}
exec(compile(ast.Module(body=nHfun,type_ignores=[]),
             str(ROOT/history_path),"exec"),nh_ns)
nH_cm3_owner=nh_ns["n_H_cm3"]
SIGMA_T_CM2=literal(history_path,"SIGMA_T_CM2")
C_CM_S=literal(history_path,"C_CM_S")
OMEGA_R_H2=literal(rec_path,"_OMEGA_R_H2")

# Source 5-state gamma-law equation, no re-lowered source or dynamic import graph.
source_tree=ast.parse((ROOT/"compiler/validation/generate_typeii_fixture.py").read_text())
rhs_ast=[node for node in source_tree.body
       if isinstance(node,ast.FunctionDef) and node.name=="typeii_rhs"]
check(len(rhs_ast)==1,"ORIGINAL_TYPEII_RHS_MISSING")
rhs_ns={"math":math}
exec(compile(ast.Module(body=rhs_ast,type_ignores=[]),
             "compiler/validation/generate_typeii_fixture.py","exec"),rhs_ns)
rhs_owner=rhs_ns["typeii_rhs"]
fixture=json.loads((ROOT/"compiler/validation/typeii_fixture_canonical.json").read_text())
samples=fixture["trajectory"]["samples"]
times=np.asarray([a["tau"] for a in samples],dtype=float)
states=np.asarray([a["state"] for a in samples],dtype=float)
rhs=np.asarray([a["rhs"] for a in samples],dtype=float)
check(len(samples)==401 and states.shape==(401,5),"TYPEII_SOURCE_401_BAD_SHAPE")
check(fixture["trajectory"]["contract"]["gamma"]==FLUID_GAMMA,"TYPEII_GAMMA_DRIFT")
check(np.all(abs(np.diff(times)-0.0005)<1e-13),"TYPEII_TIME_GRID_DRIFT")
check(np.all(states[:,3]>0) and np.all(abs(states[:,4])<1),"TYPEII_SOURCE_CHART_INVALID")
rhs_actual=np.array([rhs_owner(list(x),FLUID_GAMMA) for x in states])
rhs_gap=float(np.max(abs(rhs_actual-rhs)))
check(rhs_gap<3e-14,"TYPEII_SOURCE_RHS_MISMATCH")
interp=CubicHermiteSpline(times,states,rhs,axis=0)
sqrt3=math.sqrt(3.)
def q_from_state(vfive):
    sp,sm,s13,n1,v2=map(float,vfive)
    source_value=rhs_owner(list(vfive),FLUID_GAMMA)[3]
    return source_value/n1+4*sp
q_source=np.array([q_from_state(x) for x in states])
def q_independent(vfive):
    sp,sm,s13,n1,v=map(float,vfive)
    s2=sp*sp+sm*sm+s13*s13
    omega=1.0-s2-n1*n1/12.0
    gp=1+(FLUID_GAMMA-1)*v*v
    return 2*s2+0.5*((3*FLUID_GAMMA-2)+(2-FLUID_GAMMA)*v*v)*omega/gp
q_gap=float(max(abs(q_from_state(x)-q_independent(x)) for x in states))
check(q_gap<4e-14,"DECELELATION_SOURCE_MISMATCH")
q_spline=CubicSpline(times,q_source)
q_antiderivative=q_spline.antiderivative()
def q_integral(t):
    return q_antiderivative(t)-q_antiderivative(times[0])
# Test spline-reconstructed q against freshly evaluated full Type-II original RHS.
test_points=np.linspace(0,.2,201)
q_interp_error=float(max(abs(float(q_spline(z))-q_from_state(interp(z))) for z in test_points))
check(q_interp_error<1e-9,"DECELERATION_INTERPOLANT_DRIFT")

# Physical reference anchor: high-z FLRW H0, baryon density, Tcmb from locked BASS.
# After tau=0 this is NOT the FLRW background: actual source q(tau) determines H.
omega_m=OM_M_H2/LITTLE_H**2
omega_r=OMEGA_R_H2/LITTLE_H**2
omega_lambda=1.0-omega_m-omega_r
H_ref=(100*LITTLE_H/U.MPC_KM)*math.sqrt(
    omega_r*(1+REF_Z0)**4+omega_m*(1+REF_Z0)**3+omega_lambda)
nH_rest0_cm3=float(nH_cm3_owner(REF_Z0,OM_B_H2))
v0=float(states[0,4])
gamma0=1.0/math.sqrt(1-v0*v0)
J_H0=nH_rest0_cm3*gamma0
def evaluate_physical(t):
    t=np.asarray(t,dtype=float)
    check(np.all(np.isfinite(t)),"NONFINITE_PHYSICAL_TIME")
    check(np.all((t>=times[0])&(t<=times[-1])),"OUTSIDE_SOURCE_TIME_SUPPORT")
    xx=interp(t)
    v=xx[...,4]
    check(np.all(np.isfinite(v)&(abs(v)<1.0)),"SUPERLUMINAL_BACKGROUND")
    gamma=1/np.sqrt(1-v*v)
    zmean=(1+REF_Z0)*np.exp(-t)-1
    Temp=U.T_CMB_K*(1+zmean)
    nH_normal=J_H0*np.exp(-3*t)
    nH_rest=nH_normal/gamma
    # Source-owned actual hydrogen Saha quadratic in eV and proper cm^-3.
    xe=source_saha(U.KB_EV_K*Temp,nH_rest)
    check(np.all(np.isfinite(xe)) and np.all(xe>=0) and np.all(xe<=1),"SAHA_EQUILIBRIUM_UNPHYSICAL")
    logH=math.log(H_ref)-t-q_integral(t)
    H=np.exp(logH)
    n_e_rest=xe*nH_rest
    nu_rest=SIGMA_T_CM2*C_CM_S*n_e_rest/H
    # gamma cancellation holds in every positive source-conditioned state.
    nu_normal=nu_rest*gamma
    direct=SIGMA_T_CM2*C_CM_S*xe*J_H0*np.exp(-3*t)/H
    check(np.max(abs(nu_normal-direct))<1e-8,"GAMMA_DENSITY_CANCELLATION_FAIL")
    return {"tau":t,"v":v,"gamma":gamma,"zmean":zmean,"Temp":Temp,
            "nH_normal":nH_normal,"nH_rest":nH_rest,
            "xe":xe,"ne_rest":n_e_rest,"H":H,
            "nu_rest":nu_rest,"nu_normal":nu_normal}
phys=evaluate_physical(times)
check(np.min(phys["zmean"])>1300,"HYDROGEN_SAHA_OUTSIDE_DECLARED_HIGHZ")
check(np.all(phys["H"]>0) and np.all(phys["nH_rest"]>0),"PHYSICAL_SCALE_INVALID")
continuity_resid=float(np.max(abs(phys["nH_rest"]*phys["gamma"]*
    np.exp(3*times)/J_H0-1)))
check(continuity_resid<5e-15,"NUMBER_CURRENT_CONSERVATION_INVALID")
saha_flrw0=float(source_saha_flrw(REF_Z0,OM_B_H2,U.T_CMB_K))
check(abs(saha_flrw0-float(phys["xe"][0]))<2e-13,"SAHA_INITIAL_FRAME_MISMATCH")
def saha_stable(T,n):
    S=2.4147e15*T**1.5*np.exp(-saha_ns["_EION_H"]/(U.KB_EV_K*T))
    r=S/n
    return 2*r/(r+np.sqrt(r*r+4*r))
source_vs_stable=float(np.max(abs(phys["xe"]-saha_stable(phys["Temp"],phys["nH_rest"]))))
check(source_vs_stable<3e-12,"ORIGINAL_SOURCE_SAHA_STABLE_ROOT_MISMATCH")

# Read true previously integrated normal tetrad photon directions; interpolate n_y
# with their original Liouville ODE derivative. No original CSV is modified.
rays=np.empty((26,401,3),float)
seen=np.zeros((26,401),bool)
with base_csv.open(newline="") as f:
    for row in csv.DictReader(f):
        j=int(row["ray_id"])
        t=float(row["tau_H"])
        k=int(round(t/0.0005))
        check(0<=j<26 and 0<=k<401 and abs(times[k]-t)<1e-13,"RAY_INDEX_OR_TAU_DRIFT")
        check(not seen[j,k],"DUPLICATE_SOURCE_RAY")
        rays[j,k]=[float(row["n_x"]),float(row["n_y"]),float(row["n_z"])]
        seen[j,k]=True
check(np.all(seen),"MISSING_SOURCE_RAY")
ray_norm_err=float(np.max(abs(np.linalg.norm(rays,axis=2)-1)))
check(ray_norm_err<4e-13,"ORIGINAL_RAY_UNIT_NORM_BROKEN")
n_x,n_y,n_z=(rays[:,:,i] for i in range(3))
sp,sm,s13,n1,v2=(states[:,i][None,:] for i in range(5))
shear_nn=-2*sp*n_x**2+(sp+sqrt3*sm)*n_y**2+(sp-sqrt3*sm)*n_z**2+2*sqrt3*s13*n_x*n_z
shear_yy=sp+sqrt3*sm
nydot=(shear_nn-shear_yy)*n_y-n1*n_x*n_z
direction_interp=CubicHermiteSpline(times,n_y,nydot,axis=1)
check(np.max(abs(direction_interp(times)-n_y))<1e-14,"RAY_INTERPOLANT_KNOT_MISMATCH")
# Source analytic axial pair is invariant even with nonzero N1 and Sigma13.
axis_p=next(j for j in range(26) if max(abs(rays[j,0]-np.array([0.,1.,0.])))<1e-14)
axis_m=next(j for j in range(26) if max(abs(rays[j,0]-np.array([0.,-1.,0.])))<1e-14)
check(np.max(abs(nydot[[axis_p,axis_m],:]))<1e-14,"AXIAL_SOURCE_NOT_INVARIANT")

# Source-conditioned physical optical depth along 26 existing geodesic directions.
glx,glw=leggauss(8)
glx16,glw16=leggauss(16)
def compute_depth(order=8):
    gx,gw=(glx,glw) if order==8 else (glx16,glw16)
    answer=np.zeros((26,len(times)))
    odd=np.zeros(len(times));even=np.zeros(len(times))
    for k,(lo,hi) in enumerate(zip(times[:-1],times[1:])):
        xpts=lo+0.5*(hi-lo)*(gx+1)
        p=evaluate_physical(xpts)
        W=p["nu_normal"]
        ny=direction_interp(xpts)
        check(np.all((ny>=-1.00000001)&(ny<=1.00000001)),
              "NORMAL_DIRECTION_OVERSHOOT")
        values=(1.0-p["v"][None,:]*ny)*W[None,:]
        check(np.all(values>=0),"NEGATIVE_THOMSON_SOURCE")
        width=(hi-lo)*0.5
        answer[:,k+1]=answer[:,k]+width*(values@gw)
        even[k+1]=even[k]+width*float(np.dot(gw,W))
        odd[k+1]=odd[k]+width*float(np.dot(gw,W*p["v"]))
    return answer,even,odd
depth,even,odd=compute_depth(8)
depth16,even16,odd16=compute_depth(16)
depth_order_gap=float(np.max(abs(depth-depth16)))
check(depth_order_gap<3e-9,"THOMSON_DEPTH_GAUSS_CONVERGENCE_FAIL")
check(np.all(np.diff(depth,axis=1)>=0),"THOMSON_DEPTH_NOT_MONOTONE")
check(np.max(abs(depth[axis_p]-(even-odd)))<1e-11,"PLUS_AXIAL_THOMSON_IDENTITY_FAIL")
check(np.max(abs(depth[axis_m]-(even+odd)))<1e-11,"MINUS_AXIAL_THOMSON_IDENTITY_FAIL")
asym=(depth[axis_m,-1]-depth[axis_p,-1])/(depth[axis_m,-1]+depth[axis_p,-1])
weighted=odd[-1]/even[-1]
check(abs(asym-weighted)<2e-13,"WEIGHTED_TILT_IDENTITY_FAIL")

# Independent adaptive-quadrature endpoint on exact source-conditional functions.
def density_weight(z):
    p=evaluate_physical(z)
    return float(p["nu_normal"])
def exact_axis(sign):
    return quad(lambda z:density_weight(z)*(1.0-sign*float(interp(z)[4])),
                float(times[0]),float(times[-1]),
                epsabs=1e-11,epsrel=1e-12,limit=300)[0]
quad_p,quad_m=exact_axis(+1),exact_axis(-1)
quad_gap=max(abs(quad_p-depth[axis_p,-1]),abs(quad_m-depth[axis_m,-1]))
check(quad_gap<3e-8,"AXIS_ADAPTIVE_QUADRATURE_DISAGREEMENT")

# Explicit bad-physics numerical counterexamples on the unchanged source background.
wrong_no_gamma=SIGMA_T_CM2*C_CM_S*phys["xe"]*phys["nH_normal"]/(
    phys["H"]*phys["gamma"])
true_normal=SIGMA_T_CM2*C_CM_S*phys["xe"]*phys["nH_normal"]/phys["H"]
wrong_frame_max_rel=float(np.max(abs(wrong_no_gamma/true_normal-1)))
check(wrong_frame_max_rel>1e-4,"WRONG_DENSITY_FRAME_NEGATIVE_NOT_FOUND")
flrw_ne_reference=np.asarray(source_saha_flrw(phys["zmean"],OM_B_H2,U.T_CMB_K)) * nH_rest0_cm3*np.exp(-3*times)
naive_recomb_fraction_gap=float(np.max(abs(np.asarray(
    source_saha_flrw(phys["zmean"],OM_B_H2,U.T_CMB_K))-phys["xe"])))
naive_ne_relative=float(np.max(abs(flrw_ne_reference/phys["ne_rest"]-1)))
check(naive_ne_relative>1e-5,"NAIVE_FLRW_PROPER_DENSITY_NEGATIVE_NOT_FOUND")
# Model dependence: doubling only H_ref scales every optical depth by 1/2,
# while the odd/even optical depth asymmetry ratio is unchanged.
check(abs((odd[-1]/2)/(even[-1]/2)-weighted)<1e-15,"H_ANCHOR_RATE_SCALING_BROKEN")

# Original owner electron frame source (independent SR boost) at the original
# 401x26 ray knots, not re-computing the photon Liouville evolution.
sys.path.insert(0,str(ROOT))
from bianchi.q.electron import transform_photon
max_doppler_error=0.
for k in (0,100,200,300,400):
    v=float(states[k,4])
    _,_,D=transform_photon(1.0,rays[:,k,:],np.zeros(3),np.array([0.,v,0.]))
    expected=(1.0-v*rays[:,k,1])/math.sqrt(1.0-v*v)
    max_doppler_error=max(max_doppler_error,float(max(abs(D-expected))))
check(max_doppler_error<2e-15,"ORIGINAL_ELECTRON_DOPPLER_REJECTION")

# Physical output data, explicitly distinguish z_mean from observed redshift.
with (HERE/"HYDROGEN_SAHA_HISTORY_401.csv").open("w",newline="") as f:
    writer=csv.writer(f,lineterminator="\n")
    writer.writerow(["tau_H","z_mean_not_observed","T_m_K_assumed",
       "v2","Gamma_e","q_deceleration","H_s_inv",
       "n_H_normal_cm_minus3","n_H_rest_cm_minus3","x_e_H_only_source_Saha",
       "n_e_rest_cm_minus3","nu_rest_per_Hubble_tau",
       "nu_source_prefactor_Gamma_nu_rest",
       "int_W_d_tau","int_W_v_d_tau"])
    for k,t in enumerate(times):
        writer.writerow([format(float(z),".17g") for z in [
            t,phys["zmean"][k],phys["Temp"][k],states[k,4],
            phys["gamma"][k],q_source[k],phys["H"][k],
            phys["nH_normal"][k],phys["nH_rest"][k],phys["xe"][k],
            phys["ne_rest"][k],phys["nu_rest"][k],phys["nu_normal"][k],
            even[k],odd[k]]])
with (HERE/"SAHA_THOMSON_RAYS_401X26.csv").open("w",newline="") as f:
    writer=csv.writer(f,lineterminator="\n")
    writer.writerow(["ray_id","tau_H","n_y_normal","q_one_minus_v_ny",
                     "d_optical_depth_per_tau_H","integrated_thomson_depth"])
    for j in range(26):
        for k,t in enumerate(times):
            q=1.0-states[k,4]*n_y[j,k]
            wrate=float(phys["nu_normal"][k]*q)
            writer.writerow([j]+[format(float(z),".17g") for z in [
                t,n_y[j,k],q,wrate,depth[j,k]]])

summary={
 "schema":"bass.typeii.conserved_hydrogen_source_saha_highz_401x26.v1",
 "parent_head":PARENT, "original_main":MAIN,
 "source_orig_9_byte_exact":9,"extra_source_gits_locked":SRC,
 "background_rows":401,"source_rays":26,"source_ray_records":401*26,
 "parent_csv_sha256":expected_hash,
 "model":"original gamma=1.3 Type-II five-state, class-A conserved H-current, hydrogen-only Saha thermal reservoir, conditional high-z H anchor",
 "z_anchor_mean":REF_Z0,"z_mean_final":float(phys["zmean"][-1]),
 "Omega_b_h2_anchor":OM_B_H2,"Omega_m_h2_anchor":OM_M_H2,"h_anchor":LITTLE_H,
 "T0_K_source":U.T_CMB_K,"sigma_T_cm2_source":SIGMA_T_CM2,"c_cm_s_source":C_CM_S,
 "H_anchor_s_inv_fiducial_LCDM_only":H_ref,
 "H_endpoint_s_inv_typeii_source":float(phys["H"][-1]),
 "n_H_rest_anchor_cm_minus3":nH_rest0_cm3,
 "Gamma_anchor":gamma0,"normal_hydrogen_current_anchor_cm_minus3":J_H0,
 "n_H_rest_endpoint_cm_minus3":float(phys["nH_rest"][-1]),
 "n_e_rest_initial_cm_minus3":float(phys["ne_rest"][0]),
 "n_e_rest_final_cm_minus3":float(phys["ne_rest"][-1]),
 "x_e_initial_hydrogen_Saha":float(phys["xe"][0]),
 "x_e_final_hydrogen_Saha":float(phys["xe"][-1]),
 "nu_rest_initial_per_tau_H":float(phys["nu_rest"][0]),
 "nu_rest_final_per_tau_H":float(phys["nu_rest"][-1]),
 "source_typeii_rhs_max_abs_gap":rhs_gap,
 "q_source_independent_formula_max_abs_gap":q_gap,
 "q_cubic_interpolation_max_abs_gap":q_interp_error,
 "hydrogen_normal_current_conservation_max_relative_defect":continuity_resid,
 "saha_ast_source_vs_stable_root_max_abs_gap":source_vs_stable,
 "electron_owner_D_max_abs_gap_at_5_snapshots":max_doppler_error,
 "source_saha_vs_naive_FLRW_ionization_fraction_max_gap":naive_recomb_fraction_gap,
 "source_proper_electron_density_vs_naive_FLRW_max_relative_gap":naive_ne_relative,
 "source_normal_collision_prefactor_vs_wrong_missing_Gamma_max_relative_gap":wrong_frame_max_rel,
 "Thomson_depth_min_26_rays":float(np.min(depth[:,-1])),
 "Thomson_depth_max_26_rays":float(np.max(depth[:,-1])),
 "positive_ey_ray_id":axis_p,"negative_ey_ray_id":axis_m,
 "Thomson_depth_plus_ey":float(depth[axis_p,-1]),
 "Thomson_depth_minus_ey":float(depth[axis_m,-1]),
 "Thomson_depth_odd_part":float(odd[-1]),
 "Thomson_depth_even_part":float(even[-1]),
 "Thomson_depth_difference":float(depth[axis_m,-1]-depth[axis_p,-1]),
 "Thomson_depth_asymmetry":float(asym),
 "opacity_weighted_tilt":float(weighted),
 "Thomson_depth_8_vs_16_gl_max_abs_gap":depth_order_gap,
 "Thomson_depth_independent_quad_axial_max_abs_gap":quad_gap,
 "H_anchor_2x_depth_scaling":0.5,
 "previous_unit_opacity_asymmetry":0.048349926581410956,
 "status":"SOURCE_OWNED_PHYSICAL_HIGH_Z_HYDROGEN_SAHA_SCENARIO_NUMERICALLY_CHECKED_NOT_PRODUCTION",
 "validity_limitations":[
    "hydrogen Saha high-z equilibrium only, no helium or high precision HyRec",
    "mean-scale-factor thermal label and imposed isotropic matter reservoir; observed directional redshift differs",
    "FLRW H(0) and proper density anchors not self-consistent full Bianchi Einstein matter constraint",
    "baryon current conserved and electrons comoving tilted hydrogen by model assumption",
    "no full angular Thomson gain/loss or polarized radiation, no matter-photon backreaction"
 ],
}
(HERE/"PHYSICAL_SAHA_THOMSON_SUMMARY.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
print(json.dumps(summary,indent=2,sort_keys=True))
