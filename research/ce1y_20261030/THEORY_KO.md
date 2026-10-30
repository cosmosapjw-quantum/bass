# BASS CE1-Y | 실제 네 패널/여덟 패널/열여섯 패널 Bianchi-I 하늘의 두 시점 관측량

**2026-10-30 KST | frozen original 6-cell physical source | parent PR #270**

## 물리적 범위

메트릭 `ds²=-c² dt²+Σ a_i²(dx^i)²` 의 `(-,+,+,+)` convention; 양의 질량 없는 무충돌 반사짝수 각도 분포, 팽창하는 대각 Bianchi-I, Λ=0. 초기 여섯 angular cells 및 shear (.2,-.13,-.07)는 변경되지 않았다. 물리 시간은 u=t/Tstar, [0,.08] 및 41개 동일 표본이다.

원래 정확한 binary64 물리 입력 SHA256 `022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035`. GL6은 양의 ray 216개, GL8은 384개. 원본 Git BASS Rust comoving Frame `a29b12b5e7b0d529bddaf9eac53cfdb984ddaa84`. 원본 native Rust/MPFR192 PR #270 CI #40991211526의 여섯 저장 결과를 동결된 입력으로 사용한다. 형식적 프로그램 전체 검증은 아니다.

## 관측량과 정확한 관계

법선 공이동 관측자 tetrad에서 에너지적분 sky의 보존운동량 qhat에 대한 진화와 원점 반사짝수 성질은 이미 CE1-Q–X에서 유도되었다. 실수 공간 하늘의 complex Condon–Shortley 계수 `a_{4m}(u)`를 사용한다. 에너지 E(u)>0인 원래 무충돌 sky의 정규화 계수는 다음과 같다.

\[
\alpha_{4m}(u)=\frac{4\pi}{E(u)}a_{4m}(u),\qquad
K_4^\delta(u,v)=\frac19\sum_{m=-4}^{4}\alpha_{4m}(u)\alpha_{4m}^{*}(v).
\]

반사짝수 분포는 m=0,±2,±4만 남기므로 실수 모델에서는 `(α40(u)α40(v)+2α42(u)α42(v)+2α44(u)α44(v))/9`가 된다. 동시에 원래 원자측도 sky의 복소 조화계수를 직접 계산한 별도 식을 독립적으로 사용해 동일성을 검산한다. `r4=K4δ/√(C4δ(u)C4δ(v))`, `D4²=C4δ(u)+C4δ(v)-2K4δ(u,v)`로 패턴 유사도 및 방향 구조의 거리를 측정한다.

정확한 시간 미분은

\[
\partial_u K_4^\delta(u,v)=\frac19\sum_m
  \left[\frac{4\pi}{E(u)}\left(a'_{4m}(u)-\frac{E'(u)}{E(u)}a_{4m}(u)\right)\right]
\alpha_{4m}^{*}(v),
\]

와 같은 식이다. 각 시점에 대해 원래 BASS Rust Liouville 장과 같은 `u=t/Tstar` 시계를 사용한다. 이들은 **결정론적 두-시점 angular-energy functionals**이다. 확률 앙상블 공분산, 열적 CMB 온도 스펙트럼, 실제 두 과거광원뿔 관측은 아니다.

## 경계, 재생성과 주장의 범위

PR #270의 기존 증명은 원래 **연속 여섯 cell source ↔ 실제 저장 binary64 GL6/GL8 source** 의 \(\ell=4\) 해석적 error와, 별도 source/MPFR192 RK4/Hermite geometry carrier를 구분한다. 인증식은 수학적으로 원래 연속 정확해 K4와 해당 저장된 RK4/Hermite 경로 위의 정확한 원자측도 K4 사이의 차이에 대한 **조건부 상계**다. 4/8/16 패널에서 GL6 `5.1286e-5 / 6.4337e-6 / 9.2063e-7`, GL8 `5.1151e-5 / 6.2985e-6 / 7.8545e-7`가 각 시대쌍 전체의 균일 수학적 반경이다.

이번 연구가 추가한 것은 **실제 BASS Rust의 저장 수치 41×41 물리 K4 중심과 DOP853 저장 41×41 하늘 간의 경험적 비교**다. Rust 수치 sky의 부동소수점 평가 오차 자체가 완전한 MPFR192 interval로 감싸지지 않았고, DOP853 오차를 엄밀히 인증하지 않았다. 따라서 `조건부 수학적 반경`을 Rust/DOP853 수치에 자동으로 더한 값을 rigorously certified interval이라 부르면 안 된다.

## 연결된 기존 연구 및 원전

- Frozen source & DOP853 coupled physical input: PR #264, original 82 records, scoped independently validated.
- Actual conditional source/geometry l4 theory and matched 4/8/16-panel MPFR192 path: PR #270, CI #40991211526.
- Cross-epoch pattern geometry response: PR #269, read-only sibling.
- Lee, Nungesser & Tod, *On the future of solutions to the massless Einstein–Vlasov system in a Bianchi I cosmology*, GRG (2020), DOI 10.1007/s10714-020-02699-7; asymptotics, not a finite-time certificate for this fixed source.
- Fleury, Pitrou & Uzan, *Light propagation in a homogeneous and anisotropic universe*, PRD 91 043511 (2015), DOI 10.1103/PhysRevD.91.043511; null directions and anisotropic propagation, not our source proof.
- Jandrlić et al., *Error bounds for Gaussian quadrature formulae with Legendre weight function for analytic integrands*, ETNA 55 (2022), DOI 10.1553/etna_vol55s424; general quadrature theory; actual bounds originate from the PR270 exact source construction.