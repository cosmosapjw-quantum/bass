#!/usr/bin/env python3
"""Conservative Case-A RR+DR cooling in the C10 H/He photon packet receiver.

Scientific scope: static proper-volume Bianchi-I receiver a=1/5, source packets
initialized from original C9 fixed-q collisionless age map. New emission OFF.
On top of C10 photon-only: *original Grackle rate-derived Case-A radiative and
dielectronic recombination and recombination cooling* with a single explicit
escaped-radiation energy reservoir (no explicit recombination photons tracked).

Not a full physical reionization, radiative transfer, Case B, collisional
ionization/excitation, bremsstrahlung, Compton, cosmic expansion or universe-
wide time history. Keep frame and rate-source exact.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter

import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/"research/source07_c10_dynamic_20261015"))
import dynamic as c10  # existing frozen photo-only step
from rate_table import CaseARates, ConstantRates, EV_ERG, RateDomainError

C9=c10.c9
MICRO_RTOL=1e-12
MAX_IT=35


def stable_divided_exponential(k2:float,k3:float,dt:float)->float:
    """(exp(-k3 dt)-exp(-k2 dt))/(k2-k3), stable even at k2=k3.

    This positive convolution is the one-way feed HeIII -> HeII during
    competing HeII -> HeI decay and is O(dt) for small dt.
    """
    if not (np.isfinite([k2,k3,dt]).all() and min(k2,k3,dt)>=0):
        raise ValueError("nonnegative decay rates/time required")
    delta=abs(k2-k3)
    if delta==0.:
        return dt*math.exp(-k2*dt)
    u=delta*dt
    return math.exp(-min(k2,k3)*dt)*(-math.expm1(-u))/delta if k2!=k3 else 0.


def rec_analytic(hii:float,heii:float,heiii:float,kH:float,kHeII:float,
                 kHeIII:float,dt:float):
    """Frozen ne, T analytic Markov update, including near-degenerate He rates."""
    if min(hii,heii,heiii,kH,kHeII,kHeIII,dt)<0.:
        raise ValueError("negative Markov input")
    h1=hii*math.exp(-kH*dt)
    z1=heiii*math.exp(-kHeIII*dt)
    y1=heii*math.exp(-kHeII*dt)+heiii*kHeIII*stable_divided_exponential(kHeII,kHeIII,dt)
    events=np.array([hii-h1,(heii+heiii)-(y1+z1),heiii-z1])
    # Tiny roundoff near sub-epsilon times is a signed arithmetic observation;
    # events remain physical when rates/time are within resolved range.
    if np.any(events < -5e-15*max(hii,heii,heiii,1e-30)):
        raise c10.StepFailure("NEGATIVE_RECOMBINATION_EVENT")
    return h1,y1,z1,events


@dataclass
class ReservoirState:
    gas:c10.Gas
    photons:c10.Packets
    escaped_eV_cm3:float=0.
    recomb_electrons_cm3:float=0.
    def conserved_total_energy(self):
        return (self.photons.u+self.gas.thermal_eV_cm3+
                self.gas.binding_eV_cm3+self.escaped_eV_cm3)
    def conserved_photon_electrons(self):
        return self.photons.n+self.gas.ne+self.recomb_electrons_cm3


def rec_step(gas:c10.Gas,dt:float,provider)->tuple[c10.Gas,dict]:
    """Positive frozen-rate He-chain exact step with coupled midpoint T and ne.

    The recombination coefficients are time-frozen only inside each implicit
    substep. Iterate to self-consistent midpoint electron abundance and
    temperature; reject outside the exact Grackle table domain.
    """
    gas.check()
    if not (math.isfinite(dt) and dt>=0):
        raise ValueError("nonnegative finite proper timestep required")
    if dt==0.:
        return gas,{"recomb_events_cm3":[0.,0.,0.],
                    "thermal_cooling_eV_cm3":0., "escape_eV_cm3":0.,
                    "iterations":0,"electron_residual_cm3":0.,
                    "energy_residual_eV_cm3":0.}
    hii0=gas.nHII
    y0=gas.nHeII
    z0=gas.nHeIII
    mid_ne=gas.ne
    mid_T=gas.temperature_K
    for it in range(MAX_IT):
        try:
            coeff=provider(mid_T)
        except RateDomainError as error:
            raise c10.StepFailure(str(error)) from error
        kH,k2,k3=mid_ne*np.array((coeff[0],coeff[1]+coeff[3],coeff[2]))
        h1,y1,z1,events=rec_analytic(hii0,y0,z0,kH,k2,k3,dt)
        nextgas=c10.Gas(
            gas.nH,gas.nHe,
            gas.nH-h1,
            gas.nHe-y1-z1,
            y1,
            gas.thermal_eV_cm3)
        # Grackle coefficient units erg cm^3 s^-1. Eqn uses proper density
        # products ne*nion; DR cooling shares the HeII state.
        avg_ions=.5*np.array((hii0+h1,y0+y1,z0+z1))
        rate_erg_cm3_s=mid_ne*(avg_ions@coeff[4:7] + avg_ions[1]*coeff[7])
        cool_eV=dt*rate_erg_cm3_s/EV_ERG
        if not math.isfinite(cool_eV) or cool_eV<0.:
            raise c10.StepFailure("NONFINITE_RECOMB_COOLING")
        nextgas.thermal_eV_cm3=gas.thermal_eV_cm3-cool_eV
        nextgas.check()
        next_ne=.5*(gas.ne+nextgas.ne)
        # EOS temperature at the discrete midpoint, not an arbitrary mean
        # of endpoint temperatures, especially when ne changes.
        thermal_mid=.5*(gas.thermal_eV_cm3+nextgas.thermal_eV_cm3)
        T_mid=thermal_mid/(1.5*c10.KB_EV_K*(gas.nH+gas.nHe+next_ne))
        if abs(T_mid-mid_T)/max(mid_T,1.)<MICRO_RTOL and abs(next_ne-mid_ne)/max(gas.ne,1e-25)<MICRO_RTOL:
            # Reevaluate once using converged midpoint and use a single
            # source-owned event set for gas and energy/charge ledgers.
            mid_T,mid_ne=T_mid,next_ne
            break
        mid_T,mid_ne=T_mid,next_ne
    else:
        raise c10.StepFailure("CASE_A_MIDPOINT_NOT_CONVERGED")
    coeff=provider(mid_T)
    kH,k2,k3=mid_ne*np.array((coeff[0],coeff[1]+coeff[3],coeff[2]))
    h1,y1,z1,events=rec_analytic(hii0,y0,z0,kH,k2,k3,dt)
    avg_ions=.5*np.array((hii0+h1,y0+y1,z0+z1))
    cool_eV=dt*mid_ne*(avg_ions@coeff[4:7]+avg_ions[1]*coeff[7])/EV_ERG
    updated=c10.Gas(gas.nH,gas.nHe,gas.nH-h1,
                     gas.nHe-y1-z1,y1,gas.thermal_eV_cm3-cool_eV)
    updated.check()
    # Case A: binding released by capture and thermal RR/DR cooling
    # leave the local gas/radiation inventory, into an energy-only ledger.
    # DO NOT declare one ionizing recombination photon per event.
    escape=float(events@C9.BIND+cool_eV)
    electron_res=gas.ne-updated.ne-float(events.sum())
    energy_res=(updated.binding_eV_cm3+updated.thermal_eV_cm3+escape-
                gas.binding_eV_cm3-gas.thermal_eV_cm3)
    scale=max(gas.nH+gas.nHe,1e-30)
    if (abs(electron_res)/scale>3e-11 or
        abs(energy_res)/max(gas.binding_eV_cm3+gas.thermal_eV_cm3,1e-30)>3e-11 or
        escape<0.):
        raise c10.StepFailure("CASE_A_LOCAL_LEDGER_BROKEN")
    return updated,{
        "recomb_events_cm3":events.tolist(),
        "thermal_cooling_eV_cm3":float(cool_eV),
        "escape_eV_cm3":escape,
        "iterations":it+1,
        "electron_residual_cm3":electron_res,
        "energy_residual_eV_cm3":energy_res,
        "Tmid_K":float(mid_T),
        "nemid_cm3":float(mid_ne)}


def strang_step(state:ReservoirState,dt:float,provider)->tuple[ReservoirState,dict]:
    """Second-order symmetric photo/Case-A/photo splitting."""
    if not (math.isfinite(dt) and dt>0):
        raise ValueError("positive finite dt")
    gas1,ph1,p1=c10.midpoint_step(state.gas,state.photons,dt*.5)
    gas2,rec=rec_step(gas1,dt,provider)
    gas3,ph3,p2=c10.midpoint_step(gas2,ph1,dt*.5)
    updated=ReservoirState(
        gas3,ph3,
        state.escaped_eV_cm3+rec["escape_eV_cm3"],
        state.recomb_electrons_cm3+sum(rec["recomb_events_cm3"]))
    return updated,{"photo_events_cm3":(np.array(p1["species_events_cm3"])+
                                        np.array(p2["species_events_cm3"])).tolist(),
                    "recomb_events_cm3":rec["recomb_events_cm3"],
                    "recomb_Tmid_K":rec["Tmid_K"],
                    "cool_eV_cm3":rec["thermal_cooling_eV_cm3"],
                    "caseA_escape_eV_cm3":rec["escape_eV_cm3"]}


def summary_row(t:float,state:ReservoirState)->dict:
    row=c10.observables(t,state.gas,state.photons)
    row["radiative_escape_eV_per_H"]=state.escaped_eV_cm3/state.gas.nH
    row["cumulative_recombination_electrons_per_H"]=state.recomb_electrons_cm3/state.gas.nH
    return row


def evolve(state:ReservoirState,provider,interval_s:float=1e12,nsteps:int=32):
    """Positivity-preserving trial rejection on a fixed reporting grid."""
    if interval_s<=0 or nsteps<1:
        raise ValueError("positive interval and grid required")
    state=ReservoirState(state.gas,state.photons.clone(),
                         state.escaped_eV_cm3,state.recomb_electrons_cm3)
    ref_total=state.conserved_total_energy()
    ref_num=state.conserved_photon_electrons()
    dt=interval_s/nsteps
    hist=[summary_row(0.,state)]
    rejected=0
    accepted=0
    for j in range(nsteps):
        remain=dt
        while remain>dt*1e-13:
            trial_dt=remain
            for _ in range(18):
                try:
                    after,_=strang_step(state,trial_dt,provider)
                    state=after
                    remain-=trial_dt
                    accepted+=1
                    break
                except c10.StepFailure:
                    trial_dt*=.5
                    rejected+=1
            else:
                raise c10.StepFailure("C11_REJECT_CEILING")
            if accepted>20000:
                raise c10.StepFailure("C11_MAX_STEPS")
        hist.append(summary_row((j+1)*dt,state))
    max_energy=max(abs((h["photon_U_eV_per_H"]+h["thermal_eV_per_H"]+
                        h["binding_eV_per_H"]+h["radiative_escape_eV_per_H"])-
                        (hist[0]["photon_U_eV_per_H"]+hist[0]["thermal_eV_per_H"]+
                         hist[0]["binding_eV_per_H"])) for h in hist)
    max_number=max(abs((h["photon_N_per_H"]+h["xe_per_H"]+
                        h["cumulative_recombination_electrons_per_H"])-
                        (hist[0]["photon_N_per_H"]+hist[0]["xe_per_H"])) for h in hist)
    return {"history":hist, "final":hist[-1],"accepted":accepted,"rejected":rejected,
            "max_energy_residual_eV_per_H":max_energy,
            "max_electron_photon_residual_per_H":max_number,
            "photon_packet_bytes":state.photons.bytes}


def build_source(spectrum:str,q:float,gas:c10.Gas,compress:bool,nmu:int=12,
                 ne:int=16,amplitude_per_H:float=1.):
    """Reuse exact previous C9 age propagation and distinct source-conditioned LP."""
    model=C9.Scenario(ROOT)
    age=np.geomspace(model.ar,.2,C9.AGE_COUNT)
    if spectrum=="bb50k":
        spectrum_source=C9.Spectrum()
    elif spectrum=="hard":
        from benchmark import HardSource
        spectrum_source=HardSource()
    else:
        raise ValueError("invalid source")
    cohorts=C9.build_packets(model,spectrum_source,age,q,n_mu=nmu,n_energy=ne)
    weights=C9.source_age_weights(model,age,q)
    kept=C9.AGE_COUNT
    if compress:
        train,hold=C9.gas_states(model)
        response=C9.evaluate_packets(cohorts,np.concatenate((train,hold)))
        fit=C9.design(response,weights,5,len(train))
        kept=fit["retained"]
        weights=c10.weights_from_design(fit,len(age))
    return c10.to_packets(cohorts,weights,gas,amplitude_per_H),kept


def one_run(q=0.,spectrum="bb50k",nsteps=32,interval_s=1e12,
            compress=False,nmu=12,ne=16,provider=None):
    provider=provider if provider is not None else CaseARates()
    model=C9.Scenario(ROOT)
    gas=c10.Gas.initial(model)
    t0=perf_counter()
    packets,kept=build_source(spectrum,q,gas,compress,nmu,ne)
    prep=perf_counter()-t0
    t0=perf_counter()
    res=evolve(ReservoirState(gas,packets),provider,interval_s,nsteps)
    integration=perf_counter()-t0
    return {"q":q,"spectrum":spectrum,"compressed":compress,
            "kept_age_nodes":kept,"nsteps":nsteps,"nmu":nmu,"ne":ne,
            "interval_s":interval_s,"initial_H_dt":model.hubble(.2,q)*interval_s,
            "table_sha256":provider.sha256,"prep_seconds":prep,
            "integration_seconds":integration,**res}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--spectrum",choices=["bb50k","hard"],default="bb50k")
    p.add_argument("--q",type=float,default=0.)
    p.add_argument("--nsteps",type=int,default=32)
    p.add_argument("--interval-s",type=float,default=1e12)
    p.add_argument("--compress",action="store_true")
    p.add_argument("--output",type=Path,default=HERE/"C11_PILOT.json")
    a=p.parse_args()
    r=one_run(a.q,a.spectrum,a.nsteps,a.interval_s,a.compress)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(r,indent=2)+"\n")
    print("SOURCE",a.spectrum,"q",a.q,"compressed",a.compress,
          "ages",r["kept_age_nodes"],"T_K",r["final"]["Tgas_K"],
          "xHII",r["final"]["x_HII"],"xHeII",r["final"]["x_HeII"],
          "escape_eV_per_H",r["final"]["radiative_escape_eV_per_H"])
    print("LEDGER",r["max_energy_residual_eV_per_H"],
          r["max_electron_photon_residual_per_H"],
          "time_s",r["integration_seconds"])


if __name__=="__main__":
    main()
