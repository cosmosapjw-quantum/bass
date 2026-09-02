from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "trirepo_formula_inventory.py"
FIXTURE = ROOT / "fixtures" / "trirepo_formula_inventory_minimal.json"


class InventoryContractRedTest(unittest.TestCase):
    def test_cli_validates_minimal_inventory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "inventory.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--input",
                    str(FIXTURE),
                    "--output",
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            document = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(document["status"], "PASS_BOUNDED_PATH_INVENTORY")


if __name__ == "__main__":
    unittest.main()
