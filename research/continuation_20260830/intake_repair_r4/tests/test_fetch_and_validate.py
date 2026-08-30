from __future__ import annotations

from dataclasses import replace
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "FETCH_AND_VALIDATE.py"
SPEC = importlib.util.spec_from_file_location("bass_fetch_and_validate", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class GitFixture:
    prefix = "research/continuation_20260830"
    manifest_path = f"{prefix}/MANIFEST.sha256"

    def __init__(self, root: Path) -> None:
        self.repo = root / "repo"
        self.repo.mkdir()
        self.env = os.environ.copy()
        self.env.update(
            {
                "GIT_AUTHOR_NAME": "BASS intake test",
                "GIT_AUTHOR_EMAIL": "bass-intake@example.invalid",
                "GIT_COMMITTER_NAME": "BASS intake test",
                "GIT_COMMITTER_EMAIL": "bass-intake@example.invalid",
            }
        )
        self.git("init", "-q")
        self.write("README.md", b"base\n")
        self.base = self.commit("base")

        self.delivery = {
            f"{self.prefix}/CODEX_HANDOFF.md": b"handoff bytes\n",
            f"{self.prefix}/check_geometry_core.py": b"print('geometry')\n",
        }
        contract = {
            "repository": "fixture/repo",
            "base": {"commit": self.base[0], "tree": self.base[1]},
            "current_scientific_claim": "NO_PASS_RF04",
            "exact_next_action": "BASS-LOCAL-01_NATIVE_TELEMETRY_PARITY",
            "scientific_promotion": False,
            "delivery_paths": [
                f"{self.prefix}/CODEX_HANDOFF.md",
                f"{self.prefix}/CONTRACT.json",
                f"{self.prefix}/check_geometry_core.py",
            ]
        }
        self.delivery[f"{self.prefix}/CONTRACT.json"] = (
            json.dumps(contract, sort_keys=True).encode("utf-8") + b"\n"
        )
        for path, data in self.delivery.items():
            self.write(path, data)
        os.chmod(self.repo / f"{self.prefix}/check_geometry_core.py", 0o755)
        bad_manifest = self.manifest({**self.delivery}, corrupt_first=True)
        self.write(self.manifest_path, bad_manifest)
        self.invalid = self.commit("invalid payload")

        self.write(f"{self.prefix}/REMOTE_PUBLICATION.json", b"{}\n")
        self.publication = self.commit("publication")
        self.write(f"{self.prefix}/TERMINAL.marker", b"terminal\n")
        self.terminal = self.commit("terminal")

        good_manifest = self.manifest(self.delivery, corrupt_first=False)
        self.write(self.manifest_path, good_manifest)
        self.payload = self.commit("corrected payload")
        self.good_manifest = good_manifest
        self.bad_manifest = bad_manifest
        self.spec = MODULE.IntakeSpec(
            repository="fixture/repo",
            objects=(
                MODULE.ObjectPin("base", self.base[0], self.base[1]),
                MODULE.ObjectPin("invalid_payload", self.invalid[0], self.invalid[1]),
                MODULE.ObjectPin("publication", self.publication[0], self.publication[1]),
                MODULE.ObjectPin("prior_terminal", self.terminal[0], self.terminal[1]),
                MODULE.ObjectPin("payload", self.payload[0], self.payload[1]),
            ),
            parent_edges=(
                (self.invalid[0], self.base[0]),
                (self.publication[0], self.invalid[0]),
                (self.terminal[0], self.publication[0]),
                (self.payload[0], self.terminal[0]),
            ),
            payload_commit=self.payload[0],
            payload_tree=self.payload[1],
            manifest_path=self.manifest_path,
            manifest_blob_sha1=self.blob(self.payload[0], self.manifest_path),
            manifest_sha256=hashlib.sha256(good_manifest).hexdigest(),
            expected_entries=3,
            allowed_prefix=f"{self.prefix}/",
            scientific_claim="NO_PASS_RF04",
            next_action="BASS-LOCAL-01_NATIVE_TELEMETRY_PARITY",
        )

    def git(self, *args: str, check: bool = True) -> str:
        proc = subprocess.run(
            ["git", "-C", str(self.repo), *args],
            env=self.env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        if check and proc.returncode:
            raise RuntimeError(proc.stderr)
        return proc.stdout.strip()

    def write(self, rel: str, data: bytes) -> None:
        target = self.repo / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)

    def commit(self, message: str) -> tuple[str, str]:
        self.git("add", "-A")
        self.git("commit", "-q", "-m", message)
        commit = self.git("rev-parse", "HEAD")
        tree = self.git("rev-parse", "HEAD^{tree}")
        return commit, tree

    def blob(self, commit: str, path: str) -> str:
        return self.git("rev-parse", f"{commit}:{path}")

    @staticmethod
    def manifest(files: dict[str, bytes], corrupt_first: bool) -> bytes:
        lines = []
        for index, (path, data) in enumerate(sorted(files.items())):
            digest = hashlib.sha256(data).hexdigest()
            if corrupt_first and index == 0:
                digest = "0" * 64
            lines.append(f"{digest}  {path}\n")
        return "".join(lines).encode("ascii")


class FetchAndValidateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.fixture = GitFixture(self.root)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_success_reads_committed_blobs_not_dirty_worktree(self) -> None:
        handoff = f"{self.fixture.prefix}/CODEX_HANDOFF.md"
        self.fixture.write(handoff, b"dirty worktree mutation\n")
        validated = MODULE.validate_payload(self.fixture.repo, self.fixture.spec)
        self.assertEqual(validated.files[handoff].data, b"handoff bytes\n")
        destination = self.root / "materialized"
        old_umask = os.umask(0o077)
        try:
            receipt = MODULE.materialize(validated, destination, self.fixture.repo)
        finally:
            os.umask(old_umask)
        self.assertEqual((destination / handoff).read_bytes(), b"handoff bytes\n")
        self.assertEqual(
            (destination / f"{self.fixture.prefix}/check_geometry_core.py").stat().st_mode
            & 0o777,
            0o755,
        )
        self.assertEqual(receipt["status"], "PASS_IMMUTABLE_PAYLOAD_INTAKE_ONLY")
        self.assertEqual(receipt["scientific_claim"], "NO_PASS_RF04")

    def test_advanced_branch_tip_does_not_change_immutable_payload(self) -> None:
        self.fixture.write("AFTER_PAYLOAD.marker", b"branch advanced\n")
        self.fixture.commit("advance mutable branch tip")
        validated = MODULE.validate_payload(self.fixture.repo, self.fixture.spec)
        self.assertEqual(validated.spec.payload_commit, self.fixture.payload[0])

    def test_git_replacement_refs_are_ignored(self) -> None:
        self.fixture.write(self.fixture.manifest_path, self.fixture.bad_manifest)
        alternate = self.fixture.commit("replacement candidate")
        self.fixture.git("replace", self.fixture.payload[0], alternate[0])
        validated = MODULE.validate_payload(self.fixture.repo, self.fixture.spec)
        self.assertEqual(
            validated.files[f"{self.fixture.prefix}/CODEX_HANDOFF.md"].data,
            b"handoff bytes\n",
        )

    def test_deprecated_graft_cannot_rewrite_raw_parent_chain(self) -> None:
        grafts = self.fixture.repo / ".git" / "info" / "grafts"
        grafts.write_text(
            f"{self.fixture.payload[0]} {self.fixture.base[0]}\n",
            encoding="ascii",
        )
        validated = MODULE.validate_payload(self.fixture.repo, self.fixture.spec)
        self.assertEqual(validated.spec.payload_commit, self.fixture.payload[0])

    def test_symlink_tree_mode_is_rejected(self) -> None:
        link = self.fixture.repo / self.fixture.prefix / "symlink"
        link.symlink_to("CODEX_HANDOFF.md")
        symlink_commit = self.fixture.commit("add symlink")
        with self.assertRaisesRegex(MODULE.IntakeError, "non-regular"):
            MODULE._blob_at_path(
                self.fixture.repo,
                symlink_commit[0],
                f"{self.fixture.prefix}/symlink",
            )

    def test_historical_bad_manifest_is_rejected(self) -> None:
        bad_spec = MODULE.IntakeSpec(
            repository="fixture/repo",
            objects=(
                MODULE.ObjectPin("base", self.fixture.base[0], self.fixture.base[1]),
                MODULE.ObjectPin("invalid_payload", self.fixture.invalid[0], self.fixture.invalid[1]),
            ),
            parent_edges=((self.fixture.invalid[0], self.fixture.base[0]),),
            payload_commit=self.fixture.invalid[0],
            payload_tree=self.fixture.invalid[1],
            manifest_path=self.fixture.manifest_path,
            manifest_blob_sha1=self.fixture.blob(
                self.fixture.invalid[0], self.fixture.manifest_path
            ),
            manifest_sha256=hashlib.sha256(self.fixture.bad_manifest).hexdigest(),
            expected_entries=3,
            allowed_prefix=f"{self.fixture.prefix}/",
            scientific_claim="NO_PASS_RF04",
            next_action="BASS-LOCAL-01_NATIVE_TELEMETRY_PARITY",
        )
        with self.assertRaisesRegex(MODULE.IntakeError, "payload byte mismatch"):
            MODULE.validate_payload(self.fixture.repo, bad_spec)

    def test_manifest_blob_pin_is_enforced(self) -> None:
        with self.assertRaisesRegex(MODULE.IntakeError, "manifest blob mismatch"):
            MODULE.validate_payload(
                self.fixture.repo,
                replace(self.fixture.spec, manifest_blob_sha1="0" * 40),
            )

    def test_contract_identity_claim_and_next_action_drift_are_rejected(self) -> None:
        contract_path = f"{self.fixture.prefix}/CONTRACT.json"
        original = json.loads(self.fixture.delivery[contract_path])
        mutations = {
            "repository": lambda value: value.__setitem__("repository", "wrong/repo"),
            "base": lambda value: value["base"].__setitem__("tree", "0" * 40),
            "claim": lambda value: value.__setitem__(
                "current_scientific_claim", "PASS_RF04"
            ),
            "next": lambda value: value.__setitem__("exact_next_action", "WRONG"),
            "promotion": lambda value: value.__setitem__("scientific_promotion", True),
        }
        for label, mutate in mutations.items():
            with self.subTest(label=label):
                candidate = json.loads(json.dumps(original))
                mutate(candidate)
                with self.assertRaisesRegex(MODULE.IntakeError, "CONTRACT.json"):
                    MODULE._validate_contract(
                        candidate,
                        set(self.fixture.delivery),
                        self.fixture.spec,
                    )

    def test_exact_parent_chain_is_enforced(self) -> None:
        wrong = replace(
            self.fixture.spec,
            parent_edges=((self.fixture.payload[0], self.fixture.publication[0]),),
        )
        with self.assertRaisesRegex(MODULE.IntakeError, "parent mismatch"):
            MODULE.validate_payload(self.fixture.repo, wrong)

    def test_manifest_rejects_traversal_duplicate_and_backslash(self) -> None:
        digest = "0" * 64
        for path in ("../escape", "a/../escape", "a\\escape"):
            with self.subTest(path=path), self.assertRaises(MODULE.IntakeError):
                MODULE.parse_manifest(
                    f"{digest}  {path}\n".encode("ascii"),
                    expected_entries=1,
                    allowed_prefix="",
                )
        duplicate = f"{digest}  a\n{digest}  a\n".encode("ascii")
        with self.assertRaisesRegex(MODULE.IntakeError, "duplicate"):
            MODULE.parse_manifest(duplicate, expected_entries=2, allowed_prefix="")

    def test_existing_destination_is_never_overwritten(self) -> None:
        validated = MODULE.validate_payload(self.fixture.repo, self.fixture.spec)
        destination = self.root / "existing"
        destination.mkdir()
        marker = destination / "owned"
        marker.write_text("preserve", encoding="utf-8")
        with self.assertRaisesRegex(MODULE.IntakeError, "already exists"):
            MODULE.materialize(validated, destination, self.fixture.repo)
        self.assertEqual(marker.read_text(encoding="utf-8"), "preserve")

    def test_destination_inside_source_repo_is_rejected(self) -> None:
        validated = MODULE.validate_payload(self.fixture.repo, self.fixture.spec)
        with self.assertRaisesRegex(MODULE.IntakeError, "inside source repository"):
            MODULE.materialize(
                validated,
                self.fixture.repo / "do-not-write-here",
                self.fixture.repo,
            )

    def test_repo_subdirectory_input_still_protects_full_repo_root(self) -> None:
        subdirectory = self.fixture.repo / self.fixture.prefix
        validated = MODULE.validate_payload(subdirectory, self.fixture.spec)
        with self.assertRaisesRegex(MODULE.IntakeError, "inside source repository"):
            MODULE.materialize(
                validated,
                self.fixture.repo / "outside-input-subdirectory",
                subdirectory,
            )

    def test_symlink_parent_cannot_redirect_output_into_source_repo(self) -> None:
        validated = MODULE.validate_payload(self.fixture.repo, self.fixture.spec)
        redirect = self.root / "redirect"
        redirect.symlink_to(self.fixture.repo, target_is_directory=True)
        with self.assertRaisesRegex(
            MODULE.IntakeError, "unsafe destination parent|inside source repository"
        ):
            MODULE.materialize(
                validated,
                redirect / "do-not-write-here",
                self.fixture.repo,
            )
        self.assertFalse((self.fixture.repo / "do-not-write-here").exists())

    def test_default_temporary_root_inside_source_repo_is_rejected(self) -> None:
        validated = MODULE.validate_payload(self.fixture.repo, self.fixture.spec)
        old_tmpdir = tempfile.tempdir
        tempfile.tempdir = str(self.fixture.repo)
        try:
            with self.assertRaisesRegex(MODULE.IntakeError, "inside source repository"):
                MODULE.materialize(validated, None, self.fixture.repo)
        finally:
            tempfile.tempdir = old_tmpdir


if __name__ == "__main__":
    unittest.main()
