# ACCEL03 independent scientific, code and figure review

**Verdict: PASS_SCOPED_PORTABLE_ANALYSIS_MASSIVE_RESPONSE_AND_NCP_NUMERICAL_EQUIVALENCE.** No unresolved blocking finding. This is the one fresh independent review required by the current REI policy. The reviewer had no implementation involvement and changed no implementation files. Requested review routing was `gpt-6-astra`; observed runtime model identity is unavailable and recorded as null.

## Scientific decision

The fixed-weight derivatives are correct. Writing h=(3t−1)/2 gives d_b log R²=−4h, d_b h=−9t(1−t), and d_b(E v²)=−2(2−v²)h E v². Their product yields J2_b=−G with the stated nonnegative summand. Differentiation in x includes both the r³ measure and momentum/energy response, giving J2_x=−5J2+J4. The time derivative follows from xdot=H and bdot=s. These are exact identities of the finite weighted sum; the numerical checks verify the implementation within a bounded domain. The half-contraction convention consistently gives physical work 2sD and normalized work 2 Sigma Pi. Signed components are added before norms.

The saved input file contains the three nonnegative 96×32 quadratures at mass/T=30. Its contract and theory hashes match the reviewed files. I independently recomputed all 27 saved five-point stencil reductions from their recorded evaluations without repeating the quadrature matrix. Maximum energy-scaled residuals are **1.0715866992998556e-13 in x** and **3.6901037780978584e-14 in b**, below the frozen 2e-9 limit. Minimum recorded G is 0.012992574995213354. The one-node limits are explicitly illustrative and are not C15 parameter runs. Radiation collision/emission/UV terms remain outside the massive identity.

## Portable analysis and data accounting

Code inspection and the preserved 12 focused test outcomes support the contracted behavior. The supplied plan owns the complete candidate set. The NCP projection contains 5 successful pending cases, no missing cases and 15 unique actual history rows. The archived projection reuses 729 pinned endpoints with zero history rows loaded. This does not erase the histories preserved in the original archive. The first/second worker scope fixture admits one scientific duplicate and three samples, without treating cache metadata differences as scientific changes.

Completion aliases use science identity to resolve the pinned CSV row while retaining the requested label. Input/science/toolchain checks use the stored plan/manifest and pinned owner source, not NumPy or Python equality with the analyst host. Missing pending cases return PARTIAL, and missing exact controls remain null. Controls match requested initial shear and a cohort that incorporates source, backend, toolchain, step count, context and interval. No nearest-control substitution occurs.

Cancellation calculations use initialized, masked NumPy divisions. Exact cancellation and zero component scale receive separate null/status representations. Redundant serialized quantities are retained, and sum/norm/work checks use component scales. The maximum recorded residual-to-scale ratios are 2.528508284916226e-16 for NCP and 3.8369107064748666e-16 for archived endpoints, below 128 epsilon64. These diagnostics describe arithmetic consistency and conditioning, not a measured global solver error. No clipping or fabricated zero samples was introduced.

## Independent NCP adjudication under unchanged ACCEL02 criteria

I compared the retained original cases in ACCEL02 TRAJECTORY_RAW.json directly with NCP_TARGET_CASES_RAW.json. All five requested cases and all 40 original gate flags pass. There are 20 serialized initial/history/final comparisons because final duplicates the last history sample; the analysis correctly retains only 15 distinct samples.

Maximum absolute differences are 2.0668852438742e-21 for signed shear, 4.119968255444917e-18 for matter stress, 1.0842021724855044e-19 for radiation stress and 4.1384176918272996e-18 for total stress, against 5e-14 limits. H relative difference is 1.1128439998013552e-16 against 5e-13; temperature and ionization differences are zero. The maximum normalized work difference is 1.2713960895138061e-21 against 5e-14. The independent reductions reproduce the intake maxima. Equality of secondary error-estimate bytes is not imposed as a numerical acceptance criterion.

The target archive is SHA256 `ad92f4207a6845a0326a095cb904792b6d34bf0654f7148fe3c530b47f5e2817`. Its backend source identity is `aed4c55a61df37d97d8c0aa309b7875e5eb3629abbd284fe04faf23cb261115d`. The retained authoritative source records map BASS commit `7fe0e25a28c0e48110c522378e203ffb934cc504` to root tree `ee48c52b9d3aa2e9511f47d3fc0340c17d0a171d`, and REI commit `231df3ab717dbc112f63b77953f64def08e9bcb5` to root tree `af2c36382cc712302a54cd041e82cb9d5beaff9c`. I independently recomputed all seven selected retained source Git blobs and matched their pinned records. The intake's completed 47-file archive binding check is reused; no native build or trajectory was repeated.

## Figures and bounded repair

Both actual PNGs were opened and visually inspected. The NCP figure has six panels: four signed histories, matched-control final shear and the opposite-stress residual fraction. Three actual times per case are marked, and native two-step source/cohort labeling is explicit. Its 68 source-point entries pass 204 independently repeated exact scalar comparisons.

The archived figure has four exact-coordinate panels on the requested signed-Sigma=0 slice, with 81 actual coordinates. Its 324 entries pass 1296 exact scalar comparisons. Signed color scales, coordinate spacing, work normalization and source/cohort labeling agree with the tables. No interpolation or invented history is present.

The controller identified two narrow wording issues. One bounded plot-owner repair now says intermediate history is **not loaded in this projection**, and rings the requested zero-stress center with an explicit warning that q reflects raw floating-point residuals without physical cancellation interpretation. I opened the updated PNG and accepted both changes. Data values and tolerances were preserved. No further repair is required.

## Accepted boundary and transition

This PASS admits portable saved-result analysis, its exact-data figures, the fixed-weight massive response diagnostic, and the NCP numerical equivalence of the five prescribed two-step cases. It does not establish convergence, full EoR, non-LRS or tilted/Qa behavior, performance, or an unrestricted numerical error bound. C21N and PR199 remain attributed external comparisons; their trajectories are not C15 samples. Subsequent publication and provider receipts remain the controller's separate closeout work.

The reviewer ran only lightweight standard-library stored-data arithmetic, CSV and hash checks in one process. There were zero solver calls, new trajectories, builds or benchmarks, and no repeated old full suite or moment matrix. Exact reviewed source and evidence SHA256 values are recorded in the companion JSON. **PASS transitions directly to scoped admission and the authorized Stage C report, handoffs, restore publication and backup closeout.** No additional scientific review cycle is required.
