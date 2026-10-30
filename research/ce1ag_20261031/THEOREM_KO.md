# CE1-AG | 원래 6-cell 연속 Einstein–Vlasov 해의 전체 구간 shear-work 양성 증명

**선택된 물리 단위:** `CE1AG_CONTINUUM_SHEAR_WORK_SIGN`. Immutable base: Draft PR #284,
`a3e1139e043e3f42f682a0dd84857db819972e73`.

## 모델과 주장

대각 Bianchi I, signature `(-,+,+,+)`, `Λ=0`; 원래 source-array SHA-256
`022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035`의
여섯 개 양의 continuous angular cell과 초기 전단 `σ(0)=(.2,-.13,-.07)`의
**exact binary64 값**만 사용한다. 무질량, 무충돌, reflection-even Vlasov 분포이고
`u=t/Tstar∈[0,2/25]`, `ell_i=ln a_i`, `h_i=ell_i'`이다. 모든 진화변수는 원래
BASS Einstein-scale 무차원 정규화이며, 사용자의 원래 `h=10^-5` 목표를 변경하지 않는다.

`E=V∫U0 r dΩ`, `P_i=V∫U0 r x_i dΩ`, `R_ij=V∫U0 r x_i x_j dΩ`,
`V=exp(-Σell_i)`, `r²=Σ n_i²exp(-2ell_i)`, `x_i=n_i²exp(-2ell_i)/r²`로 놓고,
`H=(Σh_i)/3`, `σ_i=h_i-H`, `Π_i=P_i-E/3`, `W=Σσ_iΠ_i`, `q=W/E`를 정의한다.

**조건부 구간정리 (derived + exact rational checked).** 위 **특정** 원래 연속 여섯 cell
초기값 문제의 exact Einstein–Vlasov 해에서, 모든 `0≤u≤2/25`에 대해

\[
\boxed{q(u)=W(u)/E(u)>1/5000=0.0002,\qquad W(u)>7/50000=0.00014.}
\]

이는 샘플된 GL quadrature의 양성 관측이 아니라, source continuum 적분과 Einstein ODE를
대상으로 하는 수학적 비교논증이다. 다만 수학적 독립 저자 검증(R6/C9)은 미수행이며,
보편적인 모든 Vlasov 분포 또는 `u>2/25`에 대한 정리는 아니다.

## 1. 초기값의 순수 유리수 경계

원래 binary64 셀 질량은 `[[.1,.25,.05],[.2,.15,.15]]`,
`|n_z|` 경계는 `[0,1/2,1]`, `2φ/π` 경계는 `[0,1/4,3/4,1]`이다.
이를 `Fraction.from_float`로 exact dyadic rational로 해석한다.

\[
E_0=\sum e_{ij},\quad P_{z0}=\sum e_{ij}\langle\mu^2\rangle_i,\quad
D=\sum_i(1-\langle\mu^2\rangle_i)(e_{i0}-e_{i2})>0,
\]
\[
P_{x0}-P_{y0}=(2\sqrt2/\pi)D,
\quad W_0=A+B(2\sqrt2/\pi)D,
\]
\[
A=\frac{\sigma_{x0}+\sigma_{y0}}2(E_0-P_{z0})+\sigma_{z0}P_{z0},\quad
B=\frac{\sigma_{x0}-\sigma_{y0}}2>0.
\]

`7/5<sqrt(2)<3/2`와 `3<π<22/7`를 각각 아래/위에서 대입하면
`W0>A+B D (2(7/5)/(22/7)) ≡ W_L > 0.007175`.
아울러 `2sqrt(2)/π<1`이므로 `Pz0/E0<37/100` 및
`(E0-Pz0+D)/(2E0)<37/100`을 유리수로 검증한다. 따라서
`0≤w_i(0)=P_i(0)/E0<37/100`이고 `899/1000<E0<901/1000`이다.

`S0=1/2 Σσ_i0²`, `H0²=(E0+S0)/3`의 유리수 비교로
`5/9<H0<14/25`와 모든 `h_i0>0`, `h_i0<77/100`을 확인한다.

## 2. 실제 해의 a priori bounds

양의 angular source는 `E>0`, `P_i≥0`, `Σ P_i=E`, `R/E≽0`를 보장한다.
Einstein–Liouville 방정식은

\[
h_i'=-\theta h_i+P_i,\quad E'=-\theta E-\sum_i h_iP_i,\quad
\theta=3H.
\]

`h_i0>0`와 `P_i≥0` 때문에 `h_i(u)>0`; 따라서 `E'≤0`, `E≤E0<E_U=901/1000`.
또한 `h_i'≤E_U`, 따라서 `0≤ell_i(u)≤u(77/100+E_U U)<7/100=L`
(`U=2/25`). 이 a priori bound는 다음 pressure bound에 의존하지 않으므로 순환논증이 아니다.

`e^-L≤r≤1`, `x_i≤e^(2L)n_i²`이므로

\[
w_i(u)\le e^{3L}w_i(0)<\frac{37/100}{1-3L}=\frac{37}{79}<\frac23,
\]

여기서 `e^x≤1/(1-x)` (`0≤x<1`)만 사용했다. 따라서 `|Π_i|≤E_U/3`.
Constraint `3H²=E+S`, `S=Σσ_i²/2≥0`는 초기에서 성립하며,
`C'=-2θC`로 보존된다. 따라서 `H'=-2H²-S/3`,
`-3H²≤H'≤-2H²`, 그리고 양의 `H`에 대해

\[
\theta(u)\ge\frac{3H_0}{1+3H_0u}>
\frac{3(5/9)}{1+3(5/9)(2/25)}=\frac{25}{17},\qquad H(u)<14/25.
\]

이제 `σ_i'=-θσ_i+Π_i`에 적분인자를 적용하면

\[
|\sigma_i(u)|\le |\sigma_{i0}|e^{-\theta_*u}+
\frac{E_U}{3\theta_*}(1-e^{-\theta_*u})\le M,
\quad \theta_* =25/17,\quad M=\frac{15317}{75000}.
\]

초기 `max|σ_i(0)|<M`도 정확한 유리수로 확인했다. 이 bound는 미리
`W>0`를 가정하지 않는다.

## 3. Shear-work ratio의 exact 진화식과 부호 지속

`w_i=P_i/E`, `\mathcal R_{ij}=R_{ij}/E`로 두면

\[
w_i'=-2\sigma_i w_i+\sum_j\mathcal R_{ij}\sigma_j+q w_i,
\quad \sigma_i'=-3H\sigma_i+E(w_i-1/3).
\]

따라서 **정확히**

\[
q'=-3Hq+E\sum_i(w_i-1/3)^2
      -2\sum_i\sigma_i^2w_i+\sigma^\top\mathcal R\sigma+q^2.
\]

`\mathcal R≽0`, `w_i≥0`, `Σw_i=1`, `|σ_i|≤M`이므로
`q'≥-3Hq-2M²`. `q0>0`이고 첫 영점을 가정한 구간에서는 `q≥0`, 
따라서 `k=3(14/25)=42/25`로 `q'≥-kq-2M²`.
적분인자 비교와 `e^-x≥1-x`로 첫 영점 이전의 모든 `u≤U`에서

\[
q(u)>\frac{W_L}{E_U}(1-ku)-2M^2u\ge
\frac{W_L}{E_U}(1-kU)-2M^2U
=\frac{282337963103396223725684080109845874770027}
{1284922339656339027092095786549248000000000000}>
\frac1{5000}.
\]

첫 영점에서 `q=0`이면 이 엄격한 양의 하계와 모순이므로 영점은 존재하지 않는다.
결국 전체 구간에서 `q(u)>1/5000`이다. 이 핵심 단계는 **상대적으로 작은 초기
관측된 q가 아니더라도** 조건의 분명한 정량 크기 때문에 유효하다.

마지막으로 `E'/E=-θ-Σh_iw_i≥-K`,
`K=42/25+77/100+(901/1000)(2/25)=15763/6250`. 따라서

\[
E(u)\ge E_0e^{-Ku}>\frac{899}{1000}(1-KU)
=\frac{28031719}{39062500}>\frac7{10},
\]

즉 모든 구간에서 `W(u)=E(u)q(u)>(7/10)(1/5000)=7/50000`.

## 확인 상태, 한계, 문헌

- **derived:** Liouville moment hierarchy, Einstein constraint propagation,
  `q'` exact formula, finite-horizon differential comparison, existence continuation.
- **exact-rational-checked:** original raw binary64 source SHA, initial angular moments,
  W0 lower, pressure/geometry/Einstein/shear bounds, strictly positive rational remainder.
- **numerically checked:** standalone 401-row analytic lower curve and two independent GL3/GL5
  finite-difference checks of the q-evolution identity. (These GL checks validate the
  formula, **not** the analytic continuum bound.)
- **NOT_RUN:** genuinely independent author R6/C9, interval-enclosed original 6D ODE,
  non-diagonal Bianchi, observational likelihood, production release.

The literature establishes the Einstein–Vlasov Bianchi I setting and shear-stress
propagation, but the present finite-interval six-cell sign inequality is a direct
new construction **within this project**, not a literature-verified novelty claim:
Heinzle & Uggla, CQG 23 (2006), doi:10.1088/0264-9381/23/10/016;
Lee, Nungesser & Tod, GRG 52 (2020), doi:10.1007/s10714-020-02699-7.

Upper DAG remains **9/15**, CE1 **PARTIAL**, R/C **18/20 scoped**,
new completed upper nodes **0**, `production=false`, `merge=false`, `auto_next=false`.
This run stops after one bounded unit.
