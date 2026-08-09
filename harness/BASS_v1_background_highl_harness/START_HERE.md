# Start here

1. Read `AGENTS.md`.
2. Read, in order:
   - `contracts/scope_lock.json`
   - `contracts/state_machine.json`
   - `contracts/evidence_contract.json`
   - `contracts/owner_decisions.json`
   - `contracts/conventions.json`
   - `contracts/scientific_contract.json`
   - `contracts/family_registry.json`
   - `contracts/high_ell_acceptance.json`
   - `state/run_state.json`
   - `state/dag.json`
3. Run `python3 tools/validate_harness.py` from this directory. Treat
   `contracts/scope_lock.json` plus `state/run_state.json` as the only live phase source;
   `manifest.json` records the packaged initial phase only.
4. Do not ingest or inspect solver code until the user supplies it and closes the
   decisions in `docs/OWNER_DECISIONS_REQUIRED.md`.
5. At code intake, use `prompts/01_CODE_INTAKE_AUDIT.md`. That phase is read-only.
6. Implementation, build, execution, and installation remain independently closed until
   the user explicitly authorizes them at `IA0` after the read-only intake/reality audit.

Closing OD001--OD004 creates only the exact owner-decision receipt. Enabling code read is
a second explicit action recorded in `receipts/OD0_CODE_READ_AUTHORIZATION.json` and the
OD0 gate receipt; neither record grants write, build, execution, install, oracle, remote,
GitHub, or release authority.

Later solver modification/execution or pinned-oracle execution becomes historical fact
only through a dedicated activity receipt bound to a prior explicit action authorization,
producer evidence, and independent review. A live authorization bit alone is never proof
that the action occurred.

A passing harness check also proves that current H0/H1 PASS pointers resolve to fresh v2
evidence and independent review records. It never promotes a solver, scientific,
numerical, family-coverage, or release claim.
