"""C8 source-bound rational spectral theorem, empirical convergence and error separation."""
from __future__ import annotations
import json,math,pathlib,sys,unittest
from fractions import Fraction as Q
from unittest.mock import patch
import numpy as np
import mpmath as mp
HERE=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
sys.path.insert(0,str(HERE.parent/"fa03_c7_polarized_batch_20261015"))
import spectral_cert as c
import manufactured_defect as d
import convergence_c8 as v
import batch_transport as b
import stokes_vector as st

class C8ErrorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((HERE/"evidence/C8_CONVERGENCE_AND_BENCHMARK.json").read_text())

    def test_source_original_sha_bind(self):
        self.assertEqual(c.source_lock(),c.SHA)
        self.assertEqual(b.verify(),c.SHA)

    def test_source_sha_tamper_rejected(self):
        original=dict(c.SHA)
        try:
            c.SHA["fa03.py"]="0"*64
            with self.assertRaisesRegex(ValueError,"SOURCE_IDENTITY_MISMATCH"):
                c.source_lock()
        finally:
            c.SHA.clear();c.SHA.update(original)

    def test_exact_spectral_bound_rational(self):
        self.assertEqual(c.certificate(2),Q(13977,1250000000))
        self.assertEqual(c.certificate(3),Q(13977,781250000000))
        self.assertEqual(c.certificate(4),Q(13977,488281250000000))
        self.assertEqual(c.certificate(5),Q(13977,305175781250000000))
        self.assertEqual(c.certificate(6),Q(13977,190734863281250000000))

    def test_exact_gauss_decay(self):
        for n in range(1,12):
            self.assertEqual(c.certificate(n+1)*625,c.certificate(n))
            self.assertGreater(c.certificate(n),0)

    def test_minimum_order_selection_exact(self):
        expected={"1e-7":3,"1e-10":4,"1e-13":5,"1e-16":6}
        self.assertEqual({k:c.best_order(k) for k in expected},expected)
        self.assertGreater(c.certificate(3),Q("1e-10"))
        self.assertLess(c.certificate(4),Q("1e-10"))

    def test_bad_tolerance_fails_closed(self):
        for x in [1e-10,0,-1,"zero",None,True]:
            with self.assertRaises(ValueError):
                c.best_order(x)
        with self.assertRaises(ValueError):c.best_order("1e-1000",maximum=32)
        with self.assertRaises(ValueError):c.certificate(0)
        with self.assertRaises(ValueError):c.certificate(2.0)

    def test_spectral_complex_energy_Hermitian_G_nonnegative(self):
        # Re(alpha)>=33/50 on the entire disk, sample its boundary independently.
        ell,w=b._prepared_rays(3,12);data=b.fa02.setup(ell,.008,.01)
        for x in (.5,.7,1.0):
            P,H,G,k=b.fa03.fields(x,data)
            for eps in (-.1,.1):
                for phi in np.linspace(0,2*np.pi,13):
                    e=1+.5*np.exp(1j*phi)
                    A=1+eps*(e*k-1)
                    GG=G+eps*(e*k-1)[:,None,None]*H
                    sym=.5*(GG+GG.conj().swapaxes(-1,-2))
                    self.assertGreater(np.linalg.eigvalsh(sym).min(),-1e-14)
                    self.assertGreater(np.real(A).min(),.65)

    def test_complex_energy_source_trace_global_envelope(self):
        ell,w=b._prepared_rays(3,12);data=b.fa02.setup(ell,.008,.01)
        for x in (.5,.7,1.0):
            P,H,G,k=b.fa03.fields(x,data)
            for ph in np.linspace(0,2*np.pi,17):
                e=1+.5*np.exp(1j*ph)
                Bs=(e**3*(1+.1*e*k))[:,None,None]*P
                self.assertLess(max(b.trace_norm(X) for X in Bs),float(c.B_TRACE_BOUND)+1e-12)

    def test_normalized_energy_legendre_weights_positive(self):
        from numpy.polynomial.legendre import leggauss
        for n in [2,3,4,5,6,8,16]:
            x,w=leggauss(n)
            self.assertTrue((w>0).all())
            self.assertLess(abs(w.sum()/2-1),2e-14)
            for k in range(min(2*n,8)):
                exact=1/(k+1) if k%2==0 else 0
                self.assertLess(abs(np.dot(w/2,x**k)-exact),2e-14)

    def test_exact_global_manufactured_bounds(self):
        for n in [8,16,32,64,128]:
            d0=d.componentwise_exact(n)
            r=Q(d0["global_trace_norm_residual_bound"])
            self.assertGreater(r,0)
            self.assertLess(r,Q(1,100))
            if n>8:self.assertLess(r,Q(d.componentwise_exact(n//2)["global_trace_norm_residual_bound"]))

    def test_exact_bernstein_identity_and_integral(self):
        # Bernstein coefficients of u^3 satisfy B0=0, B1=0, B2=0, B3=1.
        self.assertEqual(d.cubic_bernstein((Q(0),Q(0),Q(0),Q(1))),(Q(0),Q(0),Q(0),Q(1)))
        with self.assertRaises(ValueError):d.cubic_bernstein((Q(1),Q(2)))

    def test_manufactured_error_real_decreased_under_exact_contractivity(self):
        mp.mp.dps=70
        hh=[mp.mpf(1)/5,mp.mpf(2)/5]
        Bs=[[mp.mpc("0.7"),mp.mpc("0.1","0.05")],
            [mp.mpc("0.1","-0.05"),mp.mpc("0.3")]]
        for n in [8,16,32,64,128]:
            test=d.componentwise_exact(n)
            F=np.array([[complex(Q(test["end_real_parts"][i][j]))+
                         1j*float(Q(test["end_imag_parts"][i][j]))
                         for j in range(2)] for i in range(2)])
            T=np.array([[complex(Bs[i][j]*(1-mp.exp(-(hh[i]+hh[j])/2))/(hh[i]+hh[j]))
                         for j in range(2)] for i in range(2)])
            err=b.trace_norm(F-T)
            self.assertLess(err,float(Q(test["global_trace_norm_residual_bound"])))

    def test_differentiate_exact_vs_empirical_errors(self):
        for G in self.data["convergence"]:
            self.assertIsNone(G["absolute_time_error_certified"])
            self.assertIsNone(G["absolute_roundoff_error_certified"])
            self.assertIsNone(G["continuous_cap_angular_error_certified"])
            for row in G["energy_refinements"]:
                self.assertEqual(row["exact_ODE_energy_quadrature_bound_trace"],float(c.certificate(row["ne"])))
                self.assertFalse(row["time_RK4_error_certified"])

    def test_RK4_empirical_fourth_order(self):
        for G in self.data["convergence"]:
            rows=G["time_refinements"]
            d16,d32,d64,d128=[rows[i]["max_eps_error_vs_1024_same_GL6"] for i in range(4)]
            self.assertTrue(15.8<d16/d32<16.3)
            self.assertTrue(15.8<d32/d64<16.3)
            self.assertTrue(15.8<d64/d128<16.3)

    def test_roundoff_can_exceed_tiny_exact_energy_bound(self):
        # n=8 exact GL integration error bound is ~1.87e-22, but
        # binary64 comparison to n24 differs at ~1e-16.
        for G in self.data["convergence"]:
            last=G["energy_refinements"][-1]
            self.assertEqual(last["ne"],8)
            self.assertGreater(last["empirical_trace_difference_vs_GL24"],
                               last["exact_ODE_energy_quadrature_bound_trace"])
            self.assertIsNone(G["absolute_roundoff_error_certified"])

    def test_benchmark_matched_source_and_numerical_output(self):
        for x in self.data["benchmark"]:
            self.assertEqual(x["steps"],128)
            self.assertEqual(x["epsilon"],[-.1,0,.1])
            for n in [4,5,6,8]:
                z=x["measured"][f"real_stokes_GL{n}"]
                self.assertGreater(z["median_s"],0)
                self.assertLess(z["max_tracenorm_vs_original_Jones_GL8"],3e-12)
                self.assertEqual(z["source_locked_certified_spectral_error"],float(c.certificate(n)))
                self.assertEqual(z["nominal_state_bytes"],3*x["rays"]*n*4*8)

    def test_no_generic_parallel_speed_claim(self):
        self.assertIsNone(self.data["native_rei_abundance_scientific_admission"])
        self.assertIsNone(self.data["exact_time_ODE_error_admission"])

    def test_fa03_ray_contraction_physical_domain(self):
        r=b.ray_physics_checks(nr=3,nphi=12)
        self.assertTrue(all(v["min_absorption_eig"]>.19 for v in r["per_x"]))
        self.assertTrue(all(v["min_passivity_factor"]>.9 for v in r["per_x"]))

    def test_real_observer_L_factor_source_regression(self):
        # Explicitly reproduces the RED counterexample to the original too-small
        # source bound 837/200, due to missing L in k=L*x^(-2/3)*v.
        ell,w=b._prepared_rays(3,12)
        P,H,G,k=b.fa03.fields(.5,b.fa02.setup(ell,.008,.01))
        energy=1.5
        old=Q(837,200)
        physical=(energy**3*(1+.1*energy*k))[:,None,None]*P
        actual=max(b.trace_norm(mat) for mat in physical)
        self.assertGreater(actual,float(old))
        self.assertLess(actual,float(c.B_TRACE_BOUND))
        self.assertEqual(c.MAX_REAL_RAY_K,Q(202,125))
        self.assertEqual(c.MIN_HERMITIAN_G_FACTOR,Q(411,625))

    def test_roundoff_aggregation_exact_fraction_conditional(self):
        import aggregation_roundoff as a
        self.assertEqual(a.U,Q(1,2**53))
        self.assertEqual(a.gamma(2),2*a.U/(1-2*a.U))
        for rays in [36,144,480]:
            z=a.stokes_reduce_bound(rays,4)
            self.assertGreater(z["conditional_aggregation_trace_bound_decimal"],0)
            self.assertIsNone(z["certified_binary64_whole_transport_error"])

    def test_roundoff_gamma_input_validation(self):
        import aggregation_roundoff as a
        for k in (0,-1,1.5,True):
            with self.assertRaises(ValueError):a.gamma(k)
        with self.assertRaises(ValueError):a.gamma(2**54)

    def test_actual_resource_and_parallel_evidence(self):
        j=json.loads((HERE/"evidence/RESOURCE_PROBE.json").read_text())
        self.assertEqual([v["rays"] for v in j["timings"]],[36,144,480])
        self.assertIsNone(j["intrinsic_solver_roundoff_certification"])
        for t in j["timings"]:
            q={x["ne"]:x for x in t["measurements"]}
            self.assertLess(q[4]["nominal_stokes_state_bytes"],q[8]["nominal_stokes_state_bytes"])
            self.assertLess(q[4]["tracemalloc_peak_bytes"],q[8]["tracemalloc_peak_bytes"])
            self.assertLess(q[4]["max_ref_GL8_trace_delta"],3e-12)
        self.assertEqual([k["workers"] for k in j["parallel"]],[1,2,4])
        self.assertTrue(all(k["max_difference_vs_unchunked"]<3e-12 for k in j["parallel"]))

    def test_different_reduction_order_roundoff_floors(self):
        j=json.loads((HERE/"evidence/RESOURCE_PROBE.json").read_text())
        for row in j["roundoff_reduction"]:
            self.assertLess(row["max_trace_difference"],1e-13)
            if row["chunk"]==row["grid"][0]*row["grid"][1]:
                self.assertTrue(row["bitwise_equal"])
        self.assertTrue(any(row["max_trace_difference"]>0 for row in j["roundoff_reduction"]))

if __name__=="__main__":unittest.main(verbosity=2)
