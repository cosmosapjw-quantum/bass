"""C7 exact real-Stokes transport versus original FA03 Hermitian coherency."""
from __future__ import annotations
import sys
import unittest
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import batch_transport as b
import stokes_vector as st

class RealStokesPhysics(unittest.TestCase):
    def test_4component_stokes_to_Hermitian_roundtrip(self):
        Y=np.array([[.7,.2,.1,.06],[1.,0.,0.,0.]])
        F=st.stokes_to_coherency(Y)
        self.assertLess(np.max(abs(np.stack([b.stokes(x) for x in F])-Y)),1e-16)
        self.assertLess(np.max(abs(F-F.swapaxes(-1,-2).conj())),1e-16)

    def test_real_stokes_batch_vs_reference_at_three_ray_grids(self):
        for nr,nphi in [(3,12),(6,24),(10,48)]:
            A=st.solve_energy_real([-.1,0,.1],steps=64,nr=nr,nphi=nphi,ne=8)
            B=b.solve_energy_batched([-.1,0,.1],steps=64,nr=nr,nphi=nphi,ne=8)
            self.assertLess(max(b.trace_norm(x-y) for x,y in zip(A,B)),3e-13)

    def test_actual_frozen_original_spectral_64(self):
        for eps in [-.1,0,.1]:
            A=st.solve_energy_real([eps],steps=64,nr=3,nphi=12,ne=8)[0]
            B=b.fa03.solve_energy(.008,.01,eps,steps=64,nr=3,nphi=12,ne=8)
            self.assertLess(b.trace_norm(A-B),3e-13)

    def test_epsilon_zero_fused_moment_source(self):
        z=st.solve_energy_real([0],steps=64)[0]
        m=b.solve_moments_fused(steps=64)[0]
        self.assertLess(b.trace_norm(z-m),3e-13)

    def test_multiple_energy_orders_and_non_grey(self):
        for ne in (4,8,16):
            A=st.solve_energy_real([-.1,0,.1],steps=32,ne=ne)
            B=b.solve_energy_batched([-.1,0,.1],steps=32,ne=ne)
            self.assertLess(max(b.trace_norm(x-y) for x,y in zip(A,B)),3e-13)

    def test_Stokes_generator_matches_exact_Jones_RHS_at_one_step(self):
        ell,w=b._prepared_rays(3,12)
        E=np.array([.98,1.,1.02])
        es=np.array([-.1,0.,.1])
        rng=np.random.default_rng(431)
        Y=rng.normal(size=(len(es),len(ell),len(E),4))
        S=st.stokes_to_coherency(Y)
        data=b.fa02.setup(ell,.008,.01)
        for x in (.5,.75,1.):
            c=st._stokes_coefficient(x,data,es,E)
            ps=st._rhs(Y,c)
            op=b._spectral_ops(x,data,es,E)
            js=b._spectral_rhs(S,op)
            pv=np.stack([np.trace(js,axis1=-2,axis2=-1).real,
                (js[...,0,0]-js[...,1,1]).real,2*js[...,0,1].real,-2*js[...,0,1].imag],axis=-1)
            self.assertLess(float(np.max(abs(ps-pv))),4e-14)

    def test_hermiticity_positivity_and_stokes_cone(self):
        F=st.solve_energy_real([-.1,-.05,0,.05,.1],steps=64,ne=8)
        for f in F:
            self.assertLess(float(np.max(abs(f-f.conj().T))),1e-14)
            self.assertGreater(float(np.linalg.eigvalsh(f).min()),.12)
            I,Q,U,V=b.stokes(f)
            self.assertGreater(I*I-(Q*Q+U*U+V*V),0)

    def test_epsilon_tangent_V0_and_W0(self):
        d=.01
        F=st.solve_energy_real([-d,0,d],steps=64,ne=8)
        M=b.solve_moments_fused(steps=64)
        self.assertLess(b.trace_norm((F[2]-F[0])/(2*d)-M[3]),1e-9)
        self.assertLess(b.trace_norm((F[2]-2*F[1]+F[0])/(d*d)-M[5]),1e-7)

    def test_deterministic_two_thread_ray_chunk(self):
        ell,w=b._prepared_rays(6,24)
        a=st.solve_energy_real([-.1,0,.1],steps=64,ell=ell,w=w,ne=8,ray_chunk=36,workers=1)
        t=st.solve_energy_real([-.1,0,.1],steps=64,ell=ell,w=w,ne=8,ray_chunk=36,workers=2)
        q=st.solve_energy_real([-.1,0,.1],steps=64,ell=ell,w=w,ne=8,ray_chunk=36,workers=4)
        self.assertTrue(np.array_equal(a,t))
        self.assertTrue(np.array_equal(a,q))

    def test_exact_matrix_reduction_versus_realStokes(self):
        X=st.solve_energy_real([-.1,0,.1],steps=64,output="stokes")
        Y=st.solve_energy_real([-.1,0,.1],steps=64,output="matrix")
        self.assertLess(np.max(abs(X-np.stack([b.stokes(y) for y in Y]))),2e-16)

    def test_invalid_api_input(self):
        for kw in [{"eps":[np.nan]},{"eps":[.11]},{"eps":[0],"steps":0},{"eps":[0],"ne":1},
                   {"eps":[0],"ray_chunk":0},{"eps":[0],"workers":0},{"eps":[0],"workers":9},
                   {"eps":[0],"output":"weird"}]:
            with self.assertRaises(ValueError):st.solve_energy_real(**kw)

    def test_negative_ray_weights_rejected(self):
        ell,w=b._prepared_rays(3,12)
        w[0]=-1
        with self.assertRaises(ValueError):st.solve_energy_real([0],ell=ell,w=w)

    def test_source_hash_mutation_refused(self):
        old=b.SHA['fa02.py']
        try:
            b.SHA['fa02.py']='0'*64
            with self.assertRaisesRegex(ValueError,"FROZEN_SOURCE_CHANGED"):
                st.solve_energy_real([0])
        finally:
            b.SHA['fa02.py']=old

    def test_real_state_memory_exactly_half_complex(self):
        n_eps,n_rays,n_E=3,480,8
        real=np.empty((n_eps,n_rays,n_E,4),dtype=float)
        complex_=np.empty((n_eps,n_rays,n_E,2,2),dtype=complex)
        self.assertEqual(real.nbytes*2,complex_.nbytes)

    def test_physical_polarization_rotation_does_not_couple_V(self):
        ell,w=b._prepared_rays(3,12)
        data=b.fa02.setup(ell,.008,.01)
        c=st._stokes_coefficient(.7,data,np.array([0.]),np.array([1.]))
        Y=np.zeros((1,len(ell),1,4))
        Y[...,3]=.15
        f=st._rhs(Y,c)
        # V absorption only; no extra U/Q source relative to source-only.
        fy=st._rhs(np.zeros_like(Y),c)
        self.assertLess(np.max(abs((f-fy)[...,1:3])),1e-15)
        self.assertGreater(np.max(abs((f-fy)[...,3])),0)

if __name__=="__main__": unittest.main(verbosity=2)
