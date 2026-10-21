"""S8 changed input/publication/frame/old-block guards; no scientific campaign."""
import copy
import json
import math
import os
from pathlib import Path
import struct
import tempfile
import unittest
import run_s8_native_refinement as subject


def old_row(raw=None):
    raw=subject.old_input_bytes() if raw is None else raw
    words=struct.unpack('<'+'Q'*(4*3072),raw)
    sparse=[]
    for k in range(3072):
        values=[words[j*3072+k] for j in range(4)]
        if any(values):sparse.append([k]+[f'{v:016x}' for v in values])
    h=0xcbf29ce484222325
    for b in raw:h=((h^b)*0x100000001b3)&((1<<64)-1)
    return {'old_n_mu':32,'old_cell_count':3072,'old_sparse_before':sparse,'old_sparse_after':copy.deepcopy(sparse),
            'old_digest_before_fnv1a64':f'{h:016x}','old_digest_after_fnv1a64':f'{h:016x}'}


class S8NativeGuards(unittest.TestCase):
    def test_matrix_only_new_orders_and_fixed_spectral_birth_axes(self):
        rows=subject.matrix()
        self.assertEqual(len(rows),18);self.assertEqual(len({r['case_id'] for r in rows}),18)
        self.assertEqual({r['n_mu'] for r in rows},{64,128,256})
        self.assertEqual({r['b0'] for r in rows},{.6,.9})
        self.assertTrue(all((r['n_energy'],r['cells_per_segment'],r['cohorts'],r['beta'],r['x_observe'])==(96,32,16,.2,1.) for r in rows))

    def test_original_baseline_is_reused_by_identity_with_two_failures(self):
        rows,analysis=subject.load_baseline()
        self.assertEqual(len(rows),6)
        self.assertEqual(sum(r['status']=='FEASIBILITY_FAILURE' for r in rows),2)
        m=next(r for r in analysis['metrics'] if r['case_id']=='angular_017')
        self.assertEqual(m['angular_a_error'],-0.0009945297565870925)

    def test_gate_hash_key_internal_margin_and_matrix_tampering_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'PREREGISTRATION.json'
            for field in ('gate','key','margin','matrix','workers'):
                c=subject.contract()
                if field=='gate':c['gates']['moment_absolute']=4e-15
                elif field=='key':del c['pinned_sha256']['native_adapter.rs']
                elif field=='margin':c['reuse_from']['new_orders_internal_moment_tolerance']=3e-15
                elif field=='matrix':c['matrix'][0]['n_mu']=32
                else:c['limits']['additional_workers_max']=16
                p.write_text(json.dumps(c))
                with self.assertRaisesRegex(ValueError,'PREREGISTRATION_CONTRACT_CHANGED'):subject.verify_publication(p,c)

    def test_publication_receipt_binds_exact_repo_path_and_bytes(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'PREREGISTRATION.json';rp=Path(td)/'receipt.json';c=subject.contract();p.write_text(json.dumps(c))
            r={'schema':'bass.git.preregistered.file.v1','repo':subject.REPO,'commit':'a'*40,'path':subject.LANE+subject.PREREG_REL,
               'remote_readback':True,'git_blob_sha':subject.blob(p.read_bytes()),'sha256':subject.digest(p.read_bytes())}
            rp.write_text(json.dumps(r));self.assertEqual(subject.verify_publication(p,c,rp)['commit'],'a'*40)
            for field,value in (('repo','wrong/repo'),('path',subject.LANE+'evidence_s7_native/PREREGISTRATION_R2.json'),('sha256','0'*64),('remote_readback',False)):
                broken={**r,field:value};rp.write_text(json.dumps(broken))
                with self.assertRaisesRegex(ValueError,'PUBLICATION_RECEIPT_IDENTITY'):subject.verify_publication(p,c,rp)

    def test_blas_budget_is_explicit_before_numpy(self):
        self.assertTrue(all(os.environ[k]=='1' for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS')))

    def test_reference_support_rejects_nonpositive_weights_and_relabelled_node(self):
        n=64;nu,q=subject.gl(n);row={'n_mu':n,'reference_nu':nu.tolist(),'reference_count_fraction':q.tolist()}
        g=subject.contract()['gates'];subject.reference_rule(row,g)
        for key in ('reference_nu','reference_count_fraction'):
            broken=copy.deepcopy(row);broken[key][0]=-.01 if key=='reference_count_fraction' else -.8
            with self.assertRaisesRegex(ValueError,'REFERENCE_GL_SUPPORT_IDENTITY'):subject.reference_rule(broken,g)

    def test_birth_geometry_has_one_jacobian_and_binds_actual_reference_rule(self):
        row={'b0':.4,'n_mu':64};nu,q=subject.gl(64);u=.8*.5/16;b=row['b0']+.2*u
        mu,prior=subject.birth_rule(nu,q,b)
        birth={'u':u,'b':b,'z':21*math.exp(-u)-1,'dt_s':.8/16/1e-16,'mu':mu.tolist(),'prior':prior.tolist()}
        g=subject.contract()['gates'];subject.check_birth_frame(row,birth,0,nu,q,g)
        wrong=copy.deepcopy(birth);wrong['mu'][0]+=1e-9
        with self.assertRaisesRegex(ValueError,'BIRTH_SOURCE_FRAME_IDENTITY'):subject.check_birth_frame(row,wrong,0,nu,q,g)
        wrong=copy.deepcopy(birth);wrong['prior']=(prior*prior/math.fsum(prior*prior)).tolist()
        with self.assertRaisesRegex(ValueError,'BIRTH_PRIOR_JACOBIAN_IDENTITY'):subject.check_birth_frame(row,wrong,0,nu,q,g)

    def test_failure_witness_cannot_change_birth_or_source_frame(self):
        row={'b0':.4,'n_mu':64,'mode':'P2P4','status':'NUMERICAL_FAILURE','failure':'MOMENT_NOT_CONVERGED','failed_birth':0,'failed_u':.025}
        nu,q=subject.gl(64);row['support_mu']=subject.birth_rule(nu,q,.405)[0].tolist();g=subject.contract()['gates']
        subject.check_failure(row,nu,q,g)
        wrong=copy.deepcopy(row);wrong['failed_birth']=True
        with self.assertRaisesRegex(ValueError,'FAILURE_BIRTH_INDEX'):subject.check_failure(wrong,nu,q,g)
        wrong=copy.deepcopy(row);wrong['support_mu'][0]+=.01
        with self.assertRaisesRegex(ValueError,'FAILURE_SOURCE_FRAME_IDENTITY'):subject.check_failure(wrong,nu,q,g)

    def test_old_state_binds_input_and_before_after_bits(self):
        row=old_row();self.assertEqual(subject.old_state_identity(row),subject.digest(subject.old_input_bytes()))
        wrong=copy.deepcopy(row);wrong['old_sparse_after'][0][1]='0000000000000000'
        with self.assertRaisesRegex(ValueError,'OLD_BLOCK_DIGEST_IDENTITY'):subject.old_state_identity(wrong)
        raw=bytearray(subject.old_input_bytes());raw[0:8]=struct.pack('<d',.0001)
        substituted=old_row(bytes(raw))
        with self.assertRaisesRegex(ValueError,'OLD_BLOCK_INPUT_CHANGED'):subject.old_state_identity(substituted)

    def test_nonfinite_and_incomplete_raw_cannot_be_accepted(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'raw.jsonl';c=subject.contract()
            p.write_text('{"x":NaN}\n')
            with self.assertRaisesRegex(ValueError,'NATIVE_NONFINITE_JSON'):subject.validate(p,c,[])
            p.write_text('{"x":1e309}\n')
            with self.assertRaisesRegex(ValueError,'NATIVE_NONFINITE_VALUE'):subject.validate(p,c,[])
            p.write_text('')
            with self.assertRaisesRegex(ValueError,'MISSING_NATIVE_COMPLETION'):subject.validate(p,c,[])

    def test_verified_finest_support_absence_is_not_an_integrity_error(self):
        absent={'case_id':'example','gate':'FINEST_ORDER_UNAVAILABLE'}
        self.assertEqual(subject.decision_flags([absent]),{'integrity_gates_pass':True,'finest_accuracy_targets_pass':False})
        solver={'case_id':'example','gate':'PROJECTION_NUMERICAL_FAILURE'}
        self.assertEqual(subject.decision_flags([absent,solver]),{'integrity_gates_pass':False,'finest_accuracy_targets_pass':False})
        moment={'case_id':'example','gate':'EXACT_BIRTH_MOMENTS'}
        self.assertFalse(subject.decision_flags([moment])['integrity_gates_pass'])


if __name__=='__main__':unittest.main()
