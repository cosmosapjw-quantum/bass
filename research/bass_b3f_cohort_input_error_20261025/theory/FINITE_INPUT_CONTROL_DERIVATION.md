# Independent derivation: finite input control for BASS mapped cohorts

Status: derived mathematical result and proposed next bounded unit. This note
does not admit a new numerical result or an actual history error. The parent
controller owns the frozen contract and scientific admission. Workflow:
physmath-research-loop 1.0.0. Code and previous numerical evidence are read-only.

## 1. Options and recommended dependency

1. Bind actual B3c birth tensors, maps, amplitudes, frame/clock and support.
   This is the closest physical dependency when a small owner export exists.
   The source inventory is checking availability; no old archive or IVP is
   needed merely to repeat a completed result.
2. Propagate supplied finite errors in those inputs into the stress tensor,
   then combine them with B3e angular error. This is executable without an
   invented physical history, closes the missing error-composition formula,
   and gives an explicit positive denominator and acceptance budget.
3. Build a temporal cohort quadrature for prescribed generator histories.
   This adds a clock, temporal regularity and source-support contract. Defer
   implementation until those owner inputs exist. A conditional generator
   error formula is given below as the precise future connection.

Recommend option 2 if option 1 remains unavailable. New REC136 KS01 supplies
a retarded-history response operator diagnostic. Its physical history error,
reference/endpoint/curvature and absolute uncertainty remain null in the
currently read owner report. An operator norm by itself supplies neither a
physical history radius nor a BASS momentum-map perturbation radius.

## 2. Definitions and inherited physical meaning

Use the B3e fixed birth sphere label n, normalized average <.>, and

    q_S(n) = 1 + n^T S n,
    S = S^T, tr S = 0, I+S >= 0,
    H_S = I/3 + 2S/15 = <q_S nn^T>.

Then q is nonnegative, <q>=1, and H is positive definite. The declared map
R has det R>0. Shape stress and physical stress are

    G(v) = blockdiag(|v|, vv^T/|v|), G(0)=0,
    T(S,R) = <q_S(n) G(Rn)>,
    Q(S,R,n_b,E_b) = W T(S,R), W=E_b n_b det R >= 0.

The flux is zero by the even birth source. G is the even block-diagonal
integrand used after the odd flux cancellation, not the full one-ray stress
matrix with off-diagonal flux. The Euclidean Frobenius norm used here is
invariant under spatial orthogonal frame changes, not a Lorentz scalar.

The state map keeps E=c|p| once. W includes the separately declared number
dilution det R; no event rate, source clock, donor, bath, finite bandwidth,
Source/U/J/PiRate or native absorption is introduced by these formulas.

For a=σ_min R, b=σ_max R, the inherited B3e bracket is

    F_lo(S,R) = (tr(R H_S R^T)+ab)/(a+b),
    F_up(S,R) = sqrt(tr(R H_S R^T)),
    0 < F_lo <= F=<q_S |Rn|> <= F_up.

Also ||T||_F <= sqrt(2) F <= sqrt(2) F_up. This follows from
||G(v)||_F=sqrt(2)|v| and positivity of q.

## 3. Global finite map bound

Let r=|v|, s=|w|, and c=(v.w)/(rs) when rs>0. Direct multiplication gives

    ||G(v)-G(w)||_F^2
      = 2(r-s)^2 + 2rs(1-c^2)
      = 2||v-w||^2 - 2rs(1-c)^2
      <= 2||v-w||^2.

The formula extends continuously when v or w is zero. Therefore G is
globally sqrt(2)-Lipschitz, without an inverse small-singular-value factor.
Separately, ||v|-|w|| <= ||v-w||.

For ΔR=R1-R0 and one fixed admissible S, Jensen/Cauchy-Schwarz with positive
probability measure q_S dΩ/(4π) yields

    d_R(S,ΔR) = sqrt(tr(ΔR H_S ΔR^T)),
    |F(S,R1)-F(S,R0)| <= d_R,
    ||T(S,R1)-T(S,R0)||_F <= sqrt(2) d_R.

This retains source anisotropy and noncommuting map components. If only a
spectral radius ||ΔR||_2<=ε_R is supplied, d_R<=ε_R because tr H_S=1.
The coefficient sqrt(2) is sharp for the pointwise map, though no optimal
cohort-level constant is claimed.

## 4. Finite source bound from the exact sixth sphere moment

Let V=S1-S0 be symmetric and trace free, C=R^T R. Since T is linear in S,

    Δ_S T = <(n^T V n) G(Rn)>.

The standard isotropic moments, contracted explicitly, give

    <(n^T V n)^2> = 2 tr(V^2)/15,
    <(n^T V n)^2 (n^T C n)>
      = [2 tr(V^2) tr C + 8 tr(V^2 C)]/105.

For general symmetric V before imposing tr V=0, the numerator is

    (tr V)^2 tr C + 2 tr(V^2) tr C
      + 4 tr V tr(VC) + 8 tr(V^2 C).

The denominator is 3*5*7=105. This is a contraction of the 15 pairings of
the sixth sphere moment. Each term in the trace-free expression is
nonnegative because V^2 and C are positive semidefinite.

Define

    d_S(R,V) = sqrt([2 tr(V^2) tr C + 8 tr(V^2 C)]/105).

Then Cauchy-Schwarz on the normalized sphere gives

    |Δ_S F| <= <|n^T V n| |Rn|> <= d_S,
    ||Δ_S T||_F <= sqrt(2) d_S.

Two simpler valid alternatives are

    d_S <= b sqrt(2/15) ||V||_F,
    |Δ_S F|, ||Δ_S T||_F/sqrt(2)
      <= sqrt(2/45) ||V||_F ||R||_F.

The second line is a separate product Cauchy-Schwarz bound and need not be
ordered against d_S in all orientations. Take the minimum only of bounds
whose individual assumptions have been checked. The sixth-moment bound is
already explicit and sufficient for one bounded implementation.

For the analytic isotropic-map oracle R=a O, O proper orthogonal,

    F=a, P=a O H_S O^T,
    Δ_S F=0, Δ_S P=(2a/15) O V O^T.

This sharp linear oracle is useful for testing the general finite bound;
the general bound need not saturate it.

## 5. Paired input changes and explicit physical prefactor

For two supplied admissible pairs, ΔS=S1-S0 and ΔR=R1-R0, define

    d_01 = d_R(S0,ΔR) + d_S(R1,ΔS),
    d_10 = d_R(S1,ΔR) + d_S(R0,ΔS),
    d = min(d_01,d_10).

These are the two legal orders of changing source and map. Each provides
|F1-F0|<=d and ||T1-T0||_F<=sqrt(2)d. Taking their minimum is safe; no
average source/map or cancellation assumption is introduced.

Put W_i=E_b,i n_b,i det R_i and δW=|W1-W0|. Define

    U_pair = min(W1 d + δW F_up,0,
                 W0 d + δW F_up,1).

The first expression uses Q1-Q0=W1(T1-T0)+(W1-W0)T0; the second uses
Q1-Q0=W0(T1-T0)+(W1-W0)T1. Therefore

    |Q1_00-Q0_00| <= U_pair,
    ||Q1-Q0||_F <= sqrt(2) U_pair.

The determinant must enter W_i. Treating map changes as shape changes while
freezing det R changes the declared physical number dilution. The existing
line card fixes E_b in the proposed diagnostic; the formula allows an
independently supplied nonnegative energy only as a stated generalization.

## 6. Input-radius envelope when the true pair is not supplied

Let nominal S0,R0,n0 be supplied and admissible. A radius contract may supply

    ||Rtrue-R0||_2 <= ε_R,
    ||Strue-S0||_F <= ε_S,
    |ntrue-n0| <= ε_n,
    q_true >= 0, tr Strue=0, E_b fixed.

The last source admissibility is an assumption on the actual state; a ball
around a source with angular zeros is not automatically entirely positive.
No source projection/clipping establishes it. Require ε_R<a0. Then
every admissible perturbed R has positive determinant and

    x=ε_R/a0,
    D0(1-x)^3 <= det Rtrue <= D0(1+x)^3,
    |det Rtrue-D0| <= δD=D0[(1+x)^3-1].

Proof: Rtrue=R0(I+R0^{-1}ΔR), ||R0^{-1}ΔR||_2<=x<1. All singular values
of I+X lie in [1-x,1+x], and its determinant remains positive along I+tX.
Products give the bounds. The upper deviation dominates the lower one.

For nonnegative actual density and supplied ε_n, use the safe absolute
weight radius

    ε_W = E_b [(n0+ε_n) δD + D0 ε_n].

This follows from ntrue Dtrue-n0D0=(ntrue-n0)D0+ntrue(Dtrue-D0).
There is no assertion that the actual n equals an envelope endpoint.

The source-map shape radius

    d_rad = ε_R + (b0+ε_R) sqrt(2/15) ε_S

follows by first changing R at S0 and then S at the unknown Rtrue, whose
maximum singular value is bounded by b0+ε_R. Thus

    U_rad = (W0+ε_W) d_rad + ε_W F_up,0

bounds the energy difference and sqrt(2) U_rad bounds the tensor difference.
The supplied radius is a mathematical input, not a generated physical
uncertainty. Missing owner radii must remain null/OPEN_INPUT and cannot
produce an admitted physical bound.

The current numerical B3e domain remains σ_max<=1 and condition ratio<=2.
For a radius envelope intended to certify this domain for every admitted
actual R, additionally require b0+ε_R<=1 and
(b0+ε_R)/(a0-ε_R)<=2. Otherwise the theorem still gives its finite bound but
the existing numerical interface's declared domain has not been certified.

## 7. Positive energy denominator and composition with angular error

Let U be either valid pair or radius bound, L0=W0 F_lo,0, and A0=W0 B_T,0
be the inherited ideal-node B3e angular tensor bound on the nominal state.
If L0>U, then

    Qtrue_00 >= L_true = L0-U > 0,
    ||Qangular,0-Qtrue||_F/Qtrue_00
      <= (A0+sqrt(2)U)/(L0-U).

A nonpositive L_true means the relative claim has no positive denominator;
retain the absolute bound and mark that relative admission unavailable.
Do not replace the denominator by an invented positive floor.

If A0<=αL0, sufficient admission at ideal relative target τ>α is

    U/L0 <= (τ-α)/(sqrt(2)+τ).

The fixed scientific target is 2e-8 and the inherited nominal angular
allocation α=1e-8. The empirical binary64 nominal reserve must be converted
to an absolute error before changing denominators. With ε_fp=2e-12 and the
conditional nominal bound A0+ε_fp W0 Fnom, use the safe upper reserve
ε_fp W0 F_up,0. The operational sufficient certificate is

    C_num=(A0+sqrt(2)U+ε_fp W0 F_up,0)/(L0-U).

It is not C_ideal+ε_fp. For target τ, the resulting scalar budget is

    U_max=[τ L0-A0-ε_fp W0 F_up,0]/(sqrt(2)+τ),

provided the numerator is nonnegative. A negative numerator means that no
nonnegative U satisfies this sufficient gate; it is not clipped to zero.
This empirical reserve does not transform binary64 arithmetic into an
interval certificate. The observed total residual must independently pass
the unchanged 2e-8 target, and truth-reference comparison allowance remains
separate from physical input uncertainty.

## 8. Positive mixtures and independent frames

All physical tensors must be expressed in a common final frame. For cohorts
a, sum signed tensors and let

    L0_mix = sum L0,a, U_mix=sum U_a, A_mix=sum A_a.

Then the exact same total formula applies:

    L_true,mix >= L0_mix-U_mix,
    relative bound <= (A_mix+sqrt(2)U_mix)/(L0_mix-U_mix).

It is not necessary to demand equal per-cohort relative input tolerances;
positive absolute budgets can be allocated by the supplied physical weights.
Do not average R, S or determinant across cohorts. A zero-density cohort
contributes zero; an all-zero total has undefined relative error.

For the operational floating reserve, add ε_fp sum_a(W0,a F_up,0,a) to the
numerator before dividing by L0_mix-U_mix, conditional on the corresponding
per-cohort empirical nominal bounds.

For common proper birth/final coordinate changes,

    S_i' = O_b S_i O_b^T,
    R_i' = O_f R_i O_b^T,
    ΔR' = O_f ΔR O_b^T, ΔS'=O_b ΔS O_b^T.

Every scalar d_R,d_S,U,L and the spectral/Frobenius radii is invariant.
Tensor blocks transform by diag(1,O_f). Comparing states in different
frames requires the supplied frame map before these differences are formed.

## 9. Optional continuous-generator connection, not a new IVP

Suppose actual Rdot=-A R and approximation Rhatdot=-Ahat Rhat+rhat are
independently supplied in the same frame/clock convention. Error E=R-Rhat
satisfies

    Edot=-A E-(A-Ahat)Rhat-rhat.

With the evolution operator Φ of -A,

    ||E(t)||_2 <= ||Φ(t,t0)||_2 ||E(t0)||_2
      + integral ||Φ(t,s)||_2
          [||A(s)-Ahat(s)||_2 ||Rhat(s)||_2 + ||rhat(s)||_2] ds.

One sufficient propagator envelope is
||Φ(t,s)||_2<=exp(integral_s^t λ_max[-(A+A^T)/2] du).
This identifies what an owner must supply to turn a time/feedback error
into ε_R. No current REC operator norm is substituted for this generator
error without a separately derived map between the two physical objects.
Do not implement or run a new IVP for this optional formula in this unit.

## 10. Suggested bounded diagnostic and independent review obligations

Use one new noncommuting nominal fixture with margin inside the B3e domain,
for example R0=Oz diag(.55,.70,.90) Ox^T and
S0=Oy diag(.40,-.10,-.30) Oy^T, n0=1, the existing E_b card.
Perturb map, source, density separately and jointly at explicitly declared
small h values bracketing the fixed 2e-8 admission boundary. These are
manufactured input perturbations, not recovered physical error bars.

Useful exact controls are isotropic-map/source changes, pure isotropic
redshift with its D=a^3 prefactor, zero perturbation, two independent proper
frame rotations, and one positive mixture. Adversarial controls should
detect omitting detR variation, omitting source normalization, and accepting
null physical radii as zero. Retain true zero values and all failed gates.

Validate the mathematical formula independently (sphere moments, pointwise
identity, isotropic oracle and budget algebra), then inspect implementation
and actual new raw tensors/figures. No prior B3d/B3e campaign replay is
needed. This result closes finite error composition for supplied inputs;
actual history binding and calibrated physical error radii stay OPEN_INPUT.

No broad novelty, impossibility or global-optimality result is proposed.
NG1–NG7 strong-no-go admission is NOT_APPLICABLE. The exact mathematical
claims above follow from the displayed finite identities, positivity and
Cauchy-Schwarz; finite numerical tests cross-check implementation and do
not replace those proofs.

## 11. Independent review of the controller's sharper uniform-ball contract

The controller proposed the following sharper uniform-ball formulas after
the derivation above. They are mathematically valid and supersede the more
conservative radius formulas in Section 6 when this specific ball is used.
This review does not alter code or admit numerical evidence.

Let the actual uncertainty set consist of

    Rtrue=R0+E, ||E||_2<=dR,
    Strue=S0+V, V=V^T, tr V=0, ||V||_F<=dS,
    |ntrue-n0|<=dn.

Require dR,dS,dn finite and nonnegative, nominal admissibility, and

    dR<a,
    b+dR<=1,
    (b+dR)/(a-dR)<=2,
    dS<=1+lambda_min(S0),
    dn<=n0.

The first three conditions certify the existing positive-determinant,
outgoing and condition-ratio map domain for the whole ball. The fourth
uses ||V||_2<=||V||_F and Weyl's inequality to guarantee I+Strue>=0.
The fifth guarantees nonnegative density. The source ball must explicitly
retain the symmetric/STF constraints; the norm bound alone does not imply
the normalization <q>=1. A boundary source with a zero angular direction
can have dS=0 in this sufficient whole-ball certificate. The earlier paired
bound continues to allow admissible nonzero source changes at that boundary.

### Sharper determinant radius

Let σ1,σ2,σ3 be the singular values of R0 and D0=det R0>0. Set

    e1=σ1+σ2+σ3,
    e2=σ1σ2+σ1σ3+σ2σ3,
    δD=e2*dR+e1*dR^2+dR^3.

For any 3x3 A,E, determinant multilinearity gives the exact expansion

    det(A+E)-det A
      = tr(cof(A)^T E)+tr(cof(E)^T A)+det E.

Schatten duality yields

    |tr(cof(A)^T E)| <= ||cof(A)||_* ||E||_2 <= e2*dR,
    |tr(cof(E)^T A)| <= ||cof(E)||_2 ||A||_* <= dR^2*e1,
    |det E| <= dR^3.

The cofactor singular values are σ1σ2,σ1σ3,σ2σ3; for a perturbation whose
singular values are all <=dR, its cofactor operator norm is <=dR^2. Thus
|det Rtrue-D0|<=δD. The upper deviation is attained by E=dR U V^T in an
SVD R0=U diag(σ) V^T with det(UV^T)=1. This explains the product identity
δD=product_i(σ_i+dR)-product_i σ_i. No commuting or symmetric R is assumed.

The positive-map determinant conclusion uses dR<a; the absolute expansion
bound itself is algebraic and does not require that restriction.

### Uniform source and shape radius

For Ctrue=Rtrue^T Rtrue, singular-value perturbation gives

    tr Ctrue <= sum_i (σ_i+dR)^2,
    ||Ctrue||_2 <= (b+dR)^2.

Since V^2 is positive semidefinite,
tr(V^2 Ctrue)<=||Ctrue||_2 tr(V^2). Substitution into the exact sixth moment
therefore yields

    h_source = dS sqrt([2 sum_i(σ_i+dR)^2+8(b+dR)^2]/105),
    h = dR+h_source.

Then |Ftrue-F0|<=h and ||Ttrue-T0||_F<=sqrt(2)h uniformly on the ball.

### Physical prefactor and the two legal decompositions

For the unchanged fixed E_b,

    W0=E_b n0 D0,
    δW=E_b[n0 δD+dn(D0+δD)],
    Wmax=E_b(n0+dn)(D0+δD)=W0+δW.

Both |Wtrue-W0|<=δW and Wtrue<=Wmax hold. Positivity and <qtrue>=1 give
Ftrue<=b+dR, while nominal F0<=F_up,0. The two tensor decompositions are

    Qtrue-Q0 = W0(Ttrue-T0)+(Wtrue-W0)Ttrue,
    Qtrue-Q0 = Wtrue(Ttrue-T0)+(Wtrue-W0)T0.

Consequently the uniform energy radius can be sharpened to

    U_ball=min(W0*h+δW*(b+dR),
               Wmax*h+δW*F_up,0),

and the full tensor radius is sqrt(2)U_ball. The common positive-denominator
and mixture formulas in Sections 7–8 apply unchanged.

### Concrete controls and claim boundary

Pure isotropic redshift, R0=aI and Rtrue=(1+h)R0 with source and birth density
fixed, obeys Qtrue=(1+h)^4 Q0. The factor is four powers because the shape
stress supplies one power and detR supplies three. A mutant that freezes D
predicts only (1+h)Q0, and its relative error is

    |(1+h)^4-(1+h)|/(1+h)^4,

which is approximately 3|h| at small h. An h of 1e-5 gives a discriminating
control against the fixed 2e-8 target without a new physical history.

Other useful refusals are null supplied radius, true pair outside the stated
radius, dR>=a, a ball violating outgoing/condition domain, a source ball
crossing the continuous-positivity boundary, and a nonpositive lower energy
denominator. Null means unknown physical input, not numerical zero.

The controller's final sufficient admission gate carries the empirical
nominal floating reserve as an absolute error:

    [A0+sqrt(2)U_ball+2e-12 W0 F_up,0]/(L0-U_ball) <= 2e-8.

The ratio change must not be applied only to the ideal terms while leaving
2e-12 outside the denominator. This operational gate is conditional on the
stated nominal floating reserve; it does not certify floating arithmetic by
interval methods. The actual observed total error must independently
satisfy 2e-8, with the separately measured truth-reference allowance recorded
in the comparison against the certificate itself.
