"""Source-bound combined gamma/neutrino Boltzmann and massive FD96 Einstein Bianchi-I.

Physical new lane:
 - photons gamma & massless neutrinos evolved in separate energy/number
   Legendre hierarchies, only gamma Thomson-damped by original AX08 HHe ne donor
 - BASS original massive collisionless FD96 radial/GL angular occupation,
   with independent initial positive quadrupole Am and kinetic matter fraction fm
 - independent initial Sigma=sqrt3|s|/H and signed orientation
 - Einstein Hamiltonian, shear, energy work and proper clock evolved together

This is unpolarized and one-way ne (not coupled CMB polarization, photoUV
radiation or gas/particle collisions); an opt-in REI *research* component.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import hashlib,json,math,sys,time
import numpy as np
from scipy.integrate import solve_ivp
from scipy.constants import c as SPEED_C, sigma as STEFAN

HERE=Path(__file__).resolve().parent
BASS_ROOT=HERE.parents[1]
SRC=HERE/"source_refs"
sys.path.insert(0,str(SRC))
sys.path.insert(0,str(HERE.parent/"rei_axbi_sigma_matter_20261015"))
from species_hierarchy import SpeciesHierarchy
from lrs_boltzmann import SourceLock,GAMMA_PER_NE,SmoothElectronHistory
from sigma_matter import MassiveMoments,InitialStress,verify_source_bytes,signed_q_from_sigma
from stable_moments import StableMassiveMoments

PARENT_REI_HEAD="5d41df647c4fd624d8a1b574f67fdd0b82ff5102"
PARENT_BASS_HEAD="9e50f936f3289cb0c7c8127772cf9fb8d172d7a8"
AX03_SOURCE_SHA="46f818c2f9de890c72f71fa3cc70366b28c42ca0d65190bd905b6310023e7af0"
REI_SOURCE_SHA={
"lrs_boltzmann.py":"06ef834e4cd7adacf01f0ad6e3becc5aea9a493b5b99fd398be82610543984cc",
"species_hierarchy.py":"ced7906b35c26d8d0374ee8ce7f67ceb957b51a63d44e5a2661997b7e46983c5"}
HHE_DONOR_REL="research/axbi_goal_20261014/runs/flrw/32d11e733155/ZERO_composed_001"

def verify_original_sources():
    verify_source_bytes()
    for name,sha in REI_SOURCE_SHA.items():
        p=SRC/name
        if hashlib.sha256(p.read_bytes()).hexdigest()!=sha:
            raise RuntimeError("REI_ORIGINAL_BOLTZMANN_SOURCE_SHA_CHANGED:"+name)
    p=HERE.parent/"rei_axbi_background_supplier_20261015/source/REI_BACKGROUND_FAMILY_LOCK.json"
    if hashlib.sha256(p.read_bytes()).hexdigest()!=AX03_SOURCE_SHA:
        raise RuntimeError("REI_ORIGINAL_AX03_BACKGROUND_SOURCE_CHANGED")
    return json.loads(p.read_text())

def source_lock():
    d=verify_original_sources()
    c=d["cosmology"];a=d["clock"]
    return SourceLock(h0=float(c["H0_per_s"]),omega_m=float(c["Omega_m"]),
                      omega_r=float(c["Omega_r"]),omega_lambda=float(c["Omega_lambda"]),
                      aref=float(a["a_ref"]),aend=float(a["a_end"]))

def sha256_file(path,chunk=1<<20):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        while True:
            b=f.read(chunk)
            if not b:break
            h.update(b)
    return h.hexdigest()

def actual_AX08_electron_donor(owner:Path,*,nodes=8193):
    """Explicit opt-in actual composed original REI ZERO source + exact SHA."""
    root=Path(owner).resolve()/HHE_DONOR_REL
    receipt=json.loads((root/"COMPOSITION_RECEIPT.json").read_text())
    if receipt["status"]!="COMPOSED_COMPLETED_HISTORY_NOT_SCIENTIFIC_ADMISSION":
        raise RuntimeError("ACTUAL_AX08_ELECTRON_DONOR_NOT_COMPOSED")
    if receipt["row_counts"]["history.csv"]["composed_rows"]!=312238:
        raise RuntimeError("AX08_REAL_DONOR_HISTORY_ROWS_CHANGED")
    target=root/"history.csv"
    digest=sha256_file(target)
    if digest!=receipt["output_sha256"]["history.csv"]:
        raise RuntimeError("ACTUAL_REI_HHE_DONOR_SOURCE_BYTES_CHANGED")
    data=np.loadtxt(target,delimiter=",",skiprows=1,usecols=(4,13),dtype=np.float64)
    if data.shape!=(312238,2):
        raise RuntimeError("HHE_SOURCE_COLUMN_COUNT_OR_ROWS_CHANGED")
    d=SmoothElectronHistory(data[:,0],data[:,1],nodes=nodes)
    return d,{"original_real_AX08_ZERO_history_sha256":digest,
              "original_real_AX08_rows":len(data),
              "source_kind":"one_way_C2_electron_donor",
              "max_relative_saved_source_interpolation_error":d.max_relative_source_error,
              "p999_relative_saved_source_interpolation_error":d.p999_relative_source_error,
              "native_HHe_end_to_end_coupled":False}

class KineticGammaNuMassive(SpeciesHierarchy):
    """Exactly source-normalized \u03b3,\u03bd massless and massive FD stress in same Einstein H."""
    def __init__(self,source:SourceLock,*,Sigma_ref:float=0.,orientation:int=0,
                 kappa_gamma:float=0.,kappa_nu:float=0.,
                 massive_fraction:float=0.,massive_A:float=0.,m_over_Tref:float=30.,
                 ne_source=None,ellmax:int=8,angular_n:int=32,
                 stable_massive_pi:bool=False):
        verify_original_sources()
        if not (math.isfinite(massive_fraction) and 0<=massive_fraction <=
                (source.omega_m-float(verify_original_sources()["cosmology"]["Omega_b"]))/source.omega_m):
            raise ValueError("massive population cannot double count baryon + dark matter")
        if not math.isfinite(massive_A) or not -1<=massive_A<=2:
            raise ValueError("massive positive initial source W=1+A P2")
        if not math.isfinite(m_over_Tref) or not 3<=m_over_Tref<=1e5:
            raise ValueError("source-bounded massive radial rest/thermal ratio")
        # Source normalizations of original REI are identical to BASS source lock.
        c=source_lock()
        if source!=c:raise ValueError("REI original cosmology/clock source mismatch")
        super().__init__(source,float(verify_original_sources()["cosmology"]["Tcmb0_K"]),
                         ellmax=ellmax,Sigma_ref=Sigma_ref,orientation=orientation,
                         kappa_gamma=kappa_gamma,kappa_nu=kappa_nu,ne_source=ne_source,
                         matter_nu_viscosity=0.)
        self.fm=massive_fraction
        self.Am=massive_A
        self.m_over_Tref=m_over_Tref
        if not isinstance(stable_massive_pi,bool):
            raise ValueError("stable_massive_pi must be an explicit boolean")
        self.stable_massive_pi=stable_massive_pi
        self.mass=(StableMassiveMoments if stable_massive_pi else MassiveMoments)(
            m_over_Tref,angular_n=angular_n)
        self.matter_dust_omega=source.omega_m*(1-massive_fraction)
        self.mass_normalizer=source.omega_m*massive_fraction/source.aref**3
        self.matter_max_fraction=(source.omega_m-float(verify_original_sources()["cosmology"]["Omega_b"]))/source.omega_m
        orient=orientation if orientation in (-1,1) else 1
        self.original_BASS_initial=InitialStress(
            Sigma_ref=Sigma_ref,shear_orientation=orient,
            radiation_fraction=1.,radiation_A=kappa_gamma,
            massive_matter_fraction=massive_fraction,
            massive_matter_A=massive_A,mass_over_Tref=m_over_Tref)
    def fields(self,x,y):
        if not np.isfinite(y).all() or not math.isfinite(x) or not 0<=x<=self.source.xmax+1e-12:
            raise ValueError("finite source chart required")
        if len(y)!=4+4*self.n:raise ValueError("incorrect signed Boltzmann state")
        tau,b,v,uth=y[:4]
        if abs(uth)>1e-12:
            raise ValueError("no phenomenological gas/matter energy pool in kinetic source")
        a=self.source.aref*math.exp(x)
        Eg,Ng,En,Nn=[y[4+i*self.n:4+(i+1)*self.n] for i in range(4)]
        if Eg[0]<=0 or En[0]<=0:raise ValueError("positive radiation brightness")
        s=v*self.source.href
        if self.stable_massive_pi:
            Mr,pp,pa,delta_m=self.mass.evaluate_with_delta(x,b,self.Am)
        else:
            Mr,pp,pa=self.mass.evaluate(x,b,self.Am)
            delta_m=pa-pp
        rho_m=self.mass_normalizer*Mr
        pi_m=self.mass_normalizer*delta_m/3
        pbar_m=self.mass_normalizer*(2*pp+pa)/3
        rho_rad=(self.omega_gamma*Eg[0]+self.omega_nu*En[0])/a**4
        pi_g=self.omega_gamma*Eg[2]/(3*a**4)
        pi_n=self.omega_nu*En[2]/(3*a**4)
        dust=self.matter_dust_omega/a**3
        h2=self.source.h0**2*(dust+self.source.omega_lambda+rho_m+rho_rad)+s*s
        if not h2>0:raise ArithmeticError("nonpositive Einstein Hamiltonian source")
        H=math.sqrt(h2)
        ne=0 if self.ne_source is None else float(self.ne_source.density(a))
        if not math.isfinite(ne) or ne<0:raise ValueError("actual Thomson opacity invalid")
        return {"a":a,"b":b,"s":s,"H":H,"H2":h2,
                "Sigma":math.sqrt(3)*abs(s)/H,
                "signed_s_over_H":s/H,
                "E_gamma":Eg,"N_gamma":Ng,"E_nu":En,"N_nu":Nn,
                "rho_rad_norm":rho_rad,
                "pi_gamma_norm":pi_g,"pi_nu_norm":pi_n,"pi_radiation_norm":pi_g+pi_n,
                "rho_massive_norm":rho_m,"pm_perp_norm":self.mass_normalizer*pp,
                "pm_parallel_norm":self.mass_normalizer*pa,"pbar_massive_norm":pbar_m,
                "pi_massive_norm":pi_m,
                "dust_norm":dust,"GammaT":ne*GAMMA_PER_NE,
                "electron_density_cm3":ne,
                "pi_radiation_J_m3":(pi_g+pi_n)*self.source.rhocrit_j_m3,
                "pi_massive_J_m3":pi_m*self.source.rhocrit_j_m3,
                "pi_total_J_m3":(pi_g+pi_n+pi_m)*self.source.rhocrit_j_m3,
                "rho_r_J_m3":rho_rad*self.source.rhocrit_j_m3,
                "rho_m_J_m3":rho_m*self.source.rhocrit_j_m3,
                "meanH_prime_x":-(
                    self.source.h0**2*(3*dust+4*rho_rad+3*(rho_m+pbar_m))+
                    6*s*s)/(2*H)}
    def rhs(self,x,y):
        v=self.fields(x,y)
        h=v["H"];q=v["s"]/h
        kg=v["GammaT"]/h
        Eg=v["E_gamma"];Ng=v["N_gamma"];En=v["E_nu"];Nn=v["N_nu"]
        dEg=q*(self.energy_matrix@Eg)-kg*self.thomson*Eg
        dNg=q*(self.number_matrix@Ng)-kg*self.thomson*Ng
        dEn=q*(self.energy_matrix@En)
        dNn=q*(self.number_matrix@Nn)
        pi=v["pi_gamma_norm"]+v["pi_nu_norm"]+v["pi_massive_norm"]
        dsh=-3*y[2]+3*self.source.h0**2/(self.source.href*h)*pi
        # No external viscous phenomenological "u" energy pool:
        return np.r_[self.source.href/h,q,dsh,0.,dEg,dNg,dEn,dNn]
    def integrate(self,n=301,rtol=5e-11,atol=1e-13):
        begin=time.perf_counter()
        y0=self.initial_state()
        p=solve_ivp(self.rhs,(0.,self.source.xmax),y0,
                    method="DOP853",rtol=rtol,atol=atol,
                    t_eval=np.linspace(0.,self.source.xmax,n))
        wall=time.perf_counter()-begin
        if not p.success or not np.isfinite(p.y).all():
            raise RuntimeError("POSITIVE_MASSIVE_GAMMANU_EINSTEIN_ODE_FAILED")
        vals=[self.fields(float(x),p.y[:,i]) for i,x in enumerate(p.t)]
        if any(abs(k["N_gamma"][0]-1)>5e-12 or abs(k["N_nu"][0]-1)>5e-12 for k in vals):
            raise ArithmeticError("photon/neutrino number zero-mode drift")
        return p,vals,wall
    def minimum_angular_brightness(self,y,order=128):
        """Actual independent gamma and neutrino positive angular reconstruction."""
        from numpy.polynomial.legendre import Legendre,leggauss
        mu,_=leggauss(order)
        projection=np.array([(2*l+1)*Legendre.basis(l)(mu)
                             for l in range(self.n)])
        gamma=y[4:4+self.n]@projection
        nu=y[4+2*self.n:4+3*self.n]@projection
        return float(min(np.min(gamma),np.min(nu)))

    def initial_tensors(self):
        f=self.fields(0,self.initial_state())
        c=self.source.rhocrit_j_m3
        return {
          "Sigma_ref":self.Sigma_ref,
          "orientation":self.orientation,
          "gamma_Pi_J_m3":f["pi_gamma_norm"]*c,
          "nu_Pi_J_m3":f["pi_nu_norm"]*c,
          "massive_Pi_J_m3":f["pi_massive_norm"]*c,
          "total_Pi_J_m3":(f["pi_gamma_norm"]+f["pi_nu_norm"]+f["pi_massive_norm"])*c,
          "pi_tensor_diag_J_m3":
            [-f["pi_total_J_m3"],-f["pi_total_J_m3"],2*f["pi_total_J_m3"]],
          "rho_gamma_fraction_of_rounded_radiation":self.f_gamma,
          "rho_nu_fraction_of_rounded_radiation":self.f_nu,
          "nonbaryonic_massive_fraction_of_total_matter":self.fm,
          "source_constraint":"Hamiltonian includes radiation gamma+nu plus one massive kinetic fraction of Omega_m plus remaining dust; no double counting",
          "Thomson_species":"gamma-only one-way original q0 HHe electron donor",
          "massive_pi_evaluation":("stable_inverse_energy" if self.stable_massive_pi
                                   else "legacy_pressure_subtraction")
        }
    def constraint_and_work(self,x,y):
        f=self.fields(x,y)
        q=f["s"]/f["H"]
        yp=self.rhs(x,y)
        n=self.n
        # radiation E0 work, separate for gamma and neutrinos; Thomson elastic
        eg_work=yp[4]+2*q*f["E_gamma"][2]
        en_work=yp[4+2*n]+2*q*f["E_nu"][2]
        # pointwise Raychaudhuri from independent local physical source formula
        scalar=3*self.source.h0**2/(self.source.href*f["H"])*(
               f["pi_radiation_norm"]+f["pi_massive_norm"])
        shear=yp[2]+3*y[2]-scalar
        return {"gamma_monopole_work_residual":float(eg_work),
                "nu_monopole_work_residual":float(en_work),
                "shear_Einstein_rhs_residual":float(shear),
                "massive_energy_and_pressures_J_m3":[f["rho_m_J_m3"],
                    f["pm_perp_norm"]*self.source.rhocrit_j_m3,
                    f["pm_parallel_norm"]*self.source.rhocrit_j_m3],
                "Hprime_from_Raychaudhuri":float(f["meanH_prime_x"])}
