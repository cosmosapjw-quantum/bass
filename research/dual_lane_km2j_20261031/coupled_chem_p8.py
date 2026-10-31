"""KM2J: coupled Peebles x_e + grey binding energy + original Einstein-P8 photons.

Original KM2F/G/H/I source files never edited. New conditional effective model:
externally supplied temperature histories, Sobolev local line closure, and
bolometric unpolarized line/binding output with 4 exact discrete moments.
Not a spectral or thermodynamically closed cosmological recombination model.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
from numpy.polynomial.legendre import leggauss

from research.dual_lane_km2h_20261030.external_opacity_bianchi import (
    ExternalFLRWOpacityBianchi,
)
from research.dual_lane_km2i_20261031.lya_peebles import (
    source_guards, alpha_caseB, beta_caseB, sobolev_directional,
    CHI_H_EV, E_ALPHA_EV, E_CHARGE, K_B, T_CMB0, TWO_PHOTON,
)
from research.dual_lane_km2g_20261030.neutral_baryons import (
    C_M_S, SIGMA_T_M2, M_E_KG, M_P_KG,
)
from research.dual_lane_km2f_20261030.einstein_bianchi import (
    sigma_to5, sym_traceless,
)
from tilted_collision import expected_fourforce, radiation_tensor
from curved_tilt import linear_collision

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
PARENT_HEAD="8e3cf0ac1eab96142494903ed940e27d1b66e380"
PARENT_LYA_BLOB="288762c51643855fc6d5a12fc04a911062abd449"
PARENT_F_BLOB="457790df7aba6d82326ac6f3be5814851b970b1d"
YHE=.245
ENERGY_J=CHI_H_EV*E_CHARGE


def gitblob(path):
    raw=Path(path).read_bytes()
    return hashlib.sha1(f"blob {len(raw)}\0".encode()+raw).hexdigest()


def guard_all():
    sources=source_guards()
    checks={
      "research/dual_lane_km2i_20261031/lya_peebles.py":PARENT_LYA_BLOB,
      "research/dual_lane_km2f_20261030/einstein_bianchi.py":PARENT_F_BLOB,
    }
    for rel, expected in checks.items():
        found=gitblob(ROOT/rel)
        if found!=expected:
            raise ValueError(f"IMMUTABLE_PARENT_GIT_BLOB_CHANGED {rel} {found}")
        sources[rel]=found
    return sources


def angular_grey_emission(n,w,beta,s):
    """Rest-isotropic unpolarized grey source with exact discrete (E,Q) moments.

    Units: emitted J carrier/time are in original BASS energy_unit per u.
    The nontrivial angular correction is a 4x4 moment match, not an invented
    separate frequency-resolved photon population. Its positivity is checked.
    """
    n=np.asarray(n,float);w=np.asarray(w,float);beta=np.asarray(beta,float)
    b2=float(beta@beta)
    if n.ndim!=2 or n.shape[1]!=3 or w.shape!=(len(n),) or beta.shape!=(3,):
        raise ValueError("bad angular source dimensions")
    if b2>=1 or np.any(w<=0) or not np.all(np.isfinite(w)):
        raise ValueError("unphysical boosted angular source")
    gamma=1/math.sqrt(1-b2)
    v=np.column_stack([np.ones(len(n)),n])
    D=1/(gamma*(1-n@beta))
    if np.min(D)<=0:raise ValueError("negative Doppler multiplier")
    template=D**3
    gram=np.einsum("n,na,nb->ab",w*template,v,v)
    target=gamma*np.r_[1.,beta]
    coeff=np.linalg.solve(gram,target)
    correction=v@coeff
    if np.min(correction)<=0:
        raise ValueError("negative angular quadrature emission correction")
    j=s*template*correction
    screen=np.eye(3)[None,:,:]-np.einsum("ni,nj->nij",n,n)
    source=.5*j[:,None,None]*screen
    raw=radiation_tensor(n,w,source)[0,:]
    want=s*target
    residual=float(np.max(np.abs(raw-want))/max(1e-300,float(np.max(np.abs(want)))))
    if residual>=2e-12:
        raise ArithmeticError(f"chemical four-force moment mismatch {residual}")
    return source,want,residual,float(np.min(correction)),float(np.max(correction))


class CoupledChemicalP8:
    """New, full joint IVP, not one-way chemistry on stored old geometry."""
    def __init__(self,*,ntheta=12,end=.25,chem_energy=True):
        self.parent=ExternalFLRWOpacityBianchi(ntheta=ntheta,end=end,opacity_mode="hyrec")
        self.end=float(end);self.ntheta=int(ntheta);self.chem_energy=bool(chem_energy)
        self.x0=float(self.parent.external.xe(1200.,"hyrec"))
        self.eta=(1-YHE)*ENERGY_J/((M_E_KG+M_P_KG)*C_M_S**2)
        self.initial_j_sha=hashlib.sha256(np.ascontiguousarray(self.parent.j0).tobytes()).hexdigest()
        self.initial_n_sha=hashlib.sha256(np.ascontiguousarray(self.parent.n0).tobytes()).hexdigest()
        self.N=self.parent.N
        self.initial_source=guard_all()

    def initial(self):
        return np.r_[self.parent.initial(),self.x0]

    def fields(self,t,y,derivative=False):
        y=np.asarray(y,float)
        if y.shape!=(self.parent.total_size+1,):
            raise ValueError("coupled electron fraction is a live state, not external lookup")
        x=float(y[-1])
        if not 0<x<1:raise ValueError("chemical x_e outside physical interval")
        # Only call the unchanged source-locked original Einstein/P8 geometry
        # and polarized streaming, then replace actual material source moments.
        d=self.parent.fields(t,y[:-1],derivative)
        zeta=float(d["zeta"]);gamma=float(d["gamma"])
        beta=np.asarray(d["beta"])
        p=np.asarray(d["p"])
        nH=self.parent.nH_rest0*zeta*self.parent.gamma0/gamma
        Tstar=self.parent.Tstar_seconds
        zvol=self.parent.zvol(zeta)
        if not 900<=zvol<=1200:raise ValueError("FLRW temperature support exceeded")
        Tm=float(self.parent.external.Tm(zvol));Tgamma=T_CMB0*(1+zvol)
        alpha=alpha_caseB(Tm);betab=beta_caseB(Tgamma)
        line=sobolev_directional(d["H"],d["sigma"],self.parent.n0,
                                 self.parent.w0,nH,x,Tstar)
        La=line["mean_s"]
        Cfac=(La+TWO_PHOTON)/(La+TWO_PHOTON+betab)
        rate_rest=Cfac*(betab*(1-x)*math.exp(-E_ALPHA_EV*E_CHARGE/(K_B*Tgamma))
                        -alpha*nH*x*x)
        # u is time in the normal tetrad; chemistry is a baryon-proper-time rate.
        xp=Tstar*rate_rest/gamma
        M=self.parent.M0*(1+self.eta*(x-self.x0)) if self.chem_energy else self.parent.M0
        if M<=0:raise ValueError("chemical mass defect exceeds rest mass")
        Re=M*zeta*gamma;Qe=M*zeta*p;Pe=Re*np.outer(beta,beta)
        nu=nH*x*SIGMA_T_M2*C_M_S*Tstar
        cf=expected_fourforce(d["T"],beta,nu)
        rho=d["rho_gamma"]+Re
        q=d["q_gamma"]+Qe
        P=d["Pgamma"]+Pe
        d.update(x=x,xprime=xp,nH=nH,zvol=zvol,Tm=Tm,Tgamma=Tgamma,
                 alphaB=alpha,betaB=betab,C_factor=Cfac,lambda_lya=La,
                 lya_quadrupole_norm=float(np.linalg.norm(line["quadrupole"])),
                 M=M,Re=Re,Qe=Qe,Pe=Pe,nu=nu,cf=cf,
                 rho=rho,q=q,P=P,p_iso=float(np.trace(P)/3),
                 anis=sym_traceless(P))
        # -dM/dx * zeta * dx/du, in original normal-u, energy-unit convention.
        # This is *rest-frame* grey emission; boost creates F^mu=(s gamma,s p).
        s=-self.parent.M0*self.eta*zeta*xp if self.chem_energy else 0.
        d["chem_rest_source"]=s
        if derivative:
            coll=linear_collision(d["op"],d["J"],nu)
            emission,force,gap,cmin,cmax=angular_grey_emission(d["n"],d["w"],beta,s)
            intensity=np.trace(coll,axis1=1,axis2=2)
            d.update(coll=coll,emission=emission,chem_force=force,
                     chem_discrete_gap=gap,angular_weight_correction_range=(cmin,cmax),
                     thomson_raw_force=np.r_[np.dot(d["w"],intensity),
                           np.einsum("n,n,ni->i",d["w"],intensity,d["n"])])
        return d

    def rhs(self,t,y):
        d=self.fields(t,y,True)
        H=d["H"];sigma=d["sigma"];B=d["B"]
        # The chemical rest-mass derivative and isotropic-baryon emission
        # cancel in p, so only the transverse Thomson force accelerates baryons.
        pdot=-B@d["p"]-d["cf"][1:]/(d["M"]*d["zeta"])
        ndot=-d["n"]@sigma.T+np.einsum("ni,ij,nj->n",d["n"],sigma,d["n"])[:,None]*d["n"]
        Omega=np.einsum("ni,nj->nij",ndot,d["n"])-np.einsum("ni,nj->nij",d["n"],ndot)
        Edot=np.einsum("nij,nja->nia",Omega,d["E"])
        Jdot=d["streaming"]+d["coll"]+d["emission"]
        Hdot=-.5*self.parent.kappa*(d["rho"]+d["p_iso"])-d["shear2"]
        sigmadot=-3*H*sigma+self.parent.kappa*d["anis"]
        return np.r_[(-B@d["A"]).ravel(),Edot.ravel(),Jdot.ravel(),
                     pdot,-3*H*d["zeta"],Hdot,sigma_to5(sigmadot),d["xprime"]]

    def solve(self,rtol=1e-11,atol=1.5e-13):
        sol=solve_ivp(self.rhs,(0,self.end),self.initial(),method="DOP853",
                      dense_output=True,rtol=rtol,atol=atol)
        if not sol.success:raise RuntimeError(sol.message)
        return sol

    def snapshot(self,t,y,derivative=False):
        d=self.fields(t,y,derivative)
        H=d["H"];s=d["sigma"];rho=d["rho"];k=self.parent.kappa
        ham=3*H**2-k*rho-d["shear2"]
        r={
          "u":float(t),"x_e":d["x"],"xe_parent_hyrec":float(self.parent.external.xe(d["zvol"],"hyrec")),
          "xprime_u":float(d["xprime"]),"zvol":float(d["zvol"]),"gamma_b":float(d["gamma"]),
          "H":float(H),"shear_frob":float(np.linalg.norm(s)),
          "shear":s.tolist(),"rho_gamma":float(d["rho_gamma"]),
          "rho_baryon":float(d["Re"]),"rho_total":float(rho),
          "q_total":d["q"].tolist(),"nH_m3":float(d["nH"]),
          "T_m_K":float(d["Tm"]),"T_gamma_K":float(d["Tgamma"]),
          "x_C_factor":float(d["C_factor"]),"lambda_lya_s":float(d["lambda_lya"]),
          "lyalpha_quad_F":float(d["lya_quadrupole_norm"]),
          "nu_live":float(d["nu"]),"chemical_mass_ratio":float(d["M"]/self.parent.M0),
          "chemical_rest_emission_per_u":float(d["chem_rest_source"]),
          "hamiltonian":float(ham),
          "hamiltonian_normalized":float(abs(ham)/max(k*rho+d["shear2"],1e-100)),
          "momentum_constraint_normalized":float(np.linalg.norm(d["q"])/rho),
          "charge_C_m3":float(E_CHARGE*(d["nH"]*d["x"]-d["nH"]*d["x"])),
          "xprime_rest_per_second":float(d["gamma"]*d["xprime"]/self.parent.Tstar_seconds),
          "photon_anisotropic_P":sym_traceless(d["Pgamma"]).tolist(),
        }
        if derivative:
            gap=d["thomson_raw_force"]-d["cf"]
            r.update(chem_force=d["chem_force"].tolist(),
                     thomson_discrete_gap=gap.tolist(),
                     chemical_force_moment_relative=d["chem_discrete_gap"],
                     correction_range=list(d["angular_weight_correction_range"]),
                     Hamiltonian_propagation_source=float(-k*gap[0]))
        return r

    def quadrature(self,sol,order=24):
        nodes,weights=leggauss(order)
        ts=self.end*(nodes+1)/2;ws=self.end*weights/2
        dtau=np.zeros(self.N)
        integral_chem=np.zeros(4)
        integral_rawgap=np.zeros(4)
        emission_correction_min=1e10
        emission_correction_max=0
        for t,w in zip(ts,ws):
            d=self.fields(float(t),sol.sol(float(t)),True)
            dtau+=w*d["nu"]*d["op"].D
            integral_chem+=w*d["chem_force"]
            integral_rawgap+=w*(d["thomson_raw_force"]-d["cf"])
            a,b=d["angular_weight_correction_range"]
            emission_correction_min=min(emission_correction_min,a)
            emission_correction_max=max(emission_correction_max,b)
        return {
          "tau_ray_mean":float(np.mean(dtau)),
          "tau_ray_min":float(np.min(dtau)),
          "tau_ray_max":float(np.max(dtau)),
          "tau_ray_weighted_mean":float(np.average(dtau,weights=self.parent.w0)),
          "tau_rays":dtau.tolist(),
          "integrated_chemical_fourforce":integral_chem.tolist(),
          "integrated_thomson_discrete_gap":integral_rawgap.tolist(),
          "moment_weight_correction_min":float(emission_correction_min),
          "moment_weight_correction_max":float(emission_correction_max),
        }

    def conservation(self,sol,order=24):
        x,w=leggauss(order)
        ts=self.end*(x+1)/2;ws=self.end*w/2
        data=[self.snapshot(float(t),sol.sol(float(t)),True) for t in ts]
        first=self.snapshot(0,sol.sol(0),True)
        last=self.snapshot(self.end,sol.sol(self.end),True)
        deltaC=last["hamiltonian"]-first["hamiltonian"]
        predicted=float(np.dot(ws,[v["Hamiltonian_propagation_source"] for v in data]))
        dQ=np.asarray(last["q_total"])-np.asarray(first["q_total"])
        rhsQ=np.array([-(4*v["H"]*np.eye(3)+np.asarray(v["shear"]))@np.asarray(v["q_total"])
                       +np.asarray(v["thomson_discrete_gap"])[1:] for v in data])
        intQ=np.einsum("n,ni->i",ws,rhsQ)
        return {
          "max_Hamiltonian_norm":max(z["hamiltonian_normalized"] for z in [first,last]+data),
          "max_momentum_norm":max(z["momentum_constraint_normalized"] for z in [first,last]+data),
          "delta_hamiltonian":deltaC,
          "predicted_hamiltonian_delta":predicted,
          "hamiltonian_propagation_error":float(abs(deltaC-predicted)),
          "momentum_integrated_error":float(np.max(abs(dQ-intQ))),
          "max_chemical_fourforce_discrete_relative":max(z["chemical_force_moment_relative"] for z in [first,last]+data),
        }


def run_science(output,orders=(12,16),end=.25):
    src=guard_all()
    runs={}
    for n in orders:
        modes={}
        for label,active in (("full",True),("opacity_only",False)):
            m=CoupledChemicalP8(ntheta=n,end=end,chem_energy=active)
            sol=m.solve()
            epochs=[m.snapshot(float(t),sol.sol(float(t))) for t in np.linspace(0,end,41)]
            small=[m.snapshot(float(t),sol.sol(float(t)),True) for t in (0,end/2,end)]
            cons=m.conservation(sol,order=24)
            depth=m.quadrature(sol,order=24)
            if cons["max_Hamiltonian_norm"]>5e-8 or cons["max_momentum_norm"]>5e-8:
                raise ArithmeticError("chemical Einstein constraints fail "+str(cons))
            if cons["hamiltonian_propagation_error"]>5e-8 or cons["momentum_integrated_error"]>5e-8:
                raise ArithmeticError("chemical Einstein propagation fails "+str(cons))
            if not all(0<r["x_e"]<1 for r in epochs):
                raise ArithmeticError("unphysical chemical evolution")
            modes[label]={"epochs":epochs,"source_snapshots":small,"conservation":cons,
                          "depth":depth,"rhs_evals":int(sol.nfev),
                          "initial_j_sha256":m.initial_j_sha,
                          "initial_n_sha256":m.initial_n_sha,
                          "mass_eta":m.eta}
        parent=ExternalFLRWOpacityBianchi(ntheta=n,end=end,opacity_mode="hyrec")
        psol=parent.solve(rtol=1e-11,atol=1.5e-13)
        endparent=parent.fields(end,psol.sol(end),False)
        parenttau=parent.optical_depth(psol,order=24)
        mf=modes["full"]["epochs"][-1]
        mo=modes["opacity_only"]["epochs"][-1]
        comparisons={
            "chem_xe_end":mf["x_e"],
            "old_hyrec_xe_end":float(endparent["xe_external"]),
            "full_minus_opacity_only_photon_rho":mf["rho_gamma"]-mo["rho_gamma"],
            "full_minus_opacity_only_H":mf["H"]-mo["H"],
            "full_minus_opacity_only_xe":mf["x_e"]-mo["x_e"],
            "full_minus_parent_photon_rho":mf["rho_gamma"]-float(endparent["rho_gamma"]),
            "full_minus_parent_H":mf["H"]-float(endparent["H"]),
            "full_minus_parent_shear_frob":mf["shear_frob"]-float(np.linalg.norm(endparent["sigma"])),
            "full_minus_parent_shear_matrix_frob":float(np.linalg.norm(np.asarray(mf["shear"])-endparent["sigma"])),
            "full_tau_minus_parent_mean":modes["full"]["depth"]["tau_ray_mean"]-float(np.mean(parenttau)),
            "old_parent_tau_mean":float(np.mean(parenttau)),
            "hydrogen_binding_release_eV_per_H":CHI_H_EV*(m.x0-mf["x_e"]),
            "full_photon_rho_energy_scale_J_m3":mf["rho_gamma"]*m.parent.energy_unit_J_m3,
        }
        if abs(comparisons["full_minus_parent_shear_matrix_frob"])<=1e-8:
            raise ArithmeticError("new Thomson feedback has no Einstein physical signature")
        if abs(comparisons["full_minus_opacity_only_photon_rho"])<=1e-12:
            raise ArithmeticError("new radiative binding-feedback physical effect absent")
        runs[f"GL{n}"]={
            "n_theta":n,"N_original_P8_rays":m.N,"parent_original_Einstein_IVP_nfev":int(psol.nfev),
            "parent_initial_J_sha256":hashlib.sha256(np.ascontiguousarray(parent.j0).tobytes()).hexdigest(),
            "cases":modes,"comparison":comparisons,
        }
        print("KM2J_COUPLED_PHYSICS",n,
              "x_e",mf["x_e"],"tau",modes["full"]["depth"]["tau_ray_mean"],
              "P8_binding_delta",comparisons["full_minus_opacity_only_photon_rho"],
              "shear_matrix_delta",comparisons["full_minus_parent_shear_matrix_frob"],
              "Hamiltonian",modes["full"]["conservation"]["max_Hamiltonian_norm"],flush=True)
    result={
        "schema":"bass.km2j.chemistry_thomson_grey_binding_Einstein_P8.v1",
        "parent_pr":289,"parent_head":PARENT_HEAD,"source_blobs":src,
        "upper_dag":"9/15","upper_edges":21,"KM2":"PARTIAL","new_upper_nodes":0,
        "scoped_unit":"KM2J_CHEMISTRY_TO_P8_ENERGY_MOMENTUM_FEEDBACK",
        "description":"genuine joint dynamic hydrogen xe + source-locked Einstein polarized P8 photon IVPs with proper-time Peebles rate and angular fourmoment-conserving grey chemical binding emission",
        "chemistry_rate_clock":"baryon_proper_time; dx/du=Tstar*rate_rest/gamma_b",
        "chemistry_energy":"relative cold baryon rest mass M(x)=M0[1+eta(x-x0)]; equal and opposite grey photon source; not full thermal/ionizing/line spectral energy",
        "external_rate_inputs":"original HYREC Tm(zvol), Tgamma=2.7255 K*(1+zvol); original CLASS Peebles B coefficients",
        "approximation":"original normal-frame isotropic Sobolev proxy, rest-isotropic chemically emitted bolometric unpolarized grey photon surrogate",
        "cases":runs,"production_ready":False,"merge_ready":False,"auto_next":False,
        "not_implemented":["frequency resolved Lyalpha and ionizing radiation","thermal and entropy equation","selfconsistent rate detailed balance from native P8 nonthermal photon spectrum","tilted-baryon Lyalpha transport","realistic baryon density matching CLASS","distinct-author R6/C9","angular continuum enclosure"],
        "distinct_author_R6_C9":"NOT_RUN","native_subagent":"NOT_RUN",
    }
    output=Path(output);output.parent.mkdir(exist_ok=True,parents=True)
    output.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")
    return result


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--output",required=True,type=Path)
    p.add_argument("--orders",default="12,16")
    a=p.parse_args()
    run_science(a.output,tuple(map(int,a.orders.split(","))))
