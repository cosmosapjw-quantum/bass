# CE1-AE | original six-cell 연속시간 l=4 적분 Gram 정량 정리

2026-10-30. Parent: BASS Draft PR #281, pinned HEAD `f80f03d33a8b98cd49dfb9cda85ae316d868cdf6`. Immutable positive six exact-binary64 cells SHA256 `022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035`.

**Model:** massless collisionless reflection-even Bianchi I, diagonal metric signature (-,+,+,+), Λ=0. Proper dimensionless time `u=t/Tstar∈[0,2/25]`, frozen shear `(0.2,-0.13,-0.07)` as exact dyadic values. Original fixed geometry h tolerance `1e-5` unchanged. Bolometric nonthermal sky, not a stochastic ensemble or blackbody CMB.

## Theory and exact assumptions

Let conserved incoming direction n, `b_i=e^(-2ell_i)`, `Q=sum_i b_i n_i²`, `x_i=b_i n_i²/Q`, and let `⟨·⟩_u` denote the normalized positive six-cell angular measure proportional to `U0(n) sqrt(Q)`. The time-dependent bolometric fractional real-even `l=4` components are `alpha_m=4 pi k_m ⟨T_m(x)⟩_u`, with

- `T40=35 z²−30 z+3`, `T42=(x−y)(7z−1)`, `T44=x²−6xy+y²`;
- `4π k40=(3/4)sqrt(pi)<2`, `4π k42=(3/2)sqrt(5pi/2)<5`, `4π k44=(3/4)sqrt(35pi/2)<6`;
- `X(u)=(alpha40,sqrt(2)alpha42,sqrt(2)alpha44)/3`;
- `K4(u,v)=X(u)·X(v)`, `G=∫_0^(2/25) X(u) X(u)^T du` with **unweighted dimensionless proper time measure**.

Differentiation under the finite positive angular integral is allowed for bounded finite ell because `Q>0`. The normalized angular score is `∂ell_j log(sqrt Q) = −x_j`. Thus

`∂ell_j ⟨T⟩=⟨∂ell_j T⟩−⟨T(x_j−⟨x_j⟩)⟩`.

On the positive simplex x+y+z=1, `∂ell_j x_i=2x_i(x_j−δij)` and `|∂ell_j x_i|<=1/2`. Hence for every j:

| mode | `sup|T|` | `sup|∂ell_j T|` | `sup|∂ell_j alpha|` |
|---|---:|---:|---:|
| 40 | 8 | 20 | 56 |
| 42 | 6 | 19/2 | 155/2 |
| 44 | 1 | 6 | 42 |

The inequalities include normalization covariance, and are *uniform in ell*. Therefore `||∂ell_j X||₂ < sqrt((56/3)^2+(155/4)^2+21^2)<50`.

**Independent physical ODE upper on h:** In the positive original collisionless source, `0<P_i<=E`, and for initial `E0<1` and shear (0.2,-0.13,-0.07), `H0=√[(E0+½∑s²)/3]<3/5`, so all `h_i(0)<4/5` and strictly positive (using original `E0>.5`). `h'_i=−(∑ h)h_i+P_i`; a first-zero argument preserves positivity; expansion gives `E'=-∑h_i(E+P_i)≤0`. On `u∈[0,2/25]`, `h_i(u)≤h_i(0)+∫_0^u P_i(s)ds <4/5+2/25=22/25<9/10`. Thus `||X'(u)||₂≤∑h_j ||∂ell_j X||₂<3*(9/10)*50=135<150`.

**Inherited rigorous input:** CE1-AD #281 certified, conditional on PR264/270/275/277 MPFR192 implementation and original source contracts,

`lambda_min(S_41) > 3/10^12`, `S_41 = sum_{j=0}^{40} X(u_j) X(u_j)^T`, `u_j=j/500`, `u_40=2/25`.

Take an arbitrary unit v. The positive quadratic form of `S_41` implies

`∑_{j=0}^{40} |v·X(u_j)|² > 3/10^12 > 41/(4,000,000)²`.

Thus there exists an index j with `|v·X(u_j)| > a = 1/4,000,000`. Since `|d(v·X)/du|<L=150`, on a **one-sided interval** of length `δ=a/(2L)<(2/25)/2` extending inside `[0,2/25]` from that `u_j`, `|v·X(u)|>a/2`. Consequently

`v^T G v = ∫ |v·X(u)|² du > δ(a/2)² = a³/(8L) = 1/76800000000000000000000 > 1/10^23`.

Since this holds for every unit v,

**`lambda_3(G) > 10^-23`**, as a *conditional computer-assisted physical claim* inheriting the original 41-point theorem. The nonzero eigenvalues of the finite-rank integral operator `(Tf)(u)=∫K4(u,v)f(v)dv` on `L²([0,.08],du)` equal those of `G`; hence `lambda_3(T)>10^-23`. No pointwise-to-operator theorem beyond this finite-rank algebra is needed.

This lower bound is extremely loose and does not imply that the physically sampled numerical small eigenvalue (~1e-13) has been rigorously enclosed. It does not claim observer CMB temperature, E/B polarization, global perturbations, statistical likelihood, radiative transfer, or independent human-author review.

## Computational meaning

`continuous_kernel_physics.py` evaluates original source-locked 6D self-consistent massless Einstein–Vlasov trajectories and `X(u)` at 401 times for GL6, GL8, GL16, GL64, plus 1601-times convergence/replay for GL6 and GL8. It computes a Simpson quadrature approximation to `G`, its three SVD eigenvalues, and volume-diluted raw energy-sky `C4^U=(E/(4π))² C4^fractional`. Those values are **numerically checked, not part of the 10^-23 theorem**. `certify_dyadic_integral_surrogate.py` proves strict SPD of the *finite numerical Simpson surrogate* using exact Fractions from stored binary64 data; this is NOT a physical continuum integral certificate. `spectral_gap_certificate.py` checks the exact rational lemma and parent identities.

## Prior literature (context, not priority claim)

- J. M. Heinzle & C. Uggla, *Dynamics of the spatially homogeneous Bianchi type I Einstein–Vlasov equations*, **CQG 23** (2006) 3463–3489, doi:10.1088/0264-9381/23/10/016.
- H. Barzegar, D. Fajman & G. Heißel, *Isotropization of Slowly Expanding Spacetimes*, **PRD 101** (2020) 044046, doi:10.1103/PhysRevD.101.044046.
- M. Neher, K. R. Jackson & N. S. Nedialkov, *On Taylor Model Based Integration of ODEs*, **SIAM J. Numer. Anal. 45** (2007) 236–262, doi:10.1137/050638448, verified-integration background (not needed in new Lipschitz proof).

Original upper DAG `9/15` (21 edges), `CE1=PARTIAL`, scoped original `R/C=18/20`; no new parent node promotion. `R6/C9_DISTINCT_AUTHOR=NOT_RUN`, `PRODUCTION_READY=false`, `MERGE_READY=false`, `AUTO_NEXT=false`.
