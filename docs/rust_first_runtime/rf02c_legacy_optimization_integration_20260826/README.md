# RF-02C / Legacy Optimization Integration Package

Status: `PLANNING PACKAGE / CURRENT ACTION BASS-11 / NO RUNTIME MUTATION / DRAFT UNMERGED`

This directory compiles the already-approved BASS-11 → BASS-15 integration
path into a small machine-readable execution package.

The package follows the existing BASS conventions:

- `CURRENT_STATE.json` resolves current remote, reported-local, legacy, and
  Atlassian state.
- `WORK_UNITS.json` is the executable DAG and mutation boundary.
- `ACCEPTANCE_MATRIX.json` separates identity, code, physics, numerical,
  native, performance, integration, and claim gates.
- `IMPLEMENTATION_PLAN.md` is the human execution plan.
- `CODEX_HANDOFF.md` executes exactly the current node, BASS-11.
- `validate_package.py` checks manifest integrity, schemas, the DAG, one-next
  action, dependency predicates, and optional live Git ancestry.

## Governing boundary

Actual engineering progress has priority over optional assurance. Each
implementation stage gets targeted falsification checks, one bounded review,
and at most one reproduced P0/P1 repair. Unchanged PASS evidence is reused.

The legacy optimization lane is `EXPLORATORY / NONAUTHORITATIVE`. An accepted
legacy candidate is never cherry-picked directly into RF-02C by ancestry. It
must pass the read-only BASS-13 adoption gate, be reimplemented from the frozen
RF-02C head in BASS-14, and be requalified on RF-02C in BASS-15.

The formula SSOT remains formula-only: solver construction, numerical
evolution, optimization, likelihood, and inference are outside its theorem
scope.

## Validate

```bash
cd docs/rust_first_runtime/rf02c_legacy_optimization_integration_20260826
sha256sum -c MANIFEST.sha256
python validate_package.py
python validate_package.py --live
```

`--live` accepts the recorded RF-02C pre-closeout commit as an ancestor of the
live remote branch, so the package remains valid after BASS-11 advances that
branch by ordinary fast-forward.

## Exactly one next action

Execute `CODEX_HANDOFF.md` in the existing dirty RF-02C worktree. Commit only
the already-generated evidence/native-delta bytes as the authorized third
commit, push, open the stacked draft RF-02C PR, and read back exact remote
identity. Do not start BASS-13, BASS-14, or BASS-15 in the same run.
