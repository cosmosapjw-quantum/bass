"""Contract risks for the new adapter only; no historical suite replay."""
from dataclasses import replace
from fractions import Fraction as F
import unittest
import numpy as np
from locked_bridge import (C, EPS, SUM_TOL, ROUNDTRIP_TOL, ROOT, Units, LockedGrid,
                           load_actual_inputs, to_packets, fixed_grid_inverse,
                           state_boost, physical_sums, packet_observables, residual)
from vendor import kinetic


def synthetic():
    directions = np.r_[np.eye(3), -np.eye(3)]
    grid = LockedGrid(np.array([2.,3.]), np.array([2.,5.]), directions,
                      np.ones(6)/6, ('low','high'), np.array([[1.,2.],[2.,3.]]))
    f = np.array([[0.,.25,.5,.75,1.,1.25], [1.5,1.25,1.,.75,.5,.25]])
    return grid, f


class BridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.grid, cls.f, cls.diag = load_actual_inputs()
        cls.units = Units(8*np.pi*6.67430e-11/C**4, 1e20, 5.45e-27)

    def assert_observables(self, grid, f, units):
        state = to_packets(grid,f,units)
        N,T,Ns,Ts = physical_sums(grid,f)
        a,b = packet_observables(state)
        self.assertLessEqual(residual(a,N,Ns),SUM_TOL)
        self.assertLessEqual(residual(b,T,Ts),SUM_TOL)
        out = fixed_grid_inverse(state,grid)
        positive = f>0
        self.assertTrue(np.array_equal(out[~positive], f[~positive]))
        if np.any(positive): self.assertLessEqual(float(np.max(np.abs(out[positive]/f[positive]-1))),ROUNDTRIP_TOL)
        return state

    def test_actual_910_packets_and_saved_energy_owner(self):
        state = self.assert_observables(self.grid,self.f,self.units)
        self.assertEqual(state.k.shape,(910,3))
        self.assertEqual(len(state.cell_labels),910)
        self.assertEqual(self.diag['raw_angular_sum'],1.)
        self.assertFalse(self.diag['coupled_macro_endpoint'])
        self.assertEqual(float(np.max(np.ptp(self.f,axis=1))),0.)
        with np.load(ROOT/'inputs/z1100_direct_network_node.npz',allow_pickle=False) as data:
            np.testing.assert_array_equal(self.grid.p,data['momentum_scale'])
            np.testing.assert_array_equal(self.grid.G,data['mode_measure_m3'])

    def test_true_vacuum_and_exact_zero_preservation(self):
        state = self.assert_observables(self.grid,np.zeros_like(self.f),self.units)
        for beta in ([.6,0,0],[.2,-.3,.1]):
            moved = state_boost(state,beta)
            self.assertTrue(np.all(moved.w==0))
            self.assertTrue(np.all(packet_observables(moved)[0]==0))
            self.assertTrue(np.all(packet_observables(moved)[1]==0))

    def test_isotropic_moments_and_anisotropic_state_pi(self):
        state = self.assert_observables(self.grid,self.f,self.units)
        rho,flux,pbar,pi = kinetic.moments(state.k,state.w,state.mass)
        self.assertLessEqual(float(np.max(np.abs(flux)))/rho,SUM_TOL)
        self.assertLessEqual(float(np.max(np.abs(pi)))/rho,SUM_TOL)
        self.assertLessEqual(abs(pbar/rho-1/3),SUM_TOL)
        # Explicitly synthetic perturbation of actual REC angular INITIAL-DATA.
        anis = self.f*(1+.4*self.grid.directions[:,0]+.3*(3*self.grid.directions[:,2]**2-1)/2)[None,:]
        state = self.assert_observables(self.grid,anis,self.units)
        N,T,Ns,Ts = physical_sums(self.grid,anis)
        rho,flux,pbar,pi = kinetic.moments(state.k,state.w,state.mass)
        alpha=self.units.alpha
        self.assertLessEqual(residual(flux/alpha,T[0,1:],Ts[0,1:]),SUM_TOL)
        expected=T[1:,1:]-np.eye(3)*np.trace(T[1:,1:])/3
        self.assertLessEqual(residual(pi/alpha,expected,Ts[1:,1:]),SUM_TOL)
        self.assertGreater(float(np.max(np.abs(pi)))/rho,.01)

    def test_scalar_L_Pstar_rescalings(self):
        for Lfactor,Pfactor in ((2.,1.),(1.,3.),(.125,7.)):
            other=Units(self.units.kappa,self.units.L*Lfactor,self.units.Pstar*Pfactor)
            state=self.assert_observables(self.grid,self.f,other)
            reference=to_packets(self.grid,self.f,self.units)
            np.testing.assert_allclose(state.k,reference.k/Pfactor,rtol=ROUNDTRIP_TOL,atol=0)
            np.testing.assert_allclose(state.w,reference.w*Lfactor**2*Pfactor,rtol=ROUNDTRIP_TOL,atol=0)

    def test_exact_synthetic_rational_oracle(self):
        grid,f=synthetic()
        N=[F(0) for _ in range(4)];T=[[F(0) for _ in range(4)] for _ in range(4)]
        for i in range(2):
            for j in range(6):
                count=F(int(grid.G[i]))*F(1,6)*F(str(f[i,j]))
                ell=[F(1)]+[F(int(x)) for x in grid.directions[j]]
                for a in range(4):
                    N[a]+=F(int(C))*count*ell[a]
                    for b in range(4):T[a][b]+=F(int(C))*F(int(grid.p[i]))*count*ell[a]*ell[b]
        N=np.array([float(x) for x in N]);T=np.array([[float(x) for x in row] for row in T])
        state=self.assert_observables(grid,f,Units(1,2,3))
        a,b=packet_observables(state)
        self.assertLessEqual(residual(a,N,np.abs(N)),SUM_TOL)
        self.assertLessEqual(residual(b,T,np.abs(T)),SUM_TOL)
        # Rational beta 3/5 gives exact gamma=5/4, independently specified.
        B=np.array([[1.25,.75,0,0],[.75,1.25,0,0],[0,0,1,0],[0,0,0,1]])
        moved=state_boost(state,[.6,0,0]);a,b=packet_observables(moved)
        self.assertLessEqual(residual(a,B@N,np.abs(B)@np.abs(N)),SUM_TOL)
        self.assertLessEqual(residual(b,B@T@B.T,np.abs(B)@np.abs(T)@np.abs(B.T)),SUM_TOL)

    def test_boost_covariance_and_explicit_inverse(self):
        grid=self.grid
        anis=self.f*(1+.4*grid.directions[:,0])[None,:]
        original=to_packets(grid,anis,self.units)
        N,T,Ns,Ts=physical_sums(grid,anis)
        for beta in (np.array([.6,0,0]),np.array([.2,-.3,.1])):
            B=kinetic.boost_matrix(beta)
            moved=state_boost(original,beta)
            a,b=packet_observables(moved)
            self.assertLessEqual(residual(a,B@N,np.abs(B)@Ns),SUM_TOL)
            self.assertLessEqual(residual(b,B@T@B.T,np.abs(B)@Ts@np.abs(B.T)),SUM_TOL)
            with self.assertRaises(ValueError):fixed_grid_inverse(moved,grid)
            returned=state_boost(moved,-beta)
            recovered=fixed_grid_inverse(returned,grid)
            self.assertLessEqual(float(np.max(np.abs(recovered/anis-1))),ROUNDTRIP_TOL)
            bad=replace(moved,w=original.w)
            self.assertGreater(residual(packet_observables(bad)[1],B@T@B.T,np.abs(B)@Ts@np.abs(B.T)),1e-3)

    def test_mutations_wrong_G_and_competing_energy_are_detected(self):
        N,T,Ns,Ts=physical_sums(self.grid,self.f)
        wrongG=replace(self.grid,G=self.grid.G/np.sum(self.grid.G))
        a,b=packet_observables(to_packets(wrongG,self.f,self.units))
        self.assertGreater(residual(a,N,Ns),.1)
        wrongE=replace(self.grid,p=self.diag['target_energy_J']/C)
        a,b=packet_observables(to_packets(wrongE,self.f,self.units))
        self.assertLessEqual(residual(a,N,Ns),SUM_TOL)
        self.assertGreater(residual(b,T,Ts),1000*SUM_TOL)

    def test_incompatible_inverse_identity_labels_grid_mass_frame(self):
        state=to_packets(self.grid,self.f,self.units)
        for bad in (replace(state,grid_identity='wrong'),replace(state,cell_labels=state.cell_labels[::-1]),
                    replace(state,angular_labels=state.angular_labels[::-1]),replace(state,k=state.k*1.001),
                    replace(state,mass=np.ones(910)),replace(state,frame=np.diag([1,1,1,2]))):
            with self.subTest(kind=str(bad.grid_identity)[:8]):
                with self.assertRaises(ValueError):fixed_grid_inverse(bad,self.grid)

    def test_invalid_inputs_are_rejected_without_clipping(self):
        for value in (-1.,0.,np.inf,np.nan,1+0j):
            for key in ('kappa','L','Pstar'):
                args=dict(kappa=1,L=1,Pstar=1);args[key]=value
                with self.subTest(key=key,value=value):
                    with self.assertRaises(ValueError):Units(**args)
        for value in (-1.,np.inf,np.nan,1+0j):
            f=self.f.astype(complex if np.iscomplexobj(value) else float);f=f.copy();f[0,0]=value
            with self.assertRaises(ValueError):to_packets(self.grid,f,self.units)
        for field in ('G','p','A','directions','intervals'):
            for value in (np.nan,np.inf,1+0j):
                array=getattr(self.grid,field).astype(complex if np.iscomplexobj(value) else float).copy()
                array.flat[0]=value
                with self.assertRaises(ValueError):replace(self.grid,**{field:array})
        for field in ('G','p','A'):
            array=getattr(self.grid,field).copy();array[0]=0
            with self.assertRaises(ValueError):replace(self.grid,**{field:array})
        with self.assertRaises(ValueError):replace(self.grid,A=self.grid.A*2)
        with self.assertRaises(ValueError):replace(self.grid,directions=self.grid.directions*2)
        with self.assertRaises(ValueError):to_packets(self.grid,self.f[:1],self.units)
        for beta in ([1,0,0],[np.nan,0,0],[.1+0j,0,0],[0,0]):
            with self.assertRaises(ValueError):state_boost(to_packets(self.grid,self.f,self.units),beta)

    def test_positive_underflow_and_overflow_are_explicit(self):
        grid,f=synthetic()
        with self.assertRaises(ValueError):Units(1e-300,1e-100,1)
        with self.assertRaises(ValueError):Units(1e300,1e100,1)
        with self.assertRaises(ValueError):to_packets(replace(grid,G=np.full(2,1e-300)),np.full_like(f,1e-100),Units(1,1,1))
        with self.assertRaises(ValueError):to_packets(grid,np.full_like(f,1e300),Units(1e100,1,1))
        with self.assertRaises(ValueError):to_packets(replace(grid,p=np.full(2,1e-300)),f,Units(1,1,1e100))
        # Nonzero packets must not become an apparent vacuum through the
        # unchanged vendor tensor's w*e or w/e floating operations.
        state=to_packets(grid,f,Units(1,1,1))
        for kfactor,wfactor in ((1e-150,1e-220),(1e100,1e-320)):
            bad=replace(state,k=state.k*kfactor,w=state.w*wfactor)
            with self.assertRaises(ValueError):packet_observables(bad)


if __name__=='__main__':unittest.main(verbosity=2)
