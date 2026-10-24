"""Current local finite-quadrature checks; no IVP or old campaign replay."""
from dataclasses import replace
from itertools import product
from pathlib import Path
import math
import sys
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'code'))
from event_measure import *
from rec_adapter import owner,angular,OWNER,event_bundle,native_scalar_state
from bass_binding import bass_rate_pair,attach_source,core

GATE = 5e-12


class EventTests(unittest.TestCase):
    def close(self,actual,expected,scale=1.):
        self.assertLessEqual(float(np.max(np.abs(np.asarray(actual)-np.asarray(expected))))/scale,GATE)

    def test_AB_rest(self):
        for name in 'AB':
            m = moments(ab_fixture(name))
            self.close(m.cQ_J_m3_s,[1,0,0,0])
            self.close(m.K_J_m3_s,np.diag([1,1/3,1/3,1/3]))
            self.close(m.PiRate_J_m3_s,np.zeros((3,3)))

    def test_AB_exact_three_fifths(self):
        expected = {'A':np.diag([3/10,-3/20,-3/20]),'B':np.diag([5/22,-5/44,-5/44])}
        for name in 'AB':
            e = ab_fixture(name)
            boosted = e.boosted([3/5,0,0],frame='axis_3_5')
            self.assertTrue(np.array_equal(e.rates_m3_s,boosted.rates_m3_s))
            m = moments(boosted)
            self.close(m.cQ_J_m3_s,[5/4,3/4,0,0])
            self.close(m.PiRate_J_m3_s,expected[name])
            self.close(m.PiRate_J_m3_s[0,0],exact_axis_pi_xx(name,3/5))

    def test_wrong_density_weight_negative_control(self):
        e = ab_fixture('A')
        boosted = e.boosted([.6,0,0],frame='boost')
        # Deliberately wrong kinetic density transformation, prohibited in adapter.
        wrong = replace(boosted,rates_m3_s=e.rates_m3_s*boosted.energy_J/e.energy_J)
        self.close(moments(wrong).cQ_J_m3_s,[7/4,5/4,0,0])
        self.assertGreater(np.linalg.norm(moments(wrong).cQ_J_m3_s-moments(boosted).cQ_J_m3_s),.1)

    def test_oblique_counterexample(self):
        v = [1/5,2/5,2/5]
        a,b = [moments(ab_fixture(n).boosted(v,frame='oblique')) for n in 'AB']
        delta = a.PiRate_J_m3_s[0,0]-b.PiRate_J_m3_s[0,0]
        self.close(delta,-286408/10384605)
        self.assertLess(delta,0)
        self.assertGreater(exact_axis_pi_xx('A',.6)-exact_axis_pi_xx('B',.6),0)
        with self.assertRaises(ValueError): exact_axis_pi_xx('A',v)

    def test_nonaxis_observer_covariance_and_denominator(self):
        e = ab_fixture('A')
        v = [.2,-.31,.17]
        L = boost_matrix(v)
        m = moments(e)
        moved = e.boosted(v,frame='nonaxis')
        u = L@np.array([1.,0,0,0])
        changed = moments(moved,observer=u)
        self.close(changed.K_J_m3_s,L@m.K_J_m3_s@L.T)
        self.close(changed.cQ_J_m3_s,L@m.cQ_J_m3_s)
        self.close(changed.K_J_m3_s@np.r_[-u[0],u[1:]],-changed.cQ_J_m3_s)
        self.assertIsNone(changed.PiRate_J_m3_s)
        target = moments(moved)
        self.assertGreater(np.linalg.norm(target.K_J_m3_s-changed.K_J_m3_s),.01)
        self.close(-target.K_J_m3_s[0,0]+np.trace(target.K_J_m3_s[1:,1:]),0)

    def test_event_domain_rejection(self):
        e = ab_fixture('A')
        bad = [dict(energy_J=np.zeros(6)),dict(energy_J=np.full(6,np.nan)),dict(energy_J=np.ones(6,dtype=complex)),
               dict(rates_m3_s=-np.ones(6)),dict(rates_m3_s=np.ones(6,dtype=bool)),dict(directions=e.directions*2),
               dict(directions=np.full((6,3),np.inf))]
        for args in bad:
            with self.subTest(args=list(args)):
                with self.assertRaises(ValueError): replace(e,**args)
        for beta in ([1,0,0],[True,0.,0.],[0,0,complex(0)], [math.nan,0,0]):
            with self.assertRaises(ValueError): boost_matrix(beta)
        with self.assertRaises(ValueError): moments(e,observer=[0,0,0,0])


class DonorAndBindingTests(unittest.TestCase):
    close = EventTests.close

    def identity(self,epoch='epoch0',frame='rest'):
        return Identity(OWNER,epoch,frame,'proper_time_dt_dV_invariant','CONSTRUCTED_S_FIXTURE; detached REC gross channels')

    def fixtures(self):
        return [(label,owner.state_at_depth('H_LYA_EFFECTIVE_2P',label,3.7,owner.shear_fixtures()['rotated'])) for label in ['emission','absorption','LTE']]

    def test_constructed_gross_donor_parity_signs_and_LTE(self):
        for label,state in self.fixtures():
            with self.subTest(label=label):
                bundle = event_bundle(state,self.identity())
                net = bundle.net_moments()
                direct = owner.exchange_source(state,n_mu=12,n_phi=20)
                down,up = moments(bundle.down),moments(bundle.up)
                scale = down.cQ_J_m3_s[0]+up.cQ_J_m3_s[0]
                self.assertGreaterEqual(float(bundle.down.rates_m3_s.min()),0)
                self.assertGreaterEqual(float(bundle.up.rates_m3_s.min()),0)
                self.close(down.number_rate_m3_s,direct['gross_escaped_down_m3_s'],direct['gross_escaped_down_m3_s']+direct['gross_escaped_up_m3_s'])
                self.close(up.number_rate_m3_s,direct['gross_escaped_up_m3_s'],direct['gross_escaped_down_m3_s']+direct['gross_escaped_up_m3_s'])
                self.close(net.cQ_J_m3_s[0],direct['du_radiation_J_m3_s'],scale)
                self.close(net.K_J_m3_s[1:,1:],direct['radiation_spatial_injection_J_m3_s'],scale)
                self.close(net.PiRate_J_m3_s,direct['energy_PSTF_J_m3_s'],scale)
                self.close(down.cQ_J_m3_s[1:],np.zeros(3),scale)
                self.close(up.cQ_J_m3_s[1:],np.zeros(3),scale)
                self.assertEqual(len(bundle.down.energy_J),8*12*20)
                if label == 'emission': self.assertGreater(net.cQ_J_m3_s[0],0)
                if label == 'absorption': self.assertLess(net.cQ_J_m3_s[0],0)
                if label == 'LTE': self.close(net.cQ_J_m3_s[0],0,scale)

    def test_all_eight_signs_in_owner_eigenbasis(self):
        state = self.fixtures()[0][1]
        bundle = event_bundle(state,self.identity())
        data = angular.validate_inputs(1,state.S)
        principal = bundle.down.directions@data.eigenvectors
        # Every principal node has the full octant group, with equal rates.
        for n,w in zip(principal.reshape(-1,8,3),bundle.down.rates_m3_s.reshape(-1,8)):
            self.assertEqual({tuple(np.sign(a)) for a in n},set(product((-1.,1.),repeat=3)))
            self.assertTrue(np.array_equal(w,np.repeat(w[0],8)))

    def test_native_scalar_actual_owner_call(self):
        state,info = native_scalar_state(owner.shear_fixtures()['rotated'])
        bundle = event_bundle(state,self.identity())
        net = bundle.net_moments()
        direct = owner.exchange_source(state,n_mu=12,n_phi=20)
        scale = sum(moments(e).cQ_J_m3_s[0] for e in (bundle.down,bundle.up))
        self.close(net.cQ_J_m3_s[0],direct['du_radiation_J_m3_s'],scale)
        self.close(net.PiRate_J_m3_s,direct['energy_PSTF_J_m3_s'],scale)
        t = direct['t']
        self.close(angular.beta_vector(t,np.array([.7,1.,1.3])),
                   np.array([angular.donor_beta_reference(t,q) for q in [.7,1.,1.3]]),max(direct['B'],1e-300))
        self.assertEqual(info['new_native_solver_calls'],0)

    def test_owner_opacity_shear_domain_rejection(self):
        state = self.fixtures()[0][1]
        with self.assertRaises(ValueError): event_bundle(state,replace(self.identity(),owner='wrong_donor'))
        for args in [dict(n_u_m3=3*state.n_l_m3),dict(S=np.diag([-2.,1.,1.])),dict(H_s_inv=0),dict(f_plus=-1),dict(native_line_owner_active=True)]:
            with self.assertRaises(ValueError): replace(state,**args)
        with self.assertRaises(ValueError): native_scalar_state(np.zeros((3,3),dtype=bool))

    def test_BASS_balance_state_copy_and_rate_units(self):
        bundle = event_bundle(self.fixtures()[0][1],self.identity()).boosted([.2,.3,-.1],frame='test_boost')
        p = np.array([.01,.02])
        pi = np.array([np.diag([.1,-.03,-.07]),np.diag([.02,.01,-.03])])
        result = attach_source(bundle,length_m=3e12,pressure=p,pi=pi,expected_identity=bundle.down.identity,transfer_id='x',positive_domain=lambda rates: True)
        src = result.source
        self.close(src.energy_transfer.sum(),0)
        self.close(src.momentum_transfer.sum(axis=0),np.zeros(3))
        self.assertTrue(np.array_equal(src.pressure,p))
        self.assertTrue(np.array_equal(src.pi,pi))
        self.assertFalse(np.shares_memory(src.pi,pi))
        factor = 8*np.pi*G/C**4*(3e12)**3/C
        net = bundle.net_moments()
        self.close(result.rates.U[0],factor*net.cQ_J_m3_s[0],abs(result.rates.U[0]))
        self.close(result.rates.J[0],factor*net.cQ_J_m3_s[1:],abs(result.rates.U[0]))
        self.close(result.rates.PiRate_hat_radiation,factor*net.PiRate_J_m3_s,abs(result.rates.U[0]))
        self.assertEqual(result.rates.thermal_energy_rate,0)
        self.assertEqual(result.rates.ionization_yield,0)
        with self.assertRaises(ValueError):
            core.Source(p,pi,src.energy_transfer,src.momentum_transfer+[[1,0,0],[0,0,0]]).arrays(2)

    def test_callback_duplicate_stale_and_identity_refusal(self):
        bundle = event_bundle(self.fixtures()[0][1],self.identity())
        kwargs = dict(length_m=1e12,pressure=[0.,0.],pi=np.zeros((2,3,3)),expected_identity=self.identity(),transfer_id='unique')
        for callback in (None,lambda rates: False):
            with self.assertRaises(ValueError): attach_source(bundle,**kwargs,positive_domain=callback)
        attached = attach_source(bundle,**kwargs,positive_domain=lambda rates: True)
        with self.assertRaises(ValueError): attach_source(bundle,**kwargs,positive_domain=lambda rates: True,applied_transfer_keys=attached.applied_transfer_keys)
        for field in ('owner','epoch','frame','clock','provenance'):
            bad = {**kwargs,'expected_identity':replace(self.identity(),**{field:'stale'})}
            with self.assertRaises(ValueError): attach_source(bundle,**bad,positive_domain=lambda rates: True)
        with self.assertRaises(ValueError): attach_source(bundle,**{**kwargs,'length_m':True},positive_domain=lambda rates: True)


if __name__ == '__main__':
    unittest.main(verbosity=2)
