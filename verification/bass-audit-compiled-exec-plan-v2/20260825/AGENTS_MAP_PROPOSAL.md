# Proposed short AGENTS map

Keep root `AGENTS.md` short. It should point agents to:

- `docs/quality/P0_P1_POLICY.md`
- `verification/audit-compiled/ACTIVE_PR_CONTRACT.json`
- `docs/exec-plans/active/`
- `scripts/verify_artifact_identity.py`
- `scripts/verify_allowed_diff.py`
- the task-specific evidence directory

It should state only these hard rules: read the active contract; run the exact gates; do not guess across a spec boundary; do not mutate scientific references to pass tests; stop on P0/P1 or missing evidence. Detailed scientific and execution contracts remain in structured files, not in a monolithic `AGENTS.md`.
