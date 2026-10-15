"""Independent Rust FD96 mass-shell kernel and analytic Einstein Jacobian tests."""
from __future__ import annotations
import math
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest
import numpy as np

HERE=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
sys.path.insert(0,str(HERE.parents[1]/"research/rei_sigma_kinetic_gamma_nu_20261015"))
from export_grid import source_grid, cases
from jacobian import kinetic_susceptibility,massive_jacobian_at_state
from joint_kinetic import KineticGammaNuMassive,source_lock

class NativeStressTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rustc=shutil.which("rustc")
        if not rustc:
            raise unittest.SkipTest("RUSTC_UNAVAILABLE_LOCAL; NCP rustc check separate")
        cls.tmp=tempfile.TemporaryDirectory(prefix="bass_native_stress_")
        cls.dir=pathlib.Path(cls.tmp.name)
        cls.exe=cls.dir/"native_stress"
        build=subprocess.run([rustc,"-C","opt-level=3",
                              str(HERE/"kernel.rs"),"-o",str(cls.exe)],
                             capture_output=True,text=True,timeout=90)
        if build.returncode!=0:
            raise AssertionError("NATIVE_RUST_BUILD_FAILED:\n"+build.stderr)
    @classmethod
    def tearDownClass(cls):
        if hasattr(cls,"tmp"):cls.tmp.cleanup()

    def query(self,mass,case_rows,nthreads=1):
        text,m=source_grid(float(mass))
        grid=self.dir/f"grid_m{mass}.txt"
        query=self.dir/f"query_m{mass}.tsv"
        out=self.dir/f"output_m{mass}_{nthreads}.tsv"
        grid.write_text(text)
        query.write_text("\n".join("%.17g %.17g %.17g"%z for z in case_rows)+"\n")
        result=subprocess.run([str(self.exe),"eval",str(grid),str(query),str(out),str(nthreads)],
                              capture_output=True,text=True,timeout=90)
        self.assertEqual(result.returncode,0,result.stderr)
        data=np.loadtxt(out,skiprows=1)
        return np.atleast_2d(data),m

    def test_cpp_style_source_and_data_contract(self):
        for mass in (3,30,300):
            raw,m=source_grid(float(mass))
            self.assertIn("BASS_FD96_STRESS_V1 96 32",raw)
            self.assertGreater(m.norm,0)
            self.assertEqual(len(m.q),96)
            self.assertAlmostEqual(float(np.sum(m.w)),1,14)

    def test_stress_and_susceptibility_rust_python_parity(self):
        sample=cases(60,seed=1237)
        for mass in (3,30,300):
            rows,m=self.query(mass,sample,nthreads=1)
            self.assertEqual(rows.shape,(len(sample),5))
            for (x,b,a),v in zip(sample,rows):
                p=np.array(m.evaluate_with_delta(x,b,a))
                s=kinetic_susceptibility(m,x,b,a)
                ref=np.r_[p,s]
                np.testing.assert_allclose(v,ref,atol=5e-14,rtol=8e-13)

    def test_subroundoff_shear_sign_and_zero_limit(self):
        sample=[(.5,0.,0.),(.5,1e-16,0.),(.5,-1e-16,0.),
                (.5,1e-14,0.),(.5,1e-12,0.)]
        for mass in (3,30,300):
            out,m=self.query(mass,sample)
            self.assertEqual(out[0,3],0.)
            self.assertLess(out[1,3],0.)
            self.assertGreater(out[2,3],0.)
            derivative=m.initial_linear_susceptibility(.5)
            for v,b in zip(out[1:],(1e-16,-1e-16,1e-14,1e-12)):
                self.assertLess(abs(v[3]/(b*derivative)-1),8e-10)

    def test_positive_principal_pressure_cone(self):
        sample=cases(120)
        for mass in (3,30,300):
            rows,_=self.query(mass,sample)
            self.assertTrue(np.all(rows[:,0]>0))
            self.assertTrue(np.all(rows[:,1]>0))
            self.assertTrue(np.all(rows[:,2]>0))
            self.assertTrue(np.all(rows[:,1]+rows[:,2]<=1.1*rows[:,0]))

    def test_massive_number_and_energy_work_identity(self):
        mass=3.
        raw,m=source_grid(mass)
        x=.65;b=.017;A=.6;eps=2e-5
        pp=m.evaluate_with_delta(x+eps,b,A)
        pm=m.evaluate_with_delta(x-eps,b,A)
        centered=(pp[0]-pm[0])/(2*eps)
        rho,pt,pz,delta=m.evaluate_with_delta(x,b,A)
        pbar=(2*pt+pz)/3
        expected=-3*(rho+pbar)
        self.assertLess(abs(centered/expected-1),3e-9)
        h=2e-5
        rp=m.evaluate_with_delta(x,b+h,A)[0]
        rm=m.evaluate_with_delta(x,b-h,A)[0]
        self.assertLess(abs((rp-rm)/(2*h)+2*delta),2e-11)

    def test_susceptibility_as_independent_central_derivative(self):
        for mval,x,b,A in [(3.,.3,.03,.7),(30.,.8,-.025,-.5),(300.,.5,.01,.6)]:
            _,m=source_grid(mval)
            h=5e-5
            dplus=m.delta_p_stable(x,b+h,A)
            dminus=m.delta_p_stable(x,b-h,A)
            numerical=(dplus-dminus)/(2*h)
            analytic=kinetic_susceptibility(m,x,b,A)
            self.assertLess(abs(numerical/analytic-1),2e-8)

    def test_bass_einstein_partial_jacobian_and_units(self):
        src=source_lock()
        model=KineticGammaNuMassive(src,Sigma_ref=0.,orientation=0,
                                    kappa_gamma=.2,kappa_nu=.2,
                                    massive_fraction=.1,massive_A=.5,
                                    m_over_Tref=30.,ellmax=8,stable_massive_pi=True)
        ode,_,_=model.integrate(n=31)
        x=float(ode.t[10]);y=ode.y[:,10].copy()
        jac=massive_jacobian_at_state(model,x,y)
        eps=5e-5
        yp=y.copy();ym=y.copy();yp[1]+=eps;ym[1]-=eps
        hp=model.fields(x,yp)["H"];hm=model.fields(x,ym)["H"]
        sp=model.rhs(x,yp)[2];sm=model.rhs(x,ym)[2]
        self.assertLess(abs((hp-hm)/(2*eps)-jac["dH_db_per_s"])/model.source.h0,5e-9)
        self.assertLess(abs((sp-sm)/(2*eps)-jac["d_rhs_signed_s_over_href_db"]),3e-9)
        self.assertIn("fixed x",jac["scope"])

    def test_noncoupled_mass_has_zero_b_jacobian(self):
        src=source_lock()
        model=KineticGammaNuMassive(src,stable_massive_pi=True,massive_fraction=0.)
        j=massive_jacobian_at_state(model,0,model.initial_state())
        self.assertEqual(j["dH_db_per_s"],0)
        self.assertEqual(j["d_rhs_signed_s_over_href_db"],0)

    def test_thread_bitwise_output_parity(self):
        sample=cases(97)
        ref,_=self.query(30,sample,nthreads=1)
        for width in (2,4,8,32):
            got,_=self.query(30,sample,nthreads=width)
            self.assertTrue(np.array_equal(ref,got))

    def test_invalid_case_fails_nonzero(self):
        raw,_=source_grid(30.)
        grid=self.dir/"grid_negative.txt";grid.write_text(raw)
        inp=self.dir/"invalid_case.tsv";inp.write_text("0 0 2.1\n")
        out=self.dir/"invalid.tsv"
        p=subprocess.run([str(self.exe),"eval",str(grid),str(inp),str(out),"1"],
                         capture_output=True,text=True,timeout=30)
        self.assertEqual(p.returncode,3)
        self.assertIn("CASE_PHYSICAL_DOMAIN",p.stderr)

if __name__=="__main__":unittest.main(verbosity=2)
