# R6 independent contract and mathematical review

**Verdict: PASS_SCOPED.** The finite-error equations, sufficient physical-ball
domain, positive-denominator composition and bounded diagnostic are ready
for implementation. Two precise implementation clarifications are recorded
below. They do not change a physical equation, target, fixture or budget.

Unit: BASS_B3F_COHORT_INPUT_ERROR_20261025.
Workflow: physmath-research-loop 1.0.0.
Parent BASS PR189 HEAD: 6c933f324fe54d1f590bc8ab121032702659e00a.

## Actual material read and independence

The reviewer read the complete new FROZEN_CONTRACT.md, including the
24-row design, focused controls, old-evidence reuse and execution boundary.
The reviewed contract SHA256 is

`531800cfd82c2cdb11d11bbc5b4bd0f154a05c11b7f13e1fcdfaf7250f9eb637`.

Earlier in this task the reviewer read the actual B3e frozen contract,
addendum, positive_angular.py, report, handoff and final C9 review. The new
finite-kernel and sphere-moment derivation was developed independently before
the lower-tier implementation. The copied proof note in theory/ is byte
identical to that independent note, SHA256

`5e58831f81d8e88fd2a9038cea30068ff1b3672fc97592e268a16510f9aad6df`.

No scientific Python, quadrature, test, solver, symbolic evaluator, IVP or
old campaign was run by this reviewer. No implementation or renderer was
edited. This R6 does not admit unobserved numerical output. Different-model
scientific review is NOT_RUN.

## Mathematical checks

1. **Even massless stress kernel.** G(v)=blockdiag(|v|,vv^T/|v|) has norm
   sqrt(2)|v|. The exact two-vector difference has squared norm
   2||v-w||^2-2|v||w|(1-cosθ)^2. Its continuous extension at zero is valid,
   and parallel positive vectors establish the pointwise sqrt(2) constant.
   The odd flux has already cancelled by the even source; no one-ray flux
   matrix is silently assigned this smaller constant.
2. **Source-aware map error.** Positivity and <q>=1 justify Cauchy–Schwarz
   in q dΩ/(4π), yielding sqrt(tr(ΔR H ΔR^T)) for energy and sqrt(2) times
   that quantity for the tensor. This works for nonsymmetric/noncommuting R.
3. **Finite source error.** The trace-free contraction of the sixth sphere
   moment is [2 tr(V²)tr C+8 tr(V²C)]/105. Its square root controls energy;
   sqrt(2) times it controls the tensor. There is no sign assumption on V.
4. **Paired physical prefactors.** Both source/map orders are valid. The two
   physical decompositions W0(T1−T0)+(W1−W0)T1 and
   W1(T1−T0)+(W1−W0)T0 justify the stated minimum. The determinant is part
   of W=E_b n_b detR and its mixed terms are retained.
5. **Uniform determinant radius.** Exact determinant multilinearity gives
   tr(cof(R0)^T ΔR)+tr(cof(ΔR)^T R0)+detΔR. Nuclear/operator norm duality
   bounds these by e2(σ)eR, e1(σ)eR² and eR³. The resulting finite polynomial
   is valid for general R and is attained in the increasing aligned SVD
   direction. It is not a first-order derivative estimate.
6. **Whole-ball domain.** Singular-value perturbation supplies a−eR and
   b+eR; the positive determinant follows by continuity along R0+tΔR.
   The source margin uses ||ΔS||2<=||ΔS||F together with symmetric/STF
   perturbations. The numerical positivity and map conditions are sufficient
   for the entire stated ball and stronger than validity of one endpoint.
7. **Uniform source radius.** tr C1<=Σ(σ_i+eR)² and
   tr(ΔS² C1)<=(b+eR)²||ΔS||F² give the stated h_ball. The two U_ball
   branches follow from the two physical prefactor decompositions.
8. **Denominator and operational budget.** The exact lower energy is
   L0−U. The empirical nominal floating reserve enters as the absolute term
   eps_fp B0 before division by that lower energy. The Umax algebra is
   correct. This conditional operational estimate is clearly separated
   from an interval certificate and from actual physical history admission.
9. **Mixtures and coordinates.** Positive absolute budgets add in a common
   final frame while signed tensor components are summed. Proper independent
   birth/final rotations preserve all scalar bounds and transform the tensor
   spatial block as stated. Averaged R/S or cancellation of error budgets
   is not used.

## Clarification R6-C1: ball containment and paired-bound dominance

The contract's gate that a physical ball covers its paired bound is valid,
provided the actual endpoint pair is contained in the supplied ball. Explicitly
check ||R1−R0||2<=eR, ||S1−S0||F<=eS and |n1−n0|<=en on their declared
scales. A valid ball with an unrelated, noncontained pair cannot make this
claim. Diagnostic radii computed from the actual differences supply this
containment; focused invalid cases should retain an outside-ball refusal.

For a contained pair,

    h_pair <= r0+s1 <= h_ball,
    |W1-W0| <= deltaW, W1 <= Wmax, F_up1 <= b+eR.

Therefore each corresponding pair branch is bounded by its ball branch:

    W0*h_pair+|deltaW_actual|*F_up1
      <= W0*h_ball+deltaW*(b+eR),
    W1*h_pair+|deltaW_actual|*F_up0
      <= Wmax*h_ball+deltaW*F_up0.

Taking the minima preserves U_pair<=U_ball. The implementation may retain
this gate. Compare dimensionful U values with the stated allowance times a
positive physical energy scale. Do not normalize by a possibly zero U.

## Clarification R6-C2: nominal positivity versus zero true density

The certificate requires nominal n0>0. The physical ball en<=n0 permits
actual n1=0 at its boundary. Such a state is valid for the absolute paired
tensor bound, with W1=0. A relative error divided by its zero energy is
unavailable, and the lower-denominator check must preserve that fact.

Interpret the focused-test phrase "nonpositive-density errors" as rejecting
nonpositive nominal density for this relative-certificate interface and
negative actual density. Do not reject a zero-density actual state as a
physical impossibility. An all-zero mixture likewise has no relative energy
denominator. These are domain/status distinctions, not altered tolerances.

## Discriminating numerical design and stopping transition

The frozen 21 paired rows, 2 frame comparisons and 1 positive mixture give
24 labelled output rows. Reusing stored nominal G3/G5 moments and analytic
density/scaling/isotropic laws avoids repeating the parent campaign. Only
the eight new P3/P4 endpoints require new64/96 references. The two GL32x64
packet checks test unchanged mapping against their same-rule direct moments;
they do not claim a new continuum reference.

The omitted-det P2 control is substantive: its actual physical scaling is
(1−eps)^4, whereas its mutant retains only (1−eps). Source-zero P5 pairs
remain physically admissible although their symmetric whole source ball is
not certified. Those expected sufficient-condition refusals must remain
separate from a failure of the actual paired tensor bound.

The strongest scoped claim is a finite input-to-observable theorem and its
implemented sufficient numerical budget for supplied data. Actual owner
cohort maps and calibrated physical radii remain OPEN_INPUT. REC136's Ks
operator norm alone does not supply those radii. No new no-go, universal
novelty or full BASS physical-completion claim is admitted.

**PASS → next action:** lower-tier implementation under this contract and
these clarifications, followed by read-only preexecution code review and
the actual S0 Git/Drive/Dropbox preparation ACK. Scientific Python starts
only after the controller's explicit GO. Final scientific admission still
requires actual new raw data, figure inspection and C9 review. No additional
optional theory extension or repeated R6 is needed for unchanged equations.
