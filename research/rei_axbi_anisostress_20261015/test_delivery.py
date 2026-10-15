"""Audit exported 17-case geometric and Vlasov angular stress source tables."""
from __future__ import annotations
import csv,hashlib,json,math,sys,unittest
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import produce_stress_tables as prod
import einstein_vlasov_lrs as v

class DeliveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root=HERE/"evidence/AX03_INITIAL_PI_TABLES"
        cls.m=json.loads((cls.root/"AX03_INITIAL_PI_CONTRACT.json").read_text())
        with (cls.root/"AX03_INITIAL_PI_BACKGROUND.csv").open() as f:
            cls.rows=list(csv.DictReader(f))
        with (cls.root/"AX03_INITIAL_PI_KILLING.csv").open() as f:
            cls.photon=list(csv.DictReader(f))
    def test_source_sha_and_cardinality(self):
        self.assertEqual(self.m["original_AX03_lock_sha256"],v.LOCK_SHA)
        self.assertEqual(self.m["trajectory_rows"],8517)
        self.assertEqual(self.m["ray_rows"],8585)
        self.assertEqual(len(self.rows),8517)
        self.assertEqual(len(self.photon),8585)
        self.assertEqual(self.m["case_count"],17)
    def test_original_data_hashes(self):
        for name,sha in self.m["SHA256"].items():
            self.assertEqual(hashlib.sha256((self.root/name).read_bytes()).hexdigest(),sha)
    def test_initial_stress_label_equals_independent_input(self):
        for z in self.m["cases"]:
            self.assertLess(abs(z["initial_deltaP_over_original_epsilon_rad"]-z["eta"]*z["A"]/5),1e-18)
    def test_pressure_trace_and_Hamiltonian_for_all_rows(self):
        for r in self.rows:
            x=lambda k:float(r[k])
            self.assertLess(abs(2*x("pi_perp_J_m3")+x("pi_parallel_J_m3")),2e-22)
            self.assertLess(abs(x("Hamiltonian_residual_s2"))/max(1e-50,x("H_per_s")**2),3e-13)
            self.assertGreater(x("H_per_s"),0)
            self.assertGreaterEqual(x("aniso_epsilon_J_m3"),0)
    def test_photon_Jacobian_independent_finite_difference(self):
        for c in (self.m["cases"][6],self.m["cases"][12],self.m["cases"][15]):
            model=v.EinsteinVlasovLRS(v.InitialData(c["q_ref"],c["A"],c["eta"]))
            a=.12
            bb=model.at_a(a)["b"]
            for mu in (-.8,-.5,0,.6,.9):
                def flow(m):
                    R=np.sqrt(np.exp(2*bb)*(1-m*m)+np.exp(-4*bb)*m*m)
                    return m*np.exp(-2*bb)/R
                h=1e-5
                numeric=(flow(mu+h)-flow(mu-h))/(2*h)
                R=np.sqrt(np.exp(2*bb)*(1-mu*mu)+np.exp(-4*bb)*mu*mu)
                self.assertLess(abs(numeric-R**-3),1e-9)
    def test_ray_csv_jacobian_identity_all_rows(self):
        bg={(r["case_id"],r["a"]):float(r["b"]) for r in self.rows}
        source_a=float(self.m["source_frozen_a_ref"]) if "source_frozen_a_ref" in self.m else 1/21
        for p in self.photon:
            b=bg[(p["case_id"],p["a"])]
            mu=float(p["initial_mu"])
            R=np.sqrt(np.exp(2*b)*(1-mu*mu)+np.exp(-4*b)*mu*mu)
            energy=source_a/float(p["a"])*R
            curmu=mu*np.exp(-2*b)/R
            jac=R**-3
            self.assertLess(abs(float(p["E_over_E_ref"])/energy-1),6e-14)
            self.assertLess(abs(float(p["mu_current"])-curmu),6e-14)
            self.assertLess(abs(float(p["jac_dOmega_current_over_initial"])/jac-1),6e-14)
    def test_quadrupole_negative_control_is_preserved(self):
        neg=json.loads((HERE/"evidence/JACOBIAN_NEGATIVE_CONTROL.json").read_text())
        self.assertTrue(neg["old_unpublished_file_sha256"])
        self.assertLess(neg["example"]["relative_error"],-.01)
        self.assertEqual(neg["stage"],"PRE_PUBLICATION_DIAGNOSED_AND_REPAIRED")
    def test_initial_zero_shear_initial_stress_drives_geometry(self):
        key=v.InitialData(0,1,1).key
        last=[r for r in self.rows if r["case_id"]==key][-1]
        self.assertGreater(float(last["s_over_H"]),2.9e-4)
        self.assertGreater(float(last["b"]),4.1e-4)
    def test_stress_free_source_limit_compliant(self):
        root=self.root
        keys=[v.InitialData(q,0,0).key for q in (0,.005,-.005,.01,-.01)]
        for key in keys:
            arr=[r for r in self.rows if r["case_id"]==key]
            self.assertEqual(len(arr),501)
            self.assertTrue(all(abs(float(row["pi_parallel_J_m3"]))<1e-30 for row in arr))
if __name__=="__main__":unittest.main(verbosity=2)
