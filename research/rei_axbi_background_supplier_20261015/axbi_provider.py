"""REI AX03 source-frozen stress-free LRS Bianchi I proper-time background.

Independent DOP853 solver in x=ln(a/a_ref) and vectorized exact algebra for
H,s, photon Killing momenta. Original REI rust/axbi_background.rs is *not edited*.
This supplies geometry, not anisotropic-stress feedback or ionization histories.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import hashlib,json,math
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

ROOT=Path(__file__).resolve().parent
FROZEN=ROOT/"source/REI_BACKGROUND_FAMILY_LOCK.json"
LOCK_SHA="46f818c2f9de890c72f71fa3cc70366b28c42ca0d65190bd905b6310023e7af0"
G_CGS=6.67430e-8
M_PROTON_G=1.67262192595e-24

def _finite(x):
    return bool(np.all(np.isfinite(x)))

def _read_lock():
    raw=FROZEN.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=LOCK_SHA:
        raise ValueError("REI_AX03_BACKGROUND_LOCK_BYTE_IDENTITY_MISMATCH")
    spec=json.loads(raw)
    if spec["schema"]!="rei.axbi.background_family.v1":
        raise ValueError("invalid REI background schema")
    return spec

@dataclass(frozen=True)
class Family:
    q_ref:float
    family:str="PhysicalDensityFixed"
    def __post_init__(self):
        spec=_read_lock()
        if not math.isfinite(self.q_ref) or self.q_ref not in spec["q_ref_family"]:
            raise ValueError("REI original signed case must be exactly one of frozen five q")
        if self.family not in ("PhysicalDensityFixed","SameHDiagnostic"):
            raise ValueError("REI unsupported background family")
        if self.family=="SameHDiagnostic" and self.q_ref!=spec["same_h"]["q_ref"]:
            raise ValueError("SameH only frozen q=+.01 counterfactual")

class Background:
    """One scenario, DOP853 high-accuracy in dimensionless proper time Href*t."""
    def __init__(self,case:Family,rtol=8e-13,atol=5e-15):
        s=_read_lock()
        self.case=case; self.source=s
        c=s["cosmology"];clock=s["clock"]
        self.h0=float(c["H0_per_s"])
        self.om=float(c["Omega_m"]);self.orad=float(c["Omega_r"]);self.ol=float(c["Omega_lambda"])
        self.ob=float(c["Omega_b"]);self.yhe=float(c["X_He4"]);self.t0=float(c["Tcmb0_K"])
        self.aref=float(clock["a_ref"]);self.aend=float(clock["a_end"])
        self.xmax=math.log(self.aend/self.aref)
        self.href=self.h_flrw(self.aref)
        self.sref=case.q_ref*self.href
        self.prefactor=self.sref*self.aref**3
        rho_crit=3*self.h0*self.h0/(8*math.pi*G_CGS)
        self.nh0=(1-self.yhe)*self.ob*rho_crit/M_PROTON_G
        self.nhe0=self.yhe*self.ob*rho_crit/(4*M_PROTON_G)
        if not (0<rtol<1e-8 and 0<atol<1e-10):
            raise ValueError("positive strict ODE tolerances")
        def rhs(x,Y):
            a=self.aref*math.exp(x);H=self.mean_hubble(a)
            return [self.href/H,self.shear(a)/H]
        self.ivp=solve_ivp(rhs,(0.,self.xmax),(0.,float(clock["b_ref"])),
                           method="DOP853",rtol=rtol,atol=atol,dense_output=True)
        if not self.ivp.success or not _finite(self.ivp.y):
            raise ArithmeticError("REI_AX03_BACKGROUND_SOLVER_FAILED")

    def h_flrw(self,a):
        a=np.asarray(a,dtype=float)
        if not _finite(a) or np.any(a<=0):raise ValueError("positive scale factor")
        x=(self.om/a**3+self.orad/a**4+self.ol)
        out=self.h0*np.sqrt(x)
        if not _finite(out) or np.any(out<=0):raise ValueError("invalid H_flrw")
        return float(out) if out.ndim==0 else out

    def shear(self,a):
        a=np.asarray(a,dtype=float)
        if not _finite(a) or np.any(a<=0):raise ValueError("positive scale")
        val=self.prefactor/a**3
        return float(val) if val.ndim==0 else val

    def mean_hubble(self,a):
        hf=self.h_flrw(a)
        s=self.shear(a)
        return np.hypot(hf,s) if self.case.family=="PhysicalDensityFixed" else hf

    def at_x(self,x):
        x=np.asarray(x,dtype=float)
        if not _finite(x) or np.any(x<0) or np.any(x>self.xmax):
            raise ValueError("outside sealed log scale domain")
        a=self.aref*np.exp(x)
        Y=self.ivp.sol(x)
        t=Y[0]/self.href
        bb=Y[1]
        hf=self.h_flrw(a)
        h=self.mean_hubble(a);sh=self.shear(a)
        hp=h-sh;hl=h+2*sh
        ap=a*np.exp(-bb);al=a*np.exp(2*bb)
        ans={"ln_a_over_aref":x,
            "a":a,"zbar":1/a-1,"proper_elapsed_s":t,
            "b":bb,"H_flrw_per_s":hf,"H_mean_per_s":h,
            "shear_s_per_s":sh,"sigma_s_over_H":sh/h,
            "sigma_tensor_squared_per_s2":3*sh**2,
            "H_perp_per_s":hp,"H_parallel_per_s":hl,
            "a_perp":ap,"a_parallel":al,
            "n_H_cm3":self.nh0/a**3,"n_He_cm3":self.nhe0/a**3,
            "Tbar_CMB_K":self.t0/a,
            "dt_dln_a_s":1/h,"db_dln_a":sh/h,
            "dproper_t_dz_s":-a/h,
            "volume_a_perp2_a_parallel":ap*ap*al}
        if x.ndim==0:
            return {k:float(np.asarray(v)) for k,v in ans.items()}
        return ans

    def at_a(self,a):
        a=float(a)
        if not math.isfinite(a) or a<self.aref or a>self.aend:
            raise ValueError("outside source-locked scale family")
        if a==self.aref:return self.at_x(0.)
        if a==self.aend:return self.at_x(self.xmax)
        return self.at_x(math.log(a/self.aref))

    def at_time(self,time_s):
        time_s=float(time_s)
        end=self.at_x(self.xmax)["proper_elapsed_s"]
        if not math.isfinite(time_s) or time_s<0 or time_s>end:
            raise ValueError("outside proper-time domain")
        if time_s==0:return self.at_x(0.)
        if time_s==end:return self.at_x(self.xmax)
        def f(x):return float(self.ivp.sol(x)[0])/self.href-time_s
        x=brentq(f,0,self.xmax,xtol=4e-15,rtol=8.881784197001252e-16)
        return self.at_x(x)

    def table(self,n=501):
        if not isinstance(n,int) or isinstance(n,bool) or n<3 or n>32769:
            raise ValueError("bounded 3..32769 points")
        x=np.linspace(0,self.xmax,n)
        out=self.at_x(x)
        return out

def photon_pullback(early,face,mu_face):
    """Exact axisymmetric Killing momentum relations, with common aligned axis.

    face and early are points under ONE case. mu_face is *orthonormal*
    direction cosine at face and independent of energy normalization.
    """
    mu=np.asarray(mu_face,dtype=float)
    if not _finite(mu) or np.any(np.abs(mu)>1):
        raise ValueError("physical mu_face in [-1,1]")
    if not (early["a"]<=face["a"] and early["a"]>0):
        raise ValueError("ordered geometry early->face required")
    delta_b=early["b"]-face["b"]
    R2=np.exp(2*delta_b)*(1-mu*mu)+np.exp(-4*delta_b)*mu*mu
    R=np.sqrt(R2)
    ratio=face["a"]/early["a"]*R
    mu_early=mu*np.exp(-2*delta_b)/R
    jac=R**(-3)
    return {"energy_early_over_face":ratio,"mu_early":mu_early,
            "jacobian_dOmega_early_over_face":jac,
            "number_volume_invariant":ratio**3*jac,
            "geometry_volume_factor":(face["a"]/early["a"])**3}

def matter_only_closed_form(q=0.01,a_ref=1/21,a=1/5,h0=2e-18,omega_m=1.0):
    """Independent exact dust + free-shear Bianchi-I analytic integral."""
    if not all(np.isfinite([q,a_ref,a,h0,omega_m])) or not(0<a_ref<=a and h0>0 and omega_m>0):
        raise ValueError("dust problem domain")
    Href=h0*np.sqrt(omega_m/a_ref**3)
    C=q*Href*a_ref**3
    A=h0*h0*omega_m
    u0=a_ref**3;u=a**3
    clock=(2/(3*A))*(np.sqrt(A*u+C*C)-np.sqrt(A*u0+C*C))
    b=(2/3)*(np.arcsinh(C/np.sqrt(A*u0))-np.arcsinh(C/np.sqrt(A*u)))
    return {"elapsed_proper_s":float(clock),"b":float(b)}

def run_demo():
    lock=_read_lock();out=[]
    for q in lock["q_ref_family"]:
        obj=Background(Family(q))
        p=obj.at_a(obj.aend)
        out.append({"q_ref":q,"family":"PhysicalDensityFixed",
                    "t_end_s":p["proper_elapsed_s"],"b_end":p["b"],
                    "sigma_end":p["sigma_s_over_H"],
                    "n_H_end":p["n_H_cm3"],
                    "photon_face_ref_mu0p6":{k:float(np.asarray(v)) for k,v in photon_pullback(obj.at_a(obj.aref),p,.6).items()}})
    return {"schema":"bass.rei.axbi.background_supplier.v1",
            "source_lock_sha256":LOCK_SHA,"scoped_model":"source-locked stress-free AX03 z20->z4",
            "cases":out,"scientific_admission":"BACKGROUND_NUMERICAL_COMPONENT_ONLY"}
if __name__=="__main__":
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument("--out",type=Path)
    args=ap.parse_args()
    j=run_demo()
    if args.out:
        if args.out.exists():raise FileExistsError(args.out)
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(j,indent=2)+"\n")
    print(json.dumps(j,indent=2))
