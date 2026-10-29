# BASS CE1-N: 패널 내부 source forcing 감소에 대한 구성적 정리

## R1–R3: 원본 계약과 검증 경계

- 원본 frozen 문제: metric (-,+,+,+), Λ=0, all-direction expanding diagonal Bianchi I; massless, collisionless, reflection-even, nonnegative six-cell continuum angular measure M and its stored binary64 positive ray/mass quadrature Q.
- 시간/좌표: u=t/Tstar, ell_i=ln(a_i), h_i=Tstar H_i, u∈[0,0.08], 4 RK4/Hermite panels, 원래 target max_i |Δh_i| < 1e-5.
- 물리표: mu=[0,.5,1], phi_fraction=[0,.25,.75,1], energies=[[.1,.25,.05],[.2,.15,.15]], shear=(.2,-.13,-.07), exact stored binary64 semantics.
- 부모 PR253 e4a0feba0e8709d5e996ed8ef4c9c9bf1da4c4d0, direct physical data lock/positive mass PR251; duplicate sibling PR252 separately reviewed; original upper DAG 9/15, 21 edges, CE-1 PARTIAL. No merge, no change of physical equation, source measure, initial root, integration method, Emax, or target.

## R4–R5: 정리 1, 연속/저장 경로 공통 확장률 하한

Exact continuum Einstein-Vlasov:

  ell_i' = h_i,    h_i' = -theta h_i + P_i,    theta = sum_i h_i,
  theta' = -theta^2 + E,
  E = (theta^2 - sum_i h_i^2)/2 <= theta^2/3.

Positive initial h_i and P_i>=0 imply theta(u)<=theta0/(1+(2/3)theta0 u), and

  h_i(u) >= h_i(0) [1+(2/3)theta0 u]^(-3/2) > 0.

For panel j with right endpoint u_{j+1}, outward MPFR lower

  kappa_exact,j = min_i lower(h_i0/(1+(2/3)theta0 u_{j+1})^(3/2)).

Stored exact-real binary Hermite cubic ell_i(v)=c0+c1 v+c2 v^2+c3 v^3, v∈[0,1], physical delta u_j>0. Degree-2 Bernstein controls of d ell_i/du:

  [c1, c1+c2, c1+2c2+3c3] / delta u_j.

The coefficients, delta u and division are interpreted as exact Fraction binary64 rationals; their minimum is converted to an outward MPFR lower:

  kappa_stored,j = min_{i,k} beta_{ik}/delta u_j.

Set kappa_j=min(kappa_exact,j,kappa_stored,j)>0. Parent CE1-M's certified panel-start m_j guarantees ell_i(u_j)>=m_j for BOTH exact and stored paths, including the stored polynomial left-knot identity. Hence for all u within panel

  ell_i(u) >= m_j + kappa_j (u-u_j).

The m_j, parent bounds B_i and current exact source/path SHA are preserved. The new derivative proof is not a claim of global Einstein-Boltzmann or arbitrary Bianchi dynamics.

## R5: 정리 2, 연속적으로 감소하는 source discrepancy

For fixed angular source X=M or Q, pressure P_i^X(ell+s 1)=e^(-4s)P_i^X(ell); therefore D_i=P_i^M-P_i^Q has the same degree -4 covariance. The parent CE1-M has certified eta_j valid for every ell with ell_i>=m_j and ell_i<=B_i, by taking the minimum of valid global and shifted-box source certs.

For u in panel j let delta=u-u_j>=0, s=m_j+kappa_j delta. Then x_i=ell_i(u)-s in [0,B_i-m_j]. The existing MPFR-certified nonnegative-box source error E_Q(B-m_j 1) applies to x; the GLOBAL E_Q(B) also applies to ell_i(u)-kappa_j delta. Therefore

  |D_i(ell(u))| <= eta_j exp(-4 kappa_j delta).

No monotonicity assumption about E_Q as an algorithm is required: both original box bounds are separately valid, and the minimum is applied only after each separate scale transformation.

## R5–R7: 정리 3, 양의 비교계와 directed staircase

The error vector z=(e_ell,e_h)^T satisfies the componentwise Dini comparison

  D+z <= [[0,1],[L_j,0]] z + (rho_ell,rho_h+eta_j exp(-4 kappa_j delta))^T,

where L_j=4 P_max,j is the unchanged CE1-I Jacobian coefficient. The matrix is Metzler, so its semigroup is positive. For subintervals delta∈[k Δ_j/n,(k+1) Δ_j/n], replace only the source forcing by its left endpoint

  eta_{j,k} = eta_j exp(-4 kappa_j k Δ_j/n).

Since exp(-4 kappa_j delta) is decreasing and eta_{j,k} is outward upper bounded using MPFR192, this piecewise-constant source forcing dominates the true allowed source. Every original panel's initial error, Taylor3+fourth whole-panel time residual, and exact-binary endpoint jumps remain unchanged; the source component alone is repropagated with the original positive `propagate_interval` operator.

At n=1 the CE1-M bound is recovered exactly on the frozen binary evidence. For dyadic refinement, exact-real positive comparison yields a nonincreasing sequence of source-only bounds (up to outward arithmetic overestimation). Define the exact surrogate source forcing eta_j exp(-4 kappa_j delta). Since each left-staircase is at most exp(4 kappa_j Δ_j/n) times this surrogate on its subinterval, the source-only propagated result is at most

  C_n = max_j exp(4 kappa_j Δ_j/n)

times the exact continuous-forcing surrogate result, by positivity of the complete piecewise semigroup. This multiplicative overshoot statement applies to the chosen comparison surrogate, NOT to the unknown physical model error. Original rho/time/jump carriers are excluded from this factor.

## Independent checks and interpretation

- Wolfram algebra: source common-shift ratio 1, pressure row derivative sum residual 0; exact degree-2 Bernstein derivative identity 0 and positive matrix-exponential forcing integral identity 0.
- 65-digit independent mpmath direct variation-of-constants integral below the MPFR staircase enclosure, and 120 synthetic 95-digit independent constant-force 2x2 matrix solutions below MPFR positive propagator.
- Primary literature context: A. Neumaier, *Global, rigorous and realistic bounds for the solution of dissipative differential equations. Part I: Theory*, Computing 52 (1994), DOI 10.1007/BF02276880, on logarithmic norms and differential inequalities; J.M. Heinzle and C. Uggla (2006), DOI 10.1088/0264-9381/23/10/016, on spatially homogeneous Bianchi I Einstein–Vlasov dynamics. These papers are context, NOT a source for the project-specific panel source theorem.
- Current implementation is an MPFR192 numerical oracle, NOT formally verified Python/ctypes/MPFR, NOT native Rust production; distinct-author R6/C9 remain NOT_RUN.
