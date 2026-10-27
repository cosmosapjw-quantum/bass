# Independent R6 — saved midpoint reconstruction and cohort transport

Decision: **PASS_SCOPED_R6**. Remaining blocking findings: **0**.
Next executable transition: lower-tier implementation/static C9 review, then
the frozen delta-only metered commands under the new 20 CPU / 60 wall-second
allocation. This review does not authorize replay of any historical driver.

Reviewer role: independent source/theory reviewer; no implementation, source
solver, quadrature, test or numerical scientific execution by this reviewer.
Method: read actual restored producer/core/consumer code, independently expand
the RK4 stages and tensor differential, and check the proposed inequalities
against source ownership and mathematical domains. No new strong no-go claim.

## Identity and scope

- Local and freshly read remote BASS HEAD:
  `d7dcd731de1a0c59e5e65db5038c333f5abae0bd`.
- Fresh central AGENTS blob:
  `429a5a13ee75b1222bc50627f8d5973d01dd21c4`; same governing policy.
- Tracked source was clean at review entry. The previously recovered REC NPZ
  and this new unit were the only untracked paths reported by Git.
- Reviewed frozen contract SHA256:
  `70c3bbf83875fb4d1ea59788480e32c051e33cd3636ac8ca5d0bc4699ac793d8`
  (11,802 bytes, after the root's positive-direction guard clarification).
- B3c producer SHA256:
  `1917f49c45cbd637f4d951a21d6e377c3cc3c58798c5e75690317eacabe68044`.
- Unchanged B3f `cohort_input_error.py` SHA256:
  `babd838f36712795ab7d19630e97e7481c42735742f27c235b7640993ead769b`.
- Unchanged B3e `positive_angular.py` SHA256:
  `bdc538446d753c8e757cae3ceea87297db1c52014871e9262c2445c33280093f`.
- Unchanged B3g `geometry.py` SHA256:
  `1a6f4891e3455452cc868bdd41d51d4d1b78af95d6ee50564ab263cb9b2f0b76`.

The selected physical model is the saved manufactured cold, non-tilted,
recoil-free, detached f_plus=0 Bianchi-I finite14 model. The new result is a
reconstruction from actual saved inputs, with a conditional exact-arithmetic
remainder and a separately labelled empirical arithmetic reserve. Physical
source/geometry/rate radii remain null. This scope is scientifically useful
without assuming a calibrated native REC trajectory or a finite Lyα donor.

## 1. Producer placement and exact coordinate identity

Actual `integrate_fixture` uses T(dt/2), source(dt), T(dt/2).
`source_kick` copies `run.q` without changing it. `source_arguments` passes
the source-entry H and S, and the receipt saves them. Thus the top-level
midpoint_H and midpoint_S refer to the complete first transport half-step,
not its fourth RK stage or the global endpoint. The authoritative half-step
duration is source_subflow_duration_tau/2.

For x'=v, v'=f within an arbitrary coupled classical RK4 system, the stage
velocities are v_B=v0+δ f_A/2, v_C=v0+δ f_B/2,
v_D=v0+δ f_C. Direct substitution yields

    x1−x0 = δ v0 + δ²(f_A+f_B+f_C)/6,
    δ(v0+v1)/2 = δ v0 + δ²(f_A+2f_B+2f_C+f_D)/12.

Subtracting proves the contract's correction δ²(f_A−f_D)/12. This is valid
for alpha/h and beta1/sigma1, beta2/sigma2, including coupled stage forces.
No derivative at the completed endpoint is substituted for f_D.

Reconstruction of h_mid from H_mid L/c and sigma_mid=h_mid S_mid has
floating conversion and trace-processing error. The contract explicitly
separates that from the exact-arithmetic identity. It does not claim missing
historical midpoint bytes have been recovered. The alpha-from-N expression
is a distinct nominal diagnostic, as required by the producer's semantics.

## 2. Finite stage-box containment

The unchanged core in Bianchi I and the selected cold/massless model gives

    h' = −h²−Σ sigma_i²/3−(rm+2rg)/6,
    sigma_i' = −3h sigma_i+pi_ii,
    alpha'=h, beta_i'=sigma_i.

Positive packet weights imply 0≤P_ii≤rg, p=rg/3 and
−rg/3≤pi_ii≤2rg/3. Consequently |pi_ii|≤2rg/3.
The exact diagonal characteristic over a stage displacement has
k_i/k_i0=exp(−Δalpha−Δbeta_i), w/w0=exp(−3Δalpha).
For |Δalpha|≤δ Hbar and max_i|Δbeta_i|≤δ Bbar,

    rm(stage) ≤ rm0 exp(3δ Hbar),
    rg(stage) ≤ rg0 exp(δ(4Hbar+Bbar)).

These yield the stated Mh and Ms_i bounds. Each explicit stage is its start
plus either δ/2 or δ times a previous bounded derivative. The specified
conditions therefore establish the four-stage box by induction, including
all three shear entries. They do not assert a continuous-in-time tube.

The root tightened the proposed h0−δ Mh>0 condition to
**h0−δ Mh>Bbar** before the reviewed freeze. This ensures
h+sigma_i>0 throughout the stage box and matches the producer's positive
directional-expansion guard. The current contract includes this condition;
the corresponding clarification is closed, with no outstanding repair.

The third shear coordinate is dependent. In exact arithmetic sigma3' is
−sigma1'−sigma2'=−3h sigma3+pi3 because pi is STF. Apply all three component
box checks; do not regard sigma3 as an independent stored coordinate.
Floating departures from trace-zero remain in the declared empirical scope.

## 3. Acceleration variation and reconstruction radii

For any scalar component with |δv|≤δ M,
|v_d²−v0²|≤(2|v0|+δ M)δ M. Applying this separately to h and each
sigma_i gives exactly the contract's componentwise Vh terms. The density
differences satisfy |rm_d−rm0|≤rm0 expm1(3δ Hbar) and
|rg_d−rg0|≤rg0 expm1(δ(4Hbar+Bbar)); the same bound covers either sign
of the coordinate displacement.

For shear, expand the product difference:

    |h_d sigma_d−h0 sigma0|
      ≤ |h0| δ Ms + |sigma0| δ Mh + δ² Mh Ms.

Together with |pi_d−pi0|≤2rg_max/3+|pi0| this proves Vs_i.
Multiplication by δ²/12 gives the exact-arithmetic trapezoid remainder
bound. The coarse pi-difference estimate is valid; no sampled derivative
envelope is needed. beta3=−beta1−beta2 requires the sum of the two absolute
radii, as specified.

These ideal bounds concern the declared exact-arithmetic finite method.
The saved numerical h_mid and S_mid and historical packet accumulation are
not automatically enclosed by that theorem. The 512-epsilon operational
allowance and inherited eps_fp=2e-12 are clearly empirical, not directed
rounding or physical radii. Reporting analytic-only and operational columns
separately preserves this distinction.

## 4. Mapped tensor and finite14 perturbation bound

Set Φ(v)=(|v|, vv^T/|v|) with continuous value0 at v=0.
For v=r n and perturbation z=a n+b with n·b=0,

    DΦ_v[z] = (a, a nn^T+bn^T+nb^T),
    ||DΦ_v[z]||² = 2a²+2||b||² = 2||z||².

Hence the combined energy/spatial Frobenius kernel is globally
sqrt(2)-Lipschitz, including a straight segment through zero by continuity.
The positive finite14 source measure has unit mass in exact arithmetic:
its degree-two moments and STF S give Σ A_j q_j=1. Thus a map perturbation
eR contributes E n D eR, and a determinant perturbation dD contributes
at most E n dD (b+eR). The contract's U14 and sqrt(2) U14 joint bound follow.

This norm contains the energy scalar and spatial tensor. Exact antipodal
symmetry cancels flux; measured floating odd residuals must remain separately
visible. Enforcing a declared antipodal pair evaluation is permissible when
even stress is unchanged. Nothing permits clipping q or changing its measure.

With beta3=−beta1−beta2, detR=exp(−3Δalpha) in exact arithmetic.
The component logarithm bound R_i expm1(ealpha+ebeta_i) and determinant
bound D expm1(3ealpha) have the correct signs and dimensions. Positive
underflow must retain the inherited typed refusal.

The summed finite14 comparison is on photon-sector energy scales. It tests
reconstruction consistency with the stored finite14 trajectory using the
declared empirical reserve; it does not certify full ODE or physical error.

## 5. Positive angular/B3f composition

The B3e positive-angular theorem and unchanged source card apply at each new
actual reconstructed S,R. Selecting K from its prior bound and the unchanged
1e-8 angular target is a new consumer evaluation. It does not repeat the old
sweep or tune degree against an observed discrepancy. maxK64 is retained.

B3f `ball` is mathematically usable for the reconstruction ball with frozen
source and number, eS=en=0 and the supplied numerical eR. Its historical
PHYSICAL_BALL status must be wrapped by explicit NUMERICAL_RECONSTRUCTION
semantics, as the contract requires. A separate call with absent physical
radii must retain INPUT_ERROR_UNSPECIFIED. The fixed energy card must match
the actual receipt energy; existing prior binding already enforces this.

Positive mixture bounds add A0,L0,B0,U before composition. No cancellation
of bounds, averaging of maps or denominator floor is justified. Missed
2e-8 operational targets retain their actual result. The source-continuum
tensor is postprocessing on the same source and map; its difference from
finite14 is an angular-model diagnostic, not a newly evolved trajectory.

## 6. B3i state/force separation and final admission boundary

The actual adapter uses T00,T0i,Tij in J/m³ with alphaL=(8πG/c⁴)L².
The cQ input is a rate in J/(m³ s), scaled by alphaL L/c into U/J.
Finite source kicks are already in the saved state and new reconstructed
radiation state, so cQ=U=J=0 for this consumption. Pressure and signed pi
are state stress; neither source power nor excitation loss is added as heat.

One unchanged core RHS call per final fixture with explicit Bianchi-I
equations gives the two permitted algebraic geometry checks. The radiation
change is declared and compared independently with the saved radiation.
Neither check evolves a new geometry or admits physical native absorption.

## Review stopping rule

The source identity, algebra, finite-stage assumptions, error meaning and
T/Q ownership are adequate for the bounded implementation. All old resolved
findings are reused. C9 should inspect only changed code/contract paths, and
the final independent review should inspect the actual output and two PNGs.
No additional policy, source census, old campaign replay or future-provider
gate is required by this R6 result.

Whole physical completion remains null; B3h finite absorption=false;
L4=false; historical budgets/failures remain unchanged. No implementation or
numerical execution is claimed by this review.
