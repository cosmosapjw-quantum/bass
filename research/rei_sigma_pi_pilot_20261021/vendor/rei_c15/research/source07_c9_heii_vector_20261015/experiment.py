#!/usr/bin/env python3
"""C9 SOURCE07 positive source-age compression: independent three-absorber stress test.

Scientific scope: frozen receiver, source-inspired discretely weighted ages, fixed-q
angular/energy quadrature, no chemistry feedback, no production solver mutation.
Units: energies eV, densities cm^-3, cross-sections cm^2, proper time seconds.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.optimize import linprog

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "research/source07_c1_baseline_20261014"))
from q_emission_baseline import Scenario, Spectrum  # noqa: E402

# Verner-fit parameters (chi, E0, sigma0, ya, p, yw, y0, y1)
FIT = np.array([
    (13.60, .4298, 5.475e4, 32.88, 2.963, 0., 0., 0.),
    (24.59, 13.61, 949.2, 1.469, 3.188, 2.039, .4434, 2.136),
    (54.42, 1.720, 1.369e4, 32.88, 2.963, 0., 0., 0.),
], dtype=float)
BIND = np.array([13.598434599702, 24.587389011, 54.41776])
C_CGS = 29979245800.
DT_S = 1e10
AGE_COUNT = 36
MU_ORDER = 12
ENERGY_ORDER = 16
OBSERVABLES = ("emitted_N", "emitted_U_eV", "absorbed_HI", "absorbed_HeI",
               "absorbed_HeII", "photoheat_eV", "escaped_N", "escaped_U_eV")


def cross_sections(energies: np.ndarray) -> np.ndarray:
    """NumPy vectorization of the three original Verner parameter sets."""
    energies = np.asarray(energies, dtype=float)
    result = np.zeros((energies.size, 3))
    for i, (chi, e0, sig0, ya, p, yw, y0, y1) in enumerate(FIT):
        eligible = energies >= chi
        e = energies[eligible]
        x = e / e0 - y0
        y = np.hypot(x, y1)
        result[eligible, i] = (sig0 * ((x - 1.)**2 + yw*yw) *
               y**(p/2. - 5.5) * (1. + np.sqrt(y/ya))**(-p) * 1e-18)
    return result


def build_packets(model: Scenario, spectrum: Spectrum, ages: np.ndarray,
                  q: float, n_mu: int = MU_ORDER,
                  n_energy: int = ENERGY_ORDER) -> list[tuple]:
    """Evaluate expensive geometry/spectral response once per (age, q)."""
    mu, mw = leggauss(n_mu)
    ex, ew = leggauss(n_energy)
    rp_recv, rz_recv = model.ratios(.2, q)
    packets = []
    for age in ages:
        rp_emit, rz_emit = model.ratios(float(age), q)
        rp, rz = rp_recv/rp_emit, rz_recv/rz_emit
        energy_parts, weight_parts = [], []
        for m, wm in zip(mu, mw):
            scale = math.sqrt(rp*rp*(1.-m*m) + rz*rz*m*m)
            cuts = sorted(set([13.6, 100.] + [
                t/scale for t in (13.6, 24.59, 54.42) if 13.6 < t/scale < 100.]))
            for lo, hi in zip(cuts[:-1], cuts[1:]):
                e = (hi+lo)*.5 + (hi-lo)*.5*ex
                flux = .5*wm*.5*(hi-lo)*ew*spectrum.phi(e)
                energy_parts.append(e*scale)
                weight_parts.append(flux)
        energies = np.concatenate(energy_parts)
        weights = np.concatenate(weight_parts)
        sigma = cross_sections(energies)
        excess = np.maximum(energies[:, None] - BIND[None, :], 0.)
        packets.append((energies, weights, sigma, sigma*excess))
    return packets


def evaluate_packets(packets: list[tuple], gas: np.ndarray,
                     dt: float = DT_S) -> np.ndarray:
    """All receiver states in one vectorized BLAS pass per age.

    Returned shape (n_state, n_age, 8). Never materialize age x gas x E x species.
    """
    gas = np.asarray(gas, dtype=float)
    if gas.ndim != 2 or gas.shape[1] != 3 or not np.all(np.isfinite(gas)) or np.any(gas < 0):
        raise ValueError("gas must be finite nonnegative (n,3) densities")
    if not np.isfinite(dt) or dt < 0:
        raise ValueError("dt must be nonnegative")
    result = np.empty((gas.shape[0], len(packets), len(OBSERVABLES)))
    for i, (energy, weight, sigma, sigma_heat) in enumerate(packets):
        tau = (C_CGS*dt)*(sigma @ gas.T)  # n_energy x n_gas
        factor = np.ones_like(tau)
        np.divide(-np.expm1(-tau), tau, out=factor, where=tau > 0)
        weighted = weight[:, None]*factor
        absorption = (C_CGS*dt)*(weighted.T @ sigma)*gas
        heating = np.sum((C_CGS*dt)*(weighted.T @ sigma_heat)*gas, axis=1)
        escape = weight[:, None]*np.exp(-tau)
        result[:, i, 0] = weight.sum()
        result[:, i, 1] = weight @ energy
        result[:, i, 2:5] = absorption
        result[:, i, 5] = heating
        result[:, i, 6] = escape.sum(axis=0)
        result[:, i, 7] = energy @ escape
    return result


def physics_ledger(response: np.ndarray) -> dict:
    """Independent photon-number and absorbed-binding/heat energy budgets."""
    num = response[..., 0] - response[..., 2:5].sum(axis=-1) - response[..., 6]
    energy = (response[..., 1] - response[..., 7] -
              np.einsum("...i,i->...", response[..., 2:5], BIND) -
              response[..., 5])
    norm_num = np.maximum(np.abs(response[..., 0]), 1e-30)
    norm_energy = np.maximum(np.abs(response[..., 1]), 1e-30)
    return {"max_photon_residual": float(np.max(np.abs(num)/norm_num)),
            "max_energy_residual": float(np.max(np.abs(energy)/norm_energy)),
            "max_negative_absorption": float(np.maximum(0., -response[..., 2:5].min())),
            "max_negative_escape": float(np.maximum(0., -response[..., 6:8].min()))}


def source_age_weights(model: Scenario, ages: np.ndarray, q: float) -> np.ndarray:
    """Normalized midpoint/trapezoid discretization of rate(a)/H(a,q) d ln a.

    Model-inspired discretization, NOT a transported continuous source history.
    """
    loga = np.log(ages)
    delta = np.empty(len(ages))
    delta[0] = .5*(loga[1]-loga[0])
    delta[-1] = .5*(loga[-1]-loga[-2])
    delta[1:-1] = .5*(loga[2:]-loga[:-2])
    emit = np.array([model.rate(float(a))/model.hubble(float(a), q)
                     for a in ages])
    w = delta * emit
    if np.any(w < 0) or not np.isfinite(w.sum()) or w.sum() <= 0:
        raise ValueError("invalid source quadrature")
    return w/w.sum()


def gas_states(model: Scenario) -> tuple[np.ndarray, np.ndarray]:
    n_h = model.nh * 5.**3 * (1.-.0002)
    n_he = model.nh * 5.**3 * .2454/(4*(1.-.2454))
    train_fractions = [(0.90,.90,.08), (0.50,.70,.20), (0.25,.30,.55),
                       (0.08,.10,.70), (0.01,.01,.98)]
    hold_fractions = [(h, hei, heii_frac*(1.-hei))
                      for h in (.03,.15,.45,.85)
                      for hei in (.05,.30,.70,.95)
                      for heii_frac in (.12,.45,.90)]
    def convert(fracs):
        return np.asarray([[h*n_h, a*n_he, b*n_he] for h,a,b in fracs])
    return convert(train_fractions), convert(hold_fractions)


def design(source: np.ndarray, original_weights: np.ndarray, ntrain: int,
           ntest: int) -> dict:
    """Positive sparse LP using source responses for N/U/HI/HeI/HeII/heat."""
    nages = source.shape[1]
    raw = np.concatenate((np.ones((1,nages)), source[:ntrain,:,:6].transpose(0,2,1).reshape(-1,nages)),axis=0)
    row_scale = np.maximum(np.max(np.abs(raw),axis=1), 1e-30)
    matrix = raw/row_scale[:,None]
    reference = matrix @ original_weights
    lp = linprog(np.linspace(0.,1.,nages), A_eq=matrix, b_eq=reference,
                 bounds=(0,None), method="highs",
                 options={"primal_feasibility_tolerance": 1e-9})
    if not lp.success:
        return {"status": "LP_FAILED", "reason": lp.message, "ntrain": ntrain}
    w = np.maximum(lp.x, 0.)
    target = source[:,:,:6].transpose(0,2,1) @ original_weights
    got = source[:,:,:6].transpose(0,2,1) @ w
    rel = np.abs(got-target)/np.maximum(np.abs(target),1e-25)
    testerr = rel[ntest:]
    return {"status":"SOLVED", "ntrain": ntrain, "retained":int(np.sum(w>1e-10)),
            "weights":[[int(i),float(w[i])] for i in np.where(w>1e-10)[0]],
            "weight_sum":float(w.sum()),
            "training_max_rel_error":float(np.max(rel[:ntrain])),
            "holdout_max_rel_error":float(testerr.max()),
            "holdout_max_per_feature":np.max(testerr,axis=0).tolist(),
            "max_abs_weight_error":float(np.max(np.abs(w-original_weights)))}


def one_q(q: float) -> dict:
    model=Scenario(ROOT)
    spectrum=Spectrum()
    ages=np.geomspace(model.ar,.2,AGE_COUNT)
    train, hold=gas_states(model)
    states=np.concatenate((train,hold),axis=0)
    t0=time.perf_counter()
    packets=build_packets(model,spectrum,ages,q)
    build_s=time.perf_counter()-t0
    t1=time.perf_counter()
    values=evaluate_packets(packets,states)
    evaluation_s=time.perf_counter()-t1
    age_w=source_age_weights(model,ages,q)
    ledger=physics_ledger(values)
    layouts={str(n):design(values,age_w,n,len(train)) for n in (1,3,5)}
    packet_bytes=sum(sum(item.nbytes for item in packet) for packet in packets)
    return {"q":q,"num_ages":len(ages),"training_states":len(train),
            "unseen_physical_simplex_states":len(hold),
            "nonzero_HeII_states":int(np.sum(states[:,2]>0)),
            "age_weights":age_w.tolist(),"packet_bytes":packet_bytes,
            "build_seconds":build_s,"evaluate_seconds":evaluation_s,
            "ledger":ledger,"designs":layouts}


def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument("--workers",type=int,choices=[1,3],default=1)
    parser.add_argument("--output",type=Path,default=Path(__file__).with_name("results.json"))
    args=parser.parse_args()
    t0=time.perf_counter()
    qs=(-.01,0.,.01)
    if args.workers==1:
        rows=[one_q(q) for q in qs]
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            rows=list(pool.map(one_q,qs))
    provenance={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                for p in (ROOT/"research/source07_c8_age_compression_20261015/experiment.py",
                          ROOT/"research/source07_c1_baseline_20261014/q_emission_baseline.py")}
    result={"schema":"rei.source07.c9.heii-vector.frozen-receiver.v1",
            "scope":"exploratory; q/emissivity age discretization with frozen nonzero HeII, no dynamic chemistry or temperature, no production admission",
            "workers":args.workers,"total_wall_s":time.perf_counter()-t0,
            "source_sha256":provenance,"cases":rows}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+"\n")
    for r in rows:
        print("q",r["q"],"ledger",r["ledger"],"layouts",
              [(k,v.get("retained"),v.get("holdout_max_rel_error"))
               for k,v in r["designs"].items()],flush=True)
    print("total_s",result["total_wall_s"],"output",args.output)


if __name__=="__main__":
    main()
