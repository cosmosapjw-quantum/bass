# Variable-matrix adjoint moments and a finite quadrature certificate

This is the executable mathematical companion to MODEL_AND_RESIDUAL_THEOREM.md. The selected interpolation is proper-time gross-map PL with endpoint-tagged energy, not separately interpolated per-event energy. All formulas concern the new finite model. No old numerical result is rerun here.

## 1. General observable identity: no unresolved fast-layer quadrature

Let p'=b-Mp, K=M^(-1), and let q(t) be a row or matrix multiplying p. Define

Psi_0=qK,
Psi_(r+1)=(D Psi_r)K,  D=d/dt.                           (A1)

For any m>=1, integration by parts gives the exact identity

I_q := integral_a^b q(t)p(t)dt
 = sum_(r=0)^(m-1) {
       integral_a^b Psi_r(t)b(t)dt
       -[Psi_r(t)p(t)]_a^b }
   + integral_a^b (D Psi_(m-1))(t)p(t)dt.                 (A2)

Proof: p=K(b-p'), so q p=Psi_0 b-Psi_0 p'. Integrate, then repeat on (D Psi_0)p with Psi_1=(D Psi_0)K. This proof permits noncommuting variable M. Replacing K by a constant when differentiating would give a different and incorrect formula.

For matrix q use induced one-norm; for a scalar row use its infinity norm dual to ||p||_1. The uncomputed remainder is bounded by

R_m <= Pmax integral_a^b ||D Psi_(m-1)|| dt
    <= Pmax (b-a) sup||D Psi_(m-1)||.                    (A3)

The recommended initial choice is m=3. This requires only 2x2 matrix/row jets through third derivative; the q=2 endpoint residual already requires third-order derivative information. The first two terms of the same sum yield an m=2 diagnostic without a new source run or new quadrature problem. Agreement of two orders is diagnostic; (A3), not agreement, supplies the mathematical bound.

On a piecewise-smooth incoming history apply (A2) separately on each segment, keeping both one-sided Psi values at its endpoints. Carry the same physical p through the knot. If Psi is continuous its boundary terms cancel; do not assume that when higher derivatives differ. The endpoint theorem carries E_j at every restart.

If an endpoint approximation p_hat has errors E_a,E_b, the corresponding boundary-error addition is

B_end <= sum_r [||Psi_r(a)|| E_a+||Psi_r(b)|| E_b].        (A4)

Add new bounded quadrature errors, coefficient/clock enclosure errors, omitted-layer endpoint errors and declared arithmetic allowances. Formula (A2) includes all fast-layer effects in the endpoint terms. A broad Gauss rule never has to sample exp(-M_j(t-t_j)) to obtain the count.

## 2. Six shared population moments and tagged gross counts

Define, for k=0,1,2 and j=0,1,

F_kj=integral_0^T exp(k u(t)) theta(t)^j dt,
I_kj=integral_0^T exp(k u(t)) theta(t)^j p(t)dt.            (A5)

Compute I_kj by (A2) with q=exp(ku)theta^j I_2. The scalar F_00=T and F_01=T/2 follow exactly from the selected proper-time definition. Other F_kj are new smooth scalar integrals. Do not numerically integrate 1,414 channel trajectories independently.

For any endpoint gross map a_ck+ell_ck p, its tagged counts weighted by exp(k u) are

C_c0^(k)=N_H,0 [a_c0(F_k0-F_k1)+ell_c0(I_k0-I_k1)],
C_c1^(k)=N_H,0 [a_c1 F_k1+ell_c1 I_k1].                  (A6)

Here the superscript k is the transport weight, while the channel tag is 0 or1. Both tags are nonnegative because their exact integrands are. Their unweighted aggregate is C_c=C_c0^(0)+C_c1^(0). Small subtraction in (A6) is evaluated at the fixed MP precision with its propagated bound; negative results are not clipped.

The selected sector moment is

U_s^(k)=eV_J sum_c [
       e_c0,s C_c0^(k)+e_c1,s C_c1^(k)]                 (A7)

plus the separately represented direct Ly-alpha contribution. Since sum_s e_ck,s=0 for each tag, total event energy closes algebraically. Keep the same tagged count in every sector. The weights k=1 and2 are transport moments; they are not interchangeable physical energies.

For a certified vector moment error eps_I and scalar error eps_F, a directed tag uses the actual affine row sensitivity. For example,

eps_Cc1 <= N_H,0 [|a_c1| eps_Fk1
                    +||ell_c1||_infinity eps_Ik1]
             +eps_arithmetic.                           (A8)

For tag0 sum the two corresponding F/I errors unless a sharper correlated difference was directly enclosed. An aggregate or sector bound must use its own summed row/energy sensitivity; a tolerance tied only to the largest gross channel does not certify tiny storage.

## 3. Direct Ly-alpha and reuse of the completed baseline

The downward weighted count is

C_alpha,down^(k)
 =N_H,0 integral exp(ku) R_alpha(u)e_p^T p dt,            (A9)

using (A2) with q=exp(ku)R_alpha e_p^T.

For k=0, reuse the admitted saved incoming count. For k=1, reuse the admitted saved pulled-back incoming energy divided by the fixed E21_J. Their unknown old quadrature error remains unknown, not zero. If k=2 is required, it is a new distinct weighted incoming moment with its own bound, not a rerun of the completed k=0/1 result.

The exact identity

N_H,0 Delta p_p
 =N_H,0 integral[b_n,p-(M_n p)_p]dt
   -(C_alpha,down^(0)-C_alpha,up^(0))                    (A10)

can also be evaluated from shared I_00,I_01 and endpoints. It is a useful independent conservation comparison. If one uses (A10) as the primary numerical definition of a cancellation-prone observable, label it as an identity-derived observable and do not then call the same identity an independent test.

The finite outgoing photon calculation is the preserved old baseline plus the new selected-model correction. Reusing the old incoming scalar does not certify its unknown historical quadrature remainder. A reported difference between the present endpoint-interpolation model and the earlier frozen-left model is a model-selection difference.

## 4. Tiny storage and the meaning of the residual

For an approximate trajectory p_a with r=p_a'-b+Mp_a,

sum_c nu_c C_c[p_a]
 =N_H,0 [p_a(T)-p_a(0)-integral_0^T r(t)dt].             (A11)

This explains precisely why a nonzero numerical residual can create a small difference between an approximate event sum and approximate endpoint storage. It does not license entering integral r as an actual source channel.

For moments approximating the exact p, compare each excited-stock discrepancy with

eps_balance,i =
 N_H,0 (E_T+E_0)
 +sum_c |nu_c,i| eps_Cc
 +eps_accumulation.                                     (A12)

Use propagated bounds or a sharper aggregate row bound. Report the observed discrepancy, the bound, and the actual storage magnitude. Root's intended numerical targets are:
- final fraction bound <=1e-34;
- excited-stock balance bound <=1e-16 nuclei per reference m^3;
- the same bound <=1e-8 of each actual nonzero 2s/2p storage.

These are frozen acceptance targets only after the root contract adopts them, not results. The exact event energy identity and transported-work identity receive their own sector and weight sensitivities. A gas heat or physical refill owner is never defined from an unassigned balance residual.

## 5. Native analytic clock and an explicit safe complex domain

The actual selected H has the source form

H(u)=H_pref sqrt(F(u)),
F(u)=A_m exp(-3u)+A_L+A_r exp(-4u),                       (A13)

with coefficients fixed by the saved cosmology and eta at the left selected knot. Use the original binary64 constants lifted to MP. They are positive for this admitted source. Do not replace the source endpoint H or n_H with a silently rounded surrogate.

Take a real panel centre c and complex disk |z-c|<=rho. Recommended initial rho=0.001 in u. Let

m_c=A_m exp(-3c), r_c=A_r exp(-4c), F_c=m_c+A_L+r_c,

delta_F=[m_c(exp(3rho)-1)+r_c(exp(4rho)-1)]/F_c.           (A14)

Check delta_F<1. The branch through positive H(c) is analytic on this disk and

H_min=H(c)sqrt(1-delta_F),
H_max=H(c)sqrt(1+delta_F),
B_1/H=1/H_min,

B_Hu/H=[3m_c exp(3rho)+4r_c exp(4rho)]
         /[2 F_c(1-delta_F)].                            (A15)

These are complex-modulus bounds, not sampled real-axis extrema.

The normalized clock is analytic and

|theta(z)-theta(c)|<=rho B_1/H/T.                        (A16)

Use the lower endpoint of a positive enclosure for T in a bound. New numerical errors in t(c) and T propagate into theta; use the same shared T everywhere. For an approximate t and T with errors eps_t,eps_T and T_hat>eps_T,

|t/T-t_hat/T_hat|
 <=eps_t/(T_hat-eps_T)
   +|t_hat| eps_T/[T_hat(T_hat-eps_T)].                   (A17)

Endpoints theta(0)=0 and theta(h)=1 are imposed by the exact normalized definition, not independently rounded ratios.

For g(z)=g(c)+g' (z-c), require
g_min=g(c)-|g'|rho>0 and let g_max=g(c)+|g'|rho.
Then

R_max=(LYA_FACT/n_H,0) H_max exp[3(c+rho)]/g_min,
B_Ru=R_max[B_Hu/H+3+|g'|/g_min].                         (A18)

Since M(z)=M_n,0+theta(z)Delta M_n+R_alpha(z)P,

Delta_M_disk
 <=||Delta M_n||_1 rho B_1/H/T+rho B_Ru.                  (A19)

With the actual real-centre K_c=M(c)^(-1), require

beta_M=||K_c||_1 Delta_M_disk <1,
B_K=||K_c||_1/(1-beta_M).                                (A20)

The inverse is then analytic and bounded by B_K throughout the disk. This is the required pole-exclusion certificate for any adjoint or slow-state Cauchy argument. A merely positive real-axis determinant is insufficient.

The original incoming field on a source segment is F_in(u)=d_0+d_1(u-c)+exp[-A exp(u)], A>0. For rho<pi/2,

B_F=|d_0|+|d_1|rho
       +exp[-A exp(c-rho)cos(rho)].                      (A21)

The same source segment's analytic extension may be used beyond its real knot when bounding that segment; it is not a statement that the piecewise physical function is analytic through the knot.

Because R_alpha*g cancels, a useful forcing bound is

B_b=||b_n(c)||_1+||Delta b_n||_1 rho B_1/H/T
       +3(LYA_FACT/n_H,0)H_max exp[3(c+rho)]B_F.          (A22)

The corresponding q bounds are immediate from exp[k(c+rho)], the bounded theta, and R_max when needed. All these bounds use only actual source endpoints and the exact selected clock functions.

If a disk fails (A20), shrink its radius or split that new integration panel while preserving halfwidth<rho. This is a finite numerical representation adjustment, not an unselected-provider gate. No new native solve is needed.

## 6. Analytic derivative bounds and jets

For any analytic scalar, row or matrix G bounded by B_G on a disk of radius rho, at real points with |u-c|<=d<rho,

||partial_u^n G|| <= n! B_G/(rho-d)^n.                   (A23)

This is Cauchy's derivative estimate applied componentwise or to each continuous linear functional; use a compatible matrix norm. Bounds for H derivatives follow directly from (A13) or the same estimate. Proper-time derivatives satisfy

D G=H G_u,
D^2 G=H^2 G_uu+H H_u G_u,
D^3 G=H^3 G_uuu+3H^2 H_u G_uu
       +[H(H_u)^2+H^2 H_uu]G_u.                         (A24)

Equations (A23),(A24), the inverse-jet recurrence in the companion theorem, and the Leibniz rule give explicit finite bounds for D y_2 and D Psi_2. Use analytic or finite algebraic jets, not differencing two nearly cancelling native RHS values.

One conservative derivative-bound implementation may use nested disks: prove H,g,M pole exclusion on the outer rho disk, enclose K,b,q there, and use Cauchy estimates at an inner panel. This keeps all derivative operations on a declared domain. Do not take a Cauchy derivative on the outer boundary without leaving a positive radius gap.

For a fully explicit recurrence with norm bounds K_n>=||D^n K||, Q_n>=||D^n q||,
Psi_(0,n) <= sum_(k=0)^n binom(n,k) Q_k K_(n-k),
Psi_(r+1,n) <= sum_(k=0)^n binom(n,k)
                         Psi_(r,k+1) K_(n-k).           (A25)

For m=3 the needed remainder bound is Psi_(2,1). Only derivatives through third order are required. Recurrences preserve matrix multiplication order in actual values; norm bounds can use submultiplicativity. The q=2 slow recursion uses an analogous triangular derivative table from the companion theorem.

## 7. A positive Gauss rule with a proved Cauchy remainder

Let an analytic integrand G(u) be bounded by B_G on a midpoint disk radius rho, and let d=(b-a)/2<rho. Let Q_n be the n-point Gauss-Legendre rule with positive weights and exactness through degree 2n-1. The Taylor remainder at any real point is at most

B_G (d/rho)^(2n)/(1-d/rho).

Both the integration functional and the positive quadrature functional have norm b-a, and they agree on that Taylor polynomial. Therefore

|integral_a^b G du-Q_n G|
 <=2(b-a) B_G (d/rho)^(2n)/(1-d/rho).                    (A26)

This direct proof avoids an empirical rule-difference estimate. For the small native cell, rho=0.001 makes the full-cell ratio about0.0425; the actual interval ratio is reported by implementation, not assumed here. A 24-point rule is a low-cost initial choice. A 16-point comparison may be formed from the same declared analytic integrand and bounds, but agreement alone is not certification.

For integrals in (A2), use G(u)=[sum_r Psi_r(u)b(u)]/H(u) on each preserved incoming segment. The same bounds above enclose 1/H, K, b, q and their jets. Alternatively integrate each small adjoint term separately to expose cancellation and its arithmetic allowance.

The quadrature theorem assumes exact nodes/weights/evaluations. If the implementation uses ordinary MP70 Gauss nodes and arithmetic with the declared relative allowance1e-55, report:
"analytic truncation bound plus declared MP arithmetic allowance; conditional numerical enclosure".
Do not call this an interval-arithmetic proof unless actual validated node, weight and function enclosures were used. Johannson-Mezzarobba's primary paper describes one rigorous route; adopting its library is not a mandatory new gate for this scoped conditional computation.

## 8. Minimal prescribed finite work

1. Reuse saved left maps, source operands, initial stock and old photon evidence.
2. Build right source endpoint maps once from the admitted saved operands.
3. Form the selected proper-time interpolation and tagged energy owners.
4. Bound the new clock, matrix positivity/contraction and analytic disks.
5. Compute two-state segment endpoints using q=2 and carry errors.
6. Compute six shared moments using adjoint m=3, plus needed direct-alpha rows.
7. Assemble tagged/aggregate counts, finite stocks, weighted energy and sector stress/four-force.
8. Compare the tiny storage identity against its actual propagated numerical bound.
9. Execute only the new frozen transaction/consumer allowed by the root contract.
10. Preserve actual raw outcomes, one independent review, publication and backup receipts.

This is a finite path to execution. A completed earlier campaign, missing physical radius, or unselected future provider is not an implicit extra computation or blanket prerequisite.

