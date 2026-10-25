# N5 H1 ground spontaneous RR consumer — frozen contract

Authority: root Astra, 2026-10-25. Workflow physmath-research-loop 1.0.0.
Unit `CR_N5_H1_GROUND_RR_MILNE_FINITE_CHAIN`; consumer `N5_C23D_H1_RR_MILNE_V1`.
Base BASS_CR PR104 Documents `257007cc708d0db403ec2ff0c741e4a10b6207ab`,
Science `5eb895abbacce1642c451fd3fdfd2f776783871f`.
New path `research/cr_n5_rr_milne_20261025/`; all new run outputs create-only.

## 1. Contribution and reuse

Bind the existing channel-resolved Milne relation and existing C23B H I
photoionization fit to PR104's eight saved electron-energy finite chains.
Compute spontaneous H1 ground capture competing with first entry and the
existing H1 excitation event. Resolve rare-event probabilities, time and
energy rewards, and stable paired changes relative to saved PR104 solutions.
The contribution is this consumer calculation and its bounded finite-chain
response. Milne, Saha, the Verner fit, earlier thermal quadratures, source
quadratures, EE/EI/neutral generators and old solutions are reused evidence.

REI PR151 authority `8a4f5df46f6e3058f5e685b85cc1cf3c20926368`, Unit8
`research/microphysics_r9_20261015/unit8_remaining_bridges_20261016/`, supplies
the established ground-channel Milne convention and saved thermal references.
Read, but do not import/execute, its `li_thermal_rates.py`: top-level GL creation
and all historical quadratures are outside this run. C23E total RR is a
different all-level closure and must not be added to the ground capture rate.
The exact native C23B PI module and source table are to be copied unchanged,
identified in INPUT_MANIFEST, and used only for point evaluations.

## 2. Physical contract

Reuse T=10000 K, theta=0.8617333262145178 eV, ne=0.14 cm^-3,
prescribed lnLambda=20, stationary isotropic common-temperature baths,
HI/HII/HeI/HeII/HeIII=(0.9,0.1,0.07,0.02,0.01) cm^-3, closed box/no escape.
H1 and He4 assignments remain conditional. Missing isotope densities are null.
Exposure10000 proper seconds defines the same impulsive initial population;
it is not a chemistry integration. The initial 0<W<10 eV selection is not a
ceiling on subsequent energies. First entry is a stopping diagnostic.

The NEW RR channel is zero-recoil, stationary-heavy-target, nonrelativistic
H1+ + e -> H1(1s) + photon. Electron kinetic energy E is the bath-frame energy
under that heavy-target convention. This does not include finite-proton-mass
relative-velocity averaging or recoil. Use native fit I=13.60 eV and electronic
weights g_H=2, g_p=1. Electron spin2/photon polarization2 enter the Milne
balance consistently; d=2*g_p/g_H=1. Nuclear spin cancels for the same isotope.
Do not replace I by a different spectroscopic threshold.

Use m_e=9.1093837015e-31 kg, eV_J=1.602176634e-19 J/eV, c=299792458 m/s,
consistent with the frozen PR104 consumer. REI's m_e=9.1093837139e-31 kg is
different: a saved thermal alpha reference maps by (m_REI/m_consumer)^(3/2)
when all other source/temperature constants match; record this mapping.

The channel is the spontaneous COMPONENT. Actual photon occupation,
stimulated hazard, total all-level RR and post-capture PI feedback are null
unless separately supplied. Calculating this component does not assert an
empty physical photon box. Store emitted photons in a retained energy ledger;
their future transport/reabsorption is a later coupling dependency.

For E>0 and epsilon=E+I in the native PI support:

    sigma_RR_cm2(E) = sigma_PI_cm2(epsilon) * epsilon^2 / (d*mec2_eV*E)
    v_cm_s(E) = 100*sqrt(2*E*eV_J/m_e)
    lambda_RR_s_inverse(E) = n_HII_cm3 * v_cm_s(E) * sigma_RR_cm2(E)

Here n_HII=0.1, not the electron density. Unsupported source, energy, density,
or isotope inputs must fail or remain null, never silently become zero.
An explicitly supplied n_HII=0 is an admissible control with exactly zero
component rate. E=0 is outside this differential interface; no artificial
floor is introduced. Active domain starts at q=chi*theta>0.

## 3. Saved inputs and new numerical map

Recover, do not regenerate, all eight NPZ under the verified PR104 canonical:
`recovered_neutral_20261025/research/cr_n5_neutral_elastic_20261025/runs/n5_neutral_primary_20261025_v1/`.
q/theta in {1.5,3}; upper E/theta in {40,80}; nominal N in {1024,2048}.
Use stored E, pi, Q, K0 bands, first6 and bath6 RHS, source_z and active masks,
old u_s,u_p,u_entry,t,r_s,r_p,H and old MFPT without old primary replay.
Keep the three original384-atom source tables and their saved projections.

K0=-Q_active^T+Lambda_CE is the saved backward killed operator.
Let lambda=lambda_RR(E_active), Lambda=diag(lambda), K=K0+Lambda.
Only this diagonal and new RHS change. Old off-diagonal bands, generator,
source arrays, q and reflecting upper boundary are exact reused inputs.

Per case, solve 17 physical RHS:

* old first6 (two CE probabilities, entry probability, stop time, two CE
  incoming-energy rewards), using K;
* lambda and lambda*E, giving p_RR and r_RR;
* six unchanged bath RHS, giving signed six-bath expected gains H;
* three conditional-time RHS u_s,u_p,p_RR, giving v_s,v_p,v_RR.

Also solve three response/diagnostic RHS per case:

    delta_CE = -K^-1 [lambda * (u_s_old+u_p_old)]
    delta_time = -K^-1 [lambda * t_old]
    w = K0^-1 lambda

These are new RHS/changed-operator solves, not restoration replay. Total
planned new primary RHS=20*8=160. Report actual counts, including failures.
Do not obtain tiny paired changes by subtracting almost equal old/new values;
subtraction may be reported only as a diagnostic, with inherited roundoff.

## 4. Probability, energy and comparison identities

For a finite transient chain, K0 and K are nonsingular M-matrices. Their
nonnegative inverses imply p_RR>=0 and delta_CE,delta_time<=0.
Writing eta=max(w), the identity w-p_RR=K^-1 Lambda w yields

    w/(1+eta) <= p_RR <= w.

This is an exact componentwise finite-chain bound; it is not a continuum or
physical-model error certificate. Report eta and source-weighted bounds.
The positive stopping partition is u_s+u_p+u_entry+p_RR=1 at active nodes.
Saved initial mass on q enters immediately; inactive initial mass retains its
own energy and receives no newly invented sub-q RR continuation.

Per RR event: Delta N_e=-1, Delta N_HII=-1, Delta N_HI=+1;
electric charge and H1 nuclei are conserved. Rewards are electron removal E,
retained photon +(E+I), atomic internal change -I. Therefore

    photon_RR = r_RR + I*p_RR; internal_RR = -I*p_RR.

Retain signs. The full stopped energy account is initial kinetic E equals
six bath gains + entry energy + CE outgoing kinetic + CE internal gap
10.20435eV + RR photon + RR internal change. At source level include exact
saved q mass and inactive-own-energy terms. RR radiation is not bath heat.
For conditional RR energy/time divide corresponding positive weighted
moments by RR probability only where it is strictly positive; otherwise null.
Free-proton/electron/population rewards are an expected-event ledger; frozen
coefficients do not execute composition or temperature feedback.

## 5. Frozen checks and tolerances

Reuse unchanged old validation. New controls exercise the adapter, units,
weights, support rejection, missing-null rejection, n_HII=0, density scaling,
reaction stoichiometry, signed event energy, and a small analytic killed chain.
Include mutations for wrong target density, factor2 and binding-energy sign;
an expected rejection is a passing control, not a production failure.

Primary thresholds: per-RHS scaled backward residual<=2e-12;
partition maxabs<=2e-8; scaled energy residual<=2e-8;
probabilities in [0,1] with inherited2e-10 floating tolerance, while p_RR must
be strictly positive at positive density. Reused identities must match.
Rare-response bound violations are judged relative to the relevant small
positive quantity with 5e-10 tolerance; do not hide errors under unit absolute
floors. Inherited old solution uncertainty is kept separate for paired checks.

For eachchi,z compare1024/2048 at R40 and80, and R40/R80 at N2048:
relative grid difference<=0.005 and relative upper-domain difference<=1e-5
for P_RR, conditionalRRenergy/time, RR photon/internal rewards, meanstop and
CE probability. Stable paired CE/time differences use relative grid<=0.01
and relative upper-domain<=1e-5. These are observed comparisons, not rigorous
global truncation bounds. global_error_bound/global_completion_percent=null.

Independent C9: separate reviewer, no production module imports. Decimal70
or equivalent independent arithmetic on both R80,N2048 cases, all20RHS each,
and independently computed selected RR coefficients. Compare each RHS by its
own infinity norm with tolerance5e-10; do not scale rare probabilities by1.
Inspect signed energy terms and effect sign. High precision comparison of
the intended d0+lambda and stored rounded K is classified with backward and
observable evidence; no hash-equality requirement for numerical solutions.
Use the old case's source projections as immutable inputs, not reprojected.

## 6. Execution and handoff

New input ID `n5_rr_milne_input_20261025_v1`.
Runs `n5_rr_milne_controls_20261025_v1`, `n5_rr_milne_primary_20261025_v1`,
`n5_rr_milne_c9_20261025_v1`, `n5_rr_milne_saved_plot_20261025_v1`.
Inherited known worker34.234445114 CPU seconds; globaltotal/remaining/money=null.
New unit total ceiling60CPU seconds including failed attempts; controls5CPU/20wall,
primary10CPU/40wall, independentreview10CPU/40wall, saved-onlyplot5CPU/20wall.
Do not reset budgets or overwrite failed outputs. Costs for mechanical
recovery/serialization/network and external symbolic tools are separate.
Native threads1; actual cgroup/RAM/affinity admission and own-task lease before
each child. Limit512MiB when supported. ProtectCPU55 if it exists; otherwise
record actual reserved coordinator CPU and available worker/reviewer CPUs.
External NCP runtime/lease remain UNOBSERVED. No unrelated processes are killed.

Root owns criteria, scientific decisions and publication; lower-tier executor
implements, performs prescribed checks/runs and reports raw outcomes. A fresh
Astra independent reviewer determines C9. Stop and return on missing immutable
input, ambiguous criterion, substantive scientific failure or exhausted budget.
Repairs require a concrete diagnosis; unchanged optional suites are not rerun.

Plot source-weighted six finest rows from saved outputs only: rare RR chance,
conditional RR photon energy, and stable paired time/CE effects with units.
Read the actual plot for semantic/legibility review. Do not reconstruct raw
MTCS curves or expose dense private arrays in public Git.

Each R1–R10/C1–C10 row carries EXECUTION/PUBLICATION/BACKUP/DAG independently.
Publish owned additive paths on a new branch from fixed PR104 using expected
SHA. Preserve live central owner changes. Canonical public integrated results
and private backup inputs are distinct. Existing rejected neutral terminal
must not be reconstructed or included as an upload workaround. Its upload
remains separately blocked; new unit artifacts do not change that status.

N4/N5 remain PARTIAL/OPEN; N6/N7 are not activated by this scoped component.
Maintain non-tilted LRS/fullFrobenius, signed amplitude/norm/cancellation,
atomic isotropic closure versus nonbaryonic Vlasov stress, high-energy nuclear
and general triaxial/tilted/polarized CMB HOLD, original networkPNG
NOT_RECOVERED_NOT_READ. No new strong no-go is proposed (NG1–NG7 not applicable).

## 7. Pre-execution R6 clarifications

The intended operator is the real sum of the stored K0 coefficients and the
new lambda. Record binary64 diagonal-addition loss separately. Independent
Decimal70 review must form Decimal(K0)+Decimal(lambda), rather than merely
copying the rounded new diagonal; use the frozen per-RHS relative criterion.
The bound is about that intended finite chain. Use existing5e-10 comparison
allowance for rounded primary bound checks and report its observed margins.

The event-level RR photon/internal/electron identity must also pass a
relative5e-13 control using its own RR-scale quantities. The gross2e-8 energy
criterion alone cannot detect a sign error in such a small RR component.
Wrong-sign mutation is checked at event scale. Do not add the diagnostic
electron-removal reward as a third final energy reservoir.

Current observed host: affinity0..8, quota8CPUs, RAM8GiB. ReserveCPU8 for the
coordinator, workerCPU0, independentreviewCPU1; CPU55 is unavailable.
R3 source table SHA256 a53e73b0af4cc6b801aef67b84bd964e3ed8c9c4992f214e4a69dc7e4443f389.
C23B module SHA25671b7e3a6b6f1c68ec15bcb19b98014bc025ef595f53df29703f11e25f36f4a8d.
Both are present under current_intake_20261025/source_theory/reuse_c23b/.
The saved REI10000K ground alpha is1.5893516133029456e-13cm3/s; the original
row and independently admitted review are recovered without quadrature.
