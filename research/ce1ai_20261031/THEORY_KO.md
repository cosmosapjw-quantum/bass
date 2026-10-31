# BASS CE1AI | 원래 six-cell Einstein–Vlasov의 source mass transfer, 숨은 6차 각도 정보 및 사중극/16중극 재출현

**2026-10-31, 하나의 bounded physics unit.** 원본 권위는 Draft PR #287의 immutable HEAD `c7660436f233bfe94d954146017059fd79385dd5`, 초기 six-cell source-array SHA-256 `022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035`에 고정된다. 부모·원본 기하·허용오차·main·형제 PR 불변. Signature `(-,+,+,+)`, massless collisionless reflection-even Vlasov, diagonal Bianchi I, Λ=0, normal proper `u=t/Tstar ∈[0,2/25]`. `E`, `P_i`와 source cell energy는 기존 Einstein-scale 무차원 변수이며 `c`, `Tstar`를 새로 1로 선언하지 않는다.

## 1. 원본과 별도의 5차원 양의 source family

원래 여섯 양의 셀 질량 `e0=[[.1,.25,.05],[.2,.15,.15]]`은 변경하지 않는다. 각 셀은 `μ=|n_z|` 구간 `[0,1/2],[1/2,1]`과 `t=2φ/π` 구간 `[0,1/4],[1/4,3/4],[3/4,1]`의 조건부 각도 적분에 의해 정의된다. 기준 셀 `(0,1)`의 에너지에서 다른 다섯 셀로 에너지를 이전하는 단위 방향 `D_a`, `a=1,...,5`를 정한다.

`e(ε)=e0 + Σ_a ε_a D_a`. 모든 방향 `Σ_ij (D_a)_ij=0`이므로 전체 초기 복사 에너지 `E0`가 엄격히 고정되며, 충분히 작은 `|ε|`에서는 모든 셀 질량이 양수이다. 

**별도 추가 진단 방향**

\[
 D_{\rm dark}=\frac1{406}\begin{pmatrix}53&-106&53\\-203&406&-203\end{pmatrix}
\]

은 5개 방향의 선형결합이다. 독립적인 6번째 source 자유도가 아니다. 

## 2. 정확한 모멘트 및 완전한 source+Einstein 1차 변분

고정된 source 방향 `n`에 대해

\[
 V=e^{-\sum_i\ell_i},\; Q=\sum_i n_i^2e^{-2\ell_i},\;r=\sqrt Q,\;x_i=n_i^2e^{-2\ell_i}/Q.
\]

\[
 E=V\int U_0(n)r\,d\Omega,\quad P_i=V\int U_0(n)rx_i\,d\Omega,\quad
 R_{ik}=V\int U_0(n)rx_ix_k\,d\Omega.
\]

셀 질량의 변분을 `δU_0`로 쓰고 동일한 실제 `ell`에서의 source-only 변분을 `E_\mathrm{src}`, `P_{i,\mathrm{src}}`라 하면

\[
 \boxed{\delta E= -\sum_k(E+P_k)\delta\ell_k+E_{\rm src}},\qquad
 \boxed{\delta P_i=\sum_k(-P_i-2\delta_{ik}P_i+R_{ik})\delta\ell_k+P_{i,\rm src}}.
\]

`Σ_iP_{i,src}=E_src` 및 `Σ_iδP_i=δE`는 exact trace identities다. Einstein normal proper evolution은 `ell_i'=h_i`, `h_i'=-(Σ_k h_k)h_i+P_i`이고, 이것의 **source+geometry coupled tangent**는

\[
\boxed{(\delta\ell_i)'=\delta h_i,\qquad
(\delta h_i)'=-\theta\delta h_i-h_i\sum_k\delta h_k+\delta P_i}. 
\]

원본 초기 전단을 바꾸지 않고 `δε` source를 추가하므로 `δell_i(0)=δσ_i(0)=0`. 전체 초기 에너지가 보존되는 다섯 방향에서는 `δE0=0`이며 Hamiltonian constraint `3H^2=E+Sσ`를 미분한 `δH0=δE0/(6H0)=0`을 쓴다. 실제 GL 이산화의 마지막 비트 오차는 그 값을 명시적으로 계산하여 사용한다. 유한 perturbation에서는 최초 복사 에너지로 원래 constraint의 `H0`를 재구성한다. **원본 baseline geometry를 숨겨서 바꾸지 않는다.**

정규화한 real Condon–Shortley multipole은 `alpha_{lm}=4π(∫U r V ReY_lm)/E`. `l=2,4`의 reflection-even `m=0,2,4`를 추적한다. `α`의 변분에는 `δell`을 통한 geometry Jacobian뿐 아니라

\[
 \delta\alpha_{lm}^{\rm src}=\frac{4\pi}{E}\int \delta U_0 V r\,\Re Y_{lm}\,d\Omega-\alpha_{lm}\frac{E_{\rm src}}E
\]

가 필요하다. `C2=(α20²+2α22²)/5`, `C4=(α40²+2α42²+2α44²)/9`, `W=Σσ_i(P_i−E/3)`와 `F(u)=E(u)e^{4\bar\ell(u)}/E(0)`의 변분을 계산한다. 에너지 교환의 변분으로

\[
 \boxed{\delta\log F(u)=-\int_0^u\delta\big(W/E\big)(v)\,dv}
\]

이 성립한다. 복사 field는 비열적 angular energy sky이며 이 `C_l`은 CMB 온도 multipole이나 ensemble likelihood가 아니다.

## 3. 진짜 continuum source의 초기 rank 4와 정확한 dark direction

초기 원본 `ell_i=0`에서 source cell의 `μ²` 평균은 `1/12,7/12`, `μ⁴` 평균은 `1/80,31/80`; `M_i=⟨(1−μ²)²⟩_i`는 **`203/240,53/240`**이다.

여섯 셀 source 변분을 각 `μ`행의 (i) 행 합, (ii) 양 끝 `φ`셀 차, (iii) 가운데 대비 양 끝의 대칭 조합으로 분해한다. 행 합 두 개는 `δE`와 `δα20`으로 독립적으로 측정된다. 두 행의 `φ` 차는 `δα22`와 `δα42`에서 계수 행렬식 `21/20 ≠ 0`을 갖는다. 마지막 대칭 조합 두 개 중 `δα44`에는 `M0 T0+M1 T1`이라는 하나의 결합만 나타난다. 따라서 **`(δE, δα20, δα22, δα40, δα42, δα44)`의 six-cell source map은 정확히 rank 5**, `δE=0`의 5차원 family에서 다섯 `l=2,4` 응답 map은 정확히 **rank 4**다. 이것은 SVD의 반올림 결과가 아니다.

영공간을 생성하는 `Ddark`는 각 행의 합이 0이고 좌우 azimuth 셀 질량이 같고

\[
 53\frac{203}{240}-203\frac{53}{240}=0
\]

이므로 초기 총복사 에너지와 모든 reflection-even `l=2,4` 계수가 **원본 continuum에 대해 정확히 불변**이다. 같은 이유로 초기 `δP_i(0)=0`, `δR_ij(0)=0`이므로 초기 `δh_i(0)=δh_i'(0)=0`이다.

그러나 `f_{64}=(11n_z²−1)(n_x⁴−6n_x²n_y²+n_y⁴)`이라는 **차수 6 angular polynomial**은

\[
 \delta\langle f_{64}\rangle\big|_0=-\frac{4752}{1421\pi}\,\epsilon\ne0
\]

를 갖는다. 이는 normalized `Y64` 자체가 아니라 그 상수배인 witness로서, 4차 이하 정보로 구분되지 않은 두 분포의 초기 고차 각도 차이를 명시한다.

## 4. 정확한 초기 시간미분의 비영성: high-l → l=4 Liouville coupling

`X=n_x², Y=n_y², Z=n_z²`, `B=Σ_i h_i X_i`이고 `f42=c42(7Z−1)(X−Y)`, `c42=3/8 sqrt(5/(2π))`라고 놓자. 보존 공변 운동량 방향에서

\[
 (Vr)'=-(\theta+B)Vr,\quad X_i'=2X_i(B-h_i).
\]

이 두 식을 정확히 미분하면 `d_u(Vr f42)`의 차수 6 부분은 `21 c42 Z(X−Y) B`이다. 나머지는 차수 4 이하이며 `Ddark`가 정확히 소거한다. `X−Y=(1−Z)cos2φ`, `B=h_xX+h_yY+h_zZ`를 대입하면 source dark에서 살아남는 항은 `(h_x−h_y)Z(1−Z)²cos4φ/4`뿐이다. 원래 연속 angular cell의 양의 범위에서

\[
\delta\langle Z(1-Z)^2\cos4\phi\rangle\big|_0=-\frac{432}{1421\pi}\,\epsilon.
\]

정규화 변분의 다른 항은 `δE0=δE0'=δα42(0)=0`이므로 모두 소거된다. 따라서

\[
\boxed{\partial_\epsilon\partial_u\alpha_{42}(0,0)
=-\frac{1296}{203}\frac{\sigma_{x0}-\sigma_{y0}}{E_0}\cdot \frac38\sqrt{\frac{5}{2\pi}}<0.}
\]

원본 exact-binary64 shear와 `E0`로 계산하면 이 값은 **약 −0.783081077582325**다. 이는 source continuum의 정확한 국소 시간미분 정리이며 GL 근사의 결과가 아니다. 이 정리는 모든 가능한 분포에 대한 보편 no-go나 유한시간 전 구간의 엄격한 nonzero theorem을 의미하지 않는다.

## 5. 실행 데이터, 재사용성, 한계

`source/ce1ai_source_response.py`: GL6,8,16에 대해 고정 original six-cell baseline의 6D Einstein IVP 및 **여섯 명시적 source mode(5 independent+1 exact null combination)의 42D coupled tangent**를 401 proper epochs에 계산. `GL6/8`에서는 여섯 source mode ±1e−4에 대해 **실제 6D Einstein nonlinear IVP 24회**를 별도 재계산하여 finite-difference 대조한다. 총 1,203 baseline + 7,218 tangent + 9,624 nonlinear family physical records 및 1,203 singular-spectrum diagnostics, 7 physical plots. `source/certify_dark_initial_jet.py`는 원본 exact dyadic source에 대해 Fraction-rational 각도 모멘트와 비영 부호를 독립적으로 계산한다.

검증 구별: exact initial rank and first-time jet **derived + exact rational checked**, finite `u=.08` coupled response **numerically checked**, tests/CI **implementation verified**. 유한시간 source-to-l2/l4 numerical rank5는 실수 GL 수치에서 확인되지만 exact-continuum singular-value enclosure는 **NOT_RUN**. Genuine distinct-author R6/C9 **NOT_RUN**, production/merge **HOLD**. 기존 CE1 upper DAG **9/15, 21 edges, PARTIAL**, scoped R/C **18/20**, 새 upper node 완료 **0**.

## 원전과 비교

- Rendall, A. D., *The initial singularity in solutions of the Einstein–Vlasov system of Bianchi type I*, arXiv:gr-qc/9505017 (1995). Moment functional dependence와 과거 성질의 배경.
- Heinzle, J. M. & Uggla, C., *Dynamics of the spatially homogeneous Bianchi type I Einstein–Vlasov equations*, Class. Quantum Grav. **23**, 3463–3489 (2006), DOI 10.1088/0264-9381/23/10/016.
- Lee, H., Nungesser, E. & Tod, P., *On the future of solutions to the massless Einstein–Vlasov system in a Bianchi I cosmology*, Gen. Relativ. Gravit. **52**, 48 (2020), DOI 10.1007/s10714-020-02699-7, arXiv:1911.04937.

이 논문들은 Einstein–Vlasov Bianchi I의 설정을 뒷받침한다. **특정 여섯 셀 source의 dark vector와 시간미분 수치는 여기서 직접 유도된 결과**이며 문헌상 novelty 또는 논문 우선권 검증은 아니다.
