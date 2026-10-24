# C9 pre-execution independent code review

Reviewer role: independent scientific/code reviewer; this agent did not write
the implementation or the frozen contract. This is a same-model independent
scientific review. Different-model scientific review remains **NOT_RUN**.
No scientific process, trajectory, oracle, test or remote write was executed
for this review. Reviewed file identities accompany this note.

## Preliminary decision

**PASS_SCOPED for proceeding to the frozen bounded execution.** No substantive
physics or numerical implementation defect was found by source inspection.
This is not numerical admission: actual test logs, trajectories, refinement
orders, invariant residuals and figure are still required for the final C9
recommendation.

The review accepts only the declared synthetic, cold, recoil-free,
non-tilted, diagonal Bianchi-I, vacuum-initial, zero-blue-incident, fixed14-ray
model. It does not close actual REC finite absorption, replace the REC910
bootstrap, establish continuum angular convergence, or admit broad B3c/B4/B5.

## Source-level findings

- `code/emission_split.py:15–24` constructs the specified actual source card,
  synthetic N0 and x0, approximate ground mass, Hamiltonian initial H0 and fixed
  L. The excitation denominator U0 excludes the large constant ground energy.
- `:51–69` reconstructs the exact diagonal collisionless cohort map and all
  three accounting sectors. Sector0 and sector1 describe excitation and ground
  rest energy of the same N atoms. Only the photons carry pressure/STF stress.
  Vacuum follows the parent's explicit empty-stock branch.
- `:71–78` calls unchanged `core.rhs` on the reconstructed material state and
  extracts the correct packed indices for h, the two independent diagonal
  shears and alpha. The beta equations are the actual shears. Its positive
  work expression is algebraically the stipulated excitation-plus-radiation
  energy loss; normalized work is integrated as a seventh coordinate.
- `:80–113` rebuilds current H, S, N and populations for every source substep,
  selects rest/proper-time detached ownership, uses sectors0/2, and invokes the
  unchanged finite transaction. The product order for excitation matches the
  stored n_u and actual source. Source substep duration is L/c times dtau;
  transfer IDs and epochs are distinct. Old birth coordinates and canonical
  weights are retained when a new cohort is appended. Returned U/J remain zero
  because the finite exchange is already charged.
- `:115–153` advances the global clock only under A and implements the declared
  C(h/2)-A(h)-C(h/2) and C(h)-A(h) compositions. There is no projection,
  renormalization or packet clipping. The prescribed diagnostic keeps h and
  shear fixed and is explicitly separate from the coupled Einstein path.
- `:156–189` uses the frozen output distances and roundoff-resolution rule.
  Its prescribed oracle solves a separate monotone scalar residual, then
  integrates the independently reduced axis/corner angular formulas in the
  exact exposure variable v. The upper root bracket follows
  F'(v)>=1-z>0. Dilution, redshift, photon number, tensor normalization and the
  four diagonal tensor positions agree with the direct derivation.
- `tests/test_split.py` covers initial constraints/vacuum, positive actual
  emission, the nonparticipating rest sector, exact diagonal characteristics,
  f_plus/frame/native-owner/directional/thick/stale-stock/stale-epoch rejection,
  and relevant input nonmutation. These are new-client checks; they do not
  replay parent test campaigns.

The unchanged `core.rhs`, `kinetic.moments`, `kinetic.tensor` and parent
`commit_emission` were read directly. The packet weights are state density
weights throughout. Nothing applies their boost rule to invariant event rates,
and Source.pi remains state stress rather than PiRate.

## Reporting item C9-R1 — prescribed orders need explicit final assessment

`code/summarize.py:25–36` calculates prescribed Lie and Strang oracle errors
and orders, but its aggregate `all_frozen_gates_pass` does not include the
prescribed-order demonstration in contract item7. Consequently that Boolean
alone cannot establish every requested numerical result.

This does not block the frozen runs or change a physical/numerical threshold.
At final review, explicitly assess the saved prescribed photon-tensor orders:
resolved Lie behavior must support its first-order statement and resolved
Strang behavior its second-order statement. If an automated admission summary
is used, its wording must not exceed the checks it actually aggregates. No new
trajectory or broader test campaign is required merely for this reporting item.

## Final-review inputs still pending

Read actual raw execution receipts and failures, not only the summary Boolean.
Assess final64/128 differences, resolved finest-triplet orders, the tight-A
comparison, excitation-scale work and count residuals, constraint/positive
support/opacity checks, and the actual PNG. The analytic support lemma and
numerically sampled support minima must remain distinct. Confirm the exact
implementation identity at execution; any changed substantive lines require
only a targeted readback before final admission.
