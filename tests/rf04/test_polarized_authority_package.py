from __future__ import annotations

import hashlib
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
PROBE_ROOT = REPO_ROOT / "artifacts/rust_first_runtime/rf04/polarized_source_probe"
IMPORT_RECEIPT = (
    REPO_ROOT
    / "artifacts/rust_first_runtime/rf04/polarized_authority/EVIDENCE_IMPORT.json"
)
EXPECTED_SOURCE_HEAD = "50b6e9f7a6741b7fd25b0421d2a674b9eb92cdda"
EXPECTED_SOURCE_TREE = "b32fcc26ca51dcaca9e9225d48b03fe9e02988ed"
EXPECTED_MANIFEST_SHA256 = (
    "c05a78d373f3fd87c028e8535404c2b4723aff56c533163d3822355cf3987ea1"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _manifest_entries(path: Path) -> dict[str, str]:
    entries: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        digest, relative_path = line.split(maxsplit=1)
        normalized = relative_path.removeprefix("./")
        assert normalized not in entries
        entries[normalized] = digest
    return entries


def test_imported_source_probe_bytes_and_receipt_are_exact() -> None:
    """Catches normalized, incomplete, reconstructed, or rerun probe evidence."""

    assert PROBE_ROOT.is_dir(), "source-probe evidence was not imported"
    manifest = PROBE_ROOT / "MANIFEST.sha256"
    assert _sha256(manifest) == EXPECTED_MANIFEST_SHA256

    entries = _manifest_entries(manifest)
    actual_files = {
        str(path.relative_to(PROBE_ROOT))
        for path in PROBE_ROOT.rglob("*")
        if path.is_file()
    }
    assert actual_files == set(entries) | {"MANIFEST.sha256"}
    for relative_path, expected_digest in entries.items():
        assert _sha256(PROBE_ROOT / relative_path) == expected_digest

    receipt = json.loads(IMPORT_RECEIPT.read_text(encoding="utf-8"))
    assert receipt["classification"] == "USER_LOCAL_EXECUTION_IMPORTED_NOT_RERUN"
    assert receipt["source_head"] == EXPECTED_SOURCE_HEAD
    assert receipt["source_tree"] == EXPECTED_SOURCE_TREE
    assert receipt["source_probe_manifest_sha256"] == EXPECTED_MANIFEST_SHA256
    assert receipt["imported_paths"] == sorted(actual_files)
    assert receipt["p1_to_p5_rerun"] is False

    rejection = json.loads(
        (PROBE_ROOT / "local_router/REJECTION.json").read_text(encoding="utf-8")
    )
    assert rejection["authority"] == "EXPLORATORY_NONAUTHORITATIVE"
    assert rejection["adoption"] == "REJECTED"
