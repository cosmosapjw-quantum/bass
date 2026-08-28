# Codex Handoff — RF-03 Authority Resolution and Immediate Resume

## Immutable entry

```text
repository:       cosmosapjw-quantum/bass
base branch:      agent/architecture/rust-first-rf02c-20260826-r1
base HEAD:        dfa17457d402bd441d3fdf786c2d79c529512ee5
base tree:        9fc67fb0ba10e091e25a14d7e1fac88b77a0241e
R1 package HEAD:  b7cda09d337906c17821a2b815032c985ff86bdf
implementation:   agent/architecture/rust-first-rf03-20260828-r2
next action:      RF03-AUTH-01
claim now:        NO PASS_RF03 CLAIM
```

Use a separate worktree. Do not mutate `main`, PR #36, or PR #37. Do not use
BASS-12 through BASS-15 optimization bytes.

## Re-adjudication

The prior stop was correct under the R1 wording, but the source itself already
contains the required production matter model:

```text
model_id = explicit_gamma_law_tilted_perfect_fluid_v1
p = (gamma - 1) rho
gamma is explicit caller input
state = [Omega, v1, v2, v3]
force = TiltedFluid.rhs(...)
```

Do not add a new EOS. Reject only missing/unknown-model hard-coded `w`, hidden
default `gamma`, Python fallback, or surrogate substitution.

The source does not define a tilted-temperature law. Do not create a Gamma
exponent or couple `T_gamma` into the force/JVP. Treat `T_gamma` as exogenous
context and add a metamorphic test proving invariance.

## Execute

1. Fetch and verify the immutable base and this package manifest.
2. Create `agent/architecture/rust-first-rf03-20260828-r2` from the exact base.
3. Inspect `/tmp/bass-rf03-20260828.4M5fCz/worktree/artifacts/rust_first_runtime/rf03/SCHEMA_AND_ROUTE_FREEZE.json` if it still exists. Copy its hash-bound content into the authority receipt. If absent, record `ORIGINAL_LOCAL_BLOCKER_ARTIFACT_UNAVAILABLE` and use `AUTHORITY_CONTRACT.json`; absence is not a scientific blocker.
4. Land only these authority paths first:

```text
provenance/authority/rf03/RF03_AUTHORITY.json
tools/authority/verify_thermodynamics_authority.py
tests/rf03/test_authority_contract.py
artifacts/rust_first_runtime/rf03/authority/**
```

5. The verifier must fail closed unless it proves:
   - exact source blob identities;
   - explicit model id and caller-supplied gamma;
   - state order `[Omega,v1,v2,v3]`;
   - force/JVP use the same source model at fixed context;
   - no hidden constant-w/Python/surrogate fallback;
   - `T_gamma` does not affect force/JVP;
   - historical Type-II fixtures remain surrogate-only.
6. Run the authority verifier and focused test. Only then record `PASS_RF03_AUTHORITY`.
7. In the same run, write genuine failing RF-03 tests against this frozen contract. Do not stop at documents or scaffolding.
8. Implement the unaffected R1 RF-03 scope plus this override. Preserve equations, state order, tolerances, restart/history semantics, RF-02C routing, and fail-closed policy.
9. Run targeted parity/domain/determinism tests; four bounded figures; hostile mutations; PHYS-MATH and PHYS-MATH-CODE audits; at most one bounded repair pass.
10. Build reproducible native wheel/content-addressed delta, bind terminal evidence to the exact source commit, push a draft implementation PR, and stop. Do not merge or mark ready.

## Required terminal report

```text
STATUS
ACTUAL PROGRESS
VERIFIED
DEFERRED
BLOCKERS
NEXT
```

Allowed terminal claims are `PASS_RF03_AUTHORITY` for the authority node and
`PASS_RF03` only after the complete implementation/evidence gates. No
performance or scientific promotion is authorized.
