# S9: 실제 VigilODE 연결을 위한 구간 미분과 출생 시점

S8의 전체 parameter tangent를 재사용하고, 이번에는 실제 Rust ODE solver가 호출할 구간 내부 Jacobian–vector product와 명시적 시간 편미분을 구분한다. 새로운 parameter tangent나 새 angular moment constraint를 도입하는 단계는 아니다. 연구 전 관련 GitHub·cloud intake는 `evidence_s9/intake/PUBLIC_RELATED_INTAKE.json`, 실제 VigilODE API/benchmark intake는 `evidence_s9/vigilode_intake/INTAKE.json`에 있다.

## 1. Solver 안에서 고정하는 것

한 birth와 다음 birth 사이에서는 cohort의 u, b_u, mu_i, alpha_i, 주입 amplitude L_u가 고정된다. 현재 상태 z=(h,b,y)는 h=H/H*, y=s/H*이며 독립 Raychaudhuri, geometry, signed shear를 진화시킨다. 같은 물리 계약 (-,+,+,+), a_perp=a exp(-b), a_parallel=a exp(2b)를 유지한다.

\[
F(z,x)=\begin{pmatrix}
(-h^2-2y^2-\mathcal E_d/2-\mathcal E+\Lambda_*)/h\\
y/h\\
-3y+\Pi/h
\end{pmatrix}.
\]

이 구간에서 \(\mathcal E_b=-2\Pi\), \(Q=\Pi_b\), \(\mathcal E_x=-4\mathcal E\), \(\Pi_x=-4\Pi\), \((\mathcal E_d)_x=-3\mathcal E_d\)다. 아래 x 편미분에서는 z와 bank를 고정한다. 실제 궤도의 total derivative와 다르다.

\[
J=\frac{\partial F}{\partial(h,b,y)}=
\begin{pmatrix}
-2-F^{(h)}/h&2\Pi/h&-4y/h\\
-y/h^2&0&1/h\\
-\Pi/h^2&Q/h&-3
\end{pmatrix},\qquad
F_x=\begin{pmatrix}(3\mathcal E_d/2+4\mathcal E)/h\\0\\-4\Pi/h\end{pmatrix}.
\]

Wolfram에서 J의 9항, F_x의 3항, autonomous 확장의 16항과 C'=−2C를 symbolic residual 0으로 확인했다. 초기 JSON 출력은 symbolic Times를 직렬화하지 못했으므로 symbolic jump를 InputForm string으로 출력하는 방식만 고쳤고 그 원래 실패도 보존했다. 과학 적분이나 admission gate 변경은 없었다.

## 2. 출생 뒤 cache를 갱신해야 하는 이유

한 birth에서 donor 에너지 w>0을 radiation으로 옮기고, 새 locally isotropic rule을 현재 계산한 b(u)에서 구성한다. 정확히 정규화된 이상적 rule에서 h,b,y는 연속이고 M2=0이면 Pi도 연속이지만

\[
\Delta F^{(h)}=-\frac{w}{2h},\qquad
\Delta(F_x)^{(h)}=\frac{5w}{2h}.
\]

또한 M2=M4=0이면 \(D_d(0)\)의 quadrature 평균이 −8/5여서

\[
\Delta J_{yb}=-\frac{8w}{5h}.
\]

상태 연속성과 새 source의 Pi=0은 RHS, 시간 편미분, Jacobian cache의 유효성을 보장하지 않는다. 실제 구현은 birth endpoint에 도달한 뒤 양의 rule과 exact moment certificate를 검사하고, 이전 cohort bytes를 보존한 새 immutable bank 및 새 upstream driver/workspace를 구성한다. Binary64 rule의 norm이 정확한 1과 미세하게 다른 경우의 일반식과 실제 대조군은 [독립 검토](S9_THEORY_PACKAGE_REVIEW_KO.md)에 있다.

## 3. 실제 upstream API와 비교 범위

Pinned VigilODE implementation은 a21d573980f66fe02891bd216153443b5352f921다. 최신 benchmark publication ac1cd2a4738c2441c92e5fdae5f70aba35e53544(PR71)의 Rust source와 같음을 비교했다. Primary는 `integrate_rodas5p_mf_fast_observed_gmres_into_ls_workspace`에 analytic JVP와 explicit partial_t를 제공한다. API에 partial_t를 주지 않을 때의 내부 차분 fallback을 사용하지 않는다.

두 번째 arm의 실제 `SmallProblem<4>` API는 autonomous다. 따라서 state=(h,b,y,x), x'=1로 구성하고 Jacobian의 마지막 column에 F_x를 넣는다. 두 arm 모두 정확한 OutputSchedule stops를 사용한다. Dense interpolation accuracy와 portable speedup은 이 비교의 승인 대상이 아니다.

Rodas5P의 원 논문 G. Steinebach, BIT Numerical Mathematics 63, 27 (2023), DOI [10.1007/s10543-023-00967-x](https://link.springer.com/article/10.1007/s10543-023-00967-x)의 식 (1.2)–(1.3)은 nonautonomous ROW stage에 f_t 항을 명시한다. 이 문헌은 solver 인터페이스 설계를 뒷받침하며, 수정된 특정 VigilODE 코드와 BASS 문제의 보편적 정확도 증명이 아니다. Birth cache jump는 위 BASS 모형에서 직접 유도한 결과다.

## 4. Rust 패키지를 실제 적용한 역할

- `num-dual=0.15.1`, default-features=false: 생산 JVP helper를 호출하지 않는 독립 directional AD oracle. 실제 adapter의 190 query, 5 banks, 38 bank/state point와 비교했다. 최대 JVP scaled error 4.2848454e-16, F_x 8.5225626e-17. F_x 생략 3개와 stale birth F_x 대조 1개를 모두 거부했다.
- `num-rational=0.4.2`와 `num-bigint=0.4.6`: 저장된 binary64 mu와 alpha를 exact dyadic rational로 변환하고, 정규화와 P2/P4의 unnormalized polynomial sum을 정확한 3/10^15와 비교한 뒤에만 새 cohort를 삽입한다. 기존 P24 알고리즘과 final gate를 바꾸지 않았다. Python Fraction observer가 원시 배열을 독립 검산한다.
- `faer=0.24.4`: 실제 VigilODE의 선형대수 의존성을 유지했다. 이 패키지의 일반적 성능 설명을 3상태 BASS의 성능 우위로 바꾸지 않는다. 작은 고정 차원 direct arm은 별도 비교한다.

9개 AD 단위검산과 실제 callback 비교는 구간 내부 derivative의 구현 검증이다. S8의 전체 초기조건 tangent에 들어가는 birth-memory 변화는 다른 미분 대상이며, 이번 JVP PASS로 대체하지 않는다. 고정 spectral owner0e258464와 기존 photon stock을 유지한다. Native finite-bin 보존, continuum angular accuracy, 실제 MD14 에너지 공급 closure, production/full EoR는 별도 의무다.

## 5. 사전등록 후 실행할 유한 비교

기존 S8 primal 153개 출력 행을 reference로 재사용한다. 미래의 reference b(u)는 solver input에 넣지 않는다. 같은 K32/n16/P24 이력에서 두 실제 driver와 세 ODE tolerance를 비교하고, 각 driver의 analytic FLRW control 한 개를 더해 총8개 history를 등록한다. Source/prereg를 push하고 두 cloud readback을 마친 뒤 실행한다. 이 문서 시점에는 history가 아직 실행되지 않았다. 결과는 실제 raw receipt에서 별도로 판정한다.
