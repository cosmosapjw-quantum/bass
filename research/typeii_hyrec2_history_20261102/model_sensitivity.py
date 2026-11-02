#!/usr/bin/env python3
"""Matched density and temperature comparison: HYREC2 FLRW H/He versus BASS source-Saha on fixed TypeII rays.

One exact normal-current and Hubble source for every scenario. This isolates
ionization kinetics from the YHe convention and prevents conflating the
previous Saha n_H0 normalization with the actual native HYREC2 n_H0.
"""
from pathlib import Path
import ast,contextlib,io,json,runpy,types,math
import numpy as np
from scipy.interpolate import PchipInterpolator
from numpy.polynomial.legendre import leggauss

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
with contextlib.redirect_stdout(io.StringIO()):
    m=runpy.run_path(str(HERE/"typeii_hyrec2_transport.py"))
def check(cond,msg):
    if not bool(cond):raise RuntimeError(msg)
basepath="bianchi/thermo/recombination.py"
upath="bianchi/physical/units.py"
astsrc=ast.parse((ROOT/basepath).read_text())
source_saha=[x for x in astsrc.body if isinstance(x,ast.FunctionDef) and x.name=="_saha_xe"]
check(len(source_saha)==1,"ORIGINAL_SOURCE_SAHA_MISSING")
sourcenames=["_EION_H","_NB0_PER_OBH2"]
constants={}
for name in sourcenames:
    found=[n for n in astsrc.body if isinstance(n,ast.Assign)
            and len(n.targets)==1 and isinstance(n.targets[0],ast.Name)
            and n.targets[0].id==name]
    check(len(found)==1,"ORIGINAL_CONSTANT_MISSING_"+name)
    constants[name]=ast.literal_eval(found[0].value)
utree=ast.parse((ROOT/upath).read_text())
for name in ("KB_EV_K","T_CMB_K"):
    found=[n for n in utree.body if isinstance(n,ast.Assign)
           and len(n.targets)==1 and isinstance(n.targets[0],ast.Name)
           and n.targets[0].id==name]
    check(len(found)==1,"UNIT_CONSTANT_NOT_FOUND_"+name)
    constants[name]=ast.literal_eval(found[0].value)
ns={"np":np,"U":types.SimpleNamespace(KB_EV_K=constants["KB_EV_K"]),
    "_EION_H":constants["_EION_H"]}
exec(compile(ast.Module(body=source_saha,type_ignores=[]),str(ROOT/basepath),"exec"),ns)
source_saha_f=ns["_saha_xe"]
times=m["times"];nt=len(times);N=26
W0=m["N_H0"];gamma0=m["gamma_init"];zinit=m["z0"]
pchip_h=m["pchip"];hubble=m["H_spline"]
V=m["V"];normaldirs=m["NY"];sigma=m["sigma_cm2"];c=m["c_cgs"]
nativeTm=m["tmchip"]
def scenario(t,which):
    v=V(t)
    z=(1+zinit)*np.exp(-t)-1
    temp_cmb=2.7255*(1+z)
    temp_native=nativeTm(np.log1p(z))
    g=1/np.sqrt(1-v*v)
    nH_normal=W0*np.exp(-3*t)
    nH_rest=nH_normal/g
    if which=="original_HYREC2":xe=pchip_h(np.log1p(z))
    elif which=="Saha_HyRec_density_Tcmb":
        xe=source_saha_f(constants["KB_EV_K"]*temp_cmb,nH_rest)
    elif which=="Saha_HyRec_density_Tmatter":
        xe=source_saha_f(constants["KB_EV_K"]*temp_native,nH_rest)
    elif which=="fully_ionized_H":xe=np.ones_like(np.asarray(t))
    else: raise RuntimeError("UNKNOWN_SCENARIO")
    if not np.all(np.isfinite(xe)) or np.any(np.asarray(xe)<0):
        raise RuntimeError("NEGATIVE_SOURCE_XE")
    return sigma*c*nH_normal*xe/np.exp(hubble(t))
def integrate(which,order=8):
    xi,wi=leggauss(order)
    result=np.zeros(N)
    for aa,bb in zip(times[:-1],times[1:]):
        at=aa+0.5*(bb-aa)*(xi+1)
        normaldirs_y=normaldirs(at)
        beta=V(at)
        flux=1-beta[None,:]*normaldirs_y
        nu=scenario(at,which)
        result+=.5*(bb-aa)*((nu[None,:]*flux)@wi)
    return result
cases={k:integrate(k) for k in
       ("original_HYREC2","Saha_HyRec_density_Tcmb",
        "Saha_HyRec_density_Tmatter","fully_ionized_H")}
cases16={k:integrate(k,16) for k in cases}
maxerr=max(float(np.max(abs(cases[k]-cases16[k]))) for k in cases)
check(maxerr<5e-8,"IONIZATION_SOURCE_CONVERGENCE_FAIL")
old=m["depth"][:,-1]
hy=cases["original_HYREC2"]
check(np.max(abs(hy-old))<5e-8,"REWEIGHTED_REFERENCE_DOES_NOT_MATCH")
matched=cases["Saha_HyRec_density_Tcmb"]
matched_native_Tm=cases["Saha_HyRec_density_Tmatter"]
full=cases["fully_ionized_H"]
check(np.all(hy>matched),"HYREC_NONEQUILIBRIUM_EFFECT_SIGN_NOT_OBSERVED")
check(np.all(full>=hy),"FULLY_IONIZED_H_UPPER_BOUND_NOT_HELD_ON_DOMAIN")
p=m["axis_plus"];n=m["axis_minus"]
def asym(x):return float((x[n]-x[p])/(x[n]+x[p]))
new={
 "schema":"bass.typeii.hyrec2_vs_original_saha_matched_Hydrogen_and_typeiiH.v1",
 "physical_reference":"original HHe HYREC2 FLRW scalar history, fixed TypeII source H and n_Hnormal",
 "source_Saha_f":"original SHA-locked BASS _saha_xe AST body, executed without missing JAX imports",
 "matched_hydrogen_current":True,
 "matched_Hubble_TypeII":True,
 "matched_photon_ray_geometry":True,
 "HYREC2_minus_matched_Saha_depth_plus":float(hy[p]-matched[p]),
 "HYREC2_minus_matched_Saha_depth_minus":float(hy[n]-matched[n]),
 "HYREC2_minus_matched_Saha_depth_all_rays_min":float(np.min(hy-matched)),
 "HYREC2_minus_matched_Saha_depth_all_rays_max":float(np.max(hy-matched)),
 "Saha_Tmatter_vs_Saha_Tcmb_26ray_max_abs_gap":float(np.max(abs(matched_native_Tm-matched))),
 "fully_ionized_H_minus_HYREC2_min":float(np.min(full-hy)),
 "fully_ionized_H_minus_HYREC2_max":float(np.max(full-hy)),
 "HYREC2_axial_asymmetry":asym(hy),
 "matched_Saha_axial_asymmetry":asym(matched),
 "fully_ionized_axial_asymmetry":asym(full),
 "8_16_Gauss_max_case_gap":maxerr,
 "maximum_recomputed_reference_HYREC2_depth_gap":float(np.max(abs(hy-old))),
 "claim":"SOURCE_CONTROLLED_NON_EQUILIBRIUM_HHE_HYREC2_VS_SAHA_IONIZATION_EFFECT_NUMERICALLY_CHECKED",
 "not_claimed":"HyRec2 itself recomputed on Bianchi H or exact helium Saha model."
}
(HERE/"MODEL_SENSITIVITY_RESULTS.json").write_text(json.dumps(new,indent=2,sort_keys=True)+"\n")
print(json.dumps(new,indent=2,sort_keys=True))
