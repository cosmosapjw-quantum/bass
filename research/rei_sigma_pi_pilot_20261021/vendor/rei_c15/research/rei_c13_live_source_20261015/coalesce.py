#!/usr/bin/env python3
"""Experimental positive two-point source-age compression on genuinely transported
photons from one source-locked Bianchi-I angular/spectral cell family.

For each original native source cell, preserve N, U, U2 and energy-weighted
mu² exactly within float error, with two nonnegative supported energy nodes.
Admit only when actual 3-species photon-absorption and photoheating errors
for frozen gas + holdout states pass the predeclared local step budget.
The accepted local condition is NOT a global dynamic certified error bound.
"""
from __future__ import annotations
import math
import numpy as np
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"research/source07_c10_dynamic_20261015"))
import dynamic as c10


def moments(sky):
    w=sky.NperH;e=sky.E;mu=sky.mu
    return np.array([sum(w),float(w@e),float(w@(e*e)),
                     float(w@(e*mu*mu))])


def event_heat(sky,gas,dt):
    sigma=c10.c9.cross_sections(sky.E)
    ex=np.maximum(sky.E[:,None]-c10.c9.BIND[None,:],0.)
    evt,heat,energy,rest,absorbed=c10.reactions_vector(
        sky.NperH*gas.nH,sky.E,sigma,sigma*ex,gas.neutral,dt)
    return np.array([*(evt/gas.nH),heat/gas.nH])


def reduce_age_cohorts(sky,base_cells,gas,dt_s,*,event_budget=1e-10,
                       heat_budget=1e-9):
    sky.check()
    if (not isinstance(base_cells,int) or base_cells<1 or len(sky.E)%base_cells
        or dt_s<=0 or event_budget<=0 or heat_budget<=0):
        raise ValueError("SOURCE_MODE_GRID_OR_BUDGET_INVALID")
    ncohort=len(sky.E)//base_cells
    if ncohort<=2:
        return sky,{"admitted":True,"merged":False,"max_event_abs_perH":0.,
                    "max_heat_abs_eV_perH":0.,"input_cohorts":ncohort,
                    "source_mode_count":base_cells}
    W=sky.NperH.reshape(ncohort,base_cells)
    E=sky.E.reshape(ncohort,base_cells)
    M=sky.mu.reshape(ncohort,base_cells)
    mass=W.sum(axis=0)
    if np.any(mass<=0) or not np.all(np.isfinite(mass)):
        raise ValueError("POSITIVE_REPRESENTABLE_GROUP_REQUIRED")
    avg=(W*E).sum(axis=0)/mass
    var=(W*(E-avg[None,:])**2).sum(axis=0)/mass
    lo=E.min(axis=0);hi0=E.max(axis=0)
    gap=avg-lo
    hi=np.where(gap>1e-15*np.maximum(avg,1),
                avg+np.divide(var,gap,out=np.zeros_like(var),where=gap!=0),avg)
    if np.any(hi>hi0*(1+5e-13)) or np.any(hi<lo):
        raise ValueError("TWO_POINT_SOURCE_ENERGY_SUPPORT_VIOLATION")
    denom=hi-lo
    frac=np.divide(avg-lo,denom,out=np.full_like(denom,.5),
                   where=denom>1e-16*np.maximum(avg,1.))
    if np.any(frac<0) or np.any(frac>1):
        raise ValueError("TWO_POINT_WEIGHTS_NONPOSITIVE")
    # Preserve energy-weighted axisymmetric quadrupole, not false odd-flux
    # symmetry or separate angular-angle distribution.
    mu2=(W*E*M*M).sum(axis=0)/((W*E).sum(axis=0))
    signed=(W*E*M).sum(axis=0)
    mapped_mu=np.sign(signed)*np.sqrt(np.maximum(0.,mu2))
    from short_interval import PhotonCloud
    candidate=PhotonCloud(np.stack((lo,hi)).reshape(-1),
                          np.stack((mapped_mu,mapped_mu)).reshape(-1),
                          np.stack((mass*(1-frac),mass*frac)).reshape(-1))
    candidate.check()
    original_mom=moments(sky)
    reduced_mom=moments(candidate)
    max_moment_diff=np.max(np.abs(original_mom-reduced_mom)/
                           np.maximum(abs(original_mom),1e-22))
    if max_moment_diff>3e-12:
        raise ValueError(f"TWO_POINT_MOMENTS_NOT_PRESERVED {max_moment_diff}")
    evErr=0.;heatErr=0.
    # Explicit holdout states never exceed original positive nuclei inventory.
    for scale in (1.,.7,.35):
        g=c10.Gas(gas.nH,gas.nHe,gas.nHI*scale,
                   gas.nHeI*scale,gas.nHeII*scale,
                   gas.thermal_eV_cm3)
        a=event_heat(sky,g,dt_s)
        b=event_heat(candidate,g,dt_s)
        evErr=max(evErr,float(np.max(abs(a[:3]-b[:3]))))
        heatErr=max(heatErr,float(abs(a[3]-b[3])))
    accepted=(evErr<=event_budget and heatErr<=heat_budget)
    return (candidate if accepted else sky), {
        "admitted":accepted,"merged":accepted,
        "input_cohorts":ncohort,"source_mode_count":base_cells,
        "initial_packets":len(sky.E),"final_packets":len(candidate.E) if accepted else len(sky.E),
        "max_event_abs_perH":evErr,"max_heat_abs_eV_perH":heatErr,
        "event_budget":event_budget,"heat_budget":heat_budget,
        "max_preserved_moment_rel":float(max_moment_diff),
        "claim":"finite-frozen-receiver-holdout-only-NOT_CERTIFIED_FUTURE_DYNAMIC"
    }
