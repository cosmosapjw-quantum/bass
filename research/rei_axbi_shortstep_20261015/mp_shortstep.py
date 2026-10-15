"""Independent 80-digit mpmath proper-time short-increment reference, real REI AX03.

Integrates over the exact BINARY64 endpoint float values as high precision
dyadic rationals; not over rounded requested nominal delta. Original cosmology
parameter float values are also interpreted by exact mp.mpf(float), avoiding
untracked changes of source decimals between the two methods.
"""
from __future__ import annotations
import json,math,sys
from pathlib import Path
import mpmath as mp
import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from shortstep import gauss_increment,HermiteClock,stable_dx
from axbi_provider import Background,Family,_read_lock

def mfloat(x):
    return mp.mpf(float(x))

def exact_increment(bgx:Background,a0,a1,dps=80):
    if not bgx.aref<=a0<=a1<=bgx.aend:raise ValueError("AX03 scale")
    mp.mp.dps=dps
    aa=mfloat(a0);bb=mfloat(a1)
    if aa==bb:return mp.mpf(0),mp.mpf(0)
    # Exact current *binary64* endpoint values; not nominal unrounded x1/x0.
    dx=mp.log1p((bb-aa)/aa)
    c=bgx.source["cosmology"]
    h0=mfloat(c["H0_per_s"])
    om=mfloat(c["Omega_m"]);orr=mfloat(c["Omega_r"]);ol=mfloat(c["Omega_lambda"])
    ar=mfloat(bgx.aref)
    q=mfloat(bgx.case.q_ref)
    def hf(a):
        return h0*mp.sqrt(om/a**3+orr/a**4+ol)
    shref=q*hf(ar)
    def r(x):
        a=aa*mp.exp(x)
        s=shref*(ar/a)**3
        h=mp.sqrt(hf(a)**2+s*s) if bgx.case.family=="PhysicalDensityFixed" else hf(a)
        return 1/h,s/h
    dt=mp.quad(lambda x:r(x)[0],[0,dx])
    db=mp.quad(lambda x:r(x)[1],[0,dx])
    return dt,db

def run():
    mp.mp.dps=80
    all_cases=[(0,"PhysicalDensityFixed"),(.005,"PhysicalDensityFixed"),
              (-.005,"PhysicalDensityFixed"),(.01,"PhysicalDensityFixed"),
              (-.01,"PhysicalDensityFixed"),(.01,"SameHDiagnostic")]
    data=[]
    for q,family in all_cases:
        bg=Background(Family(q,family));table=HermiteClock(bg)
        for a0 in (.05,.1,.18):
            for scale in (1e-4,1e-8,1e-10,1e-12,"nextfloat"):
                a1=np.nextafter(a0,math.inf) if scale=="nextfloat" else float(a0*(1+scale))
                exact_t,exact_b=exact_increment(bg,a0,a1)
                gt,gb=gauss_increment(bg,a0,a1,order=4)
                gt8,gb8=gauss_increment(bg,a0,a1,order=8)
                ht,hb=table.increment(a0,a1)
                naive=bg.at_a(a1)["proper_elapsed_s"]-bg.at_a(a0)["proper_elapsed_s"]
                # Since high precision reference is defined on exact float endpoints,
                # relative differences are scientific error observables, not performance alone.
                rt=float(abs((mfloat(gt)-exact_t)/exact_t))
                rh=float(abs((mfloat(ht)-exact_t)/exact_t))
                rn=float(abs((mfloat(naive)-exact_t)/exact_t))
                if exact_b:
                    rb=float(abs((mfloat(gb)-exact_b)/exact_b))
                    hbrel=float(abs((mfloat(hb)-exact_b)/exact_b))
                else:rb=0.0;hbrel=0.0
                data.append({"family":family,"q":q,"a0":a0,"a1":float(a1),
                   "nominal_relative_delta":scale,
                   "actual_delta_ln_a":stable_dx(a0,a1),
                   "mp_t_sec":mp.nstr(exact_t,48),"mp_b":mp.nstr(exact_b,48),
                   "gauss4_t_sec":gt,"gauss8_t_sec":gt8,
                   "hermite_t_sec":ht,"naive_time_subtraction_sec":naive,
                   "relative_t_gauss4_to_mp":rt,
                   "relative_t_hermite_to_mp":rh,
                   "relative_t_naive_to_mp":rn,
                   "relative_b_gauss4_to_mp":rb,
                   "relative_b_hermite_to_mp":hbrel,
                   "actual_dt_gauss4_to_gauss8":abs(gt-gt8),
                   "failure_prevented":(rn>1e-8 and rt<1e-10)})
    maximum=lambda field:max(row[field] for row in data)
    return {"schema":"bass.rei.axbi.shortstep_independent_mp80.v1",
       "source_model":"actual frozen AX03 PhysicalDensityFixed signed cases and SAME_H counterfactual",
       "reference":"mpmath80 high precision integral of dt/dln(a),db/dln(a) at exact supplied float64 a0,a1",
       "n_cases":len(all_cases),"n_intervals":len(data),
       "max_relative_time_error":{
          "gauss4":maximum("relative_t_gauss4_to_mp"),
          "Hermite501":maximum("relative_t_hermite_to_mp"),
          "naive_cumulative_subtraction":maximum("relative_t_naive_to_mp")},
       "max_relative_b_error":{
          "gauss4":maximum("relative_b_gauss4_to_mp"),
          "Hermite501":maximum("relative_b_hermite_to_mp")},
       "cases_naive_exceeds_1e-8_but_gauss_within_1e-10":sum(x["failure_prevented"] for x in data),
       "true_certified_global_error":None,"float_input_identity":"exact dyadic of supplied float64 inputs",
       "rows":data}

if __name__=="__main__":
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument("--output",type=Path,required=True)
    a=parser.parse_args()
    if a.output.exists():raise FileExistsError(a.output)
    out=run()
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps({k:v for k,v in out.items() if k!="rows"},indent=2))
