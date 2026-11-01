#!/usr/bin/env python3
"""BASS polarized Thomson response on byte-locked REI F08 S0 electron histories.

Science scope: initially isotropic unpolarized TEST blackbody at original t=0;
linear in constant trace-free Bianchi shear and in Thomson optical depth.
NOT the actual S0 monochromatic photon occupation or a full Boltzmann solution.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "source_inputs"
S0_SOURCE_SHA = {
    "S0_BI-electron_density.csv.gz": "663911291bea564d314e1d46df9750c03a39fd5d9404eca6a7485776d894f723",
    "S0_FLRW-electron_density.csv.gz": "0b81cae87d6f90888d1d3def1995cd8d029625d1cc1dd11bffab94e8d30e7efa",
    "science_scenario_v1.json": "c83d2d43adda663707f99af2b45576eb4478cd94d3440a21fd21eaed32b5f2c1",
}
REI_HEAD = "1605236b8172db411d862caa219322d6af6953b1"
PAIR_ID = "0a2bec874a5aa1b12f882033a08497b913b44447148b50b6082093bb354868e8"
C_CGS = 29979245800.0
SIGMA_T = 6.6524587051e-25
GRIDS = ((8, 16), (16, 32), (32, 64))
EPOCH_SAMPLES = (4000, 8000, 12000, 16000)

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(1048576), b""):
            h.update(b)
    return h.hexdigest()

def load_source():
    for name, digest in S0_SOURCE_SHA.items():
        if sha256(SOURCE / name) != digest:
            raise ValueError("REI F08 source byte-identity failure: " + name)
    provenance = json.loads((SOURCE / "REI349_SOURCE_PROVENANCE.json").read_text())
    if provenance["source_pair_id"] != PAIR_ID or provenance["original_F08_return"]["scientific_admission"] != "HOLD":
        raise ValueError("REI source provenance/admission mismatch")
    scenario = json.loads((SOURCE / "science_scenario_v1.json").read_text())
    if scenario["source"]["family"] != "S0" or scenario["source"]["energy_at_birth_ev"] != 13.7:
        raise ValueError("REI S0 photon owner unexpectedly changed")
    if scenario["background"]["tilt"] != [0.0, 0.0, 0.0] or scenario["background"]["a0"] != [1.0]*3:
        raise ValueError("requires original comoving diagonal Bianchi I")
    H = [float(x) for x in scenario["background"]["pairs"]["BIANCHI_I"]["H_per_s"]]
    Hmean = float(scenario["background"]["H_mean_per_s"])
    if abs(sum(H)/3 - Hmean)>1e-28 or H != [1.01e-14, 9.9e-15, 1e-14]:
        raise ValueError("original Bianchi metric mismatch")
    if scenario["time"]["t_end_s"] != 1e13:
        raise ValueError("original REI source time changed")
    hist = {}
    for key in ("S0_BI", "S0_FLRW"):
        with gzip.open(SOURCE / (key + "-electron_density.csv.gz"), "rt", newline="") as f:
            rows = list(csv.DictReader(f))
        if len(rows)!=16001:
            raise ValueError("REI F08 source has wrong accepted-history length")
        ts, ns = [], []
        for row in rows:
            t = float(row["normal_time_s"])
            ne = float(row["ne_proper_cm3"])
            nh = float(row["nH_proper_cm3"])
            nh_expected = scenario["initial_state"]["nH0_cm3"]*math.exp(-3*Hmean*t)
            if (not math.isfinite(t) or not math.isfinite(ne) or ne<=0
                or abs(nh/nh_expected - 1)>6e-12
                or float(row["D_gas_normal_observer"]) != 1.0):
                raise ValueError("invalid original F08 physical history")
            ts.append(t); ns.append(ne)
        if ts[0] != 0.0 or ts[-1] != 1e13 or any(b<=a for a,b in zip(ts,ts[1:])):
            raise ValueError("invalid proper-clock source")
        hist[key] = (ts,ns)
    if hist["S0_BI"][0] != hist["S0_FLRW"][0]:
        raise ValueError("original matched sample clocks differ")
    return scenario, H, hist

def cumulative_moments(times, density):
    """Exactly integrate linear ne(t) over each original retained time panel."""
    if len(times)<2 or len(times)!=len(density):
        raise ValueError("nonmatching or empty photon-scatter time history")
    tau, kt = [0.0], [0.0]
    optical = C_CGS*SIGMA_T
    for i in range(len(times)-1):
        a,b = times[i:i+2]
        p,q = density[i:i+2]
        dt=b-a
        if not all(math.isfinite(x) for x in (a,b,p,q)) or dt<=0 or min(p,q)<0:
            raise ValueError("invalid electron source panel")
        dN=dt*(p+q)/2
        dT=dt*(a*(p+q)/2+dt*(p/6+q/3))
        tau.append(tau[-1]+optical*dN)
        kt.append(kt[-1]+optical*dT/10)
    return tau,kt

def screen(mu, phi):
    v=math.sqrt(max(0.0,1-mu*mu))
    # standard right-handed local spherical basis, n cross e_theta = e_phi
    theta=(mu*math.cos(phi),mu*math.sin(phi),-v)
    azimuth=(-math.sin(phi),math.cos(phi),0.0)
    return theta,azimuth

def stokes_response(sigma, K, mu, phi):
    e1,e2=screen(mu,phi)
    s11=sum(sigma[i]*e1[i]*e1[i] for i in range(3))
    s22=sum(sigma[i]*e2[i]*e2[i] for i in range(3))
    s12=sum(sigma[i]*e1[i]*e2[i] for i in range(3))
    return K*(s11-s22), 2*K*s12

def direct_thomson_gain(sigma, t, mu, phi, nmu=64, nphi=128):
    """Independent direct incoming-angle quadrature of the Thomson Q,U gain."""
    e1,e2=screen(mu,phi)
    qsum,usum=0.0,0.0
    for j in range(nmu):
        z=-1.0+2*(j+0.5)/nmu
        xy=math.sqrt(1-z*z)
        for k in range(nphi):
            p=2*math.pi*(k+0.5)/nphi
            incoming=(xy*math.cos(p),xy*math.sin(p),z)
            theta=-t*sum(sigma[i]*incoming[i]**2 for i in range(3))
            aa=sum(e1[i]*incoming[i] for i in range(3))
            bb=sum(e2[i]*incoming[i] for i in range(3))
            qsum+=theta*(aa*aa-bb*bb)
            usum+=theta*(2*aa*bb)
    # negative projection kernel, unit-normalized dOmega/(4pi)
    return -3*qsum/(4*nmu*nphi), -3*usum/(4*nmu*nphi)

def generate(out: Path):
    scenario,H,hist=load_source()
    sig=tuple(v-sum(H)/3 for v in H)
    if abs(sum(sig))>1e-27:
        raise ValueError("shear not trace-free")
    tvals=hist["S0_BI"][0]
    tau_b,K_b = cumulative_moments(*hist["S0_BI"])
    tau_f,K_f = cumulative_moments(*hist["S0_FLRW"])
    out.mkdir(parents=True,exist_ok=True)
    fields=("epoch_index","observer_proper_time_s","nmu","nphi","mu_bin","phi_bin",
            "mu","phi_rad","Q_over_Tbar_BI_electron","U_over_Tbar_BI_electron",
            "P_over_Tbar_BI_electron","Q_over_Tbar_FLRW_electron_control",
            "U_over_Tbar_FLRW_electron_control","delta_Q_material_fixed_BI_geometry",
            "delta_U_material_fixed_BI_geometry")
    records=0; epoch_reports=[]
    dest=out/"REI_F08_S0_TESTRADIATION_THOMSON_POLAR_SKY.csv.gz"
    with dest.open("wb") as raw:
        with gzip.GzipFile(fileobj=raw,filename="",mtime=0,mode="wb",compresslevel=6) as z:
            import io
            with io.TextIOWrapper(z,encoding="utf-8",newline="") as txt:
                wr=csv.writer(txt);wr.writerow(fields)
                for idx in EPOCH_SAMPLES:
                    stage={"sample_index":idx,"observer_proper_time_s":tvals[idx],
                           "tau_original_BI_electron":tau_b[idx],
                           "tau_original_FLRW_electron":tau_f[idx],
                           "electron_weighted_source_time_s":10*K_b[idx]/tau_b[idx],
                           "polarization_kernel_BI_seconds":K_b[idx],
                           "polarization_kernel_FLRW_seconds":K_f[idx],
                           "shear_s_inverse":sig,
                           "mean_P_BI_by_grid":{},"max_P_BI_by_grid":{}}
                    for nmu,nphi in GRIDS:
                        ps=[]
                        for i in range(nmu):
                            mu=-1+2*(i+0.5)/nmu
                            for j in range(nphi):
                                phi=2*math.pi*(j+0.5)/nphi
                                q,u=stokes_response(sig,K_b[idx],mu,phi)
                                qf,uf=stokes_response(sig,K_f[idx],mu,phi)
                                pol=math.hypot(q,u)
                                wr.writerow((idx,tvals[idx],nmu,nphi,i,j,format(mu,".17g"),
                                    format(phi,".17g"),format(q,".17g"),format(u,".17g"),
                                    format(pol,".17g"),format(qf,".17g"),format(uf,".17g"),
                                    format(q-qf,".17g"),format(u-uf,".17g")))
                                ps.append(pol);records+=1
                        grid=f"{nmu}x{nphi}"
                        stage["mean_P_BI_by_grid"][grid]=math.fsum(ps)/len(ps)
                        stage["max_P_BI_by_grid"][grid]=max(ps)
                    epoch_reports.append(stage)
    report={
      "schema":"BASS_REI_F08_S0_FIRST_ORDER_TEST_RADIATION_THOMSON_POL_V1",
      "science_status":"DERIVED_SOURCE_MATCHED_ELECTRON_METRIC_TEST_RADIATION_CONDITIONAL",
      "original_rei_pr":349,"original_rei_head":REI_HEAD,"original_source_pair_id":PAIR_ID,
      "source_sha256":S0_SOURCE_SHA,
      "model":"original prescribed constant-H Bianchi I; comoving gas, original S0 F08 n_e(t); initially isotropic unpolarized test Planck field at t=0",
      "source_emission_completeness":"NOT_THE_ACTUAL_S0_13.7eV_SOURCE_PHOTON_TRANSFER",
      "expansion_order":"O(sigma*t) and O(tau); omit O(sigma^2), O(tau^2), incoming scattered radiation, absorber and true S0 photon source",
      "convention":"signature(-,+,+,+), scalar test radiation thermodynamic Stokes in e_theta,e_phi screen, Q=I_theta-I_phi, U=2I_theta_phi",
      "constants":{"c_cm_per_s":C_CGS,"sigmaT_cm2":SIGMA_T},
      "observer_times":list(tvals[i] for i in EPOCH_SAMPLES),
      "angular_grids":GRIDS,"epoch_reports":epoch_reports,
      "physical_ray_rows":records,"sky_file":dest.name,"sky_sha256":sha256(dest),
      "original_F08_admission":"HOLD","original_F09":"BLOCKED","original_F05":"BLOCKED",
      "BASS_upper_scoped":"9/15_REPORTED_FULL_PHYSICAL_UNKNOWN",
      "REI_central":"28/88_REPORTED","REI_working":"33/88_REPORTED",
      "canonical_delta":0,"BASS_upper_full_delta":0,
      "scientific_admission":"EXPLORATORY_ONLY","production":"HOLD","merge":False
    }
    (out/"RESULT.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    return report

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,default=ROOT/"results")
    args=ap.parse_args()
    rep=generate(args.out)
    print(json.dumps({"rows":rep["physical_ray_rows"],"sha256":rep["sky_sha256"],
      "epoch_reports":rep["epoch_reports"],"REI_central":rep["REI_central"]},sort_keys=True))
if __name__=="__main__":main()
