# Source-literal QSS: derived arithmetic enclosure

The complete derivation and source-to-code map are in the immutable capsule THEORY.md. This summary fixes the mathematical claim; it does not certify physical inputs or the missing historical QSS vector.

## Exact target and units
At the stored cut use theta=t_cut/T_stored, the saved scalar FLRW u, actual endpoint maps and absolute Wien term. JSON numeric constants mean exactbinary64 reals, strings exactdecimals. q is an abundance fraction; M and b have s^-1 units; proper time is in seconds and NH in m^-3; V0=1m3. Inherited(-,+,+,+), c,hbar,k_B and sector ownership are unchanged.

M=[[a,-beta],[-chi,d]], a,d>0,beta,chi>=0,Delta=ad-beta*chi>0. The explicit inverse is [[d,beta],[chi,a]]/Delta, hence q=((d*b1+beta*b2)/Delta,(chi*b1+a*b2)/Delta). Multiplication verifies it and proves inverse positivity. Outward interval evaluation with strict lower determinant>0 encloses the entire rectangular coefficient box, not just sampled corners. For q_i in[l_i,u_i], the exact dyadic representative qhat has E_new=sum_i max(qhat_i-l_i,u_i-qhat_i).

## Integer arithmetic and elementary functions
Represent each interval as integer[L,U]/2^P. Add/subtract exactly; multiply using extrema of four integer products and outward floor/ceil. Reciprocal is allowed only when0is excluded. Integer sqrt uses isqrt(L*2^P) and an upward-adjusted isqrt(U*2^P).

For positive x reduce y=x/2^m<=1/8. The positive Taylor polynomial T_n and next term t_(n+1) obey0<=exp(y)-T_n<=t_(n+1)/(1-y/(n+2)). Outward arithmetic encloses this tail; m squarings enclose exp(x). Negative x uses reciprocal and interval arguments use monotonic endpoints. The finite domain|x|<=128 and term cap are refusal boundaries, not extrapolation rules. The certificate uses no assumed MP arithmetic allowance.

## Residual and finite reward
Nonpositive off-diagonals and column-sum lower bound gamma>0 imply ||Mx||_1>=gamma||x||_1 by summing sign(x_i)*(Mx)_i and the off-diagonal inequalities. Thus ||M^-1||_1<=1/gamma and ||qstar-qhat||_1<=||b-Mqhat||_1/gamma.

For the source-literal whole cell, H(u)^2=Hpref^2[Om exp(-3eta)+Ol+Or exp(-4eta)] decreases for positiveOm,Or. g is positiveaffine. Bound Ralpha below by pref*H(h)/gmax and above by pref*H(0)*exp(3h)/gmin. Non-Lyalpha column sums are affine in theta; use the minimum endpoint and add the Ralpha lower bound to column2. The common lower gamma_global contracts same-law population errors. The future Lyalpha count row is bounded by NH*Ralpha_upper, so every finite suffix satisfies |deltaN|/V0<=K*delta_c, K=NH*Ralpha_upper/gamma_global. This integrates the exponential majorant to infinity and does not call old quadrature.

The inherited cut error can be added only under its original same-model hypothesis. It is not newly certified. The original E_QSS_old remainsnull; the new exact target/representative is separate. Source/physical errors and full trajectory uncertainty remainnull.

Higham's author exposition supplies M-matrix terminology; Rump2010 author metadata/abstract supplies verified-computing context. The specific proof is given here rather than imported from unread text. Explicit Wolfram algebra returned9zero scalar residuals; an earlier natural-language b12 parsing error was not used. Same-author alternate checks andCAS do not close distinct-authorR6/C9.
