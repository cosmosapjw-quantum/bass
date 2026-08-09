# Artifact and provenance policy

Every material input and output receives a stable ID, byte size, SHA-256, producer,
source commit or archive identity, honest timestamp/date precision, governing gate and
obligation IDs, and artifact state. Logs store argv, working directory, environment,
start/end, exit code, signal/timeout/skip/fallback state, and stdout/stderr.

A PASS is a non-circular graph:

1. current governing inputs and status-free gate/node projections;
2. `bass.producer_evidence/v2` with a canonical governing fingerprint;
3. `bass.review_attestation/v2` from a different run/assignment/lane;
4. `bass.gate_receipt/v2` binding both records and dependency receipts;
5. PASS pointers in DAG/gate state;
6. final whole-tree SHA-256 manifest and a live validator run.

For H0/H1, `bass.static_check_log/v2` additionally embeds the exact governing snapshot
both immediately before and immediately after command execution. Both snapshots must be
identical to each other and to the producer record's current governing snapshot. Any
governed-byte change therefore requires a new command run, not merely a new receipt.
The log also binds an immutable, shell-free argv/cwd plan and its canonical SHA-256.
Validation reconstructs that plan and checks result-specific output oracles (input hashes,
archive reports, Rust signature/key, repository pins, and the complete H1 test roster);
matching command IDs or exit codes alone never establish PASS.
The sealed H0/H1 execution context is intentionally bound to the current harness root,
its workspace parent, and the resolved validator Python executable. Relocating the
harness or changing that runtime requires fresh H0/H1 runs and receipts; historical logs
cannot silently validate commands executed against another tree.
For the six live JSON state files, the governing fingerprint also binds an immutable
projection: IDs, questions, names, dependencies, criteria, transition rules, and field
schemas remain sealed while only typed status/value/receipt/authorization fields evolve.

The whole-tree manifest excludes only itself, archives, VCS/cache files, and never makes a
stale receipt fresh. Receipt freshness comes from the gate-specific governing fingerprint.
A transcript statement without a durable hashed record is `TRANSCRIPT_ONLY` and is not
inherited after interruption.

OD001–OD004 resolution also requires `bass.owner_decision_receipt/v1`, whose canonical
decision-snapshot hash is bound by an exact path/bytes/SHA-256 file reference. It confirms
the four values only and never grants read, write, build, execution, or install authority.
Read-only code intake then requires a separate `bass.code_read_authorization/v1` bound to
that exact receipt and a reviewed OD0 gate receipt. It grants only
`READ_CANONICAL_SOLVER_CODE` and is not an implementation or execution authorization.

Historical facts about solver execution, solver modification, or external-oracle
execution are derived only from registered `bass.activity_receipt/v1` records. Each such
record must bind a prior explicit `bass.action_authorization/v1`, clean producer evidence,
and an independent PASS review in timestamp order. Current phase authorization bits are
permissions, not proof that an activity occurred; clearing them during remediation does
not erase already registered, hash-bound activity history. Generic producer evidence or a
gate receipt cannot be substituted for an activity receipt.

The three Markdown files under `state/` are immutable bootstrap-history snapshots in the
standalone pre-code package. They are H1-governed and must not be appended in place;
post-transplant operational history is carried by fresh node evidence and receipts.

Archives are listed and audited before extraction. Reject absolute paths, traversal,
backslashes, control characters, duplicates, symlinks, devices, special files, and
unbounded entry counts or expansion. Never extract an untrusted archive over a canonical
source tree.
