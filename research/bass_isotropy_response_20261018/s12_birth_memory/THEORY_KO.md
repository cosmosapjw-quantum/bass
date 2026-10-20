# S12 이론·수치 설계: Rust full birth-memory tangent와 한 실패 native 사례의 제한된 후속

## 상태와 선택

이 문서는 `physmath-research-loop` 1.3.0의 C1–C3에서 마련한 이론·수치 설계다. C1 계약은 `e48e0d5632634f6be2af63cf9059c8dd104882de`, tree `3904a366fa0c26ec422475bcc4fb24f4811cacf3`로 게시되었다. 현재 단계의 실행·자원·수락 기준은 [CONTRACT.json](CONTRACT.json)이 권위다. 아래 augmented Jacobian·partial_t·kernel·제약 전파·gauge의 51개 scalar identity는 [WOLFRAM_DERIVATIVES.json](WOLFRAM_DERIVATIVES.json)의 두 번째 호출에서 모두 0으로 확인됐다. 첫 호출의 문법/직렬화 실패도 보존했다. CAS 확인은 새 Rust 코드 검증을 대신하지 않는다. 기존 S8/S9/S10/S11 계산은 재사용하고 새 S12 실행 source/result commit을 사전에 만들어 쓰지 않는다.

주 작업은 **기존 S9/S10의 정확한 fixed-bank state JVP를 보존하면서, 새 Rust client에 과거 birth의 매개변수 의존성을 추가하는 full parameter tangent**이다. 한 번의 ray 순회에서 primal·Jacobian·birth-memory forcing을 함께 계산하는 최적화를 이 새 기능과 연결한다. 첫 물리 매개변수는 \(\theta=y_0\)이며, fixed birth schedule과 donor amplitude를 사용하는 기존 manufactured closed model로 제한한다. 별도 source-frame GL gauge는 \(\theta=b_0\)로 검사한다. Root의 C1 선택은 이 범위와 augmented6 J/JVP/partial_t, fused/prepared scalar evaluation, 작은 sandbox 검사 및 새 NCP 작업 준비다.

별도 작은 후속 작업은 **S8의 유일한 수치 실패 `b9_n64_P2P4` 한 행**에 S11 P24를 연결하는 것이다. 이것은 새 tangent 연구와 다른 물리 검증 단위이며 둘의 PASS를 합치지 않는다. 완료된 S8 native 17행, S8 Python tangent 8적분, S9 8history, S10 고정 workload, S11 projector 검사는 재실행 목록에서 제외한다.

## 1. C1 — 재사용 baseline과 새 수락 기준

### 1.1 고정된 권위와 남은 의무

- original REI owner: `0e25846433170d0f420c4cda44a0bedbf02cd177`.
- S11 실행 source: `7fb9b83cba01d37ce4cabbc4772527710601cd96`, tree `963a43f26df1f9c6f462b9df9a2c34cf99f525c9`.
- S11 결과·검토: `85d5833b4486d14855b84a9d967f5819788d05e5`, tree `fd3e994212059228501e26f7bf3d3b96462ba1d5`.
- S11 main 101/101, 독립 physics C9 235/235, provenance C9 152/152는 각각 다른 검사 집합이다. 이 기록의 통과는 새 Rust tangent 또는 실패 native history의 실행 결과가 아니다.
- S9/S10 완료 증거와 MF closed 2.973배·FLRW 4.115배는 해당 고정 workload에서만 재사용한다. Closed small의 이득 불확실성과 changing n16/cohort2의 0.9498173837599284배 회귀도 보존한다.
- S11은 양의 P246/KL projector와 S8 birth11의 점별 P24 수선을 제공했다. n64 P246 support 실패 및 49-point finite-\(d\) 예에서 P246/P24 최대 오차비 1.54913989382294는 남아 있다. P246을 모든 support나 finite-\(d\)에서 더 좋은 규칙으로 취급하지 않는다.
- 실제 MD14 정규화·donor closure·native Einstein/shear shared-Q 결합, evolving reactive full finite-bin spectral history, 넓은 finite-\(d\)/angular 고차 moment는 여전히 별도 의무다. `5.369926725506957e-12`는 제한된 source-deposition 설명이며 full spectral-history 수렴 증거가 아니다.

근거는 고정 [S11 결과](https://github.com/cosmosapjw-quantum/bass/blob/85d5833b4486d14855b84a9d967f5819788d05e5/research/bass_isotropy_response_20261018/s11_p246/RESULTS_KO.md), [결과 ledger](https://github.com/cosmosapjw-quantum/bass/blob/85d5833b4486d14855b84a9d967f5819788d05e5/research/bass_isotropy_response_20261018/s11_p246/RESULT_LEDGER.json), [S8 native 결과](https://github.com/cosmosapjw-quantum/bass/blob/85d5833b4486d14855b84a9d967f5819788d05e5/research/bass_isotropy_response_20261018/S8_NATIVE_REFINEMENT_KO.md)이다. 최종 배송 metadata와 새 cloud 상태의 권위는 부모 작업의 최신 intake에 있으며 이 이론 문서에서 다시 정의하지 않는다.

### 1.2 목표의 정확한 분류

S9 `FrozenBank::jvp`와 S10 `Evaluator::jvp`는 고정된 immutable birth bank에서 \(J_{\rm state}v\)를 정확히 제공한다. 이를 불완전한 state JVP 버그라고 부르지 않는다. 새 요구는 **모델의 매개변수를 바꿀 때 과거에 만들어진 bank 자체도 달라지는 전방 민감도**다. 새로운 companion memory와 forcing이 필요한 기능 추가이고, fused evaluation은 그 새 기능의 비용을 줄이는 후보 알고리즘이다.

물리 매개변수 단위에서는 \(\theta=y_0\)만 진화시키고 \(b_0\), donor, \(\Lambda\), birth 시각, birth amplitude는 고정한다. 별도 source-frame GL gauge에서만 \(\theta=b_0\)를 사용한다. 가변 event-time, \(\lambda\)·source amplitude 민감도, 반응률 민감도, P246 history는 확장 항목으로 남긴다. 모델을 넓히지 않고 해당 Rust 경로의 실제 미분을 완성하는 것이 목표다.

### 1.3 유지할 수락 기준

| 대상 | 제안에 적용하는 기준 | 근거·범위 |
|---|---|---|
| 새 isotropic birth의 norm/P2/P4 | 저장 binary64 입력의 exact rational 잔차 각각 \(\le3/10^{15}\) | 기존 admission 유지 |
| P6 | 선택한 새 birth에만 같은 exact gate | 첫 history의 필수 조건으로 추가하지 않음 |
| 물리 weights·reflection·source frame | 모든 \(\alpha_i>0\), 기존 parity·frame 검사 유지 | \(\alpha_\theta\)는 물리 weights가 아닌 signed derivative |
| KL covariance | \(\lambda_{\min}\ge10^{-10}\), \(\kappa_2\le10^8\) | 고정 S8 tangent 조건 |
| norm 미분 | \(|\sum_i\alpha_{i,b}|\le10^{-12}\) | S8의 별도 derivative gate |
| P2/P4 제약 미분 | 각각 절대값 \(\le10^{-11}\) | primal exact gate를 대체하지 않음 |
| 선형화 Hamiltonian·전파·cohort energy·birth event | S8 정규화 정의에서 각각 \(\le10^{-11}\) | 동일 정의를 Rust 입력 계약에 연결 |
| 독립 민감도 비교 | 새 비교에 적용할 Richardson joint 기준 \(\le10^{-8}\) | 기존 S8 지표·단위를 유지; 새 PASS는 미실행 |
| 속도 | 동일 입력·공차·출력·오차에서 timing과 변동 폭 보고 | 미리 가속 성공을 가정하지 않음 |

Exact primal admission, 미분 잔차, nonlinear finite-difference 비교는 다른 오차 질문이다. 서로 하나로 대체하거나 불리한 결과에 맞춰 tolerance를 완화하지 않는다. 새 Rust solver의 rtol/atol·관측 그리드는 소스와 함께 root가 freeze해야 한다. 기존 Python DOP853 설정을 다른 Rust solver의 동일 정확도 보장으로 해석하지 않는다.

## 2. C2 — 실제 source binding과 코드 경로

9개 소스의 full bytes를 고정 result tree에서 가져와 Git blob·크기와 대조했다. 소스를 import/build/run하지 않았다. 전부 [SOURCE_READBACK.json](native_followup/BASELINE_SOURCE_MANIFEST.json)에 URL, SHA256, Git blob이 있으며 다음 파일은 root가 그대로 재사용할 수 있다.

| 코드 경로 | 실제 역할 | Git blob |
|---|---|---|
| [s8_tangent_math.py](https://github.com/cosmosapjw-quantum/bass/blob/85d5833b4486d14855b84a9d967f5819788d05e5/research/bass_isotropy_response_20261018/s8_tangent_math.py) | kernel 편미분, moving-support KL implicit derivative, covariance gate | `a0ec1821168293b28d719a554c80a15cad3399fa` |
| [s8_tangent.py](https://github.com/cosmosapjw-quantum/bass/blob/85d5833b4486d14855b84a9d967f5819788d05e5/research/bass_isotropy_response_20261018/s8_tangent.py) | frozen tangent companion, direct chain-rule energy/stress, event·constraint 진단 | `e8ffff4fc2484a92806ff8ad53f245cbc3537c9b` |
| [S8_TANGENT_THEORY_KO.md](https://github.com/cosmosapjw-quantum/bass/blob/85d5833b4486d14855b84a9d967f5819788d05e5/research/bass_isotropy_response_20261018/S8_TANGENT_THEORY_KO.md) | 기존 complete Python tangent의 수식·8적분 계약 | `8ed790ed7b0991cb41b5289882d661bf24481e8a` |
| [s9_vigilode/src/lib.rs](https://github.com/cosmosapjw-quantum/bass/blob/85d5833b4486d14855b84a9d967f5819788d05e5/research/bass_isotropy_response_20261018/s9_vigilode/src/lib.rs) | `Cohort::moments`, `FrozenBank::eval/jvp`, event bank restart, `ClockProblem<4>` | `7eba07b0c541db103f2fa2f0d85dff7337ec6cd8` |
| [s10_optimization/src/kernel.rs](https://github.com/cosmosapjw-quantum/bass/blob/85d5833b4486d14855b84a9d967f5819788d05e5/research/bass_isotropy_response_20261018/s10_optimization/src/kernel.rs) | prepared SoA, exact state-bit cache, scalar/AVX2 ordered ray reduction | `ad7b3b6510aa92cfcc7223584c77be5b4d666afb` |
| [s10_optimization/src/lib.rs](https://github.com/cosmosapjw-quantum/bass/blob/85d5833b4486d14855b84a9d967f5819788d05e5/research/bass_isotropy_response_20261018/s10_optimization/src/lib.rs) | evaluator integration, physical client contracts | `88919d30da32c9d4ba729dfd0bbb863560faaab2` |
| [s10_optimization/src/runner.rs](https://github.com/cosmosapjw-quantum/bass/blob/85d5833b4486d14855b84a9d967f5819788d05e5/research/bass_isotropy_response_20261018/s10_optimization/src/runner.rs) | segment solving, fixed config, output and counters | `284682c63cb51a672fbf001fc14f1617976b0e4a` |
| [native_angular_refinement.rs](https://github.com/cosmosapjw-quantum/bass/blob/85d5833b4486d14855b84a9d967f5819788d05e5/research/bass_isotropy_response_20261018/native_angular_refinement.rs) | 별도 old32/new64 native blocks; 입력 CASES.csv의 행만 실행 | `e1e914fef1578306990f471b7730dd3a69f68781` |
| [run_s8_native_refinement.py](https://github.com/cosmosapjw-quantum/bass/blob/85d5833b4486d14855b84a9d967f5819788d05e5/research/bass_isotropy_response_20261018/run_s8_native_refinement.py) | 기존 18행 계약·owner staging·native ledger/continuum validation | `e6df488eeaa8bfeadb4aa364ca45a2df9767060b` |

마지막 두 파일에서 지정 CASES.csv 행만 실행하는 native binary와 18행을 고정하는 기존 wrapper의 역할을 구분한다. 새 작업에는 한 행만 명시한 새 계약과 wrapper를 준비한다.

### 2.1 기하와 model의 대응

Non-tilted axisymmetric Bianchi I, signature \((-,+,+,+)\)와

\[
a_\perp=ae^{-b},\qquad a_\parallel=ae^{2b},\qquad
s=\dot b,\qquad \Sigma=\sqrt3|s|/H
\]

를 고정한다. 무차원 변수는 실제 S8/S9 정의를 따른다.

\[
x=\log(a/a_{\rm ref}),\quad h=H/H_*,\quad y=s/H_*,\quad
E=\frac{8\pi G}{3c^2H_*^2}U,\quad
\Pi=\frac{8\pi G}{3c^2H_*^2}(P_\parallel-P_\perp),\quad
L=\frac{\Lambda c^2}{3H_*^2}.
\]

S9에 실제 구현된 fixed-bank 식은

\[
f_h=\frac{-h^2-2y^2-E_d/2-E_\gamma+L}{h},\quad
b'=y/h,\quad y'=-3y+\Pi/h.
\]

한 event 사이에는 \(E_d'=-3E_d\)이며 \(C=h^2-y^2-E_d-E_\gamma-L\)에 대해 \(C'=-2C\)다. donor/birth source는 이 제한된 closed model의 항이다. 실제 MD14 donor normalization 또는 native Einstein shared-Q가 이 식으로 이미 구현됐다고 주장하지 않는다.

고정 midpoint events \(u_j=(j+1/2)\Delta\), \(\Delta=X_B/K\)에서

\[
E_d^-=E_{d0}e^{-3u_j-\lambda j\Delta},\quad
L_j=E_d^-[-\operatorname{expm1}(-\lambda\Delta)]>0,\quad
E_d^+=E_d^-e^{-\lambda\Delta}.
\]

\(\theta=y_0\)에서는 \(u_{j,\theta}=L_{j,\theta}=E_{d,\theta}=L_\theta=0\)다. 초기 tangent는 \((h_\theta,b_\theta,y_\theta)=(y_0/h_0,0,1)\)이며 \(h_\theta=0\)으로 놓지 않는다.

## 3. C3 — full birth memory의 분리와 최적화 가능한 식

### 3.1 한 cohort의 직접 chain rule

\(d=b-b_j\), \(W=e^{2d}(1-\mu^2)\), \(V=e^{-4d}\mu^2\)라 하면

\[
R=\sqrt{W+V},\qquad D=(V-W/2)/R,\qquad C_j=L_je^{-4(x-u_j)}.
\]

S8에 이미 구현·검증된 편미분은

\[
R_d=-2D,\qquad
D_d=-\frac{W^2+14WV+4V^2}{2R^3},\qquad
R_\mu=\frac{\mu(e^{-4d}-e^{2d})}{R},
\]

\[
D_\mu=\frac{\mu(e^{2d}+2e^{-4d})}{R}
-\frac{D\mu(e^{-4d}-e^{2d})}{R^2}.
\]

새 birth에만 \(B_j=b_\theta(u_j)\), \(\mu_{ji,\theta}=\mu_{ji,b}B_j\), \(\alpha_{ji,\theta}=\alpha_{ji,b}B_j\)를 companion으로 저장한다. 실제 \(\mu,\alpha,b_j\)와 이 companion은 생성 뒤 불변이다. \(\theta=y_0\)에서 기존 stock은 \(B_j=\mu_\theta=\alpha_\theta=0\)다. 이 처리는 과거 물리 weights를 현재 상태에 맞춰 재가중하는 연산이 아니다.

별도 source-frame GL \(b_0\) gauge에서는 모든 현재 \(b\)와 과거 \(b_j\)를 같은 양만큼 이동시킨다. 초기 \(S=(0,1,0)\), 모든 old cohort의 \(B_j=1\), \(\mu_\theta=\alpha_\theta=0\)다. 새 GL birth도 \(B_j=S_b(u_j)\), \(\mu_\theta=\alpha_\theta=0\)로 만든다. 이때 \(d=b-b_j\)가 불변이므로 \(M_E=2\Pi\), \(M_\Pi=-\Pi_b\)이고 \(JS+g=0\)가 된다. 고정 coordinate support의 P24에서 \(b_0\)만 바꾸는 다른 물리 family를 이 gauge와 혼동하지 않는다.

직접 식은

\[
E_{\gamma,\theta}=\sum_{j,i}C_j\{\alpha_\theta R+
\alpha[R_d(b_\theta-B_j)+R_\mu\mu_\theta]\},
\]

\[
\Pi_\theta=\sum_{j,i}C_j\{\alpha_\theta D+
\alpha[D_d(b_\theta-B_j)+D_\mu\mu_\theta]\}.
\]

독립 scalar reference는 이 형태를 유지한다. optimized kernel의 memory decomposition과 동일한 코드를 호출하는 reference로 만들지 않는다.

### 3.2 J_state와 memory forcing의 정확한 분리

\[
M_E=\sum_{j,i}C_j[\alpha_\theta R-\alpha B_jR_d+\alpha\mu_\theta R_\mu],
\]

\[
M_\Pi=\sum_{j,i}C_j[\alpha_\theta D-\alpha B_jD_d+\alpha\mu_\theta D_\mu].
\]

그러면 \(E_{\gamma,\theta}=-2\Pi b_\theta+M_E\), \(\Pi_\theta=\Pi_b b_\theta+M_\Pi\)이고

\[
J=\begin{pmatrix}
-2-f_h/h&2\Pi/h&-4y/h\\
-y/h^2&0&1/h\\
-\Pi/h^2&\Pi_b/h&-3
\end{pmatrix},\qquad
S'=JS+g,\qquad
g=\begin{pmatrix}-M_E/h\\0\\M_\Pi/h\end{pmatrix}.
\]

여기서 \(S=(h_\theta,b_\theta,y_\theta)^T\)다. **현재 \(b_\theta\)의 효과는 이미 \(JS\)에 있으므로 memory forcing 안에 다시 더하지 않는다.** Companion bank가 고정된 한 segment에서는 \(M_E,M_\Pi\)가 현재 \(S\)와 독립이다. 다만 새로운 event의 \(B_j\)는 그 event까지 진화한 해당 tangent 열에서 만들어야 한다.

\[
C_\theta=2hS_h-2yS_y+2\Pi S_b-M_E,\qquad
C_\theta'=-2C_\theta.
\]

출생 순간에는 \(d=0\), \(S_b=B_j\), \(R=1\), \(R_\mu=0\)다. norm 및 P2 제약 미분에 따라 새 birth의 에너지·압력 tangent jump가 0이 된다. 이는 저장된 부동소수 값에서 별도 잔차로 검사해야 하는 식이며 선언만으로 PASS가 되지 않는다.

### 3.3 Moving-support KL derivative

고정 reference ray \(m_i\)의 birth source-frame 변환은

\[
R_b(m)=\sqrt{e^{2b}(1-m^2)+e^{-4b}m^2},\quad
\mu=me^{-2b}/R_b(m),\quad q_i\propto w_i/R_b(m_i)^3.
\]

따라서 \(\mu_b=-3\mu(1-\mu^2)\), \((\log q)_b=6(P_2-\langle P_2\rangle_q)\)다. \(\phi=(P_2,P_4)\), \(\phi_b=P_\ell'(\mu)\mu_b\)로 쓰고

\[
\alpha_i=\frac{q_i e^{\lambda\cdot\phi_i}}{\sum_kq_ke^{\lambda\cdot\phi_k}},\quad
a_i=(\log q_i)_b+\lambda\cdot\phi_{i,b},\quad
V=\operatorname{Cov}_\alpha(\phi,\phi)
\]

라 두면

\[
V\lambda_b=-\langle\phi_b\rangle_\alpha-
\operatorname{Cov}_\alpha(\phi,a),
\]

\[
\alpha_{i,b}=\alpha_i[(a_i-\langle a\rangle_\alpha)
+(\phi_i-\langle\phi\rangle_\alpha)\cdot\lambda_b].
\]

평균은 실제 저장된 approximate optimum에서 계산한다. 작은 primal moment 잔차를 임의로 0으로 바꾸지 않는다. \((P_2,P_4,P_6)\)에도 같은 구조가 적용되지만, first full-history unit에는 P24만 요구한다. 이 미분은 positive interior의 smooth ideal KL branch를 근사 최적점에서 평가한 것이다. solver stopping logic, IEEE 반올림 분기, feasibility 경계를 미분한다고 주장하지 않는다. rank·conditioning 실패에는 구체적인 status를 남기며 pseudoinverse나 음의 물리 weights를 넣지 않는다.

### 3.4 Augmented stiff Jacobian을 빠뜨리지 않는 구현 설계

\(z=(h,b,y)\), \(G=JS+g\)를 함께 적분하는 경우 full Jacobian은

\[
\frac{\partial(f,G)}{\partial(z,S)}=
\begin{pmatrix}J&0\\L_z&J\end{pmatrix},\qquad
L_z=\partial_z(JS+g).
\]

이를 block-diagonal \(\operatorname{diag}(J,J)\)로 대체한 뒤 exact Jacobian이라고 부르면 안 된다. 아래 식은 이번 C3에서 직접 유도했고 [Wolfram 기록](WOLFRAM_DERIVATIVES.json)에서 대수적 동일성을 확인했다. **Rust 구현은 별도의 C5 scalar/complex-step 검사로 검증해야 한다.**

\(A=2y^2+E_d/2+E_\gamma-L\), \(N=W^2+14WV+4V^2\)라 두면 필요한 추가 kernel은

\[
D_{dd}=\frac{-W^3+60W^2V-12WV^2+8V^3}{2R^5},
\]

\[
N_\mu=4\mu[(-e^{2d}+7e^{-4d})W+(-7e^{2d}+4e^{-4d})V],\quad
D_{d\mu}=-\frac{N_\mu}{2R^3}+\frac{3N R_\mu}{2R^4}.
\]

\[
\Pi_{bb}=\sum C_j\alpha D_{dd},\qquad
M_{\Pi,b}=\sum C_j[\alpha_\theta D_d-\alpha B_jD_{dd}+\alpha\mu_\theta D_{d\mu}],\qquad
M_{E,b}=-2M_\Pi.
\]

\(L_z\)의 세 행은

\[
\begin{aligned}
L_{hh}&=-2A S_h/h^3-2\Pi S_b/h^2+4yS_y/h^2+M_E/h^2,\\
L_{hb}&=-2\Pi S_h/h^2+2\Pi_b S_b/h+2M_\Pi/h,\\
L_{hy}&=4yS_h/h^2-4S_y/h;\\
L_{bh}&=2yS_h/h^3-S_y/h^2,\quad L_{bb}=0,\quad L_{by}=-S_h/h^2;\\
L_{yh}&=2\Pi S_h/h^3-\Pi_bS_b/h^2-M_\Pi/h^2,\\
L_{yb}&=-\Pi_bS_h/h^2+\Pi_{bb}S_b/h+M_{\Pi,b}/h,\quad L_{yy}=0.
\end{aligned}
\]

기존 `SmallProblem`은 autonomous API이므로 clock을 state로 넣으면 7차원이 된다. 순서를 \((h,b,y,S_h,S_b,S_y,x)\)로 고정할 경우 마지막 열에는 기존

\[
f_x=((3E_d/2+4E_\gamma)/h,\ 0,\ -4\Pi/h)^T
\]

와 다음 \(G_x\)를 넣는다.

\[
G_x=\begin{pmatrix}
(-3E_d/2-4E_\gamma)S_h/h^2-8\Pi S_b/h+4M_E/h\\
0\\
4\Pi S_h/h^2-4\Pi_bS_b/h-4M_\Pi/h
\end{pmatrix},\qquad x'=1.
\]

고정 segment 안에서 companion을 상수로 두는 미분이다. birth에서 bank를 append하면 새 driver/workspace/cache를 만든다. 대안은 primal 단계의 factorization을 재사용하는 별도 linear tangent 적분이지만, upstream API의 실제 지원을 확인하기 전에는 가능한 구현으로 확정하지 않는다.

### 3.5 계산 비용과 오류 분리

Prepared primal SoA는 기존 \(\mu^2,\alpha\)를 보존한다. 별도 tangent SoA에 \(\alpha_\theta\), \(\alpha B_j\), \(\alpha\mu_\theta\)를 저장하면 같은 \(R,D\) 계산에서 \(M_E,M_\Pi\)를 누적할 수 있다. Full augmented Jacobian이 필요할 때만 \(D_{dd},D_{d\mu}\) 채널을 계산하는 두 경로도 후보이다. 기존 primal 채널의 연산 순서와 괄호·reduction을 유지하며 signed memory 채널은 독립적인 보상 합산을 사용한다.

비용은 ray 수 \(N_r\), parameter 수 \(P\)에 대해 \(O(N_rP)\), companion 저장도 \(O(N_rP)\)다. 첫 단위는 \(P=1\)이다. KL covariance solve는 birth에서만 수행한다. 상태 cache의 exact-bit key \((x,h,b,y)\)와 evaluator의 immutable primal/companion identity를 함께 지킨다. \(G=JS+g\) 자체를 cache하면 \(S\)도 key에 포함해야 하므로, 우선 \(J,g\)만 cache하고 \(JS+g\)를 매번 계산한다.

오차는 네 갈래로 보고한다. (i) cohort/angular discretization은 고정 입력의 물리 근사 오차, (ii) ODE solver·dense interpolation은 history 적분 오차, (iii) KL nonlinear solve와 derivative conditioning은 birth 계산 오차, (iv) cancellation·ordered reduction은 roundoff다. Exact moment 통과는 (ii)의 수렴이나 finite-\(d\) continuum 정확도를 증명하지 않는다. \(y=0\)에서 \(\Sigma\)의 절댓값은 미분 불가능하므로 signed \(y/h\)를 primary로 보고하고 \(\Sigma_\theta\)는 \(y\ne0\)에서만 정의한다.

## 4. 유일한 실패 S8 native case에 S11 P24를 연결하는 조건

실제 실패 입력은 `b9_n64_P2P4`, \(b_0=0.9\), \(n_\mu=64\), energy bins 96, cells/segment 32, cohorts 16, \(\beta=0.2\), observation \(x=1\)이다. \(a=e^x/21\), \(b=0.9+0.2x\), \(H=10^{-16}\,{\rm s}^{-1}\)인 prescribed geometry다. 0-based birth11, \(u=0.5750000000000001\), \(b=1.0150000000000001\)에서 `INNER_P2_PRECISION_LIMIT`가 발생했다. 해당 support의 strict interior와 S11 점별 P24 성공은 이미 고정 증거다.

**중간 bank checkpoint는 실패 raw에 없다.** 실패 row에는 case·reference grid·failed support만 있으며 prefix cohort/bin state는 직렬화되지 않았다. 따라서 birth11 checkpoint-resume라고 쓰지 않는다. 허용 가능한 새 실행은 이 실패한 한 사례를 초기 상태부터 구성하는 **새 수선 시도**이며, 17개 완료 사례를 포함하지 않는다.

최소 변경으로 다음 dispatch를 사전에 고정하는 방안을 권한다.

1. 같은 owner·native transport·source spectra·rates·old32 block·64-ray support를 사용한다.
2. birth0–10은 기존 P24 projector를 호출하고 생성한 weights·native state를 즉시 동결한다.
3. 아직 완료된 값이 없는 birth11–15에만 S11 simultaneous P24를 호출한다. 새 cohort를 만든 뒤 과거 cohort에 접근해 재가중하지 않는다.
4. 새 support/conditioning/projector 실패가 생기면 정확한 index·입력·잔차·status를 남기고 종료한다. 자동 P246 승격, 음수 weights, tolerance 완화, 다른 case로 대체하지 않는다.
5. 새 wrapper는 exact one-row CASES.csv와 새 source/contract를 검증한다. 기존 18행 `run_s8_native_refinement.py`를 전체 호출하지 않는다.

실패 원본 gzip SHA256 `fdc70eaaea45804aa16e60bba495b283eb5e4a18a576f52d5519bfd5a1f05839`와 S11 추출 입력은 read-only baseline이다. old32의 3072 cells, number/energy_ref/support_lo/support_hi 전체 bit identity를 유지하며 기존 digest `79a81384cf24516c9fa93802145a5e864a95da3d2ee6e02187374badc9d155de`와 연결한다. new64 block을 old32에 remesh하거나 기존 물리 anisotropic stock을 등방화하지 않는다.

이 job의 수락은 exact norm/P2/P4 \(3\times10^{-15}\), source·native transfer ledger \(10^{-11}\), discrete R/D 대 native inventory \(3\times10^{-14}\), block sum·per-H continuity \(10^{-11}\), spectral/rate bit identity를 각각 유지한다. Per-H continuity는 \(U_H'+U_H+2b'\Delta P_H=0\)이고 physical density의 \(+4U\) 식과 혼동하지 않는다.

\(|A-A_{\rm continuum}|\le10^{-6}\), \(A=\Delta P_{\rm new}/U_{\rm new}\)는 n64의 **별도 accuracy target**으로 기록한다. 원 native campaign의 finest admission은 n256이었다. P24/native ledger를 통과해도 n64 angular target이 실패할 수 있고 그 실패를 보존해야 한다. 이 한 history의 완료도 evolving reactive spectral convergence나 native Einstein coupling 완료를 뜻하지 않는다.

## 5. 제한된 새 작업 그래프와 NCP 준비

아래는 C1–C3 단계에서 작성한 **미실행 준비 목록**이다. 실제 C4 publication·C5 source가 준비되기 전에는 executable-ready라고 부르지 않는다. 실제 source와 함께 확정되는 기계 판독 기준은 [S12 계약](CONTRACT.json)에 둔다. 아래 matrix 후보를 아직 실행되지 않은 실제 명령 목록으로 오인하지 않는다.

| ID | 새 계산 또는 준비 | 선행 조건 | 현재 상태 |
|---|---|---|---|
| T0 | 새 parameter/state/source/solver 계약과 source freeze | root의 C1 선택·upstream API 확인 | PREPARED_DRAFT |
| T1 | 새 Rust local kernel·KL derivative·full augmented JVP 대 독립 direct/complex-step 검사 | T0, 새 코드 | NOT_RUN |
| T2 | 새 Rust 짧은 fixed-schedule full-memory history, event·constraint 검사 | T1 | NOT_RUN |
| T3 | 새 Rust full tangent 1회 대 저장 S8 관측값 비교 | T2, exact baseline input binding | NOT_RUN |
| T4 | 허용된 fresh short input 1개에서 독립 nonlinear perturbation/Richardson 판별 | T2, 사전 고정 오차·budget | NOT_RUN |
| T5 | 새 larger-memory NCP full histories·paired primal FD·64-case stored-state parallel benchmark | T3/T4 수락, 실제 NCP topology·quota 확인 | DESIGN_ONLY_NOT_RUN |
| N1 | S8 실패 native 한 case의 legacy-prefix/S11-P24 suffix 후속 | 새 one-case wrapper·owner/source binding | DESIGN_ONLY_NOT_RUN |

T3은 새로운 Rust 구현의 아직 없는 full tangent를 계산하는 작업이다. 기존 Python tangent campaign을 다시 돌리지 않는다. T4 역시 기존 S8의 6개 nonlinear perturbation을 재실행하는 목록이 아니며, 새로운 짧은 입력·필요한 perturbation 수를 source 전에 고정한다. 기존 omission controls의 결론은 재사용하고, 새 memory code가 바뀐 위험에 맞는 국소 음성 대조만 T1에 둔다. 모든 출력을 pass/fail로 저장하며 느리거나 부정확한 결과도 결과 집합에서 빼지 않는다.

T5의 제안 후보는 \(b_0\in\{0.3,0.6\}\), \(n\in\{32,64\}\), \(K\in\{128,512\}\)의 8개 **새 Rust full-memory** 사례다. 이는 아직 선택·사전등록된 실행 matrix가 아니다. P24 support와 conditioning은 각 새 birth에서 검사하며 실패하면 그 사례의 실패로 남긴다. solver를 바꾸거나 더 큰 \(n\)으로 자동 확장하지 않는다. 각 사례의 paired primal FD는 같은 새 Rust 물리 입력에서 tangent code를 호출하지 않는 독립 nonlinear solve로 준비하고, epsilon·solver·관측값·cost budget을 source와 함께 고정한다.

Root가 선택한 64-case parallel benchmark는 64 CPU/128 GiB 환경에서 준비하는 새 memory-kernel workload다. 준비안은 위 8개 history 각각에서 사전 고정한 8개 관측 지점의 immutable bank/state pack을 추출해 64개 work item을 만드는 것이다. 성능 반복은 이 stored pack만 평가하며 ODE history를 64회 재생성하지 않는다. 이 구성과 반복 횟수는 실제 source 계약에서 확정해야 한다. full history·FD·kernel benchmark 결과 수를 한 개의 성공 건수로 합치지 않는다.

NCP 요청은 **64 CPU cores / 128 GiB RAM 자원 프로파일**이다. worker128 지점이 아니다. 실제 SMT·NUMA·cgroup CPU/RAM quota·disk·compiler를 읽어 확인한 뒤 node와 case 배치를 고정한다. full-history 첫 배치는 단일 thread case 최대 8개면 충분하다. 64개 ready work item의 동시성은 별도로 실제 CPU quota와 NUMA 배치에 맞춰 정하며 nested BLAS/Rayon/OMP 병렬화는 끈다. 64 core 프로파일 자체를 64 solver worker 의무로 해석하거나 worker128 실험으로 바꾸지 않는다.

Sandbox는 기존 worker≤16, RAM≤16 GiB, task disk≤4 GiB, 개별 job≤1800초 상한과 **관측된 8 CPU/8 GiB cgroup 중 더 작은 실제 한도**를 적용한다. 시작 계획은 science worker1, build worker≤2, 총 작업 메모리≤6 GiB를 목표로 두고 실제 RSS를 기록하는 것이다. NCP에서도 이 단위는 전체 task disk4 GiB 안에 충분히 들어가도록 보관을 설계하며, input/source를 복제하는 case별 checkout을 만들지 않는다. 각 실행에는 1740초 guard와 남은 receipt 저장 시간을 두고 최종 hard limit1800초를 지킨다. timeout 후 결과를 확인하지 않고 자동 재시작하지 않는다.

정량 성능은 같은 물리 입력·공차·출력·오차를 충족한 뒤 보고한다. Small workload regression 가능성을 남기고 old 2.973/4.115를 새 tangent 가속비로 옮겨 쓰지 않는다. 결과 source·raw stdout/stderr·exit·timing·RSS·disk·counter를 create-only receipt에 묶고 단계별 Git publication과 두 provider backup/readback은 root가 실제 성공 범위만 기록한다.

## 6. 프로토콜 적용과 다음 단계의 판단 근거

`project_sources`의 01·04·05·07·08 본문을 모두 읽었으며 실행 script나 대형 archive를 실행·추출하지 않았다. 01의 넓은 low-ell/CMB auditor 목록을 S12 전체 물리 범위로 확대하지 않는다. 04의 실제 code path 우선·kill test 원칙, 05의 DAG 선행 조건·증거 재사용을 현재 세 단계에 적용했다. 07/08의 figure semantics·hostile/residual review는 새 실제 자료가 생기는 이후 단계에 적용한다. 현 단계에서 가짜 실험 plot이나 plot PASS를 만들지 않는다.

| 가설 | 예측되는 판별 신호 | 반증 또는 보류 조건 |
|---|---|---|
| H1 full tangent에는 memory forcing이 필요 | direct chain rule와 split 식 일치; omission에서 새 birth response 차이 | code의 정의가 fixed bank라면 기존 JVP에 오류 판정하지 않음 |
| H2 fused pass가 memory evaluation 비용을 줄임 | 동일 오차에서 ray traversal/allocation 감소 및 measured timing | small 사례가 느리면 회귀 그대로 기록 |
| H3 birth derivative가 event·constraint 일관성을 유지 | norm/P2/P4 derivative와 \(C_\theta\) 전파 잔차가 고정 gate 안 | covariance 경계·domain 실패이면 중단 |
| H4 S11 P24가 원 S8 수치 실패의 후속 경로를 열음 | 한 native case의 birth11 이후 실제 ledger/array 출력 | 점별 성공만으로 전체 history 통과를 주장하지 않음 |

우선순위는 H1/H3의 새 Rust 구현 정확성, 다음은 H2 비용이다. H4는 독립적인 작은 후속으로 병행 준비할 수 있다. P246 full-history 확대와 실제 MD14/shared-Q 결합은 이 단계에서 보류한다. Strong no-go 주장을 새로 만들지 않는다.

## 7. 문헌의 사용 범위

이론 담당자의 C1–C3 source 검토에서는 새 문헌 검색을 수행하지 않았다. 다음은 고정 S8/S11 문서의 **상속 bibliography**이며 원문을 새로 재검토했다고 주장하지 않는다. Root가 scope freeze 뒤 수행한 51개 Wolfram identity 검증은 위 CAS receipt에 별도로 기록했다. SciSpace/Exa의 새 원문 검토도 실제 기록과 구분한다.

- [Lee–Nungesser–Tod, Einstein–Vlasov/Bianchi I](https://arxiv.org/html/1911.04937v2): 고정 S8의 conserved covariant momentum 배경.
- [Geenens–Kojadinovic–Martini, finite φ-projection differentiation](https://arxiv.org/pdf/2407.05997): fixed-equality projection의 기존 implicit-function 근거. 이 문서의 moving-feature 추가항은 위 제약을 직접 미분한 것이다.
- [Wainwright–Jordan, exponential families](https://people.eecs.berkeley.edu/~jordan/sail/readings/wainwright-jordan-fnt.pdf): covariance Hessian에 대한 상속 근거.
- [Fleury–Pitrou–Uzan](https://www2.iap.fr/users/pitrou/publi/1410.8473.pdf): Bianchi I ray map의 상속 문헌.

이 문서가 새로 제공하는 결과는 실행 PASS가 아니라, 실제 fixed-bank JVP와 full parameter tangent를 연결하는 식, 전체 augmented Jacobian에 필요한 채널, 그리고 실패한 native 한 사례만 다루는 구체적인 실행 경계다.
