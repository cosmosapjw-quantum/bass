from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "run_bg02_einstein_projection_red_local.sh"


class BG02RedWrapperAncestryTests(unittest.TestCase):
    def test_descendant_red_commit_uses_scientific_parent_ancestry(self) -> None:
        source = RUNNER.read_text(encoding="utf-8")
        new_gate = (
            'if [ "$PARENT_ANCESTRY_PASS" = true ] \\\n'
            '   && [ "$RAW_RC" -eq 1 ]'
        )
        old_gate = (
            'if [ "$HEAD" = "$EXPECTED_HEAD" ] \\\n'
            '   && [ "$RAW_RC" -eq 1 ]'
        )
        self.assertIn(
            new_gate,
            source,
            "RED wrapper must accept a committed test overlay descended from PR #91",
        )
        self.assertNotIn(
            old_gate,
            source,
            "RED execution HEAD cannot equal its scientific parent after committing tests",
        )
        self.assertIn(
            '"expected_red_identity_policy": '
            '"SCIENTIFIC_PARENT_IS_ANCESTOR"',
            source,
        )


if __name__ == "__main__":
    unittest.main()
