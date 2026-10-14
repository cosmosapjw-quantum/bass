"""BASS R9 read-only REI LRS Bianchi I geometry-clock consumer.

No chemical trajectory, new REI scientific acceptance, or process dispatch.
The background is the exact prescribed SOURCE-LOCK law, with its originally
rounded binary64 cosmological parameters represented by their declared decimals.
"""
from __future__ import annotations
from decimal import Decimal
from fractions import Fraction
from pathlib import Path
import json
import mpmath as mp

MODEL_LOCK_SHA = "46f818c2f9de890c72f71fa3cc70366b28c42ca0d65190bd905b6310023e7af0"
SCENARIO_LOCK_SHA = "07aa11d2d3fd47d2ed95e9d9161f6205e4d9ba386c27ad43d2b298fcd86d1696"
A_REF = Fraction(1,21)
A_END = Fraction(1,5)
JULIAN_YEAR_S = 31557600
MYR_S = JULIAN_YEAR_S*10**6
CLOCK_ORIGIN = "ELAPSED_GAS_PROPER_TIME_SINCE_ZBAR20"

class ContractHold(ValueError):
    pass

def _input(v):
    if isinstance(v,float): raise ContractHold("HOLD_FLOAT_VS_DECIMAL_LOCK")
    if isinstance(v,Fraction): return mp.mpf(v.numerator)/v.denominator
    return mp.mpf(str(v))

class Background:
    def __init__(self):
        # Values read from hash-pinned BACKGROUND_FAMILY_LOCK.json, not a new fit.
        self.h0 = mp.mpf('67.4')*mp.mpf('1e5')/mp.mpf('3.085677581491367e24')
        self.om = mp.mpf('0.315')
        self.orad = mp.mpf('0.000092')
        self.ol = mp.mpf('0.684908')
        self.aref = mp.mpf(1)/21
        self.aend = mp.mpf(1)/5
        self.href = self.Hf(self.aref)

    def Hf(self,a):
        return self.h0*mp.sqrt(self.orad*a**(-4)+self.om*a**(-3)+self.ol)

    def g(self,a):
        return self.href*(self.aref/a)**3/self.Hf(a)

    def Hq(self,a,q):
        return self.Hf(a)*mp.sqrt(1+(q*self.g(a))**2)

    def _range(self,a,q):
        if a<self.aref or a>self.aend:raise ContractHold("HOLD_OUTSIDE_FROZEN_REI_INTERVAL")
        if abs(q)>mp.mpf('0.01'):raise ContractHold("HOLD_OUTSIDE_SIGNED_Q_FAMILY")

    def integrate_log(self,fn,a0,a1):
        return mp.quad(lambda x:fn(mp.exp(x)),[mp.log(a0),mp.log(a1)])

    def tau(self,a,q):
        self._range(a,q)
        return self.integrate_log(lambda aa:1/self.Hq(aa,q),self.aref,a)

    def clock_shift(self,a,q):
        self._range(a,q)
        if q==0:return mp.mpf(0)
        # Stable difference formula avoids subtracting two ~Gyr times.
        return -self.integrate_log(lambda aa:(1-1/mp.sqrt(1+(q*self.g(aa))**2))/self.Hf(aa),self.aref,a)

    def moments(self,a):
        self._range(a,mp.mpf(0))
        A2=self.integrate_log(lambda aa:self.g(aa)**2/self.Hf(aa),self.aref,a)
        A4=self.integrate_log(lambda aa:self.g(aa)**4/self.Hf(aa),self.aref,a)
        return A2,A4

    def quartic_envelope(self,a,q):
        """Exact functional inequality for f(x)=1-(1+x)^(-1/2), x>=0.

        0 <= x/2-f(x) <= 3 x²/8, hence bounds the true clock.
        The definite integrals here are mp numerical evaluations, not validated
        interval enclosures for their numerical rounding errors.
        """
        self._range(a,q)
        A2,A4=self.moments(a)
        lower=-q*q*A2/2
        upper=lower+3*q**4*A4/8
        return lower,upper,A2,A4


def geometry_clock(a: str, q: str, digits: int = 60):
    if digits < 30 or digits > 100:raise ContractHold("HOLD_PRECISION_SCOPE")
    with mp.workdps(digits):
        b=Background();a1=_input(a);q1=_input(q);b._range(a1,q1)
        shift=b.clock_shift(a1,q1)
        lower,upper,A2,A4=b.quartic_envelope(a1,q1)
        if not(lower <= shift <= upper):raise ContractHold("HOLD_QUARTIC_BOUND_CONTRADICTION")
        if not (mp.mpf(0)<=b.g(a1)<=1):raise ContractHold("HOLD_MONOTONE_G_DOMAIN")
        assert 0<=A4<=A2
        return {
            "model":"PRESCRIBED_STRESS_FREE_AXISYMMETRIC_BIANCHI_I",
            "source_sha256":MODEL_LOCK_SHA,
            "a":mp.nstr(a1,25),"q_ref":mp.nstr(q1,25),
            "delta_tau_seconds":mp.nstr(shift,30),
            "delta_tau_Julian_years":mp.nstr(shift/JULIAN_YEAR_S,23),
            "quadratic_lower_seconds":mp.nstr(lower,30),
            "quartic_upper_seconds":mp.nstr(upper,30),
            "quartic_remainder_width_seconds":mp.nstr(upper-lower,22),
            "uniform_rel_quartic_width_Le_3q2over4":mp.nstr(3*q1*q1/4,12),
            "A2_seconds":mp.nstr(A2,30),"A4_seconds":mp.nstr(A4,30),
            "elapsed_origin":CLOCK_ORIGIN,
            "numerical_quadrature_error":"NOT_RIGOROUSLY_ENCLOSED",
            "source_clock_equivalence":"EXACT_Q_SIGN_PARITY_WITHIN_PRESCRIBED_GEOMETRY",
            "chemistry_abundance_effect":"NOT_COMPUTED",
        }


def milestone_decomposition(a_zero:str, a_case:str, q:str,
                            *, source_pair_bound:bool=False,
                            actual_case_reviewed:bool=False,
                            actual_zero_reviewed:bool=False,
                            digits:int=50):
    """Time shift = geometric clock at ZERO crossing + crossing-position shift.

    Preserve source consistency and owner scientific review prerequisites. This
    cannot turn a partial history into a completed scientific comparison.
    """
    if not source_pair_bound:raise ContractHold("HOLD_SOURCE_PAIR_RELATION_UNVERIFIED")
    if not(actual_case_reviewed and actual_zero_reviewed):
        raise ContractHold("HOLD_SIGNED_HISTORY_NOT_COMPLETED_AND_REVIEWED")
    with mp.workdps(digits):
        b=Background();az=_input(a_zero);ac=_input(a_case);qq=_input(q)
        b._range(az,qq);b._range(ac,qq)
        geom=b.clock_shift(az,qq)
        chemistry_clock=b.integrate_log(lambda aa:1/b.Hq(aa,qq),az,ac)
        observed_total=b.tau(ac,qq)-b.tau(az,mp.mpf(0))
        diff=observed_total-(geom+chemistry_clock)
        assert abs(diff)<mp.mpf('1e-25')*max(1,abs(observed_total))
        return {
            "geometry_seconds":mp.nstr(geom,25),
            "crossing_position_seconds":mp.nstr(chemistry_clock,25),
            "total_seconds":mp.nstr(observed_total,25),
            "decomposition_numeric_check_seconds":mp.nstr(diff,14),
            "source_pair_bound":True,"signed_case_reviewed":True,
            "scientific_error_model":"NUMERICAL/ATOMIC/GEOMETRIC_ERROR_STILL_SEPARATE",
        }


def main():
    import argparse
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument("--a",default="0.2")
    a.add_argument("--q",default="0.01")
    a.add_argument("--out",type=Path)
    args=a.parse_args();out=geometry_clock(args.a,args.q)
    if args.out:
        with args.out.open("x") as f:json.dump(out,f,indent=2)
    print(json.dumps(out,indent=2))
if __name__=="__main__":main()
