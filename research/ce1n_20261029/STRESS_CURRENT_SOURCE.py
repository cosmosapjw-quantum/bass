"""CE1-N independent exact-rational positive rebind stress (no observational inference)."""
from __future__ import annotations
import json
import time
from fractions import Fraction
from random import Random

from bianchi.nonperturbative.einstein_error_budget import PolynomialRadiation
from bianchi.nonperturbative.einstein_interval import (
    Interval, _ideal_moment, _source_stored_binary, source_full_rounding_bound
)


def stress(ncases=36):
    rng=Random(251029)
    s=PolynomialRadiation(ntheta=8,backend='python_oracle')
    frozen_n=s.n.copy();frozen_mass=s.mass.copy()
    initial=source_full_rounding_bound(s,[0.]*3,[0.]*3,max_K=3)['bounds']
    t=time.perf_counter()
    rows=[]
    for idx in range(ncases):
        # Numerical stored-Q rebinding, not a changed physical continuum M.
        fac_mass=0.45+1.7*rng.random()
        fac_ray=1.+.018*rng.random()
        s.mass=frozen_mass.copy()*fac_mass
        s.n=frozen_n.copy()*fac_ray
        cert=source_full_rounding_bound(s,[0.]*3,[0.]*3,max_K=3)['bounds']
        pressure=_source_stored_binary(s,[Interval(0)]*3)
        gaps=[]
        for i in range(3):
            P=_ideal_moment(s,i,0,0,0)
            lo=Fraction.from_float(pressure[i].lower)
            hi=Fraction.from_float(pressure[i].upper)
            gap=max(Fraction(0),lo-P,P-hi)
            gaps.append(float(gap))
            assert Fraction.from_float(cert[i])>=gap, (idx,i,fac_mass,fac_ray,gap,cert[i])
        rows.append({'case':idx,'mass_factor':fac_mass,'ray_factor':fac_ray,
                     'true_pressure_gap_lower_max':max(gaps),
                     'current_source_bound_upper_max':max(cert),
                     'enclosure_ratio':max(g/c for g,c in zip(gaps,cert) if c>0)})
    return {'schema':'bass.ce1n.independent_positive_source_rebind_stress.v1',
            'cases':len(rows),'axes_tested':len(rows)*3,
            'maximum_gap_over_upper':max(r['enclosure_ratio'] for r in rows),
            'minimum_gap_over_upper':min(r['enclosure_ratio'] for r in rows),
            'original_source_bound':initial,
            'elapsed_seconds':time.perf_counter()-t,
            'all_cases_enclosed':True,'rows':rows}


if __name__=='__main__':
    obj=stress()
    print(json.dumps(obj,indent=2,sort_keys=True))
    print('CE1N_INDEPENDENT_EXACT_RATIONAL_SOURCE_STRESS_PASS')
