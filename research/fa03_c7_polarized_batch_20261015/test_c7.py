"""FA03 C7 physical and optimization regressions, actual frozen source."""
import json
import math
import pathlib
import sys
import unittest
from unittest.mock import patch

import numpy as np

HERE=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import batch_transport as b

class C7Physics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b.verify()
        cls.ell,cls.w=b._prepared_rays(3,12)
        cls.y=b.solve_moments_fused(64,ell=cls.ell,w=cls.w)

    def test_byte_identity_locked(self):
        self.assertEqual(b.verify(),b.SHA)

    def test_altered_parent_source_is_rejected(self):
        t=dict(b.SHA)
        try:
            b.SHA["fa03.py"]="0"*64
            with self.assertRaisesRegex(ValueError,"FROZEN_SOURCE_CHANGED"):
                b.verify()
        finally:
            b.SHA.clear();b.SHA.update(t)

    def test_six_state_fused_against_frozen_original(self):
        orig=b.fa03.solve_moments(.008,.01,steps=64,nr=3,nphi=12)
        for left,right in zip(self.y,orig):
            self.assertLess(b.trace_norm(left-right),3e-14)

    def test_original_saved_R7_coefficients(self):
        from pathlib import Path
        cert=json.loads((HERE.parent/"fa03_c5_angular_cap_20261015"/"reference"/"R7_MAIN_CERTIFICATE.json").read_text())
        for state,expected in zip(self.y,cert["reference_stokes_display"]):
            self.assertLess(np.max(abs(b.stokes(state)-expected)),2e-14)

    def test_six_fused_at_64and144_ray(self):
        for q in [(4,16),(6,24)]:
            actual=b.solve_moments_fused(32,nr=q[0],nphi=q[1])
            ref=b.fa03.solve_moments(.008,.01,steps=32,nr=q[0],nphi=q[1])
            self.assertLess(max(b.trace_norm(a-c) for a,c in zip(actual,ref)),3e-14)

    def test_physical_screen_and_source_cone(self):
        p=b.ray_physics_checks()
        self.assertEqual(p["angle_count"],36)
        self.assertGreater(min(p["P3_eigenvalues"]),-1e-15)
        for q in p["per_x"]:
            self.assertLess(q["max_screen_orthonormal_error"],3e-14)
            self.assertLess(q["max_ray_unit_error"],3e-14)
            self.assertLess(q["max_kk_ray_error"],2e-14)
            self.assertGreater(q["min_source_eig"],.27)
            self.assertGreater(q["min_absorption_eig"],.19)
            self.assertGreater(q["min_passivity_factor"],.9)

    def test_G_absorption_plus_screen_rotation_trace(self):
        import fa03
        data=b.fa02.setup(self.ell,.008,.01)
        P,H,G,k=fa03.fields(.7,data)
        self.assertLess(np.max(abs(G+G.swapaxes(-1,-2)-2*H)),1e-14)
        r=np.random.default_rng(19)
        f=np.einsum('nij,nkj->nik', (r.standard_normal((len(self.ell),2,2))+1j*r.standard_normal((len(self.ell),2,2))), (r.standard_normal((len(self.ell),2,2))+1j*r.standard_normal((len(self.ell),2,2))).conj())
        f=.5*(f+f.swapaxes(-1,-2).conj())
        for eps in (-.1,0,.1):
            for e in (.98,1.02):
                ge=G+eps*(e*k[:,None,None]-1)*H
                source=(e**3*(1+.1*e*k))[:,None,None]*P
                rhs=source-ge@f-f@ge.swapaxes(-1,-2)
                expected=np.trace(source,axis1=-2,axis2=-1)-2*(1+eps*(e*k-1))*np.trace(H@f,axis1=-2,axis2=-1)
                self.assertLess(np.max(abs(np.trace(rhs,axis1=-2,axis2=-1)-expected)),2e-14)

    def test_constant_screen_rotation_covariance(self):
        data=b.fa02.setup(self.ell,.008,.01)
        P,H,G,k=b.fa03.fields(.7,data)
        ca,sa=np.cos(.37),np.sin(.37)
        U=np.array([[ca,-sa],[sa,ca]])
        f=np.array([[.7,.1+.06j],[.1-.06j,.3]])
        c=1+.05*(1.01*k-1)
        B=(1.01**3*(1+.1*1.01*k))[:,None,None]*P
        ge=G+.05*(1.01*k-1)[:,None,None]*H
        R=B-ge@f-f@ge.swapaxes(-1,-2)
        BT=U.T@B@U;GT=U.T@ge@U;FT=U.T@f@U
        RT=BT-GT@FT-FT@GT.swapaxes(-1,-2)
        self.assertLess(np.max(abs(RT-U.T@R@U)),2e-14)

    def test_finite_epsilon_matches_frozen_R7(self):
        for eps in (-.1,0,.1):
            opt=b.solve_energy_batched([eps],steps=64,nr=3,nphi=12,ne=8)[0]
            ref=b.fa03.solve_energy(.008,.01,eps,steps=64,nr=3,nphi=12,ne=8)
            self.assertLess(b.trace_norm(opt-ref),2e-13)

    def test_all_epsilon_one_pass_matches_three_independent(self):
        e=(-.1,0,.1)
        fast=b.solve_energy_batched(e,steps=64,nr=3,nphi=12,ne=8)
        for i,eps in enumerate(e):
            ref=b.fa03.solve_energy(.008,.01,eps,steps=64,nr=3,nphi=12,ne=8)
            self.assertLess(b.trace_norm(fast[i]-ref),2e-13)

    def test_finite_epsilon_Hermitian_psd(self):
        eps=(-.1,-.05,0,.05,.1)
        F=b.solve_energy_batched(eps,steps=64,nr=3,nphi=12,ne=12)
        for f in F:
            self.assertLess(float(np.max(abs(f-f.conj().T))),1e-13)
            self.assertGreater(float(np.linalg.eigvalsh(f).min()),.12)

    def test_epsilon0_agrees_grey_s0(self):
        F=b.solve_energy_batched([0],steps=64,ne=8)[0]
        self.assertLess(b.trace_norm(F-self.y[0]),2e-13)

    def test_epsilon_taylor_V0_W0_derivatives(self):
        # Central-difference bias is O(d^2). .02 was measured at 1.33e-9;
        # reduce the step without loosening the original 1e-9 target.
        d=.01
        Fs=b.solve_energy_batched([-d,0,d],steps=64,ne=10)
        deriv=(Fs[2]-Fs[0])/(2*d)
        second=(Fs[2]-2*Fs[1]+Fs[0])/d**2
        self.assertLess(b.trace_norm(deriv-self.y[3]),1e-9)
        self.assertLess(b.trace_norm(second-self.y[5]),1e-7)

    def test_finite_poly_error_decreases_cubically(self):
        d=.1
        F=b.solve_energy_batched([-d,-d/2,d/2,d],steps=64,ne=8)
        pred=lambda q:self.y[0]+q*self.y[3]+.5*q*q*self.y[5]
        errs=[b.trace_norm(f-pred(q)) for f,q in zip(F,[-d,-d/2,d/2,d])]
        self.assertLess(max(errs[1:3]),max(errs[0],errs[3])*.2)
        self.assertGreater(min(errs[0],errs[3]),1e-10)

    def test_ray_chunk_and_deterministic_threading(self):
        a=b.solve_energy_batched([-.1,0,.1],steps=64,nr=6,nphi=24,ne=8)
        c=b.solve_energy_batched([-.1,0,.1],steps=64,nr=6,nphi=24,ne=8,ray_chunk=36,workers=1)
        d=b.solve_energy_batched([-.1,0,.1],steps=64,nr=6,nphi=24,ne=8,ray_chunk=36,workers=2)
        self.assertLess(max(b.trace_norm(x-y) for x,y in zip(a,c)),2e-13)
        self.assertLess(max(b.trace_norm(x-y) for x,y in zip(a,d)),2e-13)
        self.assertTrue(np.array_equal(c,d))  # same deterministic reduction order

    def test_passivity_coefficient_guarantee(self):
        # General frozen Kasner bound: x>=.5, so v>=x and k=x^-2/3 v>0.
        for x in np.linspace(.5,1,19):
            for k in (x**(1/3),x**(-2/3)):
                for e in (.98,1.02):
                    for eps in (-.1,.1):
                        self.assertGreater(1+eps*(e*k-1),.899999)

    def test_validate_bad_parameters(self):
        bad=[([.11],64,3,12,8),([float('nan')],64,3,12,8),([0],0,3,12,8),([0],64,3,12,1)]
        for eps,steps,nr,nphi,ne in bad:
            with self.assertRaises(ValueError):b.solve_energy_batched(eps,steps=steps,nr=nr,nphi=nphi,ne=ne)
        with self.assertRaises(ValueError):b.solve_energy_batched([0],workers=0)
        with self.assertRaises(ValueError):b.solve_energy_batched([0],ray_chunk=0)
        with self.assertRaises(ValueError):b.solve_energy_batched([0],ell=np.zeros((2,3)),w=np.ones(3))
        with self.assertRaises(ValueError):b.solve_moments_fused(0)

    def test_fixed_cone_margin_is_not_new_observational_claim(self):
        F=b.solve_energy_batched([0],steps=64)[0]
        self.assertGreater(float(np.linalg.eigvalsh(F).min()),.1254)
        # No claim to continuum cap or to accurate cosmological photoionization.
        self.assertIsNone(b.ray_physics_checks()["empirical_atomic_accuracy"])

    def test_moment_rhs_fused_identity_local(self):
        data=b.fa02.setup(self.ell,.008,.01)
        y=np.zeros((6,len(self.ell),2,2),complex)
        rng=np.random.default_rng(15)
        for i in range(6):
            A=rng.standard_normal((len(self.ell),2,2))+1j*rng.standard_normal((len(self.ell),2,2))
            y[i]=A+A.swapaxes(-1,-2).conj()
        slow=b.fa03._rhs(.73,list(y),data)
        fast=b._mom_rhs(y,b._mom_coeff(.73,data))
        self.assertLess(max(np.max(abs(a-c)) for a,c in zip(slow,fast)),1e-14)

if __name__=="__main__":
    unittest.main(verbosity=2)
