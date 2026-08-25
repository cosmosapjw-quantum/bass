# Codex handoff — RF-02C only

Continue BASS from draft branch
`agent/audit/science-system-differential-20260826-r1`.
Do not restart recovery or any closed RF node.

Current verdict:

- RF-02A detector repair: scoped PASS.
- RF-02B pointwise parity: development-mode code-contract PASS.
- RF-02B default verified production dispatch: BLOCKED.
- Science/formula/performance/legacy/production states remain separate as recorded.

Before editing, verify `MANIFEST.sha256` and run the sole command in
`WORK_UNITS.json#/package_validation`. Then read:

1. `CURRENT_STATE.json`
2. `AUDIT.json`
3. `WORK_UNITS.json#/work_units[id=RF-02C]`

Execute exactly RF-02C from that object, including its ordered pre-solver
provenance, public-route, receipt, and projection repairs. Reuse unchanged
receipts only through the registry predicates. Do not run inherited PASS
lanes, the full suite, Wolfram, timing, GPU, RF-03+, or merge/promotion work.

Stop rather than guess if a scientific authority choice is unresolved.
Push only one stacked draft RF-02C PR after its targeted proof and one fresh
review. Exactly one successor after RF-02C closes: RF-03.

