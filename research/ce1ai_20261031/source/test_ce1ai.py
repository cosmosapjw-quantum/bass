"""CE1AI source-owned physical, mathematical and adversarial checks.

These are scoped same-context checks, not R6/C9 distinct-author review or certified
whole-continuum numerical error enclosures.
"""
from __future__ import annotations
import csv, hashlib, json, math, sys
from fractions import Fraction as F
from pathlib import Path
import numpy as np
import pytest
from scipy.special import sph_harm_y
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ce1ai_source_response as p


def load():
 return json.loads((p.ROOT/'data'/'CE1AI_PHYSICAL_RESPONSE_RESULTS.json').read_text())

def rows(name):
 with (p.ROOT/'data'/name).open(newline='') as f:return list(csv.DictReader(f))


def test_original_source_sha_and_frozen_parent():
 assert p.validate_immutable()==p.ORIGINAL_SOURCE_SHA
 assert p.ORIGINAL_SOURCE_SHA=='022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035'
 assert p.IMMUTABLE_PARENT_HEAD=='c7660436f233bfe94d954146017059fd79385dd5'


def test_5d_independent_mass_preserving_source_manifold():
 assert np.linalg.matrix_rank(p.MASS_DIRECTIONS[:5].reshape(5,6))==5
 assert all(x==0 for x in p.MASS_DIRECTIONS.sum(axis=(1,2)))
 assert len(p.NAMES)==6


def test_exact_dark_integer_angular_moment_annihilator():
 # Row totals vanish: all mu-only moments including l=0, m=0 (l=2,4).
 D=p.DARK_INTEGER
 assert np.array_equal(D.sum(axis=1),[0,0])
 # Each row has x/y azimuth equality: m=2 harmonics vanish for all mu powers.
 assert D[0,0]==D[0,2] and D[1,0]==D[1,2]
 # Exact normalized per-cell cos(4 phi) expectations are [2,-2,2]/pi.
 mu0=F(203,240);mu1=F(53,240)
 assert F(D[0,0]-D[0,1]+D[0,2])*mu0+F(D[1,0]-D[1,1]+D[1,2])*mu1==0
 # Not a zero source family: sixth-degree angular polynomial is visible.
 avg=lambda a,b,k:(b**(k+1)-a**(k+1))/((k+1)*(b-a))
 v=lambda a,b:-1+13*avg(a,b,2)-23*avg(a,b,4)+11*avg(a,b,6)
 assert v(F(0),F(1,2))==F(-1207,6720)
 assert v(F(1,2),F(1))==F(5303,6720)
 assert F(8,406)*(53*v(F(0),F(1,2))-203*v(F(1,2),F(1)))==F(-4752,1421)


def test_dark_is_linear_combination_of_five_transfers():
 a=np.array([53,53,-203,406,-203],dtype=float)/406
 np.testing.assert_allclose(a@p.MASS_DIRECTIONS[:5].reshape(5,6),p.MASS_DIRECTIONS[5].ravel(),atol=2e-16,rtol=0)


@pytest.mark.parametrize('gl',[6,8,16])
def test_positive_gl_original_and_source_derivatives(gl):
 r,mm=p.make_cell_rays(gl);d=p.ray_source_basis(gl,mm)
 assert np.all(mm>0) and len(mm)==6*gl*gl and d.shape==(6,len(mm))
 assert np.max(abs(d.sum(axis=1)))<3e-13
 for n in p.NAMES:
  for sg in (-1,1):
   pert=p.positive_reweighted_mass(gl,mm,n,sg*1e-4)
   assert np.all(pert>0)
   assert abs(pert.sum()-mm.sum())<3e-13


@pytest.mark.parametrize('gl',[6,8])
def test_source_radiation_trace_and_initial_geometry_constraint(gl):
 rays,m=p.make_cell_rays(gl);r2=rays*rays
 dm=p.ray_source_basis(gl,m)
 ell=np.array([.011,.019,.027]);q=r2*np.exp(-2*ell)
 x=q/q.sum(axis=1)[:,None]
 dE,dP,_=p.source_integrals(r2,dm,ell,x=x)
 assert np.max(abs(dP.sum(axis=1)-dE))<2e-14
 z=p.tangent_initial(r2,m,dm)
 assert np.max(abs(z[:,:3]))==0
 H=p.initial_condition(r2,m)[3:].mean()
 assert np.max(abs(6*H*z[:,3:].mean(axis=1)-p.source_integrals(r2,dm,np.zeros(3))[0]))<3e-14


def test_normalized_harmonic_polynomial_vs_scipy():
 r,mm=p.make_cell_rays(6);u=np.array([.012,.02,.03]);z=r*np.exp(-u[None,:])
 z=z/np.linalg.norm(z,axis=1)[:,None]
 x=z*z;phi=np.arctan2(z[:,1],z[:,0]);theta=np.arccos(z[:,2])
 f=p.real_even_harmonics(x)
 ref=np.vstack([sph_harm_y(l,m,theta,phi).real for l,m in ((2,0),(2,2),(4,0),(4,2),(4,4))])
 assert np.max(abs(ref-f))<5e-14


@pytest.mark.parametrize('gl',[6,8])
def test_true_continuous_initial_l6_dark_witness_versus_gl(gl):
 r,m=p.make_cell_rays(gl);d=p.ray_source_basis(gl,m)[-1]
 sq=r*r
 f=(11*sq[:,2]-1)*(sq[:,0]**2-6*sq[:,0]*sq[:,1]+sq[:,1]**2)
 # Pure-source integrand: (11 nz²-1) (nx⁴-6nx²ny²+ny⁴).
 assert abs(d@f+4752/(1421*math.pi)) < (2e-10 if gl==6 else 1e-12)


def test_adversarial_no_negative_or_large_masses():
 rays,m=p.make_cell_rays(6)
 with pytest.raises(ValueError):p.positive_reweighted_mass(6,m,'EQ_Y',.05)
 with pytest.raises(ValueError):p.positive_reweighted_mass(6,m,'EQ_Y',float('nan'))
 with pytest.raises(KeyError):p.positive_reweighted_mass(6,m,'NOT_A_MODE',.0001)


def test_negative_tamper_original_source(monkeypatch):
 monkeypatch.setattr(p,'frozen_source_identity',lambda:'wrong-sha')
 with pytest.raises(RuntimeError,match='Original six-cell SHA256 drift'):p.produce(6,41,finite=False)


def test_physical_output_row_shapes():
 d=load();c=d['counts']
 assert c==dict(baseline=1203,linear_response=7218,nonlinear_family=9624,singular_spectrum=1203)
 for path,fields,num in [('CE1AI_BASELINE_PHYSICAL.csv',p.BASE_FIELDS,1203),
                         ('CE1AI_SOURCE_TANGENT_PHYSICAL.csv',p.TAN_FIELDS,7218),
                         ('CE1AI_FINITE_FAMILY_PHYSICAL.csv',p.FD_FIELDS,9624),
                         ('CE1AI_HARMONIC_RESPONSE_SINGULAR_VALUES.csv',p.SPEC_FIELDS,1203)]:
  v=rows(path)
  assert len(v)==num and list(v[0])==fields
  assert all(set(row)==set(fields) for row in (v[0],v[len(v)//2],v[-1]))


def test_new_result_qualifications_not_astronomical_promotion():
 d=load()
 assert d['DAG']==dict(upper='9/15',edges=21,CE1='PARTIAL',scoped_R_C='18/20',new_upper_nodes=0)
 assert d['original_baseline_immutable'] is True
 assert d['claims']['actual_CMB_likelihood'] is False
 assert d['claims']['rigorous_angular_continuum_numerical_error'] is False
 assert d['claims']['distinct_author_R6_C9'] is False
 assert not d['production_ready'] and not d['merge_ready'] and not d['auto_next']


@pytest.mark.parametrize('gl',[6,8,16])
def test_full_physical_constraint_and_energy_exchange(gl):
 s=load()['GL'][str(gl)]
 assert s['baseline_rows']==401 and s['tangent_rows']==2406
 assert s['baseline_constraint_max']<1e-10
 assert s['tangent_constraint_max']<1e-10
 assert s['max_abs_linearized_log_work_identity']<3e-11
 assert max(abs(x) for x in s['initial_dE0'])<3e-13
 if gl in (6,8):assert s['original_41sample_max_state_difference']<5e-13
 assert s['final_baseline']['W']>0 and s['final_baseline']['F']<1


@pytest.mark.parametrize('gl',[6,8])
def test_full_nonlinear_finite_difference_verifies_tangent(gl):
 errs=load()['GL'][str(gl)]['finite_difference_max_errors']
 assert len(errs)==6*5
 assert max(errs.values())<8e-9


def test_GL8_16_physical_tangent_consistency_empirical_only():
 d=load()['GL'];a=d['8'];b=d['16']
 for n in p.NAMES:
  for key in ('dC2','dC4','dW','dE','dF'):
   assert abs(a['endpoint_response'][n][key]-b['endpoint_response'][n][key])<4e-11
 # This check is empirical GL agreement; it is NOT a continuum error enclosure.


def test_exact_zero_initial_dark_then_nonzero_l4_evolved():
 source=rows('CE1AI_SOURCE_TANGENT_PHYSICAL.csv')
 for gl in ('6','8','16'):
  x=[r for r in source if r['GL']==gl and r['mode']=='DARK_L2L4']
  assert len(x)==401
  for col in ('dE','dW','dC2','dC4','dalpha20','dalpha22','dalpha40','dalpha42','dalpha44','dconstraint'):
   assert abs(float(x[0][col]))<1e-12,(gl,col,x[0][col])
  assert abs(float(x[-1]['dalpha42']))>.05
  assert abs(float(x[-1]['dalpha44']))>.01
  assert abs(float(x[-1]['dC4']))>.003


def test_initial_rank_four_but_later_empirical_rank_five():
 report=load()['GL']
 for gl in ('6','8','16'):
  s=report[gl]
  assert s['initial_source_harmonic_singular_values'][-1]<3e-14
  assert s['initial_source_harmonic_singular_values'][-2]>6
  assert s['final_source_harmonic_singular_values'][-1]>1.0e-4
  assert 1e5 <s['final_source_harmonic_condition']< 2e5
 # No exact *continuum-time* rank theorem is admitted from this numeric SVD.


def test_immutable_CE1AH_baseline_same_geometry():
 from pathlib import Path
 original=p.RESEARCH/'ce1ah_20261031'/'data'/'CE1AH_BASELINE_PHYSICAL.csv'
 assert original.is_file()
 with original.open(newline='') as f:old=list(csv.DictReader(f))
 new=rows('CE1AI_BASELINE_PHYSICAL.csv')
 assert len(old)==len(new)==1203
 for x,y in zip(old,new):
  assert int(x['GL'])==int(y['GL']) and float(x['u'])==float(y['u'])
  for a,b in [('E','E'),('H','H'),('W','W'),('C2','C2'),('C4','C4'),('F','energy_ratio')]:
   assert abs(float(y[a])-float(x[b]))<6e-13,(a,b,x[b],y[a])
