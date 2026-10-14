"""Focused source-specific mathematical/gating tests. Does not run REI or FA03 producers."""
import json,math,unittest,sys
from pathlib import Path
from fractions import Fraction
sys.path.insert(0,str(Path(__file__).parent))
from decide import decision,rat,REF,stokes_norm,R6_COEFF

class R8Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.a=decision()
    def test_scope(self):
        d=self.a
        self.assertEqual(d['stage'],'FA03-R8')
        self.assertEqual(d['finite_detector']['rays'],36)
        self.assertIn('continuous_angle_cap_quadrature',d['held_claims'])
        self.assertIn('whole_nonzero_shear_REI',d['held_claims'])
    def test_exact_cross_certificate(self):
        x=json.loads((REF/'PEER_COMPATIBILITY.json').read_text())
        self.assertEqual(len(x['state_checks']),6)
        self.assertTrue(all(z['entire_peer_component_box_inside_main_trace_ball'] for z in x['state_checks']))
        expected=(rat(x['state_checks'][0]['main_reference_error_from_peer_box'])+rat(x['state_checks'][3]['main_reference_error_from_peer_box'])/10+rat(x['state_checks'][5]['main_reference_error_from_peer_box'])/200)
        self.assertEqual(expected,rat(x['main_numeric_polynomial_error_from_peer_box']))
        self.assertLess(expected+R6_COEFF/1000,Fraction(475,10**9))
    def test_hermitian_stokes_cone(self):
        d=self.a
        self.assertGreater(Fraction(d['conservative_stokes_min_eigen_lower']),Fraction(12548,100000))
        self.assertLess(d['intensity_opacity_slope_at_zero'],0)
    def test_xe_resolution_risk(self):
        d=self.a
        self.assertGreater(d['xe_over_H_floor_display'],1e-7)
        self.assertLess(d['historical_bad_xe_floor_discriminator'],d['xe_over_H_floor_display'])
        self.assertGreater(d['historical_bad_xe_floor_discriminator'],1e-7)
        self.assertAlmostEqual(d['electron_per_baryon_floor_display'],9.3865e-8,delta=1e-18)
        self.assertEqual(d['owner_reducer_floor_current']['decision'].startswith('PREVIOUS_XE_FLOOR_MISMATCH_ALREADY_RESOLVED'),True)
    def test_clock_symmetry_and_signed_exact_pair(self):
        d=self.a
        self.assertLess(abs(d['geometry_difference_seconds']-d['frozen_original_pair_seconds']),20)
        for p in d['geometry_clock']:
            self.assertLess(float(p['delta_010_years']),float(p['delta_005_years']))
            self.assertLess(float(p['delta_005_years']),0)
    def test_milestone_local_conditioning_only(self):
        d=self.a
        self.assertEqual(len(d['milestone_chord_diagnostics']),3)
        years=[v['nominal_1e-7_fraction_to_years'] for v in d['milestone_chord_diagnostics']]
        self.assertTrue(years[0]>years[1]>years[2]>0)
        for v in d['milestone_chord_diagnostics']:
            self.assertIn('NOT_CONTINUOUS',v['slope_type'])
    def test_missing_error_not_faked(self):
        d=self.a
        self.assertIn('AX11_convergence',d['held_claims'])
        self.assertIn('numeric_observer_derivative',d['held_claims'])
    def test_parent_identity(self):
        d=self.a
        self.assertEqual(d['parent_pr147'],'e67d6fc6c1ad8b3a219abf72104877da1f267e6d')
        self.assertEqual(d['parent_pr146'],'3e612547a5e54f48aa930a16778b6b656f4671ad')
if __name__=='__main__':unittest.main(verbosity=2)
