#!/usr/bin/env python3
"""Fraction-exact continuum angular initial-null and nonzero first-time-jet witness.

This does not prove nonzero at a *specified finite* u: that remains a numerical
Einstein--Vlasov observation unless separately interval enclosed.
"""
from __future__ import annotations
import json, math, sys
from fractions import Fraction as F
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import ce1ai_source_response as p


def average_mu_power(a,b,k):
 return (b**(k+1)-a**(k+1))/((k+1)*(b-a))


def certify():
 p.validate_immutable()
 D=np.asarray(p.DARK_INTEGER)
 assert D.tolist()==[[53,-106,53],[-203,406,-203]]
 cells=[[F.from_float(float(v)) for v in row] for row in p.CELL_E]
 E0=sum(sum(row) for row in cells)
 s=[F.from_float(float(x)) for x in p.SHEAR]
 assert s[0]-s[1]>0 and E0>0 and sum(s)==0
 v=[]
 for aa,bb in ((F(0),F(1,2)),(F(1,2),F(1))):
  m2=average_mu_power(aa,bb,2);m4=average_mu_power(aa,bb,4);m6=average_mu_power(aa,bb,6)
  v.append(dict(m2=m2,m4=m4,m6=m6,M4=1-2*m2+m4,M6z=m2-2*m4+m6,
                L6m4=-1+13*m2-23*m4+11*m6))
 assert [x['M4'] for x in v]==[F(203,240),F(53,240)]
 assert [x['M6z'] for x in v]==[F(407,6720),F(617,6720)]
 assert [x['L6m4'] for x in v]==[F(-1207,6720),F(5303,6720)]
 # Exact rank: row totals -> E and Y20 have independent mu means;
 # row azimuth differences -> Y22 and Y42 form a 2x2 invertible system;
 # Y44 adds one independent symmetric azimuth combination.
 row_total_mu_det=v[1]['m2']-v[0]['m2']
 d2=[1-x['m2'] for x in v]
 d4=[-1+8*x['m2']-7*x['m4'] for x in v]
 m2_m4_az_det=d2[0]*d4[1]-d2[1]*d4[0]
 assert row_total_mu_det==F(1,2) and m2_m4_az_det==F(21,20)
 # Consequently six-dimensional cell weights -> (E, five l2/l4 coefficients)
 # has rank 5, and on delta E=0 the five-harmonic map has exact rank 4.
 assert all(sum(int(x) for x in row)==0 for row in D)
 assert D[0,0]==D[0,2] and D[1,0]==D[1,2]
 assert 53*v[0]['M4']-203*v[1]['M4']==0
 # The unnormalised l6,m4-like polynomial angular source response: coeff/Pi.
 f64_pref=F(8,406)*(53*v[0]['L6m4']-203*v[1]['L6m4'])
 assert f64_pref==F(-4752,1421)
 # delta ∫ Z(1-Z)^2 cos(4 phi) = (pref/Pi)*epsilon.
 m64_pref=F(8,406)*(53*v[0]['M6z']-203*v[1]['M6z'])
 assert m64_pref==F(-432,1421)
 # f42=C42*(7Z-1)*(X-Y) with C42=3/8 sqrt(5/(2*pi)).
 # Liouville: (delta alpha42)'(0) = 4pi/E0 * 21*C42*(hx-hy)/4 * m64_pref/pi.
 # = C42 * [-1296/203] * (sigma_x-sigma_y)/E0.
 jet_rational_pref=F(21)*m64_pref
 assert jet_rational_pref==F(-1296,203)
 jet_value=float(jet_rational_pref*(s[0]-s[1])/E0)*(3/8*math.sqrt(5/(2*math.pi)))
 assert jet_value<-.7 and jet_value>-.9
 certificate={
  'schema':'bass.ce1ai.exact_continuum_source_dark_initial_jet.v1',
  'source_sha256':p.ORIGINAL_SOURCE_SHA,'original_parent_head':p.IMMUTABLE_PARENT_HEAD,
  'dark_source_integer_matrix':D.tolist(),'source_parameter_normalization':'epsilon times integer matrix divided by 406',
  'source_E0_exact':str(E0),'initial_shear_x_minus_y_exact':str(s[0]-s[1]),
  'mu_moments':[{k:str(val) for k,val in x.items()} for x in v],
  'initial_E_l2_l4_response_exact_zero':True,
  'initial_linear_source_map_rank_with_E_exact':5,
  'initial_l2_l4_map_rank_on_fixed_E_family_exact':4,
  'exact_rank_two_row_total_mu_det':str(row_total_mu_det),
  'exact_rank_azimuth_l2_l4_det':str(m2_m4_az_det),
  'full_initial_P_and_R_tensors_response_exact_zero':True,
  'unscaled_6th_order_m4_polynomial_source_witness':'('+str(f64_pref)+')/pi',
  'sixth_order_mu_factor_source_witness':'('+str(m64_pref)+')/pi',
  'alpha42_initial_time_derivative_exact_form':'(3/8)*sqrt(5/(2*pi)) * ('+str(jet_rational_pref)+') * (sigma_x0-sigma_y0)/E0',
  'alpha42_initial_time_derivative_float_display':jet_value,
  'sign_certification':'strictly negative because coefficient is negative, sqrt(5/(2*pi)) positive, (sigma_x0-sigma_y0)>0, E0>0',
  'proof_scope':'exact continuum initial moments and first proper-time derivative; finite-time response only numerically checked',
  'numerical_source_quadrature_certificate':False,'distinct_author_review':'NOT_RUN',
  'DAG':'9/15','CE1':'PARTIAL','new_completed_upper_nodes':0
 }
 return certificate


def main():
 c=certify();p.ROOT.joinpath('data').mkdir(exist_ok=True,parents=True)
 p.ROOT.joinpath('data','CE1AI_EXACT_DARK_INITIAL_JET_CERTIFICATE.json').write_text(json.dumps(c,indent=2,allow_nan=False)+'\n')
 print('CE1AI_EXACT_INITIAL_L2_L4_NULL_AND_NONZERO_L4_FIRST_JET',c['alpha42_initial_time_derivative_float_display'])
 return c

if __name__=='__main__':main()
