# CE1-AD: 원래 six-cell Einstein–Vlasov의 41시점 세 번째 Gram 고유값 엄격 하계

**주장 상태**: `DERIVED + EXACT_RATIONAL_INTERVAL_CHECKED`, 단 원본 PR270/264/277의 정리와 `libmpfr.so.6` 192-bit directed 계산의 정확성을 상속하는 **조건부 인증**. 제3자 독립 R6/C9, 전체 프로그램 형식증명은 미실행. 원래 상위 DAG=9/15, CE1=PARTIAL.

## 1. 원본과 컨벤션

- 모형: 원래 정확 이진유리수 양의 여섯 angular cell, 반사대칭, massless collisionless Einstein–Vlasov, 대각 Bianchi I, Λ=0, 서명 (-,+,+,+).
- 고유시간 `u=t/Tstar ∈ [0,0.08]`; 기존 `h<1e-5` 기하 목표 불변. 무차원 `E=8πG Tstar²ρ_energy/c²` 등 원래 우변 사용.
- 원본 고정 source SHA-256 `022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035`.
- 부모 Draft PR #280 HEAD `15dd3ad604f0219132984b7b23538ef91aeff87e`; PR277 HEAD `1ee44436da37a45b6322c3606f0fb43998bed83c`의 조건부 41시점 IVP 경계를 상속. 옛 형제 Draft를 병합하지 않는다.

`α_m(u)=4π a_{4m}(u)/E(u)` (`m=0,2,4`)로 정의하고

\[
X(u)=\frac13\big(\alpha_{40}(u),\sqrt2\alpha_{42}(u),\sqrt2\alpha_{44}(u)\big),\qquad
K_4(u,v)=X(u)\cdot X(v).
\]

원래 41개 고정 고유시간 `u_j=.002 j`에서 `A_{jm}=X_m(u_j)`와 `S=A^T A`를 정의한다. `S`는 시간적 **sampled deterministic Gram**이며 ensemble covariance, 연속시간 적분연산자, 열적 CMB 온도 파워가 아니다.

## 2. 구성적 유도: 작은 특이값 직접 전파

기존 CE1-AB의 Gram-Weyl 이동 상계는 `~7.696×10⁻⁶`이지만 세 번째 `λ₃≈5.7133×10⁻¹¹`이므로 직접 고유값 이동으로는 인증할 수 없다. 그러나 41×3 배열로 되돌리면

\[
\begin{aligned}
A_* &= A_{GL}(\ell^D)+\Delta A_{geometry}+\Delta A_{source},\\
\|\Delta A\|_2 &\leq \|\Delta A\|_F \leq B_{geom}+B_{src},\\
\sigma_3(A_*)&\geq\sigma_3(A_{GL}(\ell^D))-B_{geom}-B_{src}.
\end{aligned}
\]

여기서 `*`는 **원래 정확한 연속 각도분포와 자기일관 Einstein–Vlasov 해**이다. `D`는 PR277이 원본 41시점 저장 경로와 연결한 고정 이진 DOP853 수치기하다. `B_geom`은 PR277의 outward 192-bit, 각 시점 3성분 Jacobian까지 포함한 `frob_deltaX_upper`를 **그대로 사용**한다. 새 계산에서 기하 오차를 임의로 축소하지 않는다.

PR270의 정확 유리 source-only 각도 정리는 동일 `ell∈[0,.08]^3`에서 각 `|δα_{4m}|≤ε_m`를 인증한다. 따라서

\[
B_{src}\leq \sqrt{\frac{41}{9}\big(\epsilon_{40}^2+2\epsilon_{42}^2+2\epsilon_{44}^2\big)}.
\]

입력 `EXACT_SIX_CELL_L4_SOURCE.json`의 huge rational 분자/분모를 그대로 파싱한다. 실제 upper: GL6 `2.9345748717779428×10⁻⁸`, GL8 `1.4358710129615821×10⁻⁹`. 

## 3. 저장 GL 행렬의 엄격한 특이값 하계

PR275의 각 시점 방향성 MPFR192 구간 `alpha_mpfr192`를 `mpfr_get_str(base16)` mantissa/exponent로 읽고 **정확한 `Fraction` 이진유리수**로 복원한다. √2는 정수 제곱근 10⁻⁷⁵ 바깥구간으로 감싼다. 이 41×3 구간행렬 `A_ref`에 대해 각 곱과 합을 유리수 하·상계로 평가한 `S_ref=A_ref^T A_ref`의 3×3 대칭 구간을 구한다.

\[
s_0=\frac{7549}{10^9}=7.549\times10^{-6},\quad M=S_{ref}-s_0^2 I_3.
\]

Sylvester 양정성 판정에서 세 leading principal minor의 **엄격한 유리 하계**가 모두 양수이다.

| 유리 구간 증인 | GL6 lower | GL8 lower |
|---|---:|---:|
| `M11` | 0.0848074214905894064237390588983900439272 | 0.0848074214905890639146796904832990204534 |
| `det M[:2,:2]` | 0.0000014342099230862800599491328406041643 | 0.0000014342099225095675726669908935462873 |
| `det M` | 2.45159842211690175455215413134604e-18 | 2.44788106949980130945184828381546e-18 |

따라서 `σ₃(A_ref)>s₀`가 **exact-rational interval checked**이다. 최초 binary64 표시형 endpoint를 사용한 경우에는 세 번째 determinant 구간이 0을 포함해서 FAIL이 발생했고, 원본 192-bit mantissa를 사용하는 것으로 진단·복구했다. 16-bit 또는 double 단순 변경으로 PASS라 주장하지 않는다.

## 4. 연속 Einstein–Vlasov 41시점으로의 결론

| 상계/하계 (무차원 41-point) | GL6 | GL8 |
|---|---:|---:|
| `σ₃(A_ref)` | `>7.549e-6` | `>7.549e-6` |
| `B_geom` (PR277) | `5.7761807820414045e-6` | `5.776215993679961e-6` |
| `B_src` (PR270) | `<2.9345748717779428e-8` (상향표시) | `<1.4358710129615821e-9` |
| `σ₃(A_*)` | `>1.7434734692408160e-6` | `>1.7713481353070770e-6` |
| `λ₃(S_*)` | `>3.0396997379466069e-12` | `>3.1376742164558589e-12` |

**양쪽에 대해 공통 결론**:

\[
\boxed{\lambda_3\!\left(\sum_{j=0}^{40}X_*(u_j)X_*(u_j)^T\right)>3\times 10^{-12}}.
\]

이는 PR280의 정성적 **continuous-time rank=3**을 실제 원래 41시점의 정량 하계로 연결한 첫 번째 명시적 대상이다. 정의에 따르는 유한합이지 표준 CMB 관측 스펙트럼/시간 적분연산자 고유값에 대한 정량 하계가 아니다. 원래 상위 9/15 완료 노드 승격은 하지 않으며, CE1 전체 gate는 여전히 PARTIAL이다.

## 5. 새 물리 데이터와 판별력

기존 원본 41시점 MPFR sky와 CE1-AC time jets를 사용해 `X40,X42,X44`, **세 번째 직교 시간모드 진폭** `z₃(u)=X_ref(u)·v₃` 및 두 시간미분을 82행 CSV로 새로 생성했다. `v₃`는 각 GL reference 행렬의 오른쪽 최소 특이벡터이며 `v₃[2]>0`의 부호 관례로 고정했다. 부호 관례 자체는 물리적 부호가 아니다.

- GL6·GL8의 `σ₃(ref)`는 각각 약 `7.55865652034e-6`, `7.55864188786e-6` (수치 진단).
- 두 source에서 `z₃(u)`가 0을 지나는 이산 시점 구간은 공통으로 `(0.014,0.016)`, `(0.062,0.064)`이다. 이는 **고정 mode projection의 부호변화**이며 물리적 instability나 새로운 mode onset이 아니다.
- 41개 시점의 가장 큰 절대 3행 determinant가 GL6 `1.27677304616e-9`, GL8 `1.27677055229e-9`로 `u=(0,0.038,0.08)`에서 관측되었다 (수치 진단).

## 6. 신뢰 경계와 문헌

**상속된 조건**: PR270 exact real 저장 GL ray 대 continuum 각도 source 정리, PR264 continuum-versus-GL exact ODE geometry 비교, PR277 MPFR192 DOP853 adaptive trajectory/tube + 41-point angular Jacobian 구간 계산, PR275 sky MPFR192 RNDD/RNDU 구현의 올바름. 본 계산은 이 원본 theorem을 다른 경로로 **재증명하지 않으며** 새로운 유리 3×3 Sylvester/SVD 전파만 독립 계산한다.

**판정**: source-level theoretical/conditional strict rank3-41 sample: `DERIVED, EXACT_RATIONAL_INTERVAL_CHECKED, IMPLEMENTATION_VERIFIED_SCOPED`. 별도 저자 검증/형식증명 `NOT_RUN`; production/merge `false`; 다음 node 자동진입 `false`.

참고: Neher, Jackson & Nedialkov, *On Taylor Model Based Integration of ODEs*, SIAM J. Numer. Anal. 45 (2007), DOI:10.1137/050638448; Heinzle & Uggla, *Dynamics of the spatially homogeneous Bianchi type I Einstein–Vlasov equations*, CQG 23 (2006) 3463, DOI:10.1088/0264-9381/23/10/016. 검증된 ODE 일반론과 원본 모델 동역학에 관한 문헌이며, 이번 특정 six-cell 41-point Gram 값의 문헌 우선권을 주장하지 않는다.
