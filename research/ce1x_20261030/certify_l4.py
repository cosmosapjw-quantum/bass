"""CE1-X: exact-rational 6-cell source certificate for reflection-even l=4 sky.

Uses the original CE1-U exact rational/Machin/pi/sqrt2 source moment engine from
PR264, not the pressure-only bound; source = original six positive physical
cells versus exact-real stored binary64 GL6/GL8 ray/mass measure.

Certified same-geometry delta-K4, plus monotone CE1-W MPFR192 logscale carrier
for *the original 4/8/16-panel RK4-Hermite paths*. BASS Rust used separately
as the independent stored-source binary64 harmonic evaluator.

NO blackbody, polarization, Doppler tilt, statistical covariance, DOP853
interval certificate, or full formal Python/MPFR validation.
"""
from __future__ import annotations

import argparse
from fractions import Fraction as F
import json
import math
from pathlib import Path
from time import perf_counter

import numpy as np
from research.ce1v_20261030.donor import ce1u_cert_source as ex

K=12
Q=F(1,11)
PREF=F(6,5)
MAX_MASS=F(91,100)
DEGREE_BOUND=14
SOURCE_SHA="022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035"
RUST_BLOB="a29b12b5e7b0d529bddaf9eac53cfdb984ddaa84"
PARENT_CI_RUN=40985138735
EXPECTED_RAYS={
  6:("6f6e5d0797404521abd51cb8394a8b2beca3e96b392924b9ad30b2093098d957",
     "56cb2c5baabdcf10355cc7ddf2f1cf41ad8a131d890e285320e39bab52758199"),
  8:("90e29d100d35dc7ac31f9d75f7d6d4c2d423d90ad487ec0922246bc8f39891cb",
     "2c0b9ca7d1845458639217fae0a86b3339c32f57f9f71dd6c649c3408d319a79"),
}
# These are exact-display roundtrips of MPFR outward upper endpoints of the
# previously completed final-head PR268 CI, not separate DOP853 sample errors.
PARENT_CERTIFIED_ELL={
  6:{4:2.0790956675592526e-7,8:2.5584142381590396e-8,16:3.173187675590132e-9},
  8:{4:2.0790955724813467e-7,8:2.5584132916752962e-8,16:3.1731782487970456e-9},
}
PARENT_CERTIFIED_PATH_COEFFICIENT_SHA={
  6:{
    4:"d1f439768f0540dd71cb0beedf7ff4c57dabff47e6c270f6229a0eec4942b471",
    8:"5d8805b2f82a7eb91d73ad9fe256106c4a13e26005e68082e5f97c71ee6497e0",
    16:"76d05a20e9ef303f09ed224dd94d234f6bef9d94ac36657ea8cff4fab9129baa",
  },8:{
    4:"00dcd7c13b96350521b9c298bfb0057cea5cfca60721f0add84e9125139d49d1",
    8:"f664a34c087ed989330339a3be7b939c8ce701c42de206a4214cfab5275a5c9b",
    16:"30a40a63f4a19f0f3132f1d0ec04d3f38ead288a834cbf770ad2ef8d2d079bef",
  }
}
PI4_UP=F(13) # upper for 4pi; valid pi<22/7
GEOMETRY_DK_DELL_UP=F(41) # exceeds exact 4pi(1+sqrt(20)/2)
E_MIN=F(3,5)


def binomial_abs(beta:F,k:int)->F:
    z=F(1)
    for j in range(k):
        z*=F(beta-j,j+1)
    return abs(z)


def tail(beta:F)->F:
    # |choose(beta,k)|<=1 for beta=+/-1/2.
    # |choose(-3/2,k)|<=2k+1 for k>=0.
    p=Q**(K+1)
    if beta==F(-3,2):
        return p*(F(2*K+3)/(1-Q)+2*Q/(1-Q)**2)
    if beta in (F(1,2),F(-1,2)):
        return p/(1-Q)
    raise ValueError("Unsupported exact binomial order")


def ceil_decimal(x:F,digits:int=27)->str:
    """Exact nonnegative rational ceiling, displayed with fixed decimal digits."""
    if x<0:raise ValueError("Positive certificate required")
    scale=10**digits
    integer=(x.numerator*scale+x.denominator-1)//x.denominator
    return f"{integer//scale}.{integer%scale:0{digits}d}"


def _error_moments(order):
    if ex.SOURCE_SHA!=SOURCE_SHA:
        raise ValueError("Original six physical cells changed")
    # K+1 in donor means total moment order 1..K+2=14 (not K+1).
    stored,hashes,_,rays,normgap=ex.gl_moments_exact(order,K+1)
    if rays!=6*order*order or (hashes["ray_sha256"],hashes["mass_sha256"])!=EXPECTED_RAYS[order]:
        raise ValueError("Exact-real stored GL binary source identity mismatch")
    if not F(0)<=normgap<F(1,10**12):
        raise ArithmeticError("Nonunit GL ray correction is not bounded")
    # The donor does not include degree-zero in its 559 pressure monomials.
    # Include the initial continuum-vs-stored *exact binary mass* discrepancy.
    qray,wray=ex.make_cell_rays(order)
    mass0=sum((F.from_float(float(w)) for w in wray),F(0))
    stored[(0,0,0)]=mass0
    if not F(89,100)<mass0<F(91,100):
        raise ArithmeticError("GL mass outside original positive bounds")
    D={}
    for abc,value in stored.items():
        low,high=ex.continuum_interval(ex.continuum_symbol(*abc))
        if low>high:
            raise ArithmeticError("Reversed exact continuum moment enclosure")
        D[abc]=max(abs(low-value),abs(high-value))
    if len(D)!=len(ex.all_monos(K+1))+1:
        raise ArithmeticError("Incomplete exact even monomial basis")
    return D,hashes,normgap,len(D)


def _term_error(power:tuple[int,int,int],D:dict,normgap:F)->dict:
    degree=sum(power)
    if degree not in (0,1,2):
        raise ValueError("Only original l4 polynomial monomial degrees 0/1/2")
    beta=F(1,2)-degree
    finite=F(0)
    for k in range(K+1):
        s=F(0)
        for i in range(k+1):
            for j in range(k-i+1):
                h=k-i-j
                idx=(power[0]+i,power[1]+j,power[2]+h)
                if idx not in D:
                    raise ArithmeticError("Missing exact six-cell moment "+str(idx))
                multinomial=F(math.factorial(k),
                              math.factorial(i)*math.factorial(j)*math.factorial(h))
                s+=multinomial*D[idx]
        finite+=binomial_abs(beta,k)*Q**k*s
    # For each monomial numerator the continuum integral is <.91 and
    # the stored term is <=2 times positive stored mass <.91, sum <3.
    bounded_tail=3*tail(beta)
    # Stored ray norm^2 = 1+delta. On |X|<1/11, |delta|<1e-12,
    # both radicands >=0.83. For beta>=-3/2, derivative <=3,
    # numerator <=2, prefactors <=6/5, so 8 sum(w |delta|) dominates.
    offunit=8*normgap
    result=PREF*(finite+bounded_tail)+offunit
    return {"bound":result,"finite":finite,"tail":bounded_tail,"offunit":offunit}


def certify(order:int, time_evidence:dict)->dict:
    if type(order) is not int or order not in EXPECTED_RAYS:
        raise ValueError("Only the exact locked GL6/GL8 sources are in scope")
    started=perf_counter()
    D,hashes,normgap,count=_error_moments(order)
    requested={
      "E":(0,0,0),
      "mz":(0,0,1),"mzz":(0,0,2),
      "mx":(1,0,0),"my":(0,1,0),
      "mxz":(1,0,1),"myz":(0,1,1),
      "mxx":(2,0,0),"mxy":(1,1,0),"myy":(0,2,0)
    }
    T={key:_term_error(p,D,normgap) for key,p in requested.items()}
    # Exact rational overestimates of the three Condon-Shortley
    # positive reflection-even l=4 harmonic normalization factors.
    eps={
      "a40":F(1,9)*(35*T["mzz"]["bound"]+30*T["mz"]["bound"]+3*T["E"]["bound"]),
      "a42":F(7,20)*(7*T["mxz"]["bound"]+7*T["myz"]["bound"]
                       +T["mx"]["bound"]+T["my"]["bound"]),
      "a44":F(1,2)*(T["mxx"]["bound"]+6*T["mxy"]["bound"]+T["myy"]["bound"]),
    }
    E=T["E"]["bound"]
    # E_cont, E_stored >= 3/5; |a_stored|<=E_stored because
    # max_l4m |Y_lm|<=sqrt(9/(4pi))<1; 4pi<13.
    alpha={key:PI4_UP/E_MIN*(value+E) for key,value in eps.items()}
    d=max(alpha.values())
    # kernel = (alpha40u*alpha40v +2alpha42u*alpha42v
    #           +2alpha44u*alpha44v)/9.
    # |alpha_m|<=13 at either epoch for either positive source.
    K_SOURCE=F(130,9)*d
    cases={}
    if time_evidence.get("parent_head")!="2d5076ecb2307cea39c1b608396c34050021ebc3":
        raise ValueError("Fresh time evidence is not computed from the original CE1-W parent")
    fixed=time_evidence["cases"][str(order)]
    if not fixed.get("source_contract_not_changed"):
        raise ValueError("Time-panel source SHA mutation")
    for steps in (4,8,16):
        validated=fixed["cases"][str(steps)]
        if (validated["source_ray_sha256"]!=hashes["ray_sha256"]
            or validated["source_mass_sha256"]!=hashes["mass_sha256"]
            or validated["steps"]!=steps or validated["u_end"]!=.08
            or validated["target_h"]!=1e-5 or not validated["target_met"]):
            raise ValueError("Fresh MPFR192 path/source identity, units or fixed target conflict")
        ell=F.from_float(float(validated["final_ell_upper"]))
        if not F(0)<ell<F(1,10**5):
            raise ValueError("Fresh whole-path MPFR192 logscale carrier invalid")
        # The parent outward positive comparison is monotonic on
        # all panels; the terminal ell bound works at both epochs.
        # Each partial geometric derivative <=41 for l4 kernel;
        # three logscales at two epochs => 6*41*ell.
        geo=F(246)*ell
        total=K_SOURCE+geo
        cases[str(steps)]={
            "geometry_kernel_upper_exact":str(geo),
            "geometry_kernel_upper_ceil_27":ceil_decimal(geo),
            "source_kernel_upper_exact":str(K_SOURCE),
            "source_kernel_upper_ceil_27":ceil_decimal(K_SOURCE),
            "total_cross_kernel_upper_exact":str(total),
            "total_cross_kernel_upper_ceil_27":ceil_decimal(total),
            "geometry_ell_upper_f64":float(ell),
            "parent_path_coefficients_sha256":validated["path_sha256"]["coefficients"],
            "fresh_time_mpfr_h_upper":validated["final_h_upper"],
            "fresh_time_mpfr_carrier_SHA_BINDING":"EXACT_IN_SAME_CI",
            "valid_for_both_epochs":"all u,v in [0,0.08] on certified original Hermite path",
        }
    result={
      "schema":"bass.ce1x.exact_rational_l4_source_and_mpfr_geometry.v1",
      "order":order,"positive_octant_rays":6*order*order,
      "physics":"Original exact binary64 six positive angular cells, massless collisionless Bianchi I",
      "original_physical_source_sha256":SOURCE_SHA,
      "source_ray_sha256":hashes["ray_sha256"],
      "source_mass_sha256":hashes["mass_sha256"],
      "source_proof":"Original six cell exact angular even monomials Q(sqrt2,pi) vs exact stored GL dyadic rationals",
      "binomial_K":K,"binomial_radius":str(Q),
      "monomial_moment_count":count,"maximum_total_monomial_order":DEGREE_BOUND,
      "offunit_weighted_norm_error_exact":str(normgap),
      "energy_source_error_upper":str(E),"energy_source_error_ceil_27":ceil_decimal(E),
      "harmonic_source_errors":{k:{"exact":str(x),"ceil_27":ceil_decimal(x)} for k,x in eps.items()},
      "fractional_harmonic_source_errors":{k:{"exact":str(x),"ceil_27":ceil_decimal(x)} for k,x in alpha.items()},
      "source_only_cross_kernel_error":str(K_SOURCE),
      "source_only_cross_kernel_error_ceil_27":ceil_decimal(K_SOURCE),
      "time_path_cases":cases,
      "cost_source_moment_seconds":perf_counter()-started,
      "proof_scope":"Uniform all-geometry [0,.08]^3 source, composed with PR268 MPFR192 original RK4/Hermite geometry ell carrier; not DOP853",
      "upper_dag":"9/15","ce1":"PARTIAL",
      "production_ready":False,"merge_ready":False,"auto_next":False,
      "whole_program_formal_verification":"NOT_RUN",
    }
    print(f"CE1X_GL{order}_SOURCE_L4_EXACT_PASS",
          f"E={ceil_decimal(E)}",
          f"a40={ceil_decimal(eps['a40'])}",
          f"source_K4={ceil_decimal(K_SOURCE)}",
          f"fullK4_4p={cases['4']['total_cross_kernel_upper_ceil_27']}",
          f"elapsed={result['cost_source_moment_seconds']:.2f}",flush=True)
    return result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",required=True)
    parser.add_argument("--time-certificate",required=True,
                        help="Fresh actual 6-case MPFR192 CE1-W result from this same CI")
    args=parser.parse_args()
    time_data=json.loads(Path(args.time_certificate).read_text())
    results={str(n):certify(n,time_data) for n in (6,8)}
    destination=Path(args.output)
    destination.parent.mkdir(exist_ok=True,parents=True)
    destination.write_text(json.dumps({
        "unit":"CE1X_NATIVE_RUST_L4_REAL_SKY_SOURCE_AND_GEOMETRY",
        "source":SOURCE_SHA,"parent_pr":268,"sibling_theory_pr":269,
        "BASS_original_Rust_blob":RUST_BLOB,
        "cases":results,"new_top_level_nodes":0,"upper_dag":"9/15",
        "production_ready":False,"merge_ready":False,"auto_next":False,
    },indent=2)+"\n")
    return results


if __name__=="__main__":
    main()
