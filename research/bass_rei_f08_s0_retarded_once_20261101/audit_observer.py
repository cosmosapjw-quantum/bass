#!/usr/bin/env python3
"""Independent pure-stdlib audit of published BASS→REI retarded Stokes samples.

This is a same-author data-level countercheck, not an independent model or
a distinct-author blind referee.
"""
from pathlib import Path
import csv,gzip,hashlib,json,math
ROOT=Path(__file__).resolve().parent
RESULT=ROOT/"results"
def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):h.update(b)
    return h.hexdigest()
def read(path):
    with gzip.open(path,"rt",newline="") as f:return list(csv.DictReader(f))
def run():
    r=json.loads((RESULT/"RESULT.json").read_text())
    skyfile=RESULT/"RETARDED_ONCE_THOMSON_OBSERVER_STOKES.csv.gz"
    clockfile=RESULT/"RETARDED_ONCE_SCATTER_TIME_CHRONOLOGY.csv.gz"
    assert sha(skyfile)==r["sky_sha256"]
    assert sha(clockfile)==r["chronology_sha256"]
    sky=read(skyfile)
    clock=read(clockfile)
    assert len(sky)==r["sky_rows"]==2048
    assert len(clock)==r["chronology_rows"]==48
    m1={}; max_parity_rel=0.;max_flrw=0.;max_stokes=0.; max_bad_chron=0.
    for record in sky:
        key=(record["branch"],float(record["observer_time_s"]))
        m1.setdefault(key,[]).append(record)
        I,Q,U,N=[float(record[k]) for k in ("I1_ev_per_H_sr","Q1_ev_per_H_sr","U1_ev_per_H_sr","N1_photons_per_H_sr")]
        pol=math.hypot(Q,U)
        assert all(map(math.isfinite,(I,Q,U,N)))
        assert 0<N<0.1 and 0<I<10 and pol<=I*(1+1e-12)
        max_stokes=max(max_stokes,abs(pol/I-float(record["P1_over_I1"])))
        s,e,t=map(float,(record["mean_birth_time_s"],record["mean_scatter_time_s"],record["observer_time_s"]))
        max_bad_chron=max(max_bad_chron,max(s-e,e-t,0.))
        assert 0<=s<=e<=t
        if key[0]=="S0_FLRW":max_flrw=max(max_flrw,pol/I)
    assert len(m1)==4 and max_flrw<1e-10
    source_checks=[]
    for s in r["summary"]:
        key=(s["branch"],float(s["observer_time_s"]))
        rows=m1[key];assert len(rows)==512
        vI=math.fsum(float(x["I1_ev_per_H_sr"]) for x in rows)/512
        vN=math.fsum(float(x["N1_photons_per_H_sr"]) for x in rows)*4*math.pi/512
        vP=math.fsum(float(x["P1_over_I1"]) for x in rows)/512
        assert math.isclose(vI,s["mean_I1_ev_per_H_sr"],rel_tol=6e-15)
        assert math.isclose(vN,s["sky_integrated_N1_per_H"],rel_tol=6e-15)
        assert math.isclose(vP,s["mean_P1_over_I1"],rel_tol=6e-15)
        index={(int(x["mu_index"]),int(x["phi_index"])):x for x in rows}
        assert len(index)==512
        for (i,j),one in index.items():
            other=index[(15-i,(j+16)%32)]
            I1,I2=float(one["I1_ev_per_H_sr"]),float(other["I1_ev_per_H_sr"])
            Q1,Q2=float(one["Q1_ev_per_H_sr"]),float(other["Q1_ev_per_H_sr"])
            U1,U2=float(one["U1_ev_per_H_sr"]),float(other["U1_ev_per_H_sr"])
            N1,N2=float(one["N1_photons_per_H_sr"]),float(other["N1_photons_per_H_sr"])
            err=max(abs(I1-I2),abs(Q1-Q2),abs(U1+U2),abs(N1-N2))/max(I1,I2)
            max_parity_rel=max(max_parity_rel,err)
        source_checks.append({"branch":key[0],"observer_time_s":key[1],"N1_H":vN,"mean_pol":vP})
    assert max_parity_rel<1e-8, f"unexpected opposite-sky parity: {max_parity_rel}"
    assert max_bad_chron==0
    for row in clock:
        t_s=float(row["scatter_time_s"]);t_o=float(row["observer_time_s"])
        assert 0<t_s<t_o<=1e13
        for name in ("sky_mean_local_I_gain_ev_per_H_sr_s","scatter_quadrature_weight_s"):
            assert float(row[name])>0
    out={"schema":"BASS_REI_F08_S0_RETARDED_ONCE_INDEPENDENT_READBACK_V1",
         "scope":"DATA_LEVEL_SAME_AUTHOR_HOSTILE_AUDIT_NOT_DISTINCT_AUTHOR",
         "status":"PASS_WITH_SOURCE_EQUIVALENCE_HOLD",
         "number_of_independent_physical_histories":2,
         "number_of_sky_ray_records":len(sky),
         "number_of_scatter_chronology_records":len(clock),
         "max_Stokes_fraction_residual":max_stokes,
         "max_sky_antipodal_parity_rel":max_parity_rel,
         "max_FLRW_P1_over_I1":max_flrw,
         "source_metrics":source_checks,
         "original_REI_F08":"HOLD",
         "original_REI_F05":"BLOCKED_TICK160/131072",
         "canonical":"28/88_REPORTED_DELTA_0",
         "source_original_discrete_photon_state_replay":"NOT_CERTIFIED",
         "science_model":"CONDITIONAL_PRESCRIBED_HHE_AND_METRIC_FIRST_AND_LAST_ONCE_SCATTERED"}
    (RESULT/"INDEPENDENT_AUDIT.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("PASS_INDEPENDENT_DATA_READBACK",json.dumps({k:out[k] for k in
     ("number_of_sky_ray_records","number_of_scatter_chronology_records",
      "max_Stokes_fraction_residual","max_sky_antipodal_parity_rel",
      "max_FLRW_P1_over_I1")},sort_keys=True))
    return out
if __name__=="__main__":run()
