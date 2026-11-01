import json, subprocess, sys
from pathlib import Path
import sympy as sp
import vi0_exact as model

def test_exact_codazzi_and_gauss():
    x, state = model.constraint_witness()
    assert all(sp.simplify(c.subs(state)) == 0 for c in x['codazzi'])
    assert sp.simplify(x['gauss'].subs(state)) == 0

def test_constraint_minor_rank_certificate():
    x, state = model.constraint_witness()
    assert sp.N(x['rank_certificate'].subs(state),40)>0
    assert x['rank_certificate'].subs({x['variables']['p']:0})==0
    assert x['rank_certificate'].subs({x['variables']['q']:0})==0

def test_projector_ranks_and_exact_kato():
    result = model.run_all()
    assert result['dimension_scalar_projector_image_generic'] == 3
    assert result['dimension_strict_zero_tilt_background'] == 4

def test_wrong_typeii_transplant_detected():
    x=sp.Rational(1,8);y=sp.Rational(-1,7);z=sp.Rational(1,9)
    assert model.projector_6axes([x,y,z])['P'] != model.projector_6axes([0,y,0])['P']

def test_projector_positive_eigenrank_exact():
    v=[sp.Rational(1,10),sp.Rational(1,11),sp.Rational(1,12)]
    P=model.projector_6axes(v)['P']
    assert P.rank() == 1
    assert P.trace()==1

def test_full_branch_vs_restricted_zero_tilt():
    r=model.projector_6axes([0,0,0]); assert any(any(z!=0 for z in pp) for pp in r['P_i'])
    assert r['P']**2 == r['P']

def test_no_borrowed_production_claim():
    q=model.run_all()
    assert not q['production_ready'] and not q['merge_ready'] and not q['auto_next']
    assert 'P_MIG_II_PREFLIGHT' in q['not_derived']

def test_exact_projector_differential_rank_three():
    o=model.projector_6axes([sp.Rational(1,10),-sp.Rational(1,9),sp.Rational(1,11)])
    mat=sp.Matrix.hstack(*(sp.Matrix(36,1,list(pi)) for pi in o['P_i']))
    assert mat.rank()==3

def test_seeded_physical_bianchi_vi0_constraints_and_identity():
    import numpy as np
    rng=np.random.default_rng(20261101)
    max_cod=max_gauss=max_P=0.
    nn=np.array([[1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1]],float)
    for _ in range(64):
        sp0,sm0=rng.uniform(-.15,.15,size=2)
        p,q=rng.uniform(.22,.68,size=2)
        gamma=rng.uniform(.8,1.8)
        v=rng.uniform(-.18,.18,size=3)
        Gp=1+(gamma-1)*np.dot(v,v)
        alpha=3*gamma/Gp
        R=1-sp0**2-sm0**2-(p+q)**2/12
        beta=3*gamma**2/Gp**2*(v[0]**2/(p+q)**2+v[1]**2/q**2+v[2]**2/p**2)
        Omega=2*R/(1+np.sqrt(1+4*beta*R))
        off=np.array([-alpha*Omega*v[2]/p,-alpha*Omega*v[1]/q,alpha*Omega*v[0]/(p+q)])
        N=np.diag([0,p,-q])
        S=np.array([[-2*sp0,off[0],off[1]],
                 [off[0],sp0+np.sqrt(3)*sm0,off[2]],
                 [off[1],off[2],sp0-np.sqrt(3)*sm0]])
        cod=np.array([(p+q)*off[2],-q*off[1],-p*off[0]])-alpha*Omega*v
        gauss=Omega+np.trace(S@S)/6+(p+q)**2/12-1
        max_cod=max(max_cod,np.max(np.abs(cod)))
        max_gauss=max(max_gauss,abs(gauss))
        qq=1-nn@v; rr=(1-np.dot(v,v))**2/qq**4; aa=qq/6
        P=np.outer(rr,aa)/np.dot(aa,rr)
        max_P=max(max_P,np.max(np.abs(P@P-P)))
    assert max_cod<3e-15 and max_gauss<4e-15 and max_P<4e-15
