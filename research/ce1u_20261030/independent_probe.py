"""Nonrigorous independent GL40 pressure falsification of proved GL source bound."""
import json
import numpy as np
from research.ce1u_20261030.certified_gl_source import sample_gl_source, certify_gl_source
from research.ce1t_20261030.cellwise_gl_rust import make_cell_rays

def pressure_direct(rays,mass,ell):
    b=np.exp(-2*ell);v=np.exp(-sum(ell));q=np.asarray(rays)*np.sqrt(b)
    r=np.linalg.norm(q,axis=1)
    return v*np.einsum('q,qi->i',np.asarray(mass)/r,q*q)

def run():
    # GL40 reuses the *same continuous table*, but this is still only a numerical
    # reference; it does not prove an interval inequality.
    nref,wref=make_cell_rays(40)
    rng=np.random.default_rng(20261030)
    states=[np.zeros(3),np.array([.07,.07,.07]),np.array([.06,.025,.045])]
    states.extend(rng.uniform(0,.07,(32,3)))
    out={}
    for order in (4,6,8):
        src=sample_gl_source(order);cert=certify_gl_source(order,src)
        gaps=[float(max(abs(pressure_direct(nref,wref,e)-src.moments(e)[1]))) for e in states]
        assert max(gaps) < cert['total_pressure_error_upper'],(order,max(gaps),cert)
        out[str(order)]={'states':len(states),'largest_numeric_discrepancy':max(gaps),
                         'MPFR_source_upper':cert['total_pressure_error_upper'],
                         'observed_error_over_bound':max(gaps)/cert['total_pressure_error_upper']}
    print(json.dumps({'status':'SCOPED_INDEPENDENT_NUMERIC_FALSIFICATION_PASS',
      'reference':'GL40, nonrigorous','results':out},indent=2))
if __name__=='__main__':run()
