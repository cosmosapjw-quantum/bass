"""Recovery-path regressions for the saved S3 campaign; no optimization rerun."""
import copy
import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch
from run_s3_campaign import validate_reused_measurements

HERE=Path(__file__).resolve().parent


class RecoveryGuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original=json.loads((HERE/'evidence_s3/campaign/ANGULAR_CAMPAIGN.json').read_text())
        cls.sources={p:hashlib.sha256((HERE/p).read_bytes()).hexdigest()
                     for p in cls.original['source_sha256']}

    def fresh(self):return copy.deepcopy(self.original)

    def row(self,data,mode='P2'):
        return next(r for r in data['rows'] if r['constraint']==mode and r['birth_b']==.3 and r['n_mu']==8)

    def reject(self,data,tag):
        with self.assertRaisesRegex(ValueError,tag):
            validate_reused_measurements(data,self.sources)

    def test_valid_saved_run_uses_no_optimizer(self):
        with patch('run_s3_campaign.project',side_effect=AssertionError('optimizer rerun')), \
             patch('run_s3_campaign.project2',side_effect=AssertionError('optimizer rerun')):
            rows=validate_reused_measurements(self.fresh(),self.sources)
        self.assertEqual(len(rows),165)
        self.assertEqual(sum(r['status']=='MEASURED' for r in rows),146)

    def test_duplicate_key_is_not_a_full_grid(self):
        d=self.fresh();d['rows'][1]=copy.deepcopy(d['rows'][0])
        self.reject(d,'MEASUREMENT_GRID_CHANGED')

    def test_changed_grid_and_dependency_are_rejected(self):
        d=self.fresh();d['rows'][0]['birth_b']=.31
        self.reject(d,'MEASUREMENT_GRID_CHANGED')
        d=self.fresh();d['source_sha256']['angular_balance.py']='0'*64
        self.reject(d,'MEASUREMENT_DEPENDENCY_CHANGED')

    def test_support_and_prior_must_match_original_source_frame(self):
        for field in ['mu','prior']:
            with self.subTest(field=field):
                d=self.fresh();self.row(d)[field][0]+=1e-8
                self.reject(d,'MEASUREMENT_SOURCE_FRAME_CHANGED')

    def test_weight_domain_and_reflection_are_checked(self):
        for replacement,tag in [(float('nan'),'MEASUREMENT_ARRAY_DOMAIN'),
                                (-1e-8,'MEASUREMENT_POSITIVE_PARITY_NORMALIZATION')]:
            with self.subTest(replacement=replacement):
                d=self.fresh();self.row(d)['weights'][0]=replacement;self.reject(d,tag)
        d=self.fresh();w=self.row(d)['weights'];w[0]+=1e-6;w[1]-=1e-6
        self.reject(d,'MEASUREMENT_POSITIVE_PARITY_NORMALIZATION')

    def test_p2_gate_recomputes_weights_not_cached_moment(self):
        d=self.fresh();w=self.row(d)['weights']
        w[0]+=1e-5;w[-1]+=1e-5;w[1]-=1e-5;w[-2]-=1e-5
        self.reject(d,'MEASUREMENT_P2_CONSTRAINT')

    def test_p24_gate_does_not_accept_p2_only_weights(self):
        d=self.fresh();self.row(d,'P24')['weights']=self.row(d)['weights'].copy()
        self.reject(d,'MEASUREMENT_P4_CONSTRAINT')

    def test_cached_diagnostic_is_verified(self):
        d=self.fresh();self.row(d)['diagnostics']['moments']['2']=0.25
        self.reject(d,'MEASUREMENT_DIAGNOSTICS_CHANGED')

    def test_response_d_grid_and_values_are_verified(self):
        d=self.fresh();self.row(d)['response'][0]['d']=-.21
        self.reject(d,'MEASUREMENT_RESPONSE_GRID_CHANGED')
        d=self.fresh();self.row(d)['response'][0]['A']+=1e-4
        self.reject(d,'MEASUREMENT_RESPONSE_CHANGED')

    def test_rejection_requires_recomputed_support_failure(self):
        d=self.fresh();r=self.row(d);r.update(status='REJECTED',error='INFEASIBLE_ANGULAR_SUPPORT',failure_class='support_feasibility')
        self.reject(d,'MEASUREMENT_REJECTION_UNVERIFIED')
        d=self.fresh();d['rows'][0]['P24_feasibility']['status']='STRICT_INTERIOR'
        self.reject(d,'MEASUREMENT_FEASIBILITY_CHANGED')

    def test_prior_baseline_cannot_be_reweighted(self):
        d=self.fresh();self.row(d,'prior')['weights']=self.row(d)['weights'].copy()
        self.reject(d,'MEASUREMENT_PRIOR_CHANGED')

    def test_reference_and_derivative_caches_are_checked(self):
        d=self.fresh();d['continuum_reference'][0]['d']=-.21
        self.reject(d,'MEASUREMENT_REFERENCE_GRID_CHANGED')
        d=self.fresh();self.row(d)['central_A_prime_h1e_5']=0.
        self.reject(d,'MEASUREMENT_DERIVATIVE_CHANGED')


if __name__=='__main__':unittest.main()
