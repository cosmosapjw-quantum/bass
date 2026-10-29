# CE1-J: 시간 국소적인 angular-source 인증 (2026-10-29)

## 물리적 정의

Frozen positive reflection-even massless collisionless diagonal Bianchi-I, Lambda=0, metric (-,+,+,+), normal proper u=t/Tstar; ell_i=ln(a_i), h_i=Tstar*H_i. Positive finite angular-energy original-cell continuum measure M and fixed exact-real stored binary ray/mass measure Q. For b_i=exp(-2ell_i), V^-1=exp(-sum_i ell_i), Z=sum_i b_i n_i^2, write P_i^M(ell)=V^-1 int b_i n_i^2/sqrt(Z) dM; P_i^Q is the same integrand summed over stored rays/masses.

## Constructive result (derived here)

For every s real, P_i^M(ell+s*1)=exp(-4s)P_i^M(ell). The same identity holds for P_i^Q by fixed ray/mass coordinates and no time-dependent mass adaptation. Thus D_i=P_i^M-P_i^Q obeys D_i(ell+s*1)=exp(-4s)D_i(ell). Proof: V^-1 multiplies exp(-3s), b_i multiplies exp(-2s), Z^(-1/2) multiplies exp(s), resulting net exp(-4s). No cancellation/positivity estimate is used for this algebraic identity; positivity is needed for the inherited outward source majorant.

From CE1-H for positive radiation, partial_(ell_j)P_i=-(1+2delta_ij)P_i+R_ij, 0<=R_ij<=P_i, sum_j R_ij=P_i; hence all entries nonpositive and row absolute sum 4P_i. CE1-I certifies ell_i(u)>=c*u for exact and stored-Hermite curves using positive h_i(0), theta'=-theta^2+E<=-2theta^2/3 and h_i'>=-theta*h_i. For T=.08, the exact-flow bound yields c_exact>0.375713199284988 and the stored cubic exact-binary Bernstein check permits c=3/8.

For time panel [u_j,u_{j+1}], both paths have ell_i>=c*u_j. Let s_j be a *directed lower interval* for c*u_j. Existing unchanged global geometry box ell_i<=B_i yields x=ell-s_j*1 in [0,B_i-s_j]. Original CE1-F certification E_Q(B) bounds |D_i| on a positive source box with exact stored source. The new valid panelwise bound is

  eta_j=min(eta_global, exp(-4s_j)*E_Q(B-s_j*1)),

where E_Q is outward MPFR192 certified_tabulated_pressure() applied to an outward shifted box. All arithmetic of s_j, shifted upper bounds and exponential scaling is outward directed; Emax retains its unchanged role in geometry existence/source box. Do not replace Emax with Pmax. If the growth/box certificate fails or source/path identity changes, reject rather than silently reuse this envelope. For the Jacobian comparison use inherited CE1-I cap L_j=4Pmax(0)*exp(-4c*u_j), valid over both exact and reconstructed paths.

The Dini comparison e_ell'+<=e_h+rho_ell; e_h'+<=L_j*e_ell+eta_j+rho_h applies using the positive 2x2 comparison semigroup for each panel and exact stored binary Hermite knot jumps. Same initial error and whole-panel Taylor3/fourth residual budget as CE1-I. Source-only panel contributions newly recomputed; other ref16 terms are SHA-verified reused evidence.

## Limit and adversarial checks

At u0=0, eta_0 equals the old global cap; if c=0 the comparison reverts to old bound or tighter only through local boxing; if source Q=M, D=0 and eta may still be conservatively positive. Negative mass, time-dependent source weights, collisions, tilt, or general Bianchi family break the current theorem's hypotheses. The lambda and source frame are not changed. No inference of measured-sky physical error or floating numerical RK4 true-error independence from MPFR program execution.

## Check

Wolfram single-ray exact algebra output {1,0}: scaled pressure ratio 1 and sum of partial derivatives +4P_i=0. Python targeted 94 PASS for original source and modified code; independently reported PR243/244 adversarial tests RED before changes and GREEN after; the same-model review does not close distinct-author R6/C9.
