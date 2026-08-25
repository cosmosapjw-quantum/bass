from __future__ import annotations
import json, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

class CompiledPlanTests(unittest.TestCase):
    def test_package_verifier_passes(self):
        p=subprocess.run([sys.executable,str(ROOT/'scripts/verify_compiled_plan.py'),str(ROOT)],capture_output=True,text=True)
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertIn('BASS_AUDIT_COMPILED_PLAN_VERIFY_PASS',p.stdout)

    def test_every_p0_p1_has_mechanical_detector(self):
        for line in (ROOT/'P0_P1_THREAT_CATALOGUE.jsonl').read_text().splitlines():
            if not line.strip(): continue
            obj=json.loads(line)
            self.assertIn(obj['detection']['type'],{'test','command','stop_gate'})

    def test_contract_is_exact_base_and_read_only_review(self):
        c=json.loads((ROOT/'PR_CONTRACTS/BASS-AC-01.json').read_text())
        r=json.loads((ROOT/'FRESH_CONTEXT_REVIEW_CONTRACT.json').read_text())
        self.assertRegex(c['base_sha'],r'^[0-9a-f]{40}$')
        self.assertTrue(r['fresh_context_required'])
        self.assertFalse(r['reviewer_may_modify'])
        self.assertEqual(r['pass_condition']['P0'],0)
        self.assertEqual(r['pass_condition']['P1'],0)

    def test_handoff_contract_bootstrap_is_self_consistent(self):
        c=json.loads((ROOT/'PR_CONTRACTS/BASS-AC-01.json').read_text())
        allowed=set(c['scope']['allowed_paths'])
        self.assertIn('verification/audit-compiled/ACTIVE_PR_CONTRACT.json', allowed)
        for item in c['verification']['negative']:
            self.assertNotIn('tests/fixtures/', item['command'])
            self.assertIn('python -m unittest', item['command'])
        h=(ROOT/'CODEX_HANDOFF.md').read_text()
        self.assertIn('two', h.lower())
        self.assertIn('bass-ac01-plan', h)
        self.assertIn('bass-ac01-impl', h)
        self.assertIn('e7837c0ecd92793c19ecc53c5559fd9f67cd4884a393eaf4c323fbbbebe46cca', h)

if __name__=='__main__': unittest.main()
