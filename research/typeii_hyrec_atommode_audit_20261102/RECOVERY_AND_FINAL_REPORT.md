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
