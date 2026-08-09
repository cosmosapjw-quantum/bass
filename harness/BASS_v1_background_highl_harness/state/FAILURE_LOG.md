# Failure log

## F-001 — Legacy automation false verifier

The uploaded low-ell automation scaffold can emit hard-coded successful checks and its
runner does not implement the lifecycle advertised by its README. It is quarantined.

## F-002 — Generic harness overlay collision

The research and coding ZIPs share root paths with different contents. Direct extraction
would silently replace policy and manifest files. Direct overlay is forbidden.

## F-003 — Uploaded restore bootstrap is not an installer

The supplied bootstrap mutates system Python, installs unpinned packages, builds code,
and runs incomplete tests from a different snapshot. It was not executed and is excluded.

## F-004 — First H1 evidence-capture import failure

The first v2 H1 capture attempt invoked ten named tests as `test_harness_tools.*` from the
harness root, where that module name was not importable. The command exited 1 and was not
accepted as evidence. The tests directory was made an explicit package and the runner now
uses `tests.test_harness_tools.*`; H1 evidence was recaptured from a fresh run.

## F-005 — First isolated GPG recapture lacked a home directory

The first strengthened H0 capture passed hash/archive/repository checks but its isolated
GPG import exited 2 because the temporary `--homedir` did not yet exist. No H0 receipt was
issued from that run. The capture runner now creates the isolated directory with mode 0700
before import and recaptures the complete H0 log from scratch.

## F-006 — GPG import tried to start an unavailable agent

After creating the isolated home, the public key imported but `gpg` returned 2 while
trying to start `gpg-agent`; that run also issued no receipt. The final read-only path
uses `gpg --dearmor`, `gpg --show-keys --fingerprint`, and `gpgv --keyring`, which require
no agent and still verify the exact detached signature against the exact tarball.

## F-007 — Key display attempted the read-only default GPG home

The next recapture reached detached verification but `gpg --show-keys` attempted to create
the default `/root/.gnupg` and exited 2. No receipt was issued. The fingerprint command now
uses the existing isolated 0700 home with `--no-autostart`; verification remains `gpgv`.

## F-008 — Instruction files escaped the first H1 fingerprint

The first exact-path payload allowlist rejected new solver files but did not bind allowed
instruction files. Re-manifested edits to `AGENTS.md`, `START_HERE.md`, and the executor
prompt incorrectly survived validation. The final H1/OD0 governing set seals every
immutable instruction, policy, prompt, tool, test, and bootstrap-history file.

## F-009 — A past PASS static log could be reissued

The initial static log did not identify the governing bytes present when commands ran, so
old command results could be wrapped in fresh evidence after a tool/test change. Static
log v2 now records identical pre/post governing snapshots; producer issuance and live
validation both require exact equality with the current fingerprint.

## F-010 — Live state mixed mutable values with mutable instructions

Six JSON files must change as the DAG advances, but their first treatment left decision
questions, transition rules, node names, gate criteria, claim topology, and a free-form
resume instruction outside H1. The final fingerprint binds immutable projections of those
files, replaces run-state prose with validated machine codes, and leaves only typed
status/value/receipt/authorization values mutable.

## F-011 — Command IDs could disguise a no-op execution plan

The first independent-rerun design required distinct logs and exact command IDs but did
not reconstruct argv/cwd. A hand-authored log could therefore label `/bin/true` as every
expected command. Static log v2 now binds a canonical shell-free plan fingerprint, the
exact current harness/workspace/runtime context, and command-specific semantic outputs.
Producer issuance, review issuance, and live validation all enforce the same plan.

## F-012 — Generic evidence could manufacture cumulative activity history

The initial run-state projection derived execution/modification flags from lists of
generic producer or gate receipts. Those records did not prove the named activity or its
authorization at the time. The registry now accepts only dedicated activity receipts
that bind exact action authorization, prerequisite PASS receipts, approved plan,
full producer evidence, independent review, and a monotonic authorization-to-review
timeline. Durable activity receipt files and registry entries must cover each other
exactly.
