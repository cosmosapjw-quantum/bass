# BASS PR automatic commit/push policy

Effective 2026-08-18.

For every subsequent BASS PR-level task, the agent should perform the following without requiring a separate commit/push instruction:

1. create or reuse the PR-specific branch;
2. execute the scoped scientific/code verification gates;
3. commit completed reviewable changes and evidence;
4. push the branch normally (never force-push unless explicitly approved);
5. create the PR when it becomes reviewable, or update the existing PR automatically;
6. fetch/verify the remote branch or PR head SHA before reporting completion;
7. preserve failure evidence when a gate fails instead of silently dropping it.

## Merge boundary

Automatic commit/push **does not imply automatic merge**.

- `main` or another integration branch is merged only after explicit user approval unless the user later changes this policy.
- Failed or partially verified scientific claims must remain clearly scoped in the PR description/receipts.
- Production migration remains separately gated from research/reference PRs.

## Commit granularity

Prefer one coherent commit per independently reviewable task when the available Git interface permits it. Multiple ordinary commits inside one PR are acceptable when connector/API constraints make atomic multi-file commits impractical.

## Amendment 2026-11-01: portfolio direction and scientific progress

This amendment is reviewed as a separate Draft PR and has no effect on historical user-owned physics sources or production until the amendment is accepted. The existing automatic commit/push permission and explicit no-auto-merge boundary remain unchanged.

1. **Keep distinct authorities.** The repo root DAG.json is an ACCEL02 R/C execution DAG, NOT the 15-node BASS physics upper DAG. Use docs/development/BASS_PHYSICS_UPPER_DAG_20261101.json for physics routing; historical remaining DAG, REI 28/88 and VigilODE 7/23 have independent denominators. Never add R/C stages, plots, source files, PRs or backup copies as upper scientific nodes.
2. **Objective before next letter.** Each research PR identifies (a) source-owned physical question, (b) one falsifiable result or obstruction, (c) which original upper dependency or observable it advances, (d) why this is preferable to the shortest currently executable critical-path step. Exploration remains permitted when explicitly labeled exploratory/reference.
3. **Admission accounting.** Report source-mapped, scoped physical success, fully closed physical node, and production/observational validation separately. A scoped COMPLETE with a PARTIAL parent must name the narrower source/domain witness and may not imply the parent is complete. Keep 9/15 qualified rather than portraying it as 60% fully completed physics; do not invent a full completion denominator.
4. **Stall trigger, not another gate.** Three consecutive same-lane scoped-only PRs with zero upper closure, zero actual blocker removal and no discriminating observable should interrupt *automatic adjacent subletter selection*. In the next decision choose an available upper-critical-path physical calculation, or record a concise reason for an exploratory exception. Do not multiply audits, freeze good physics or require permanent approval.
5. **Source identity and scientific output.** Every PR closeout supplies a source/parent commit, input owner and typed identity, actual NEW vs reused/model rows, observed numerical/analytic result, claim ceiling and next incomplete physical obligation. Report numerical identity separately from immutable byte identity. Do not borrow success from another RHS, screen, closure, owner, or provider.
6. **Lean verification and checkpoint.** Reuse previously verified immutable data; one targeted test plus at most one risk-justified independent hostile check is usually enough. Checkpoint before expensive work and at the usable end; S0/S1/S2, full CI reruns and dual-provider readback are evidence options, not a new mandatory ceremonial loop. Report provider ACK and readback separately.
7. **Stacked PR hygiene.** Do not replace an owning physics PR with a packaging-only successor. Keep one branch per substantive science owner when feasible, apply lower-layer fixes at their owner, and distinguish Draft/open/unmerged from adopted integration. Before a new same-lane PR, read its actual parent/head and open blockers. Merge and production authority still require explicit user approval.
8. **Progress-first termination.** After two process-only no-progress iterations, stop the meta-work and return to the smallest safe scientific operation or checkpoint. Do not claim new physics when only documents, DAG counters, software performance, or backups changed.

The 2026-08-21 architecture realignment remains an independent core production authority: Type-II reference, VI0 manifold classification, preflight and Join J1. This amendment does not silently mark these finished.
