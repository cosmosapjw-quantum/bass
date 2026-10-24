# REC-LOCAL-02 momentum-scale repair and rereview record

## Authorization and immutable parent

This additive cycle was explicitly authorized after the historical
REC-LOCAL-02 repair budget ended. Its sole P1 scope is the locked
`momentum_scale` owner identified by the PHYS-MATH review in
`../rec_local02/REC_LOCAL_02_REVIEW_RECORD.md`.

- Parent commit: `dd0e080400bc76d6c5e6af382717e613a9fb32f8`
- Parent tree: `1baed7d1d072fcc94b583e66a6461c657e6520c8`
- Parent PR: `https://github.com/cosmosapjw-quantum/rec_bianchi/pull/42`
- Parent review record: preserved without modification
- Preserved REC-LOCAL-01 evidence and source worktree: not normalized, reset,
  cleaned, or rerun

## Reproduction and root cause

The committed pre-repair witness was reconstructed as `B[target,source]` and
evaluated against the tracked owner
`network["momentum_scale"] * c / electron_volt`. Its reproducible maximum
locked-energy residual was `5.540597669551062e-08 eV`. The new regression
selector failed with one assertion failure and no collection error:

```text
tests/trajectory/test_physical_split_reference.py::test_adjacent_energy_witness_uses_locked_momentum_scale_owner
1 failed in 0.88s
```

The defect was provenance, not tolerance. The candidate reconstructed a
centroid from a modern line and interval faces. The tracked network owns the
finite-volume photon-momentum value in `momentum_scale` with units
`kg m s^-1`; its cell energy is therefore `momentum_scale*c/electron_volt` in
eV. The old test repeated the candidate's formula and was a circular oracle.

## Bounded repair

- `physical_split_reference.py` now feeds only the tracked momentum owner to
  `adjacent_energy_feasibility`.
- The line/interval and point reconstructions remain comparison diagnostics
  and are explicitly non-authoritative.
- The focused test independently loads the fixed-hash NPZ owner, reconstructs
  the 35x8 witness, verifies source-column number and energy conservation,
  and proves that the legacy-centroid mutant fails the locked oracle.
- `REC_LOCAL_02_EXECUTION.json` was regenerated from the same eight tracked
  scientific inputs.
- No deposition map was selected and no downstream physical operation was
  enabled.

## Scientific result

- Locked target range:
  `[10.19434557462061, 10.203326358172344] eV`
- Native source range: `[10.194417, 10.203012] eV`
- All 8 sources strictly inside the target hull: `true`
- Orientation: `B[target_com_cell,source_native_index]`
- Maximum number residual: `0.0`
- Maximum locked-energy residual: `0.0 eV`
- Minimum nonzero fraction: `0.07017554027169913`
- Locked target-energy SHA-256:
  `19b9b6bb3d3d0657cb71745118ea396dc3cce92ed15491c20df8a9df8d91f8c8`
- Witness SHA-256:
  `0277e168ac0a596e19078c0489b53fd797770dbe618de767970eeb43f141966e`
- Legacy centroid to locked-owner maximum difference:
  `5.545800263462297e-08 eV`
- Classification: `EXPLORATORY_NONAUTHORITATIVE`
- Physical map selected: `false`

## Validation

Environment used for the recorded rerun:

- Python `3.12.13`
- NumPy `2.4.2`
- SciPy `1.17.0`
- pytest `9.1.1`

Results:

- Regression RED: `1 failed`, `0` collection errors
- Regression GREEN: `1 passed in 1.05s`
- Focused source-authority file: `9 passed in 2.06s`
- Owner dependency cone: `61 passed in 5.43s`
- Wider non-slow run excluding the unavailable `mpmath` collection module:
  `431 passed`, `2 failed`, `37 deselected`; both failures were solely
  `ModuleNotFoundError: mpmath`
- Import check, HyRec binary-hash policy, compile, and `git diff --check`:
  `PASS`
- `verify_repo.py --all`: expected inherited evidence-policy `FAIL`; it
  identified only the preserved PR #42 whitespace/EOF bytes and did not reach
  pytest

The execution receipt was regenerated twice byte-identically in this
environment. One unrelated direct-node measure residual differs in the last
reported digits from the historical receipt, so cross-environment receipt
byte identity is not claimed; the scientific bound remains unchanged.

## Independent rereviews

### PHYS-MATH

Disposition: `PASS` with `P0=0`, `P1=0`, `P2=1` publication-binding note.
The review independently confirmed dimensions, tracked-owner provenance,
positivity, strict hull inclusion, zero number/locked-energy residuals,
legacy-centroid falsification, receipt freshness, and preservation of the
claim ceiling. The locked `momentum_scale` P1 is closed.

### PHYS-MATH-CODE

Disposition: `PASS_WITH_P2_PUBLICATION_CONDITIONS` with `P0=0`, `P1=0`.
The review confirmed that the fixed-hash NPZ gate remains in force, the test
is no longer circular, receipt regeneration is byte-identical in the recorded
environment, and the change does not select a map or enable any `NOT_RUN`
operation. This additive record closes the required historical/publication
binding; environment-independent JSON byte identity remains an explicitly
recorded residual risk.

## Byte binding before commit

- Diagnostic module SHA-256:
  `d4a2d797c2f5c705564d15ef72a9911661b92ca26d5ba9b5f2366d0836f7e36c`
- Focused test SHA-256:
  `4a65a3b6ef1ecd7ecc38417fdb6de4061d379af149f80f1524a86008febf9001`
- Unchanged runner SHA-256:
  `b381925a3056b5669b70b7ece69739a14278494e82da3310fa8406d49b34099f`
- Execution receipt SHA-256:
  `7bf0ebf143589b45308f5e0157a80ff842dc99783b5207748732f332a6c12912`

The final commit and tree are bound by post-push GitHub readback; a commit
cannot self-bind its own hash inside these bytes.

## Claim disposition and terminal state

The exact locked-owner feasibility certificate is now admitted for the
bounded existence witness only. It does not admit deposition authority.
Source-defined 26-direction face reconstruction is still absent, so the
repository claim remains:

`NO_PASS_REC_PHYSICAL_SPLIT`

Current terminal state:

`BLOCKED_REC_PHYSICAL_INTERFACE_DEFECT / SOURCE_DEFINED_26_DIRECTION_FACE_RECONSTRUCTION_ABSENT`

All eight downstream operations remain exactly `NOT_RUN`. No merge, ready
transition, physical-map selection, or broader science claim is authorized by
this record.
