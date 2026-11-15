# BASS native atomic-mode comparison: recovery and bounded closure

Baseline: PR332 ee298e24a6bac85bb11a81393f37499a8b0ddbe3; current branch resumed from 2c642089cf44d757f766e2b9bad96c5c898685bc.

## R3/C3: recovery and claim alignment
The previous atommode worktree and its uncommitted R3/R4 outputs were absent at the old path on 2026-11-15. Only R1/C1 and R2/C2 are remotely preserved. This is a preservation gap, not evidence that the old numerical solution was wrong. Original 16 computation source/header/atomic-table files have now been recovered from CLASS upstream, with every file matching PR330's immutable SHA256. The two old distribution sample files input.dat and output_xe.dat are not needed by this experiment and are not claimed recovered. The actual calibrated input and parent TypeII H/nH/26-ray histories are Git-owned and preserved.

The new execution will compile each model independently with MODEL=SWIFT, EMLA2s2p or FULL. This keeps allocation, timestep selection and hyrec_integrator in agreement. Atomic evolution step and fixed 2248-point externally supplied Hubble interpolation grid remain separate. Default 3e-4 hydrogen post-Saha threshold is not widened.

Acceptance: SWIFT must reproduce the parent within 2e-9 absolute xe over 300<=z<=1700; use FULL timestep factors 1,2,4 to measure convergence, plus SWIFT factors 1,2,4 and a step matched to FULL. Never treat a tiny quadrature error as an atomic-mode error bound. EMLA is a diagnostic approximation, not a superior reference. FULL remains an isotropic radiative-transfer closure with prescribed source histories, not a complete tilted-Bianchi recombination solution.

DAG: upper 9/15 scoped/source-mapped unchanged. No new full-production node. Native subagent NOT_RUN; distinct-author referee NOT_RUN.

## R4/C4: implementation contract
Five tests first failed because the isolated builder was absent, then passed. The new builder deterministically derives scratch copies from the 16 exact originals. It changes MODEL at compile time and only the declared timestep for convergence; no runtime-only mode substitution is used. Exactly 12 hydrogen and 4 helium density references are redirected as in the parent. The two Hubble interpolation grid-length declarations are fixed at 2248 independently of the atomic integration grid. Expected campaign: 18 histories, three approximations, two backgrounds, timestep refinement and a common-step SWIFT comparison.

## R5/C5: actual executions
16 histories completed. SWIFT step 0.001 fails on the FLRW control in the original helium routine at z=2852.557707, with xHeI=-3.020442e-5. This is before the z=1700 TypeII intervention, so the equivalent TypeII-prefix case was not repeated. This is a source numerical refinement failure, not a proof of a physical pathology. No source post-Saha threshold was widened. SWIFT default, half-step and FULL-matched-step runs, EMLA default/half, and FULL default/half/quarter completed on both backgrounds. The parent SWIFT xe maximum absolute difference is 4.9930060086467165e-12 over z=300..1700.

## R6/C6: executable verification
The five mode-isolation contracts ran normally and under Python -O (10 successful unittest cases). Six malformed native-grid cases were actually passed to the C binary: negative H, truncated H, extra H, NaN H, negative proper-density factor, and truncated proper-density factor. All rejected with exit2 and no output table. A fresh compile and FULL quarter-step TypeII execution reproduced the current output byte-for-byte. The physics analysis ran under -O and reproduced both JSON and CSV outputs exactly; scientifically relevant gates use explicit checks, not removable Python assertions.

These are implementation checks, not 18/18 scientific simulation success: the campaign deliberately retains 16 successful histories, one native numerical failure, and one equivalent-prefix case not run.

## R7/C7: physical meaning
See THEORY_MODE_AND_CLOCK.md for the full four-level elimination, signs/units and the newly explicit proper-clock obligation. Correcting nHrest alone does not provide dx/dtau_H=R_proper/(Gamma H_n). The inherited model comparison remains a controlled numerical experiment; it is not a fully covariant tilted electron reaction/thermal closure. This gap is a concrete next constructive task, not a reason to discard the measured mode comparison.

## R8/C8: numerical decision
TypeII matched-step SWIFT versus FULL quarter-step: max absolute xe difference 0.00031889001419160845 and max relative difference 0.0033637560252735531. The FLRW matched-step relative difference is 2.1988624925637243e-05.
The TypeII FULL half-to-quarter maximum absolute xe difference is 2.2725266213274864e-07. The FLRW global maximum difference is not monotone (switch-adjacent maximum around z1563); no global Richardson order or exact error bound is claimed. Local z1100 and restricted-window diagnostics are provided separately. Fixed external-grid error and covariant closure error are not the same as the atomic timestep error.
The optical-depth differences are small and partially cancel across redshift, but this does not imply uniformly small xe errors. Full tables and per-ray deltas are retained, rather than interpreting only the final integral.

## R9/C9: review verdict
The unpatched standalone control reproduces the SWIFT quarter-step helium failure with process exit0. This confirms why a successful process exit cannot substitute for a valid history. Wrong Thomson-interface counterexamples and the proper reaction-clock limitation are recorded in SELF_HOSTILE_REVIEW.md. The same-author review is complete, but the production/scientific-covariance gate remains held.

## R10/C10: final bounded disposition
The original mode-comparison question is answered with 16 current successful native histories and explicit failure classification for the remaining two scenarios. The 16 executable source files are byte-exact restored; original BASS 9/9 source blobs remain exact. The original sample input/output distribution files are not claimed restored. The source cosmology correction diff1 at T0fid/T0=1 is 2.3878209660242039e-05, correcting the old R2 sign/approximation.
FULL-quarter TypeII optical depths are Tplus=42.586108216321065 and Tminus=46.824789468916052; asymmetry=0.047406763183576076. This replaces historical uncommitted values as the current source-conditioned result. See CONVERGENCE_AND_ERROR_BUDGET.json for comparisons with common-step and refined references.
Ten local stages are complete as a bounded audit/experiment and disposition, not as 18/18 successful simulations. Upper DAG remains 9/15 scoped/source-mapped, zero new fully complete production nodes. StageII and Join holds remain. The next actionable unit is a two-clock atom/thermal/radiation interface: separate proper reaction time, fluid expansion, and photon redshifting, with a zero-tilt reduction test before source integration. No additional optional review loop is needed.
Primary literature: https://arxiv.org/abs/2007.14114 and https://arxiv.org/abs/1011.3758 . Source provenance is bound to the original file hashes and a pinned upstream commit, not a model-name claim.
