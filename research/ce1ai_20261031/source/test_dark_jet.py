"""Independent SciPy harmonic and exact Fraction checks for CE1AI dark source jet."""
from fractions import Fraction as F
import math,sys
from pathlib import Path
import numpy as np
from scipy.special import sph_harm_y
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ce1ai_source_response as p
import certify_dark_initial_jet as d


def test_pure_rational_continuum_jets_and_provenance():
 c=d.certify()
 assert c['initial_E_l2_l4_response_exact_zero']
 assert c['full_initial_P_and_R_tensors_response_exact_zero']
 assert c['unscaled_6th_order_m4_polynomial_source_witness']=='(-4752/1421)/pi'
 assert c['sixth_order_mu_factor_source_witness']=='(-432/1421)/pi'
 assert F(-1296,203)<0
 assert c['alpha42_initial_time_derivative_float_display']<0


def test_original_source_identity_detection(monkeypatch):
 monkeypatch.setattr(p,'frozen_source_identity',lambda:'wrong-sha')
 with pytest.raises(RuntimeError):d.certify()


def independent_direct_scipy_alpha42_source(ell,gl=8):
 rays,m=p.make_cell_rays(gl)
 dm=p.ray_source_basis(gl,m)[-1]
 q=rays*np.exp(-ell)
 rad=np.linalg.norm(q,axis=1)
 n=q/rad[:,None]
 Y=sph_harm_y(4,2,np.arccos(n[:,2]),np.arctan2(n[:,1],n[:,0])).real
 energy=np.exp(-sum(ell))*m*rad
 src=np.exp(-sum(ell))*dm*rad
 E=energy.sum();dE=src.sum()
 return 4*math.pi*(src@Y/E - (energy@Y)*dE/E**2)


@pytest.mark.parametrize('gl',[6,8,16])
def test_independent_scipy_first_time_jet(gl):
 r,m=p.make_cell_rays(gl)
 y0=p.initial_condition(r*r,m)
 h0=y0[3:]
 delta=1e-6
 numerical=(independent_direct_scipy_alpha42_source(h0*delta,gl)-independent_direct_scipy_alpha42_source(-h0*delta,gl))/(2*delta)
 exact=d.certify()['alpha42_initial_time_derivative_float_display']
 assert abs(numerical-exact)<2e-7,(gl,numerical,exact)
 assert abs(independent_direct_scipy_alpha42_source(np.zeros(3),gl))<2e-13


def test_exact_hidden_mode_sourced_immediately_in_numeric_IVP():
 import csv
 with (p.ROOT/'data'/'CE1AI_SOURCE_TANGENT_PHYSICAL.csv').open(newline='') as f:
  rows=[r for r in csv.DictReader(f) if r['GL']=='16' and r['mode']=='DARK_L2L4']
 assert len(rows)==401
 assert abs(float(rows[0]['dalpha42']))<1e-12
 approx=float(rows[1]['dalpha42'])/float(rows[1]['u'])
 exact=d.certify()['alpha42_initial_time_derivative_float_display']
 assert abs(approx-exact)<2e-4
