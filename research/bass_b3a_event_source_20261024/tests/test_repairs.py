"""Authorized F1/F2 regressions and exact-zero donor obligation.

Initially run against the pre-repair implementation; raw RED receipt retained.
"""
from dataclasses import replace
from pathlib import Path
import sys
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'code'))
from event_measure import Identity,GrossEventBundle,moments
from rec_adapter import owner,OWNER,event_bundle
from bass_binding import bass_rate_pair,attach_source

CLOCK = 'proper_time_dt_dV_invariant'


class AuthorizedRepairTests(unittest.TestCase):
    def setUp(self):
        self.identity=Identity(OWNER,'repair_epoch','rest',CLOCK,'CONSTRUCTED_REPAIR_FIXTURE')
        self.state=owner.state_at_depth('H_LYA_EFFECTIVE_2P','emission',3.7,np.zeros((3,3)))

    def test_F1_canonical_source_origin_and_binding_clock(self):
        for field,value in [('clock','ln_a'),('clock','conformal_time'),('frame','already_boosted')]:
            with self.subTest(field=field,value=value):
                with self.assertRaises(ValueError):
                    event_bundle(self.state,replace(self.identity,**{field:value}),n_mu=2,n_phi=2)
        bundle=event_bundle(self.state,self.identity,n_mu=2,n_phi=2)
        moved=bundle.boosted([.2,0,0],frame='any_explicit_target_frame')
        self.assertEqual(moved.down.identity.clock,CLOCK)
        self.assertEqual(moved.down.identity.frame,'any_explicit_target_frame')
        self.assertIsNotNone(bass_rate_pair(moved,length_m=1e12))
        for clock in ['ln_a','conformal_time']:
            bad=replace(self.identity,clock=clock)
            forged=GrossEventBundle(replace(bundle.down,identity=bad),replace(bundle.up,identity=bad))
            with self.subTest(pair_clock=clock):
                with self.assertRaises(ValueError): bass_rate_pair(forged,length_m=1e12)

    def test_F2_cross_frame_duplicate_physical_transfer(self):
        bundle=event_bundle(self.state,self.identity,n_mu=2,n_phi=2)
        kwargs=dict(length_m=1e12,pressure=[0.,0.],pi=np.zeros((2,3,3)),
                    transfer_id='same_physical_event',positive_domain=lambda rates:True)
        first=attach_source(bundle,expected_identity=self.identity,**kwargs)
        moved=bundle.boosted([.2,0,0],frame='new_observer')
        with self.assertRaises(ValueError):
            attach_source(moved,expected_identity=moved.down.identity,applied_transfer_keys=first.applied_transfer_keys,**kwargs)

    def test_exact_zero_actual_donor_no_callback_binding(self):
        # Positive lower population and opacity, but neither upper population
        # nor incoming occupancy. No new finite reservoir is asserted.
        zero=owner.LineState('H_LYA_EFFECTIVE_2P','collapsed_2p',1e9,0.,1e-13,0.,np.zeros((3,3)),
                             'CONSTRUCTED_EXACT_ZERO_SOURCE','CONSTRUCTED_S_ZERO_FIXTURE')
        direct=owner.exchange_source(zero,n_mu=2,n_phi=2)
        self.assertEqual(direct['gross_escaped_down_m3_s'],0.)
        self.assertEqual(direct['gross_escaped_up_m3_s'],0.)
        bundle=event_bundle(zero,self.identity,n_mu=2,n_phi=2)
        for events in [bundle.down,bundle.up]:
            self.assertTrue(np.array_equal(events.rates_m3_s,np.zeros(len(events.energy_J))))
            m=moments(events)
            self.assertTrue(np.array_equal(m.cQ_J_m3_s,np.zeros(4)))
            self.assertTrue(np.array_equal(m.K_J_m3_s,np.zeros((4,4))))
            self.assertTrue(np.array_equal(m.PiRate_J_m3_s,np.zeros((3,3))))
        p=np.array([.01,.02])
        pi=np.array([np.diag([.1,-.03,-.07]),np.diag([.02,.01,-.03])])
        attached=attach_source(bundle,length_m=1e12,pressure=p,pi=pi,expected_identity=self.identity,
                               transfer_id='zero_event')  # callback intentionally absent
        self.assertTrue(np.array_equal(attached.rates.U,np.zeros(2)))
        self.assertTrue(np.array_equal(attached.rates.J,np.zeros((2,3))))
        self.assertTrue(np.array_equal(attached.rates.PiRate_hat_radiation,np.zeros((3,3))))
        self.assertTrue(np.array_equal(attached.source.pressure,p))
        self.assertTrue(np.array_equal(attached.source.pi,pi))


if __name__=='__main__':unittest.main(verbosity=2)
