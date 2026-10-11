"""Identity-only link of existing scoped receiver evidence; no solver/reference import."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
UPSTREAM = REPO / "research/rei_pr104_cells_20261010"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def function_text(text, name):
    start = text.index("pub fn " + name + "(")
    opening = text.index("{", start)
    depth = 1
    end = opening + 1
    while depth:
        depth += (text[end] == "{") - (text[end] == "}")
        end += 1
    return text[start:end]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--restored-root", type=Path, required=True)
    args = parser.parse_args()
    contract = json.loads((ROOT / "CONTRACT.json").read_text())
    previous = json.loads((UPSTREAM / "CONTRACT.json").read_text())
    valid = json.loads((UPSTREAM / "evidence/binary64_v2/VALIDATION.json").read_text())
    review = json.loads((UPSTREAM / "evidence/binary64_v2/INDEPENDENT_REVIEW.json").read_text())
    result = {
        "kind": "EVIDENCE_IDENTITY_ONLY",
        "scientific_revalidation": False,
        "new_solver_calls": 0,
        "new_receiver_calls": 0,
        "contract_sha256": digest((ROOT / "CONTRACT.json").read_bytes()),
        "producer_files": [],
        "native_source": [],
        "receiver_stdout": [],
        "upstream_decision": review["verdict"],
        "upstream_scope": review["claim_ceiling"],
    }
    producer = args.restored_root / "research/broad_history_20261010"
    for name, expected in previous["members"].items():
        data = (producer / name).read_bytes()
        actual = digest(data)
        assert actual == expected, (name, actual, expected)
        result["producer_files"].append({"path": name, "sha256": actual, "bytes": len(data), "matches_upstream": True})
    source = REPO / "_rustcore/examples/rei_pr104_cell_receiver.rs"
    assert digest(source.read_bytes()) == valid["receiver_source_sha256"]
    result["receiver_source_sha256"] = digest(source.read_bytes())
    for file, names in (
        ("_rustcore/src/microphysics/visibility.rs", ("integrate_visibility",)),
        ("_rustcore/src/microphysics/axisym_observables.rs", ("fixed_time_optical_depth", "with_observer_tail")),
    ):
        old = subprocess.check_output(["git", "show", contract["source_receiver_commit"] + ":" + file], cwd=REPO, text=True)
        new = (REPO / file).read_text()
        for name in names:
            a, b = function_text(old, name), function_text(new, name)
            assert a == b, (file, name)
            result["native_source"].append({"file": file, "function": name, "function_sha256": digest(b.encode()), "byte_identical_to_executed_ancestor": True})
    for case, filename in (("flrw", "evidence/repair/flrw.stdout.log"), ("rp01", "evidence/binary64_v2/rp01.stdout.log")):
        data = (UPSTREAM / filename).read_bytes()
        assert digest(data) == valid["cases"][case]["stdout_sha256"]
        assert valid["cases"][case]["validation"]["status"] == "PASS_SCOPED"
        result["receiver_stdout"].append({"case": case, "path": filename, "sha256": digest(data), "bytes": len(data), "execution": "UPSTREAM_REUSED_NO_RERUN"})
    assert valid["status"] == review["verdict"] == "PASS_SCOPED"
    result["evidence_files"] = []
    for filename in ("CONTRACT.json", "CONTRACT_V2.json", "evidence/binary64_v2/VALIDATION.json", "evidence/binary64_v2/INDEPENDENT_REVIEW.json", "evidence/binary64_v2/EXECUTION.json", "evidence/binary64_v2/CAMPAIGN_RECEIPT.json"):
        data = (UPSTREAM / filename).read_bytes()
        result["evidence_files"].append({"path": str((UPSTREAM / filename).relative_to(REPO)), "sha256": digest(data), "bytes": len(data)})
    result["status"] = "IDENTITY_LINK_VERIFIED"
    out = ROOT / "evidence/EVIDENCE_IDENTITY.json"
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "producer_files": len(result["producer_files"]), "native_functions": len(result["native_source"]), "stdout_files": len(result["receiver_stdout"]), "new_science_execution": False}))


if __name__ == "__main__":
    main()
