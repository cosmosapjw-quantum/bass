# CE1-X S0 | Original BASS Rust l=4 two-time sky: certified angular source + geometry transfer

2026-10-30 KST · parent PR268 frozen HEAD `c4d303ebd8294df8a4b564b140b88fc8e57b0e67`; sibling PR269 geometry sensitivity HEAD `9728915cd586115dde1f1d2dc32ebe8fffc2a9f3` is **read-only reference**, not merged. Original BASS Rust `_rustcore/src/kinetic/comoving.rs` Git blob `a29b12b5e7b0d529bddaf9eac53cfdb984ddaa84`. Upper BASS DAG **9/15**, CE-1 PARTIAL.

## Actual missing physics
The prior PR269 correctly demonstrated that pressure-only source discrepancy cannot bound l=4 source observables: positive angular densities `1±eta P4(qz)` can have identical E/P but distinct a40. Thus this work derives source error for the full **three surviving reflection-even real l=4 harmonic components** and transplants the existing certified geometry error from the *original exact-binary RK4/Hermite path*, never from an unverified DOP853 sample.

## Frozen mathematical model
Original exact binary64 six positive angular cells SHA256 `022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035`, eight reflections, no tilt/polarization/collision, massless collisionless all-expanding diagonal Bianchi I Λ=0, metric (-,+,+,+), proper u=t/Tstar in [0,.08], shear (.2,-.13,-.07). Finite positive cell continuum and the separate stored binary64 GL6 (216 rays), GL8 (384 rays); no smoothing the ray sky or changing the physical source. Exact source/geometry target `max|Δh|<1e-5` unchanged. The present new output is an **energy-integrated normal-frame deterministic harmonic cross-kernel**, not thermodynamic temperature C_l or a cosmological stochastic likelihood.

Define `b_i=e^{-2ell_i}`, `v=e^{-sum ell_i}`, `r=sqrt(sum b_i n_i²)`, `t_i=b_i n_i²/r²`, positive initial ray weights w, `a_lm=∫v r Y_lm*(s) dE0`, observer incoming sky `s=-M n/r`, M=diag(e^-ell). Reflection parity leaves the real components a40,a42,a44. With Condon-Shortley harmonics:
```
C40=3/(16 sqrt(pi)), C42=(3/8) sqrt(5/(2pi)), C44=(3/16) sqrt(35/(2pi)).
a40=C40 v [35 b_z² <n_z^4/r³> -30 b_z<n_z²/r>+3<r>].
a42=C42 v [7 b_z (b_x<n_x²n_z²/r³>-b_y<n_y²n_z²/r³>)
            -(b_x<n_x²/r>-b_y<n_y²/r>)].
a44=C44 v [b_x²<n_x^4/r³>-6b_xb_y<n_x²n_y²/r³>
             +b_y²<n_y^4/r³>].
```
Angle brackets mean exact original positive physical cell measure; the stored GL ray expression uses **its exact binary64 dyadic rationals**.

## Exact-rational 6-cell moment source certificate (new)
Import the already pinned exact arithmetic donor `research/ce1v_20261030/donor/ce1u_cert_source.py` Git blob `0e8ef8375cf5f26a9a020d6ec878e4b77b5d0560`, rather than another numerical GL40 reference. Its original-cell continuum even monomial moments `M_abc=<n_x^(2a)n_y^(2b)n_z^(2c)>` are exactly Q(sqrt2,pi) with rigorous rational enclosures of pi (Machin) and sqrt2 (integer isqrt). Stored GL moments are exact dyadic Fractions, including non-unit native directions.

Set B=23/25 and `alpha_j=(b_j-B)/B`; for all `0<=ell_i<=.08`, `|alpha_j|<=2/23<q=1/11`. For exact unit continuum `r²=B(1+X)` with `X=sum alpha_i n_i²`; stored binary64 rays satisfy `r²=B(1+X+δ)`, `δ=Σ n_i²-1`, `|δ|<1e-12`. For each monomial numerator n_x^(2a)n_y^(2b)n_z^(2c) of degree m=0,1,2, use `beta=1/2-m`, K=12:
```
(1+X)^beta = sum_{k=0}^K binomial(beta,k) X^k + R.
D_abc = |M_abc^continuum - M_abc^stored|_upper (exact rational).
poly_error = Σ_k |binomial(beta,k)| q^k Σ_{i+j+h=k} k!/(i!j!h!)
                                D_{a+i,b+j,c+h}.
```
For beta=1/2,-1/2, `|R|<=q^(K+1)/(1-q)`; for beta=-3/2, use `|binomial(-3/2,k)|<=(2k+1)`, hence `|R|<=q^(K+1)[(2K+3)/(1-q)+2q/(1-q)^2]`. Since continuum total mass <.91 and stored mass <.91 with each stored monomial numerator <=2, the combined tail <=3|R|. On radicands >=.83 and m<=2 the derivative of `x^beta` has modulus <=3; including numerator <=2 and prefactor `v B^beta prod b_i^a <=6/5` yields a conservative **8 sum_a w_a |δ_a|** off-unit correction. Thus each raw term error:
`epsilon_(abc) <= (6/5)(poly_error + 3 tail) + 8 Σ_a w_a |δ_a|`.
Use rational upper coefficients `C40<1/9`, `C42<7/20`, `C44<1/2` and the explicit positive term-by-term sums above. No current binary64 pressure/source algorithm is substituted into the proof.

## Normalize and lift to unequal times
Energy discrepancy epsilon_E is the m=0 beta=+1/2 term. For all expanding ell_i<=.08 both continuum and stored positive E>=3/5 by the original mass and `exp(-.32)>=1-.32` lower bound (stored norm² in (1±1e-12)). For l=4, `|Y_lm|<=sqrt(9/(4pi))<1`; `4pi<13`; so `|Δalpha_lm|<= 13*(5/3)*(epsilon_a_lm+epsilon_E)` where `alpha=(4pi/E)a`. For the real reflection-even l4 kernel
`K4_delta(u,v) = [alpha40(u)alpha40(v)+2alpha42(u)alpha42(v)+2alpha44(u)alpha44(v)]/9`,
and `|alpha_lm|<=13`, source-only uniformly `|ΔK4| <= (130/9) max_m epsilon_alpha_m`.

The **different-geometry** carrier comes from the original verified CE1-W positive MPFR192 RK4/Hermite comparison (not parent PR269 unverified DOP853): positive comparison means `||ell^continuum(u)-ell^stored_interp(u)||inf<=epsilon_ell_terminal` for all 0<=u<=.08. The spherical addition theorem and `∂ell alpha` formula give `|∂_{ell_j}K4delta| <=4pi*(1+sqrt(20)/2)<41`. At two epochs `|ΔK4_geometry|<=3*41*(epsilon_ell_u+epsilon_ell_v)<=246 epsilon_ell_terminal`. Add source-only and geometry by the triangle inequality. Read each **actual exact source and path SHA**, not only a historical display decimal.

## Implementation and trust boundaries
S1 will compute **outward exact-rational epsilon_E, epsilon_a40,a42,a44 and K4 source upper** from the frozen original-cell moment formula on `[0,.08]^3`, using PR264 donor methods with K+2=14 degrees. Combine with committed PR268 `final_ell_upper` for GL6/8 N4/N8/N16, preserving original proper-time path and source identity. BASS native Rust `Frame::apply/det/phys_dirs` via CE1-R executable will compute stored exact-source **binary64** a40/a42/a44 and K4δ(0,.08) on those paths and cross-check against an independent Python harmonic implementation. It is not itself an interval proof. True independent human-author R6/C9 and formal whole-code correctness remain NOT_RUN.

S0 status: theory/evidence contract only, no source numerical upper asserted prior to execution. Upper DAG **9/15**, 21 edges, CE-1 PARTIAL, production_ready=false, merge_ready=false, auto_next=false. Separate Git/Drive/Dropbox receipts required before backup SUCCESS claims. No auto-merge.
