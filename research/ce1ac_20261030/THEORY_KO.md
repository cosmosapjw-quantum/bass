# BASS CE1-AC | 원래 양의 six-cell Einstein–Vlasov 연속시간 l=4 rank-3 정리

- 2026-10-30 KST; PR277 원본 HEAD `1ee44436da37a45b6322c3606f0fb43998bed83c` 위 독립 후속 연구.
- 원래 양의 6개 binary64 cell energy (`SOURCE_SHA256=022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035`), 양의 reflection-even angular source, 비열적 massless collisionless photons.
- 대각 Bianchi I, Λ=0, (-,+,+,+), 원래 proper u=t/Tstar∈[0,2/25], a_i(0)=1, 초기 shear s=(0.2,-0.13,-0.07)는 저장 binary64의 정확한 이진유리수로 해석한다. c를 흡수하지 않는다: E=8π G Tstar² ρ_energy/c², P_i=8π G Tstar² p_i/c² (ρ_energy와 p_i는 둘 다 에너지밀도 단위; metric과 시간 정규화에 따른 등가 표현). 여기서는 저장된 무차원 Einstein ODE 우변의 E/P 자체를 계약으로 고정한다.
- 물리 ODE: ell_i'=h_i, h_i'=-theta h_i+P_i(ell), theta=∑_i h_i, h_i(0)=H0+s_i, H0=√[(E0+½∑s_i²)/3]. 관찰 sky는 정지 tetrad의 질량 없는 에너지 밝기, 온도/편광 가정 없음.

## 1. 원래 연속 각도 원천의 유한 모멘트

초기 보존방향 n_i에 대해 Q=∑n_i² e^{-2ell_i}, r=√Q, x_i=n_i² e^{-2ell_i}/Q, U0(n)≥0. 정확한 정규화 각도 조화원천은

- f_40(ell)=∫ U0 r (35x_z²−30x_z+3)dΩ / ∫ U0 r dΩ;
- f_42(ell)=∫ U0 r (x_x−x_y)(7x_z−1)dΩ / ∫ U0 r dΩ;
- f_44(ell)=∫ U0 r (x_x²−6x_xx_y+x_y²)dΩ / ∫ U0 r dΩ.

각 성분에 곱해지는 원래 Y_4m 정규화 상수 4πk_m과 K4 고유벡터의 스케일 [1,√2,√2]/3은 엄격 양수이다. 따라서 rank는 f=(f_40,f_42,f_44)의 rank와 동일하다.

필요한 초기 모멘트 M_abc=∫U0 n_x^{2a}n_y^{2b}n_z^{2c}dΩ는 모든 a+b+c≤4에 대해 직접 계산한다. 원본 μ=[0,½,1], t=2φ/π=[0,¼,¾,1], 2×3 개 셀의 정확한 이진유리수 에너지 가중치를 이용한다. μ 적분은 유리다항식, φ 적분은 유한 코사인 Fourier 전개로 구현하여 M_abc=A_abc+(D_abc+G_abc√2)/π, A,D,G∈Q 를 얻는다. 최종 계산은 저장 ray/GL을 사용하지 않는다.

## 2. 유도: 초기시간 두 차수 jet

B=∑_i x_i h_i, C=∑_i x_i h_i², D=∑_i x_i h_i'. 다음 항등식은 모든 u에서 성립한다.

- r'/r=−B;
- x_i'=2x_i(B−h_i);
- B'=2(B²−C)+D;
- x_i''=4x_i(B−h_i)²+2x_i(B'−h_i');
- r''/r=2C−B²−D.

T_m(x)를 위 다항식이라고 하면, 모멘트의 시간 jet는

M_m=∫U0 rT_m, M_m'=∫U0 r(T_m'−BT_m), M_m''=∫U0 r[T_m''−2BT_m'+(2C−B²−D)T_m].

정규화 M0=∫U0 r에 대해 f_m=M_m/M0를 두면

f_m'=(M_m'−f_m M0')/M0,

f_m''=(M_m''−f_m M0''−2f_m'M0')/M0.

u=0 에서 모든 피적분함수는 n_i²의 최대 4차 다항식이다. 원본 여섯 cell의 정확한 M_abc만 필요하다. 초기 방정식으로 h_i'=-theta h_i+P_i, P_i(0)=M_ei를 대입하면 이는 정확한 continuum Einstein–Vlasov 시간 jet이다.

## 3. 원래 연속 모델에 대한 부호 인증

증명 프로그램 `source/initial_jet_certificate.py`: 모든 유리수와 최초 에너지/shear를 exact Fraction으로 전개하고 정수 10^80 격자에서 매 연산 바깥쪽 방향 반올림한다. π는 Machin arctan 교대급수의 유리 상하계, √2와 H0는 integer-isqrt로 포락한다. division 시 0 포함은 오류로 중단된다. 총 35개 유효한 초기 모멘트가 평가되며 최대 다항식 차수=4이다.

J_f = [f(0);f'(0);f''(0)] ∈R^{3×3}에 대해 프로그램이 얻은 정확한 정수간격의 determinant는

> 0.000013102168598091874127705504570834887032205441594547633466586351670...

엄격 양의 하계를 가진다. 부호는 정수 반올림 규칙과 유리수 경계만으로 재현된다. 4πk_m 및 [1,√2,√2]/3의 **양의** 열 스케일을 복원한 physical X의 초기 jet determinant는 약 3.016039594736×10^-5 (이 값 자체는 별도 엄격 하계가 아니라 수치 설명)이다.

## 4. 정리와 증명 범위

**정리 (조건부 계산지원 인증)**. 위 정확한 원본 six-cell 연속 각도 원천, 무차원 Einstein–Vlasov IVP와 interval 구현이 의도한 수학을 계산한다는 전제 아래, 정규화된 real even l=4 세 시간성분 X40(u),X42(u),X44(u)는 초기 u=0의 모든 우측 열린 근방에서 선형 독립이다. 따라서 임의의 u=0 주변에 양의 밀도를 갖는 시간측도 w(u)du 에 대해 K4(u,v)=X(u)·X(v)는 rank 정확히 3인 연속시간 유한랭크 kernel이며 이에 대응하는 적분연산자 역시 rank 3이다.

증명: 만약 상수 c≠0에 대해 ∑c_m X_m(u)=0이 어떤 우측 시간구간 전체에서 성립한다면, u=0에서 연속성·우측 두 번 미분을 사용하여 J_X(0)c=0을 얻는다. 그러나 det J_X(0) ≠0 이므로 c=0이어야 한다. 양의 w에 대해 ∫w(u)(c·X(u))²du=0 이면 연속성에 따라 c·X=0 on support, 모순이다. Rank는 X의 세 성분 수를 넘을 수 없으므로 정확히 3.

**금지된 승격**: 이전 41개 u_j에서의 3×3 sampled Gram λ3의 엄격 양적 하계는 이 논리만으로 추론되지 않는다. GL6/GL8 수치 λ3≈5.7133e-11은 독립 실험 진단이며 본 정리의 조건이 아니다. 연속시간 연산자의 최소 비영 고유값에 관한 정량 하계도 제출하지 않는다. Genuine distinct-author R6/C9, 전프로그램 formal verification, 비FLRW 확장, 물리 CMB 파워/temperature, polarization, ensemble likelihood 모두 NOT_RUN/NOT_CLAIMED.

## 5. 보조 물리 진화 검산

원래 저장된 41×2 DOP853 geometry를 고정해 새 82개 X,X',X'' 실수치와 3,362개 K4(u,v), ∂uK4,∂vK4,∂u∂vK4를 생성했다. 단위 스칼라는 fractional normalized energy-sky convention이며 기존 unnormalized energy multipole power와 구분한다. E와 α=4πa/E 관계 때문에

C4^U = (E/(4π))² C4^α,

(C4^U)'=(E/(4π))²[(C4^α)'+2(E'/E)C4^α].

두 정의 사이의 원래 데이터 직접 검산은 최대 수 e-18 절대 차이. 모델에서 u=0.08, GL6: (C4^α)'=+4.706450136049044e-3, (C4^U)'=−1.4789130142318007e-4. 팽창희석과 패턴 anisotropization을 분리한 새 물리적 진화 데이터이다. 시간 구간의 exact continuum source와 sample geometry 오차포락을 K4'에 이전하는 인증은 하지 않는다.

## 6. 원전·기존 프로젝트 근거

1. Heinzle, J. Mark & Uggla, Claes, *Dynamics of the spatially homogeneous Bianchi type I Einstein–Vlasov equations*, Classical and Quantum Gravity **23** (2006) 3463–3489. DOI 10.1088/0264-9381/23/10/016; arXiv:gr-qc/0512031. 대각 Bianchi-I Vlasov 동역학 배경. 위 특수 six-cell 수치는 본 프로젝트 고유.
2. Barzegar, Hamed; Fajman, David; Heißel, Gernot, *Isotropization of slowly expanding spacetimes*, Physical Review D **101** (2020) 044046; DOI 10.1103/PhysRevD.101.044046; arXiv:1904.13290. 질량 없는 Bianchi-I EV의 정성적 점근 동역학 배경.
3. DLMF §3.1(ii)/(iii) https://dlmf.nist.gov/3.1 : interval 및 exact rational 연산 원리.
4. 프로젝트 exact predecessor PR264/270/275/277와 HEAD `1ee44436...`, frozen original six-cell source SHA 및 CE1-AB complete ZIP. 원전의 정리와 *이 연구에서 직접 유도한 초기 jet rank 정리*를 혼동하지 않는다.

UPPER_DAG=9/15, CE1=PARTIAL, scoped R/C=18/20, third sampled Gram λ3=UNRESOLVED, no auto merge/production.
