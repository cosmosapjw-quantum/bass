# Independent R9 — actual midpoint/transport results and two PNGs

Decision: **PASS_SCOPED**. Blocking findings: **0**.

Admit the reconstructed saved-cohort transport, finite14 endpoint consistency,
selected source-continuum numerical postprocessing, and two algebraic B3i
state-consumption checks within the frozen manufactured B3c model. This is
not a physical input-error admission or a native finite absorption transaction.
Publication, preservation and selected DAG observations may proceed.

## Independent review method and identities

The reviewer did not implement the code, rerun tests/consumer/plots, call an
RHS, evaluate a new quadrature, or replay a trajectory. The reviewer read the
current code, C9 corrections, ten-test log, execution ledger, actual SUMMARY,
512 saved midpoint rows and their recorded fields. Structural inventory,
min/max of recorded diagnostics and byte hashes were inspected without
executing the scientific implementation. Both actual PNGs were opened through
the image viewer and visually inspected.

The five code/test files still match EXECUTION_FREEZE.json. Its selected
input-manifest SHA matches, and all20 enumerated immutable input/dependency
files match their recorded SHA256. The C9 revision of the contract changes
equation-scale residual comparison and interruption recording, preserving
the R6 scientific construction and all original tolerances.

| Actual output | Bytes | SHA256 |
|---|---:|---|
| results/MIDPOINT_ROWS.json | 2548843 | d77dcfc5114973bf088aa78012f3ba9c74d6152d9c480a20e709a3f7aef76542 |
| results/MIDPOINT_ROWS.csv | 138612 | 780599a23870514a37c79fdc53067ec5f4d1b41f453c4cf88d45add879a8565a |
| results/SUMMARY.json | 12573 | 91bf6c1fe242c111bf1a254a59626e96c8f221573eadb2d9bcd95a69918fc290 |
| results/EXECUTION_LEDGER.json | 3376 | 85c16bd27e10ec693eab1f2920ae73774195f0c064b1ab047a6a75d5beae2577 |
| figures/MIDPOINT_MAP.png | 116537 | f09bf43633c4676ebe84eea3911bc43fb8ab54c299759acc7ca1daf0e4288c66 |
| figures/FINAL_STRESS.png | 88224 | 84cedc07d659b70baacdf32798ed74669830c3c203c1e68ba532593e945c69d5 |

## 1. Executed delta and preserved budget

The ledger records tests → consume → plot, each exactly once with completed
state and returncode0. The test log contains ten named PASS controls: exact
RK4 identity; stage-box refusal; authoritative duration/STF; degree-four
finite14 birth moments; isotropic scaling and determinant dilution; beta-sign
adverse comparison; missing physical input; underflow refusal; nonzero ANISO
reconstruction; and cancellation-safe equation-scale normalization.

The source consumer contains exactly one final core.rhs call per fixture and
reports two total. It reads saved B3c data and calls the unchanged angular
and finite-error consumers. Tests use one manufactured algebraic RK4 identity
control, not a new B3c IVP. There is no source solve, native REC run, history
query replay, finite absorption or old campaign execution in these commands.

| Stage | Child CPU s | Child wall s | Measured wrapper CPU s |
|---|---:|---:|---:|
| tests | 1.002403 | 1.020943735999026 | 0.023861 |
| consume | 3.524320 | 3.544990869002504 | 0.081891 |
| plot | 2.651191 | 2.6799030840011255 | 0.024371 |

New child CPU is7.177914s and child wall7.245837689002656s. Measured wrapper
CPU is0.130123s, giving measured new CPU7.308037s. These observed costs are
within the frozen20CPU/60wall allocation and per-child10CPU/20wall limits.
Unmeasured metadata/I/O remains UNKNOWN_EXCLUDED. The ledger preserves prior
known CPU3.7263/wall3.739223223001318, historical remaining=null and
historical_budget_reset=false. It does not transfer REI budgets.

The plot stderr reports a non-writable default Matplotlib cache and its
automatic temporary-cache fallback. The plot command completed and both
images rendered correctly; no scientific failure or retry occurred.

## 2. Actual cohort reconstruction and domain evidence

There are512 unique transfer IDs,256 ISO and256 ANISO. Every saved row contains
the reconstructed coordinates, analytic/empirical radii separately, diagonal
map and determinant, numerical B3f result, finite14 and continuum tensors.
The producer subflow duration is used; accumulated endpoint subtraction is
kept only as a diagnostic. beta3 follows the dependent STF chart.

| Saved diagnostic | ISO | ANISO |
|---|---:|---:|
| Analytic alpha radius range | 2.266867367012007e-12 .. 2.878896659994195e-12 | 2.316375703942564e-12 .. 2.945033800483283e-12 |
| Maximum analytic beta radius, including beta3 | 2.2582139353962876e-12 | 2.838418265247154e-12 |
| Operational map radius range | 4.571854071780593e-12 .. 4.9917770149642565e-12 | 5.0251880797629734e-12 .. 5.629548970010874e-12 |
| Determinant range | 0.7565867851337884 .. 0.9994905540362831 | 0.7566618787981042 .. 0.9994908908031132 |
| Minimum recorded H-box upper margin | 0.009695235158982301 | 0.009695805157664281 |
| Minimum recorded component shear margin | 0.19988164062494773 | 0.049881640625000015 |

The completed consumer passed each row's stage/directional domain check.
Positive incoming counts were already integrated source counts; the new code
does not multiply them by a second duration. Reconstruction arithmetic reserves
remain empirical. These radii do not certify unobserved historical floating
stage values or the continuous cosmological solution.

All512 physical_ball statuses are INPUT_ERROR_UNSPECIFIED, all explicitly
reported physical eS/en/eE/geometry radii are null, and all numerical wrappers
declare NUMERICAL_RECONSTRUCTION. The inherited PHYSICAL_BALL name occurs
inside that explicit numerical wrapper, not as a new physical admission.

## 3. Photon-sector endpoint consistency and continuum numerical budget

The saved endpoint comparison uses the energy-plus-spatial tensor Frobenius
norm, with odd components recorded separately. Its denominator is saved
photon energy, not dominant atomic rest energy.

| Actual result | ISO | ANISO |
|---|---:|---:|
| Reconstructed finite14 T00, J/m³ | 282.18476631788036 | 282.0628084802531 |
| Saved T00, J/m³ | 282.18476631532747 | 282.06280847765845 |
| Joint endpoint difference, J/m³ | 2.9478371867139945e-9 | 3.00486466925232e-9 |
| Operational consistency allowance, J/m³ | 5.73649482085279e-9 | 6.043561274315194e-9 |
| Joint difference / saved photon energy | 1.0446478827350775e-11 | 1.0653175742913758e-11 |
| Allowance / saved photon energy | 2.0328860752328997e-11 | 2.1426296174718444e-11 |
| B3f continuum-mixture operational bound | 3.020869003168952e-11 | 1.846001725178548e-9 |
| Individual B3f targets passed | 256/256 | 256/256 |

Both endpoint consistency checks pass. Both positive-mixture operational
budgets pass the unchanged2e-8 target. ISO selects K0 for all256 rows;
ANISO selects K4:92, K3:125, K2:37, K1:2. The degree is chosen from the
prior angular bound at the new S,R, not from observed output error.

The small finite14-versus-saved difference and the continuum-versus-finite14
angular-model difference are distinct. In ANISO, the recorded continuum-minus-
finite14 spatial diagonal is

    (−0.007368368020408411,
      0.006235741462489841,
      0.0011751232178340842) J/m³,

and its energy difference is +4.249665994393581e-5 J/m³. This is a
non-negligible angular-model diagnostic relative to the reconstruction
residual. The passed2e-8 continuum evaluation budget does **not** establish
finite14 agreement with the continuum at2e-8. The code saves this difference
as angular_model_difference and does not replace the old evolved model.
The final report should retain this distinction explicitly, as the root has
already agreed; no extra scientific execution or plot is needed.

Measured finite14 odd-kernel residuals are at most1.3877787807814457e-17;
continuum odd-kernel residuals are at most7.817097663620487e-17. They remain
available as floating diagnostics rather than being described as physical
anisotropic momentum creation.

## 4. Actual B3i algebraic consumption

The adapter receives the saved cold lower-rest/excitation sectors and the new
finite14 radiation state, with zero cQ. Recorded U and J are zero for both
fixtures. Signed pi is computed from state T; no instantaneous source power
is added to it and no excitation transfer is called heat.

The largest raw dh residual is2.220446049250313e-16, normalized by its
positive equation-term scale to1.9576932666551466e-16. ANISO's only nonzero
sigma residual is its reconstructed zz component2.7755575615628914e-17,
normalized to9.385893166190505e-17. drho and dflux differences are zero in
the saved output. These satisfy the unchanged512-epsilon comparison.

The recorded reconstruction-induced hdot differences are
−1.2133533281092943e-21 (ISO) and −1.2260195312390126e-21 (ANISO), in
the fixed core normalization. ANISO's signed sigma derivative difference is
diag(2.6125982659604533e-22,−8.853700221480056e-23,
−1.727224204844613e-22). These are algebraic state-response diagnostics.
No new geometry trajectory or calibrated physical prediction follows from
the two RHS calls.

## 5. Actual visual review

**MIDPOINT_MAP.png: PASS_SCOPED.** Both panels were actually viewed. The left
panel identifies analytic alpha radii and the right operational map radii;
fixture legends, birth-index axes and displayed orders of magnitude agree
with the saved diagnostics. Curves are legible and uncropped. No artificial
zero floor is presented as measured error. Caption should retain the exact-
arithmetic/empirical distinction already fixed in the contract.

**FINAL_STRESS.png: PASS_SCOPED.** Both panels were actually viewed. The left
panel shows signed reconstructed finite14-minus-saved diagonal stress on
saved photon-energy scale, with ISO equal-component and ANISO component-
dependent residuals. The right panel's two observed joint differences lie
below their respective allowances. Labels and markers are legible and no
data are obscured. This figure is the reconstruction check; it does not
plot the separate continuum-minus-finite14 angular-model difference.
The joint norm here is energy plus spatial tensor, with odd moments reported
separately, consistent with the declared theorem.

## Admission and next action

The evidence supports a scoped reconstructed-final-transport result from
actual saved cohort data and numerical consistency in the finite14 model.
It also supports the new positive-angular numerical consumer and the two
state/force-separated B3i algebraic checks. Physical_error remains null,
B3h physical finite absorption remains false, B4/B5 remain NOT_RUN and L4=false.

The two preexecution C9 defects were repaired once before scientific
execution, and the completed raw results validate the affected paths without
tolerance changes. There is no new blocking finding. Stop optional testing
and proceed to source publication, dual backup and selected DAG update while
preserving prior results, failures, budgets and parallel branch ownership.
