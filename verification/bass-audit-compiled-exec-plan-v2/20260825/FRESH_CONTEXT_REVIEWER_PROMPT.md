# Fresh-context reviewer prompt — BASS-AC-01

Start in a new session with no implementer conversation history. Review only; do not edit files.

Inputs:
- exact base SHA
- final SHA
- full diff
- `PR_CONTRACTS/BASS-AC-01.json`
- raw verification logs
- machine receipt JSON

Do not trust the implementer summary. Reconstruct behavior from the diff, repository, tests, and logs.

Return JSON only:

```json
{
  "verdict": "PASS|FAIL_P0_P1|BLOCKED_BY_MISSING_EVIDENCE",
  "P0": [],
  "P1": [],
  "P2": [],
  "P3": [],
  "evidence_complete": true,
  "reviewer_did_not_modify": true
}
```

Every finding must include exact file:line, violated invariant, reproducer, and evidence. First pass must not fix code. Pass only when P0=0, P1=0, evidence is complete, and the reviewer made no modifications.
