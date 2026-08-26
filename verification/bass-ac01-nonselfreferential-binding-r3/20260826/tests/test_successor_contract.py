from __future__ import annotations
import json, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

class SuccessorContractTests(unittest.TestCase):
    def setUp(self):
        self.c=json.loads((ROOT/'WU-004-R3-NONSELFREFERENTIAL-BINDING.json').read_text())
        self.pre=json.loads((ROOT/'PRECOMMIT_RECEIPT.schema.json').read_text())
        self.post=json.loads((ROOT/'POST_PUSH_BINDING.schema.json').read_text())
    def test_precommit_receipt_forbids_self_sha(self):
        forbidden=[set(x['required']) for x in self.pre['not']['anyOf']]
        self.assertIn({'final_sha'},forbidden)
    def test_post_push_binding_owns_subject_sha(self):
        self.assertIn('subject_sha',self.post['required'])
        self.assertEqual(self.c['receipt_policy']['review_target_field'],'post_push_binding.subject_sha')
    def test_one_implementation_commit_preserved(self):
        self.assertEqual(self.c['commit_policy']['implementation']['count_from_base'],1)
    def test_attestation_is_separate_one_file_commit(self):
        self.assertEqual(self.c['commit_policy']['attestation']['changed_paths'],['verification/bass-ac-01/20260826/POST_PUSH_BINDING.json'])
    def test_science_boundaries_unchanged(self):
        text=' '.join(self.c['objective']['non_goals']+self.c['scope']['forbidden_changes'])
        for token in ['runtime','Rust','solver','authority']:
            self.assertIn(token,text)

if __name__=='__main__': unittest.main()
