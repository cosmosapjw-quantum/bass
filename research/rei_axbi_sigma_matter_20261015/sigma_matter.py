"""AX03 initial Σ and TWO independent kinetic anisotropic stresses, Einstein-Vlasov.

Extends actual source-locked radiation Einstein-Vlasov Bianchi I from BASS
research/rei_axbi_anisostress_20261015 with a source-normalized MASSIVE
collisionless component taken from the existing Ω_m energy budget, using
THE ORIGINAL BASS bianchi.matter.freestream radial Fermi-Dirac quadrature.

Public input Σ_ref=sqrt(σ_ab σ^ab/2)/H_ref >=0; sign must be supplied separately.
No guessed viscous pi(t): radiation and massive matter phase-space invariant
comoving momenta yield exact kinetic epsilon, pressure and pi_ab. The rest of
matter (including all Ω_b) is cold dust and has pi_ab=0. No realistic radiation
Thomson interactions or ionizing source collisions here.
"""
from __future__ import annotations
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import hashlib,math,sys
import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.integrate import solve_ivp

HERE=Path(__file__).resolve().parent
BASS_ROOT=HERE.parents[1]
sys.path.insert(0,str(BASS_ROOT))
PARENT=HERE.parent/"rei_axbi_anisostress_20261015"
if not (PARENT/"einstein_vlasov_lrs.py").is_file():
    raise FileNotFoundError("PARENT_SOURCE_LOCKED_EINSTEIN_VLASOV_UNAVAILABLE")
sys.path.insert(0,str(PARENT))
import einstein_vlasov_lrs as radiation
from bianchi.matter import freestream as bass_vlasov

G_SI=radiation.G_SI
C_SI=radiation.C_SI
LOCK_SHA=radiation.LOCK_SHA
SOURCE_Q=(0.,.005,-.005,.01,-.01)
ORIGINAL_BASS_SHA256={
    'bianchi/matter/freestream.py':'b03aeed2cfcdaa5baf45fdab626941905674e2385bc06d1173a4b8c39ebf8bb4',
    'bianchi/matter/hierarchy.py':'27f81acd681acc34537ad59ad2bec923d95c0adb7ac6d52413c4e3b2e0980aa6',
    'bianchi/matter/kinetic_einstein.py':'59f1c49539d35061d17490944ace63c48addce0e44e3d1a0f39f8f40b363d93b',
    'research/rei_axbi_anisostress_20261015/einstein_vlasov_lrs.py':'3add79941ddc8601170dc330cfafb3b3a6d23fff638129e4a67b4853c6b29a51',
}
def verify_source_bytes():
    for path,source_sha in ORIGINAL_BASS_SHA256.items():
        if hashlib.sha256((BASS_ROOT/path).read_bytes()).hexdigest()!=source_sha:
            raise ValueError('ORIGINAL_BASS_HIERARCHY_BYTE_IDENTITY_MISMATCH:'+path)
    if radiation._read_lock()['schema']!='rei.axbi.background_family.v1':
        raise ValueError('INVALID_REI_SOURCE')
    return ORIGINAL_BASS_SHA256


def sigma_from_legacy_q(q):
    q=float(q)
    if not math.isfinite(q):raise ValueError("finite previous signed q")
    return math.sqrt(3)*abs(q)/math.hypot(1.,q)

def signed_q_from_sigma(sigma_ref,orientation):
    """Exact bijection to frozen stress-free q at initial time (NOT q input API)."""
    sig=float(sigma_ref)
    if not math.isfinite(sig) or not (0<=sig<math.sqrt(3)):
        raise ValueError("0<=Sigma<sqrt(3) for H constraint")
    if orientation not in (-1,1):
        raise ValueError("explicit signed LRS shear orientation +/-1")
    return orientation*sig/math.sqrt(3-sig*sig)

@dataclass(frozen=True)
class InitialStress:
    Sigma_ref:float
    shear_orientation:int=1
    radiation_fraction:float=0.0
    radiation_A:float=0.0
    massive_matter_fraction:float=0.0
    massive_matter_A:float=0.0
    mass_over_Tref:float=30.0
    def __post_init__(self):
        s=radiation._read_lock()
        scalars=(self.Sigma_ref,self.radiation_fraction,self.radiation_A,
                 self.massive_matter_fraction,self.massive_matter_A,self.mass_over_Tref)
        if not all(math.isfinite(float(z)) for z in scalars):
            raise ValueError("finite physical initial family")
        if not (0<=self.Sigma_ref<=0.07):  # explicit bounded exploratory lane
            raise ValueError("0<=Sigma_ref<=0.07 exploratory source family")
        if self.shear_orientation not in (-1,1):
            raise ValueError("sign branch +/-1 required even for Sigma0")
        if not (0<=self.radiation_fraction<=1):
            raise ValueError("0<=radiation_fraction<=1 source Omega_r budget")
        if not(-1<=self.radiation_A<=2):
            raise ValueError("positive radiation W=1+A P2")
        if not(-1<=self.massive_matter_A<=2):
            raise ValueError("positive massive W=1+A P2")
        c=s["cosmology"]
        limit=(c["Omega_m"]-c["Omega_b"])/c["Omega_m"]
        if not(0<=self.massive_matter_fraction<=limit+1e-15):
            raise ValueError("massive component must be within nonbaryonic Omega_m budget")
        if not(3<=self.mass_over_Tref<=1.e5):
            raise ValueError("massive collisionless rest/thermal ratio physical bounded")
        if self.Sigma_ref==0 and self.shear_orientation==-1:
            raise ValueError("canonical zero shear orientation is +1")
    @classmethod
    def from_stress_ratios(cls,Sigma_ref,shear_orientation,
                           pi_r_over_total_r,pi_m_over_total_m,
                           radiation_fraction,massive_matter_fraction,
                           mass_over_Tref=30.,angular_n=32):
        """Construct independently requested initial pi_ref / total epsilon_ref.

        pi_r0 is the LRS coefficient in diag(-Pi,-Pi,2Pi), in J/m^3.
        Ratios are to the TOTAL original Omega_r and Omega_m budgets,
        rather than their collisionless portions.
        """
        rr=float(radiation_fraction)
        fm=float(massive_matter_fraction)
        mr=MassiveMoments(mass_over_Tref,angular_n=angular_n)
        v2=mr.initial_mean_v2
        if rr==0 and pi_r_over_total_r!=0:
            raise ValueError("nonzero radiation pi without kinetic radiation")
        if fm==0 and pi_m_over_total_m!=0:
            raise ValueError("nonzero matter pi without massive kinetic matter")
        Ar=15*pi_r_over_total_r/rr if rr else 0.
        Am=15*pi_m_over_total_m/(fm*v2) if fm else 0.
        return cls(Sigma_ref,shear_orientation,rr,Ar,fm,Am,mass_over_Tref)

class MassiveMoments:
    """Actual BASS FD q^2dq radial rule, analytic φ integral and GL μ quadrature.

    Q/DQ and FD come from the ORIGINAL bianchi/matter/freestream.py.
    The reference norm is integral q² fFD(q) E_ref(q)dq, so the kinetic
    fraction is an INITIAL ENERGY FRACTION, not a particle count fraction.
    """
    def __init__(self,mass_over_Tref=30.,angular_n=32):
        verify_source_bytes()
        m=float(mass_over_Tref)
        if not math.isfinite(m) or m<3 or m>1e5:raise ValueError("bounded massive ratio")
        if not isinstance(angular_n,int) or angular_n<8 or angular_n>256:
            raise ValueError("8<=number angular nodes<=256")
        self.mass=m
        self.q=np.array(bass_vlasov._Q,dtype=float)
        self.dq=np.array(bass_vlasov._DQ,dtype=float)
        self.rw=self.dq*self.q**2*bass_vlasov.f_fermi_dirac(self.q)
        self.er=np.hypot(m,self.q)
        self.norm=float(self.rw@self.er)
        self.initial_mean_v2=float(np.dot(self.rw,self.q**2/self.er)/self.norm)
        self.mu,self.w=leggauss(angular_n)
        self.w=self.w/2
        self.p2=(3*self.mu**2-1)/2
        self.n=angular_n
        if not(self.norm>0 and 0<self.initial_mean_v2<1):
            raise ArithmeticError("invalid source FD quadrature")
    def _calc(self,x,b,A):
        x=np.asarray(x,dtype=float)
        b=np.asarray(b,dtype=float)
        if x.shape!=b.shape or not np.isfinite(x).all() or not np.isfinite(b).all():
            raise ValueError("same shape finite logarithmic scale and b")
        if np.any(abs(b)>1) or not(-1<=A<=2):
            raise ValueError("source-bounded geometric chart and W>=0")
        # Shape: input_shape + (radial momentum, inclination).
        r=np.exp(-x)
        q2=np.square(r[...,None,None]*self.q[None,:,None])
        z=self.mu**2
        ep=np.exp(2*b)[...,None,None]
        ez=np.exp(-4*b)[...,None,None]
        pperp2=q2*ep*(1-z)/2
        ppar2=q2*ez*z
        E=np.sqrt(self.mass**2+2*pperp2+ppar2)
        weight=self.rw[:,None]*(1+A*self.p2[None,:])*self.w[None,:]
        w=weight/self.norm
        pref=r**3
        e= pref*np.sum(w*E,axis=(-2,-1))
        pp= pref*np.sum(w*pperp2/E,axis=(-2,-1))
        pa= pref*np.sum(w*ppar2/E,axis=(-2,-1))
        return e,pp,pa
    def evaluate(self,x,b,A=0.):
        values=self._calc(x,b,A)
        if np.asarray(x).ndim==0:
            return tuple(float(np.asarray(v).reshape(-1)[0]) for v in values)
        return values
    def batch_chunked(self,x,b,A=0.,chunk=128):
        x=np.atleast_1d(np.asarray(x,dtype=float))
        b=np.atleast_1d(np.asarray(b,dtype=float))
        if x.ndim!=1 or b.shape!=x.shape or not len(x):
            raise ValueError("finite nonempty batched x and b")
        if not isinstance(chunk,int) or chunk<1:
            raise ValueError("chunk positive")
        out=[np.empty_like(x) for _ in range(3)]
        for i in range(0,len(x),chunk):
            val=self.evaluate(x[i:i+chunk],b[i:i+chunk],A)
            for j in range(3):out[j][i:i+chunk]=val[j]
        return tuple(out)

class EinsteinVlasovSigmaMatter:
    def __init__(self,initial:InitialStress,angular_n=32,rtol=3e-12,atol=2e-14):
        verify_source_bytes()
        self.initial=initial
        self.source=radiation._read_lock()
        self.rad=radiation.Moments(angular_n)
        self.mass=MassiveMoments(initial.mass_over_Tref,angular_n=angular_n)
        c=self.source["cosmology"]
        self.H0=float(c["H0_per_s"]);self.om=float(c["Omega_m"])
        self.orad=float(c["Omega_r"]);self.ol=float(c["Omega_lambda"])
        self.ob=float(c["Omega_b"])
        self.aref=float(self.source["clock"]["a_ref"])
        self.aend=float(self.source["clock"]["a_end"])
        self.xmax=math.log(self.aend/self.aref)
        self.href=self.H0*math.sqrt(self.om/self.aref**3+self.orad/self.aref**4+self.ol)
        self.q_legacy_audit=signed_q_from_sigma(initial.Sigma_ref,initial.shear_orientation)
        self.sref=self.q_legacy_audit*self.href
        self.ematterref=self.H0**2*self.om*initial.massive_matter_fraction/self.aref**3
        self.eradfrac=self.H0**2*self.orad*initial.radiation_fraction
        self.dustfrac=self.H0**2*self.om*(1-initial.massive_matter_fraction)
        self.radioperf=self.H0**2*self.orad*(1-initial.radiation_fraction)
        self.lambda_term=self.H0**2*self.ol
        self.reference_nuclei=radiation.source_abundance_bg()
        if not(0<rtol<1e-8 and 0<atol<1e-10):
            raise ValueError("positive ODE tolerances")
        def rhs(x,Y):
            tau,b,u=Y
            S=self.href*u
            vals=self._source_terms(float(x),float(b),float(S))
            H=vals["H"]
            return [self.href/H,S/H,
                -3*u+(vals["source_shear_per_s2"]/(self.href*H))]
        y0=[0.0,0.0,self.sref/self.href]
        ode=solve_ivp(rhs,(0.,self.xmax),y0,method="DOP853",rtol=rtol,atol=atol,dense_output=True)
        if not ode.success or not np.isfinite(ode.y).all():
            raise ArithmeticError("COUPLED_MASSIVE_EINSTEIN_VLASOV_FAIL")
        self.sol=ode
        self.nfev=ode.nfev
    def _source_terms(self,x,b,s,chunk=128):
        a=self.aref*np.exp(x)
        u=np.asarray(x)
        M0r,Mdr,prperp,prpar=self.rad.evaluate(b,self.initial.radiation_A)
        Mr,pmperp,pmpar=self.mass.evaluate(x,b,self.initial.massive_matter_A) if np.asarray(x).ndim==0 else self.mass.batch_chunked(x,b,self.initial.massive_matter_A,chunk=chunk)
        Fr=self.eradfrac/a**4
        Fm=self.ematterref
        Fdust=self.dustfrac/a**3
        Frperfect=self.radioperf/a**4
        H2=Fdust+Frperfect+self.lambda_term+Fr*M0r+Fm*Mr+s*s
        H=np.sqrt(H2)
        delta_m=pmpar-pmperp
        source=Fr*Mdr+Fm*delta_m
        H2_flrw=self.H0**2*(self.om/a**3+self.orad/a**4+self.ol)
        return dict(H=H,H0_flrw=np.sqrt(H2_flrw),a=a,Fr=Fr,Fm=Fm,Fdust=Fdust,
            Frperfect=Frperfect,M0r=M0r,Mdr=Mdr,Mr=Mr,
            prperp=prperp,prpar=prpar,pmperp=pmperp,pmpar=pmpar,
            delta_m=delta_m,source_shear_per_s2=source)
    def at_x(self,x):
        x=np.asarray(x,dtype=float)
        if not np.isfinite(x).all() or np.any(x<0) or np.any(x>self.xmax):
            raise ValueError("outside source-locked REI logarithmic scale")
        tau,b,u=self.sol.sol(x)
        s=self.href*u
        val=self._source_terms(x,b,s)
        H=val["H"];a=val["a"]
        Fr,Fm=val["Fr"],val["Fm"]
        pi_r_scaled=Fr*val["Mdr"]/3
        pi_m_scaled=Fm*val["delta_m"]/3
        conv=3*C_SI**2/(8*math.pi*G_SI)
        pir=pi_r_scaled*conv
        pim=pi_m_scaled*conv
        dHdx=(-3*val["Fdust"]-4*val["Frperfect"]-4*Fr*val["M0r"]-
            3*Fm*(val["Mr"]+(2*val["pmperp"]+val["pmpar"])/3)-6*s*s)/(2*H)
        r=dict(x=x,a=a,zbar=1/a-1,proper_elapsed_s=tau/self.href,
            b=b,s_per_s=s,H_mean_per_s=H,
            H_FLRW_ref_per_s=val["H0_flrw"],signed_s_over_H=s/H,
            Sigma=np.sqrt(3)*abs(s)/H,
            a_perp=a*np.exp(-b),a_parallel=a*np.exp(2*b),
            H_perp_per_s=H-s,H_parallel_per_s=H+2*s,
            shear2_per_s2=3*s*s,
            radiation_kinetic_energy_J_m3=Fr*val["M0r"]*conv,
            radiation_pressure_perp_J_m3=Fr*val["prperp"]*conv,
            radiation_pressure_parallel_J_m3=Fr*val["prpar"]*conv,
            pi_r_perp_J_m3=-pir,pi_r_parallel_J_m3=2*pir,Pi_r_J_m3=pir,
            matter_kinetic_energy_J_m3=Fm*val["Mr"]*conv,
            matter_pressure_perp_J_m3=Fm*val["pmperp"]*conv,
            matter_pressure_parallel_J_m3=Fm*val["pmpar"]*conv,
            pi_m_perp_J_m3=-pim,pi_m_parallel_J_m3=2*pim,Pi_m_J_m3=pim,
            Pi_total_J_m3=pir+pim,
            n_H_cm3=self.reference_nuclei.nh0/a**3,
            n_He_cm3=self.reference_nuclei.nhe0/a**3,
            Tbar_CMB_K=self.reference_nuclei.t0/a,
            dt_dln_a_s=1/H,db_dln_a=s/H,
            ds_dln_a_per_s=-3*s+val["source_shear_per_s2"]/H,
            dH_dln_a_per_s=dHdx,
            constraint_rel=(H*H-(val["Fdust"]+val["Frperfect"]+self.lambda_term+Fr*val["M0r"]+Fm*val["Mr"]+s*s))/(H*H))
        if x.ndim==0:return {k:float(np.asarray(v)) for k,v in r.items()}
        return r
    def at_a(self,a):
        if not math.isfinite(float(a)) or a<self.aref or a>self.aend:
            raise ValueError("physical scale within REI source")
        if a==self.aref:return self.at_x(0.)
        if a==self.aend:return self.at_x(self.xmax)
        return self.at_x(math.log(float(a)/self.aref))
    def table(self,n=501):
        if not isinstance(n,int) or isinstance(n,bool) or n<3 or n>32769:
            raise ValueError("3..32769 source table points")
        return self.at_x(np.linspace(0,self.xmax,n))
    def initial_tensors(self):
        # This returns SI physical energy density and tracefree stress by species.
        p=self.at_x(0.)
        return {"Sigma_ref":self.initial.Sigma_ref,
            "shear_orientation":self.initial.shear_orientation,
            "legacy_q_ref_for_source_parity_only":self.q_legacy_audit,
            "massive_reference_velocity2_energyweighted":self.mass.initial_mean_v2,
            "initial_radiation_Pi_J_m3":p["Pi_r_J_m3"],
            "initial_matter_Pi_J_m3":p["Pi_m_J_m3"],
            "initial_radiation_pi_diag_J_m3":[-p["Pi_r_J_m3"],-p["Pi_r_J_m3"],2*p["Pi_r_J_m3"]],
            "initial_matter_pi_diag_J_m3":[-p["Pi_m_J_m3"],-p["Pi_m_J_m3"],2*p["Pi_m_J_m3"]],
            "initial_epsilon_r_kin_J_m3":p["radiation_kinetic_energy_J_m3"],
            "initial_epsilon_m_kin_J_m3":p["matter_kinetic_energy_J_m3"],
            "physical_source":"frozen AX03 Omega_m/Omega_r energy fractions, zero double counting"}
