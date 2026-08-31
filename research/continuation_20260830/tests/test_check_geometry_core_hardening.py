from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch


REPO = Path(__file__).resolve().parents[3]
SCRIPT = REPO / "research/continuation_20260830/check_geometry_core.py"
SPEC = spec_from_file_location("check_geometry_core", SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("failed to load check_geometry_core validator")
CHECK = module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class GeometryValidatorHardeningTests(unittest.TestCase):
    def test_internal_git_show_disables_replacement_objects(self) -> None:
        with patch.object(CHECK.subprocess, "check_output", return_value=b"baseline") as call:
            self.assertEqual(CHECK.read_baseline(REPO), b"baseline")
        call.assert_called_once_with(
            ["git", "--no-replace-objects", "show", f"{CHECK.BASE}:{CHECK.REL}"],
            cwd=REPO,
        )

    def test_historical_old_donor_cannot_masquerade_as_candidate(self) -> None:
        old = subprocess.check_output(
            [
                "git",
                "--no-replace-objects",
                "show",
                f"{CHECK.BASE}:{CHECK.REL}",
            ],
            cwd=REPO,
        )
        self.assertEqual(CHECK.blob(old), CHECK.OLD)
        with self.assertRaisesRegex(ValueError, "candidate expected=.*observed"):
            CHECK.require_source_identities(old, old)

    def test_explicit_identity_gate_rejects_arbitrary_bytes(self) -> None:
        with self.assertRaisesRegex(ValueError, "immutable numerical input mismatch"):
            CHECK.require_source_identities(b"not the baseline", b"not the candidate")


if __name__ == "__main__":
    unittest.main()
