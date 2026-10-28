# BASS CE1-D 연구보고서: 물리 입력 불확실성의 비섭동적 기하학 전달

**상태:** `COMPLETE_SCOPED_PHYSICAL_INPUT_INTERVAL_TRANSFER`; 상위 CE-1 `PARTIAL`, 상위 DAG **9/15**. 부모 PR235, HEAD `41a20d7a69751ad77a392a669d97bd05566ec822`. 원본 CE1-C ZIP SHA-256 `a96f2b8a7373d9b9af33ef60e6d5cba6fec55f5c45ed546f0c27bcc0556a5b5d` 검증. 전용 child branch, 원격 main/owner/부모 branch 변경 없음.

## 정의와 출발점

CE1-C는 **저장된 정확한 이진수** 초기자료 및 reconstruction에 대한 MPFR-directed nominal-path upper `B_h^nom=7.3457959948804625e-6` (u=0..1, ntheta8,nphi16,RK4 64)을 제공했다. CE1-D는 이를 다시 계산하지 않고, 사용자가 별도로 선언한 **정확한 유리수 십진수 구간**과 nominal 이진자료 사이의 물리 입력 오차를 전파한다. 사용자 입력의 실측 acquisition uncertainty가 선언된 구간 안에 있다는 사실까지 증명하는 것은 아니다.

서명 (-,+,+,+), normal proper time `u=t/T_*`, `ell_i=ln a_i`, `h_i=T_*H_i`, `E,P_i=(8 pi G T_*²/c²)×(물리 에너지밀도·압력)`이다. Λ=0, 대각·반사대칭 Bianchi I의 무질량 무충돌 복사를 다루며, 모든 초기 방향별 팽창 h_i(0)>=0, 양의 4차 angular polynomial이라는 제한을 둔다. 진화 자체는 비선형이며 진화 도중 작은 섭동 근사, 모멘트 폐쇄, constraint projection, weight 재정규화, clipping을 수행하지 않는다.

기본 continuum 초기 복사 에너지분포는

\[
F_0(q)=\frac{E_0}{4\pi}\big[1+c_2P_2(q_z)+c_t(q_x^2-q_y^2)+c_4P_4(q_z)\big].
\]

`E_0,c_2,c_t,c_4,s_x,s_y`에 각각 독립된 decimal center ± radius를 입력하고, `s_z=-s_x-s_y`를 정확히 적용한다. 센터 0.9와 float64(0.9)의 차이도 0으로 취급하지 않는다. E의 하한은 양수여야 하며 angular polynomial과 모든 initial h_i의 positivity를 구간 전체에서 확인한다.

## 유도: L1 source 차이에서 비선형 기하학 오차로

`b_i=exp(-2ell_i)`, `r(q,ell)=sqrt(sum_i b_i q_i²)`, `V=exp(sum_i ell_i)`라 하면

\[
P_i(\ell)=V^{-1}\int_{S^2}F_0(q)\frac{b_iq_i^2}{r}\,d\Omega.
\]

전 방향 팽창에서는 ell_i>=0, 정상화된 연속 q에서 `b_i q_i²/r <= r <= 1`, `V>=1`이므로

\[
\|\Delta P(\ell)\|_\infty\le\int_{S^2}|\Delta F_0|\,d\Omega.
\]

기준의 angular shape는 양수이고 평균 1이다. 임의의 허용 parameter 변화에 대해 triangle inequality를 적용하면 `|delta E| + Emax * (basis L1 mean × |delta c|)`이 나온다. 기저 상계는

\[
\langle|P_2|\rangle=2/(3\sqrt3)<2/5,\quad
\langle|q_x^2-q_y^2|\rangle=4/(3\pi)<4/9,\quad
\langle|P_4|\rangle\le \sqrt{\langle P_4^2\rangle}=1/3.
\]

따라서

\[
\boxed{\eta_{\rm input}=\delta E+E_{\max}
\left(\tfrac25\delta c_2+\tfrac49\delta c_t+\tfrac13\delta c_4\right)}
\]

가 모든 expanding geometry에서 uniform source difference upper이다. 여기서 δ는 **입력 box에서 기존 정확한 이진수 reference까지의 최대 거리**다. 양의 angular shape의 exact-rational 최소값에서 계수 δ의 합을 빼 positivity margin을 확인한다. 초기 Hamiltonian 해는

\[
\bar h_0=\sqrt{[E_0+(s_x^2+s_y^2+s_z^2)/2]/3},\qquad h_{i0}=\bar h_0+s_i.
\]

이 구간식을 MPFR 192비트 RNDD/RNDU로 직접 평가하고 `h_i0>0` 여부와 reference 차이 y0를 구한다. CE1-A의 nonlinear comparison은

\[
D^+x\le y,\qquad D^+y\le4E_{\max}x+\eta_{\rm input},\qquad x(0)=0,\ y(0)\le y_0
\]

이다. 이에 따라 `k=2 sqrt(Emax)`에서

\[
y(u)\le y_0\cosh(ku)+\eta_{\rm input}\sinh(ku)/k.
\]

이 입력 불확실성 upper와 **이미 검증된 CE1-C nominal-path upper를 triangle inequality로 더한다**. 진화방정식의 선형화가 아니라 두 유한 진폭 해의 차이에 대한 비교부등식이다.

## 계산 결과와 목표 선택

`u∈[0,1]`, nominal `E0=.9`, `(c2,ct,c4)=(.6,.25,.2)`, `(sx,sy)=(.2,-.13)`이고, nominal CE1-C는 nθ8,nφ16,RK4 64 그대로다. 각 입력 box의 radius는 다음과 같다.

| 구간 | δE | δ(c2,ct,c4) 각각 | δ(sx,sy) 각각 | input-only h upper | nominal + input total h upper | 목표 1e-5 |
|---|---:|---:|---:|---:|---:|---|
| tight | 1e-8 | 1e-7 | 1e-8 | 2.824341364e-7 | **7.628230131e-6** | **PASS** |
| medium | 5e-8 | 5e-7 | 5e-8 | 1.412170765e-6 | **8.757966760e-6** | **PASS** |
| wide | 5e-6 | 1e-5 | 1e-6 | 3.919461738e-5 | 4.654041338e-5 | **NOT MET** |

세 입력 box 모두 이번 fixture에서 positivity 및 전 방향 초기 팽창 조건을 만족한다. Tight에서는 source difference upper `1.160000012e-7`, 초기 geometry rate upper `2.439820239e-8`, propagated source-to-h upper `1.992573216e-7`이다. 이는 CE1-C nominal-path upper `7.345795995e-6`와 분리되어 있다.

참조 nonlinear Einstein-Vlasov IVP 1회와 네 개 perturbation IVP를 SciPy DOP853 (`rtol=1e-12`, `atol=1e-14`), 별도의 nθ32 angular grid로 수행했다. 관찰된 최대 endpoint rate 차이 `7.623235487e-9`는 tight input-only upper `2.824341364e-7` 안에 있다. 또한 두 angular source perturbation의 nθ64 pressure gap은 각각 `6.416274692e-9`와 `5.193795796e-9`로 `η=1.160000012e-7`보다 작았다. 이 표본 비교는 반증 시험이지 uniform bound의 근거가 아니다.

Wolfram exact CAS에서 `⟨|P2|⟩=2/(3sqrt3)`, `⟨|q_x²-q_y²|⟩=4/(3pi)`, `⟨P4²⟩=1/9`를 재확인했다.

## 검증과 한계

새 모듈 `bianchi.nonperturbative.einstein_input_enclosure`, 새 테스트 `tests/nonperturbative/test_einstein_physical_input.py`. 새 5개 테스트, 이전 CE1-C/B 27개 테스트를 함께 실행해 **32 PASS**. 부모 수치 코드와 source identity는 보존했다. 별도 S1 GitHub workflow와 설치 wheel numerical smoke 성공. Native Rust, native subagent, 독립 모델 심사, 전체 저장소 policy PASS는 주장이 아니다.

초기 TDD의 첫 RED는 모듈이 없어 collection 단계에서 실패한 것으로, 의미론적 RED assertion까지 확인한 사례는 아니다. 이후 구현과 focused/회귀 Green은 실행했다.

**주요 제외:** nonpolynomial/unknown angular field, contracting sectors, spatially inhomogeneous Einstein constraints, generic tilted collisional coupling, 측정값이 선언된 interval에 포함되는지에 대한 실험적 보증, formal proof of Python+MPFR binding. 기존 CE1-C nominal upper를 전달받으므로 그 전제와 구현 검증 한계를 그대로 상속한다. Production_ready=false, merge_ready=false.

## 판정 및 다음 의무

`CE1-D=COMPLETE_SCOPED_PHYSICAL_INPUT_INTERVAL_TRANSFER`, `CE-1=PARTIAL`, 상위 DAG **9/15**. 기존 노드 이름·의존성 변경 없음. 다음 CE1-E는 양의 일반 nonpolynomial angular field의 구적 상계를 구성하거나 MPFR 소프트웨어 보증을 독립 검토하는 후보이며 이번에는 수행하지 않았다. Main/owner/부모 브랜치 merge는 수행하지 않았다.
