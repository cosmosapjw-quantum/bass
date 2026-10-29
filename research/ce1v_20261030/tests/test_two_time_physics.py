"""CE1-V: real BASS six-cell GL6/8 two-epoch kinetic sky science tests."""
import csv
import json
import math
import sys
from pathlib import Path
import numpy as np
import pytest
from scipy.special import sph_harm_y

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'source'))
from build_crosstime import load_channel, product_kernel, sha, EXPECTED_INPUT, ORIGINAL_PHYSICAL_SOURCE_SHA


def model(n):
    return load_channel(ROOT/'inputs'/f'GL{n}_coupled_41epochs.csv',n)


def result():
    return json.loads((ROOT/'data'/'RESULTS.json').read_text())


def direct_source_alms(n, ell, lm=((2,0),(2,2),(4,0),(4,2),(4,4))):
    """Separate SciPy complex-Y_lm projection on immutable six-cell angular measure."""
    edges_mu=[0.,0.5,1.]
    edges_phi=[0.,.25,.75,1.]
    energy=[[.1,.25,.05],[.2,.15,.15]]
    nodes,weights=np.polynomial.legendre.leggauss(n)
    m=np.exp(-np.array(ell,dtype=float))
    vol=m.prod()
    out={i:0.0+0.0j for i in lm}
    mom=0.
    for i in range(2):
      for j in range(3):
       for a in range(n):
        mu=(edges_mu[i]+edges_mu[i+1])/2+(edges_mu[i+1]-edges_mu[i])*nodes[a]/2
        for b in range(n):
         frac=(edges_phi[j]+edges_phi[j+1])/2+(edges_phi[j+1]-edges_phi[j])*nodes[b]/2
         ph=frac*np.pi/2
         q=np.array([np.sqrt(1-mu*mu)*np.cos(ph),np.sqrt(1-mu*mu)*np.sin(ph),mu])
         rr=np.linalg.norm(q*m)
         w=energy[i][j]*weights[a]*weights[b]/4 * vol * rr/8
         for sx in (-1,1):
          for sy in (-1,1):
           for sz in (-1,1):
            s=-q*m*np.array([sx,sy,sz])/rr
            theta=np.arccos(np.clip(s[2],-1,1));phi=np.arctan2(s[1],s[0])%(2*np.pi)
            for l,mm in lm:
             out[(l,mm)]+=w*np.conj(sph_harm_y(l,mm,theta,phi))
            mom+=w
    return out,mom


@pytest.mark.parametrize('n',[6,8])
def test_source_byte_identity_and_physics(n):
    p=ROOT/'inputs'/f'GL{n}_coupled_41epochs.csv'
    assert sha(p)==EXPECTED_INPUT[n]
    ct=json.loads((ROOT/'inputs'/'SOURCE_CONTRACT.json').read_text())
    assert ct['original_physical_six_cell_sha256']==ORIGINAL_PHYSICAL_SOURCE_SHA
    d=model(n)
    assert len(d['u'])==41
    assert np.max(np.abs(d['Hamiltonian_C']))<5e-12
    assert np.max(np.abs(d['E']-(d['P1']+d['P2']+d['P3'])))<2e-12


@pytest.mark.parametrize('n',[6,8])
def test_exact_quadrupole_kinetic_identity(n):
    d=model(n)
    assert np.max(abs(d['a20']-np.sqrt(5/(16*np.pi))*(3*d['P3']-d['E'])))<2e-13
    assert np.max(abs(d['a22']-np.sqrt(15/(32*np.pi))*(d['P1']-d['P2'])))<2e-13
    assert np.max(abs(d['da20']-np.sqrt(5/(16*np.pi))*(3*d['P3prime']-d['Eprime'])))<2e-13
    assert np.max(abs(d['da22']-np.sqrt(15/(32*np.pi))*(d['P1prime']-d['P2prime'])))<2e-13


@pytest.mark.parametrize('n',[6,8])
def test_kernels_symmetric_diagonal_and_derivatives(n):
    d=model(n)
    for l in (2,4):
        k=product_kernel(d,l)
        assert np.max(abs(k['K']-k['K'].T))<1e-16
        assert np.max(abs(k['KF']-k['KF'].T))<1e-14
        assert np.max(abs(np.diag(k['K'])-d[f'C{l}']))<3e-15
        assert np.max(abs(2*np.diag(k['Ku'])-d[f'C{l}prime']))<3e-15
        assert np.max(abs(k['Ku']-k['Kv'].T))<1e-16
        assert np.max(abs(np.diag(k['KF'])-((4*np.pi)/d['E'])**2*d[f'C{l}']))<1e-13
        assert np.max(abs(np.diag(k['KFu']+k['KFv'])-np.gradient(np.diag(k['KF']),d['u'],edge_order=2)))<1e-3


@pytest.mark.parametrize('n',[6,8])
def test_gram_psd_rank_and_cauchy(n):
    d=model(n)
    for l,rank in ((2,2),(4,3)):
        k=product_kernel(d,l)
        assert np.linalg.eigvalsh(k['K']).min()>-5e-17
        assert np.linalg.eigvalsh(k['KF']).min()>-1e-14
        assert np.max(abs(k['rho']))<=1+2e-12
        assert np.max(abs(np.diag(k['rho'])-1))<1e-12
        eig=np.linalg.eigvalsh(k['KF'])
        assert (eig>1e-10).sum()<=rank
        assert k['dist2'].min()>-2e-14


@pytest.mark.parametrize('n',[6,8])
def test_direct_scipy_original_angular_measure(n):
    d=model(n)
    for ix in (0,20,40):
        # Reconstruct ell_i from source CSV, not assumed analytic background.
        with (ROOT/'inputs'/f'GL{n}_coupled_41epochs.csv').open() as f:
            rec=list(csv.DictReader(f))[ix]
        ell=[float(rec[f'ell{k}']) for k in (1,2,3)]
        direct,e=direct_source_alms(n,ell)
        assert abs(e-d['E'][ix])<2e-12
        for (l,m),a in direct.items():
            assert abs(a.imag)<2e-13
            assert abs(a.real-d[f'a{l}{m}'][ix])<4e-12, (n,ix,l,m,a)


def test_two_epoch_direct_harmonic_overlap_GL8():
    n=8;d=model(n)
    with (ROOT/'inputs'/'GL8_coupled_41epochs.csv').open() as f:rows=list(csv.DictReader(f))
    es=[]
    for ix in (0,40):
        ell=[float(rows[ix][f'ell{k}']) for k in (1,2,3)]
        es.append(direct_source_alms(n,ell)[0])
    for l in (2,4):
        K_direct=(es[0][l,0].real*es[1][l,0].real+2*sum((es[0][l,m]*es[1][l,m].conjugate()).real for m in range(2,l+1,2)))/(2*l+1)
        K_comp=product_kernel(d,l)['K'][0,-1]
        assert abs(K_direct-K_comp)<3e-13


@pytest.mark.parametrize('n',[6,8])
def test_independent_five_point_partial_time_derivative(n):
    d=model(n);dt=d['u'][1]-d['u'][0]
    for l in (2,4):
        k=product_kernel(d,l)
        for i,j in ((8,22),(20,37),(35,4)):
            fd=(-k['K'][i+2,j]+8*k['K'][i+1,j]-8*k['K'][i-1,j]+k['K'][i-2,j])/(12*dt)
            assert abs(fd-k['Ku'][i,j])<3e-7, (n,l,i,j,fd,k['Ku'][i,j])


@pytest.mark.parametrize('n',[6,8])
def test_rotational_addition_theorem_even_parity(n):
    z=np.load(ROOT/'data'/f'GL{n}_two_time_rotation_average.npz')
    k2=z['K2_fractional'];k4=z['K4_fractional'];xi=z['xi_even_l2_l4']
    assert xi.shape==(41,41,181)
    assert np.max(abs(xi-xi[:,:,::-1]))<1e-14
    assert np.max(abs(xi-xi.transpose(1,0,2)))<1e-14
    expected=(5*k2+9*k4)/(4*np.pi)
    assert np.max(abs(xi[:,:,0]-expected))<1e-14
    assert np.max(abs(xi[:,:,-1]-expected))<1e-14
    assert np.max(abs(xi[:,:,90]-((5*(-.5)*k2)+(9*(3/8)*k4))/(4*np.pi)))<1e-14


def test_angular_convergence_between_coupled_sources():
    x=result()
    assert x['interchannel']['max_abs_K2delta_GL6_vs_GL8']<1e-10
    assert x['interchannel']['max_abs_K4delta_GL6_vs_GL8']<1e-9
    for n in (6,8):
        ch=x['channels'][f'GL{n}']
        assert ch['endpoints']['2']['rho_0_008']<ch['endpoints']['4']['rho_0_008']
        assert ch['endpoints']['2']['D2_0_008']>ch['endpoints']['4']['D2_0_008']
        assert ch['endpoints']['2']['Cdelta_initial']>ch['endpoints']['2']['Cdelta_final']
        assert ch['endpoints']['4']['Cdelta_initial']<ch['endpoints']['4']['Cdelta_final']


def test_invalid_parent_bytes_rejected(tmp_path):
    p=tmp_path/'input.csv';p.write_bytes((ROOT/'inputs'/'GL6_coupled_41epochs.csv').read_bytes()+b'altered')
    with pytest.raises(ValueError,match='byte identity'):
        load_channel(p,6)


def test_all_3362_csv_rows_and_no_nan():
    for n in (6,8):
        with (ROOT/'data'/f'GL{n}_two_time_1681.csv').open() as f:r=list(csv.DictReader(f))
        assert len(r)==41*41
        assert all(math.isfinite(float(v)) for row in r for v in row.values())
