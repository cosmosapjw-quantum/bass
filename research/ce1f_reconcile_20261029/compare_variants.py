"""Compare independently implemented CE1-F radiation on exactly matching binary inputs.

`frozen_sibling_C10.py` is the immutable PR239 reference, source blob
 e1f5e11baada25858f8fb03321f071ed759b6f99; it is not the production module.
"""
from __future__ import annotations
import importlib.util
from fractions import Fraction
from decimal import Decimal, localcontext
import json
import sys
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
from numpy.polynomial.legendre import leggauss
from bianchi.nonperturbative import einstein_tabulated_source as variant

HERE = Path(__file__).resolve().parent
MOD = 'bianchi.nonperturbative._ce1f_sibling_C10_frozen'
SPEC = importlib.util.spec_from_file_location(MOD, HERE/'frozen_sibling_C10.py')
if SPEC is None or SPEC.loader is None:
    raise RuntimeError('Pinned sibling C10 code is absent')
sibling = importlib.util.module_from_spec(SPEC)
sys.modules[MOD] = sibling
SPEC.loader.exec_module(sibling)


def binary_fraction_string(v):
    return str(Fraction.from_float(float(v)))


def exact_stored_energy(source):
    with localcontext() as ctx:
        ctx.prec = 110
        cv=lambda f: Decimal(f.numerator)/Decimal(f.denominator)
        return sum((cv(Fraction.from_float(float(w))) *
                    cv(sum((Fraction.from_float(float(z))**2 for z in q),Fraction())).sqrt()
                    for w,q in zip(source.mass, source.n)), Decimal(0))


def independent_pressure_at(ell, mu, az, energies, n=32):
    """Direct original-physical-cell quadrature, no use of either certificate/kernel."""
    q,w=leggauss(n)
    ell=np.asarray(ell,float); b=np.exp(-2*ell);v=np.exp(-sum(ell));p=np.zeros(3)
    for i in range(len(mu)-1):
        for j in range(len(az)-1):
            m=mu[i]+(q+1)*(.5*(mu[i+1]-mu[i]))
            a=np.pi/2*(az[j]+(q+1)*(.5*(az[j+1]-az[j])))
            mz=m[:,None]**2
            X=(1-mz)*np.cos(a[None,:])**2
            Y=(1-mz)*np.sin(a[None,:])**2
            Z=np.broadcast_to(mz,X.shape)
            squares=np.stack([X,Y,Z],axis=-1)
            radial=np.sqrt(squares@b)
            coeff=w[:,None]*w[None,:]/4
            p+=energies[i][j]*v*b*np.einsum('ab,abi->i',coeff/radial,squares)
    return p


def execute():
    mu=[0.,.5,1.];az=[0.,.25,.75,1.]
    energies=[[.1,.25,.05],[.2,.15,.15]]
    rows=[]
    for refinement in (1,2,4,8):
        a=sibling.TabulatedRadiation(mu,az,energies,refinement=refinement,backend='python_oracle')
        b=variant.TabulatedRadiation(tuple(map(binary_fraction_string,mu)),
            tuple(map(binary_fraction_string,az)),
            tuple(tuple(map(binary_fraction_string,row)) for row in energies),
            refinement=refinement,backend='python_oracle')
        assert a.continuum_energy==b.exact_energy
        ba=sibling.certified_tabulated_pressure(a,[.08]*3)
        bb=variant.certified_tabulated_pressure(b,[0.]*3,[.08]*3)
        ga=sibling.certified_tabulated_geometry(a,end=.08)
        gb=variant.certified_tabulated_geometry(b,end=.08)
        assert Decimal.from_float(gb['energy_max_upper'])>=exact_stored_energy(b)
        assert Decimal.from_float(ga['energy_max_upper'])>=exact_stored_energy(a)
        rng=np.random.default_rng(20261029)
        els=[np.array([0.,0.,0.]),np.array([.01,.04,.07]),np.array([.08,.08,.08])]
        els.extend(rng.uniform(0,.08,(16,3)))
        diffs=[];reference_ratios=[]
        for k,ell in enumerate(els):
            _,pa=a.moments(ell);_,pb=b.moments(ell)
            diffs.append(float(np.max(np.abs(pa-pb))))
            if k<3:
                pref=independent_pressure_at(ell,mu,az,energies)
                reference_ratios.append(float(max(np.max(abs(pa-pref))/ba['bound_max'],
                                                  np.max(abs(pb-pref))/bb['max_pressure_upper'])))
        maxdiff=max(diffs)
        assert maxdiff<2e-14, (refinement,maxdiff)
        assert max(reference_ratios)<1, (refinement,reference_ratios)
        t=np.array([0.,.025,.05,.08])
        y1=solve_ivp(a.rhs,(0,.08),a.initial_state(),t_eval=t,method='DOP853',rtol=1e-11,atol=1e-13)
        y2=solve_ivp(b.rhs,(0,.08),b.initial_state(),t_eval=t,method='DOP853',rtol=1e-11,atol=1e-13)
        assert y1.success and y2.success
        dg=float(np.max(abs(y1.y-y2.y)))
        assert dg<1e-11,(refinement,dg)
        rows.append({'refinement':refinement,'ray_count':len(b.mass),
          'same_exact_continuum_energy':True,'max_pressure_difference':maxdiff,
          'max_coupled_6state_difference':dg,
          'independent_original_cell_quadrature_ratio_max':max(reference_ratios),
          'sibling_source_upper':ba['bound_max'],
          'repaired_source_upper':bb['max_pressure_upper'],
          'sibling_geometry_h_upper':ga['geometry_h_upper'],
          'repaired_geometry_h_upper':gb['geometry_h_upper'],
          'sibling_exact_energy_cap_valid':True,'repaired_exact_energy_cap_valid':True})
    result={'schema':'bass.ce1f.same_physics_reconciliation.v1',
       'sibling_git_sha':'9de0f37955f259b5e9172ce406d1353bf7cc3695',
       'independent_parent_sha':'0286dd0a97f512a2dc6f431e462e64bd65267047',
       'fixed_initial_cap':True,'physical_input':'exact-binary-matched positive table',
       'rows':rows,'time_integrator_certified':False,'upper_dag':'9/15',
       'production_ready':False,'merge_performed':False}
    print(json.dumps(result,indent=2))
    return result

if __name__=='__main__':
    result=execute()
    name=sys.argv[1] if len(sys.argv)>1 else '/tmp/ce1f_comparison.json'
    Path(name).write_text(json.dumps(result,indent=2)+'\n')
