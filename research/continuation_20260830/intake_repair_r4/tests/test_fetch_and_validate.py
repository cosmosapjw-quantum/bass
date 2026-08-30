from __future__ import annotations

from dataclasses import replace
from contextlib import redirect_stderr, redirect_stdout
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


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

    def test_validated_payload_cannot_be_materialized_with_another_repository(self) -> None:
        validated = MODULE.validate_payload(self.fixture.repo, self.fixture.spec)
        other_parent = self.root / "other-repository"
        other_parent.mkdir()
        other = GitFixture(other_parent)
        destination = self.root / "cross-repository-output"
        with self.assertRaisesRegex(MODULE.IntakeError, "repository binding mismatch"):
            MODULE.materialize(validated, destination, other.repo)
        self.assertFalse(destination.exists())

    def test_repository_path_replacement_after_validation_is_rejected(self) -> None:
        validated = MODULE.validate_payload(self.fixture.repo, self.fixture.spec)
        displaced = self.root / "displaced-validated-repository"
        other_parent = self.root / "replacement-repository"
        other_parent.mkdir()
        other = GitFixture(other_parent)
        original_path = self.fixture.repo
        original_path.rename(displaced)
        other.repo.rename(original_path)
        destination = self.root / "replaced-repository-output"
        with self.assertRaisesRegex(MODULE.IntakeError, "repository binding mismatch"):
            MODULE.materialize(validated, destination, original_path)
        self.assertFalse(destination.exists())

    def test_repository_path_replacement_during_materialization_is_rejected(self) -> None:
        validated = MODULE.validate_payload(self.fixture.repo, self.fixture.spec)
        displaced = self.root / "displaced-during-materialization"
        other_parent = self.root / "replacement-during-materialization"
        other_parent.mkdir()
        other = GitFixture(other_parent)
        source_path = self.fixture.repo
        destination = self.root / "source-swap-partial"
        original_write = MODULE._write_materialized_records

        def write_then_replace(root_fd: int, payload: object) -> None:
            original_write(root_fd, payload)
            source_path.rename(displaced)
            other.repo.rename(source_path)

        with mock.patch.object(
            MODULE, "_write_materialized_records", side_effect=write_then_replace
        ):
            with self.assertRaisesRegex(MODULE.IntakeError, "repository binding mismatch"):
                MODULE.materialize(validated, destination, source_path)

        self.assertTrue(destination.is_dir())
        self.assertEqual(destination.stat().st_mode & 0o777, 0o700)

    def test_validate_only_rechecks_repository_binding_before_receipt(self) -> None:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with mock.patch.object(MODULE, "SPEC", self.fixture.spec), mock.patch.object(
            MODULE,
            "_bound_materialization_layout",
            side_effect=MODULE.IntakeError("injected repository binding mismatch"),
        ), redirect_stdout(stdout), redirect_stderr(stderr):
            result = MODULE.main([str(self.fixture.repo), "--validate-only"])
        self.assertEqual(result, 2)
        self.assertEqual(stdout.getvalue(), "")
        self.assertIn("repository binding mismatch", stderr.getvalue())

    def test_repo_subdirectory_input_still_protects_full_repo_root(self) -> None:
        subdirectory = self.fixture.repo / self.fixture.prefix
        validated = MODULE.validate_payload(subdirectory, self.fixture.spec)
        with self.assertRaisesRegex(MODULE.IntakeError, "inside source repository"):
            MODULE.materialize(
                validated,
                self.fixture.repo / "outside-input-subdirectory",
                subdirectory,
            )

    def test_non_ascii_repository_path_is_supported(self) -> None:
        unicode_parent = self.root / "저장소"
        unicode_parent.mkdir()
        unicode_fixture = GitFixture(unicode_parent)
        validated = MODULE.validate_payload(unicode_fixture.repo, unicode_fixture.spec)
        destination = self.root / "unicode-materialized"
        result = MODULE.materialize(validated, destination, unicode_fixture.repo)
        self.assertEqual(result["status"], "PASS_IMMUTABLE_PAYLOAD_INTAKE_ONLY")

    def test_ambient_git_routing_cannot_replace_supplied_repository(self) -> None:
        decoy_parent = self.root / "decoy-fixture"
        decoy_parent.mkdir()
        decoy = GitFixture(decoy_parent)
        injected = {
            "GIT_DIR": str(decoy.repo / ".git"),
            "GIT_WORK_TREE": str(decoy.repo),
            "GIT_COMMON_DIR": str(decoy.repo / ".git"),
            "GIT_OBJECT_DIRECTORY": str(decoy.repo / ".git" / "objects"),
            "GIT_ALTERNATE_OBJECT_DIRECTORIES": str(self.fixture.repo / ".git" / "objects"),
            "GIT_INDEX_FILE": str(decoy.repo / ".git" / "index"),
            "GIT_PREFIX": "injected/",
            "GIT_NAMESPACE": "injected",
            "GIT_SHALLOW_FILE": str(decoy.repo / ".git" / "shallow"),
            "GIT_REPLACE_REF_BASE": "refs/injected/",
            "GIT_CONFIG_PARAMETERS": "'core.bare=false'",
            "GIT_CONFIG_SYSTEM": str(decoy.repo / "system.gitconfig"),
            "GIT_CONFIG_GLOBAL": str(decoy.repo / "global.gitconfig"),
            "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": "core.bare",
            "GIT_CONFIG_VALUE_0": "false",
        }
        with mock.patch.dict(os.environ, injected, clear=False):
            git_env = MODULE._git_environment()
            self.assertEqual(
                {key for key in git_env if key.startswith("GIT_")},
                {
                    "GIT_CONFIG_GLOBAL",
                    "GIT_CONFIG_NOSYSTEM",
                    "GIT_NO_LAZY_FETCH",
                    "GIT_NO_REPLACE_OBJECTS",
                    "GIT_OPTIONAL_LOCKS",
                    "GIT_TERMINAL_PROMPT",
                },
            )
            self.assertEqual(git_env["GIT_NO_LAZY_FETCH"], "1")
            self.assertEqual(
                MODULE._git_argv(Path("/validated/repo"), "cat-file", "blob", "abc")[:4],
                ["git", "--no-replace-objects", "--no-lazy-fetch", "-C"],
            )
            self.assertEqual(
                MODULE._repository_root(self.fixture.repo),
                self.fixture.repo.resolve(strict=True),
            )
            validated = MODULE.validate_payload(self.fixture.repo, self.fixture.spec)
        self.assertEqual(validated.spec.payload_commit, self.fixture.payload[0])

    def test_linked_worktree_git_metadata_roots_are_protected(self) -> None:
        linked = self.root / "linked"
        linked_two = self.root / "linked-two"
        self.fixture.git("worktree", "add", "-q", "--detach", str(linked), self.fixture.payload[0])
        self.fixture.git("worktree", "add", "-q", "--detach", str(linked_two), self.fixture.terminal[0])
        validated = MODULE.validate_payload(linked, self.fixture.spec)
        git_dir = Path(
            self.fixture.git("-C", str(linked), "rev-parse", "--absolute-git-dir")
        ).resolve(strict=True)
        common_dir = Path(
            self.fixture.git(
                "-C",
                str(linked),
                "rev-parse",
                "--path-format=absolute",
                "--git-common-dir",
            )
        ).resolve(strict=True)
        protected_roots = (
            linked.resolve(strict=True),
            linked_two.resolve(strict=True),
            self.fixture.repo.resolve(strict=True),
            git_dir,
            common_dir,
        )
        for protected in protected_roots:
            with self.subTest(protected=protected), self.assertRaisesRegex(
                MODULE.IntakeError, "source repository|protected Git path"
            ):
                MODULE.materialize(validated, protected / "do-not-write-here", linked)

        for protected in protected_roots:
            with self.subTest(tmpdir=protected):
                old_tmpdir = tempfile.tempdir
                tempfile.tempdir = str(protected)
                try:
                    with self.assertRaisesRegex(
                        MODULE.IntakeError, "source repository|protected Git path"
                    ):
                        MODULE.materialize(validated, None, linked)
                finally:
                    tempfile.tempdir = old_tmpdir

        unsafe_alias = self.root / "unsafe-tmp-alias"
        unsafe_alias.symlink_to(common_dir, target_is_directory=True)
        old_tmpdir = tempfile.tempdir
        tempfile.tempdir = None
        try:
            with mock.patch.dict(
                os.environ,
                {
                    "TMPDIR": str(unsafe_alias),
                    "TEMP": str(unsafe_alias),
                    "TMP": str(unsafe_alias),
                },
                clear=False,
            ):
                before = set(common_dir.glob("bass-rf04-intake-*"))
                with self.assertRaisesRegex(MODULE.IntakeError, "protected Git path"):
                    MODULE.materialize(validated, None, linked)
                self.assertEqual(
                    set(common_dir.glob("bass-rf04-intake-*")),
                    before,
                )
        finally:
            tempfile.tempdir = old_tmpdir

    def test_materialization_fails_closed_without_dir_fd_support(self) -> None:
        validated = MODULE.validate_payload(self.fixture.repo, self.fixture.spec)
        with mock.patch.object(MODULE.os, "supports_dir_fd", set()):
            with self.assertRaisesRegex(MODULE.IntakeError, "unsupported"):
                MODULE.materialize(
                    validated,
                    self.root / "unsupported-platform",
                    self.fixture.repo,
                )

    def test_opened_parent_inode_inside_protected_worktree_is_rejected(self) -> None:
        validated = MODULE.validate_payload(self.fixture.repo, self.fixture.spec)
        intended_parent = self.root / "intended-parent"
        intended_parent.mkdir()
        moved_parent = self.root / "moved-intended-parent"
        original = MODULE._open_stable_directory
        attacked = False

        def replace_parent(path: Path) -> tuple[Path, int]:
            nonlocal attacked
            if not attacked:
                attacked = True
                intended_parent.rename(moved_parent)
                self.fixture.repo.rename(intended_parent)
            return original(path)

        with mock.patch.object(
            MODULE, "_open_stable_directory", side_effect=replace_parent
        ):
            with self.assertRaisesRegex(MODULE.IntakeError, "protected Git path"):
                MODULE.materialize(
                    validated,
                    intended_parent / "do-not-write-here",
                    self.fixture.repo,
                )
        self.assertFalse((intended_parent / "do-not-write-here").exists())

    def test_parent_path_replacement_prevents_success_receipt(self) -> None:
        validated = MODULE.validate_payload(self.fixture.repo, self.fixture.spec)
        public_parent = self.root / "public-parent"
        public_parent.mkdir()
        destination = public_parent / "materialized"
        moved_parent = self.root / "moved-public-parent"
        replacement_marker = public_parent / "attacker-marker"
        original = MODULE._write_materialized_records

        def replace_parent(root_fd: int, payload: object) -> None:
            public_parent.rename(moved_parent)
            public_parent.mkdir()
            replacement_marker.write_text("preserve", encoding="utf-8")
            original(root_fd, payload)

        with mock.patch.object(
            MODULE, "_write_materialized_records", side_effect=replace_parent
        ):
            with self.assertRaisesRegex(MODULE.IntakeError, "parent identity changed"):
                MODULE.materialize(validated, destination, self.fixture.repo)

        self.assertEqual(replacement_marker.read_text(encoding="utf-8"), "preserve")
        self.assertTrue(
            (moved_parent / "materialized" / self.fixture.manifest_path).is_file()
        )
        self.assertFalse(destination.exists())

    def test_creation_error_never_removes_replacement_root_directory(self) -> None:
        validated = MODULE.validate_payload(self.fixture.repo, self.fixture.spec)
        destination = self.root / "creation-error-root"
        diverted = self.root / "diverted-creation-root"

        def replace_root(_descriptor: int, _mode: int) -> None:
            destination.rename(diverted)
            destination.mkdir()
            raise OSError("injected fchmod failure")

        with mock.patch.object(MODULE.os, "fchmod", side_effect=replace_root):
            with self.assertRaisesRegex(
                MODULE.IntakeError,
                "partial output.*creation-error-root.*injected fchmod failure",
            ):
                MODULE.materialize(validated, destination, self.fixture.repo)

        self.assertTrue(destination.is_dir())
        self.assertTrue(diverted.is_dir())

    def test_post_write_failure_leaves_private_partial_without_cleanup(self) -> None:
        validated = MODULE.validate_payload(self.fixture.repo, self.fixture.spec)
        destination = self.root / "post-write-partial"

        with mock.patch.object(
            MODULE,
            "_assert_public_parent_identity",
            side_effect=MODULE.IntakeError("injected post-write failure"),
        ):
            with self.assertRaisesRegex(
                MODULE.IntakeError,
                "partial output.*post-write-partial.*injected post-write failure",
            ):
                MODULE.materialize(validated, destination, self.fixture.repo)

        self.assertTrue(destination.is_dir())
        self.assertEqual(destination.stat().st_mode & 0o777, 0o700)
        self.assertTrue((destination / self.fixture.manifest_path).is_file())

    def test_insecure_writable_destination_namespace_is_rejected(self) -> None:
        validated = MODULE.validate_payload(self.fixture.repo, self.fixture.spec)
        insecure_parent = self.root / "insecure-parent"
        insecure_parent.mkdir(mode=0o777)
        insecure_parent.chmod(0o777)
        destination = insecure_parent / "do-not-create"
        with self.assertRaisesRegex(MODULE.IntakeError, "insecure destination namespace"):
            MODULE.materialize(validated, destination, self.fixture.repo)
        self.assertFalse(destination.exists())

    def test_path_replacement_cannot_redirect_writes_or_cleanup(self) -> None:
        validated = MODULE.validate_payload(self.fixture.repo, self.fixture.spec)
        destination = self.root / "materialized-race"
        diverted = self.root / "diverted-owned-root"
        replacement_marker = destination / "attacker-marker"
        trap = self.root / "trap"
        trap.mkdir()
        original = MODULE._write_materialized_records

        def replace_path(root_fd: int, payload: object) -> None:
            destination.rename(diverted)
            destination.mkdir()
            replacement_marker.write_text("preserve", encoding="utf-8")
            original(root_fd, payload)

        with mock.patch.object(
            MODULE, "_write_materialized_records", side_effect=replace_path
        ):
            with self.assertRaisesRegex(MODULE.IntakeError, "destination identity changed"):
                MODULE.materialize(validated, destination, self.fixture.repo)

        self.assertEqual(replacement_marker.read_text(encoding="utf-8"), "preserve")
        self.assertEqual(list(trap.iterdir()), [])
        self.assertTrue(diverted.is_dir())
        self.assertTrue((diverted / self.fixture.manifest_path).is_file())

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

    def test_ambient_temp_candidates_never_probe_or_mutate_protected_repo(self) -> None:
        validated = MODULE.validate_payload(self.fixture.repo, self.fixture.spec)
        audit_state: dict[str, object] = {"active": False, "writes": []}

        def audit(event: str, args: tuple[object, ...]) -> None:
            if not audit_state["active"]:
                return
            is_write_open = (
                event == "open"
                and len(args) >= 3
                and isinstance(args[2], int)
                and bool(
                    args[2]
                    & (
                        os.O_WRONLY
                        | os.O_RDWR
                        | os.O_CREAT
                        | os.O_TRUNC
                        | os.O_APPEND
                    )
                )
            )
            if is_write_open:
                try:
                    audited_path = Path(os.fsdecode(os.fspath(args[0]))).resolve()
                except (TypeError, ValueError, OSError):
                    audited_path = None
                is_write_open = audited_path is not None and (
                    audited_path == self.fixture.repo
                    or audited_path.is_relative_to(self.fixture.repo)
                )
            if is_write_open or event in {
                "os.mkdir",
                "os.remove",
                "os.rmdir",
                "os.rename",
            }:
                writes = audit_state["writes"]
                assert isinstance(writes, list)
                writes.append((event, args))

        sys.addaudithook(audit)

        for variable in ("TMPDIR", "TEMP", "TMP"):
            with self.subTest(variable=variable):
                writes: list[tuple[str, tuple[object, ...]]] = []
                audit_state["writes"] = writes

                old_tmpdir = tempfile.tempdir
                tempfile.tempdir = None
                try:
                    with mock.patch.dict(os.environ, {}, clear=False):
                        for candidate in ("TMPDIR", "TEMP", "TMP"):
                            os.environ.pop(candidate, None)
                        os.environ[variable] = str(self.fixture.repo)
                        audit_state["active"] = True
                        try:
                            with self.assertRaisesRegex(
                                MODULE.IntakeError, "inside source repository"
                            ):
                                MODULE.materialize(
                                    validated, None, self.fixture.repo
                                )
                        finally:
                            audit_state["active"] = False
                finally:
                    tempfile.tempdir = old_tmpdir
                self.assertEqual(writes, [])


if __name__ == "__main__":
    unittest.main()
