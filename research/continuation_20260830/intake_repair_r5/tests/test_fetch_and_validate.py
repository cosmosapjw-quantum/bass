from __future__ import annotations

from dataclasses import replace
from contextlib import redirect_stderr, redirect_stdout
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import shutil
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


def load_locator_module(suffix: str) -> object:
    """Load a fresh locator module so PATH-bound Git behavior is isolated."""

    name = f"bass_fetch_and_validate_{suffix}"
    spec = importlib.util.spec_from_file_location(name, MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


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

    def partial_clone(self, name: str, git: Path) -> Path:
        self.fixture.git("config", "uploadpack.allowFilter", "true")
        destination = self.root / name
        proc = subprocess.run(
            [
                str(git),
                "clone",
                "-q",
                "--filter=blob:none",
                "--no-checkout",
                f"file://{self.fixture.repo}",
                str(destination),
            ],
            env=self.fixture.env,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        if proc.returncode:
            self.fail(f"could not create partial-clone fixture: {proc.stderr}")
        return destination

    def assert_blob_missing_without_lazy_fetch(
        self, git: Path, repo: Path, blob: str
    ) -> None:
        env = self.fixture.env.copy()
        env["GIT_NO_LAZY_FETCH"] = "1"
        proc = subprocess.run(
            [str(git), "-C", str(repo), "cat-file", "-e", blob],
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertNotEqual(proc.returncode, 0, "blob was unexpectedly materialized")

    @staticmethod
    def object_inventory(repo: Path) -> tuple[tuple[str, int, str], ...]:
        objects = repo / ".git" / "objects"
        return tuple(
            sorted(
                (
                    str(path.relative_to(objects)),
                    path.stat().st_size,
                    hashlib.sha256(path.read_bytes()).hexdigest(),
                )
                for path in objects.rglob("*")
                if path.is_file()
            )
        )

    @staticmethod
    def regular_file_inventory(root: Path) -> tuple[tuple[str, int, str], ...]:
        return tuple(
            sorted(
                (
                    str(path.relative_to(root)),
                    path.stat().st_size,
                    hashlib.sha256(path.read_bytes()).hexdigest(),
                )
                for path in root.rglob("*")
                if path.is_file()
            )
        )

    def write_git_wrapper(
        self, name: str, delegate: Path, *, strip_no_lazy_environment: bool = True
    ) -> Path:
        wrapper_dir = self.root / name
        wrapper_dir.mkdir()
        wrapper = wrapper_dir / "git"
        environment_line = (
            "os.environ.pop('GIT_NO_LAZY_FETCH', None)\n"
            if strip_no_lazy_environment
            else ""
        )
        source = (
            "#!/usr/bin/python3\n"
            "import os\n"
            "import sys\n"
            f"{environment_line}"
            f"os.execv({str(delegate)!r}, [{str(delegate)!r}, *sys.argv[1:]])\n"
        )
        wrapper.write_text(source + "#" * (4096 - len(source)), encoding="utf-8")
        wrapper.chmod(0o755)
        return wrapper

    def require_git_243(self) -> Path:
        legacy_git = Path("/usr/bin/git")
        self.assertTrue(legacy_git.is_file(), "/usr/bin/git is unavailable")
        version = subprocess.run(
            [str(legacy_git), "--version"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(version.returncode, 0, version.stderr.decode(errors="replace"))
        self.assertEqual(version.stdout, b"git version 2.43.0\n")
        option_probe = subprocess.run(
            [str(legacy_git), "--no-lazy-fetch", "--version"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertNotEqual(
            option_probe.returncode,
            0,
            "/usr/bin/git unexpectedly accepts --no-lazy-fetch",
        )
        return legacy_git

    def write_exec_path_wrapper(
        self, name: str, delegate: Path, exec_path: Path
    ) -> Path:
        wrapper_dir = self.root / name
        wrapper_dir.mkdir()
        wrapper = wrapper_dir / "git"
        wrapper.write_text(
            "#!/usr/bin/python3\n"
            "import os\n"
            "import sys\n"
            "if sys.argv[1:] == ['--exec-path']:\n"
            f"    os.write(1, os.fsencode({str(exec_path)!r}) + b'\\n')\n"
            "    raise SystemExit(0)\n"
            f"os.execv({str(delegate)!r}, [{str(delegate)!r}, *sys.argv[1:]])\n",
            encoding="utf-8",
        )
        wrapper.chmod(0o755)
        return wrapper

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

    def test_git_243_accepts_complete_repository_without_global_flag(self) -> None:
        legacy_git = self.require_git_243()

        with mock.patch.dict(os.environ, {"PATH": "/usr/bin:/bin"}, clear=False):
            compatible = load_locator_module("git243_complete")
            try:
                validated = compatible.validate_payload(
                    self.fixture.repo, self.fixture.spec
                )
            except compatible.IntakeError as exc:
                self.fail(f"Git 2.43 compatibility failed: {exc}")
        self.assertEqual(validated.spec.payload_commit, self.fixture.payload[0])

    def test_git_243_environment_guard_blocks_real_promisor_fetch(self) -> None:
        legacy_git = self.require_git_243()

        partial = self.partial_clone("partial-real-git243", legacy_git)
        manifest_blob = self.fixture.spec.manifest_blob_sha1
        self.assert_blob_missing_without_lazy_fetch(legacy_git, partial, manifest_blob)
        before = self.object_inventory(partial)
        with mock.patch.dict(os.environ, {"PATH": "/usr/bin:/bin"}, clear=False):
            compatible = load_locator_module("git243_real_promisor")
            with self.assertRaises(compatible.IntakeError):
                compatible.validate_payload(partial, self.fixture.spec)
        self.assertEqual(self.object_inventory(partial), before)
        self.assert_blob_missing_without_lazy_fetch(legacy_git, partial, manifest_blob)

    def test_unproven_environment_guard_is_rejected_before_payload_read(self) -> None:
        legacy_git = self.require_git_243()

        partial = self.partial_clone("partial-unprotected-wrapper", legacy_git)
        manifest_blob = self.fixture.spec.manifest_blob_sha1
        self.assert_blob_missing_without_lazy_fetch(legacy_git, partial, manifest_blob)
        wrapper = self.write_git_wrapper("ignores-no-lazy-env", legacy_git)
        path = f"{wrapper.parent}:/usr/bin:/bin"

        with mock.patch.dict(os.environ, {"PATH": path}, clear=False):
            incompatible = load_locator_module("ignored_environment_guard")
            with self.assertRaisesRegex(
                incompatible.IntakeError,
                "Git lazy-fetch guard capability could not be proven",
            ):
                incompatible.validate_payload(partial, self.fixture.spec)

        self.assert_blob_missing_without_lazy_fetch(legacy_git, partial, manifest_blob)

    def test_failed_capability_probe_does_not_leak_test_owned_directory(self) -> None:
        legacy_git = self.require_git_243()
        wrapper = self.write_git_wrapper("leak-check-wrapper", legacy_git)
        probe_parent = self.root / "probe-parent"
        probe_parent.mkdir()
        old_tmpdir = tempfile.tempdir
        tempfile.tempdir = str(probe_parent)
        try:
            with mock.patch.dict(
                os.environ,
                {"PATH": f"{wrapper.parent}:/usr/bin:/bin"},
                clear=False,
            ):
                incompatible = load_locator_module("failed_probe_cleanup")
                with self.assertRaisesRegex(
                    incompatible.IntakeError,
                    "Git lazy-fetch guard capability could not be proven",
                ):
                    incompatible.validate_payload(self.fixture.repo, self.fixture.spec)
        finally:
            tempfile.tempdir = old_tmpdir
        self.assertEqual(list(probe_parent.iterdir()), [])

    def test_probe_cleanup_failure_does_not_cache_verified_runtime(self) -> None:
        isolated = load_locator_module("cleanup_cache")
        layout = isolated._repository_layout(self.fixture.repo)
        probe_parent = self.root / "cleanup-cache-parent"
        probe_parent.mkdir()
        old_tmpdir = tempfile.tempdir
        tempfile.tempdir = str(probe_parent)
        retained: Path | None = None
        try:
            with mock.patch.object(
                isolated.shutil, "rmtree", side_effect=OSError("injected cleanup failure")
            ):
                with self.assertRaisesRegex(
                    isolated.IntakeError, "injected cleanup failure"
                ) as raised:
                    isolated._verify_git_lazy_fetch_guard(layout)
            match = re.search(
                r"probe evidence retained at (.+)$", str(raised.exception)
            )
            self.assertIsNotNone(match)
            assert match is not None
            retained = Path(match.group(1)).resolve(strict=True)
            self.assertEqual(retained.parent, probe_parent.resolve(strict=True))
            self.assertTrue(retained.name.startswith("bass-rf04-intake-"))
            self.assertIsNone(isolated._VERIFIED_GIT_RUNTIME)
            shutil.rmtree(retained)
            retained = None
            with mock.patch.object(
                isolated,
                "_create_destination",
                wraps=isolated._create_destination,
            ) as allocate:
                isolated._verify_git_lazy_fetch_guard(layout)
            self.assertEqual(allocate.call_count, 1)
        finally:
            tempfile.tempdir = old_tmpdir
            if retained is not None and retained.is_dir():
                shutil.rmtree(retained)

    def test_helper_command_path_is_quoted_against_shell_injection(self) -> None:
        delegate = self.require_git_243()
        marker = self.root / "PWNED"
        exec_path = Path(
            str(self.root / "helpers;touch${IFS}") + str(marker) + ";#"
        )
        exec_path.mkdir(parents=True)
        real_exec_path = Path(
            subprocess.check_output([str(delegate), "--exec-path"])
            .decode("ascii")
            .strip()
        )
        (exec_path / "git-upload-pack").symlink_to(
            (real_exec_path / "git-upload-pack").resolve(strict=True)
        )
        wrapper = self.write_exec_path_wrapper(
            "metachar-helper-wrapper", delegate, exec_path
        )
        with mock.patch.dict(
            os.environ,
            {"PATH": f"{wrapper.parent}:/usr/bin:/bin"},
            clear=False,
        ):
            isolated = load_locator_module("metachar_helper")
            validated = isolated.validate_payload(self.fixture.repo, self.fixture.spec)
        self.assertEqual(validated.spec.payload_commit, self.fixture.payload[0])
        self.assertFalse(marker.exists())

    def test_non_ascii_and_quoted_helper_path_is_supported(self) -> None:
        delegate = self.require_git_243()
        exec_path = self.root / "Git 헬퍼 path 'quoted'"
        exec_path.mkdir()
        real_exec_path = Path(
            os.fsdecode(subprocess.check_output([str(delegate), "--exec-path"])).strip()
        )
        (exec_path / "git-upload-pack").symlink_to(
            (real_exec_path / "git-upload-pack").resolve(strict=True)
        )
        wrapper = self.write_exec_path_wrapper(
            "unicode-helper-wrapper", delegate, exec_path
        )
        with mock.patch.dict(
            os.environ,
            {"PATH": f"{wrapper.parent}:/usr/bin:/bin"},
            clear=False,
        ):
            isolated = load_locator_module("unicode_helper")
            validated = isolated.validate_payload(self.fixture.repo, self.fixture.spec)
        self.assertEqual(validated.spec.payload_commit, self.fixture.payload[0])

    def test_modern_global_option_guards_when_environment_is_stripped(self) -> None:
        modern_git = Path("/usr/local/bin/git")
        option_probe = None
        if modern_git.is_file():
            option_probe = subprocess.run(
                [str(modern_git), "--no-lazy-fetch", "--version"],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
        if option_probe is not None and option_probe.returncode == 0:
            wrapper = self.write_git_wrapper("modern-cli-only", modern_git)
        else:
            legacy_git = Path("/usr/bin/git")
            if not legacy_git.is_file():
                self.fail("neither a modern Git nor /usr/bin/git is available")
            wrapper_dir = self.root / "synthetic-modern-cli"
            wrapper_dir.mkdir()
            wrapper = wrapper_dir / "git"
            wrapper.write_text(
                "#!/usr/bin/python3\n"
                "import os\n"
                "import sys\n"
                "args = sys.argv[1:]\n"
                "if '--no-lazy-fetch' in args:\n"
                "    args = [arg for arg in args if arg != '--no-lazy-fetch']\n"
                "    os.environ['GIT_NO_LAZY_FETCH'] = '1'\n"
                "else:\n"
                "    os.environ.pop('GIT_NO_LAZY_FETCH', None)\n"
                f"os.execv({str(legacy_git)!r}, [{str(legacy_git)!r}, *args])\n",
                encoding="utf-8",
            )
            wrapper.chmod(0o755)
        path = f"{wrapper.parent}:/usr/bin:/bin"
        with mock.patch.dict(os.environ, {"PATH": path}, clear=False):
            compatible = load_locator_module("modern_cli_only")
            try:
                validated = compatible.validate_payload(
                    self.fixture.repo, self.fixture.spec
                )
            except compatible.IntakeError as exc:
                self.fail(f"redundant modern Git CLI guard was not used: {exc}")
            argv = compatible._git_argv(
                self.fixture.repo, "cat-file", "blob", "0" * 40
            )
        self.assertEqual(validated.spec.payload_commit, self.fixture.payload[0])
        self.assertIn("--no-lazy-fetch", argv)

    def test_replaced_bound_git_is_rejected_before_materialization(self) -> None:
        delegate = Path("/usr/local/bin/git")
        if not delegate.is_file():
            delegate = Path("/usr/bin/git")
        if not delegate.is_file():
            self.fail("no Git executable is available")
        wrapper = self.write_git_wrapper(
            "replace-bound-git", delegate, strip_no_lazy_environment=False
        )
        marker = self.root / "replacement-executed"
        path = f"{wrapper.parent}:/usr/bin:/bin"
        destination = self.root / "must-not-materialize-after-git-replacement"
        with mock.patch.dict(os.environ, {"PATH": path}, clear=False):
            compatible = load_locator_module("replace_bound_git")
            validated = compatible.validate_payload(
                self.fixture.repo, self.fixture.spec
            )
            replacement = wrapper.parent / "replacement"
            replacement.write_text(
                "#!/usr/bin/python3\n"
                "from pathlib import Path\n"
                f"Path({str(marker)!r}).write_text('executed', encoding='ascii')\n"
                "raise SystemExit(91)\n",
                encoding="utf-8",
            )
            replacement.chmod(0o755)
            os.replace(replacement, wrapper)
            with self.assertRaisesRegex(
                compatible.IntakeError, "Git executable binding changed"
            ):
                compatible.materialize(
                    validated, destination, self.fixture.repo
                )
        self.assertFalse(marker.exists())
        self.assertFalse(destination.exists())

    def test_in_place_bound_git_rewrite_invalidates_capability_cache(self) -> None:
        delegate = Path("/usr/local/bin/git")
        if not delegate.is_file():
            delegate = Path("/usr/bin/git")
        if not delegate.is_file():
            self.fail("no Git executable is available")
        wrapper = self.write_git_wrapper(
            "rewrite-bound-git", delegate, strip_no_lazy_environment=False
        )
        marker = self.root / "rewrite-executed"
        path = f"{wrapper.parent}:/usr/bin:/bin"
        destination = self.root / "must-not-materialize-after-git-rewrite"
        with mock.patch.dict(os.environ, {"PATH": path}, clear=False):
            compatible = load_locator_module("rewrite_bound_git")
            validated = compatible.validate_payload(
                self.fixture.repo, self.fixture.spec
            )
            before = wrapper.stat()
            malicious = (
                "#!/usr/bin/python3\n"
                "from pathlib import Path\n"
                f"Path({str(marker)!r}).write_text('executed', encoding='ascii')\n"
                "raise SystemExit(92)\n"
            ).encode("utf-8")
            original_size = before.st_size
            self.assertLessEqual(
                len(malicious), original_size, "test wrapper is too small"
            )
            malicious += b"#" * (original_size - len(malicious))
            wrapper.write_bytes(malicious)
            wrapper.chmod(0o755)
            os.utime(wrapper, ns=(before.st_atime_ns, before.st_mtime_ns))
            after = wrapper.stat()
            self.assertEqual(after.st_ino, before.st_ino)
            self.assertEqual(after.st_size, before.st_size)
            self.assertEqual(after.st_mtime_ns, before.st_mtime_ns)
            with self.assertRaisesRegex(
                compatible.IntakeError, "Git executable binding changed"
            ):
                compatible.materialize(
                    validated, destination, self.fixture.repo
                )
        self.assertFalse(marker.exists())
        self.assertFalse(destination.exists())

    def test_production_transport_denial_survives_post_probe_guard_loss(self) -> None:
        delegate = Path("/usr/local/bin/git")
        if not delegate.is_file():
            delegate = Path("/usr/bin/git")
        if not delegate.is_file():
            self.fail("no Git executable is available")

        partial = self.partial_clone("partial-post-probe-loss", delegate)
        manifest_blob = self.fixture.spec.manifest_blob_sha1
        self.assert_blob_missing_without_lazy_fetch(delegate, partial, manifest_blob)
        before = self.object_inventory(partial)
        wrapper_dir = self.root / "post-probe-loss-wrapper"
        wrapper_dir.mkdir()
        wrapper = wrapper_dir / "git"
        wrapper.write_text(
            "#!/usr/bin/python3\n"
            "import os\n"
            "import sys\n"
            f"target = {str(partial)!r}\n"
            "args = sys.argv[1:]\n"
            "if target in args:\n"
            "    os.environ.pop('GIT_NO_LAZY_FETCH', None)\n"
            "    args = [arg for arg in args if arg != '--no-lazy-fetch']\n"
            f"os.execv({str(delegate)!r}, [{str(delegate)!r}, *args])\n",
            encoding="utf-8",
        )
        wrapper.chmod(0o755)
        path = f"{wrapper.parent}:/usr/bin:/bin"

        with mock.patch.dict(os.environ, {"PATH": path}, clear=False):
            compatible = load_locator_module("post_probe_guard_loss")
            with self.assertRaises(compatible.IntakeError):
                compatible.validate_payload(partial, self.fixture.spec)

        self.assertEqual(self.object_inventory(partial), before)
        self.assert_blob_missing_without_lazy_fetch(delegate, partial, manifest_blob)

    def test_probe_rejects_control_with_wrong_sentinel_bytes(self) -> None:
        isolated = load_locator_module("wrong_control_bytes")
        layout = isolated._repository_layout(self.fixture.repo)
        original = isolated._probe_git

        def wrong_control(runtime: object, *args: str, **kwargs: object) -> object:
            result = original(runtime, *args, **kwargs)
            if "cat-file" in args and kwargs.get("no_lazy_fetch") is False:
                return subprocess.CompletedProcess(result.args, 0, b"wrong\n", b"")
            return result

        with mock.patch.object(isolated, "_probe_git", side_effect=wrong_control):
            with self.assertRaisesRegex(
                isolated.IntakeError,
                "control could not fetch the local sentinel",
            ):
                isolated._verify_git_lazy_fetch_guard(layout)

    def test_probe_rejects_guarded_stdout_on_failure(self) -> None:
        isolated = load_locator_module("guarded_stdout")
        layout = isolated._repository_layout(self.fixture.repo)
        original = isolated._probe_git

        def guarded_stdout(runtime: object, *args: str, **kwargs: object) -> object:
            result = original(runtime, *args, **kwargs)
            if "cat-file" in args and kwargs.get("no_lazy_fetch") is True:
                return subprocess.CompletedProcess(result.args, 1, b"exposed\n", result.stderr)
            return result

        with mock.patch.object(isolated, "_probe_git", side_effect=guarded_stdout):
            with self.assertRaisesRegex(
                isolated.IntakeError,
                "guarded sentinel lookup fetched or exposed",
            ):
                isolated._verify_git_lazy_fetch_guard(layout)

    def test_probe_detects_in_place_object_store_content_mutation(self) -> None:
        isolated = load_locator_module("object_store_content_mutation")
        layout = isolated._repository_layout(self.fixture.repo)
        original = isolated._probe_git
        seeded = False
        mutated = False

        def mutate_store(runtime: object, *args: str, **kwargs: object) -> object:
            nonlocal seeded, mutated
            result = original(runtime, *args, **kwargs)
            if (
                "config" in args
                and "remote.probe.partialclonefilter" in args
                and args[-1] == "blob:none"
            ):
                client = Path(args[args.index("-C") + 1])
                if client.name == "guarded":
                    marker = client / ".git" / "objects" / "info" / "inventory-marker"
                    marker.write_bytes(b"before")
                    seeded = True
            if (
                seeded
                and not mutated
                and "cat-file" in args
                and kwargs.get("no_lazy_fetch") is True
            ):
                client = Path(args[args.index("-C") + 1])
                marker = client / ".git" / "objects" / "info" / "inventory-marker"
                marker.write_bytes(b"after!")
                mutated = True
            return result

        with mock.patch.object(isolated, "_probe_git", side_effect=mutate_store):
            with self.assertRaisesRegex(
                isolated.IntakeError,
                "guarded sentinel lookup fetched or exposed",
            ):
                isolated._verify_git_lazy_fetch_guard(layout)
        self.assertTrue(seeded)
        self.assertTrue(mutated)

    def test_probe_rejects_alternate_object_store(self) -> None:
        isolated = load_locator_module("alternate_object_store")
        layout = isolated._repository_layout(self.fixture.repo)
        original = isolated._probe_git

        def add_alternate(runtime: object, *args: str, **kwargs: object) -> object:
            result = original(runtime, *args, **kwargs)
            if (
                "config" in args
                and "remote.probe.partialclonefilter" in args
                and args[-1] == "blob:none"
            ):
                client = Path(args[args.index("-C") + 1])
                if client.name == "guarded":
                    alternate = client / ".git" / "objects" / "info" / "alternates"
                    alternate.write_text("/untrusted/objects\n", encoding="ascii")
            return result

        with mock.patch.object(isolated, "_probe_git", side_effect=add_alternate):
            with self.assertRaisesRegex(
                isolated.IntakeError, "unexpectedly uses alternates"
            ):
                isolated._verify_git_lazy_fetch_guard(layout)

    def test_probe_rejects_shared_object_store(self) -> None:
        isolated = load_locator_module("shared_object_store")
        layout = isolated._repository_layout(self.fixture.repo)
        original = isolated._probe_git
        replaced = False

        def share_store(runtime: object, *args: str, **kwargs: object) -> object:
            nonlocal replaced
            result = original(runtime, *args, **kwargs)
            if (
                not replaced
                and "config" in args
                and "remote.probe.partialclonefilter" in args
                and args[-1] == "blob:none"
            ):
                client = Path(args[args.index("-C") + 1])
                if client.name == "guarded":
                    guarded_objects = client / ".git" / "objects"
                    control_objects = client.parent / "control" / ".git" / "objects"
                    shutil.rmtree(guarded_objects)
                    guarded_objects.symlink_to(control_objects, target_is_directory=True)
                    replaced = True
            return result

        with mock.patch.object(isolated, "_probe_git", side_effect=share_store):
            with self.assertRaisesRegex(
                isolated.IntakeError, "object stores are not isolated"
            ):
                isolated._verify_git_lazy_fetch_guard(layout)
        self.assertTrue(replaced)

    def test_probe_rejects_second_guarded_lookup_exposure(self) -> None:
        isolated = load_locator_module("second_guarded_exposure")
        layout = isolated._repository_layout(self.fixture.repo)
        original = isolated._probe_git
        guarded_lookups = 0

        def expose_on_recheck(runtime: object, *args: str, **kwargs: object) -> object:
            nonlocal guarded_lookups
            result = original(runtime, *args, **kwargs)
            if "cat-file" in args and kwargs.get("no_lazy_fetch") is True:
                guarded_lookups += 1
                if guarded_lookups == 2:
                    return subprocess.CompletedProcess(
                        result.args,
                        0,
                        b"BASS RF-04 Git lazy-fetch capability probe\n",
                        b"",
                    )
            return result

        with mock.patch.object(
            isolated, "_probe_git", side_effect=expose_on_recheck
        ):
            with self.assertRaisesRegex(
                isolated.IntakeError, "guarded store changed after the control fetch"
            ):
                isolated._verify_git_lazy_fetch_guard(layout)
        self.assertEqual(guarded_lookups, 2)

    def test_probe_rejects_changed_protected_repository_identity(self) -> None:
        isolated = load_locator_module("protected_identity")
        layout = isolated._repository_layout(self.fixture.repo)
        changed = tuple(
            isolated.ProtectedRoot(root.label, root.path, (0, 0))
            for root in layout.protected_roots
        )
        changed_layout = isolated.RepositoryLayout(
            layout.worktree,
            layout.git_dir,
            layout.common_git_dir,
            layout.worktree_identity,
            layout.git_dir_identity,
            layout.common_git_dir_identity,
            changed,
        )
        with self.assertRaisesRegex(
            isolated.IntakeError,
            "protected repository identity changed during Git probe",
        ):
            isolated._verify_git_lazy_fetch_guard(changed_layout)

    def test_probe_rejects_git_digest_mismatch_after_differential(self) -> None:
        isolated = load_locator_module("git_digest_mismatch")
        layout = isolated._repository_layout(self.fixture.repo)
        runtime = isolated._resolve_git_runtime()
        original = isolated._hash_git_executable

        def wrong_git_digest(path: Path, expected: tuple[int, ...]) -> str:
            digest = original(path, expected)
            return "0" * 64 if path == runtime.executable else digest

        with mock.patch.object(
            isolated, "_hash_git_executable", side_effect=wrong_git_digest
        ):
            with self.assertRaisesRegex(
                isolated.IntakeError,
                "Git executable content changed during capability probe",
            ):
                isolated._verify_git_lazy_fetch_guard(layout)

    def test_probe_rejects_upload_pack_digest_mismatch_after_differential(self) -> None:
        isolated = load_locator_module("helper_digest_mismatch")
        layout = isolated._repository_layout(self.fixture.repo)
        runtime = isolated._resolve_git_runtime()
        original = isolated._hash_git_executable

        def wrong_helper_digest(path: Path, expected: tuple[int, ...]) -> str:
            digest = original(path, expected)
            return "0" * 64 if path == runtime.upload_pack_target else digest

        with mock.patch.object(
            isolated, "_hash_git_executable", side_effect=wrong_helper_digest
        ):
            with self.assertRaisesRegex(
                isolated.IntakeError,
                "Git helper content changed during capability probe",
            ):
                isolated._verify_git_lazy_fetch_guard(layout)

    def test_executable_hash_detects_content_drift_with_fixed_stat_oracle(self) -> None:
        executable = self.root / "hash-oracle-executable"
        executable.write_bytes(b"#!/bin/sh\nexit 0\n")
        executable.chmod(0o755)
        signature = MODULE._git_stat_signature(executable)
        original_digest = MODULE._hash_git_executable(executable, signature)
        replacement = b"#!/bin/sh\nexit 9\n"
        self.assertEqual(len(replacement), signature[5])
        executable.write_bytes(replacement)
        executable.chmod(0o755)
        opened = mock.Mock(
            st_dev=signature[0],
            st_ino=signature[1],
            st_mode=signature[2],
            st_uid=signature[3],
            st_gid=signature[4],
            st_size=signature[5],
            st_mtime_ns=signature[6],
            st_ctime_ns=signature[7],
        )
        with mock.patch.object(
            MODULE, "_git_stat_signature", return_value=signature
        ), mock.patch.object(MODULE.os, "fstat", return_value=opened):
            replacement_digest = MODULE._hash_git_executable(executable, signature)
        self.assertNotEqual(replacement_digest, original_digest)

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
                    "GIT_ALLOW_PROTOCOL",
                    "GIT_ATTR_NOSYSTEM",
                    "GIT_NO_LAZY_FETCH",
                    "GIT_NO_REPLACE_OBJECTS",
                    "GIT_OPTIONAL_LOCKS",
                    "GIT_PROTOCOL_FROM_USER",
                    "GIT_TERMINAL_PROMPT",
                },
            )
            self.assertEqual(git_env["GIT_NO_LAZY_FETCH"], "1")
            argv = MODULE._git_argv(
                Path("/validated/repo"), "cat-file", "blob", "abc"
            )
            self.assertTrue(Path(argv[0]).is_absolute())
            self.assertEqual(Path(argv[0]), Path(argv[0]).resolve(strict=True))
            self.assertEqual(
                argv[1:3],
                ["--no-pager", "--no-replace-objects"],
            )
            if MODULE._resolve_git_runtime().use_no_lazy_fetch_flag:
                self.assertIn("--no-lazy-fetch", argv)
            else:
                self.assertNotIn("--no-lazy-fetch", argv)
            self.assertEqual(
                MODULE._repository_root(self.fixture.repo),
                self.fixture.repo.resolve(strict=True),
            )
            validated = MODULE.validate_payload(self.fixture.repo, self.fixture.spec)
        self.assertEqual(validated.spec.payload_commit, self.fixture.payload[0])

    def test_git_environment_drops_process_injection_variables(self) -> None:
        injected = {
            "LD_PRELOAD": "/attacker/preload.so",
            "LD_LIBRARY_PATH": "/attacker/lib",
            "BASH_ENV": "/attacker/bash-env",
            "ENV": "/attacker/sh-env",
            "PYTHONPATH": "/attacker/python",
            "CDPATH": "/attacker/cdpath",
            "IFS": "x",
            "PATH": "/attacker/bin",
            "HOME": "/attacker/home",
            "XDG_CONFIG_HOME": "/attacker/xdg",
            "HTTP_PROXY": "http://attacker.invalid",
            "HTTPS_PROXY": "http://attacker.invalid",
            "ALL_PROXY": "socks5://attacker.invalid",
            "NO_PROXY": "*",
            "SSH_AUTH_SOCK": "/attacker/agent.sock",
            "GIT_SSH": "/attacker/ssh",
            "GIT_ASKPASS": "/attacker/askpass",
            "SSH_ASKPASS": "/attacker/ssh-askpass",
            "GIT_EDITOR": "/attacker/editor",
            "GIT_PAGER": "/attacker/pager",
            "PAGER": "/attacker/pager",
            "TMPDIR": "/attacker/tmpdir",
            "TEMP": "/attacker/temp",
            "TMP": "/attacker/tmp",
        }
        with mock.patch.dict(os.environ, injected, clear=False):
            git_env = MODULE._git_environment()
        self.assertEqual(git_env["PATH"], os.defpath)
        self.assertEqual(git_env["LC_ALL"], "C")
        for variable in injected:
            if variable != "PATH":
                self.assertNotIn(variable, git_env)

    def test_temporary_probe_skips_invalid_first_candidate_for_safe_later_one(self) -> None:
        missing = self.root / "missing-temp-parent"
        safe = self.root / "safe-temp-parent"
        safe.mkdir()
        old_tmpdir = tempfile.tempdir
        tempfile.tempdir = None
        try:
            with mock.patch.dict(
                os.environ,
                {
                    "TMPDIR": str(missing),
                    "TEMP": str(safe),
                    "TMP": str(safe),
                },
                clear=False,
            ):
                isolated = load_locator_module("temp_candidate_fallback")
                validated = isolated.validate_payload(
                    self.fixture.repo, self.fixture.spec
                )
        finally:
            tempfile.tempdir = old_tmpdir
        self.assertEqual(validated.spec.payload_commit, self.fixture.payload[0])
        self.assertFalse(missing.exists())
        self.assertEqual(list(safe.iterdir()), [])

    def test_bound_git_environment_pins_its_helper_directory(self) -> None:
        runtime = MODULE._resolve_git_runtime()
        try:
            git_env = MODULE._git_environment(runtime=runtime)
        except TypeError as exc:
            self.fail(f"bound Git helper environment is unavailable: {exc}")
        self.assertEqual(git_env["GIT_EXEC_PATH"], str(runtime.exec_path))
        self.assertEqual(git_env["PATH"].split(":"), [str(runtime.exec_path), "/usr/bin", "/bin"])
        self.assertEqual(git_env["GIT_ALLOW_PROTOCOL"], "none")

    def test_production_git_argv_denies_transports_hooks_and_maintenance(self) -> None:
        argv = MODULE._git_argv(
            Path("/validated/repo"), "cat-file", "blob", "0" * 40
        )
        required_pairs = {
            ("protocol.allow", "never"),
            ("core.hooksPath", os.devnull),
            ("maintenance.auto", "false"),
            ("maintenance.autoDetach", "false"),
            ("gc.auto", "0"),
            ("fetch.writeCommitGraph", "false"),
        }
        observed_pairs = {
            tuple(argv[index + 1].split("=", 1))
            for index, value in enumerate(argv[:-1])
            if value == "-c" and "=" in argv[index + 1]
        }
        self.assertTrue(required_pairs.issubset(observed_pairs))
        self.assertIn("--no-pager", argv)

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

    def test_first_capability_probe_never_writes_to_protected_ambient_tmp(self) -> None:
        before = self.regular_file_inventory(self.fixture.repo)
        old_tmpdir = tempfile.tempdir
        tempfile.tempdir = None
        try:
            with mock.patch.dict(
                os.environ,
                {
                    "TMPDIR": str(self.fixture.repo),
                    "TEMP": str(self.fixture.repo),
                    "TMP": str(self.fixture.repo),
                },
                clear=False,
            ):
                isolated = load_locator_module("protected_ambient_probe")
                with self.assertRaisesRegex(
                    isolated.IntakeError, "inside source repository"
                ):
                    isolated.validate_payload(self.fixture.repo, self.fixture.spec)
        finally:
            tempfile.tempdir = old_tmpdir
        self.assertEqual(self.regular_file_inventory(self.fixture.repo), before)


if __name__ == "__main__":
    unittest.main()
