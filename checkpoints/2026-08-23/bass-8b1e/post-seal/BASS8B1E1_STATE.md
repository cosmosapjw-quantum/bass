# BASS-8B.1E durable research/implementation state

## Objective (frozen)

Implement an independent cold-electron **test-field** state for the BASS Thomson lane, embed the comoving-electron closure `u_e = u_fluid` as an exact restriction of that state, and implement the finite fluid-frame ↔ electron-frame transformation needed by photon intensity/polarization collision inputs. Preserve project conventions `g=(-,+,+,+)`, `epsilon_123=+1`, and explicit `c`. Do not add electron backreaction, recombination/reionization dynamics, promote row 7, start row 8, or touch classifier/solver/runtime production branches in this phase.

## Controlling user decision (frozen)

The 2026-08-23 user decision selects H2 as the encompassing model: retain an independent electron test-field state, include H1 as the exact `u_e=u_fluid` comoving restriction, and implement the frame transformation between them. This resolves the scientific H1/H2/H3 selector for this phase but does not silently fill the other OD002 booleans or complete the canonical OD001–OD004 receipt.

## Narrow modelling assumptions (frozen)

1. “Test field” means electron state is prescribed/input data and does not source the A.4 background Einstein–perfect-fluid evolution.
2. The electron velocity is independent in the general branch. The comoving restriction identifies velocity only. Proper free-electron density remains an explicit independent nonnegative input unless a later composition/ionization authority supplies a map.
3. Cold-electron scope is retained; nonzero electron temperature or a full electron momentum distribution is out of scope.
4. Frame transformation must act on physical photon four-momentum and the screen-projected polarization tensor. A coordinate-only relabeling or unverified Stokes rotation is insufficient.

## Frozen hypotheses

- **H1 — reusable internal seam exists.** Prediction: `bianchireview87` contains a moving-electron collision/frame module with a stable public seam that can host the new state/adapter without rewriting the collision kernel. Falsifier: only lane-local perturbative approximations or incompatible conventions exist.
- **H2 — independent state with exact comoving restriction is well-defined.** Prediction: one normalized relative-velocity representation gives `u_e.u_e=-1`, invertible finite boosts for `|beta|<1`, and exact identity at `beta=0`. Falsifier: project normalization or data layout requires a different owner decision.
- **H3 — screen-tensor transformation can be made representation-safe.** Prediction: transforming the photon null vector plus projecting the polarization tensor onto the target screen preserves transversality, trace-free linear polarization, Hermiticity/PSD of the coherency carrier, and round-trip equivalence modulo screen-basis `U(1)`. Falsifier: the existing finite carrier lacks sufficient basis/gauge data.
- **H4 — current selection is technically actionable but not a canonical row-7 promotion.** Prediction: a hash-bound selection record can authorize this bounded prototype/authority package while OD001–OD004 receipt completion and full radiation quotient proof remain separate gates. Falsifier: current authority forbids even local research implementation after explicit user selection.

## Planned experiments

- **E1 confirmatory — local authority/code survey.** Establish exact archive hashes, package layout, dependency versions, velocity normalization, collision API, and existing tests before editing.
- **E2 confirmatory — primary-source equations.** Retrieve exact finite observer/electron boost, screen projector, polarization tensor, and cold-Thomson density/velocity requirements from primary literature. Record signature/unit conversions.
- **E3 confirmatory — red tests.** In an isolated extracted copy, add public-seam tests for independent state validation, comoving identity, boost inverse/nullness, density invariance, polarization screen constraints, and round-trip modulo screen gauge. Observe nonzero failure for missing behavior before production edits.
- **E4 confirmatory — minimal implementation.** Add only the state and frame adapter needed by E3, reusing current project carriers and leaving background/collision owners unchanged.
- **E5 confirmatory — integrated exact/numerical checks.** Run identical red command green, affected existing tests, property/hostile boundary cases, and an independent symbolic or high-precision check where it adds distinct evidence.
- **E6 confirmatory — fresh independent review.** A read-only verifier inspects the frozen plan, diff, red/green log, sources, and claims without an expected verdict.
- **E7 confirmatory — durable seal.** Package source diff/implementation/tests/reports with internal manifest, ZIP CRC, extracted rerun, and SHA sidecar.

## Falsifiable criteria

1. **C1 tracer:** a public construction creates an independent electron state and its `comoving(...)` restriction; focused test must fail before source edit and pass after.
2. **C2 frame kinematics:** finite transforms preserve photon nullness and positive energy and round-trip within declared tolerance for representative and hostile subluminal velocities.
3. **C3 polarization/screen:** target polarization is transverse to target observer and photon direction, preserves the physical coherency spectrum/PSD, and round-trips modulo explicit screen `U(1)`.
4. **C4 compatibility:** existing affected collision/frame tests remain green; `beta=0` reproduces the prior electron-rest/comoving result exactly.
5. **C5 authority boundary:** test-field/no-backreaction, independent density, cold scope, canonical-receipt gap, and non-promotion boundary are machine- and human-readable.
6. **C6 independent verification:** fresh verdict is `confirmed` or `partially-confirmed`; `inconclusive` blocks closeout.
7. **C7 durable artifact:** manifest, archive CRC, extracted tests, and sidecar all return exit 0.

## Stopping rules

- Stop with `BLOCKED_NORMALIZATION_OR_CARRIER_AUTHORITY` if local conventions cannot be reconciled without inventing a new owner decision.
- Stop with `PARTIAL_FRAME_KINEMATICS_ONLY` if Lorentz kinematics closes but polarization quotient/screen carrier cannot be proved; do not label row 7 complete.
- Stop with `FAILED_RED_GREEN` if the focused test never establishes a valid red or cannot be made green with the bounded implementation.
- At most one classified retry per exact command. No package installation, remote write, branch, commit, PR, or control-plane promotion in this phase.

## Criterion status

- C1: pending
- C2: pending
- C3: pending
- C4: pending
- C5: pending
- C6: pending
- C7: pending

## Evidence log (append-only)

- **EV001 — explicit model selection.** Source: user message dated 2026-08-23. Decisive content: add an independent electron test-field state, include the `u_e=u_fluid` comoving-electron closure, and implement the frame transformation between them. Observation: H2 is selected as the general model with H1 embedded as a restriction; H3 is rejected for this lane.
- **EV002 — valid focused RED.** Command: `cd electron_testfield_work/repo && python tests/test_electron_test_field.py`. Exit: `1`. Decisive output: `AssertionError: RED: bianchi.q.electron state/frame adapter has not been implemented`. Classification: missing requested public behavior, not a dependency/import/test-runner failure. No production source existed or had been edited at this point.
- **EV003 — primary-source reconciliation.** Sources: Pitrou (arXiv:0809.3036), Challinor (astro-ph/9911481), Beneke–Fidler (arXiv:1003.1834), and Takahashi et al. (astro-ph/0502283). Observation: the exact observer map uses `D=Gamma(1-beta.e)` in the target `(-,+,+,+)` convention; polarization is target-screen projected; bolometric brightness and solid angle carry `D^4` and `D^-2`; cold-electron density and velocity are separate inputs. Decisive semantic boundary: generic H2 and the H1 restriction are different physical states distinguished by invariant `Gamma_ef`, while fluid/electron frame transformation is a reversible representation map of one state.
- **EV004 — internal seam and authority survey.** Input archive SHA-256: `6bb094d30a6d24b3feee11a1d9ae2827049945dae8281ed37d0d0796a6e9ea84`. Reused production primitives: `bianchi/q/boost.py::doppler` and `bianchi/q/polstate.py::boost_shape`; independent prior oracle: `audit/p9_boost_screen.py`. Internal `Low-ell Bianchi Einstein–Boltzmann Solver.txt` requires an exact electron-frame authority path and rejects shortcut frame transforms. Observation: legacy `Collision.v_b` and Rust ABI support only a constant single normal-frame velocity, so runtime wiring is a separate change and was not modified.
- **EV005 — focused GREEN.** Identical command: `cd electron_testfield_work/repo && python tests/test_electron_test_field.py`. Latest exit: `0`; `Ran 10 tests ... OK`. Covered state/domain, exact comoving restriction, explicit-c four-velocity, non-collinear frame composition, existing single-boost parity, photon round trip/nullness, polarization screen/PSD/round trip, Mode-A scaling, and machine-readable authority boundaries.
- **EV006 — hostile independent 4-vector/screen audit.** Direct-matrix oracle, 1,000 random cases with each speed up to `0.85c`: metric and inverse maximum `8.216e-15`, relative-gamma `8.882e-16`, photon direction `3.803e-15`, photon energy `1.776e-15`, photon round trip `1.665e-15`, polarization direct parity `3.136e-15`, polarization round trip `9.992e-16`, screen leak `1.639e-16`, trace `2.220e-16`. Spatial-block asymmetry reached `1.619`, proving non-collinear rotation cases were exercised.
- **EV007 — compatibility diagnostic and repair.** A new exact-parity gate found that a mathematically identity zero-velocity screen stage introduced projection roundoff before the existing single-boost path. Production fix: skip exactly zero source/target boost stages. Same gate then passed bitwise for photon and normalized polarization shape. This changed no collision kernel or physical formula.
- **EV008 — available local regression evidence.** `python audit/p9_boost_screen.py` exit `0`: scale `4.441e-16`, anisotropy `6.661e-16`, canonical transported-screen phase `6.667e-16`, round trip `7.772e-16`. `py_compile` for implementation/audit/test and JSON parsing both exit `0`. Full locked pytest/Rust suites remain unexecuted because the scratch host lacks pytest/JAX/Rust extension dependencies and the stopping rule forbids installing them.

## Status update 2026-08-23 (append-only)

- C1: PASS — valid red and public independent/comoving constructions now green.
- C2: PASS_BOUNDED — exact photon/frame properties and hostile non-collinear audit green to recorded tolerances.
- C3: PASS_LOCAL_SCREEN — basis-free canonical transported-screen carrier green; global residual-U(1) quotient remains explicitly outside this claim.
- C4: PARTIAL — focused existing single-boost parity and prior P9 audit green; full affected pytest/Rust suites unavailable in this host.
- C5: PASS — source metadata plus Markdown/JSON contract preserve no-backreaction, density, cold, receipt, and non-promotion boundaries.
- C6: pending — fresh independent implementation reviewer is running.
- C7: pending — durable manifest/archive/CRC/extracted rerun not yet sealed.
- **EV009 — independent review defect and verified repair.** Fresh reviewer reproduced a forged comoving label with `Gamma_ef=1.091089...` and a non-identity adapter despite the closure tag. Negative tests first produced 10 failures. Repair made `closure` factory-only (`init=False`) and enforced exact stored-electron/fluid beta equality on all relational and forward/inverse adapter methods. Fresh focused command then passed `12/12`; reviewer independently confirmed the repair.
- **EV010 — low-risk findings closed.** Internal rate survey showed the legacy history lane uses `cm^-3` and `cm/s`, while this adapter exposes `c` in `m/s`. A test-first change added immutable `density_unit="m^-3"` to state, metadata, Markdown, and JSON, with an explicit future conversion warning. A committed antisymmetric circular-polarization carrier regression was also added. Latest focused command: `13/13 PASS`.
- **EV011 — updated independent verdict.** Verdict: `PARTIALLY-CONFIRMED`. No open implementation or focused-test finding. Confirmed selection semantics, exact comoving enforcement, ordered non-collinear Lorentz/Wigner map, photon/polarization/Mode-A transformations, SI density unit, and authority honesty. The qualifier is solely the unavailable normal installed-package and full pytest/JAX/Rust integration on this host; runtime relative-flux, residual-U(1), Rust ABI, and canonical promotion remain out of scope.

## Status update 2026-08-23 after independent review (append-only)

- C1: PASS — final focused gate includes factory-integrity and mismatched-comoving rejection.
- C2: PASS_BOUNDED — unchanged after hostile rerun.
- C3: PASS_LOCAL_SCREEN — symmetric PSD plus antisymmetric circular carrier green.
- C4: PARTIAL_ENVIRONMENT — exact reused single-boost parity and P9 audit green; full package suite unavailable.
- C5: PASS — unit, schedule, vacuum, receipt, and promotion boundaries are explicit.
- C6: PARTIALLY_CONFIRMED — no open bounded implementation finding; qualifier is unavailable full-stack integration.
- C7: pending — seal and extracted rerun remain.
- **EV012 — seal-candidate verification.** Candidate ZIP SHA-256 `0e36bfaf215312cbde61b99a073cb71425eec13d1b7f8475ceea8b8f3f6f3a34`; `unzip -t`, internal `sha256sum -c MANIFEST.sha256`, clean extracted focused `13/13`, P9 screen audit, contract JSON, and source-identity JSON all exited `0`. Generated `__pycache__`/`.pyc` files were excluded from the source artifact. This candidate evidence authorizes a final state/receipt-only reseal; the non-circular final archive hash is owned by the external `.sha256` sidecar.

## Final criterion status before non-circular reseal (append-only)

- C1: PASS
- C2: PASS_BOUNDED
- C3: PASS_LOCAL_SCREEN
- C4: PARTIAL_ENVIRONMENT
- C5: PASS
- C6: PARTIALLY_CONFIRMED
- C7: PASS — candidate archive integrity, manifest, and extracted rerun all green; final sidecar verification remains the last non-circular command.

## Final non-circular verification 2026-08-23 (append-only)

- **EV013 — final archive and sidecar.** Canonical ZIP SHA-256 `054d85e0e2f900162dfb58e42ec953c1de45b9ba636cfadbcdaf5ba667596544`. The adjacent `.zip.sha256` check, ZIP CRC, internal manifest, clean extracted focused `13/13`, P9 screen audit, electron-frame adapter audit, contract JSON parse, and `py_compile` all exited `0`.
- C7: PASS_FINAL — the final external sidecar and independently extracted archive now agree; no post-seal archive mutation occurred.
