"""Small, falsifiable source-owned KM2 visibility tests. No Einstein IVP reruns."""
from __future__ import annotations
import hashlib, json, math, unittest
from pathlib import Path
import numpy as np
from numpy.polynomial.legendre import leggauss
from source_visibility import (ROOT, SOURCE, MANIFEST, GRID, source_arrays, run_grid,
                               integrate_visibility_arrays, run)

class OriginalVisibility(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.groups={gl:run_grid(gl) for gl in GRID}
    def test_sha_source_exact(self):
        d=json.loads(MANIFEST.read_text())
        self.assertEqual(d['parent_head'],'4137f942d2a95999f4e6627b71042e98f7afc1b7')
        for n,expected in d['files'].items():
            self.assertEqual(hashlib.sha256((SOURCE/n).read_bytes()).hexdigest(),expected)
    def test_source_p8_electron_clock(self):
        for gl in GRID:
            ld,op=source_arrays(gl)
            self.assertLess(np.max(np.abs(ld['nu'][:,None]*ld['D']-op['hazard_edges'])),1e-11)
            self.assertEqual(len(ld['nu']),41)
            self.assertEqual(op['hazard_nodes'].shape[0],320)
    def test_positive_and_causal_source(self):
        for gl in GRID:
            ld,op=source_arrays(gl)
            self.assertGreater(float(op['hazard_nodes'].min()),0)
            self.assertGreater(float(np.diff(op['tau_edges'],axis=0).min()),0)
            self.assertLess(float(np.max(np.diff(ld['mu'],axis=0))),1e-11)
    def test_direct_visibility_normalization_all_rays(self):
        for gl,tuple_ in self.groups.items():
            summ,header,rows,ph,profile,ar=tuple_
            self.assertLess(summ['survival_visibility_GL_quadrature_maxabs_residual'],1e-12)
            self.assertLess(summ['source_opacity_integral_maxabs_error'],1e-12)
            self.assertEqual(len(rows),2*gl*gl)
            self.assertEqual(ar['visibility_probability_per_u'].shape,(320,2*gl*gl))
    def test_probability_quantile_and_redshift(self):
        for gl,result in self.groups.items():
            summ,header,rows,ph,profile,ar=result
            for row in rows:
                rec=dict(zip(header,row))
                self.assertGreater(rec['p_ge1'],0)
                self.assertLess(rec['p_ge1'],1)
                self.assertLess(rec['last_event_q10_u'],rec['last_event_q50_u'])
                self.assertLess(rec['last_event_q50_u'],rec['last_event_q90_u'])
                self.assertLess(rec['last_event_q90_u'],.25)
                self.assertGreater(rec['event_q50_redshift'],0)
    def test_integrated_late_probability_direct_from_tau(self):
        for gl,result in self.groups.items():
            summ,header,rows,ph,profile,ar=result
            ld,op=source_arrays(gl)
            p=-np.expm1(-op['tau_edges'][-1])
            late=-np.expm1(op['tau_edges'][32]-op['tau_edges'][-1])/p
            v=np.array([row[-1] for row in rows]);self.assertLess(float(np.max(abs(v-late))),1e-12)
    def test_constant_hazard_analytic_oracle(self):
        U=.25; h=12.; nodes,weights=leggauss(8)
        t=np.repeat(np.linspace(0,U,41)[:-1],8)+np.tile((nodes+1)*U/80,40)
        dweights=np.tile(weights*U/80,40)
        tau=h*t[:,None];hvec=np.full((len(t),1),h)
        g,integrated,p,gap=integrate_visibility_arrays(hvec,tau,np.array([h*U]),dweights)
        self.assertLess(gap,3e-14)
        self.assertLess(abs(integrated[0]+math.expm1(-h*U)),1e-14)
        tmean=float(np.dot(dweights*t,g[:,0])/p[0])
        true=U-1/h+U/math.expm1(h*U)
        self.assertLess(abs(tmean-true),5e-14)
    def test_forged_hazard_fails(self):
        ld,op=source_arrays(12)
        v,w=leggauss(8); weights=np.tile(w*.25/80,40)
        with self.assertRaises(ArithmeticError):
            integrate_visibility_arrays(np.roll(op['hazard_nodes'],1,axis=1),op['tau_nodes'],op['tau_edges'][-1],weights)
    def test_forged_survival_sign_fails(self):
        ld,op=source_arrays(12)
        v,w=leggauss(8); weights=np.tile(w*.25/80,40)
        with self.assertRaises(ArithmeticError):
            integrate_visibility_arrays(op['hazard_nodes'],2*op['tau_edges'][-1][None,:]-op['tau_nodes'],op['tau_edges'][-1],weights)
    def test_gl_agreement_is_scoped_not_continuum(self):
        a=self.groups[12][0];b=self.groups[16][0]
        self.assertLess(abs(a['weighted_tau_mean']-b['weighted_tau_mean']),2e-8)
        self.assertLess(abs(a['conditional_last_event_mean_u']-b['conditional_last_event_mean_u']),2e-8)
        self.assertLess(abs(a['median_event_to_observer_redshift_mean']-b['median_event_to_observer_redshift_mean']),5e-8)
        self.assertGreater(b['opacity_angular_moments']['dipole'][0],0)
        self.assertGreater(b['median_redshift_angular_moments']['quadrupole_frobenius'],1e-4)
    def test_not_a_false_cmb_observation(self):
        data=json.loads((ROOT/'results/KM2_VISIBILITY_RESULTS.json').read_text())
        self.assertFalse(data['production_ready'])
        self.assertFalse(data['merge_ready'])
        self.assertEqual(data['new_owner_einstein_ivps'],0)
        self.assertEqual(data['BASS_upper'],'9/15 SCOPED_OR_SOURCE_MAPPED')
        self.assertTrue(all(x['not_full_photon_CMB_visibility'] for x in data['cases'].values()))
    def test_saved_rows_and_origin(self):
        data=json.loads((ROOT/'results/KM2_VISIBILITY_RESULTS.json').read_text())
        self.assertEqual(data['physical_ray_observable_rows'],800)
        self.assertEqual(data['time_profile_rows'],82)
        self.assertEqual(len(data['original_source']['files']),4)

if __name__=='__main__':unittest.main(verbosity=2)