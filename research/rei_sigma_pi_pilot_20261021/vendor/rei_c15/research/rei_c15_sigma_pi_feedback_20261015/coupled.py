#!/usr/bin/env python3
"""C15 Einstein shear-stress backreaction on source-native C13 H/He cosmochemistry.

Actually integrates geometry b,s and PR137 photon/neutrino Boltzmann multipoles,
with exact positive BASS PR140 finite-mass source moments and C13 changing UV
photon/gas states in a bounded predictor-corrector short cosmic interval.
State input is Sigma=|sigma|/H and an independent axis orientation. Historical
q_ref is NOT a dynamics input. Here reference eta=0 is the explicit warm gas
a=.1999, NOT the original primordial a=1/21 BASS kinetic reference.

NOT full microscopic covariant radiative/matter Q^a energy-momentum closure:
MD14 stellar production is external, Case-A escape is energy-only, gamma
Thomson angular collision leaves out recoil/polarization, H/He gas isotropic,
the independent massive nonbaryonic component is collisionless. The pilot is
a genuinely computed stress-sourced Einstein metric, not a full EoR solution.
"""
from __future__ import annotations
from dataclasses import dataclass
from functools import lru_cache
import hashlib, json, math, sys, time
from pathlib import Path

import numpy as np
from scipy.integrate import solve_ivp
from scipy.linalg import expm

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/"research/rei_c13_live_source_20261015"))
sys.path.insert(0,str(ROOT/"research/rei_c14_thomson_receiver_20261015"))
import short_interval as c13
import dynamic_thomson as c14
# PR140 exactly original source; keep its actual dependencies as separate,
# deterministic module aliases, WITHOUT modifying owner code.
sys.modules.setdefault("lrs_boltzmann",sys.modules["vendor_pr137_lrs_boltzmann"] if "vendor_pr137_lrs_boltzmann" in sys.modules else __import__("vendor_pr137_lrs_boltzmann"))
import vendor_pr140_species_hierarchy as original_species
sys.modules.setdefault("species_hierarchy",original_species)
import vendor_pr140_massive_radial as pr140

C_SI=299792458.
G_SI=6.67430e-11
KAPPA=8*math.pi*G_SI/(3*C_SI*C_SI)
EV_CM3_TO_J_M3=1.602176634e-13
A_RAD=c14.A_RAD
START=c13.START
END=c13.STOP
SUPPORTED_MODELS=("direct_Vlasov_kinetic","no_massive_tracer")


@dataclass(frozen=True)
class Parameters:
    Sigma_initial:float
    orientation:int
    gamma_quadrupole:float=.2
    nu_quadrupole:float=.2
    massive_fraction:float=.1
    massive_quadrupole:float=.5
    massive_mass_over_T:float=30.
    L:int=8
    native_md14_source:bool=True
    enable_thomson:bool=True
    enable_primordial_pi:bool=True
    enable_matter_pi:bool=True
    enable_ionizing_pi:bool=True
    manufactured_ionizing_stress_scale:float=1.
    enable_C13_positive_coalescence:bool=True

    def __post_init__(self):
        vals=(self.Sigma_initial,self.gamma_quadrupole,self.nu_quadrupole,
              self.massive_fraction,self.massive_quadrupole,
              self.massive_mass_over_T,self.manufactured_ionizing_stress_scale)
        if (not all(math.isfinite(v) for v in vals)
            or not 0<=self.Sigma_initial<math.sqrt(3)
            or (self.Sigma_initial==0)!=(self.orientation==0)
            or self.orientation not in (-1,0,1)
            or not -1<=self.gamma_quadrupole<=2
            or not -1<=self.nu_quadrupole<=2
            or not 0<=self.massive_fraction<=.5
            or not -1<=self.massive_quadrupole<=2
            or not 3<=self.massive_mass_over_T<=1e5
            or self.L not in (4,8,12)
            or self.manufactured_ionizing_stress_scale<=0):
            raise ValueError("C15_SOURCE_SPECIFIC_POSITIVE_SIGMA_STRESS_DOMAIN")


@dataclass
class State:
    a:float
    b:float
    s:float
    H:float
    gas_and_UV:c13.SourceState
    moments:np.ndarray # shape 4 x (L+1): gamma(E,N), nu(E,N)

    def clone(self):
        st=self.gas_and_UV
        g=st.gas
        gc=c13.c10.Gas(g.nH,g.nHe,g.nHI,g.nHeI,g.nHeII,g.thermal_eV_cm3)
        cloned=c13.SourceState(st.a,gc,st.photons.clone(),st.elapsed_s,
              st.source_N_perH,st.source_E_eV_perH,st.recomb_e_perH,
              st.escape_E_eV_perH,st.geometry_work_eV_perH,st.thomson_tau)
        return State(self.a,self.b,self.s,self.H,cloned,self.moments.copy())


def source_identity():
    expected={"vendor_pr140_massive_radial.py":"0eec2880c9d0d5675938ad516e00039b994ba18a",
              "vendor_pr140_species_hierarchy.py":"cc5094ba28f1da371d50cb9a854d7460c2dcec3f"}
    for name,sha in expected.items():
        raw=(HERE/name).read_bytes()
        blob=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
        if sha!=blob:raise ValueError("ORIGINAL_PR140_MASSIVE_GIT_BLOB_DRIFT")
    src=c14.validate_source_sha()
    return {"PR140_original_massive_blobs":expected,"PR137_BASS_photon_blob":src["PR137_git_blob"],
            "C13_source":"MD14_Z002_FESC_BB50K_13P6_100_V1",
            "C11_source":"rei_microphysics::igm_rates/Grackle-3.4.1-CaseA"}


def initial_moments(params:Parameters):
    J=np.zeros((4,params.L+1),dtype=float)
    for i,k in enumerate((params.gamma_quadrupole,params.gamma_quadrupole,
                          params.nu_quadrupole,params.nu_quadrupole)):
        J[i,0]=1.
        J[i,2]=k/5.
    return J


def UV_moments_per_H(source_state:c13.SourceState):
    photons=source_state.photons
    power=photons.NperH*photons.E
    if not np.isfinite(power).all() or np.any(power<0):
        raise ValueError("UV_SOURCE_PHOTON_MOMENT_NEGATIVE")
    p2=.5*(3*photons.mu**2-1)
    return float(power.sum()),float(power@p2)


@dataclass(frozen=True)
class Proxy:
    start_ne_perH:float
    end_ne_perH:float
    start_ion_energy_eV_H:float
    end_ion_energy_eV_H:float
    start_ion_Pi_eV_H:float
    end_ion_Pi_eV_H:float
    start_gas_nonrest_eV_H:float
    end_gas_nonrest_eV_H:float

    @classmethod
    def from_states(cls,a:c13.SourceState,b:c13.SourceState):
        def f(st):
            ue,pi=UV_moments_per_H(st)
            return st.gas.ne/st.gas.nH,ue,pi,(
                   st.gas.thermal_eV_cm3+st.gas.binding_eV_cm3)/st.gas.nH
        aa=f(a);bb=f(b)
        return cls(aa[0],bb[0],aa[1],bb[1],aa[2],bb[2],
                   aa[3],bb[3])

    def evaluate(self,lam):
        z=min(1.,max(0.,float(lam)))
        return tuple((1-z)*p+z*q for p,q in zip(
         (self.start_ne_perH,self.start_ion_energy_eV_H,
          self.start_ion_Pi_eV_H,self.start_gas_nonrest_eV_H),
         (self.end_ne_perH,self.end_ion_energy_eV_H,
          self.end_ion_Pi_eV_H,self.end_gas_nonrest_eV_H)))


class EinsteinBoltzmann:
    def __init__(self,params:Parameters,a0=START,fast_massive=True,source_grid="8X8"):
        self.params=params
        if source_grid not in ("4X8","8X8","16X8","32X8","8X16"):
            raise ValueError("SOURCE_NATIVE_ENERGY_ANGLE_GRID")
        self.source_grid=source_grid
        self.fast_massive=bool(fast_massive)
        self.a0=float(a0)
        if not 0<self.a0<END:raise ValueError("SOURCE_INTERVAL")
        self.cosmo=c13.Scenario(ROOT)
        self.source=c13.NativeStellarSource.load(
           self.cosmo,ROOT/("research/rei_c13_live_source_20261015/"+
                             "NATIVE_SOURCE_"+source_grid+".csv"))
        self.owner=c13.CaseARates()
        self.H0_ref=self.cosmo.hf(a0)
        self.Om=self.cosmo.om
        self.Hubble0=self.cosmo.h0
        self.Ecrit=3*C_SI*C_SI*self.Hubble0**2/(8*math.pi*G_SI)
        self.source_omegas=c14.omega_gamma_fraction(self.cosmo)
        self.E_gamma0=self.Ecrit*self.source_omegas["Omega_gamma"]
        self.E_nu0=self.Ecrit*self.source_omegas["Omega_nu"]
        self.A_E,self.A_N,self.D=c14._cached_source_angular_operators(params.L)
        self.massive=pr140.MassiveRadialGrid(params.massive_mass_over_T,96,32)
        self.massive_weight=(self.massive.rw[:,None]/self.massive.norm)*(
            self.massive.wmu*(1+params.massive_quadrupole*self.massive.p2))[None,:]
        self.massive_q2=self.massive.q[:,None]**2
        if np.any(self.massive_weight<0):
            raise ValueError("SOURCE_BASS_MASSIVE_POSITIVE_VLASOV_WEIGHTS")
        # PR140 exact source-owned positive massive nonbaryonic component.
        Y=self.cosmo.data["cosmology"]["helium_mass_fraction"]
        ob=.0224/.674**2
        if params.massive_fraction*self.Om>self.Om-ob:
            raise ValueError("MASSIVE_MATTER_OVERLAPS_BARYON_BUDGET")
        self.mass_ref_density=self.Ecrit*self.Om*params.massive_fraction/a0**3
        self.iterations=0
        self.rhs_evals=0

    @staticmethod
    def legacy_reference_adapter(q_ref):
        """Historical pre-existing stress-free q, NOT a new model input."""
        if not math.isfinite(q_ref):
            raise ValueError("nonfinite historical q")
        return (math.sqrt(3)*abs(q_ref)/math.hypot(1,q_ref),
                (1 if q_ref>0 else -1 if q_ref<0 else 0))

    def initial(self):
        params=self.params
        gas=c13.initial_gas(self.cosmo,self.a0)
        sky=c13.PhotonCloud.empty()
        uv=c13.SourceState(self.a0,gas,sky)
        J=initial_moments(params)
        self.proxy=Proxy.from_states(uv,uv)
        base_fields=self._physical(0.,0.,0.,J,self.proxy,0.)
        Hbase=base_fields["H"]
        if params.Sigma_initial:
            H=Hbase/math.sqrt(1-params.Sigma_initial**2/3)
            s=params.orientation*params.Sigma_initial*H/math.sqrt(3)
        else:
            H=Hbase;s=0.
        st=State(self.a0,0.,s,H,uv,J)
        fields=self._physical(0.,0.,s/self.H0_ref,J,self.proxy,0.)
        if abs(fields["H"]-H)/H>4e-14:
            raise RuntimeError("INITIAL_EINSTEIN_HAMILTONIAN_SHEAR_CONSTRAINT")
        return st

    def massive_source_3moments(self,x,b):
        """Exactly PR140's FD momentum quadrature, restricted to Einstein-used
        J0^(0), J0^(1), J2^(0). No new kinetic closure or moment projection.
        Original vendor full J0/J2/J4 evaluator remains independent oracle.
        """
        if not (math.isfinite(x) and 0<=x<=4 and math.isfinite(b) and abs(b)<=1):
            raise ValueError("BASS_MASSIVE_SOURCE_DOMAIN")
        if not self.fast_massive:
            full=self.massive.moments(x,b,A=self.params.massive_quadrupole,imax=2)
            return float(full.j0[0]),float(full.j0[1]),float(full.j2[0])
        rr=math.exp(-x)
        perp=math.exp(2*b);parallel=math.exp(-4*b)
        R2=perp*(1-self.massive.mu2)+parallel*self.massive.mu2
        p2=(rr*rr)*self.massive_q2*R2[None,:]
        energy=np.sqrt(self.massive.mass**2+p2)
        v2=p2/(energy*energy)
        mu2=parallel*self.massive.mu2/R2
        weighted=(rr**3)*self.massive_weight*energy
        j0=float(np.sum(weighted))
        j1=float(np.sum(weighted*v2))
        j2=float(np.sum(weighted*v2*.5*(3*mu2-1)[None,:]))
        return j0,j1,j2

    def _physical(self,x,b,v,J,proxy,frac):
        a=self.a0*math.exp(x)
        params=self.params
        s=v*self.H0_ref
        J=np.asarray(J,dtype=float).reshape(4,params.L+1)
        gam=self.E_gamma0/a**4; nu=self.E_nu0/a**4
        E_gamma=gam*J[0,0]
        E_nu=nu*J[2,0]
        Pi_gamma=gam*J[0,2]
        Pi_nu=nu*J[2,2]
        ne_H,uion_H,piion_H,ugas_H=proxy.evaluate(frac)
        nh=self.cosmo.nh/a**3
        uion=nh*EV_CM3_TO_J_M3*uion_H
        piion=nh*EV_CM3_TO_J_M3*piion_H
        ugas=nh*EV_CM3_TO_J_M3*ugas_H
        # Original BASS PR140: collisionless massive component takes a
        # matched fraction out of original Omega_m rest energy, never adds it.
        if params.massive_fraction==0.:
            Em=Pim=0.
        else:
            j0,j1,j2=self.massive_source_3moments(x,b)
            Em=self.mass_ref_density*j0
            Pim=self.mass_ref_density*j2
            if Em<=0 or abs(Pim)>Em*(1+1e-12):
                raise FloatingPointError("MASSIVE_VLASOV_STRESS_ENERGY_CONE")
        drad=(E_gamma-gam)+(E_nu-nu)
        dmass=Em-self.Ecrit*self.Om*params.massive_fraction/a**3
        hsq=self.cosmo.hf(a)**2+s*s+KAPPA*(drad+dmass+uion+ugas)
        if not math.isfinite(hsq) or hsq<=0:
            raise FloatingPointError("NONPOSITIVE_EINSTEIN_HAMILTONIAN")
        H=math.sqrt(hsq)
        Pi_UV_scale=params.manufactured_ionizing_stress_scale if params.enable_ionizing_pi else 0.
        Pi_total=((Pi_gamma+Pi_nu) if params.enable_primordial_pi else 0.)+(
                  Pim if params.enable_matter_pi else 0.)+Pi_UV_scale*piion
        gamma=nh*ne_H*c13.C_CGS*c13.THOMSON_CGS if params.enable_thomson else 0.
        # Boundary scalars are fully source-identified, not q_ref.
        Sigma=math.sqrt(3)*abs(s)/H
        # A signed orientation must not be spuriously assigned to sub-roundoff
        # shear in exact-isotropic controls. Preserve s itself unmodified.
        resolved=Sigma>=3e-13
        axis_sign=(1 if s>0 else -1) if resolved else 0
        return {"a":a,"H":H,"s":s,"Sigma":Sigma,
                "orientation":axis_sign,
                "orientation_status":("RESOLVED" if resolved else
                    "NUMERICALLY_UNRESOLVED_BELOW_SIGMA_3E-13"),
                "Pi_gamma":Pi_gamma,"Pi_nu":Pi_nu,"Pi_massive":Pim,
                "Pi_ion":piion,"Pi_total_source":Pi_total,
                "E_gamma":E_gamma,"E_nu":E_nu,"E_massive":Em,
                "E_UV":uion,"E_gas":ugas,
                "delta_radiation":drad,"delta_massive":dmass,
                "H_constraint_residual":H*H-hsq,
                "gamma_T_per_s":gamma,
                "n_e_cm3":nh*ne_H}

    def rhs(self,x,y,proxy,x_start,x_end):
        L=self.params.L;N=L+1
        b,v,clock=y[:3]
        J=y[3:].reshape(4,N)
        frac=(x-x_start)/(x_end-x_start)
        f=self._physical(x,b,v,J,proxy,frac)
        H=f["H"];s=f["s"]
        k=s/H
        g=f["gamma_T_per_s"]/H
        de=k*(self.A_E@J[0])-g*self.D*J[0]
        dn=k*(self.A_N@J[1])-g*self.D*J[1]
        dve=k*(self.A_E@J[2])
        dvn=k*(self.A_N@J[3])
        # Actual physical Einstein d(s)/dt + 3 H s = kappa Pi_total.
        dsv=-3*v+KAPPA*f["Pi_total_source"]/(H*self.H0_ref)
        self.rhs_evals+=1
        return np.r_[k,dsv,self.H0_ref/H,de,dn,dve,dvn]

    def _geom(self,st:State,a_end,proxy):
        x0=math.log(st.a/self.a0);x1=math.log(a_end/self.a0)
        y0=np.r_[st.b,st.s/self.H0_ref,0.,st.moments.ravel()]
        atol=np.r_[1e-15,1e-15,1e-12,np.full(len(y0)-3,8e-14)]
        sol=solve_ivp(lambda x,y:self.rhs(x,y,proxy,x0,x1),(x0,x1),y0,
                      method="DOP853",dense_output=True,
                      rtol=3e-11,atol=atol,max_step=0.001)
        if not sol.success or not np.isfinite(sol.y).all():
            raise RuntimeError("EINSTEIN_BASS_STRESS_HIERARCHY_DOP853_FAILURE")
        self.iterations+=1
        return sol

    def _push_expansion(self,uv:c13.SourceState,a_end,dt,db):
        a0=uv.a
        if not (a0<=a_end<=END and dt>=0 and math.isfinite(db)):
            raise ValueError("EXPANSION_STEP_BOUNDARY")
        if a_end==a0:return uv
        f=(a0/a_end)**3
        g=uv.gas
        newgas=c13.c10.Gas(g.nH*f,g.nHe*f,g.nHI*f,g.nHeI*f,g.nHeII*f,
                           g.thermal_eV_cm3*f*(a0/a_end)**2)
        newgas.check()
        sky=uv.photons.drift(c13.stable_dx(a0,a_end),db)
        dwork=(uv.photons.energy-sky.energy)+(
                g.thermal_eV_cm3/g.nH-newgas.thermal_eV_cm3/newgas.nH)
        return c13.SourceState(a_end,newgas,sky,uv.elapsed_s+dt,
            uv.source_N_perH,uv.source_E_eV_perH,
            uv.recomb_e_perH,uv.escape_E_eV_perH,
            uv.geometry_work_eV_perH+dwork,uv.thomson_tau)

    def _chem(self,st:State,a_end,sol,*,compress=True):
        x0=math.log(st.a/self.a0);x1=math.log(a_end/self.a0)
        y0=sol.sol(x0);ym=sol.sol((x0+x1)/2);ye=sol.sol(x1)
        am=math.sqrt(st.a*a_end)
        t1=ym[2]/self.H0_ref;t2=(ye[2]-ym[2])/self.H0_ref
        if not (t1>0 and t2>0):raise RuntimeError("C15_POSITIVE_PROPER_EPOCH")
        first=self._push_expansion(st.gas_and_UV,am,t1,float(ym[0]-y0[0]))
        # Actual native original source, same log-time midpoint, two halves.
        rate=(self.cosmo.rate(am) if self.params.native_md14_source else 0.)
        src=c13.emit_half(first,self.source,rate,(t1+t2)/2)
        reacted,ev=c13.reaction_step(src,t1+t2,self.owner)
        twice=c13.emit_half(reacted,self.source,rate,(t1+t2)/2)
        after=self._push_expansion(twice,a_end,t2,float(ye[0]-ym[0]))
        tau_delta=(t1+t2)*c13.C_CGS*c13.THOMSON_CGS*(
                   st.gas_and_UV.gas.ne+after.gas.ne)/2
        after.thomson_tau=st.gas_and_UV.thomson_tau+tau_delta
        if compress and after.photons.number>0:
            from coalesce import reduce_age_cohorts
            if len(after.photons.E)%len(self.source.energy)==0:
                after.photons,receipt=reduce_age_cohorts(
                  after.photons,len(self.source.energy),after.gas,
                  max(t1+t2,1.),event_budget=1e-12,heat_budget=1e-11)
            else:receipt={"admitted":False,"merged":False}
        else:receipt={"admitted":False,"merged":False}
        return after,receipt

    def step(self,st:State,a_end,feedback=True,compress=True):
        if not st.a<a_end<=END:raise ValueError("POSITIVE_C15_EXPANSION_INTERVAL")
        beforeN=st.gas_and_UV.number_ledger()
        beforeE=st.gas_and_UV.energy_ledger()
        guess=Proxy.from_states(st.gas_and_UV,st.gas_and_UV)
        candidate=None
        # Causal coupled predictor + corrected endpoint; fixed one-step source
        # and gas/UV geometry solved at same BASS/Einstein clock. No full
        # step reinitialization under a changed prior snapshot.
        repeats=2 if feedback else 1
        for it in range(repeats):
            sol=self._geom(st,a_end,guess)
            candidate,receipt=self._chem(st,a_end,sol,compress=compress)
            if feedback:guess=Proxy.from_states(st.gas_and_UV,candidate)
        final=sol.y[:,-1]
        b=float(final[0]);s=float(final[1]*self.H0_ref)
        J=final[3:].reshape(4,self.params.L+1)
        f=self._physical(math.log(a_end/self.a0),b,s/self.H0_ref,J,
                         Proxy.from_states(candidate,candidate),1.)
        nxt=State(a_end,b,s,f["H"],candidate,J)
        nerr=abs(candidate.number_ledger()-beforeN)
        eerr=abs(candidate.energy_ledger()-beforeE)
        if nerr>5e-12 or eerr>5e-11:
            raise RuntimeError(f"C15_GAS_PHOTON_LEDGER_BROKEN {nerr} {eerr}")
        for v in J[[1,3],0]:
            if abs(v-1)>3e-9:raise RuntimeError("NUMBER_MONOPOLE_NOT_CONSERVED")
        r={"nerr":nerr,"eerr":eerr,"Pi_total_source":f["Pi_total_source"],
           "source":"PR140_BASS_massive_PR137_gamma_nu_and_C13_ionizing",
           "H":f["H"],"Pi_gamma":f["Pi_gamma"],"Pi_nu":f["Pi_nu"],
           "Pi_massive":f["Pi_massive"],"Pi_UV":f["Pi_ion"],
           "Sigma":f["Sigma"],"orientation":f["orientation"],
           "orientation_status":f["orientation_status"],
           "gamma_J2":float(J[0,2]),"nu_J2":float(J[2,2]),
           "x_HII":candidate.gas.nHII/candidate.gas.nH,
           "x_HeII":candidate.gas.nHeII/candidate.gas.nHe,
           "Tgas_K":candidate.gas.temperature_K,
           "remaining_UV_photons_perH":candidate.photons.number,
           "source_photons_perH":candidate.source_N_perH,
           "UV_packets":candidate.photons.packet_count,
           "collision_tau":candidate.thomson_tau,
           "gamma_number_N0":float(J[1,0]),
           "nu_number_N0":float(J[3,0]),
           "compress_admitted":receipt.get("admitted",False),
           "Hamiltonian_source_J_m3":{
               "gamma":f["E_gamma"],"nu":f["E_nu"],
               "massive":f["E_massive"],
               "ionizing":f["E_UV"],"chemical_gas":f["E_gas"]},
           "model_scope":"near-z4 native MD14 born; Einstein s/H/b and BASS l2 Gamma/nu + Vlasov matter feedback active; stellar source emitter global Q^a and full EoR NOT closed"}
        return nxt,r

    def run(self,nsteps=32,compress=True,feedback=True):
        if not 2<=nsteps<=1024:
            raise ValueError("C15_STEPS_SUPPORTED")
        st=self.initial()
        baseline=(st.gas_and_UV.number_ledger(),st.gas_and_UV.energy_ledger())
        rows=[]
        dx=c13.stable_dx(st.a,END)/nsteps
        for i in range(nsteps):
            target=END if i==nsteps-1 else self.a0*math.exp((i+1)*dx)
            st,r=self.step(st,target,feedback,compress)
            r.update({"a":st.a,"elapsed_s":st.gas_and_UV.elapsed_s,
                      "b":st.b,"s_inv_s":st.s,"Sigma_init":self.params.Sigma_initial})
            rows.append(r)
        errors={"photochemical_number_abs_max":max(r["nerr"] for r in rows),
                "photochemical_energy_eV_H_abs_max":max(r["eerr"] for r in rows),
                "gamma_number_monopole_abs_max":max(abs(r["gamma_number_N0"]-1) for r in rows),
                "nu_number_monopole_abs_max":max(abs(r["nu_number_N0"]-1) for r in rows)}
        return {"schema":"rei.c15.active_source_shear_stress_coupling.v1",
                "config":dict(self.params.__dict__),
                "nsteps":nsteps,
                "source_identity":source_identity(),
                "scope":"Einstein sourced Sigma/shear active PR137 gamma-nu Thomson, original PR140 positive massive Vlasov, C13 MD14 H-He Case A UV Pi, short near-z4",
                "initial_constraints":baseline,"final":rows[-1],
                "history":rows,"errors":errors,
                "rhs_evaluations":self.rhs_evals,
                "geometry_integrations":self.iterations}
