# Saved cohort binding, finite transport error and sector geometry

Status: direct conditional derivations; current physical radii are not supplied.
Conventions: (-,+,+,+), nonrotating orthonormal matter tetrad, x0=ct,
fixed L, tau=ct/L, kappa=8*pi*G/c^4, alphaL=kappa*L^2.
Sources: unchanged B3c THEORY/code and B3f finite-input theorem; exact paths
and hashes are in the input manifest. No new general no-go is asserted.

## 1. A stored birth is an actual finite source endpoint

The B3c source receipt stores a gross downward number density n_b (m^-3),
already integrated over its proper duration, and q(n)=1+n^T S n on S^2.
S is symmetric trace-free and q>=0. With normalized angular mean,
<n_i n_j>=delta_ij/3 and
<n_i n_j n_k n_l>=(delta_ij delta_kl+delta_ik delta_jl+
delta_il delta_jk)/15. Hence

    <q>=1, <q n_i>=0, <q n_i n_j>=delta_ij/3+2 S_ij/15.

For ell^a=(1,n), T_b^{ab}=E_b n_b <q ell^a ell^b> is in J/m^3.
Its anisotropic stress is 2 E_b n_b S/15 with its signed components.
The actual B3c positive Q14 rule is exact for these polynomials at birth.
Thus these moments can be recovered from receipts without replaying a source
root solve, a transport step or an Einstein IVP. R(t_b,t_b)=I and detR=1 are
definitions at the same event and frame, not fitted physical uncertainties.

The source is the saved manufactured B3c closure. Its angular source, photon
yield, effective energy and atomic mass remain subject to their source-model
uncertainties. Neither exact polynomial moments nor a small arithmetic
residual supplies those errors. The H_LYA_EFFECTIVE_2P card is not silently
upgraded to isotope-resolved finite-mass hydrogen.

## 2. Why final cohort transport needs an additional saved quantity

For diagonal Bianchi I in this tetrad,

    d p_i / d tau = -(h+sigma_i) p_i,
    alpha'=h, beta_i'=sigma_i, sum_i beta_i=0,
    R_i(t_f,t_b)=exp[-Delta alpha-Delta beta_i], detR=exp[-3 Delta alpha].

The restored B3c path supplies alpha,beta at full-step endpoints. A birth is
at the split-step midpoint. The source receipt supplies N_b,H_b,S_b but no
beta_b. N_b=N0 exp(-3 alpha_b) yields the nominal reconstruction
alpha_b=-log(N_b/N0)/3; the exp/rounding/log reconstruction error remains
a separate numerical obligation. H_b and S_b give the instantaneous derivative beta'_b,
not its value. Endpoint averaging would introduce a new interpolation and
its error. We therefore bind the birth moments and leave final R with the
precise beta_b/interpolation-bound obligation. Existing completed endpoint
geometry and aggregate stress are consumed directly below.

## 3. G1C diagonal finite input-to-map bound

Let a_i=Delta alpha+Delta beta_i, a_hat_i its supplied nominal value and
|a_i-a_hat_i|<=e_i with e_i>=0. Then

    |exp(-a_i)-exp(-a_hat_i)|
      = exp(-a_hat_i) |exp[-(a_i-a_hat_i)]-1|
      <= exp(-a_hat_i) expm1(e_i).

The spectral norm of a real diagonal matrix is its largest absolute entry:

    ||R-Rhat||_2 <= max_i exp(-a_hat_i) expm1(e_i).

This is finite, with all mixed powers retained; it reduces to
max_i Rhat_i e_i at first order. If |Delta alpha-Delta alpha_hat|<=e_alpha
and both beta tensors are exactly STF,

    |detR-detRhat| <= detRhat * expm1(3 e_alpha).

Separate physical input bounds e_i^phys and numerical reconstruction bounds
e_i^num may be summed by the triangle inequality before the nonlinear map.
Their provenance remains separate; a missing bound stays null. Saved sample
agreement alone does not establish an interval-wide interpolation bound.
After eR, eS, en and fixed E are supplied, unchanged B3f.ball/compose applies
its positive lower denominator and inherited 2e-8 target. Birth q exactness
does not eliminate uncertainty in the physical q that the model approximates.

## 4. General matrix defect bound for a future supplied geometry path

This section is conditional on interval-wide bounds. Ahat denotes the exact
mathematical nominal coefficient field chosen by the model, so eta below is
the physical input/model discrepancy. Numerical coefficient evaluation error
must be enclosed in D relative to this Ahat, not silently assigned to eta.
Let R'=-A R and a differentiable represented path Rhat obey
D=Rhat'+Ahat Rhat. For E=R-Rhat,

    E'=-A E-(A-Ahat)Rhat-D.

For the spectral matrix norm let mu2(B)=lambda_max((B+B^T)/2). If
mu2(-Ahat)<=mhat, ||A-Ahat||2<=eta, ||Rhat||2<=M and ||D||2<=d throughout
an interval of length T, set m=mhat+eta. The transition norm satisfies
||Phi(t,s)||2<=exp[m(t-s)]. Variation of constants then gives

    ||E(T)||2 <= exp(mT) e0 + (eta*M+d)*T*phi1(mT),
    phi1(z)=expm1(z)/z, phi1(0)=1.

With e0=e0_phys+e0_num, report the two additive terms separately:

    B_phys=exp(mT)e0_phys+eta*M*T*phi1(mT),
    B_num =exp(mT)e0_num +d*T*phi1(mT).

Both share the full growth factor; this decomposition labels the origin of
uncertainty and does not pretend the growth factor is independent of physics.
All terms are dimensionless when tau is used: A has units tau^-1, D has
units R/tau, mT is dimensionless. T=0 returns the initial bound. At m=0 the
integral factor is T; for m<0 the factor is still positive. No saved B3c
sample-derived eta or defect envelope is claimed in this unit.

## 5. Native incoming source and finite absorption

REC LINE02 uses a native Wien departure. Keep Delta f_+ and its native
reference as owner data. The physical total occupation under that reference
is exp(-E21/TR)+Delta f_+. LINE01's separately declared stimulated/Planck
model uses 1/expm1(E21/TR)+Delta f_+; these are different source conventions.
TR is stored in eV, so E21/TR is dimensionless without an additional k_B.
Native LYA_FACT and hPc determine native coefficients and retain their exact
source identity. A modern-constant substitution changes that source.

A scalar f_+ does not determine the number of donor photons in a finite cell.
For a bound volume V and owned subset D of the original B3b2 measure, the
candidate donor count is V sum_D G_i A_j f_ij. A face-flux formulation instead
needs area, time and directional cosine. In both formulations the actual
cell-to-face/source-query map is required. The stored cell average and native
line-face value cannot be equated without that map. We implement readiness
and exact missing fields, without fabricating a bandwidth or donor population.
The native direct pair owns Trr[1,1]+=r and sr[1]+=r*b; other atomic channels
and history updates remain with their source owners.

## 6. Stress, four-force and fixed-scale geometry

For each sector in the common tetrad write

    T_s = [[rho_s, F_s^T], [F_s, p_s I+pi_s]],
    nabla_a T_s^{ab}=Q_s^b, sum_s Q_s=Q_external.

T, rho,p,pi,F have SI J/m^3; physical energy flux is cF. Let cQ denote the
energy-equivalent rate in J/(m^3 s), with spatial entries equal to c times
momentum transfer per volume per second. Then Q=cQ/c has J/m^4 and

    rho_hat=alphaL*rho, F_hat=alphaL*F,
    p_hat=alphaL*p, pi_hat=alphaL*pi,
    U_s=alphaL*(L/c)*(cQ_s)^0,
    J_s=alphaL*(L/c)*(cQ_s)^i.

This follows by multiplying the SI conservation equation by kappa L^3
and using d/dtau=(L/c)d/dt. It agrees with the existing B3a source bridge.
Q is a derivative source; T and pi are instantaneous state stress. Adding
a PiRate to a state pi violates dimensions and double-counts source history.

For stored B3c, use separate lower-rest, excitation and radiation sectors.
The first two are cold dust; radiation has p_gamma=rho_gamma/3. Finite
source kicks were already applied, so stored endpoints have U=J=0. No
thermal heating claim is generated from excitation-to-photon exchange.

With Bianchi-I curvature and rotation zero, the unchanged core equations are

    h'=-h^2-sigma:sigma/3-sum_s(rho_s+3p_s)/6,
    sigma'=-3h sigma+sum_s pi_s,
    rho_s'=-3h(rho_s+p_s)-sigma:pi_s+U_s,
    F_s'= -4h F_s-sigma F_s+J_s.

The four first/final saved endpoint RHS evaluations compare these expressions
to the real core after SI conversion. Their agreement verifies this adapter.
The source-free G1B and existing B3c convergence evidence remain separately
reused. A selected physical REC geometry run still needs complete B3g/B3h
structural inputs and its own declared execution contract.
