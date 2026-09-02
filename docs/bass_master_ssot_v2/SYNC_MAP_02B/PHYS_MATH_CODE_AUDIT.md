# SYNC-MAP-02B PHYS–MATH–CODE audit

## Reconstructed code path

```text
BASS PR #93 semantic export (14 geometry formulas)
  + active REC PR #47 exact source blobs
    -> RECRelationClassification.wl
       - relation registry
       - shared-owner export-gap registry
       - exact algebraic relation oracle
       - formal-oracle split
       - BASS-14 relation matrix
       - proposal-only impact DAG
    -> RECRelationClassificationValidationFix1.wl
       - computed rather than declared residuals
       - sign/coefficient hostile mutations
       - exact DAG endpoint closure
    -> SYNCMAP02B*.wlt
    -> restored 13-file Wolfram/xAct regression stack
```

## Exact source bindings

### REC source occurrences

- `characteristics.py`: `f71ec2607daac808b871279ad0893d4653169343`;
- `directional_face_admission.py`: `789213442fada2b3455a2866d49e4085896fc330`;
- `verify_frame_face_event.wls`: `51d62d3159d2ef8f4ad401bce06c49906e7b1125`.

### New BASS classifier paths

- `RECRelationClassification.wl`: `434f777476b0ff82dbc3ed12f13738aab25cc5ae`;
- `SYNCMAP02BRecRelationClassification.wlt`: `20cf9af99dc8e74ac2ca1d538fd24d4aed0ac8b3`;
- `RECRelationClassificationValidationFix1.wl`: `b553fd9682615a5ebba9b0d296800fe57f45f1e4`;
- `SYNCMAP02BValidationHardening.wlt`: `5cbec329c2cde9ecfece5f52642b6d88925cf28f`.

All four new executable paths were reconstructed from Dropbox and reproduced their Git blob SHA-1 identities.

## What is genuinely computed

- expansion of the REC projected normal-frame direction characteristic;
- exact residual against the BASS direction-flow expression;
- sphere tangency `e.V=0`;
- exact normal-frame energy-drift residual;
- Doppler positivity under a subluminal domain;
- unit norm of the aberrated direction;
- exact hydrogen-frame adapter residual;
- exact derivative of the moving Doppler coordinate;
- independent counterexamples separating `R_H=0` from `v_x=0`;
- acyclicity and exact node/edge endpoint closure of the proposal DAG;
- sign and coefficient hostile mutations.

## What remains metadata or bounded classification

- The four missing common formulas are referenced by proposed formula IDs but are not yet canonical BASS EquationIR records.
- `13/14 no active REC rederivation` is an active-lineage path and formula-occurrence classification, not a theorem that no duplicate exists on every historical branch.
- The two formal-script groups are counted from the exact source and classified, but this stage does not rewrite the REC script into separate executables.
- No provider values, runtime history, or physical face object are consumed by BASS.

## Failure-preserving verification history

1. TDD RED: 11 required APIs absent.
2. Focused implementation: 21/21 PASS.
3. First combined stack: 196/196 symbolic tests passed, but a custom Git-blob verifier encoded `backslash + zero` rather than a NUL byte; this result was not promoted.
4. Corrected identity check: 2/2 exact Git blob identities PASS.
5. One temporary-link replay downloaded 925-byte error documents and ran only the 175 parent tests; excluded from physics evidence.
6. Restored pre-hardening stack: 196/196 PASS.
7. Dual-audit hardening added four tests and two computed-residual repairs.
8. Final restored stack: 200/200 PASS, failed 0, not evaluated 0.

## Hostile tests

- wrong normal-energy sign: nonzero residual `6`;
- wrong coefficient in `R_H=R_normal+D0 ln D`: nonzero residual `1`;
- foreign unregistered DAG endpoint: rejected;
- oracle authority effect changed away from `NONE`: registry invalid;
- physical face or provider marked admitted: receipt invalid;
- missing shared owner formula gap: test failure;
- duplicate authority inserted into the BASS-14 matrix: test failure.

## Ranked findings

### P0

None.

### P1

1. Exact import locks cannot be emitted until BASS exports the four shared frame/photon formulas as EquationIR.
2. REC's physical 26-direction face and provider remain blocked and must not be inferred from the formal contract or event predicates.

### P2 — repaired here

1. Two relation checks were literal `0/True` rather than computed residuals.
2. The initial impact-DAG validator did not exclude foreign endpoints in both directions.
3. The initial custom Git-blob oracle used the wrong delimiter representation.

All three were repaired without changing a physical formula or classification.

### P2 — remaining

1. The relation classifier manually re-expresses the shared formulas; it does not parse the REC Python AST into EquationIR.
2. The four shared formula IDs have no canonical owner semantic hashes yet.
3. The formal REC script remains physically mixed in one file even though its authority roles are now separated in the registry.

### P3

- The Git commits are unsigned.
- GitHub Actions for this new branch are not yet observed; the authoritative evidence is the fresh connected and Dropbox-restored Wolfram replay.

## Verdict

```text
PASS_WITH_SHARED_FORMULA_EXPORT_GAPS
```

The active REC lineage does not currently constitute a competing geometry authority. The correct next work is to classify REI relations and then issue a single BASS-owned shared frame/photon EquationIR extension, rather than copying these formulas into REC.
