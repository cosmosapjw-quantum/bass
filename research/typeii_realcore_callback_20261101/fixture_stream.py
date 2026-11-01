#!/usr/bin/env python3
"""Read ONLY the original byte-locked 401-row Type II fixture and stream its states/RHS."""
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "compiler/validation/typeii_fixture_canonical.json"
EXPECTED = {
    "compiler/validation/typeii_fixture_canonical.json": "dea22f0fce116b61314b13cea7d0bdd38efe48bc",
    "generated/rust/typeii/typeii_background.rs": "3616990750099e0088a180ce8612ddbf597e9414",
    "_rustcore/src/geom/group.rs": "3a500f20367f939807b3b06f240a8bf771858206",
    "_rustcore/src/core/conventions.rs": "9ad463c1bb617a9fd41288c4d6dcad03a07e3cf4",
}
for name, expected in EXPECTED.items():
    actual = subprocess.check_output(["git", "-C", str(ROOT), "hash-object", name], text=True).strip()
    if actual != expected:
        raise RuntimeError(f"Immutable source mismatch: {name}: {actual} != {expected}")

records = json.loads(FIXTURE.read_bytes())["trajectory"]
samples = records["samples"]
if len(samples) != 401 or records["contract"]["gamma"] != 1.3:
    raise RuntimeError("Canonical fixture count/gamma mismatch")
for i, row in enumerate(samples):
    if row["index"] != i or len(row["state"]) != 5 or len(row["rhs"]) != 5:
        raise RuntimeError(f"Malformed source fixture at index {i}")
    print(",".join(format(float(a), ".17g") for a in (row["state"] + row["rhs"])))
