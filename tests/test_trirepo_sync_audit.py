from __future__ import annotations

import copy
import unittest

from scripts.trirepo_sync_audit import (
    PROGRAM_ID,
    audit_documents,
    canonical_json,
    sha256_json,
    validate_export,
    validate_import_lock,
)

RUN_ID = "72fa2eabd32ab5d6ce2cbdb7633375d71ebce93c543ab562162d6853bd54e69f"
CONVENTION_HASH = "e12258405c1c2ec296839524f5169e03441715b3acaaff1cef9de28bfa490a70"
SEMANTIC_HASH = "1" * 64
COMMIT = "2" * 40
TREE = "3" * 40


def export_document(repository: str, records: list[dict]) -> dict:
    return {
        "schema_version": "2.0.0",
        "program_id": PROGRAM_ID,
        "change_id": "TEST",
        "sync_run_id": RUN_ID,
        "repository": repository,
        "policy_base": {"branch": "policy/test", "commit": COMMIT, "tree": TREE},
        "exports": records,
        "claim_boundary": "TEST_ONLY",
    }


def authority_record(
    formula_id: str = "BASS.TEST.001",
    owner: str = "bass",
    mode: str = "AUTHORITATIVE_DERIVATION",
    semantic_hash: str | None = SEMANTIC_HASH,
    status: str = "SYMBOLIC_VERIFIED_DRAFT",
) -> dict:
    return {
        "formula_id": formula_id,
        "owner": owner,
        "authority_mode": mode,
        "producer_ref": "branch/test",
        "producer_commit": COMMIT,
        "source_path": "formula.wl",
        "semantic_hash": semantic_hash,
        "convention_hash": CONVENTION_HASH,
        "status": status,
        "consumers": ["rec_bianchi"],
        "allowed_consumer_modes": ["PINNED_IMPORT", "INDEPENDENT_ORACLE"],
        "dependencies": [],
    }


def import_document(
    repository: str = "rec_bianchi",
    formula_id: str = "BASS.TEST.001",
    producer_repository: str = "bass",
    producer_commit: str | None = COMMIT,
    semantic_hash: str | None = SEMANTIC_HASH,
    status: str = "PINNED",
) -> dict:
    return {
        "schema_version": "2.0.0",
        "program_id": PROGRAM_ID,
        "change_id": "TEST",
        "sync_run_id": RUN_ID,
        "repository": repository,
        "imports": [
            {
                "formula_id": formula_id,
                "producer_repository": producer_repository,
                "producer_ref": "branch/test" if producer_commit else None,
                "producer_commit": producer_commit,
                "semantic_hash": semantic_hash,
                "convention_hash": CONVENTION_HASH if semantic_hash else None,
                "local_mode": "PINNED_IMPORT",
                "use": "test import",
                "status": status,
                "required_claim_level": "SYMBOLIC_VERIFIED",
            }
        ],
        "no_silent_fallback": True,
        "claim_boundary": "TEST_ONLY",
    }


class CanonicalIdentityTests(unittest.TestCase):
    def test_key_order_does_not_change_hash(self) -> None:
        left = {"b": 2, "a": 1}
        right = {"a": 1, "b": 2}
        self.assertEqual(canonical_json(left), canonical_json(right))
        self.assertEqual(sha256_json(left), sha256_json(right))


class ContractValidationTests(unittest.TestCase):
    def test_valid_documents(self) -> None:
        validate_export(export_document("bass", [authority_record()]))
        validate_import_lock(import_document())

    def test_silent_fallback_is_rejected(self) -> None:
        document = import_document()
        document["no_silent_fallback"] = False
        with self.assertRaises(ValueError):
            validate_import_lock(document)


class AuditTests(unittest.TestCase):
    def test_exact_pin_is_in_sync(self) -> None:
        result = audit_documents(
            [export_document("bass", [authority_record()])],
            [import_document()],
            RUN_ID,
        )
        self.assertEqual(result["classification"], "PASS_IN_SYNC")
        self.assertEqual(result["structural_findings"], [])
        self.assertEqual(result["dependency_findings"], [])

    def test_duplicate_formula_authority_fails(self) -> None:
        second = authority_record(owner="rec_bianchi")
        result = audit_documents(
            [
                export_document("bass", [authority_record()]),
                export_document("rec_bianchi", [second]),
            ],
            [],
            RUN_ID,
        )
        codes = {finding["code"] for finding in result["structural_findings"]}
        self.assertIn("DUPLICATE_AUTHORITY", codes)
        self.assertEqual(result["classification"], "FAIL_STRUCTURE")

    def test_same_semantic_hash_as_declared_oracle_is_not_duplicate_authority(self) -> None:
        oracle = authority_record(
            formula_id="REC.ORACLE.BASS_TEST.001",
            owner="rec_bianchi",
            mode="INDEPENDENT_ORACLE",
        )
        oracle["replay_of"] = "BASS.TEST.001"
        oracle["consumers"] = []
        oracle["allowed_consumer_modes"] = []
        result = audit_documents(
            [
                export_document("bass", [authority_record()]),
                export_document("rec_bianchi", [oracle]),
            ],
            [],
            RUN_ID,
        )
        codes = {finding["code"] for finding in result["structural_findings"]}
        self.assertNotIn("DUPLICATE_SEMANTIC_AUTHORITY", codes)

    def test_stale_commit_is_structural_failure(self) -> None:
        stale = import_document(producer_commit="4" * 40)
        result = audit_documents(
            [export_document("bass", [authority_record()])],
            [stale],
            RUN_ID,
        )
        codes = {finding["code"] for finding in result["structural_findings"]}
        self.assertIn("STALE_UPSTREAM", codes)

    def test_unpublished_provider_is_dependency_blocker_not_structural_failure(self) -> None:
        blocked_import = import_document(
            formula_id="REC.RECOMBINATION.HISTORY.001",
            producer_repository="rec_bianchi",
            producer_commit=None,
            semantic_hash=None,
            status="BLOCKED_PROVIDER_NOT_PUBLISHED",
        )
        result = audit_documents([], [blocked_import], RUN_ID)
        self.assertEqual(result["structural_findings"], [])
        self.assertEqual(result["classification"], "PASS_STRUCTURE_WITH_BLOCKED_DEPENDENCIES")
        self.assertEqual(result["dependency_findings"][0]["code"], "BLOCKED_DEPENDENCY")

    def test_run_id_mismatch_is_structural_failure(self) -> None:
        changed = import_document()
        changed["sync_run_id"] = "5" * 64
        result = audit_documents(
            [export_document("bass", [authority_record()])],
            [changed],
            RUN_ID,
        )
        codes = {finding["code"] for finding in result["structural_findings"]}
        self.assertIn("SYNC_RUN_ID_MISMATCH", codes)

    def test_input_documents_are_not_mutated(self) -> None:
        export = export_document("bass", [authority_record()])
        lock = import_document()
        before_export = copy.deepcopy(export)
        before_lock = copy.deepcopy(lock)
        audit_documents([export], [lock], RUN_ID)
        self.assertEqual(export, before_export)
        self.assertEqual(lock, before_lock)


if __name__ == "__main__":
    unittest.main()
