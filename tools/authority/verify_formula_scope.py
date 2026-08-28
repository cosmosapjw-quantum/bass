#!/usr/bin/env python3
"""Verify the source-bound SCI-AUTH-04 formula-scope bridge manifest."""

from __future__ import annotations

import argparse
from collections.abc import Mapping, Sequence
import fnmatch
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
import sys
from typing import NoReturn


BASE_BRANCH = "agent/architecture/rust-first-rf02b-20260826-r1"
BASE_HEAD = "0563c080e54fcd90d6160bec35e4f20d240d8d2e"
BASE_TREE = "40ae99f9e7465d6332e98b65a5269a1f71eadfb5"
FORMULA_AUTHORITY_SHA256 = (
    "3ecf0dbc8b47a8af83da81e9ed37823b6922e139e420c5bfa2e071b6bbabe361"
)

REQUIRED_DOMAINS = {
    "background",
    "collision",
    "projector",
    "kato",
    "thermodynamics",
}

EXPECTED_SCOPES = {
    "background": {
        "included_scope": {
            "HOMOGENEOUS_POLARIZED_LIOUVILLE_FORMULA",
            "TYPEII_ALIGNED_FIVE_STATE_GENERATED_REFERENCE",
        },
        "excluded_scope": {
            "EINSTEIN_BACKGROUND_EVOLUTION_AUTHORITY",
            "CROSS_FAMILY_RUNTIME_AUTHORITY",
            "SCIENTIFIC_PROMOTION",
        },
    },
    "collision": {
        "included_scope": {
            "COLD_NONTILTED_ELECTRON_REST_THOMSON_FORMULA",
            "TYPEII_ALIGNED_FINITE_TILT_REFERENCE_RUNTIME",
            "SCALAR_AND_POLARIZED_REFERENCE_ACTIONS",
        },
        "excluded_scope": {
            "FINITE_ELECTRON_TILT_FORMULA_AUTHORITY",
            "THERMAL_OR_RECOIL_COMPTON",
            "KLEIN_NISHINA",
            "ALL_MICROPHYSICS_EXACT",
            "PRODUCTION_MIGRATION_AUTHORITY",
        },
    },
    "projector": {
        "included_scope": {
            "TYPEII_MOVING_EQUILIBRIUM_PROJECTOR_REFERENCE",
            "SCALAR_AND_POLARIZED_GENERATED_ACTIONS",
        },
        "excluded_scope": {
            "GENERAL_PROJECTOR_THEOREM",
            "CROSS_FAMILY_AUTHORITY",
            "PRODUCTION_MIGRATION_AUTHORITY",
        },
    },
    "kato": {
        "included_scope": {
            "TYPEII_MOVING_EQUILIBRIUM_KATO_REFERENCE",
            "FULL_DIMENSIONAL_REFERENCE_ARNOLDI_COMPOSITION",
        },
        "excluded_scope": {
            "ADAPTIVE_RESTARTED_KRYLOV_AUTHORITY",
            "CROSS_FAMILY_AUTHORITY",
            "PRODUCTION_MIGRATION_AUTHORITY",
        },
    },
    "thermodynamics": {
        "included_scope": {
            "RECEIPT_CONSTRAINED_SAHAHISTORY_RATE_SCHEDULE_SURROGATE",
            "HISTORICAL_TYPEII_FIXTURE_RECONSTRUCTION",
        },
        "excluded_scope": {
            "ORIGINAL_SAHA_HISTORY_THERMODYNAMICS_AUTHORITY",
            "RECOMBINATION_REIONIZATION_COMPLETE",
            "FRESH_THERMODYNAMICS_AUTHORITY",
            "PRODUCTION_PROMOTION",
        },
    },
}

EXPECTED_CLAIM_REFS = {
    "background": ["HC01"],
    "collision": ["HC02", "FC07", "FC08", "FC09", "FC10"],
    "projector": [],
    "kato": [],
    "thermodynamics": ["FC11"],
}

EXPECTED_DOMAIN_AUTHORITIES = {
    "background": [
        {
            "id": "FORMULA-CORE-HC01",
            "classification": "SOURCE_LOCKED_FORMULA_AUTHORITY",
            "fresh": False,
            "production_runtime_authority": False,
        },
        {
            "id": "GENERATED-TYPEII-BACKGROUND-V1",
            "classification": "PROJECT_DERIVED_GENERATED_REFERENCE",
            "fresh": False,
            "production_runtime_authority": False,
        },
    ],
    "collision": [
        {
            "id": "FORMULA-CORE-HC02",
            "classification": "SOURCE_LOCKED_FORMULA_AUTHORITY",
            "fresh": False,
            "production_runtime_authority": False,
        },
        {
            "id": "G-POL-RUNTIME-II-FINITE-TILT",
            "classification": "REFERENCE_RUNTIME_EVIDENCE",
            "fresh": False,
            "production_runtime_authority": False,
        },
    ],
    "projector": [
        {
            "id": "GENERATED-TYPEII-PROJECTOR-V1",
            "classification": "PROJECT_DERIVED_GENERATED_REFERENCE",
            "fresh": False,
            "production_runtime_authority": False,
        }
    ],
    "kato": [
        {
            "id": "G-RUNTIME-KATO-II",
            "classification": "REFERENCE_RUNTIME_EVIDENCE",
            "fresh": False,
            "production_runtime_authority": False,
        }
    ],
    "thermodynamics": [
        {
            "id": "TYPEII-FIXTURE-SAHARATE-SURROGATE",
            "classification": "SURROGATE_REFERENCE_ONLY",
            "fresh": False,
            "production_runtime_authority": False,
        }
    ],
}

EXPECTED_DOMAIN_IDS = {
    domain: f"SCI-AUTH-04-{domain.upper()}-V1" for domain in REQUIRED_DOMAINS
}

HISTORICAL_POLARIZED_SOURCE_COMMIT = "dc546a07c5d05cd68b6d43c9ca4c41a57d8d5c81"
HISTORICAL_POLARIZED_SOURCE_TREE = "336ba546e4aaa4a5dbe87366a6f465bcff87735d"
EXPECTED_HISTORICAL_DIVERGENCES = [
    {
        "path": "_rustcore/src/kinetic/pol_collide.rs",
        "manifest_sha256": (
            "c6cb5099b139a4f04a5693d1f07ae8bffd90acc9b5ffd32579532a2dce5fe202"
        ),
        "current_blob_sha1": "afcac634c356490ff9af6f30bd1a88217393c211",
        "current_sha256": (
            "e2472459aaf0f6b404010306fa6302801d2e21470079ba9f80c625bbc0f6ad6b"
        ),
    },
    {
        "path": "bianchi/q/polstate.py",
        "manifest_sha256": (
            "3ebabbfe264a50dfe2fd0a2e39c279b201a6911a9711abd9f698f9ad53264da1"
        ),
        "current_blob_sha1": "90cfba2841804f3a0b311aacc107fbc7a5b0a95f",
        "current_sha256": (
            "929d1799105b2b77ddbf18ad6803ea78082a62b72c84f7586a52afb548ec8d41"
        ),
    },
]

EXPECTED_TREES = {
    "_rustcore/src/kinetic": "de19a1472a69d8ef3879a30dd67d1d90df193e07",
    "_rustcore/src/thermo": "3022dabfce6ca50e75b92e2759667f3d1a1bacd0",
    "bianchi/matter": "e10195d46f1ccf78995db36c2894bf9943365863",
    "bianchi/thermo": "a264b3c72fee755c4e42f74c27ffe1c5483e25b3",
    "compiler/derivatives": "402c919e0598823126e36889b6a5ebe1d7f6daa6",
    "compiler/examples": "4026664200ae6327471da9d1dabe065de7832e45",
    "compiler/lowering": "3b3d48026a11292024af6873c0090a09b6946387",
    "compiler/runtime": "87e75e9ec21739f40a4e9062836a741fa15fe645",
    "compiler/validation": "e0f26c61bc696d8b080ff2dd3526f043d334a9a8",
    "generated/rust/typeii": "bfd1d203e10d9690704b1bc8b484bf8530d8c20e",
    "provenance/formula_core": "41ef651611c69140fe4fb74ad1c2d3c881da7f16",
    "runtime/rust/typeii": "9563c86dc59d0375358cd178673420f85e50c871",
}

EXPECTED_DOCUMENTS = {
    "compiler/VERIFICATION.json": {
        "blob_sha1": "6b1bf5be76a578bd1044483571a16c2433e4b69a",
        "sha256": "1c42d41e47ae3ef4e7617b930c13c71137215b12ce91d1b4e57ba9830c5132f2",
    },
    "compiler/runtime/G_RUNTIME_KATO_II_RECEIPT.json": {
        "blob_sha1": "ff38a80356a664bcd2e1c1539d3a7c7cccca8f68",
        "sha256": "1c8b31b4600c65ee502abfabd3fb383c4bd28741dc6a51ac8b8277f6b7c7d9a6",
    },
    "compiler/validation/G_CONSERVATION_QUAD_II_RECEIPT.json": {
        "blob_sha1": "b067185d56171b36a722fef19322acbc0c2d937b",
        "sha256": "2c9cf9c2be104635ad5c67add3debf64309ad8d20b4e0704ab743de232062458",
    },
    "compiler/validation/G_POL_RUNTIME_II_RECEIPT.json": {
        "blob_sha1": "99fce6330490f6fc4789029d59bec15631028bd9",
        "sha256": "b99e22ab06564f77920bd552aff26ad1d3d5e60c68d4982b5579ede68c677008",
    },
    "compiler/validation/typeii_fixture_authority.json": {
        "blob_sha1": "b71372faa7dde85e928802c08c831299ebe99bcd",
        "sha256": "8085430c3e29d44b73d113e14f051c58285569c86b56eb74c0fdd40469719f4d",
    },
    "compiler/validation/typeii_fixture_receipt.json": {
        "blob_sha1": "6ced331a9af4954e2c79949a4281ed2bf3aba277",
        "sha256": "db830d9676dcf94f971d2a01e5952dcc53c6a3697050e33583809a367be96e26",
    },
    "docs/development/STATE_AUTHORITY_LEDGER_20260821.json": {
        "blob_sha1": "b17bc53e34ab1b1031804d6540ce4035ff23bfb0",
        "sha256": "140db670ab4cff1af3c07907e2d6b9e87b6e0475185cfa5a52d4f4d8f166269d",
    },
    "generated/rust/typeii/manifest.json": {
        "blob_sha1": "0ba8e32b1454d5fa29ccb052de051107fad1e936",
        "sha256": "5a8f05b917a7134584052167d5ece0c787a1f2683f347316ec6260844a5d19f4",
    },
    "generated/rust/typeii/polarized_manifest.json": {
        "blob_sha1": "24f4182cd0c72626a9561ab98325548be5c02600",
        "sha256": "6c59254536a1ecdd69bc0f4610f28cdc2ae33ebcd633d4f70e0aee2b7a63fca4",
    },
    "provenance/formula_core/Bianchi_Core_Closure_Final_Claim_Policy.json": {
        "blob_sha1": "b152938aecbbc06023c7fc99f40eed41dda3f223",
        "sha256": "63fbe84aef42b21fe98f479aa17d7e1731bba65a4bae58a50d97561825c84aa8",
    },
    "provenance/formula_core/authority/Bianchi_CC01_Convention_Manifest_FINAL.json": {
        "blob_sha1": "4d082befafe3b67067516d84d2f2f40f8a6102d8",
        "sha256": "fb2fdeccfe4ed9af70cb9a33d611abe12a242ad47096be541d3b3c60a1a742d7",
    },
    "provenance/integration/BACKGROUND_EVOLUTION_INTEGRATION_20260824.json": {
        "blob_sha1": "d8ae1f098be79fa9156c0bac9170cc204edf8812",
        "sha256": "0cf73ff049b2f567a6a95e7e8fe8ee00262a469ddb13ed683640a4f4e188b5fa",
    },
    "runtime/rust/typeii/tests/FIXTURE_PROVENANCE.json": {
        "blob_sha1": "dfee51903025b4c9d3f62f63581271bd3b6a98cb",
        "sha256": "ba1f5915fe28db7ce4c8ecf7b96f189502d997c91c81f658f63f57e3e2817b0e",
    },
}

SCALAR_GENERATED_FILES = {
    "mod.rs": "3268f06134026646dc0ff7b3b4ac4e4907f1c52f47382053c7e20ff381c35265",
    "typeii_background.rs": (
        "0f1f31dad4c106fa22ac1ea8e95651ede24a32d24400629e10f8271d99490d15"
    ),
    "typeii_collision.rs": (
        "745f15441abdd48b1ac5e1e10946aeca9bf22d5e74ab8c8215a449d681572e39"
    ),
    "typeii_kato.rs": (
        "ddea9a2af01201f84aecdabce2f70642650ccf816c827b80e6605921031f13de"
    ),
}

SCALAR_SEMANTICS = {
    "background": "exact Type-II aligned 5-state specialization",
    "collision": "matrix-free moment-factorized finite-tilt scalar Thomson generator action",
    "kato": "matrix-free [Pdot,P] action",
    "projector": "low-rank scalar bolometric moving-equilibrium action",
}

POLARIZED_SEMANTICS = {
    "boost": (
        "canonical gauge-restored screen isometry plus D^4 amplitude and "
        "dOmega/D^2 weights"
    ),
    "carrier": "basis-free rank-9 coherency tensor: symmetric 6 + antisymmetric/V 3",
    "collision": (
        "finite-electron-tilt rest-frame rank-9 Thomson generator, "
        "matrix-free O(Nang)"
    ),
    "kato": "matrix-free [Pdot,P] action on the polarized moving equilibrium manifold",
    "projector": "rank-one boosted unpolarized equilibrium projector",
}

ALLOWED_CHANGE_PATTERNS = (
    "provenance/**",
    "tools/authority/**",
    "tests/authority/**",
    "artifacts/authority/sci_auth_04/**",
    "docs/authority/**",
)


class VerificationError(RuntimeError):
    """Typed fail-closed verification error."""


def fail(code: str, detail: str) -> NoReturn:
    raise VerificationError(f"{code}: {detail}")


def load_json(path: Path) -> object:
    def reject_duplicates(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                fail("DUPLICATE_JSON_KEY", f"{path}: {key}")
            result[key] = value
        return result

    try:
        return json.loads(
            path.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicates
        )
    except VerificationError:
        raise
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        fail("INVALID_JSON", f"{path}: {exc}")


def as_mapping(value: object, label: str) -> dict[str, object]:
    if not isinstance(value, dict):
        fail("MANIFEST_CLAIM_MISMATCH", f"{label} must be an object")
    return value


def as_list(value: object, label: str) -> list[object]:
    if not isinstance(value, list):
        fail("MANIFEST_CLAIM_MISMATCH", f"{label} must be an array")
    return value


def git(
    repo: Path, *args: str, check: bool = True
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", "--no-replace-objects", "-C", str(repo), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and result.returncode:
        fail("GIT_FAILURE", f"git {' '.join(args)}: {result.stderr.strip()}")
    return result


def git_line(repo: Path, *args: str) -> str:
    return git(repo, *args).stdout.removesuffix("\n")


def sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        fail("SOURCE_IDENTITY_MISMATCH", f"{path}: {exc}")


def safe_repo_path(repo: Path, relative: str) -> Path:
    pure = PurePosixPath(relative)
    if pure.is_absolute() or ".." in pure.parts or str(pure) != relative:
        fail("SOURCE_IDENTITY_MISMATCH", f"unsafe repository path: {relative!r}")
    return repo.joinpath(*pure.parts)


def unique_strings(value: object, label: str, *, nonempty: bool) -> list[str]:
    items = as_list(value, label)
    if not all(isinstance(item, str) and item for item in items):
        fail("MANIFEST_CLAIM_MISMATCH", f"{label} must contain strings")
    strings = list(items)
    if len(strings) != len(set(strings)):
        fail("MANIFEST_CLAIM_MISMATCH", f"{label} contains duplicates")
    if nonempty and not strings:
        fail("MISSING_DOMAIN_AUTHORITY", f"{label} is empty")
    return strings


def verify_manifest_semantics(manifest: dict[str, object]) -> None:
    if manifest.get("schema") != "bass-scientific-authority-scope/v1":
        fail("MANIFEST_CLAIM_MISMATCH", "unexpected schema")
    if manifest.get("work_unit") != "SCI-AUTH-04":
        fail("MANIFEST_CLAIM_MISMATCH", "unexpected work unit")

    source_base = as_mapping(manifest.get("source_base"), "source_base")
    expected_base = {
        "branch": BASE_BRANCH,
        "head": BASE_HEAD,
        "tree": BASE_TREE,
    }
    if source_base != expected_base:
        fail("BASE_IDENTITY_MISMATCH", "manifest source base differs")

    boundary = as_mapping(manifest.get("claim_boundary"), "claim_boundary")
    expected_boundary = {
        "terminal_on_validator_pass": "PASS_SCI_AUTH_04_VALIDATOR",
        "formula_authority": "TYPED_BUT_NOT_AUTO_PROMOTED",
        "scientific_promotion": False,
        "scientific_equivalence": "UNCHANGED",
        "performance": "NONE",
    }
    if boundary != expected_boundary:
        fail("MANIFEST_CLAIM_MISMATCH", "claim boundary differs")

    label = as_mapping(
        manifest.get("formula_authority_label"), "formula_authority_label"
    )
    if label.get("sha256") != FORMULA_AUTHORITY_SHA256:
        fail("MANIFEST_CLAIM_MISMATCH", "formula authority label differs")
    if label.get("source_presence") != "HASH_ONLY_EXTERNAL":
        fail("MANIFEST_CLAIM_MISMATCH", "external formula bytes were promoted")
    if label.get("claim_policy_path") != (
        "provenance/formula_core/Bianchi_Core_Closure_Final_Claim_Policy.json"
    ):
        fail("MANIFEST_CLAIM_MISMATCH", "claim-policy path differs")
    if unique_strings(
        label.get("allowed_claim_ids"), "allowed_claim_ids", nonempty=True
    ) != [f"HC{index:02d}" for index in range(1, 9)]:
        fail("MANIFEST_CLAIM_MISMATCH", "allowed claim IDs differ")
    if unique_strings(
        label.get("forbidden_claim_ids"), "forbidden_claim_ids", nonempty=True
    ) != [f"FC{index:02d}" for index in range(1, 16)]:
        fail("MANIFEST_CLAIM_MISMATCH", "forbidden claim IDs differ")

    domains = as_mapping(manifest.get("domains"), "domains")
    if set(domains) != REQUIRED_DOMAINS:
        fail(
            "MISSING_DOMAIN_AUTHORITY",
            f"expected={sorted(REQUIRED_DOMAINS)} actual={sorted(domains)}",
        )

    seen_ids: set[str] = set()
    for domain in sorted(REQUIRED_DOMAINS):
        entry = as_mapping(domains.get(domain), f"domains.{domain}")
        authority_id = entry.get("authority_id")
        if not isinstance(authority_id, str) or not authority_id:
            fail("MISSING_DOMAIN_AUTHORITY", f"{domain} authority_id is missing")
        if authority_id in seen_ids:
            fail("MISSING_DOMAIN_AUTHORITY", f"duplicate authority_id {authority_id}")
        seen_ids.add(authority_id)
        if authority_id != EXPECTED_DOMAIN_IDS[domain]:
            fail("MANIFEST_CLAIM_MISMATCH", f"{domain} authority_id differs")

        included = set(
            unique_strings(
                entry.get("included_scope"),
                f"domains.{domain}.included_scope",
                nonempty=True,
            )
        )
        excluded = set(
            unique_strings(
                entry.get("excluded_scope"),
                f"domains.{domain}.excluded_scope",
                nonempty=True,
            )
        )
        if included & excluded:
            fail("OVERBROAD_SCOPE", f"{domain} included/excluded scopes overlap")
        expected_included = EXPECTED_SCOPES[domain]["included_scope"]
        expected_excluded = EXPECTED_SCOPES[domain]["excluded_scope"]
        added = (included - expected_included) | (excluded - expected_excluded)
        if added:
            fail("OVERBROAD_SCOPE", f"{domain} adds {sorted(added)}")
        if included != expected_included or excluded != expected_excluded:
            fail("MANIFEST_CLAIM_MISMATCH", f"{domain} scope is incomplete")

        refs = unique_strings(
            entry.get("claim_policy_refs"),
            f"domains.{domain}.claim_policy_refs",
            nonempty=False,
        )
        if refs != EXPECTED_CLAIM_REFS[domain]:
            fail("MANIFEST_CLAIM_MISMATCH", f"{domain} claim refs differ")

        authorities = as_list(entry.get("authorities"), f"domains.{domain}.authorities")
        if not authorities:
            fail("MISSING_DOMAIN_AUTHORITY", f"{domain} has no authority entries")
        typed = [as_mapping(item, f"domains.{domain}.authorities") for item in authorities]
        if domain == "thermodynamics":
            for authority in typed:
                if (
                    authority.get("classification") != "SURROGATE_REFERENCE_ONLY"
                    or authority.get("fresh") is not False
                    or authority.get("production_runtime_authority") is not False
                ):
                    fail(
                        "SURROGATE_PROMOTION",
                        "historical Type-II thermodynamics must remain surrogate-only",
                    )
        if typed != EXPECTED_DOMAIN_AUTHORITIES[domain]:
            fail(
                "MANIFEST_CLAIM_MISMATCH",
                f"{domain} authority classification differs",
            )
        for authority in typed:
            nested_id = authority.get("id")
            if not isinstance(nested_id, str) or not nested_id or nested_id in seen_ids:
                fail("MISSING_DOMAIN_AUTHORITY", f"invalid nested authority in {domain}")
            seen_ids.add(nested_id)

    unresolved = as_list(
        manifest.get("unresolved_authorities"), "unresolved_authorities"
    )
    expected_unresolved = [
        {
            "id": "ORIGINAL-SAHISTORY-THERMODYNAMICS",
            "domain": "thermodynamics",
            "status": "MISSING_HISTORICAL_AUTHORITY",
            "may_promote": False,
        }
    ]
    if unresolved != expected_unresolved:
        fail(
            "SURROGATE_PROMOTION",
            "missing historical thermodynamics authority was relabeled",
        )

    historical = as_mapping(
        manifest.get("historical_manifest_bindings"),
        "historical_manifest_bindings",
    )
    expected_historical = {
        "source_commit": HISTORICAL_POLARIZED_SOURCE_COMMIT,
        "source_tree": HISTORICAL_POLARIZED_SOURCE_TREE,
        "classification": "HISTORICAL_REFERENCE_BINDING_NOT_CURRENT_AUTHORITY",
        "scientific_promotion": False,
        "divergences": EXPECTED_HISTORICAL_DIVERGENCES,
    }
    if historical != expected_historical:
        fail(
            "MANIFEST_CLAIM_MISMATCH",
            "historical polarized-manifest binding classification differs",
        )

    if as_mapping(manifest.get("frozen_trees"), "frozen_trees") != EXPECTED_TREES:
        fail("SOURCE_IDENTITY_MISMATCH", "frozen tree inventory differs")
    if as_mapping(
        manifest.get("document_bindings"), "document_bindings"
    ) != EXPECTED_DOCUMENTS:
        fail("SOURCE_IDENTITY_MISMATCH", "document binding inventory differs")


def verify_git_and_source_identity(repo: Path) -> None:
    actual_root = Path(git_line(repo, "rev-parse", "--show-toplevel")).resolve()
    if actual_root != repo.resolve():
        fail("BASE_IDENTITY_MISMATCH", f"repo root expected={repo} actual={actual_root}")
    if git_line(repo, "rev-parse", f"{BASE_HEAD}^{{tree}}") != BASE_TREE:
        fail("BASE_IDENTITY_MISMATCH", "exact RF-02B base tree differs")
    ancestry = git(repo, "merge-base", "--is-ancestor", BASE_HEAD, "HEAD", check=False)
    if ancestry.returncode:
        fail("BASE_IDENTITY_MISMATCH", "exact RF-02B base is not an ancestor")

    for path, expected in EXPECTED_TREES.items():
        actual = git_line(repo, "rev-parse", f"HEAD:{path}")
        if actual != expected:
            fail(
                "SOURCE_IDENTITY_MISMATCH",
                f"tree {path} expected={expected} actual={actual}",
            )
    for path, identity in EXPECTED_DOCUMENTS.items():
        actual_blob = git_line(repo, "rev-parse", f"HEAD:{path}")
        if actual_blob != identity["blob_sha1"]:
            fail(
                "SOURCE_IDENTITY_MISMATCH",
                f"blob {path} expected={identity['blob_sha1']} actual={actual_blob}",
            )
        actual_sha256 = sha256(safe_repo_path(repo, path))
        if actual_sha256 != identity["sha256"]:
            fail(
                "SOURCE_IDENTITY_MISMATCH",
                f"sha256 {path} expected={identity['sha256']} actual={actual_sha256}",
            )


def verify_claim_policy(repo: Path) -> None:
    policy_path = safe_repo_path(
        repo, "provenance/formula_core/Bianchi_Core_Closure_Final_Claim_Policy.json"
    )
    policy = as_mapping(load_json(policy_path), "claim policy")
    allowed = [
        as_mapping(item, "allowed_headline_claims")
        for item in as_list(policy.get("allowed_headline_claims"), "allowed claims")
    ]
    forbidden = [
        as_mapping(item, "forbidden_claims")
        for item in as_list(policy.get("forbidden_claims"), "forbidden claims")
    ]
    if [item.get("id") for item in allowed] != [
        f"HC{index:02d}" for index in range(1, 9)
    ]:
        fail("MANIFEST_CLAIM_MISMATCH", "claim-policy HC IDs differ")
    if [item.get("id") for item in forbidden] != [
        f"FC{index:02d}" for index in range(1, 16)
    ]:
        fail("MANIFEST_CLAIM_MISMATCH", "claim-policy FC IDs differ")

    hc02 = next(item for item in allowed if item.get("id") == "HC02")
    expected_conditions = {
        "Cold electron distribution.",
        "Electron bulk tilt is zero in the authority frame.",
        "Elastic Thomson limit.",
    }
    if hc02.get("classification") != "EXACT_SOURCE_LOCKED" or set(
        unique_strings(hc02.get("minimal_conditions"), "HC02 conditions", nonempty=True)
    ) != expected_conditions:
        fail("MANIFEST_CLAIM_MISMATCH", "HC02 cold/non-tilted/elastic lock differs")
    hc02_exclusions = set(
        unique_strings(hc02.get("not_implied"), "HC02 exclusions", nonempty=True)
    )
    if hc02_exclusions != {
        "thermal or recoil Comptonization",
        "Klein-Nishina corrections",
        "finite-electron-tilt collisions",
    }:
        fail("MANIFEST_CLAIM_MISMATCH", "HC02 exclusions differ")

    extensions = [
        as_mapping(item, "future_extensions")
        for item in as_list(policy.get("future_extensions"), "future extensions")
    ]
    finite_tilt = next(item for item in extensions if item.get("id") == "EX01")
    if finite_tilt.get("current_status") != "NOT_INCLUDED":
        fail("OVERBROAD_SCOPE", "finite-electron tilt was promoted in claim policy")


def verify_sha_map(repo: Path, values: object, label: str) -> None:
    mapping = as_mapping(values, label)
    for relative, expected in mapping.items():
        if not isinstance(relative, str) or not isinstance(expected, str):
            fail("SOURCE_IDENTITY_MISMATCH", f"invalid {label} entry")
        actual = sha256(safe_repo_path(repo, relative))
        if actual != expected:
            fail(
                "SOURCE_IDENTITY_MISMATCH",
                f"{label} {relative} expected={expected} actual={actual}",
            )


def verify_generated_manifests(repo: Path) -> None:
    scalar = as_mapping(
        load_json(safe_repo_path(repo, "generated/rust/typeii/manifest.json")),
        "scalar generated manifest",
    )
    polarized = as_mapping(
        load_json(safe_repo_path(repo, "generated/rust/typeii/polarized_manifest.json")),
        "polarized generated manifest",
    )
    if scalar.get("schema") != "bass-generated-rust-v1":
        fail("MANIFEST_CLAIM_MISMATCH", "scalar generated schema differs")
    if scalar.get("formula_authority_sha256") != FORMULA_AUTHORITY_SHA256:
        fail("MANIFEST_CLAIM_MISMATCH", "scalar formula label differs")
    if as_mapping(scalar.get("semantics"), "scalar semantics") != SCALAR_SEMANTICS:
        fail("MANIFEST_CLAIM_MISMATCH", "scalar generated semantics differ")
    if as_mapping(
        scalar.get("generated_files"), "scalar generated files"
    ) != SCALAR_GENERATED_FILES:
        fail("MANIFEST_CLAIM_MISMATCH", "scalar generated-file manifest differs")
    for filename, expected in SCALAR_GENERATED_FILES.items():
        relative = f"generated/rust/typeii/{filename}"
        actual = sha256(safe_repo_path(repo, relative))
        if actual != expected:
            fail(
                "SOURCE_IDENTITY_MISMATCH",
                f"generated file {relative} expected={expected} actual={actual}",
            )

    if polarized.get("schema") != "bass-generated-rust-polarization-v1":
        fail("MANIFEST_CLAIM_MISMATCH", "polarized generated schema differs")
    if polarized.get("stage") != "G-POL-RUNTIME-II":
        fail("MANIFEST_CLAIM_MISMATCH", "polarized stage differs")
    if as_mapping(
        polarized.get("semantics"), "polarized semantics"
    ) != POLARIZED_SEMANTICS:
        fail("MANIFEST_CLAIM_MISMATCH", "polarized generated semantics differ")
    polarized_files = as_mapping(
        polarized.get("generated_files"), "polarized generated files"
    )
    expected_polarized = {
        "typeii_polarized.rs": (
            "34cad7b9fdb38652be48faa111a12f6b54cfd7a2cb172e5ed428745c19ca288b"
        )
    }
    if polarized_files != expected_polarized:
        fail("MANIFEST_CLAIM_MISMATCH", "polarized generated-file manifest differs")
    verify_sha_map(
        repo,
        {
            f"generated/rust/typeii/{name}": digest
            for name, digest in expected_polarized.items()
        },
        "polarized generated files",
    )
    authority_hashes = as_mapping(
        polarized.get("authority_hashes"), "polarized authority hashes"
    )
    divergences = {
        entry["path"]: entry for entry in EXPECTED_HISTORICAL_DIVERGENCES
    }
    observed_divergences: set[str] = set()
    if git_line(
        repo, "rev-parse", f"{HISTORICAL_POLARIZED_SOURCE_COMMIT}^{{tree}}"
    ) != HISTORICAL_POLARIZED_SOURCE_TREE:
        fail("SOURCE_IDENTITY_MISMATCH", "historical polarized source tree differs")
    for relative, expected in authority_hashes.items():
        if not isinstance(relative, str) or not isinstance(expected, str):
            fail("MANIFEST_CLAIM_MISMATCH", "invalid polarized authority hash entry")
        path = safe_repo_path(repo, relative)
        actual = sha256(path)
        if actual == expected:
            continue
        divergence = divergences.get(relative)
        if divergence is None or divergence["manifest_sha256"] != expected:
            fail(
                "SOURCE_IDENTITY_MISMATCH",
                f"unclassified polarized authority-hash divergence: {relative}",
            )
        actual_blob = git_line(repo, "rev-parse", f"HEAD:{relative}")
        if (
            actual_blob != divergence["current_blob_sha1"]
            or actual != divergence["current_sha256"]
        ):
            fail(
                "SOURCE_IDENTITY_MISMATCH",
                f"current polarized reference bytes drifted: {relative}",
            )
        historical_bytes = git(
            repo,
            "show",
            f"{HISTORICAL_POLARIZED_SOURCE_COMMIT}:{relative}",
        ).stdout.encode("utf-8")
        historical_sha256 = hashlib.sha256(historical_bytes).hexdigest()
        if historical_sha256 != expected:
            fail(
                "SOURCE_IDENTITY_MISMATCH",
                f"historical polarized reference bytes drifted: {relative}",
            )
        observed_divergences.add(relative)
    if observed_divergences != set(divergences):
        fail(
            "MANIFEST_CLAIM_MISMATCH",
            "historical polarized divergence inventory is incomplete",
        )

    compiler_verification = as_mapping(
        load_json(safe_repo_path(repo, "compiler/VERIFICATION.json")),
        "compiler verification",
    )
    if compiler_verification.get("formula_authority_sha256") != FORMULA_AUTHORITY_SHA256:
        fail("MANIFEST_CLAIM_MISMATCH", "compiler formula label differs")


def verify_historical_thermodynamics(repo: Path) -> None:
    fixture_authority = as_mapping(
        load_json(
            safe_repo_path(repo, "compiler/validation/typeii_fixture_authority.json")
        ),
        "Type-II fixture authority",
    )
    opacity = as_mapping(fixture_authority.get("opacity_model"), "opacity_model")
    boundary = opacity.get("authority_boundary")
    if not isinstance(boundary, str) or (
        "surrogate" not in boundary
        or "not the original thermodynamics authority" not in boundary
    ):
        fail("SURROGATE_PROMOTION", "fixture thermodynamics boundary differs")
    fixture_claim = as_mapping(
        fixture_authority.get("claim_boundary"), "fixture claim boundary"
    )
    not_established = unique_strings(
        fixture_claim.get("not_established"),
        "fixture not_established",
        nonempty=True,
    )
    if "the original SahaHistory thermodynamics implementation" not in not_established:
        fail("SURROGATE_PROMOTION", "fixture claims original thermodynamics")

    provenance = as_mapping(
        load_json(
            safe_repo_path(repo, "runtime/rust/typeii/tests/FIXTURE_PROVENANCE.json")
        ),
        "fixture provenance",
    )
    provenance_claim = as_mapping(
        provenance.get("claim_boundary"), "provenance claim boundary"
    )
    excluded = unique_strings(
        provenance_claim.get("not_established"),
        "provenance not_established",
        nonempty=True,
    )
    if "original SahaHistory thermodynamic authority" not in excluded:
        fail("SURROGATE_PROMOTION", "fixture provenance promotes thermodynamics")
    historical = as_mapping(
        provenance.get("historical_preserved"), "historical preserved"
    )
    legacy = as_mapping(
        historical.get("legacy_80kb_fixture_receipt"), "legacy fixture"
    )
    if legacy.get("bytes_available") is not False:
        fail("SURROGATE_PROMOTION", "unavailable historical fixture was relabeled")

    integration = as_mapping(
        load_json(
            safe_repo_path(
                repo, "provenance/integration/BACKGROUND_EVOLUTION_INTEGRATION_20260824.json"
            )
        ),
        "background integration receipt",
    )
    integration_boundary = as_mapping(
        integration.get("claim_boundary"), "background integration claim boundary"
    )
    if (
        integration_boundary.get("authority_row_promoted") is not False
        or integration_boundary.get("production_collision_wired") is not False
    ):
        fail("OVERBROAD_SCOPE", "historical integration receipt was promoted")


def verify_transitive_fixture_freeze(repo: Path) -> None:
    receipt = as_mapping(
        load_json(
            safe_repo_path(repo, "compiler/validation/typeii_fixture_receipt.json")
        ),
        "fixture receipt",
    )
    verify_sha_map(repo, receipt.get("input_hashes"), "fixture input hashes")
    verify_sha_map(
        repo,
        receipt.get("executable_test_sources"),
        "fixture executable test hashes",
    )
    verify_sha_map(repo, receipt.get("canonical_outputs"), "fixture output hashes")
    dependency = as_mapping(
        receipt.get("source_dependency_status"), "source dependency status"
    )
    pre_liouville = as_mapping(
        dependency.get("pre_liouville_ap_implementation"),
        "pre-Liouville source binding",
    )
    verify_sha_map(repo, pre_liouville.get("hashed_paths"), "pre-Liouville hashes")


def path_is_allowed(relative: str) -> bool:
    if relative.startswith("generated/"):
        name = PurePosixPath(relative).name
        return name.startswith("manifest") and name.endswith(".json")
    if relative.startswith("compiler/validation/"):
        name = PurePosixPath(relative).name
        return "authority" in name and name.endswith(".json")
    return any(fnmatch.fnmatchcase(relative, pattern) for pattern in ALLOWED_CHANGE_PATTERNS)


def verify_changed_path_closure(repo: Path) -> list[str]:
    tracked = git(repo, "diff", "--name-only", "-z", BASE_HEAD).stdout
    untracked = git(
        repo, "ls-files", "--others", "--exclude-standard", "-z"
    ).stdout
    paths = sorted({path for path in (tracked + untracked).split("\0") if path})
    forbidden = [path for path in paths if not path_is_allowed(path)]
    if forbidden:
        fail("PATH_SCOPE_VIOLATION", f"outside allowlist: {forbidden}")
    return paths


def verify(repo: Path, manifest_path: Path) -> dict[str, object]:
    loaded = load_json(manifest_path)
    manifest = as_mapping(loaded, "authority manifest")
    verify_manifest_semantics(manifest)
    verify_git_and_source_identity(repo)
    verify_claim_policy(repo)
    verify_generated_manifests(repo)
    verify_historical_thermodynamics(repo)
    verify_transitive_fixture_freeze(repo)
    changed_paths = verify_changed_path_closure(repo)
    return {
        "schema": "bass-sci-auth-04-verification/v1",
        "base_head": BASE_HEAD,
        "base_tree": BASE_TREE,
        "manifest_sha256": sha256(manifest_path),
        "frozen_document_count": len(EXPECTED_DOCUMENTS),
        "frozen_tree_count": len(EXPECTED_TREES),
        "changed_paths": changed_paths,
        "checks": {
            "authority_domains": "PASS",
            "claim_policy_scope": "PASS",
            "generated_manifest_scope": "PASS",
            "historical_thermodynamics_surrogate_only": "PASS",
            "immutable_source_trees": "PASS",
            "path_closure": "PASS",
        },
        "formula_authority": "TYPED_BUT_NOT_AUTO_PROMOTED",
        "scientific_equivalence": "UNCHANGED",
        "performance": "NONE",
        "terminal": "PASS_SCI_AUTH_04_VALIDATOR",
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    default_repo = Path(__file__).resolve().parents[2]
    default_manifest = (
        default_repo
        / "provenance"
        / "authority"
        / "sci_auth_04"
        / "FORMULA_SCOPE_AUTHORITY.json"
    )
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=default_repo)
    parser.add_argument("--manifest", type=Path, default=default_manifest)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        result = verify(args.repo.resolve(), args.manifest.resolve())
    except VerificationError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
