#!/usr/bin/env python3
"""SOURCE07 C10: source-age compression challenged by evolving H/He photon sinks.

A bounded source-conditioned test of a photoionization-only subproblem:
* Old emitted cohorts are free-streamed to a *single* receiver a=0.2.
* The received photon packets are then absorbed during a short fixed-geometry proper
  interval. No new emission, H/He recombination, collisional rates, cooling or
  expansion/redshift within the local interval. This is NOT AX08 production RT.
* Photon+binding+thermal energy and H/He/charge are conserved by construction.

Numbers in cm^-3, seconds, energies eV, temperature K, (-,+,+,+) background.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import math
import sys
from pathlib import Path
from time import perf_counter

import numpy as np

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"research/source07_c9_heii_vector_20261015"))
import experiment as c9

KB_EV_K=8.617333262145e-5
DEFAULT_INTERVAL_S=2.0e10
DEFAULT_PHOTONS_PER_H=.35

@dataclass
class Gas:
    """Neutral and HeII proper gas densities; all other species follow invariants."""
    nH: float
    nHe: float
    nHI: float
    nHeI: float
    nHeII: float
    thermal_eV_cm3: float

    @classmethod
    def initial(cls,model:c9.Scenario,T0:float=12000.):
        nH=model.nh*5.**3
        nHe=nH*.2454/(4.*(1.-.2454))
        nHI=.60*nH
        nHeI=.20*nHe
        nHeII=.50*nHe
        ne=(nH-nHI)+nHeII+2*(nHe-nHeI-nHeII)
        u=1.5*KB_EV_K*T0*(nH+nHe+ne)
        return cls(nH,nHe,nHI,nHeI,nHeII,u)

    @property
    def neutral(self):
        return np.array([self.nHI,self.nHeI,self.nHeII],dtype=float)

    @property
    def nHII(self):
        return self.nH-self.nHI

    @property
    def nHeIII(self):
        return self.nHe-self.nHeI-self.nHeII

    @property
    def ne(self):
        return self.nHII+self.nHeII+2*self.nHeIII

    @property
    def temperature_K(self):
        return self.thermal_eV_cm3/(1.5*KB_EV_K*(self.nH+self.nHe+self.ne))

    @property
    def binding_eV_cm3(self):
        return (c9.BIND[0]*self.nHII+c9.BIND[1]*(self.nHeII+self.nHeIII)
                +c9.BIND[2]*self.nHeIII)

    def check(self):
        numbers=[self.nH,self.nHe,self.nHI,self.nHeI,self.nHeII,
                 self.nHeIII,self.nHII,self.ne,self.thermal_eV_cm3,
                 self.temperature_K]
        if not all(math.isfinite(x) for x in numbers) or min(numbers)<-1e-14:
            raise StepFailure("unphysical gas")
        if self.nHI>self.nH*(1+1e-13) or self.nHeI+self.nHeII>self.nHe*(1+1e-13):
            raise StepFailure("ion simplex violated")


@dataclass
class Packets:
    E: np.ndarray
    sigma: np.ndarray
    sigma_heat: np.ndarray
    count: np.ndarray
    def clone(self):
        return Packets(self.E,self.sigma,self.sigma_heat,self.count.copy())
    @property
    def n(self):
        return float(self.count.sum())
    @property
    def u(self):
        return float(self.count @ self.E)
    @property
    def bytes(self):
        return sum(x.nbytes for x in (self.E,self.sigma,self.sigma_heat,self.count))


class StepFailure(Exception):
    pass


def to_packets(cohorts:list[tuple],ages_weight:np.ndarray,gas:Gas,
               photons_per_H:float=DEFAULT_PHOTONS_PER_H)->Packets:
    if len(cohorts)!=len(ages_weight) or np.any(ages_weight<0.) or not np.isfinite(ages_weight).all():
        raise ValueError("invalid positive age weights")
    idx=np.flatnonzero(ages_weight>1e-12)
    if len(idx)==0:
        raise ValueError("empty positive compression")
    energy=np.concatenate([cohorts[k][0] for k in idx])
    sigma=np.concatenate([cohorts[k][2] for k in idx],axis=0)
    sigheat=np.concatenate([cohorts[k][3] for k in idx],axis=0)
    # Convert normalized photons-per-H to proper cm^-3 in a static receiver.
    photons=np.concatenate([cohorts[k][1]*ages_weight[k]*gas.nH*photons_per_H
                            for k in idx])
    if np.any(photons<0) or not np.isfinite(photons).all():
        raise ValueError("invalid input photons")
    return Packets(energy,sigma,sigheat,photons)


def reactions_vector(pop:np.ndarray, energy:np.ndarray,sigma:np.ndarray,
                     sigma_heat:np.ndarray, neutral:np.ndarray,dt:float):
    tau=(c9.C_CGS*dt)*(sigma@neutral)
    if np.any(tau<0.) or not np.isfinite(tau).all():
        raise StepFailure("negative/invalid optical depth")
    factor=np.ones_like(tau)
    np.divide(-np.expm1(-tau),tau,out=factor,where=tau>0.)
    mass_flux=pop*factor
    events=(c9.C_CGS*dt)*(mass_flux@sigma)*neutral
    heat=(c9.C_CGS*dt)*float((mass_flux@sigma_heat)@neutral)
    absorbed=pop*(-np.expm1(-tau))
    surviving=pop*np.exp(-tau)
    photon_energy_abs=float(absorbed@energy)
    return events,heat,photon_energy_abs,surviving,float(absorbed.sum())


def reactions_scalar(pop,energy,sigma,neutral,dt):
    """Independent direct loop, not using the vectorized kernel."""
    absorbed=np.zeros(3,dtype=float)
    heat=0.
    photon_energy=0.
    count=0.
    for i,e in enumerate(energy):
        rates=c9.C_CGS*neutral*sigma[i]
        total=float(rates.sum())
        if total==0.:
            continue
        P=-math.expm1(-dt*total)
        ph=pop[i]*P
        count+=ph
        photon_energy+=ph*e
        for j in range(3):
            event=ph*rates[j]/total
            absorbed[j]+=event
            heat+=event*(e-c9.BIND[j])
    return absorbed,heat,photon_energy,count


def midpoint_step(gas:Gas, photons:Packets,dt:float):
    """Implicit-midpoint opacity, exact exponential attenuation at frozen midpoint.

    This is a second-order candidate for smooth gas evolution, not an exact
    nonlinear coupled thermochemistry integrator. Every accepted discrete step
    has exact event/energy ownership and a positive admissible state.
    """
    if not (math.isfinite(dt) and dt>0):
        raise ValueError("dt must be positive")
    neutral0=gas.neutral
    mid=neutral0.copy()
    scale=np.array([gas.nH,gas.nHe,gas.nHe])
    for it in range(48):
        events,heat,dEg,after,absorbed=reactions_vector(
            photons.count,photons.E,photons.sigma,photons.sigma_heat,mid,dt)
        end=neutral0+np.array([-events[0],-events[1],events[1]-events[2]])
        if end[0]<-1e-13*gas.nH or end[1]<-1e-13*gas.nHe or end[2]<-1e-13*gas.nHe:
            raise StepFailure("trial absorbed more atoms than available")
        if end[1]+end[2]>gas.nHe*(1+1e-12):
            raise StepFailure("trial HeII+HeI exceeds helium")
        next_mid=.5*(neutral0+end)
        if np.max(np.abs(next_mid-mid)/scale)<2e-13:
            mid=next_mid
            break
        mid=next_mid
    else:
        raise StepFailure("midpoint fixed point not converged")
    # Use exactly the converged midpoint in both gas and photon updates.
    events,heat,dEg,after,absorbed=reactions_vector(
        photons.count,photons.E,photons.sigma,photons.sigma_heat,mid,dt)
    end=neutral0+np.array([-events[0],-events[1],events[1]-events[2]])
    newgas=Gas(gas.nH,gas.nHe,float(end[0]),float(end[1]),float(end[2]),
               gas.thermal_eV_cm3+heat)
    newgas.check()
    photon_conservation=absorbed-float(events.sum())
    energy_conservation=dEg-heat-float(events@c9.BIND)
    if abs(photon_conservation)>1e-11*max(photons.n,gas.nH*1e-8):
        raise StepFailure("photon allocation ledger failure")
    if abs(energy_conservation)>1e-11*max(photons.u,gas.nH*1e-8):
        raise StepFailure("photon heat/binding ledger failure")
    newpop=Packets(photons.E,photons.sigma,photons.sigma_heat,after)
    return newgas,newpop,{"photons_abs_cm3":absorbed,"species_events_cm3":events.tolist(),
                          "heat_eV_cm3":heat,"fixedpoint_iterations":it+1,
                          "number_residual_cm3":photon_conservation,
                          "energy_residual_eV_cm3":energy_conservation}


def observables(time:float,gas:Gas,photons:Packets)->dict:
    return {"time_s":float(time),"x_HII":float(gas.nHII/gas.nH),
            "x_HeII":float(gas.nHeII/gas.nHe),
            "x_HeIII":float(gas.nHeIII/gas.nHe),
            "xe_per_H":float(gas.ne/gas.nH),
            "Tgas_K":float(gas.temperature_K),
            "photon_N_per_H":float(photons.n/gas.nH),
            "photon_U_eV_per_H":float(photons.u/gas.nH),
            "thermal_eV_per_H":float(gas.thermal_eV_cm3/gas.nH),
            "binding_eV_per_H":float(gas.binding_eV_cm3/gas.nH)}


def propagate(packets:Packets,gas:Gas,nsteps:int=16,
              interval:float=DEFAULT_INTERVAL_S)->dict:
    """Fixed reporting grid with positive half-step rejection fallback."""
    if nsteps<1 or not math.isfinite(interval) or interval<=0.:
        raise ValueError("invalid grid")
    photons=packets.clone()
    start=observables(0,gas,photons)
    conserved_energy=(photons.u+gas.thermal_eV_cm3+gas.binding_eV_cm3)
    conserved_count=photons.n+gas.ne
    history=[start]
    max_e=0.
    max_n=0.
    total_substeps=0
    total_reject=0
    for k in range(nsteps):
        nominal=interval/nsteps
        remaining=nominal
        # At most a small number of monotone independent subdivisions.
        while remaining>1e-12*nominal:
            candidate=remaining
            for _ in range(16):
                try:
                    nextgas,nextphot,receipt=midpoint_step(gas,photons,candidate)
                    gas,photons=nextgas,nextphot
                    max_e=max(max_e,abs(photons.u+gas.thermal_eV_cm3+
                                        gas.binding_eV_cm3-conserved_energy))
                    max_n=max(max_n,abs(photons.n+gas.ne-conserved_count))
                    remaining-=candidate
                    total_substeps+=1
                    break
                except StepFailure:
                    candidate*=.5
                    total_reject+=1
            else:
                raise StepFailure("substep reject ceiling reached")
            if total_substeps>4000:
                raise StepFailure("too many microsteps")
        history.append(observables((k+1)*nominal,gas,photons))
    return {"history":history,"substeps":total_substeps,"rejections":total_reject,
            "max_total_energy_rel_residual":max_e/max(abs(conserved_energy),1e-30),
            "max_photon_plus_electron_rel_residual":max_n/max(abs(conserved_count),1e-30),
            "final":history[-1],"initial":start,"stored_energy_bins":len(photons.E),
            "packet_bytes":packets.bytes}


METRICS=("x_HII","x_HeII","x_HeIII","Tgas_K","photon_N_per_H",
         "photon_U_eV_per_H","thermal_eV_per_H","binding_eV_per_H")

def compare(reference:dict,target:dict)->dict:
    r=reference["history"]; t=target["history"]
    assert len(r)==len(t)
    for x,y in zip(r,t):
        assert x["time_s"]==y["time_s"]
    return {key:{"max_abs":float(max(abs(a[key]-b[key]) for a,b in zip(r,t))),
                 "endpoint_abs":float(abs(r[-1][key]-t[-1][key]))}
            for key in METRICS}


def weights_from_design(row:dict,nages:int)->np.ndarray:
    assert row["status"]=="SOLVED",row
    w=np.zeros(nages)
    for k,weight in row["weights"]:
        w[k]=weight
    assert abs(w.sum()-1.)<1e-7 and np.min(w)>=0
    return w


def one_run(q:float,spectrum:str="bb50k",nsteps:int=16,
            nmu:int=12,ne:int=16,photons_per_H:float=DEFAULT_PHOTONS_PER_H,
            interval_s:float=DEFAULT_INTERVAL_S):
    model=c9.Scenario(ROOT)
    initial=Gas.initial(model)
    ages=np.geomspace(model.ar,.2,c9.AGE_COUNT)
    if spectrum=="bb50k":
        source=c9.Spectrum()
    elif spectrum=="hard":
        from benchmark import HardSource
        source=HardSource()
    else:
        raise ValueError("unknown spectrum")
    t0=perf_counter()
    cohorts=c9.build_packets(model,source,ages,q,n_mu=nmu,n_energy=ne)
    training,holds=c9.gas_states(model)
    original=c9.source_age_weights(model,ages,q)
    responses=c9.evaluate_packets(cohorts,np.vstack((training,holds)))
    fits={kind:c9.design(responses,original,int(kind),len(training))
          for kind in ("1","5")}
    prep=perf_counter()-t0

    t1=perf_counter()
    raw=propagate(to_packets(cohorts,original,initial,photons_per_H),initial,nsteps,interval_s)
    raw_time=perf_counter()-t1
    alternatives={}
    for kind,row in fits.items():
        weights=weights_from_design(row,len(ages))
        t1=perf_counter()
        sim=propagate(to_packets(cohorts,weights,initial,photons_per_H),initial,nsteps,interval_s)
        runtime=perf_counter()-t1
        alternatives["frozen_train_"+kind]={
            "age_count":row["retained"],"training_max_rel_error":row["training_max_rel_error"],
            "initial_static_holdout_max_rel_error":row["holdout_max_rel_error"],
            "elapsed_integration_s":runtime,"dynamic_disagreement":compare(raw,sim),
            "simulation":sim}
    # ***Oracle-only*** trajectory-conditioned age optimization. Not deployable.
    # It knows gas states in the reference future and is a scientific upper baseline.
    indexes=np.linspace(0,len(raw["history"])-1,5).round().astype(int)
    orbit_states=np.array([[initial.nH*(1.-h["x_HII"]),
                            initial.nHe*(1.-h["x_HeII"]-h["x_HeIII"]),
                            initial.nHe*h["x_HeII"]]
                           for h in [raw["history"][k] for k in indexes]])
    values=c9.evaluate_packets(cohorts,np.vstack((orbit_states,holds)))
    pathfit=c9.design(values,original,5,len(orbit_states))
    pathw=weights_from_design(pathfit,len(ages))
    t1=perf_counter()
    pathsim=propagate(to_packets(cohorts,pathw,initial,photons_per_H),initial,nsteps,interval_s)
    alternatives["oracle_future_path"]={
        "age_count":pathfit["retained"],"elapsed_integration_s":perf_counter()-t1,
        "initial_static_holdout_max_rel_error":pathfit["holdout_max_rel_error"],
        "dynamic_disagreement":compare(raw,pathsim),"simulation":pathsim}
    return {"q":q,"source":spectrum,"nsteps":nsteps,"nmu":nmu,"ne":ne,
            "photons_per_H":photons_per_H,"interval_s":interval_s,
            "H_interval":model.hubble(.2,q)*interval_s,
            "prep_seconds":prep,"dense_runtime_s":raw_time,"dense":raw,
            "alternatives":alternatives}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--q",type=float,default=0.)
    p.add_argument("--spectrum",choices=["bb50k","hard"],default="bb50k")
    p.add_argument("--nsteps",type=int,default=16)
    p.add_argument("--interval-s",type=float,default=DEFAULT_INTERVAL_S)
    p.add_argument("--photons-per-H",type=float,default=DEFAULT_PHOTONS_PER_H)
    p.add_argument("--nmu",type=int,default=12)
    p.add_argument("--ne",type=int,default=16)
    p.add_argument("--output",type=Path,default=Path(__file__).with_name("pilot.json"))
    args=p.parse_args()
    r=one_run(args.q,args.spectrum,args.nsteps,args.nmu,args.ne,
              args.photons_per_H,args.interval_s)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(r,indent=2)+"\n")
    print("BASE",r["source"],r["q"],"xHII",r["dense"]["final"]["x_HII"],
          "T",r["dense"]["final"]["Tgas_K"],
          "Nph",r["dense"]["final"]["photon_N_per_H"])
    for k,v in r["alternatives"].items():
        print(k,"age",v["age_count"],
              "dTmax",v["dynamic_disagreement"]["Tgas_K"]["max_abs"],
              "dxHmax",v["dynamic_disagreement"]["x_HII"]["max_abs"],
              "dHeIImax",v["dynamic_disagreement"]["x_HeII"]["max_abs"])
    print("ledger",r["dense"]["max_total_energy_rel_residual"],
          r["dense"]["max_photon_plus_electron_rel_residual"])


if __name__=="__main__":
    main()
