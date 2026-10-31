"""Independent saved-source scientific audit of retarded once-scattered P8 photons.

NO original Einstein/P8/Peebles RHS imports. Reconstructs exact normal
source-energy, phase-space spectral first moment and 2x2 screen polarization
using only frozen per-time factorized M_e, F, mu, tau and w sources. Uses
mathematical expressions distinct from the production frequency-bin remap.
Explicit exceptions survive python -O optimization.
"""
from __future__ import annotations
import argparse,hashlib,json,math
from pathlib import Path
import numpy as np
from numpy.polynomial.legendre import leggauss


def require(cond,msg):
    if not bool(cond):raise ArithmeticError("KM2N_BLIND_SAVED_SOURCE_FAIL "+msg)


def saved_audit(source,out):
    p=Path(source);d=json.loads(p.read_text());root=p.parent
    require(d["upper_dag"]=="9/15" and d["KM2"]=="PARTIAL","DAG")
    require(not (d["production_ready"] or d["merge_ready"] or d["auto_next"]),"FALSE_PRODUCTION")
    require(set(d["cases"])=={"GL12","GL16"},"PHYSICAL_GRIDS")
    nb=d["frequency_bins_per_snapshot"]
    require(nb==1200,"FREQ_BINS")
    y=np.linspace(-.5+1/2400.,.5-1/2400.,1200)
    err={"bolometric_gain_relative":0.,"mean_frequency_abs":0.,
         "source_p8_parity":0.,"rho_trapezoid_vs_simpson":0.,
         "fourmom_momentum_abs":0.,"polarization_mean_abs":0.,
         "screen_transversality_abs":0.,"raw_screen_field_abs":0.}
    observed=0
    for key,case in d["cases"].items():
        file=root/case["first_source_ledger_file"]
        require(file.is_file(),"LEDGER_NOT_SAVED")
        require(hashlib.sha256(file.read_bytes()).hexdigest()==case["first_source_ledger_sha256"],"LEDGER_SHA")
        with np.load(file,allow_pickle=False) as f:
            T=f["time"];M=f["Me"];F=f["F"];nu=f["nu"];D=f["D"]
            mu=f["mu"];tau=f["tau"];w=f["w"];n=f["n"];E=f["E"]
            rates=f["source_gain_rate"]
            require(len(T)==41 and M.shape==(41,1200,3,3),"SOURCE_CASE_CARDINALITY")
            N=len(w[0]);require(N==2*case["grid"]**2,"ORIGINAL_RAY_COUNT")
            require(np.min(D)>0 and np.min(mu)>0 and np.min(nu)>0,"PHYSICAL_RATES")
            require(np.min(np.diff(tau,axis=0))>0,"POSITIVE_THOMSON_OPTICAL_DEPTH")
            require(np.min(np.diff(T))>0,"CAUSAL_TIME")
            ortho=np.max(abs(np.einsum("tni,tnia->tna",n,E)))
            err["screen_transversality_abs"]=max(err["screen_transversality_abs"],float(ortho))
            require(ortho<5e-9,"ORIGINAL_SCREEN_GEODESIC")
            # Independent frequency integral first-moment tensors; no bin interpolation.
            M0=M.sum(axis=1)
            M1=np.tensordot(M,y,axes=([1],[0]))
            require(M1.shape==(41,3,3),"SPECTRAL_FIRST_MOMENT")
            for j,U in enumerate((8,16,24,32,40)):
                observed+=1
                rec=case["snapshots"][j]
                require(abs(T[U]-rec["u"])<3e-14,"U_TIME")
                h=T[U]/U
                B=np.zeros((N,2,2));Q1=np.zeros(N)
                Btrap=np.zeros((N,2,2))
                for s in range(1,U+1):
                    sf=(4 if s%2 else 2) if s!=U else 1
                    quadrature=sf*h/3.
                    trapezoid=h*(.5 if s==U else 1.)
                    rat=mu[U]/mu[s]
                    require(np.max(rat)<1+1e-11 and np.min(rat)>0,"ENERGY_GEODESIC")
                    depth=tau[U]-tau[s]
                    require(np.min(depth)>-3e-12,"NEGATIVE_SECOND_SURVIVAL")
                    greens=rat**4*np.exp(-np.maximum(0.,depth))*nu[s]*D[s]**-3*(3/(8*math.pi))
                    f=F[s]
                    # Audit basis uses component-wise tensor contractions, different
                    # from producer's all-frequency rank-2 matrix bin remapping.
                    bb=np.einsum("nia,ij,njb->nab",f,M0[s],f,optimize=True)
                    b1=np.einsum("nia,ij,nja->n",f,M1[s],f,optimize=True)
                    tr=np.trace(bb,axis1=-2,axis2=-1)
                    shift=-np.log(D[s])+np.log(rat)
                    moment=b1+shift*tr
                    B+= (quadrature*greens)[:,None,None]*bb
                    Q1+=(quadrature*greens)*moment
                    Btrap+= (trapezoid*greens)[:,None,None]*bb
                a=np.trace(B,axis1=1,axis2=2)
                rho=float(np.dot(w[U],a))
                rho_trap=float(np.dot(w[U],np.trace(Btrap,axis1=1,axis2=2)))
                Q=float(np.dot(w[U],Q1)/rho)
                err["bolometric_gain_relative"]=max(err["bolometric_gain_relative"],abs(rho/rec["rho_exactly_one"]-1))
                err["mean_frequency_abs"]=max(err["mean_frequency_abs"],abs(Q-rec["mean_logfreq"]))
                err["rho_trapezoid_vs_simpson"]=max(err["rho_trapezoid_vs_simpson"],abs(rho_trap/rho-1))
                momentum=np.einsum("n,ni->i",w[U]*a,n[U])
                err["fourmom_momentum_abs"]=max(err["fourmom_momentum_abs"],float(np.max(abs(momentum-np.asarray(rec["q_exactly_one"])))))
                # Compute polarization via eigenvalue gap, not original source formula.
                eig=np.linalg.eigvalsh((B+B.swapaxes(1,2))/2.)
                require(np.min(eig)>-1e-16*max(1.,float(np.max(abs(B)))), "NEGATIVE_POLARIZATION")
                degree=(eig[:,1]-eig[:,0])/np.maximum(eig[:,1]+eig[:,0],1e-300)
                weighted=float(np.dot(w[U]*a,degree)/rho)
                err["polarization_mean_abs"]=max(err["polarization_mean_abs"],abs(weighted-rec["mean_linear_polarization"]))
                if rec["factorized_field_file"]:
                    raw=root/rec["factorized_field_file"]
                    require(hashlib.sha256(raw.read_bytes()).hexdigest()==rec["factorized_field_sha256"],"FINAL_MATRIX_SHA")
                    with np.load(raw,allow_pickle=False) as z:
                        original=z["screen_bolometric_first_one"]
                        err["raw_screen_field_abs"]=max(err["raw_screen_field_abs"],float(np.max(abs(original-B))))
                        actual_freq=z["screen_spectral_first_one"]
                        require(actual_freq.shape==(N,1200,2,2),"REAL_POL_FREQUENCY_FIELD")
                        require(np.min(np.linalg.eigvalsh(actual_freq.sum(axis=1)))>-1e-16,"FINAL_SCREEN_PSD")
                require(rho>0 and Q<.5 and Q>-.5,"REAL_PHOTON_FIELD")
                require(abs(sum(rec["spectral_energy_bins"])/rho-1)<3e-11,"FREQUENCY_ENERGY_CLOSURE")
                require(abs(weighted-rec["mean_linear_polarization"])<2e-10,"POLARIZATION_PARITY")
                require(abs(Q-rec["mean_logfreq"])<3e-5,"FREQUENCY_CENTROID_PARITY")
        err["source_p8_parity"]=max(err["source_p8_parity"],case["max_source_p8_gain_parity_relative"])
    require(observed==10,"FIRST_SCATTERED_EPOCH_COUNT")
    require(err["bolometric_gain_relative"]<3e-12,"INDEPENDENT_SOURCE_GREEN_RHO")
    require(err["polarization_mean_abs"]<3e-10,"INDEPENDENT_POLARIZATION")
    require(err["fourmom_momentum_abs"]<2e-13,"INDEPENDENT_Q_MOMENTUM")
    require(err["source_p8_parity"]<4e-10,"ORIGINAL_P8_THOMSON_PARITY")
    require(err["raw_screen_field_abs"]<2e-13,"SCREEN_BOL_FROM_RAW")
    # Independent analytic exactly-one pulse/constant emissivity checks.
    h=.35;g=4.2;t=.19;j=1.7;A=2.4
    x,w=leggauss(64)
    ts=t*(x+1)/2
    numerical=np.dot(w*t/2,g*A*np.exp(-(4*h+g)*ts)*np.exp(-(4*h+g)*(t-ts)))
    expected=A*g*t*np.exp(-(4*h+g)*t)
    require(abs(numerical/expected-1)<2e-14,"POISSON_EXACT_ONE_LIMIT")
    v=np.dot(w*t/2,g*j*(-np.expm1(-(4*h+g)*ts))/(4*h+g)*np.exp(-(4*h+g)*(t-ts)))
    exact=j*g*(-math.expm1(-(4*h+g)*t)-(4*h+g)*t*math.exp(-(4*h+g)*t))/(4*h+g)**2
    require(abs(v/exact-1)<3e-14,"CONSTANT_EMITTING_EXACT_ONE_LIMIT")
    report={"schema":"bass.km2n.independent_retarded_one_thomson.v1",
            "science_SHA256":hashlib.sha256(p.read_bytes()).hexdigest(),
            "original_BASS_RHS_imported":False,"uses_saved_source_only":True,
            "actual_nonzero_scattered_observation_epochs":observed,
            "independent_method":"bolometric 2x2 tensor Green + unremapped exact first-frequency moment + symmetric eigenvalue polarization and Simpson vs trapezoid",
            "maxima":err,"verdict":"PASS_SCOPED"}
    out=Path(out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("KM2N_HOSTILE_SAVED_AUDIT",report["verdict"],"epochs",observed,
          "max_bol_gap",err["bolometric_gain_relative"],
          "mean_freq",err["mean_frequency_abs"],
          "Simpson_trapezoid",err["rho_trapezoid_vs_simpson"],flush=True)
    return report

if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--source",required=True,type=Path)
    a.add_argument("--output",required=True,type=Path)
    z=a.parse_args();saved_audit(z.source,z.output)
