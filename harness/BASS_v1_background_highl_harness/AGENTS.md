# BASS v1.0 agent rules

## Mission and current phase

Build and validate BASS v1.0 as an Einstein--Boltzmann solver for exact/nonlinear,
spatially homogeneous Bianchi backgrounds with a convergence-controlled finite angular
hierarchy. The packaged initial phase is `USER_SCOPE_CONFIRMATION`. The authoritative
live phase exists only in `contracts/scope_lock.json` and `state/run_state.json`; never
infer it from this prose. No phase may authorize solver implementation before `IA0`.

## Read first

Before substantive work, read the contract/state files listed in `START_HERE.md`.
More specific `AGENTS.md` files may add constraints but may not weaken the root scope
lock, convention lock, claim firewall, or write boundaries.

## Hard scope firewall

- Spatial perturbations and their `k`-mode, SVT, gauge, primordial-spectrum,
  transfer-function, perturbative LoS, stochastic covariance, likelihood, posterior,
  and real-data paths are outside v1.0.
- High ell means angular resolution of a homogeneous radiation distribution. It does
  not mean spatial perturbations.
- Exact/nonperturbative describes background amplitude and equations. Finite
  `ell_max`, time stepping, energy/angular quadrature, and closure are numerical
  approximations and require convergence evidence.
- Global tilt, if enabled by owner decision, is forward background/electron-frame
  physics. A local observer boost is output-only and may never replace it.
- `bianchi_phase_r` is a pinned, read-only external oracle lane, not a production
  dependency and not automatically independent evidence.

## Authorization locks

Read `contracts/scope_lock.json` and `contracts/state_machine.json` before every transition.
Code read, code write, solver build, solver execution, dependency installation, external
oracle execution, external writes, GitHub writes, and public release are separate locks.
An authorization never implies another one. Harness-only static validation and read-only
inspection of the already named setup inputs are allowed in the current phase.

## Evidence and state

- Documentation, comments, names, and test counts are claims, not implementation proof.
- Every PASS needs fresh v2 producer evidence, a different-lane review attestation, and a
  gate receipt binding the governing fingerprint, dependencies, criteria, obligations,
  logs, artifacts, and claim effects.
- H0/H1 static logs must bind both their pre- and post-execution governing snapshots to
  the current bytes. A past PASS log cannot be reused after any governed instruction,
  policy, prompt, tool, or test changes.
- Use gate states `NOT_RUN`, `PASS`, `FAIL`, `BLOCKED`, `NOT_APPLICABLE` only.
- Use artifact states `DURABLE_VERIFIED`, `DURABLE_UNVERIFIED`, `TRANSCRIPT_ONLY`,
  `MISSING`, `INVALIDATED` only.
- A timeout, skipped tool, empty output, fallback outside its regime, NaN/Inf, or
  partial transcript is never `PASS`.
- A governing fingerprint mismatch makes the PASS stale. Run the transitive invalidation
  tool, preserve old evidence, and re-run from the first affected gate.
- `state/DECISION_LOG.md`, `state/EVIDENCE_LEDGER.md`, and `state/FAILURE_LOG.md` in this
  standalone package are sealed bootstrap-history snapshots, not append targets. Later
  operational state belongs in node evidence/receipts after the harness is transplanted.

## Scientific validation order

For an authorized change: syntax/import -> targeted software test -> equation-to-code
map -> exact identity/invariant -> analytic or symmetry limit -> resolution/tolerance
convergence -> cross-backend equivalence -> independent review. A smoke test cannot
replace a scientific gate.

## Multi-agent discipline

Delegate only bounded, independent lanes. One coordinator owns canonical state and
shared files. Producers and blocking-gate reviewers must have different assignment/run
identities and review the same pinned inputs. Parallel writers may not touch the same
files. After a reviewed change, the relevant review is stale until repeated.

## Stop rules

Work one DAG node at a time. Code intake authorization (`OD0`) and implementation/build/
execute authorization (`IA0`) are separate owner gates. A node may receive at most two repair iterations per
failure class. Then mark it `BLOCKED`, preserve evidence, and ask the user. Stop for any
owner decision, convention/baseline/tolerance change, production dependency, external
write, destructive action, or material scope expansion.

## Completion reporting

Report the current DAG node, what actually changed, exact checks run, receipts/artifacts,
scientific claims promoted or still locked, blockers, and one next step. Never report a
percentage in place of requirement-level evidence.
