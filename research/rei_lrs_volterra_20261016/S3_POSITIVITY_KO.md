# S3 | A causal positive shear-response envelope for BASS LRS FD96

Date 2026-10-16 KST. Parent sources: BASS PR168 `03a01d21ed21e7d32737ca5e5f6d889a7203aa70`; original freestream blob `8467932c3281f9d426712b3a582f2aae3a484692`; PR164 source tangent blob `1cab2bf7eab5a306ab207206ca3a0fc793dc9163`. This is an **exact linear-response** statement about the collisionless BASS source-only background; it is not a stability theorem for nonzero finite A or for the coupled REI photon+HHe+radiation Einstein equations.

## Stronger mass-independent contraction

Since `k/E0 <= E0`, normalized isotropic reference density at x=0 is ρ0=1 and `κ(0)=2J1−(2/5)J2 <=2J1<=2`. The S2 bound gives for ANY positive isotropic canonical-momentum radial distribution with the declared energy normalization:

`q(X) <= [5/3]*f_m/(1−f_m)*(1−exp(−X))`.

For the actual BASS/REI lane f_m=.1 and X=ln(21/5), this universal source-independent upper bound is **0.14109347442680775 <1**. It does not require high-order angular sampling or a particular mass; the much tighter FD96 sampled bounds for m=3,30,300 are 0.06474263899983676, 0.001968810308024507, and 0.00002027890565784328. The theorem requires H>0, positive dust background and no negative matter components; do not transplant it to a different matter budget without rederivation.

## Sign-definite retarded geometry response

The open-loop `g(x) = ∫_0^x G(x,u)α(u)du` is nonnegative and increasing, because the kernel and its x derivative are nonnegative. If f≥0 is increasing, so is T f and `(Tf)(x) <=q f(x)` on [0,X]. Hence the alternating Neumann terms satisfy

`0 <= ... <=T² g <= Tg <= g`, and the convergent series `B=g−Tg+T²g−...` satisfies

`(1−q)g(x) <= B(x) <= g(x)`, and `B(x)>0` for x>0.

The bound also gives a definite sign of s_A. At any isotropic x,

`α/κ=1/(10−2R)>=0.1`; and, from `α(u)<=exp(−3u)/5` and the S2 Green bound,

`0<=g(x) <= g_max(X)=[2/15] f_m/(1−f_m) * [X−(2/3)(1−exp(−3X/2))]`.

At f_m=.1, X=ln(21/5), `g_max(X)=0.012531411042438566<0.1` and `B<=g`. Thus `α−κ B>0` for all x in (0,X], making `s_A(x)>0` via its exact integrating-factor equation. Initial A>0 consequently produces `b=A B+O(A²)>0` and signed `s=A s_A+O(A²)>0` **to first order only**. The sign of public Sigma=sqrt(3)|s|/H is nonnegative by definition and carries no orientation information. If A<0, first-order signs reverse.

The proof uses the Volterra kernel's positivity, not a claim that the kinetic stress-neutral root b*(x) equals the actual geometry response B(x)A. The latter has dynamical lag and Hubble damping.

## Actual sandbox campaign with parent BASS source

Commands:

`OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python run_campaign.py --out evidence/S3_CAMPAIGN_FINAL`

`OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python -m unittest -q test_retarded test_campaign`

Outputs: `evidence/S3_CAMPAIGN_FINAL/RESULTS.json`, `LRS_RESPONSE.csv` (99 source-only rows), `SHA256SUMS.txt`; `evidence/S3_TESTS_FINAL.log`. **21/21 tests PASS, 3 source masses, 513-time-point each, parent PR164 nonlinear IVP and tangent reused and independently compared.** Source-normalized max absolute |Volterra−DOP853| 1.3972369693770412e-13. Max |PR164 tangent b_A−independent DOP853| 2.3048579646418876e-14. m3/30/300 Picard iterations 5/3/2 for tolerance 1e-14. Measured endpoint feedback suppressions relative to no-feedback `g`: 0.005756014312134683 / 0.00012898955473539253 / 0.0000013112709155160829. Positive signed s_A observed on all sampled x and implied by the above theorem in this parameter domain.

In m3 at grid N=65/129/257/513/1025, end b_A difference against independent DOP853 was respectively 7.1078116e-11 / 4.4423519e-12 / 2.7777867e-13 / 1.7492084e-14 / 1.2251485e-15, approximately 4th order until near the floating-point/Ode tolerance floor. Finite-A nonlinear PR164 difference: for m3 and |A|=.05, relative |b_nonlin−A B|/|b_nonlin|=5.54e-5; for larger |A|=.1 about 1.11e-4. This is a sampled error, not a uniform nonlinear bound. m300 finite-A error enters the parent ODE tolerance floor; no measured quadratic scaling assertion for m300. Angles GL16 vs96 at x=.7,b=.2,A=.5 produce max (rho,ΔP,χ) differences 5.47e-13 for m3; this is a *local LRS* comparison, not the PR168 non-LRS broad-domain angular accuracy closure.

## REI handoff boundary

The causal kernel gives a candidate **source-only first-variation** check for non-tilted axisymmetric REI: signed b_A and s_A/H0 at BASS background sample clocks, with finite-A perturbative error explicitly unadmitted. It cannot be used as a closure for (1) frequency-resolved ionizing photon π_ab or photon birth/absorption stress, (2) primordial gamma/nu hierarchy, (3) ionized gas momentum Q^a or stellar recoil, (4) general-relativistic full backreaction/observational EoR. A REI owner adapter would have to recompute the full source budget, actual source history and new checkpoint, not add this shear twice to PR159's existing prescribed BASS geometry.

## Evidence and claim

DERIVED: Volterra kernel, contraction, mass-independent q, signed first-order shear bounds. Wolfram validated angular identities and power-law kernel. NUMERICALLY_CHECKED: actual FD96 source-reconstructed numerical campaign and small-A parent IVP agreement. IMPLEMENTATION_VERIFIED: Python-only, 21 focused tests. REI/NCP native: NOT_RUN. Full non-LRS strong anisotropy quadrature remains separately HOLD in PR168. No claim of numerical global error certification outside the explicit Volterra Picard (not quadrature) bound.
