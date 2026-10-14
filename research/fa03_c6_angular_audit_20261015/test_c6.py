"""C6 bounded regressions: independent mp matrices, periodic alias and held accuracy."""
from __future__ import annotations
import json
import math
import pathlib
import sys
import unittest
from unittest.mock import patch
from fractions import Fraction as F

import numpy as np
import mpmath as mp

HERE=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import mp_cap_snapshot as h
import mp_full_grey as g
import analytic_strip as a
sys.path.insert(0,str(HERE.parent/"fa03_c5_angular_cap_20261015"))
import angular_sweep as c5

class AngularC6(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        h.source_lock()

    def setUp(self):
        # Preserve arithmetic precision across tests that intentionally use 48 dps.
        mp.mp.dps=70

    def test_reused_original_source_hashes(self):
        self.assertEqual(h.LOCKS,c5.SOURCE_LOCKS)
        self.assertEqual(h.LOCKS["fa03.py"],c5.SOURCE_LOCKS["fa03.py"])

    def test_tampered_parent_source_refuses_to_run(self):
        original=dict(h.LOCKS)
        try:
            h.LOCKS["fa03.py"]="0"*64
            with self.assertRaisesRegex(ValueError,"SOURCE_BYTE_IDENTITY_MISMATCH"):h.source_lock()
        finally:
            h.LOCKS.clear();h.LOCKS.update(original)
        h.source_lock()

    def test_independent_B_H_G_snapshot_matches_native_numpy(self):
        t=mp.mpf(0);phi=mp.mpf("1.01");x=mp.mpf(".7")
        B,H,G=h.source_at(t,phi,x,True)
        r=2*np.arcsin(np.sqrt(.5)*np.sin(.01))
        ell=np.array([[np.cos(r),np.sin(r)*np.cos(float(phi)),np.sin(r)*np.sin(float(phi))]])
        pp,hh,gg,k=c5.fa03.fields(.7,c5.fa02.setup(ell,.008,.01))
        w=(c5.fa03.moment(3)+.1*c5.fa03.moment(4)*k)[:,None,None]*pp
        for computed,truth in [(B,w),(H,hh),(G,gg)]:
            self.assertLess(max(abs(complex(computed[i][j])-truth[0,i,j]) for i in range(2) for j in range(2)),1e-14)

    def test_source_independent_70digit_snapshot(self):
        record=json.loads((HERE/"evidence/HIGHPREC_SNAPSHOT_X07.json").read_text())
        self.assertEqual(record["dps"],70)
        d={(r["nr"],r["nphi"]):mp.mpf(r["max_matrix_component_delta_6x24"]) for r in record["rows"]}
        self.assertTrue(mp.mpf("1e-27")<d[(3,12)]<mp.mpf("1e-24"))
        self.assertTrue(mp.mpf("1e-20")<d[(2,8)]<mp.mpf("1e-16"))
        self.assertIsNone(record["time_integrated_continuum_cap_error"])

    def test_full_grey_source_does_not_need_ground_truth_angle(self):
        z=json.loads((HERE/"evidence/HIGHPREC_FULL_GREY_S0_64.json").read_text())
        d={(r["nr"],r["nphi"]):mp.mpf(r["max_entry_delta_to_last_grid"]) for r in z["rows"]}
        self.assertEqual(z["steps"],64)
        self.assertTrue(mp.mpf("1e-27")<d[(3,12)]<mp.mpf("1e-24"))
        self.assertTrue(mp.mpf("1e-29")<d[(3,16)]<mp.mpf("1e-26"))
        self.assertIsNone(z["true_continuum_angular_error_bound"])
        self.assertIsNone(z["true_ode_error_bound"])

    def test_grey_mp_single_rk4_matches_exact_source_reference(self):
        mp.mp.dps=48
        t=mp.mpf(0);phi=mp.mpf("1.013")
        res=g.one_ray(t,phi,16)
        ell=np.array([[float(mp.cos(2*mp.asin(mp.sqrt(mp.mpf(".5"))*mp.sin(mp.mpf(".01"))))),
                       float(mp.sin(2*mp.asin(mp.sqrt(mp.mpf(".5"))*mp.sin(mp.mpf(".01"))))*mp.cos(phi)),
                       float(mp.sin(2*mp.asin(mp.sqrt(mp.mpf(".5"))*mp.sin(mp.mpf(".01"))))*mp.sin(phi))]])
        original=c5.solve_six_at_nodes(ell,np.array([1.0]),16)
        self.assertLess(max(abs(complex(res[i][j])-original[0,i,j]) for i in range(2) for j in range(2)),3e-14)

    def test_analytic_strip_elementary_guards_pass(self):
        q=a.strip_guards()
        self.assertEqual(q["width"],4)
        self.assertTrue(all(q["conditions"].values()))
        self.assertLess(F(q["hh_guard"]),1)
        self.assertLess(F(q["v_guard"]),1)
        self.assertLess(F(q["dm_guard"]),1)

    def test_conditional_bound_not_numeric_certificate(self):
        rec=a.demonstrate()
        self.assertIsNone(rec["numerically_admitted_angular_cap_error"])
        self.assertIsNone(rec["strip"]["complex_strip_transfer_envelope_M4"])
        self.assertIsNone(rec["strip"]["radial_Gauss3_error_bound"])

    def test_fft_mode12_fully_aliased_on_grid12(self):
        mp.mp.dps=65
        for n,expected in [(12,1),(16,0),(24,0)]:
            avg=sum(mp.cos(12*2*mp.pi*j/n) for j in range(n))/n
            self.assertLess(abs(avg-expected),mp.mpf("1e-58"))

    def test_phase_does_not_remove_mode12_alias_certification_gap(self):
        # Offset 0.37 node-spacing: Q12 cos12phi=cos(2pi*.37).
        phase=mp.mpf(".37")
        sampled=sum(mp.cos(12*2*mp.pi*(j+phase)/12) for j in range(12))/12
        self.assertLess(abs(sampled-mp.cos(2*mp.pi*phase)),mp.mpf("1e-57"))
        self.assertGreater(abs(sampled),mp.mpf(".5"))

    def test_strip_bound_coefficients_decay_geometrically(self):
        self.assertGreater(a.alias_coefficient(12),0)
        self.assertLess(a.alias_coefficient(16),a.alias_coefficient(12))
        self.assertLess(a.alias_coefficient(12),mp.mpf("3e-21"))

    def test_real_source_sample_physically_hermitian(self):
        B,H,G=h.source_at(mp.mpf("0"),mp.mpf(".7"),mp.mpf(".7"),True)
        self.assertLess(abs(B[0][1]-mp.conj(B[1][0])),mp.mpf("1e-50"))
        self.assertLess(abs(H[0][1]-H[1][0]),mp.mpf("1e-50"))
        self.assertGreater(float(mp.re(B[0][0])),0)

    def test_unchanged_c5_36ray_certificate_scope(self):
        r=c5.r7_fixed_reference()
        self.assertIsNone(r["angular_continuum_error"])
        self.assertEqual(r["rays"],36)

    def test_highprecision_source_not_substituted_for_energy_model(self):
        z=json.loads((HERE/"evidence/HIGHPREC_SNAPSHOT_X07.json").read_text())
        self.assertEqual(z["type"],"independent_full_real_angle_source_snapshot_not_time_integrated")
        self.assertIsNone(z["time_integrated_continuum_cap_error"])

    def test_invalid_parameters_fail_clearly(self):
        with self.assertRaises(ValueError):a.alias_coefficient(0)
        with self.assertRaises(ValueError):h.study(dps=31)
        with self.assertRaises(ValueError):g.run(dps=31)
        with self.assertRaises(ValueError):g.run(steps=2)

    def test_highprecision_full_grey_angular_delta_stable_under_time_halving(self):
        y32=json.loads((HERE/"evidence/HIGHPREC_FULL_GREY_S0_32.json").read_text())
        y64=json.loads((HERE/"evidence/HIGHPREC_FULL_GREY_S0_64.json").read_text())
        c32=mp.mpf(y32["rows"][0]["max_entry_delta_to_last_grid"])
        c64=mp.mpf(y64["rows"][0]["max_entry_delta_to_last_grid"])
        self.assertLess(abs(c32/c64-1),mp.mpf("1e-6"))
        self.assertLess(c64,mp.mpf("3e-26"))
        self.assertIsNone(y32["true_ode_error_bound"])

    def test_rei_owner_snapshot_keeps_history_and_admission_separate(self):
        import rei_owner_readonly as ro
        import tempfile,hashlib
        with tempfile.TemporaryDirectory() as tmp:
            base=pathlib.Path(tmp)
            repo=base/"repo";repo.mkdir()
            state=repo/ro.STATE_REL
            state.parent.mkdir(parents=True)
            state.write_text(json.dumps({"goal_status":"IN_PROGRESS",
                "scientific_admission":"NOT_ISSUED",
                "nodes":{"AX08":{"status":"IN_PROGRESS",
                  "scientific_work_status":"HALF_MINUS_ORIGINAL_LIVE"}}}))
            case=repo/ro.CASE_PARENT/"SHEAR_HALF_MINUS"
            case.mkdir(parents=True)
            (case/"RETURN.txt").write_text('status=STOPPED_CHECKPOINTED\naccepted=200000\nresult=Err(InvalidInput("AXBI_RUNTIME_CAP"))\nscientific_admission=NOT_ISSUED\n')
            (case/"checkpoint.txt").write_text("synthetic")
            original_digest=hashlib.sha256(state.read_bytes()).hexdigest()
            out=base/"out"/"read.json"
            report=ro.write_snapshot(repo,out)
            self.assertTrue(out.exists())
            self.assertEqual(report["state"]["global_scientific_admission"],"NOT_ISSUED")
            self.assertEqual(report["original_signed_cases"][-1]["status_from_return"],"STOPPED_CHECKPOINTED")
            self.assertFalse(report["original_signed_cases"][-1]["scoped_science_pass"])
            self.assertIn("AX08_DESCRIPTIVE_STATUS_STALE_WRT_HALF_MINUS_TERMINAL",report["staleness_findings"])
            self.assertEqual(original_digest,hashlib.sha256(state.read_bytes()).hexdigest())
            with self.assertRaises(ValueError):ro.write_snapshot(repo,repo/"forbidden.json")
            with self.assertRaises(FileExistsError):ro.write_snapshot(repo,out)

    def test_actual_rei_owner_snapshot_observer_failure_not_science_fail(self):
        j=json.loads((HERE/"evidence/REI_LIVE_READONLY.json").read_text())
        self.assertEqual(j["state"]["global_scientific_admission"],"NOT_ISSUED")
        self.assertTrue(j["plus_continuation"]["historical_observer_error_exists"])
        self.assertFalse(j["plus_continuation"]["terminal_RETURN_exists"])
        self.assertEqual(len(j["original_signed_cases"]),4)
        self.assertTrue(all(x["status_from_return"]=="STOPPED_CHECKPOINTED"
            for x in j["original_signed_cases"]))

if __name__=="__main__":
    unittest.main(verbosity=2)
