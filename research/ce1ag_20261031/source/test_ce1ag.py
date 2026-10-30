"""Bounded adversarial tests for the exact continuum shear-work sign certificate."""
import csv
from fractions import Fraction as F
from pathlib import Path
import hashlib
import importlib.util
import math
import sys
import numpy as np
import pytest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import certify_continuum_sign as p


def test_source_exact_binary64_identity():
    src=p.MU.tobytes()+p.PHI.tobytes()+p.CELLS.tobytes()+p.SHEAR.tobytes()
    assert hashlib.sha256(src).hexdigest()==p.ORIGINAL_SOURCE_SHA
    assert p.certify()[0]['source_array_sha256']==p.ORIGINAL_SOURCE_SHA


def test_actual_parent_source_when_repository_present():
    orig=HERE.parents[1]/'ce1af_20261030'/'input'/'cellwise_gl_rust.py'
    if not orig.exists():
        pytest.skip('Full parent Git source is not mounted in local isolated sandbox; verify on PR CI')
    spec=importlib.util.spec_from_file_location('original_cellwise',orig)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    assert mod.frozen_source_identity()==p.ORIGINAL_SOURCE_SHA
    for a,b in ((mod.MU,p.MU),(mod.PHI,p.PHI),(mod.CELL_E,p.CELLS),(mod.SHEAR,p.SHEAR)):
        assert a.dtype==b.dtype and a.tobytes()==b.tobytes()


def test_rational_horizon_and_work_certificate():
    cert,rows=p.certify()
    v={k:F(x) for k,x in cert['bounds_rational'].items() if k in ('q_uniform_strict_lower','E_uniform_strict_lower','theta_lower','shear_abs_upper')}
    assert v['q_uniform_strict_lower']>F(1,5000)
    assert v['E_uniform_strict_lower']>F(7,10)
    assert v['theta_lower']==F(25,17)
    assert v['shear_abs_upper']==F(15317,75000)
    assert len(rows)==401


def test_bound_curve_is_monotone_and_positive():
    _,rows=p.certify()
    t=[F(r[0]) for r in rows]
    q=[float(r[2]) for r in rows]
    e=[float(r[3]) for r in rows]
    w=[float(r[4]) for r in rows]
    assert t[0]==0 and t[-1]==F(2,25) and all(b>a for a,b in zip(t,t[1:]))
    assert all(b<a for a,b in zip(q,q[1:]))
    assert all(b<a for a,b in zip(e,e[1:]))
    assert all(b<a for a,b in zip(w,w[1:]))
    assert all(z>1/5000 for z in q)
    assert all(z>.7 for z in e)
    assert all(z>7/50000 for z in w)


def test_exact_moment_upper_wi_and_source_tamper(monkeypatch):
    c,_=p.certify()
    b=c['bounds_rational']
    assert F(b['initial_w_i_upper'])==F(37,100)
    assert F(b['horizon_w_i_upper'])==F(37,79)<F(2,3)
    xx=p.CELLS.copy();xx[0,0]=.11
    monkeypatch.setattr(p,'CELLS',xx)
    with pytest.raises(AssertionError,match='source_array_sha_mismatch'):
        p.certify()


def independent_moments(order,ell):
    nodes,ws=np.polynomial.legendre.leggauss(order)
    energy=0.; press=np.zeros(3); fourth=np.zeros((3,3))
    for i in range(2):
        for j in range(3):
            for k in range(order):
                mu=(p.MU[i]+p.MU[i+1])/2+(p.MU[i+1]-p.MU[i])*nodes[k]/2
                for l in range(order):
                    t=(p.PHI[j]+p.PHI[j+1])/2+(p.PHI[j+1]-p.PHI[j])*nodes[l]/2
                    phi=math.pi*t/2
                    n=np.array([math.sqrt(1-mu*mu)*math.cos(phi),math.sqrt(1-mu*mu)*math.sin(phi),mu])
                    mass=float(p.CELLS[i,j])*ws[k]*ws[l]/4
                    v=n*n*np.exp(-2*ell)
                    rr=math.sqrt(sum(v));x=v/(rr*rr)
                    wt=mass*rr*math.exp(-sum(ell))
                    energy+=wt; press+=wt*x;fourth+=wt*np.outer(x,x)
    return energy,press,fourth


@pytest.mark.parametrize('order',[3,5])
def test_independent_quadrupole_work_derivative(order):
    ell=np.array([.017,.024,.031]);h=np.array([.67,.45,.50]);eps=1e-6
    energy,press,fourth=independent_moments(order,ell)
    Eplus,Pplus,_=independent_moments(order,ell+eps*h)
    Eminus,Pminus,_=independent_moments(order,ell-eps*h)
    H=h.mean();sg=h-H;w=press/energy;q=sg@w
    wdot=-2*sg*w+(fourth/energy)@sg+q*w
    pid=press-energy/3
    sigdot=-3*H*sg+pid
    qdot_expected=sigdot@w+sg@wdot
    qdot_closed=(-3*H*q+energy*np.sum((w-1/3)**2)
         -2*np.sum(sg*sg*w)+(sg@fourth@sg)/energy+q*q)
    assert abs(qdot_expected-qdot_closed)<4e-14
    # First central-difference only the exact integral dependence at fixed h.
    wplus=Pplus/Eplus;wminus=Pminus/Eminus
    qdot_fd=sigdot@w+sg@((wplus-wminus)/(2*eps))
    assert abs(qdot_fd-qdot_closed)<4e-10
    assert energy>0 and abs(sum(press)-energy)<3e-14
    assert np.linalg.eigvalsh(fourth).min()>-5e-16


def test_generated_row_count_when_present():
    out=p.ROOT/'data'/'CE1AG_RIGOROUS_LOWER_CURVE_401.csv'
    if not out.exists(): pytest.skip('Run certificate producer first')
    with out.open() as f:rows=list(csv.DictReader(f))
    assert len(rows)==401 and list(rows[0])==['u_rational','u','q_lower','E_lower','W_lower']
