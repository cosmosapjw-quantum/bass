# FA03-R8 결과 판정: 두 유한 검출기 인증의 채택 범위와 Stokes cone 여유

2026-10-14 KST. 대상은 `physmath-research-loop`의 단일 선택 단계 **R8 (결과 판정)**. 원 FA-02 b453 판본, signature $(-,+,+,+)$, Kasner 지수 $(2/3,2/3,-1/3)$, $x=t/t_o\in[1/2,1]$, source 및 absorber의 normal-frame 정지, zero incoming coherency, observer 고정 $(\chi,\psi)=(1/125,1/100)$, cap radius $1/50$ rad를 보존한다. detector는 **정확한** GL3×uniform-12 azimuth 양의 36-ray 규칙이며, $e=E_w/E_*\in[.98,1.02]$ band는 exact rational moments로 적분된다. $\epsilon$은 **흡수만** 변화시킨다.

## R8 결정

**`PROMOTE_FOR_SPECIFIED_USE`: 위 고정 유한 검출기의 비회색 2차 수치 응답 다항식.** 실제 복원된 PR147 archived 64-step fixed-cubic/whole-cell residual certificate와 PR146 archived 32-step 20차 interval-Taylor enclosure, parent R6 및 두 결과의 exact rational interoperability record를 직접 확인했다. 보존된 원본 각각의 SHA-256은 `551ca3cd2f86…`, `5fbdc60f4d61…`; parent R6은 `c040514105fa…`. 이는 같은 수학적 observable의 서로 다른 수치 근사이지 **같은 bytes 또는 서로 독립적인 원자물리 인증**이 아니다. 세 archive 원본과 입력계약은 바꾸지 않았다.

정규화된 observer coherency $\mathcal J_{36}(\epsilon)$에 대해

$$\widehat P_2(\epsilon)=\widehat S_0+\epsilon\widehat V_0+\frac{\epsilon^2}{2}\widehat W_0,\qquad |\epsilon|\le\frac1{10},$$

$$\|\mathcal J_{36}(\epsilon)-\widehat P_2(\epsilon)\|_1\le \delta_{\rm coef}+C_3|\epsilon|^3,$$

$$ C_3=\frac{926402349807}{1953125000000000},\quad \delta_{\rm coef}<7.361\times10^{-12},\quad \boxed{\delta_{\rm total}<4.75\times10^{-7}}.$$

원 coefficient error의 upper는 `PEER_COMPATIBILITY.json`의 exact fractions를 그대로 사용하여
$E_0+0.1E_1+0.005E_2=7.360273381795437\times 10^{-12}$로 재계산했고, 합계는 $4.743253633745658\times10^{-7}$이었다. `4.75e-7`은 짧은 상향 반올림 표시다. 이 강한 값의 정당화에는 **PR146 certificate가 의존**한다. PR147의 독립 저장 residual bound $<4.84\times10^{-7}$은 원래 결과로 유지한다. 본 R8은 R5–R7 생산을 반복하지 않고 저장 자료 및 정확한 유리수 관계를 재검사했다.

### Stokes invariant와 cone 여유 (이번 판정에서 명시적으로 계산)

$F=\tfrac12\begin{psmallmatrix}I+Q&U-iV\\U+iV&I-Q\end{psmallmatrix}$이며 원 dossier의 $V=-2\operatorname{Im}F_{12}$ convention을 보존한다. $I,Q,U,V$가 실수이면

$$\lambda_\pm(F)=\frac{I\pm\sqrt{Q^2+U^2+V^2}}{2},\qquad \|F\|_1=\max\bigl(|I|,\sqrt{Q^2+U^2+V^2}\bigr).$$

이 결과는 실제 Wolfram 15.0.1에서 Hermiticity·eigenvalues·quadratic trace로 검산했다. PR147의 저장된 정확한 이진 유리수 계수에서
$\widehat I_0>.4958$, $|\widehat Q_0|<.2287$, $|\widehat U_0|<.0658$, $|\widehat V_0|<.0486$이며, 뒤 세 성분 제곱합은 $(.243)^2$보다 작다. 또한 $\|\widehat V_0\|_1<.0091$, $\|\widehat W_0\|_1<.000364$이다. Weyl inequality와 같은 $\delta_{\rm total}$를 사용하면

$$\begin{aligned}
\lambda_{\min}(\mathcal J_{36}(\epsilon))
&\ge \frac{.4958-.243}{2}-.1(.0091)-.005(.000364)-4.75\times10^{-7}\\
&=.125487705>\boxed{.12548}.
\end{aligned}$$

이것은 **해당 observer/36-ray/비회색 매개변수 전체에서 수치적으로 인증된 물리 cone 내부 여유**다. 일반 CMB의 polarization fraction 또는 측정된 광도의 인증으로 바꾸지 않는다. 정확한 finite-detector $\partial_\epsilon I|_0<-.009$ 역시 certificate가 허용하는 고정 observer의 비회색 기울기 주장이다. Source strength가 실험적으로 보정됐다는 뜻이 아니다.

## 의도적으로 HOLD인 주장

- **HOLD**: 정확한 연속 angular cap의 적분 오차. GL3×12 finite detector의 time/roundoff certificate와 별도다. 연속 cap으로 가려면 angular analytic strip/derivative bound 또는 별도 interval quadrature가 필요하다.
- **HOLD**: $\partial_\chi$, $\partial_\psi$를 수치 interval로 둘러싼 joint observer+opacity 전체 모델의 certificate. R6의 exact joint remainder만으로 numeric observer coefficient error를 자동 부여하지 않는다.
- **HOLD**: 유한 $\epsilon\ne0$에서의 finite six-moment closure, self-consistent Einstein–Boltzmann feedback, 실제 원자물리 opacity 정확도, empirical cosmological claims.
- **HOLD**: REI full signed abundance accuracy, positive/negative shear detection, physical milestone error, AX11/AX12 science admission. Source/clock/thermal convergence와 이번 고정 finite-cap photon toy는 서로 다른 claim family다.

즉, 일반적 `FA03 solved everywhere`라는 문장은 **REJECT_OUT_OF_SCOPE**, 고정 검출기에서 위 수치 2차 다항식 사용은 **ADOPT_SCOPED**다. 새 strong no-go 정리는 주장하지 않는다.

## 출처와 방법 구분

Fleury–Pitrou–Uzan, *Phys. Rev. D* **91**, 043511 (2015), [arXiv:1410.8473](https://arxiv.org/abs/1410.8473)는 Bianchi I의 conserved momenta와 null-ray redshift의 원전이다. Gammie–Leung, *ApJ* **752**, 123 (2012), DOI [10.1088/0004-637X/752/2/123](https://doi.org/10.1088/0004-637X/752/2/123)은 covariant polarized coherency transfer의 문헌 근거다. Jawecki–Auzinger–Koch, [arXiv:1809.03369](https://arxiv.org/abs/1809.03369), Estep, *SIAM J. Numer. Anal.* (1995), DOI [10.1137/0732001](https://doi.org/10.1137/0732001), Han, *Applicable Analysis* (2015), DOI [10.1080/00036811.2014.992423](https://doi.org/10.1080/00036811.2014.992423)은 residual/error decomposition의 방법 근거이며 **지정된 수치상계의 원문 출처는 아님**. 수치상계와 Stokes margin은 이 dossier family에 대한 직접 계산·검산 결과다.

## 실제 실행 범위

저장 R7 package의 read-only verifier 두 개가 PASS; R7 cross-compatibility의 exact rational 검사 PASS; 신규 decision/preflight script 8개 tests PASS. Wolfram scalar Hermitian/trace/eigenvalue와 positive floor 정리를 실제 실행했고, 연구 PC의 Wolfram 15.0.0 + xAct/xTensor 1.3.0으로 kinematic signature/shear 및 boost 관련 7개 잔차가 0임을 확인했다. Cas symbolic, immutable archival numeric evidence, light new 1D geometric integration은 서로 다른 검증 층이다. Native subagent와 외부 독립 scientific review는 NOT_RUN. 이번 단계에서 새 36-ray/REI heavy solver를 실행하지 않았다.

**R8 종료 후 다음 단계는 R9 (정식 결과 및 coding 계약 연결)**이며, R9/R10은 아직 실행하지 않는다. R9에서 source-defined equation/claim IDs와 컴퓨팅 입력 계약을 formal dossier에 연결하되 부모 I–VII 원본을 대체하지 않는다.
