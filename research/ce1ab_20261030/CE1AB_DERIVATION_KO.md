# CE1-AB | 원본 양의 six-cell Einstein–Vlasov 연속 DOP853 IVP 및 rank-2 전파

단위: `CE1AB_DOP853_CONTINUOUS_IVP_MPFR192_GEOMETRY_TO_GRAM_20261030`.
권위: `cosmosapjw-quantum/bass` PR275 pinned HEAD `bc06cb2fc3952477b437891d8b04650f8f164b40`.
원본 source SHA256 `022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035`.
유지: 원래 six positive binary64 angular cells, reflection-even, massless collisionless, diagonal expanding Bianchi I, Λ=0, signature (-,+,+,+), 정상계 proper u=t/Tstar, 범위 [0,0.08], initial shear (.2,-.13,-.07), 원래 strict h<1e-5. 원본 PR273/PR275 병합 또는 변경 없음.

## 1. 직접 계산한 정확한 IVP 대상

`ell_i = log a_i`, `h_i = d ell_i / du`, `theta = sum_i h_i`, dimensionless `E=8 pi G Tstar^2 rho_energy / c^2`. 원본 exact dyadic GL ray `n_q`와 positive mass `w_q`는 **renormalization 없이 그대로** 쓴다.

\[
\dot\ell_i=h_i,\quad \dot h_i=-\theta h_i+P_i(\ell),\quad P_i(\ell)=e^{-\sum_j\ell_j}\sum_q w_q\frac{q_i}{\sqrt{Q}},\quad q_i=n_{qi}^2e^{-2\ell_i},\quad Q=\sum_iq_i.
\]

`ell(0)=0`, `h_i(0)=sqrt((E(0)+sum shear_i^2/2)/3)+shear_i`. MPFR192 초기조건 구간이 저장 binary64 시작점과의 차이를 엄밀히 감싼다.

## 2. 원본 경로의 정확한 복원과 다항식 잔차

원본 CE1-U `ce1u_physical_histories.py`는 `solve_ivp(...method='DOP853', rtol=3e-12, atol=3e-14, t_eval=linspace(0,.08,41))`이다. **원본에서 적응 내부 스텝/조밀출력 계수를 따로 저장하지 않았다.** CE1-AB는 같은 original RHS/IC/GL 원자료와 SciPy 1.17.0, NumPy 2.3.5에서 DOP853 `dense_output=True`를 재실행하여 양쪽 모두 41x6 저장 상태를 exact binary64 비교로 완전히 재현했다. 원본 적응 계수 자체의 archival byte identity라고 주장하지 않는다.

각 adaptive segment에서 `s=(u-t_old)/h`, SciPy DOP853 실제 7차 `F_0,...,F_6`을 정확한 binary64 hex로 저장한다. 실제 `Dop853DenseOutput`의 nested recurrence를 구간 자동미분하여 `p(s),p_s(s),p_ss(s)`를 계산하며 각 `F`와 시작 상태는 exact dyadic real로 해석한다. `h`와 `t`도 같은 방식이다. 최종 실수시간 knot는 `s_end=(t_end-t_old)/h`로 계산하여 binary64 덧셈/뺄셈의 미세한 차이를 숨기지 않는다.

RHS `f(y)=(h,-theta h+P(ell))`의 연속 결함 및 미분:

\[
r(u)=p'(u)-f(p(u)),\quad
r'_{\ell_i}=p''_{\ell_i}-p'_{h_i},\quad
r'_{h_i}=p''_{h_i}+\theta' h_i+\theta p'_{h_i}-\sum_jJ_{ij}(\ell)p'_{\ell_j}.
\]

정확한 pressure Jacobian은
\[
J_{ij}=-(1+2\delta_{ij})P_i+R_{ij},\qquad
R_{ij}=e^{-\sum\ell_k}\sum_qw_q\frac{q_iq_j}{Q^{3/2}}.
\]
Wolfram symbolic differentiation과 원본 함수의 독립적 중앙차분으로 식을 검산했다. positive ray에서 `R_ij>=0`, `sum_j R_ij=P_i`이며 `sum_j |J_ij|=5P_i`다.

각 adaptive segment를 `N=32`개 실시간 slab으로 분해한다. 모든 실수값을 MPFR192 RNDD/RNDU outward로 처리하여 다음 상계를 계산한다.
\[
\sup_{u\in I_k}|r(u)|_\infty\leq
|r(m_k)|_\infty+\frac{|I_k|}{2}\sup_{u\in I_k}|r'(u)|_\infty.
\]
최대 `r`/`r'`는 192bit interval automatic differentiation의 연산 결과다. 잔차 상계 후반 합산, 초기조건, 구간 경계 jump, Grönwall 지수도 MPFR192 방향성 반올림으로 마무리한다. 점 샘플과 exact dyadic dense polynomial의 차이도 따로 측정한다.

## 3. 구간 비교 정리: 연속 ODE의 실제 해

전체 길이 T는 저장된 binary64 종료점으로 취급한다. 채택한 충분한 비교 tube는 `ell_i∈[-.001,.081], h_i∈[0,.9]`. 원본 양의 GL mass 총합 `sum w<.91`, 정확한 `||n_q||²<1+10^-12`, `e^.004<=250/249`로 tube 내부 `0<E<.92`임을 exact rational로 확인한다. `|theta|<=2.7`과 `|h_i|<=.9`에서 RHS ∞-norm Lipschitz `L<=max(1,5E+5.4)<10<12`. 실행에는 보수적인 `L=12` 사용.

`rho`가 모든 segment의 MPFR 상계, `j_k`가 내부 knot jump, `eta_0`가 초기조건 오차라면 (선형화가 아닌 exact nonlinear Grönwall 비교)
\[
\|y(u)-p(u)\|_\infty\leq e^{12T}\eta_0+\frac{e^{12T}-1}{12}\rho+\sum_{t_k<T}e^{12(T-t_k)}j_k=:\eta_{\rm GL}.
\]
각 slab의 interval polynomial bounds와 비교하여 `p +- eta_GL`가 tube에 포함되는 것을 확인했다. 따라서 continuation argument에 의해 이는 단순 수치적 유사성이 아닌 **연속한 exact GL-source ODE 해의 a posteriori enclosure**이다. 그린 함수 등 추가 closure가 들어간 것은 아니다.

## 4. 원래 six-cell exact continuum source의 self-consistent 진화로 이동

기존 PR264의 exact-rational source-to-stored-GL **exact ODE solution-to-solution** transport bound (GL6 `5.474586575721355e-13`, GL8 `1.1315891404909281e-14`)를 source theorem identity가 일치할 때만 재사용한다. 저장 마지막 binary64 종료점은 유리수 `2/25`보다 정확히 `3/1801439850948198400`만큼 크다. 초기 원본 소스 상계와 Lipschitz 7을 사용해 이 극미량 연장 및 구형 decimal bound 표시 오차를 합해 `1e-20`을 추가로 허용한다. 모든 실제 정확한 해의 `ell∈[0,.08]`는 positivity `h>0`과 전체 tube `h<.9, T<.081`에서 따라오므로 PR264/PR270 angular box 가정은 유지된다.

\[
\eta_{\rm original\leftrightarrow saved}\leq\eta_{\rm GL}+\eta_{\rm sampled\leftrightarrow polynomial}+\eta_{\rm exact\ source\leftrightarrow exact\ GL\ ODE}+10^{-20}.
\]

여기서 `saved`는 PR275의 원래 binary64 41개 기하학 상태다. 국소 오차처럼 서로 다른 선형화 궤적을 혼동하지 않는다.

## 5. 원래 연속 angular source Gram rank2 전파

원본 정상 tetrad의 볼로메트릭 에너지 각도 분포에서 `x_i=q_i/Q`, `W_q=w_q sqrt(Q)`, `T_40=35x_3²−30x_3+3`, `T_42=(x_1−x_2)(7x_3−1)`, `T_44=x_1²−6x_1x_2+x_2²`.

`M0=sum W`, `M_m=sum W T_m`, `c_40=3/(16sqrt(pi))`, `c_42=(3/8)sqrt(5/(2pi))`, `c_44=(3/16)sqrt(35/(2pi))`. 원본 normalized source coefficient `alpha_m=4pi c_m M_m/M0`이고,

\[
\partial_j x_i=2x_i(x_j-\delta_{ij}),\quad
\partial_j W=-Wx_j,\quad
\partial_j\alpha_m=4\pi c_m\left(\frac{M'_{mj}}{M_0}-\frac{M_m M'_{0j}}{M_0^2}\right).
\]

원래 MPFR192 angular coefficient 계산은 다시 증명하지 않고, 새 코드는 이 analytic Jacobian만 41개 `ell_saved ± eta` 입방구간에서 정확한 원본 stored GL rays/mass로 interval evaluated했다. `X_{t,\cdot}=(alpha40/3, sqrt(2)alpha42/3, sqrt(2)alpha44/3)`; `S=X^TX` (41x3 sample Gram). 계산한 Jacobian ∞ row bound로 `||DeltaX||F`를, 원래 `X` MPFR 하/상계로 `||Xref||F`를 구해
\[
\|S_{\mathrm{GL},\mathrm{true}}-S_{\mathrm{GL},\mathrm{saved}}\|_2\leq
2\|X_{\mathrm{saved}}\|_F\|\Delta X\|_F+\|\Delta X\|_F^2.
\]

원본 PR270의 continuum angular six-cell source-only `K4delta` full 41x41 entrywise exact rational error (동일 geometry 어느 곳에서나 적용)로 PR275가 얻은 λ2 하계를 이 기하학 섭동에 대해 Weyl 이동한다. 완전히 다른 RK4/Hermite sibling PR273의 인증 경로나 source coefficient를 끌어오지 않는다.

새로 엄격하게 긍정한 대상은 **연속 자기일관 Einstein–Vlasov 시공간에서 41개 시간에 평가한 원본 볼로메트릭 결정론적 `l=4` Gram의 λ2>0**이다. 따라서 연속시간 deterministic kernel의 rank≥2도 귀결되지만, 그 적분연산자의 양의 두 번째 고유값에 동일한 수치 하계를 주장하지 않는다. λ3, 온도·분극·ensemble covariance/likelihood는 NOT_CERTIFIED.

## 6. Claim gate와 독립성

- Established/reused: PR264 exact source-vs-exact-GL ODE geometry, PR270 uniform angular source comparison, PR275 fixed-geometry MPFR source/Gram λ2.
- Derived and MPFR192 numerically checked: exact-dyadic DOP853 replay dense-polynomial interval defect, true GL IVP enclosure, 41-epoch Jacobian and Gram perturbation.
- Conditional mathematical claim: original six-cell exact self-consistent Einstein–Vlasov 41-sample `lambda2 > 0` if original predecessor proofs and currently reused libmpfr.so.6 ctypes direction contracts are accepted.
- Implementation verification: targeted pytest, frozen-hash checks, local original-state exact comparison; no independent distinct-author R6/C9, no full whole-program formal MPFR verification.
- Upper DAG **9/15 (21 edges)**, CE1 PARTIAL, scoped R/C **18/20**, production=false, merge=false, auto_next=false.

**Single bounded unit STOP. No additional upper node promotion and no cross-sibling merge.**
