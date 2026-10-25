# BASS_B3F_COHORT_INPUT_ERROR_20261025 — frozen contract v1

Workflow: physmath-research-loop 1.0.0. Root owns this scientific contract,
admission and repair decisions. A lower-tier agent owns implementation and
bounded execution. Independent Astra review reads theory, actual code, raw
results and actual saved figures. No merge or production activation.

Parent: cosmosapjw-quantum/bass PR189, branch
research/bass-b3e-positive-angular-20261025, actual HEAD
6c933f324fe54d1f590bc8ab121032702659e00a, science
338f982721336dabbe6cced765edf97a896428d5.
New lane: research/bass_b3f_cohort_input_error_20261025/.
New stacked Draft branch: research/bass-b3f-cohort-input-error-20261025.
Central observed HEAD8e946b46aa44581f09141184f193223277f2ec88;
AGENTS429a5a13ee75b1222bc50627f8d5973d01dd21c4;
fixed/current BASS handoff55c86aabe97702d6b64631c5f24a9d1a9563820e.

## R1–R3 / C1–C2: problem and source boundary

B3e supplies a positive angular rule with an a priori tensor error bound for
specified massless mapped cohorts. This unit supplies the missing observable
map from finite errors in R, S and birth number density to energy–momentum
error, including number dilution detR and a positive energy denominator.
It composes that error with the existing angular bound. This is neither an
Einstein/history integration nor a new photon source transaction.

Current source intake found REC136 same-h scalar-history admission and a
represented stable Ks norm certificate. Its physical history error remains
null. Those operator rows/units do not supply errors in BASS R/S/density.
The REC_HISTORY02 C5 checkpoint owns retarded crossing, direction, occupation
and fixed-cell tangent; that parallel task is not implemented here.
No selected actual B3c cohort history export has been supplied. Actual
history application and finite receiver absorption remain OPEN_INPUT.

Reuse B3e saved G3/G5 nominal selected moments, reference moments, selector
and reference evidence by exact identity, without rerunning its campaign.
Copy positive_angular.py, its vendor modules and source card exactly into
this lane as dependencies. Copy the saved POSITIVE_ANGULAR_SWEEP.json;
SHA256 b5933f2347665f8246e8de79c3c66496c96f79dfae965eeb2c48729333040494.
No old IVP, old tests/sweep, archive or NPZ download. Existing source copies
are not edited. No clone/worktree; current bass_source is a selected source
snapshot, not a local Git checkout.

## Physical and mathematical definitions

Metric(-,+,+,+), c,hbar,k_B retained. Fixed birth label n on the unit sphere,
normalized mean <.>=(4pi)^(-1) integral dOmega. S is real symmetric STF,
lambda_min(S)>=-1, q=1+n^T S n>=0, <q>=1. Source zeros are allowed. No
clipping/projection. All compared tensors use the same final frame and the
same birth-label identification; coordinate rotations must transform both.

R is real invertible, detR>0. The theory permits all such maps. The tested
numeric interface inherits b=sigma_max<=1 and b/a<=2 (512eps comparison
allowance only). Endpoint conditions do not infer continuous-time support.
E_b=1.6340142155180418e-18 J from the unchanged H_LYA_EFFECTIVE_2P card,
Pstar=E_b/c, L=1m, alphaL=kappa L^2. n_b is diagnostic birth density m^-3.
Same E_b is used on both sides; energy uncertainty is outside this unit.

    G(v)=blockdiag(|v|, vv^T/|v|), G(0)=0,
    T(R,S)=<q G(Rn)>, F=T00, P=Tspatial, pi=P-I F/3,
    H(S)=I/3+2S/15, M=R H R^T,
    F_lo=(trM+a*b)/(a+b), F_up=sqrt(trM),
    D=detR, W=E_b*n_b*D, Q=W*T.

The exact antipodal flux is zero. Full Euclidean tensor Frobenius norms are
invariant under spatial rotations, not arbitrary Lorentz boosts. Physical
packets retain k=Rn, w=alphaL E_b n_b D A q, mass0 and E=c|p| once.
State density weights, invariant event rates and observer clocks remain
distinct. No Source/U/J/PiRate, bath/donor/bandwidth, clipping or absorption.

## R4–R5: finite perturbation result

For v=r u,w=s z, cang=u.z, direct contraction gives

    ||G(v)-G(w)||F^2 = 2(r-s)^2+2rs(1-cang^2)
                       <=2||v-w||^2.

The continuous extension at zero is used only in the kernel test. Equality
for parallel positive vectors establishes the sqrt2 constant for this kernel.
For two admitted endpoints i=0,1, define dR=R1-R0, U=S1-S0 and Cj=Rj^T Rj:

    r_i=sqrt(tr(dR H_i dR^T)),
    s_j=sqrt((2 tr(U^2)tr(Cj)+8 tr(U^2 Cj))/105),
    h=min(r_0+s_1, s_0+r_1).

The spherical sixth-moment identity and Cauchy–Schwarz give
|F1-F0|<=h and ||T1-T0||F<=sqrt2*h. Source matrices need not commute with
R^T R. Record both ordered paths, not just their minimum.

For W_i=E_b*n_i*detR_i and dW=|W1-W0|:

    U_pair=min(W0*h+dW*F_up1, W1*h+dW*F_up0).

Then |Q1_00-Q0_00|<=U_pair and ||Q1-Q0||F<=sqrt2 U_pair.
Keep the map, source and prefactor terms separately, along with the chosen
path. For numerical stability compute dW from a determinant difference
that is accurate at small perturbations: exact 3x3 multilinearity/cofactor
formula or an algebraically equivalent compensated difference. Do not
divide by a perturbation or silently set a tiny difference to zero.

## Uniform input-radius certificate

Supplied nonnegative radii eR,eS,en mean ||DeltaR||2<=eR,
||DeltaS||F<=eS with DeltaS symmetric STF, and |Delta n_b|<=en.
The nominal cohort has n0>0. Unknown radius None/null returns
INPUT_ERROR_UNSPECIFIED; it is never replaced by zero.

The physical all-ball sufficient domain requires

    eR<a, b+eR<=1, (b+eR)/(a-eR)<=2,
    eS<=1+lambda_min(S0), en<=n0.

Only 512eps comparison allowance is allowed at exact floating boundaries.
An endpoint pair can remain valid when this stronger whole-ball domain is
not certified. In particular the source-zero G5 nominal has zero symmetric
source-ball radius. Preserve NOT_COVERED_BY_PHYSICAL_BALL for eS>0 there;
do not reject its actual valid one-sided pair or clip its source.

Let sigma_i be the three nominal singular values. Define

    deltaD=e2(sigma)*eR+e1(sigma)*eR^2+eR^3,
    deltaW=E_b*(n0*deltaD+en*(D0+deltaD)), Wmax=W0+deltaW,
    h_ball=eR+eS*sqrt((2 sum_i(sigma_i+eR)^2+8(b+eR)^2)/105),
    U_ball=min(W0*h_ball+deltaW*(b+eR),
               Wmax*h_ball+deltaW*F_up0).

The determinant polynomial follows from cofactors/exterior minors; no
linearization drops mixed terms. Its finite bound and source sixth moment
are proved in the theory note and independently cross-checked.

## Positive denominator and angular/error composition

Read the saved nominal B3e selected bound B_T0 and angular approximation;
do not select a new nominal degree from observed perturbed errors.
For either a pair or a supplied physical ball set

    A0=W0*B_T0, L0=W0*F_lo0, B0=W0*F_up0,
    Ltrue=L0-U,
    ideal_total=(A0+sqrt2*U)/Ltrue,
    operational_total=(A0+sqrt2*U+eps_fp*B0)/Ltrue,
    Umax=(tau*L0-A0-eps_fp*B0)/(sqrt2+tau).

Here tau=2e-8 unchanged and eps_fp=2e-12. Ltrue must be positive; otherwise
return NONPOSITIVE_ENERGY_LOWER_BOUND without a denominator floor.
Umax<0 means the nominal angular allocation/reserve leaves no input budget.
The ideal result is an exact-arithmetic theorem. The operational result uses
an explicitly empirical binary64 reserve supported by parent/new checks;
it is not interval certification. Reference quadrature has a separately
reported 2e-12 comparison allowance. The reserve is multiplied by B0 and
divided by Ltrue; a changed energy denominator is not ignored.

CERTIFIED_SCOPED_NUMERICAL_BUDGET means operational_total<=tau with supplied
domain/radii. Larger values mean BUDGET_NOT_CERTIFIED, not physical invalidity
or proof that actual error exceeds tau. Missing radii remain unspecified.
Exact pair/ball numerical validation and actual-history admission are separate.

For a finite positive mixture with common final frame, sum the physical signed
tensors and A0,L0,B0,U per cohort. Apply the same denominator/formula to these
sums. Sum absolute error budgets; do not cancel them or average R/S.

## R7 / C3: frozen discriminating cases

Read G3/G5 nominal S,R and saved tensors from B3e. G3 birth n0=1m^-3.
Use proper rational rotations OZ,OX,OY from the unchanged dependency.
Set S_alt=OY diag(-.2,.4,-.2) OY^T and
R_alt=OZ diag(.55,.65,.80) OX^T. Epsilon list is exactly
[1e-10,1e-8,1e-4,1e-2], fixed before results.

Main pair rows: P0 identical G3, plus five families at all four eps (21rows):
P1 density only: S1=S0,R1=R0,n1=1+eps.
P2 map scaling: S1=S0,R1=(1-eps)R0,n1=1.
P3 source: S1=(1-eps)S0+eps*S_alt,R1=R0,n1=1.
P4 mixed: S1 as P3,R1=(1-eps)R0+eps*R_alt,n1=1+eps/2.
P5 source-zero G5: S1=(1-eps)S0,R1=(1-eps/2)R0,n1=1+eps.
All are manufactured finite endpoint perturbations, not REC/B3c history.

P0/P1/P2 reuse nominal reference tensors with exact density/scaling laws.
In P2 physical Q scales as(1-eps)^4, not(1-eps).
P5 has R=lambda I, exact F=lambda,P=lambda H(S1),flux0.
Only the eight P3/P4 endpoints need new independent direct product-rule
reference64x128 and96x192. Do not rerun old nominal references. New reference
64/96 agreement<=2e-12, fixed-K61/93 ideal B3e reference bounds<=2e-12.
Compute all pair bounds, actual pair errors, combined nominal-angular errors,
physical ball radii from each actual difference, and all statuses.

Add two two-frame covariance comparisons of the saved P4 eps=.01 row:
(Ob,Of)=(OY,OX) and(OZ,OY). Transform both endpoints/rays/tensors as
S'=Ob S Ob^T,R'=Of R Ob^T; compare bounds and physical tensors in same units.
These use saved tensors and algebra, no repeat angular campaign.
Add one positive mixture from P1/P2/P3/P4 at eps1e-10 with multiplicities
[1,.25,2,.5]. Propagate per-cohort U and compare summed signed tensors.
Thus the main output has21pair+2frame+1mixture=24rows, labelled by scope.

Actual unchanged kinetic mapping is checked on P4 eps=.01 and P5 eps=.01
only, using positive GL32x64 rays: compare packet T, number, flux, trace and
PSD to direct same-rule moments. This is a mapping test, not its continuum
accuracy reference. New physical numbers are n1 detR1. Source weight signs
must be retained; no clipping.

Focused tests: exact sixth-moment monomials via known sphere formula with
Nmu4 (degree7) for rational STF U and nonsymmetric R; kernel Lipschitz
equality/zero/antiparallel; determinant polynomial/mixed terms; exact
isotropic-density/R/source limits; missing radii; negative/nonfinite radii;
asymmetric/non-STF sources; determinant/nonpositive-density/domain errors;
all-zero mixture; nonpositive combined denominator; whole-ball failure at
source-zero vs valid pair; frame normalization and positivity.
One deliberate omitted-det control uses P2 eps1e-4; preserve its measured
wrong tensor residual and require it exceed2e-8. Another control compares
the corrected lower denominator to a frozen-nominal denominator on P2eps.01
and reports the difference. No tolerance mutation, hidden row or post-hoc
fixture choice.

## Gates, resources and stopping rule

Every actual energy difference<=U+2e-12*positive reference energy;
every tensor difference<=sqrt2 U+same allowance. Keep signed residuals.
Every admitted operational certificate must have actual combined error<=2e-8.
Every physical ball covers its paired bound/actual residual within floating
allowance; report conservative/noncertified rows without relabelling failure.
Symmetry/trace/number/PSD/packet/co-rotation/exact oracle checks<=512eps on
their declared positive energy/number scale. No zero denominator normalization.
RawJSON, allrowsCSV, summaryJSON and actual PNGs must reconcile.

Lower-tier allowed paths: code/,tests/,vendor/ exactcopies,results/,
provenance/reused_data/, factual implementation/packaging notes. Root controls
theory/contract/reviews/admission and publication. Code review and actual
S0 Git+Drive+Dropbox preparation ACK precede scientific Python GO.
Planned commands from this lane, one thread, writable MPLCONFIGDIR:

    python code/metered_run.py tests/test_cohort_input_error.py
    python code/metered_run.py code/run_sweep.py
    python code/metered_run.py code/summarize.py

New guard120wall/60CPU seconds, implementation allocation60wall/40CPU,
perchild30wall/20CPU. Historical remainingwall/CPU=null,budget_reset=false;
old34.1262904040002 is a partial historical subtotal, not a balance.
Keep all child argv/cwd/start/end/exit/stdout/stderr and CPU/wall receipts.
No IVP, source transaction, old campaign replay or full archive restore.
Wolfram bounded exact cross-checks are separately measured.

Substantive failed gate or ambiguous physical input returns to root with raw
evidence; no silent contract change. Root authorizes a diagnosis-specific
repair and only affected rerun. Independent reviewer reads actual final
code/raw/figures; stop optional reviews after concrete obligations close.
Different-model scientific review NOT_RUN unless actually observed.

## R9–R10 / C10 delivery and DAG

S0 covers R1–R6/C1–C5 preparation, S1 validated R7–R9/C6–C9,
S2 final R10/C10 handoff. Each stage records its actual covering cumulative
snapshot and separates science/Git/provider ACK/full remote restore. No claim
of20separateuploads. Preserve originals, exact prior handoff and prior failure
scopes. Final S2 self commit/hash/ACK is recorded outside itself in PR body.
Use only fresh actual expectedSHA and non-force updates; no central overwrite.

B3d->B3e->B3f finite input-to-observable control->actual cohort history/input
error binding OPEN_INPUT->calibrated REC/geometry OPEN->B4/B5 NOT_RUN.
The separate native finite absorption branch remains OPEN_INPUT_OWNERSHIP.
Whole BASS physical completion=null. NG1–NG7 are NOT_APPLICABLE to a strong
no-go claim; this unit makes finite constructive bounds and tests them.
