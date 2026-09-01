from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "trirepo_sync_audit.py"
PROGRAM = "BIANCHI-WOLFRAM-TRIREPO-20260830"
CONVENTION = "c" * 64


def load_auditor(testcase: unittest.TestCase):
    testcase.assertTrue(SCRIPT.exists(), f"missing production module: {SCRIPT}")
    spec = importlib.util.spec_from_file_location("trirepo_sync_audit", SCRIPT)
    testcase.assertIsNotNone(spec)
    testcase.assertIsNotNone(spec.loader)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def export_doc(repository: str, formula_id: str, semantic_hash: str, owner: str | None = None) -> dict:
    return {
        "schema_version": "2.0.0",
        "program_id": PROGRAM,
        "repository": repository,
        "source_binding": {
            "mode": "BOUND_BY_SYNC_POINTER",
            "pointer_path": "docs/bianchi_program/TRIREPO_SYNC_POINTER.json",
        },
        "exports": [{
            "formula_id": formula_id,
            "owner": owner or repository,
            "authority_kind": "formula",
            "domain": "test",
            "authority_effect": "AUTHORITATIVE_DERIVATION",
            "status": "DECLARED",
            "semantic_hash": semantic_hash,
            "convention_hash": CONVENTION,
            "source_paths": ["docs/bianchi_program/example.json"],
            "consumers": sorted({"bass", "rec_bianchi", "rei_bianchi"} - {repository}),
            "allowed_consumer_modes": ["PINNED_IMPORT", "INDEPENDENT_ORACLE", "ADAPTER_SPECIALIZATION"],
            "claim_boundary": "TEST_ONLY",
        }],
    }


def lock_doc(repository: str, imports: list[dict] | None = None, claims: list[dict] | None = None) -> dict:
    return {
        "schema_version": "2.0.0",
        "program_id": PROGRAM,
        "repository": repository,
        "imports": imports or [],
        "local_formula_claims": claims or [],
    }


def imported(formula_id: str, producer: str, semantic_hash: str) -> dict:
    return {
        "formula_id": formula_id,
        "producer_repository": producer,
        "producer_commit": "1" * 40,
        "producer_tree": "2" * 40,
        "semantic_hash": semantic_hash,
        "convention_hash": CONVENTION,
        "use": "test consumer",
        "local_mode": "PINNED_IMPORT",
    }


def clean_inputs():
    return (
        [
            export_doc("bass", "BASS.GEO.001", "a" * 64),
            export_doc("rec_bianchi", "REC.HISTORY.001", "b" * 64),
            export_doc("rei_bianchi", "REI.HISTORY.001", "d" * 64),
        ],
        [lock_doc("bass"), lock_doc("rec_bianchi"), lock_doc("rei_bianchi")],
    )


class CanonicalIdentityTests(unittest.TestCase):
    def test_hash_is_key_order_invariant(self) -> None:
        auditor = load_auditor(self)
        self.assertEqual(
            auditor.sha256_json({"b": 2, "a": {"y": 2, "x": 1}}),
            auditor.sha256_json({"a": {"x": 1, "y": 2}, "b": 2}),
        )

    def test_sync_id_changes_when_binding_changes(self) -> None:
        auditor = load_auditor(self)
        payload = {
            "program_id": PROGRAM,
            "dag_version": "2.0.0",
            "repo_bindings": auditor.example_repo_bindings(),
            "document_digests": {"bass": "a" * 64},
            "convention_hashes": [CONVENTION],
            "approved_edges": auditor.DEFAULT_APPROVED_EDGES,
        }
        moved = json.loads(json.dumps(payload))
        moved["repo_bindings"]["bass"]["commit"] = "9" * 40
        self.assertNotEqual(auditor.compute_sync_run_id(payload), auditor.compute_sync_run_id(moved))


class AuthorityTests(unittest.TestCase):
    def test_duplicate_formula_owner_fails_closed(self) -> None:
        auditor = load_auditor(self)
        exports, locks = clean_inputs()
        exports[1] = export_doc("rec_bianchi", "BASS.GEO.001", "a" * 64, owner="rec_bianchi")
        result = auditor.audit_documents(exports, locks, auditor.example_repo_bindings(), auditor.DEFAULT_APPROVED_EDGES, {})
        self.assertEqual(result["sync_state"]["status"], "DRIFT_DETECTED")
        self.assertIn("BASS.GEO.001", result["duplicate_report"]["duplicate_owner_formula_ids"])

    def test_authorized_oracle_is_not_duplicate_authority(self) -> None:
        auditor = load_auditor(self)
        exports, locks = clean_inputs()
        locks[1]["local_formula_claims"] = [{
            "local_formula_id": "REC.ORACLE.GEO.001",
            "semantic_hash": "a" * 64,
            "authority_effect": "NONE",
            "replay_of": "BASS.GEO.001",
            "independence_class": "COMPONENT_ORACLE",
        }]
        result = auditor.audit_documents(exports, locks, auditor.example_repo_bindings(), auditor.DEFAULT_APPROVED_EDGES, {})
        self.assertEqual(result["duplicate_report"]["unauthorized_local_claims"], [])
        self.assertEqual(len(result["duplicate_report"]["allowed_replays"]), 1)

    def test_unbound_same_semantics_is_duplicate_path(self) -> None:
        auditor = load_auditor(self)
        exports, locks = clean_inputs()
        locks[1]["local_formula_claims"] = [{
            "local_formula_id": "REC.UNBOUND.GEO.001",
            "semantic_hash": "a" * 64,
            "authority_effect": "AUTHORITATIVE_DERIVATION",
        }]
        result = auditor.audit_documents(exports, locks, auditor.example_repo_bindings(), auditor.DEFAULT_APPROVED_EDGES, {})
        finding = result["duplicate_report"]["unauthorized_local_claims"][0]
        self.assertEqual(finding["classification"], "DUPLICATE_DERIVATION_PATH")

    def test_stale_import_is_detected(self) -> None:
        auditor = load_auditor(self)
        exports, locks = clean_inputs()
        locks[1]["imports"] = [imported("BASS.GEO.001", "bass", "9" * 64)]
        result = auditor.audit_documents(exports, locks, auditor.example_repo_bindings(), auditor.DEFAULT_APPROVED_EDGES, {})
        self.assertIn("STALE_UPSTREAM", {item["code"] for item in result["sync_state"]["findings"]})

    def test_missing_import_is_detected(self) -> None:
        auditor = load_auditor(self)
        exports, locks = clean_inputs()
        locks[1]["imports"] = [imported("MISSING.001", "bass", "a" * 64)]
        result = auditor.audit_documents(exports, locks, auditor.example_repo_bindings(), auditor.DEFAULT_APPROVED_EDGES, {})
        self.assertIn("MISSING_IMPORT_FORMULA", {item["code"] for item in result["sync_state"]["findings"]})


class DagAndOutputTests(unittest.TestCase):
    def test_bootstrap_never_mutates_official_edges(self) -> None:
        auditor = load_auditor(self)
        exports, locks = clean_inputs()
        result = auditor.audit_documents(exports, locks, auditor.example_repo_bindings(), auditor.DEFAULT_APPROVED_EDGES, {})
        proposal = result["dag_proposal"]
        self.assertEqual(proposal["proposal_status"], "PROPOSAL_ONLY_NO_DAG_MUTATION")
        self.assertEqual(proposal["proposed_official_edge_mutations"], [])
        self.assertEqual(proposal["approved_edges"], auditor.DEFAULT_APPROVED_EDGES)

    def test_write_outputs_emits_five_contracts(self) -> None:
        auditor = load_auditor(self)
        exports, locks = clean_inputs()
        result = auditor.audit_documents(exports, locks, auditor.example_repo_bindings(), auditor.DEFAULT_APPROVED_EDGES, {})
        with tempfile.TemporaryDirectory() as tmp:
            paths = auditor.write_outputs(result, Path(tmp))
            self.assertEqual(
                {path.name for path in paths},
                {
                    "TRIREPO_AUTHORITY_REGISTRY.json",
                    "TRIREPO_SYNC_STATE.json",
                    "TRIREPO_DUPLICATE_REPORT.json",
                    "TRIREPO_DAG_PROPOSAL.json",
                    "TRIREPO_SYNC_RECEIPT.json",
                },
            )
            for path in paths:
                self.assertEqual(json.loads(path.read_text(encoding="utf-8"))["sync_run_id"], result["sync_run_id"])


if __name__ == "__main__":
    unittest.main()
