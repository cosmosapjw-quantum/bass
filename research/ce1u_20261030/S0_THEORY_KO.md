# BASS CE1-U | 원본 연속 각도 source 대 실제 GL6/GL8 source의 전구간 엄밀 경계

Date: 2026-10-30 KST. **Theory stage S0**, 상위 DAG **9/15**, 21 edges, CE1=PARTIAL.

## Authority and locked physical meaning

- Repo `cosmosapjw-quantum/bass`; parent CE1-T PR #263 HEAD `db144f755eacaade0cf34cb6555631d5a73feaad`; independent siblings PR #262 and ancestors #261, #259, #258 untouched.
- Original source lock SHA-256 `022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035`: `mu=[0,.5,1]`, `t=2 phi/pi=[0,.25,.75,1]`, binary64 `Eij=[[.1,.25,.05],[.2,.15,.15]]`, shear `(.2,-.13,-.07)`, eight reflections.
- Massless, collisionless, unpolarized, positive, reflection-even, expanding *diagonal Bianchi I*, Lambda=0, signature `(-,+,+,+)`, `a_i(0)=1`, `u=t/Tstar` in `[0,2/25]`; no spectral/thermal CMB or polarization assumption.
- Dimensionless `ell_i=ln a_i`, `h_i=dell_i/du`, `E=8 pi G Tstar² rho_energy/c²` and similarly normalized diagonal pressures.

## Exact pressure expression

For an initial unit direction `n` in the original cell angular measure, set `b_i=exp(-2ell_i)`, `v=exp(-sum ell_i)`, `r=sqrt(sum b_j n_j²)`. The exact continuum stress is

`P_i^C(ell) = v ∫ U0(n) b_i n_i² / r dOmega_0`.

The numerical GLn source is **not** a replaced fluid closure: `P_i^Q(ell)=v sum_q w_q b_i N_{qi}² / sqrt(sum_j b_j N_{qj}²)`, with each `w_q` and `N_{qi}` interpreted as the exact dyadic rational represented by the stored binary64. In each physical cell the positive tensor GLn mass is `Eij*omega_a*omega_b/4` and there are `6n²` positive-octant rays. These rays are a quadrature, not the continuum measure itself.

## A finite exact-rational enclosure, valid for every ell_i in [0,2/25]

Choose `B=23/25`, `alpha_i=(b_i-B)/B`. Since `e^(-x)>=1-x` for `x>=0`, `b_i` lies in `[21/25,1]` and `|alpha_i|<=2/23`. The stored GL rays satisfy `||N||²=1+delta_q` with `|delta_q|<10^-12` by exact dyadic rational comparison. Therefore `|X|=|sum_i alpha_i N_i²|<q=1/11`; for true unit continuum `|X|<=2/23`.

For `K=12`, use the exact finite identity and bounded tail

`(1+X)^(-1/2) = sum_{k=0}^{12} (-1)^k binom(2k,k)/4^k X^k + R_12`, with `|R_12| <= q^13/(1-q)`.

The `i` pressure polynomial at degree `k` contains monomial moments `M_{abc}=∫U0 n_x^(2a)n_y^(2b)n_z^(2c) dOmega0` for `a+b+c=k+1`, compared with exactly stored GL ray moments `sum w_q N_{qx}^{2a}N_{qy}^{2b}N_{qz}^{2c}`. There are **559 distinct monomials** for degrees 1..13.

For each cell the continuum moment factorizes as

`Eij * <mu^(2c)(1-mu²)^(a+b)>_[mu_i,mu_i+1] * <cos^(2a)phi sin^(2b)phi>_[t_j,t_j+1]`.

The `mu` average is a finite rational polynomial integral. Expanding the trigonometric factor into cosine Fourier modes yields an **exact** expression `A+(B+C sqrt(2))/pi` with rational A,B,C, because every original phi endpoint is `0,pi/8,3pi/8,pi/2`. The code evaluates it by exact Fractions, with rational enclosures of `pi` from the alternating Machin arctan series and of `sqrt(2)` by integer square-root bounds. All GL monomials are exact dyadic rationals. No floating rounding enters the certificate summation.

Let `D_{abc}` be the exact outward absolute discrepancy of each monomial. Then

`eps_i <= (21/20) sum_{k=0}^{12} [binom(2k,k)/4^k] q^k sum_{a+b+c=k} [k!/(a!b!c!)] D_{a+delta_ix,b+delta_iy,c+delta_iz}`

`          + 2*(21/20)*(91/100)*q^13/(1-q) + 2 sum_q w_q | ||N_q||²-1 |`.

The last term is essential: stored binary64 `N_q` is not *exactly* unit length. Indeed `r_Q²=B(1+X+delta_q)` while the surrogate polynomial uses `B(1+X)`. Both radicands exceed `.83`; by the mean value theorem `|x^(-1/2)-y^(-1/2)| <= |x-y|` on this domain, and positivity allows the conservative correction `2 sum w_q |delta_q|`. The positive source weights are strictly below `.91`. The common prefactor `v b_i/sqrt(B) <= 21/20`. The resulting expression is an **exact rational upper bound** for the continuum-to-**stored-binary64-ray exact-real source** on the entire box, not just an empirical GL40 comparison.

## Transport from pressure discrepancy into exact coupled Einstein–Vlasov geometry

The locked ODE is `ell_i'=h_i`, `h_i'=-theta h_i + P_i(ell)` with `theta=sum h_i`. For both positive sources initial `0<h_i<1`. At the boundaries `h_i=0` the derivative is `P_i>=0`, and at `h_i=1` the derivative is `<=-1+Emax<0`; hence `0<h_i<1` and `0<=ell_i<=u<=.08` persist. On this invariant region `E<=.91`.

The pressure Jacobian is exact:

`partial P_i/partial ell_j=-(1+2delta_ij)P_i+R_ij`, `R_ij=v∫ U0 b_i n_i² b_j n_j²/r³`, `0<=R_ij<=P_i`.

Its row absolute sum is at most `5 P_i<=5`, while the `h` part of `partial h_i'/partial h_j` has row sum `theta+3h_i<=6`.

Set `X=||ell^C-ell^Q||_∞`, `Y=||h^C-h^Q||_∞`, `Z=X+Y`. Then `D^+ Z<=7 Z+eps`, `eps=max eps_i`. The initial expansion difference is bounded by `Z(0)<=deltaE0/3`, where `deltaE0=|sum_q w_q-E0|+sum_q w_q| ||N_q||²-1 |` and the Hamiltonian positive square root derivative is below 1/3.

With `T=2/25`, `7T=14/25`, and the rational inequality `e^x<=1/(1-x)` for `0<=x<1`, obtain the fully explicit bound

`max_(0<=u<=T) |delta h_i| <= max Z(u) <= (25/11)*(deltaE0/3)+(2/11)*eps`.

The pressure and geometry bounds in `data/GL6_source_exact_bound.json` and `data/GL8_source_exact_bound.json` meet the pre-existing `1e-5` h target. This is an **exact-solution-to-exact-solution** comparison, not a proof of the accuracy of a particular numerical integrator's computed state.

## Scope and proof limits

- Positivity and original physical angular cell identities must hold; distinct stored GL6/8 ray SHA values are bound explicitly.
- The exact-rational proof is stronger than a sampled MPFR test but is **not MPFR192 interval IVP integration**. Subsequent fresh MPFR192 pointwise E/P checks do not certify DOP853/RK4 trajectories.
- `GL40` is a numerical reference only, not an interval-certified continuum enclosure. Any claim about `C4'` in the coupled solution is tested numerically and is not bounded by the pressure-only comparison unless an additional observable stability argument is supplied.
- No auto-merge or production promotion. Upper DAG stays **9/15** until an actual top-level node gate closes; true distinct-author R6/C9 remain `NOT_RUN`.

## Independent checks

Wolfram `Integrate` verifies the first-cell cosine-squared average `1/2+sqrt(2)/pi` and independent `mu` factor `11/12`. Scoped Python tests check the symbolic exact massless trace identity, 559 monomial enumeration, source hashes, positivity, parity and code implementation. They are not distinct-author validation.
