# BASS CE1-E: 양의 비다항식 angular radiation의 인증된 구적오차와 Einstein–Vlasov 전달

**상태:** `COMPLETE_SCOPED_NONPOLYNOMIAL_SOURCE_QUADRATURE_AND_COUPLED_TRANSFER` (하위 노드). 상위 CE-1 `PARTIAL`, 상위 DAG **9/15**. 부모 PR #236, Git commit `24a5d8f76ce134c57fb691ff90e382425d5bb7cd`. 원본 부모 ZIP `BASS_CE1D_FINAL_20261029.zip` SHA256 `7f2d3f06677bc9c6354401a0761b92b8a3ffccfda96ad9f13b8c760e1c73b670`. 원본과 owner/main의 과학 코드, 허용오차는 변경하지 않았다.

## 1. 모델·물리적 범위

서명 `(-,+,+,+)`, normal proper time `u=t/T_*`, `\ell_i=\log a_i`, `h_i=T_*H_i`, 무차원 에너지와 압력은 `8πGT_*²/c²`를 물리 에너지밀도·압력에 곱한다. Λ=0, 대각·반사대칭, 모든 초기 방향별 팽창이 비음수인 **무질량·무충돌 Bianchi-I Einstein–Vlasov** 문제다. 경계는 공간적으로 균질, 초기 3-방향 운동량 반사대칭이며, 공간적 평균/tilt/산란/주파수변환을 새로 구현하지 않는다.

초기 covariant-momentum angular energy density를 다음의 **전체 함수**로 둔다.

\[
F_0(\mathbf q)=\frac{E_*}{4\pi}G(\mathbf q)\exp(\lambda q_z^2),\quad
G=1+c_2P_2(q_z)+c_t(q_x^2-q_y^2)+c_4P_4(q_z)>0,\quad \lambda\ge0.
\]

`E_*`는 *진폭*이며 실제 초기 에너지와 다르다. **물리적 source는 지수함수를 절단하지 않으며**, 증명에서만 두 유한 다항식 근사를 사용한다. 입력 기준은 저장된 `binary64` `E_*=0.9`, `c=(0.6,0.25,0.2)`, `lambda=0.2`; 이번 구현의 지원 영역은 `0≤lambda≤1`이다. 정확한 유리수로 G의 전체 구면 양성을 확인한다.

\[
b_i=e^{-2\ell_i},\quad r(\mathbf q,\ell)=\sqrt{\sum_i b_iq_i^2},\quad V=e^{\sum\ell_i},\quad
P_i(\ell)=\frac{1}{V}\int_{S^2}F_0(\mathbf q)\frac{b_iq_i^2}{r}\,d\Omega.
\]

이 압력을 `\ell_i'=h_i`, `h_i'=-\theta h_i+P_i`, `\theta=\sum h_i`와 연결한다. 초기 Hamiltonian constraint는 해당 모델의 **실제 초기 에너지**로 정한다. 진화 중 constraint projection, raw-weight renormalization, fluctuation clipping, 유한 multipole closure는 하지 않는다.

## 2. 새로운 연속각도 구적오차 보증의 유도

생성기의 실제 저장된 `binary64` 광선 `q_j`와 질량 `m_j`를 정확한 이진 유리수로 해석하여, 이들이 정의한 `P_{i,Q}`와 연속 `P_i`를 비교한다. 단위광선인 연속구면과 달리 저장된 `q_j`의 노름은 엄밀하게 1이 아닐 수 있고, `m_j`에는 GL/방위각 node·weight 및 density 평가의 반올림이 들어 있다. 이것을 버리지 않는다.

지수함수를 `T_N(t)=\sum_{n=0}^Nt^n/n!`로 전개할 때 연속구면에서

\[
|e^{\lambda q_z^2}-T_N(\lambda q_z^2)|\le e^\lambda\frac{\lambda^{N+1}}{(N+1)!}.
\]

기하학 부분은 `m=(b_min+b_max)/2`, `z=1-r²/m`에서

\[
\frac1r=\frac1{\sqrt m}\left[\sum_{k=0}^K c_k z^k+R_K(z)\right],\qquad
c_k=\binom{2k}{k}4^{-k},\quad
|R_K|\le c_{K+1}\frac{\rho^{K+1}}{1-\rho}.
\]

여기서 `ρ`는 연속구면과 실제 저장 광선 **양쪽에서** `|z|≤ρ<1`을 만족하도록 각 `\ell` box에 대해 MPFR 외향 반올림으로 계산한다. 두 근사의 다항식 부분은 아래 정확한 구면 monomial 적분과 실제 저장 질량의 정확한 유리수 합을 각각 구해 뺀다.

\[
\left\langle q_x^{2a}q_y^{2b}q_z^{2c}\right\rangle
=\frac{(2a-1)!!(2b-1)!!(2c-1)!!}{(2a+2b+2c+1)!!}.
\]

이렇게 구성한 `Δ_{i,abc}`에 대한 삼각부등식, binomial remainder의 연속/이산 합, 연속 exponential remainder, 저장된 `m_j^{new}-m_j^{base}T_N(\lambda q_{z,j}^2)`의 **정확한 유리수 차이**를 모두 더한다. 양의 G와 T_N가 필요한 부분의 부호를 보장하며, MPFR192 RNDD/RNDU가 수치 상계를 바깥쪽에서 제한한다. 지수함수를 물리적으로 Taylor 절단한 결과로 계산하는 것은 아니다.

Polynomial mismatch는 `K`를 늘리면 오히려 커질 수 있다. `K=0..K_max`의 각 독립적 유효 상계를 계산해 최소값을 취하는 것은 진정한 상계의 최소값이므로 엄밀성에 영향을 주지 않는다. 원래 반올림된 `q_j`를 이상적 GL root로 간주하지 않는다. NIST DLMF §3.5는 정확한 Gauss 다항식 원리를 제공하지만, 이번 증명은 그것을 floating GL 계산의 무오류 가정으로 사용하지 않았다.

## 3. 초기 Hamiltonian 데이터와 기하학 오차 전파

실제 `E(0)=\int F_0dΩ`는 E_*와 다르다. 유한 exponential Taylor와 정확한 유리수 angular moment로 연속 E를 제한하고, 저장된 `m_j^{new}`의 노름·실수합·마지막 float64 합의 차이를 포함했다. 기준에서

\[
E(0)\in[0.979584395997861,\;0.9795843960048798],\qquad
|E(0)-E_Q(0)|\le3.5093057875294107\times10^{-12}.
\]

정확한 초기 tracefree shear는 **저장된 sx,sy binary values와 정확한 `sz=-(sx+sy)`**로 구성한다. 이 정확한 constraint root와 실제 float64 초기 h 사이의 차이도 MPFR로 감싼다.

양의 전 방향 팽창 영역에서 `E'=-\sum_i h_i(E+P_i)≤0`, `h_i'≤E(0)`이므로, 초기 h의 상한으로 **실제 두 해의 `\ell`을 모두 포함하는 닫힌 box**를 계산한다. 일반 양의 radiation에서 `\sum_j|\partial_{\ell_j}P_i|=4P_i≤4E_max`가 성립하므로 두 해의 차이는

\[
D^+x\le y,\qquad D^+y\le4E_{max}x+\eta_Q,\qquad
x(0)=0,\quad y(0)\le \delta h_0
\]

를 따른다. 기존 CE1-C의 MPFR 양의 비교계로 전달하되, 이번 결과는 **연속 Einstein–Vlasov ODE와 저장된 이산 각도 source가 정의한 정확한 실수 ODE**의 차이 상계다. SciPy DOP853의 시간적분 반올림·절단오차를 이번 상계에 끼워 넣지 않았으며 CE1-C의 개별 scalar path bound와 구분한다.

## 4. 실제 계산 (2026-10-29)

`ntheta=8,nphi=16`, `lambda=0.2`, `N=8`, 최대 `K=5`에 대해 geometry box `[0,U]^3`의 source 상계는 다음과 같다 (all dimensionless).

| U | source pressure `max_i` upper | 선택된 K |
|---:|---:|---:|
| 0.02 | 1.3995660624657458e-6 | 3 |
| 0.04 | 2.0843059715742335e-6 | 3 |
| 0.06 | 4.8341244065557746e-6 | 3 |
| 0.08 | 1.2314632530986521e-5 | 3 |

**실제 연계된 `0≤u≤0.08` pilot**는 `\ell` 상한 `(0.06556419,0.03916419,0.04396419)`와 더 좁은 박스를 사용하므로 `η_Q≤6.295927096810174e-6`, `δh0≤1.0078992636191925e-12`이고

\[
\boxed{\max_i|h_i^{continuum}(u)-h_i^{stored-Q}(u)|\le5.057829658977816\times10^{-7}}
\]

를 얻었다. 이 값은 **source 이산화와 초기자료 불일치**의 상계지, 독립 수치적분기의 모든 오류를 합친 수치는 아니다.

반증 검사에서는 새로운 비선형 Einstein–Vlasov IVP **3개** (`8×16,24×48,64×128`), 출력 9시각, SciPy DOP853으로 계산했다. `8×16`과 `64×128` 경로의 측정된 팽창률 차이 최대치는 `4.0308312243553246e-12`, `\ell` 차이는 `1.9278328933225453e-13`, 세 이력의 Hamiltonian constraint residual 최대는 약 `2.76e-13`이었다. 이 값은 상계의 증명이 아니라 반증 검사다.

별도의 mpmath 80자리 적분에서 `ct=0`, `ell=(.025,.025,.055)`인 정확한 축대칭 pressure와 저장된 `8×16` source의 최대 차이는 `1.6016581054e-10`으로 source 상계 내부였다. 동일 입력에서 Legendre 계수 `ℓ=6:0.01490962396`, `ℓ=8:0.0004132253352`, `ℓ=10:7.53974709e-6`이 **실제 비다항식 초기장의 고차 angular 정보**를 확인했다. `ct=0.25`의 일반 입력에도 독립 고해상도 수치 source 검사를 사용했다.

추가 스트레스 검사에서 `λ=0.6,0.8,1.0`, 더 낮은 angular grids 및 임의의 공간형상 값 36건의 pressure gap이 해당 uniform 상계 내부임을 확인했고, 미분항등식 `∂_{ell_j}E=-E-P_j`를 유한차분으로 검사했다. 독립 계산은 같은 물리 입력/수치라이브러리의 일부를 공유하므로 전체 독립 모델 심사가 아니다.

## 5. 구현·실행·허용 범위

실제 새 모듈: `bianchi/nonperturbative/einstein_exponential_source.py`. 공개 주요 함수는 `ExponentialRadiation`, `certified_nonpolynomial_pressure`, `certified_initial_energy`, `certified_coupled_geometry`. `backend='python_oracle'`를 명시한다. 기존 CE1-B/C/D의 module은 바이트를 변경하지 않았다.

현재 턴의 targeted 신규 테스트 **7 PASS**, 부모 CE1-B/C/D **32 PASS**, 합계 **39 PASS**. 의도한 실패는 초기 NotImplementedError(5건)와 exact-shear 부재(1건), 모두 로그 보존 후 해결했다. 별도 GitHub scoped CI와 installed-wheel 검사는 결과 영수증에 따로 기록한다. 원본 부모 과학 캠페인을 재실행하지 않았다.

**제외/미검증:** (a) 임의 양의 비다항식 또는 측정 angular map, (b) 긴 시간·큰 geometry box에서의 경제적인 sharp certificate, (c) floating RK/DOP853 자체의 full-path interval proof, (d) 사용자 십진 입력 취득 불확실성, (e) 일반 Bianchi/공간 Einstein feedback, (f) thermal/recoil/Thomson full-frequency, (g) native Rust, (h) 독립 형식검증된 MPFR/Python, (i) BF-4나 생산 시스템 merge. 이번 제한에서 `production_ready=false`, `merge_ready=false`다.

## 6. 판정 및 다음 연결

**CE1-E = COMPLETE_SCOPED_NONPOLYNOMIAL_SOURCE_AND_COUPLED_ERROR_TRANSFER.** CE-1 상위 claim은 여전히 부분 완료, 9/15 유지. 다음 후보 CE1-F는 (1) 실제 관측 angular table을 positive spectral envelope로 검증하는 경로 또는 (2) independent interval-software assurance 중 한 개로 제한하고 별도 요청 시만 실행한다. 본 단위에서 선택하지 않았으며 main/owner/부모 branch를 병합·변경하지 않았다.

참고 문헌: NIST DLMF §3.5(v) (Gauss quadrature의 다항식 정확성), *Dynamics of the spatially homogeneous Bianchi type I solutions of the Einstein–Vlasov system* (massless, reflection-symmetric Bianchi-I kinetic theory). 두 문헌은 이 코드의 finite-amplitude 수치 검산을 대신하지 않는다.
