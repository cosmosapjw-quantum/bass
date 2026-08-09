# Independent H1 hostile harness review

- Verdict: PASS
- Blocking findings: 0
- Reviewer run: `dirac-h1-hostile-review-20260802`
- Reviewer assignment: `final-exact-byte-h1-hostile-review`
- Reviewer lane: `independent-harness-audit-dirac`
- Producer evidence: `evidence/E-H1-20260801-V2.json`
- Producer evidence physical SHA-256: `abc76be9280be10ad33351348cf3af58e5ca26ba4bcfe34e1bd17b66bf82b456`
- Producer evidence canonical fingerprint: `e8221bb7f7651ce27658eb2a4f7f50af3fa3df5ab7ac32f169872dad61c8739d`
- Governing fingerprint: `19b86bc8f99149215e998eb3071707a06ccdf87072fae2909bf450aa287f6074`
- Producer static-log SHA-256: `3eb153f9e6de946113d12159dd45ac0d9dffec1c768593bf736c1dc1a9b6156d`
- Bundled reviewer static-log SHA-256: `7fce9f2483f738611743911f992d0250bdcb2763e2636f2ef8f3ea6529c1ecc4`
- Reviewer-owned post-submission rerun SHA-256: `6e196a4a53e6f5536ccdbacdd76d7f73cc5f3cedfd43db3a61bebb8c112a03d2`

The reviewer independently recomputed the producer physical/canonical/governing hashes,
all 53 immutable governing file references, all six live-state immutable projections,
and the complete H0 dependency graph. The reviewer-owned execution ran after producer
submission from `2026-08-02T02:09:43.226016+09:00` through
`2026-08-02T02:09:47.909112+09:00`. Its pre/post governing snapshots were identical,
all three exact canonical argv/cwd commands were clean PASS, all 37 declared hostile
tests passed in 4.410 seconds, and the current semantic validator returned zero errors.
The bundled reviewer execution is also post-submission and has a distinct hash from the
producer static log.

The negative matrix covers archive traversal, exact-path and executable/binary injection,
minimal/forged receipts, blocked-gate claim promotion, instruction mutation, stale-log
reissuance, governing-profile and coordinated science-contract weakening, high-ell and
massless-neutrino drift, owner receipt/code-read binding, valid and invalid OD0 transitions,
transitive invalidation/remediation, free-form run-state injection, canonical command-plan
replacement, alternate execution roots, generic activity-evidence reuse, and minimal
nested activity evidence. The positive fixtures also demonstrate the full H1 and OD0
producer-review-receipt paths without solver code.

No solver or oracle activity is present: code roots are empty; code read/write, build,
execute, install, oracle, remote-write, GitHub-write, and release authorizations are false;
all three cumulative activity registries are empty; and scientific/runtime/release claims
remain locked. H1 therefore supports only harness structure, static tools, and fail-closed
evidence behavior.

Explicit boundary: the test harness can verify current packaged bytes and execution
records, but it cannot establish methodological independence against an actor who can
replace every governed byte and obtain a new trusted external review. Relocation or Python
runtime replacement requires fresh H0/H1 evidence. Solver, physics, numerical, family,
backend, and release correctness were not tested or claimed.
