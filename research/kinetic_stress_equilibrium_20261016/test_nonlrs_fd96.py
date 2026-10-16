"""Original FD96 source controls for the non-LRS tensor evaluator."""
import math
import unittest

import numpy as np

from bianchi.matter import freestream
from kinetic_equilibrium import FD96Equilibrium
from nonlrs_fd96 import B, FD96Diagonal, source_einstein_residual
from nonlrs_einstein_ivp import run as run_ivp


class NonLRSFD96(unittest.TestCase):
    def test_original_grid_and_normalization(self):
        f = FD96Diagonal(3., 0.)
        np.testing.assert_array_equal(f.q, freestream._Q)
        np.testing.assert_array_equal(f.dq, freestream._DQ)
        np.testing.assert_array_equal(f.nhat, freestream._NHAT)
        np.testing.assert_array_equal(f.wang, freestream._WANG)
        raw = freestream.moments((1., 1., 1.), 3.)[0]
        self.assertLess(abs(raw/(4*math.pi*f.norm)-1), 3e-15)
        self.assertLess(abs(f.moments(0., (0., 0.)).rho-1), 3e-15)

    def test_lrs_parent_energy_pressure_susceptibility(self):
        d = np.array([-1., -1., 2.])
        for mass in (3., 30., 300.):
            for A in (-1., 0., .5, 2.):
                f = FD96Diagonal(mass, A, polar=32, azimuth=32)
                parent = FD96Equilibrium(mass, angular=32)
                for x, b in ((0., 0.), (.7, -.08), (1.2, .13)):
                    v = f.moments(x, (-b, -b))
                    p = parent.stress(x, b, A)
                    delta = v.pressure[2,2] - .5*(v.pressure[0,0]+v.pressure[1,1])
                    np.testing.assert_allclose([v.rho,v.pbar,delta,v.pressure[0,0],v.pressure[2,2]],
                        [p.rho,p.pbar,p.delta,p.p_perp,p.p_parallel],rtol=2e-12,atol=4e-15)
                    self.assertLess(abs(d @ v.hessian3 @ d + 2*p.chi_b), 3e-12*max(p.rho,1e-5))
                    self.assertLess(abs(-d@np.diag(v.pressure) + 2*p.delta), 3e-12*max(p.rho,1e-5))

    def test_tensor_parity_permutations_and_odd_rejection(self):
        beta=np.array([.08,-.03,-.05]); u=np.array([beta[0],beta[1]])
        f=FD96Diagonal(3., .5)
        v=f.moments(.7,u)
        self.assertEqual(v.parity_defect,0.)
        self.assertLess(v.offdiagonal_max/v.rho,3e-16)
        self.assertLess(abs(np.trace(v.pi))/v.rho,3e-16)
        self.assertGreater(v.quadrature_weight_min,0.)
        for perm in ((1,0,2),(2,0,1),(1,2,0)):
            rotated=FD96Diagonal(3.,.5,permutation=perm)
            b2=beta[list(perm)]
            result=rotated.moments(.7,b2[:2])
            np.testing.assert_allclose(result.pressure,v.pressure[np.ix_(perm,perm)],rtol=2e-14,atol=2e-16)
            self.assertLess(abs(result.rho-v.rho),2e-15)
        odd=lambda n:1.+.4*n[:,0]*n[:,1]
        with self.assertRaisesRegex(ValueError,'OFFDIAGONAL_SOURCE_PARITY'):
            f.moments(.7,u,modifier=odd)
        full=f.moments(.7,u,modifier=odd,diagonal_only=False)
        self.assertGreater(abs(full.pressure[0,1])/full.rho,1e-3)
        for bad in (lambda n:np.zeros(len(n)),
                    lambda n:np.full(len(n),-1e-16),
                    lambda n:np.full(len(n),np.nan)):
            with self.assertRaisesRegex(ValueError,'NONPOSITIVE_PHASE_SPACE_WEIGHT'):
                f.moments(.7,u,modifier=bad,diagonal_only=False)
        with self.assertRaisesRegex(ValueError,'NONPOSITIVE_PHASE_SPACE_WEIGHT'):
            f.moments(0.,(-1.,0.),modifier=lambda n:np.full(len(n),1.7e308),diagonal_only=False)

    def test_derivatives_hessian_and_work(self):
        f=FD96Diagonal(3.,.5)
        x=.7; u=np.array([.04,-.02]); m=f.moments(x,u)
        h=2e-5
        for j in range(2):
            v=np.zeros(2);v[j]=h
            plus=f.moments(x,u+v);minus=f.moments(x,u-v)
            grad=(plus.rho-minus.rho)/(2*h)
            self.assertLess(abs(grad-m.energy_gradient2[j])/m.rho,2e-10)
            hcol=(plus.energy_gradient2-minus.energy_gradient2)/(2*h)
            self.assertLess(np.max(np.abs(hcol-m.hessian2[:,j]))/m.rho,3e-10)
        self.assertGreater(np.linalg.eigvalsh(m.hessian2)[0],0.)
        c=source_einstein_residual(f,x,u,np.array([.03,-.01]))
        self.assertLess(abs(c['energy_work_raw'])/c['energy_work_denominator'],1e-9)
        self.assertLess(abs(c['hamiltonian_raw'])/c['hamiltonian_denominator'],1e-14)
        self.assertLess(c['raychaudhuri_hx'],0.)
        self.assertAlmostEqual(sum(c['signed_shear_over_H']),0.,places=15)

    def test_strict_convexity_root_and_resolution(self):
        for A in (-1.,.5,2.):
            f=FD96Diagonal(3.,A)
            u,m,res=f.neutral_root(.7)
            self.assertLess(res/m.rho,5e-13)
            self.assertGreater(np.linalg.eigvalsh(m.hessian2)[0],0.)
            self.assertLess(abs(u[0]-u[1]),3e-13)
            self.assertLess(abs(-u[0]-FD96Equilibrium(3.).equilibrium(.7,A).b_star),2e-12)
        base=FD96Diagonal(3.,.5)
        candidate=[FD96Diagonal(3.,.5,radial=nr,polar=na,azimuth=na).moments(.7,(.05,-.02))
                   for nr,na in ((64,16),(96,24),(128,32),(160,48))]
        ref=candidate[-1]
        errors=[abs(v.rho-ref.rho)/ref.rho + np.max(abs(v.pressure-ref.pressure))/ref.rho
                +np.max(abs(v.hessian2-ref.hessian2))/ref.rho for v in candidate[:-1]]
        self.assertLess(errors[-1],2e-9)
        self.assertLess(errors[1],errors[0])

    def test_positive_triaxial_fd96_radial_extension_has_genuine_2d_root(self):
        f=FD96Diagonal(3.,.3,triaxial_C=.2,polar=32,azimuth=32)
        u,m,res=f.neutral_root(.7)
        self.assertGreater(abs(u[0]-u[1]),1e-3)
        self.assertLess(res/m.rho,5e-13)
        self.assertGreater(m.quadrature_weight_min,0.)
        self.assertGreater(np.linalg.eigvalsh(m.hessian2)[0],0.)
        self.assertLess(m.offdiagonal_max/m.rho,3e-16)
        beta=B@u
        for perm in ((1,0,2),(2,1,0),(2,0,1)):
            rotated=FD96Diagonal(3.,.3,triaxial_C=.2,polar=32,azimuth=32,permutation=perm)
            bp=beta[list(perm)]
            q=rotated.moments(.7,bp[:2])
            np.testing.assert_allclose(q.pressure,m.pressure[np.ix_(perm,perm)],rtol=2e-14,atol=2e-16)
            self.assertLess(abs(q.rho-m.rho),2e-15)
        with self.assertRaisesRegex(ValueError,'NONPOSITIVE_CONTINUOUS_ANGULAR_SOURCE'):
            FD96Diagonal(3.,2.,triaxial_C=.001)

    def test_source_only_nonlrs_einstein_ivp_invariants(self):
        r=run_ivp()
        self.assertEqual(len(r['rows']),15)
        self.assertLess(r['max_hamiltonian_normalized'],1e-13)
        self.assertLess(r['max_raychaudhuri_normalized'],2e-9)
        self.assertLess(r['max_energy_work_normalized'],2e-9)
        for row in r['rows']:
            self.assertGreater(row['H'],0.)
            self.assertGreater(row['min_hessian_eigen'],0.)
            self.assertLess(row['offdiagonal_over_rho'],1e-12)
            self.assertAlmostEqual(sum(row['signed_shear_over_H']),0.,places=14)


if __name__=='__main__': unittest.main()
