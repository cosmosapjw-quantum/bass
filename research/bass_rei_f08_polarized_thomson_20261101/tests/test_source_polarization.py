import csv
import gzip
import json
import math
import unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from polarized_rei_f08 import (
    load_source,cumulative_moments,stokes_response,direct_thomson_gain,
    sha256,generate,S0_SOURCE_SHA,ROOT,EPOCH_SAMPLES,GRIDS,C_CGS,SIGMA_T
)

class ScienceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scenario,cls.H,cls.hist=load_source()
        cls.sig=tuple(x-sum(cls.H)/3 for x in cls.H)
        cls.tau,cls.K=cumulative_moments(*cls.hist["S0_BI"])

    def test_original_source_lock(self):
        self.assertEqual(len(self.hist["S0_BI"][0]),16001)
        self.assertEqual(self.hist["S0_BI"][0][-1],1e13)
        self.assertAlmostEqual(sum(self.sig),0,delta=1e-27)

    def test_original_provenance_not_promoted(self):
        p=json.loads((ROOT/"source_inputs/REI349_SOURCE_PROVENANCE.json").read_text())
        self.assertEqual(p["original_F08_return"]["scientific_admission"],"HOLD")
        self.assertEqual(p["original_26event_first_interval"],"BLOCKED_at_160/131072")

    def test_exact_linear_piecewise_integration(self):
        t=[0.,2.,3.]
        ne=[2.,6.,8.]  # ne=2+2t
        tau,K=cumulative_moments(t,ne)
        self.assertAlmostEqual(tau[-1],C_CGS*SIGMA_T*15,delta=1e-26)
        self.assertAlmostEqual(K[-1],C_CGS*SIGMA_T*(9+2*9)/10,delta=1e-26)
        # Integral_0^3 (2+2t) t dt = 9+18=27

    def test_density_zero_and_scaling(self):
        ts,ne=self.hist["S0_BI"]
        tau0,K0=cumulative_moments(ts,[0.]*len(ne))
        self.assertEqual(tau0[-1],0.)
        self.assertEqual(K0[-1],0.)
        tau2,K2=cumulative_moments(ts,[2*x for x in ne])
        self.assertAlmostEqual(K2[-1]/self.K[-1],2,delta=5e-15)
        self.assertAlmostEqual(tau2[-1]/self.tau[-1],2,delta=5e-15)

    def test_FLRW_null_shear(self):
        for mu in (-.75,0.,.75):
            for phi in (.13,1.7,5.1):
                self.assertEqual(stokes_response((0.,0.,0.),self.K[-1],mu,phi),(0.,0.))

    def test_North_pole_tensor_sign(self):
        q,u=stokes_response(self.sig,self.K[-1],1.,0.)
        self.assertAlmostEqual(q,self.K[-1]*(self.sig[0]-self.sig[1]),delta=1e-21)
        self.assertAlmostEqual(u,0.,delta=1e-21)

    def test_spin_two_basis_rotation_at_pole(self):
        amp=self.K[-1]*(self.sig[0]-self.sig[1])
        for phi in (.12,.3,.7,1.1):
            q,u=stokes_response(self.sig,self.K[-1],1.,phi)
            self.assertAlmostEqual(q,amp*math.cos(2*phi),delta=2e-21)
            self.assertAlmostEqual(u,-amp*math.sin(2*phi),delta=2e-21)

    def test_direct_Thomson_angular_quadrature(self):
        mu,phi=.34,.71
        t=1e13
        q,u=direct_thomson_gain(self.sig,t,mu,phi)
        qe,ue=stokes_response(self.sig,t/10,mu,phi)
        self.assertLess(abs(q-qe),3e-3*max(abs(qe),abs(ue)))
        self.assertLess(abs(u-ue),3e-3*max(abs(qe),abs(ue)))

    def test_sky_parity_invariant_amplitude(self):
        mu,phi=.34,.71
        q,u=stokes_response(self.sig,self.K[-1],mu,phi)
        qm,um=stokes_response(self.sig,self.K[-1],-mu,phi+math.pi)
        self.assertAlmostEqual(q,qm,delta=1e-20)
        self.assertAlmostEqual(u,-um,delta=1e-20)
        self.assertAlmostEqual(math.hypot(q,u),math.hypot(qm,um),delta=1e-20)

    def test_time_optical_moments_physical(self):
        self.assertTrue(all(a<b for a,b in zip(self.tau,self.tau[1:])))
        self.assertTrue(all(a<b for a,b in zip(self.K,self.K[1:])))
        for idx in EPOCH_SAMPLES:
            self.assertGreater(self.tau[idx],0.)
            self.assertLess(self.tau[idx],2e-5)
            self.assertLessEqual(10*self.K[idx]/self.tau[idx],self.hist["S0_BI"][0][idx])

    def test_error_from_forged_hash_is_rejected(self):
        name="science_scenario_v1.json"
        actual=S0_SOURCE_SHA[name]
        try:
            S0_SOURCE_SHA[name]="0"*64
            with self.assertRaisesRegex(ValueError,"source byte-identity"):
                load_source()
        finally:
            S0_SOURCE_SHA[name]=actual

    def test_actual_sky_output_audit(self):
        report=json.loads((ROOT/"results/RESULT.json").read_text())
        path=ROOT/"results"/report["sky_file"]
        self.assertEqual(sha256(path),report["sky_sha256"])
        with gzip.open(path,"rt",newline="") as f:
            rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),4*sum(a*b for a,b in GRIDS))
        self.assertEqual(len(rows),10752)
        for r in rows:
            v=[float(r[key]) for key in ("Q_over_Tbar_BI_electron",
                "U_over_Tbar_BI_electron","P_over_Tbar_BI_electron",
                "delta_Q_material_fixed_BI_geometry",
                "delta_U_material_fixed_BI_geometry")]
            self.assertTrue(all(math.isfinite(x) for x in v))
            self.assertAlmostEqual(math.hypot(v[0],v[1]),v[2],delta=1e-22)
        self.assertEqual(report["canonical_delta"],0)
        self.assertEqual(report["production"],"HOLD")

if __name__=="__main__":
    unittest.main()
