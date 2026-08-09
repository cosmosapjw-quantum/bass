# Evidence ledger

| Evidence ID | Relation | Durable status | Location |
|---|---|---|---|
| EV-HARNESS-RESEARCH | contextual/limited | DURABLE_VERIFIED | `audit/INPUT_INVENTORY.json` |
| EV-HARNESS-CODING | contextual/limited | DURABLE_VERIFIED | `audit/INPUT_INVENTORY.json` |
| EV-LOWELL-PROTOCOLS | contextual/contradicts-scope | DURABLE_VERIFIED | `audit/INPUT_INVENTORY.json` |
| EV-AUTOMATION-KIT | contradicts-safe-install | DURABLE_VERIFIED | `docs/HARNESS_AUDIT_REPORT.md` |
| EV-RUST-1.94.1 | supports-authenticity-only | DURABLE_VERIFIED | `audit/TOOLCHAIN_STATUS.md` |
| EV-RUSTCORE-PARTIAL | contextual/unverified-provenance | DURABLE_UNVERIFIED | `audit/TOOLCHAIN_STATUS.md` |
| EV-PHASE-R | contextual/external-oracle-only | DURABLE_VERIFIED | `audit/REPO_ORACLE_SNAPSHOT.md` |
| EV-H1-INSTRUCTION-HOSTILE | instruction mutation / old-log reuse negatives | DURABLE_VERIFIED | `tests/test_harness_tools.py` |
| EV-OD0-TRANSITION-HOSTILE | full decision/auth/evidence transition fixture | DURABLE_VERIFIED | `tests/test_harness_tools.py` |
| EV-H1-STATIC-PLAN-HOSTILE | no-op/alternate-root command-plan negatives | DURABLE_VERIFIED | `tests/test_harness_tools.py` |
| EV-ACTIVITY-HISTORY-HOSTILE | generic/minimal activity-evidence negatives | DURABLE_VERIFIED | `tests/test_harness_tools.py` |
