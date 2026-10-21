#!/usr/bin/env python3
"""C13: REAL frozen MD14 stellar photon births + BASS Bianchi clock/Killing flow
+ C11 source Grackle Case-A H/He photoionization/recombination on one *short*
cosmological interval near zbar=4.

All astrophysical source amplitudes and spectral/angular cell moments are from
original rei_microphysics::axbi_sources; the continuous rate evaluates exactly
that frozen analytic source formula (cross-checked at all 17 native grid nodes).
No cosmic-history initial-condition claim; prescribed gas at a0 has been
constructed explicitly. The owner Einstein-sourced Sigma/pi branch is separate.

Metric (-,+,+,+): ds^2=-c^2dt^2+a^2 e^-2b(dx^2+dy^2)+a^2 e^4b dz^2.
Photons carry N per cosmic H nucleus (no angular J reweighting after pushforward).
Thermal gas is ideal nonrel isotropic under expansion (no pi_m evolution).
"""
from __future__ import annotations
from dataclasses import dataclass
import csv,hashlib,json,math,sys
from pathlib import Path

import numpy as np
from scipy.integrate import quad

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/"research/source07_c1_baseline_20261014"))
sys.path.insert(0,str(ROOT/"research/source07_c10_dynamic_20261015"))
sys.path.insert(0,str(ROOT/"research/source07_c11_casea_20261015"))
sys.path.insert(0,str(ROOT/"research/rei_crossrepo_integration_20261015/suppliers/bass/rei_axbi_shortstep_20261015"))
from q_emission_baseline import Scenario
import dynamic as c10
import casea as c11
from rate_table import CaseARates
from shortstep import Background,Family,gauss_increment,stable_dx
from supplier_sigma_pi_PR135 import (sigma_from_signed_axis, SigmaPiScenario, RadiationKillingGL, KAPPA)

THOMSON_CGS=6.6524587051e-25
EV_CM3_TO_PA=1.602176634e-13
C_CGS=29979245800.
START=0.1999
STOP=0.2


@dataclass(frozen=True)
class NativeStellarSource:
    energy:np.ndarray
    mu:np.ndarray
    weights:np.ndarray
    segments:int
    nang:int
    source_id:str
    nh0:float
    normalization_relative_residual:float
    tail_omitted_fraction:float
    grid_rate:np.ndarray
    source_sha256:str

    @classmethod
    def load(cls,model:Scenario,path):
        raw=Path(path).read_bytes()
        rows=list(csv.reader(raw.decode().splitlines()))
        header=[r for r in rows if r[0]=="META"]
        if len(header)!=1 or len(header[0])!=8:
            raise ValueError("NATIVE_SOURCE_META_SCHEMA")
        m=header[0]
        if m[1]!="MD14_Z002_FESC_BB50K_13P6_100_V1" or abs(float(m[3])-.2)>1e-15:
            raise ValueError("SOURCE_ID_OR_ESCAPE_FRACTION_CHANGED")
        nh=float(m[2])
        if abs(nh-model.nh)/model.nh>2e-14:
            raise ValueError("SOURCE_NH0_MISMATCH")
        seg=int(m[4]);numu=int(m[5])
        if seg not in (4,8,16,32) or numu not in (8,16,32):
            raise ValueError("UNSUPPORTED_NATIVE_SOURCE_RESOLUTION")
        spectra=np.asarray([[float(y) for y in r[2:]]
                            for r in rows if r[0]=="SPECTRUM"],dtype=float)
        angles=np.asarray([[float(y) for y in r[2:]]
                           for r in rows if r[0]=="ANGLE"],dtype=float)
        rates=np.asarray([[float(y) for y in r[1:]]
                          for r in rows if r[0]=="RATE"],dtype=float)
        if spectra.shape!=(3*seg,4) or angles.shape!=(numu,2) or rates.shape!=(17,4):
            raise ValueError("NATIVE_SOURCE_CELL_COUNTS")
        if (np.any(spectra[:,0]<=0) or np.any(spectra[:,1]<=spectra[:,0])
                or np.any(spectra[:,2]<spectra[:,0]) or np.any(spectra[:,2]>spectra[:,1])
                or np.any(spectra[:,3]<=0) or np.any(angles[:,1]<=0)
                or np.any(abs(angles[:,0])>=1)):
            raise ValueError("BAD_SOURCE_CELL_MOMENT_OR_DIRECTION")
        if abs(spectra[:,3].sum()-1)>1e-13 or abs(angles[:,1].sum()-1)>1e-13:
            raise ValueError("SOURCE_SPECTRAL_ANGULAR_NORM")
        if float(m[6])>1e-7 or not 0<=float(m[7])<1e-3:
            raise ValueError("NATIVE_SOURCE_NORMALIZATION")
        for z,p,proper,comoving in rates:
            a=1/(z+1)
            expected=model.rate(a)
            if abs(expected-p)/p>3e-14:
                raise ValueError(f"MD14_SOURCE_RATE_MISMATCH z={z}: {expected} {p}")
            if abs(proper/(model.nh/a**3)-p)/p>3e-14:
                raise ValueError("NATIVE_SOURCE_PROPER_NUMBER_CONVERSION")
            if not (p>0 and proper>0 and comoving>0):
                raise ValueError("NATIVE_SOURCE_NEGATIVE")
        Es=np.repeat(spectra[:,2],numu)
        mus=np.tile(angles[:,0],len(spectra))
        counts=np.repeat(spectra[:,3],numu)*np.tile(angles[:,1],len(spectra))
        assert abs(counts.sum()-1.)<1e-13
        return cls(Es,mus,counts,seg,numu,m[1],nh,float(m[6]),float(m[7]),rates,hashlib.sha256(raw).hexdigest())

    def birth(self,number_perH):
        if not (math.isfinite(number_perH) and number_perH>=0):
            raise ValueError("NONNEGATIVE_STELLAR_PHOTON_NUMBER")
        return PhotonCloud(self.energy.copy(),self.mu.copy(),self.weights*number_perH)


@dataclass
class PhotonCloud:
    E:np.ndarray
    mu:np.ndarray
    NperH:np.ndarray
    @classmethod
    def empty(cls):
        return cls(np.empty(0),np.empty(0),np.empty(0))
    def clone(self):
        return PhotonCloud(self.E.copy(),self.mu.copy(),self.NperH.copy())
    @property
    def number(self):
        return float(np.sum(self.NperH))
    @property
    def energy(self):
        return float(np.dot(self.NperH,self.E))
    @property
    def live_bytes(self):
        return sum(x.nbytes for x in (self.E,self.mu,self.NperH))
    @property
    def packet_count(self):
        return len(self.E)
    def check(self):
        if not (self.E.ndim==self.mu.ndim==self.NperH.ndim==1 and
                len(self.E)==len(self.mu)==len(self.NperH)):
            raise ValueError("PHOTON_CLOUD_SHAPE")
        if (not all(np.isfinite(z).all() for z in (self.E,self.mu,self.NperH))
              or np.any(self.E<=0) or np.any(abs(self.mu)>1) or np.any(self.NperH<0)):
            raise ValueError("INVALID_POSITIVE_KILLING_PHOTON_CLOUD")
    def inject(self,source:NativeStellarSource,number_perH):
        self.check()
        b=source.birth(number_perH)
        return PhotonCloud(np.concatenate([self.E,b.E]),
                           np.concatenate([self.mu,b.mu]),
                           np.concatenate([self.NperH,b.NperH]))
    def drift(self,delta_ln_a,delta_b):
        """Analytic fixed-Killing ray pushforward; no second angular Jacobian."""
        if not np.isfinite([delta_ln_a,delta_b]).all() or delta_ln_a<0:
            raise ValueError("INVALID_BIANCHI_GEOMETRY_INCREMENT")
        rm1=(1-self.mu**2)*math.expm1(2*delta_b)+(self.mu**2)*math.expm1(-4*delta_b)
        logD=.5*np.log1p(rm1)
        E=self.E*np.exp(-delta_ln_a+logD)
        mu=self.mu*np.exp(-2*delta_b-logD)
        mu=np.maximum(-1.,np.minimum(1.,mu))
        return PhotonCloud(E,mu,self.NperH.copy())
    def to_native_chemistry(self,nH_cm3):
        if nH_cm3<=0:raise ValueError("NEGATIVE_PROPER_H_NUCLEI")
        sigma=c10.c9.cross_sections(self.E)
        excess=np.maximum(self.E[:,None]-c10.c9.BIND[None,:],0.)
        return c10.Packets(self.E,sigma,sigma*excess,self.NperH*nH_cm3)
    def chemical_update(self,packets:c10.Packets,new_nH_cm3):
        if len(packets.E)!=len(self.E) or not np.array_equal(self.E,packets.E):
            raise ValueError("CHEMISTRY_CHANGED_KILLING_PACKET_GRID")
        return PhotonCloud(self.E.copy(),self.mu.copy(),packets.count/new_nH_cm3)


@dataclass
class SourceState:
    a:float
    gas:c10.Gas
    photons:PhotonCloud
    elapsed_s:float=0.
    source_N_perH:float=0.
    source_E_eV_perH:float=0.
    recomb_e_perH:float=0.
    escape_E_eV_perH:float=0.
    geometry_work_eV_perH:float=0.
    thomson_tau:float=0.

    def number_ledger(self):
        return (self.photons.number+self.gas.ne/self.gas.nH+
                self.recomb_e_perH-self.source_N_perH)
    def energy_ledger(self):
        return (self.photons.energy+(self.gas.thermal_eV_cm3+self.gas.binding_eV_cm3)/self.gas.nH
                +self.escape_E_eV_perH+self.geometry_work_eV_perH-self.source_E_eV_perH)
    def summary(self):
        photon_E=self.photons.NperH*self.photons.E
        u_rad=self.gas.nH*float(np.sum(photon_E))*EV_CM3_TO_PA
        p_parallel=self.gas.nH*float(np.dot(photon_E,self.photons.mu**2))*EV_CM3_TO_PA
        p_perp=.5*self.gas.nH*float(np.dot(photon_E,1-self.photons.mu**2))*EV_CM3_TO_PA
        if abs(p_parallel+2*p_perp-u_rad)>5e-13*max(u_rad,1e-40):
            raise c10.StepFailure("IONIZING_RADIATION_TRACE_FAILURE")
        pi_ion=p_parallel-p_perp
        return {"a":self.a,"zbar":1/self.a-1,"elapsed_s":self.elapsed_s,
                "ion_rad_energy_Pa":u_rad,"Pi_ion_Pa":pi_ion,
                "ion_shear_source_ds_dt_s2":KAPPA*pi_ion,
                "Sigma":float("nan"),"x_HII":self.gas.nHII/self.gas.nH,
                "x_HeII":self.gas.nHeII/self.gas.nHe,
                "x_HeIII":self.gas.nHeIII/self.gas.nHe,
                "x_e_perH":self.gas.ne/self.gas.nH,
                "Tgas_K":self.gas.temperature_K,
                "photon_N_perH":self.photons.number,
                "photon_U_eV_perH":self.photons.energy,
                "source_N_perH":self.source_N_perH,
                "source_E_eV_perH":self.source_E_eV_perH,
                "recomb_e_perH":self.recomb_e_perH,
                "escape_E_eV_perH":self.escape_E_eV_perH,
                "geometry_work_eV_perH":self.geometry_work_eV_perH,
                "thomson_tau":self.thomson_tau,
                "packet_count":self.photons.packet_count,
                "packet_live_bytes":self.photons.live_bytes,
                "number_ledger":self.number_ledger(),
                "energy_ledger":self.energy_ledger()}


def initial_gas(model:Scenario,a,temperature_K=12000):
    if not model.ar<=a<=.2:
        raise ValueError("SOURCE_INTERVAL_OUTSIDE_Z20_TO4")
    g=c10.Gas.initial(model,T0=temperature_K)
    scale=(.2/a)**3
    return c10.Gas(g.nH*scale,g.nHe*scale,g.nHI*scale,g.nHeI*scale,g.nHeII*scale,
                   g.thermal_eV_cm3*scale)


def drift_state(state:SourceState,a1:float,bg:Background):
    a0=state.a
    if not state.a<=a1<=.2 or a1<=0:
        raise ValueError("COSMO_SOURCE_INTERVAL_ORDER")
    if a1==a0:return state
    dt,db=gauss_increment(bg,a0,a1,order=4)
    dx=stable_dx(a0,a1)
    if dt<=0 or not np.isfinite([dt,db,dx]).all():
        raise ValueError("INVALID_PROPER_CLOCK")
    before_cloud_u=state.photons.energy
    before_thermal_perH=state.gas.thermal_eV_cm3/state.gas.nH
    newsky=state.photons.drift(dx,db)
    f=(a0/a1)**3
    g=state.gas
    updated_gas=c10.Gas(g.nH*f,g.nHe*f,g.nHI*f,g.nHeI*f,g.nHeII*f,
                        g.thermal_eV_cm3*f*(a0/a1)**2)
    updated_gas.check()
    after_thermal_perH=updated_gas.thermal_eV_cm3/updated_gas.nH
    work=(before_cloud_u-newsky.energy)+(before_thermal_perH-after_thermal_perH)
    if work< -1e-10*max(1.,before_cloud_u+before_thermal_perH):
        raise c10.StepFailure("UNPHYSICAL_NEGATIVE_GEOMETRY_WORK_ON_EXPANDING_CASE")
    return SourceState(a1,updated_gas,newsky,state.elapsed_s+dt,
           state.source_N_perH,state.source_E_eV_perH,
           state.recomb_e_perH,state.escape_E_eV_perH,
           state.geometry_work_eV_perH+work,state.thomson_tau)


def emit_half(state:SourceState,source:NativeStellarSource,rate_perH_s,half_dt_s):
    dN=rate_perH_s*half_dt_s
    if dN<0 or not math.isfinite(dN):
        raise ValueError("INVALID_MD14_EMISSIVITY")
    photons=state.photons.inject(source,dN)
    injected_U=dN*float(np.dot(source.energy,source.weights))
    return SourceState(state.a,state.gas,photons,state.elapsed_s,
             state.source_N_perH+dN,state.source_E_eV_perH+injected_U,
             state.recomb_e_perH,state.escape_E_eV_perH,
             state.geometry_work_eV_perH,state.thomson_tau)


def reaction_step(state:SourceState,dt:float,provider):
    g=state.gas
    p=state.photons.to_native_chemistry(g.nH)
    orig=c11.ReservoirState(g,p)
    nextstate,receipt=c11.strang_step(orig,dt,provider)
    updated_sky=state.photons.chemical_update(nextstate.photons,nextstate.gas.nH)
    newrec=state.recomb_e_perH+nextstate.recomb_electrons_cm3/g.nH
    newesc=state.escape_E_eV_perH+nextstate.escaped_eV_cm3/g.nH
    return SourceState(state.a,nextstate.gas,updated_sky,state.elapsed_s,
           state.source_N_perH,state.source_E_eV_perH,newrec,newesc,
           state.geometry_work_eV_perH,state.thomson_tau),receipt


def one_interval(state:SourceState,a_end:float,bg:Background,model:Scenario,
                 source:NativeStellarSource,provider:CaseARates,source_scale:float=1.):
    if not (state.a<a_end<=.2):
        raise ValueError("INVALID_MACRO_INTERVAL")
    a_mid=math.sqrt(state.a*a_end)
    dt_total,db=gauss_increment(bg,state.a,a_end,order=4)
    gas_ne_start=state.gas.ne
    mid=drift_state(state,a_mid,bg)
    if not (math.isfinite(source_scale) and source_scale>=0.):
        raise ValueError("NONNEGATIVE_MD14_SOURCE_SCALE")
    rate_mid=source_scale*model.rate(a_mid)
    injected=emit_half(mid,source,rate_mid,dt_total/2)
    reacted,events=reaction_step(injected,dt_total,provider)
    after_source=emit_half(reacted,source,rate_mid,dt_total/2)
    out=drift_state(after_source,a_end,bg)
    # Trapezoidal Thomson opacity of comoving observer on this proper interval.
    out.thomson_tau=state.thomson_tau+.5*C_CGS*THOMSON_CGS*dt_total*(gas_ne_start+out.gas.ne)
    if abs((out.elapsed_s-state.elapsed_s)-dt_total)/dt_total>3e-11:
        raise c10.StepFailure("CLOCK_HALFSTEP_COMPOSITION_MISMATCH")
    if abs(out.gas.nH-model.nh/a_end**3)/(model.nh/a_end**3)>5e-14:
        raise c10.StepFailure("GEOMETRY_DENSITY_SCALE_DRIFT")
    out.photons.check()
    if out.gas.temperature_K<provider.minT or out.gas.temperature_K>provider.maxT:
        raise c10.StepFailure("STELLAR_SOURCE_C11_RATE_T_DOMAIN_EXIT")
    return out,events


def run(q:float,source:NativeStellarSource,nstep=32,a_start=START,a_end=STOP,
        source_scale=1.,coalescence_budget=None):
    if q not in (0.,-.005,.005,-.01,.01) or nstep<1 or nstep>512:
        raise ValueError("LOCKED_SIGNED_SCENARIO_OR_STEP_RANGE")
    model=Scenario(ROOT)
    bg=Background(Family(q))
    provider=CaseARates()
    sigma_source=SigmaPiScenario.from_locked_json(ROOT/"research/axbi_goal_20261014/scenario/SCENARIO_LOCK.json")
    cmb_tensor=RadiationKillingGL(64)
    def attach_geometry_and_radiation(row,epoch):
        geo=bg.at_a(epoch)
        sig,orient=sigma_from_signed_axis(geo["shear_s_per_s"],geo["H_mean_per_s"])
        row["Sigma"]=sig
        row["shear_orientation"]=orient
        row["b_axis"]=geo["b"]
        row["Pi_CMB_source_Pa"]=(sigma_source.radiation_energy_ref*
             (sigma_source.a_ref/epoch)**4 * cmb_tensor.factors(geo["b"])[1])
        row["ion_Pi_to_CMB_energy_ratio"]=(abs(row["Pi_ion_Pa"])/
             (sigma_source.radiation_energy_ref*(sigma_source.a_ref/epoch)**4))
        return row
    g=initial_gas(model,a_start)
    if not(provider.minT<g.temperature_K<provider.maxT):
        raise ValueError("NOT_SUPPORTED_T")
    state=SourceState(a_start,g,PhotonCloud.empty())
    baseline_number=state.number_ledger()
    baseline_energy=state.energy_ledger()
    rows=[]
    r=state.summary()
    attach_geometry_and_radiation(r,state.a)
    rows.append(r)
    max_number=0.
    max_energy=0.
    max_packet=0
    compress_receipts=[]
    dx=stable_dx(a_start,a_end)/nstep
    for i in range(nstep):
        target=a_end if i==nstep-1 else a_start*math.exp((i+1)*dx)
        state,receipt=one_interval(state,target,bg,model,source,provider,source_scale)
        max_packet=max(max_packet,state.photons.packet_count)
        if coalescence_budget is not None and state.photons.number>0:
            from coalesce import reduce_age_cohorts
            # Single specified original source cell identity per array position.
            dt_for_gate=gauss_increment(bg,state.a,max(state.a,
                (a_end if i==nstep-1 else a_start*math.exp((i+2)*dx))),order=4)[0] if i<nstep-1 else gauss_increment(bg,a_start,target,order=4)[0]
            sky,accept=reduce_age_cohorts(state.photons,len(source.energy),state.gas,
                 dt_for_gate,event_budget=coalescence_budget[0],
                 heat_budget=coalescence_budget[1])
            state.photons=sky
            compress_receipts.append(accept)
        nerr=abs(state.number_ledger()-baseline_number)
        eerr=abs(state.energy_ledger()-baseline_energy)
        max_number=max(max_number,nerr)
        max_energy=max(max_energy,eerr)
        max_packet=max(max_packet,state.photons.packet_count)
        if nerr>1e-11 or eerr>1e-9:
            raise c10.StepFailure(f"C13_LOCAL_NUMBER_ENERGY_LEDGER_FAIL:{nerr},{eerr}")
        row=state.summary()
        attach_geometry_and_radiation(row,state.a)
        rows.append(row)
    dt=state.elapsed_s
    ref_source,quadrature_error=quad(
         lambda x: model.rate(math.exp(x))/model.hubble(math.exp(x),q),
         math.log(a_start),math.log(a_end),epsabs=2e-13,epsrel=2e-13)
    ref_source*=source_scale
    source_error=(abs(state.source_N_perH-ref_source)/ref_source
                  if ref_source>0 else abs(state.source_N_perH))
    return {"q":q,"a_range":[a_start,a_end],"nstep":nstep,"source_grid":[source.segments,source.nang],
            "source_scale_explicit_sensitivity":source_scale,
            "source_sha256":source.source_sha256,
            "sigma_pi_source_git_blob_sha1":"c1f8c351a04891085fb6cfdc7fcb2956fa97c8da",
            "model":"REI_AXBI_MD14_NATIVE_SOURCE_SHORT_C13",
            "assumption":"prescribed BASS stress-free q boundary; no UV ray scattering, no Einstein pi feedback; C11 Case A subset; initialized gas near z4",
            "source_direct_quadrature_perH":ref_source,"source_midpoint_relative_error":source_error,
            "max_number_abs_residual":max_number,"max_energy_eV_perH_residual":max_energy,
            "baseline_number":baseline_number,"baseline_energy_eV_perH":baseline_energy,
            "maximum_packets":max_packet,"end":rows[-1],"history":rows,
            "coalescence_attempts":len(compress_receipts),
            "coalescence_admitted_count":sum(x["merged"] for x in compress_receipts),
            "coalescence_holds":sum(not x["admitted"] for x in compress_receipts),
            "coalescence_max_event_abs_perH":max((x["max_event_abs_perH"] for x in compress_receipts),default=0.),
            "coalescence_max_heat_abs_eV_perH":max((x["max_heat_abs_eV_perH"] for x in compress_receipts),default=0.),
            "coalescence_budget":coalescence_budget}


def independent_scalar_killing(E,mu,da,db):
    d=math.hypot(math.sqrt(max(0.,1-mu*mu))*math.exp(db),
                 mu*math.exp(-2*db))
    return E*math.exp(-da)*d, mu*math.exp(-2*db)/d
