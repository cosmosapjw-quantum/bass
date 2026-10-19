"""S7 guards exercise execution/evidence boundaries, not the previous S3 tests."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import run_native_cohorts as subject


class NativeCohortEvidenceTests(unittest.TestCase):
    def test_numpy_worker_cap_is_explicit_even_for_inherited_large_value(self):
        import os
        for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):
            self.assertEqual(os.environ[key],'1')

    def test_matrix_separates_axes_without_repeating_same_physical_case(self):
        rows=subject.matrix()
        keys=[tuple(r[k] for k in ('n_mu','n_energy','cells_per_segment','cohorts','b0','beta','x_observe','mode','slab')) for r in rows]
        self.assertEqual(len(keys),51)
        self.assertEqual(len(set(keys)),len(keys))
        self.assertEqual({r['cohorts'] for r in rows if r['block']=='birth_time'},{8,32,64,128})
        self.assertTrue(all(r['n_mu']<=32 for r in rows))

    def test_csv_preserves_case_identity_and_boolean_domain(self):
        rows=subject.matrix();lines=subject.case_csv(rows).splitlines()
        self.assertEqual(len(lines),len(rows))
        self.assertTrue(all(len(l.split(','))==11 for l in lines))
        self.assertEqual({l.split(',')[-1] for l in lines},{'0','1'})

    def test_unpublished_or_changed_contract_cannot_execute(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'PREREGISTRATION.json';contract=subject.contract()
            path.write_text(json.dumps(contract));contract['pinned_sha256']['native_cohort_probe.rs']='0'*64
            with self.assertRaisesRegex(ValueError,'SOURCE_CHANGED_AFTER_PREREGISTRATION'):
                subject.verify_publication(path,contract)

    def test_contract_cannot_relax_gates_or_omit_source_hash_keys(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'PREREGISTRATION.json'
            for change in ('gate','hash_key','schema','limit'):
                contract=subject.contract()
                if change=='gate':contract['gates']['moment_absolute']=1e-10
                elif change=='hash_key':del contract['pinned_sha256']['native_adapter.rs']
                elif change=='schema':contract['schema']='unreviewed_schema'
                else:contract['limits']['ram_bytes']=2*subject.RAM
                path.write_text(json.dumps(contract))
                with self.assertRaisesRegex(ValueError,'PREREGISTRATION_CONTRACT_CHANGED'):
                    subject.verify_publication(path,contract)

    def test_external_publication_receipt_is_bound_to_exact_blob_and_repo(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'PREREGISTRATION.json';rp=Path(td)/'publication.json';contract=subject.contract()
            path.write_text(json.dumps(contract))
            receipt={'schema':'bass.git.preregistered.file.v1','repo':subject.REPO,'commit':'a'*40,
                     'path':subject.LANE+'evidence_s7_native/PREREGISTRATION_R2.json','remote_readback':True,
                     'git_blob_sha':subject.blob(path.read_bytes()),'sha256':subject.digest(path.read_bytes())}
            rp.write_text(json.dumps(receipt))
            self.assertEqual(subject.verify_publication(path,contract,rp)['commit'],'a'*40)
            for field,value in [('repo','different/repo'),('remote_readback',False),('git_blob_sha','0'*40),('sha256','0'*64)]:
                broken=copy.deepcopy(receipt);broken[field]=value;rp.write_text(json.dumps(broken))
                with self.assertRaisesRegex(ValueError,'PREREGISTRATION_REMOTE_RECEIPT_IDENTITY'):
                    subject.verify_publication(path,contract,rp)

    def test_missing_completion_and_wrong_grid_fail_before_analysis(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'native.jsonl';p.write_text('')
            with self.assertRaisesRegex(ValueError,'MISSING_COMPLETION'):
                subject.validate(p,subject.contract())
            p.write_text(json.dumps({'schema':'bass.native.cohorts.s7.complete.v1','rows':0})+'\n')
            with self.assertRaisesRegex(ValueError,'COMPLETION_IDENTITY'):
                subject.validate(p,subject.contract())

    def test_nonfinite_native_evidence_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'native.jsonl';p.write_text('{"value":NaN}\n')
            with self.assertRaisesRegex(ValueError,'NATIVE_NONFINITE_JSON'):
                subject.validate(p,subject.contract())

    def test_per_h_normalization_uses_single_redshift_factor(self):
        import math
        r,d=subject.kernels(.0,.23)
        self.assertEqual(float(r),1.)
        self.assertAlmostEqual(float(d),(3*.23**2-1)/2)
        self.assertGreater(subject.source_rate(.8),subject.source_rate(.0))
        # At fixed b, U_per_H scales as a^-1; conversion to physical density
        # supplies the other a^-3. The native stored photon count is constant.
        self.assertAlmostEqual(math.exp(-.8)*math.exp(-3*.8),math.exp(-4*.8))

    def test_birth_ray_frame_cannot_be_relabelled_or_perturbed(self):
        import math
        row=subject.matrix()[11];u=.8*.5/row['cohorts'];b=row['b0']+row['beta']*u
        mu,_=subject.angular_balance.lrs_rule(b,row['n_mu'])
        birth={'u':u,'b':b,'z':21*math.exp(-u)-1,'dt_s':.8/row['cohorts']/1e-16,'mu':mu.tolist()}
        subject.check_birth_geometry(row,birth,0,subject.contract()['gates'])
        changed=copy.deepcopy(birth);changed['mu'][0]-=1e-9;changed['mu'][-1]+=1e-9
        with self.assertRaisesRegex(ValueError,'SOURCE_FRAME_BINDING'):
            subject.check_birth_geometry(row,changed,0,subject.contract()['gates'])
        changed=copy.deepcopy(birth);changed['b']+=.01
        with self.assertRaisesRegex(ValueError,'BIRTH_GEOMETRY_OR_TIME_IDENTITY'):
            subject.check_birth_geometry(row,changed,0,subject.contract()['gates'])

    def test_negative_row_witness_is_bound_to_case_frame_and_birth_index(self):
        row=next(copy.deepcopy(r) for r in subject.matrix() if r['b0']==.9 and r['n_mu']==8 and r['mode']=='P2P4')
        u=.8*.5/row['cohorts'];mu,_=subject.angular_balance.lrs_rule(row['b0']+row['beta']*u,row['n_mu'])
        row.update(failed_birth=0,failed_u=u,support_mu=mu.tolist())
        subject.check_failure_witness(row,subject.contract()['gates'])
        for index in (-1,row['cohorts'],True,.5):
            broken=copy.deepcopy(row);broken['failed_birth']=index
            with self.assertRaisesRegex(ValueError,'FAILURE_BIRTH_INDEX'):
                subject.check_failure_witness(broken,subject.contract()['gates'])
        broken=copy.deepcopy(row);broken['failed_u']+=.01
        with self.assertRaisesRegex(ValueError,'FAILURE_BIRTH_TIME'):
            subject.check_failure_witness(broken,subject.contract()['gates'])
        for substitute in ([-.8,-.6,-.4,-.2,.2,.4,.6,.8],mu[:-1].tolist(),[float('nan')]*len(mu)):
            broken=copy.deepcopy(row);broken['support_mu']=substitute
            with self.assertRaisesRegex(ValueError,'FAILURE_SOURCE_FRAME_BINDING'):
                subject.check_failure_witness(broken,subject.contract()['gates'])

    def test_exact_moment_repairs_known_false_rejection_and_rejects_true_excess(self):
        import math
        from fractions import Fraction
        # Exact recorded binary64 inputs from run01 birth_time_031, birth11.
        # Raw SHA4b544414...db8122; native source published2865f60.
        mu=[-0.9851312050357156,-0.9242773415975377,-0.8241196759764,-0.6963232451454118,
            -0.5516083612913262,-0.39781505174968634,-0.2397760408156852,-0.0800640793093739,
            0.0800640793093739,0.2397760408156852,0.39781505174968634,0.5516083612913262,
            0.6963232451454118,0.8241196759764,0.9242773415975377,0.9851312050357156]
        alpha=[0.01892239275379172,0.04117779506177422,0.05797241375575576,0.0689151563790352,
               0.07514664169502536,0.07825098505648646,0.07958174739349028,0.08003286790464104,
               0.08003286790464104,0.07958174739349028,0.07825098505648646,0.07514664169502536,
               0.0689151563790352,0.05797241375575576,0.04117779506177422,0.01892239275379172]
        rounded=math.fsum(a*(3*(m*m)-1)/2 for a,m in zip(alpha,mu))
        norm,m2,_=subject.exact_moments(mu,alpha);gate=Fraction(3,10**15)
        self.assertGreater(abs(rounded),3e-15)
        self.assertLess(abs(m2),gate)
        self.assertEqual(float(m2),-2.9993863364154428e-15)
        self.assertNotEqual(norm,Fraction(1))  # The gate did not renormalize.
        changed=alpha.copy()
        for j in (0,15):changed[j]+=1e-14
        for j in (7,8):changed[j]-=1e-14
        _,bad,_=subject.exact_moments(mu,changed)
        self.assertGreater(abs(bad),gate)

    def test_reanalysis_refuses_substituted_native_output(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td);(path/'NATIVE_COHORTS.jsonl').write_text('unrelated output\n')
            with self.assertRaisesRegex(ValueError,'REUSE_ARTIFACT_IDENTITY'):
                subject.verify_existing_run(path,subject.contract())

    def test_plain_and_gzip_raw_content_identity_and_corruption(self):
        import gzip
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'NATIVE_COHORTS.jsonl';raw=b'{"schema":"test","value":0.125}\n'
            packed=gzip.compress(raw,mtime=0);path.write_bytes(raw)
            compressed=path.with_name(path.name+'.gz');compressed.write_bytes(packed)
            meta={'schema':'bass.lossless.raw_storage.v1','gzip_sha256':subject.digest(packed),
                  'raw_sha256':subject.digest(raw),'raw_bytes':len(raw)}
            mp=path.parent/'RAW_STORAGE.json';mp.write_text(json.dumps(meta))
            self.assertEqual(subject.read_native_raw(path),raw)
            path.unlink()
            self.assertEqual(subject.read_native_raw(path),raw)
            self.assertEqual(subject.read_native_raw(compressed),raw)
            meta['raw_sha256']='0'*64;mp.write_text(json.dumps(meta))
            with self.assertRaisesRegex(ValueError,'RAW_STORAGE_CONTENT_IDENTITY'):
                subject.read_native_raw(path)
            meta['gzip_sha256']='0'*64;mp.write_text(json.dumps(meta))
            with self.assertRaisesRegex(ValueError,'RAW_STORAGE_IDENTITY'):
                subject.read_native_raw(path)


if __name__=='__main__':unittest.main(verbosity=2)
