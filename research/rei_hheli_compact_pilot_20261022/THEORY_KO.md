# 33상태 H–Li 결합계의 유도와 z=20→2 preliminary 계약

## R1–R3. 이번에 계산하는 대상

이번 연구는 REC119의 실제 21상태 원자망과 BASS 계열 LRS 기하·운동량
방정식을 연결한 유한 모형을, 샌드박스에서 끝까지 적분하는 문제다.
기존 warm729의 a=0.1999→0.2 결과는 그대로 보존한다. 새 초기시점은
a_ref=1/21이며 마지막은 a=1/3, 독립변수는 x=ln(a/a_ref)∈[0,ln7]이다.
두 실행의 광원·기체 초기조건·정규화와 구간은 각각의 계약으로 추적한다.

현재 source는 rec_bianchi `a949529872eb5ba0e20c7e206fe893e5d544e48c`다.
HE32 `e8bb035d31f59e34734947b9082bdbd60128b799`의 짝수 부분공간 유도를
재사용하고, 같은 원소의 동위원소 전하분율이 이루는 불변부분공간을 추가한다.
외부 자료와 최신 실행 조사 범위는 `intake/`에, 고정 수용 기준은
`FROZEN_CONTRACT.md`에 있다.

## R4–R5. 기하, 응력, 독립 초기값

서명 (-,+,+,+), 정규직교 공간 frame에서

    a_perp=a exp(-b), a_parallel=a exp(2b), s=db/dt,
    sigma_ab=diag(-s,-s,2s), pi_A,ab=diag(-p_A,-p_A,2p_A).

따라서 sigma_ab sigma^ab=6s², pi_A,ab pi_A^ab=6p_A²,
sigma_ab pi_A^ab=6sp_A다. 코드의 p_A=(P_parallel-P_perp)/3이며,
과거 D_A 표기와 D_A=3p_A로 연결된다.

시간 H=(da/dt)/a를 s^-1, rho와 p를 J m^-3로 쓸 때
kappa_t=8πG/c²다. 기하학적 H_g=H/c를 쓸 경우에는
kappa_g=8πG/c⁴와 함께 써야 같은 무차원 결과를 얻는다.

    S_F=√6 s/H,  P_A,F=√6 kappa_t p_A/H²,
    Sigma_F=|S_F|, Pi_A,F=|P_A,F|,
    Pi_total,F=|P_m,F+P_r,F|.

기존 half-contraction convention은 S_h=S_F/√2, P_A,h=P_A,F/√2다.
두 convention을 결과 파일에 함께 저장한다. 초기 matter/radiation 좌표는
서로 독립이며, 처음부터 norm을 더하지 않고 signed 성분을 합한다.

유지하는 Einstein 식은

    H²=(kappa_t/3) rho_total+s²,
    ds/dt+3Hs=kappa_t(p_m+p_gamma+p_nu),
    db/dx=s/H.

질량 있는 collisionless 성분에는 준비된 24×12 canonical cell,
cell당 Gauss3, 총 2592개의 양의 운동량 packet을 사용한다.
이는 기존 유한 quadrature의 계산 순서를 재사용한 것이다. m/T_ref=30,
matter fraction=0.1이며 바리온 예산과 중복되지 않는 비바리온 성분이다.
양의 초기 분포 f∝1+A P2를 요구하고 source의 허용 A 범위 안에서
지정한 초기 P_m,F와 P_r,F를 역변환한다.

각 packet에서 q_perp² exp(-2x+2b), q_parallel² exp(-2x-4b)를 물리적
운동량 제곱으로 변환한다. E=sqrt(m²+q_phys²)와 고정 양의 weight를
합산하여 rho_m, P_perp,m, P_parallel,m을 계산한다. 이 표현은
∂rho_m/∂b=-6p_m을 만족한다. photon/neutrino의 energy·number 다중극은
각각 L=8까지 유지한다. 전자밀도에 의한 Thomson 항은 photon에만 넣는다.

정규화된 shear의 식은 다음과 같이 바로 얻어진다.

    dS_F/dx = -(3+d ln H/dx) S_F + P_m,F+P_r,F.

S_F(0)=0이고 P_m,F(0)+P_r,F(0)=0이면 초기 1차 기울기는 0이다.
그 이후의 응력은 각 성분의 진화식으로 결정된다. 초기 b=0의 분리 가능한
P2 massive 분포에서 J2≠0일 때 beta_m=J4/J2라 두면 0≤beta_m≤1이고,
zero-shear 순간에는 p_m'=(beta_m-5)p_m이다. radiation은
p_r'=-4p_r-(9/10)(Gamma_T/H)p_gamma다. 그러므로 정확한 초기 상쇄점에서

    S_F''(0)=(beta_m-1)P_m,F(0)
              -(9/10)(Gamma_T/H)_0 P_gamma,F(0).

공통 H 정규화의 미분항은 P_m+P_r=0 때문에 사라진다. 이 식은 massive
성분의 다른 redshift와 photon 산란이 상쇄를 어떻게 해제하는지 구별한다.
유한 구간의 수치는 실제 적분에서 확인한다. 이 국소식 자체를 전 구간
해나 전역 수렴 결과로 사용하지 않는다.
두 명시적 상쇄 사례는 J2≠0이다. 등방 무응력 기준 사례에는 이 비를
계산할 필요가 없다.

## R5. 원자망과 동위원소 불변부분공간

출력은 n; H1 I–II; D I–II; T I–II; He3 I–III; He4 I–III;
Li6 I–IV; Li7 I–IV의 21개 상태다. 전자는 전하 합으로 계산한다.
I_A는 핵종 A의 초기 수밀도/바리온 비이며 Y_A,q=I_A f_Z,q다.
입력 abundance는 donor의 지정값을 그대로 사용한다:
D/H1=2.5e-5, He3/H1=1e-5, He4/H1=0.08112582781456953,
Li6/H1=1e-14, Li7/H1=5e-10, n=T=0.
이 수들은 초기조건이며 이번 실행으로 추론한 BBN abundance가 아니다.

원래 원자망의 식은

    dY/dt = [G_photo(T,J)+D_beta+n_e R(T)]Y,
    n_e=n_b q^T Y,
    J_Y=G_photo+D_beta+n_e R+n_b(RY)q^T.

원자 전이의 off-diagonal은 비음수이고 column 합은 0이다. 각 핵종 내
전하 사슬은 핵종 수를 보존한다. beta 전이는 A를 보존하고 생성 전자까지
세면 총전하도 보존한다. 이번 초기조건에서는 n/T=0이 불변이므로 그 flux는 0이다.

원소 Z가 같은 동위원소에는 동일한 전자 반응률과 동일한 초기 전하분율을
적용한다. 이는 source의 명시적 electronic-equality 근사다. 그러면

    df_Z/dt = [G_photo,Z+n_e R_Z] f_Z,
    n_e=n_b Σ_Z (Σ_(A∈Z) I_A) q_Z^T f_Z.

모든 동위원소가 공유하는 비선형 n_e는 이 동일성을 깨지 않는다. 원래 식에
Y_A=I_A f_Z를 대입하면 각 isotope 식이 위 원소 식과 일치한다. 유한
온도·광원 영역의 매끄러운 반응률과 양의 H에서 ODE의 국소 유일성을
적용하면 동일 초기분율은 전 구간에서 유지된다. 따라서 21개 scaled
population은 H의 2개, He의 3개, Li의 4개 분율, 총 9개로 표현된다.

P를 이 9개를 원래 isotope scaled population으로 복사하는 행렬,
R을 H1/He4/Li7 대표를 선택하는 행렬이라 하면

    RP=I, F(Pf)=P R F(Pf), J_reduced=R J_full P.

같은 관계를 전체 geometry/chemistry/tau Jacobian에 적용하면 H와 n_e의
상호 미분항도 보존된다. isotope abundance나 출력 열을 삭제하지 않는다.
각 isotope 초기 inventory와 복원된 전하분율의 곱을 실제 Y로 저장한다.
원래 division의 2.71e-20 초기 반올림 차이는 별도 잔차로 기록한다.

## R5–R6. 62→33 축약과 검산

반사대칭 f(mu)=f(-mu) 아래 홀수 다중극은 0이다. LRS 수송 연산자는
parity를 보존하며 Thomson damping은 대각이다. 네 energy/number tower에서
각각 ell=0,2,4,6,8을 유지한다. elapsed-time, b, s 세 변수와 합쳐
기하 상태 수는 23이다. identically-zero gas-energy placeholder만 제거한다.
원자 9개와 tau 하나를 더하면 총 33개다.

이는 적분 좌표 수를 29/62=46.77% 줄인다. 33×33 Newton 행렬의 원소 수는
62×62의 28.33%다. 실제 wall-time 또는 전체 RSS 감소율은 측정하지 않았으므로
이 대수적 크기 감소를 속도 향상 측정으로 표시하지 않는다.

Wolfram의 실제 CAS 출력은 generator column 합 0, 공통 electron 표현의
잔차 0, isotope 표현의 잔차 0, tensor norm²=6s²/6p², work=6sp를 확인했다.
독립 intake의 실제 source 3개 입력에서는 chemistry lift 잔차가
1.26e-29–5.05e-29 s^-1이었다. 전체 코드의 finite-state projection 검산과
두 전 구간 full62 비교는 별도 실행 근거로 연결한다.

비영 n/T 초기량, isotope별 전자율·초기 전하분율, nuclear transmutation,
홀수 초기 multipole을 활성화하는 모델은 이 축약의 정의역 밖이다.
그 경우 compact adapter는 원래 62상태 경로가 필요함을 명시한다.

## R6–R8. 광원, 에너지, 첨부 그림의 대응

지정 입력은 Q(z)=[1+tanh((7-z)/0.8)]/2,
T(z)=100+11900Q K이며 UV number spectrum은 5–200 eV의 E^-2.5다.
late Gamma_HI=1e-12 s^-1로 정규화한다. 이 source는 각 시점의 local
isotropic reservoir다. 동적으로 수송되는 CMB/nu와는 구분한다.
100 K 하한은 채택한 Li RR 자료의 q=3 하한 90 K보다 높다.

Photo 단면적은 Verner–Ferland–Korista–Yakovlev 1996 및
Verner–Yakovlev 1995 partial-shell 식, RR은 Verner–Ferland 및 Badnell,
DR은 기존 Badnell coefficient를 그대로 재사용한다. Li I의 inner-shell
흡수에는 source의 단일 charge-step 근사를 유지하고 primary electron
에너지와 미해결 core energy를 나누어 기록한다.

바리온은 등방 common-T gas로 pi_b=0이다. matter 응력은 별도 collisionless
성분에서 오며, 실제 원자망은 n_e를 통해 photon 산란에 되먹임한다.
열/이온화/UV 에너지의 동적 critical density 비와 지정 온도 경로에 필요한
순 열입력 장부를 저장한다. 그 작은 비 자체를 전역 오차 상계로 바꾸지 않는다.

그림의 오른쪽 19개 반응을 `intake/theory/NETWORK19_SCOPE.json`에 기록한다.
Li IV와 Li6를 추가했고, n beta decay는 HII를 만들며 TI/TII beta decay는
spectator-electron 근사에서 각각 He3II/He3III를 만든다. 그림의 일부
화살표 위치와 nuclear stoichiometry가 달라 오른쪽 반응 목록을 기준으로 했다.

추가 Li6(alpha+D) 채널의 문턱은 TUNL 평가자료에서 1.4743 MeV다.
다른 표시된 nuclear photodisintegration 문턱은 이보다 높다. 따라서
Phi(E)=0 for E>200 eV인 현재 모델에서는

    Gamma_nuclear=∫Phi(E)sigma_nuclear(E)dE=0

가 지원영역 분리로 성립한다. 이 결론은 thermal fusion의 생략 오차를
계산한 것이 아니다. 기존 toy_bbn의 REACLIB 계수는 후속 핵반응 확장용
source로 식별했으며 100–12000 K에 임의 외삽하여 활성화하지 않았다.
현재 활성 원자망과 비활성/미구현 핵반응의 상태를 표와 파일로 유지한다.

## R9–R10. 구현 연결과 판정 범위

O.C1–O.C10은 source 재사용과 정확한 좌표축약, R1–R10은 위 조건부 모형과
proof, C1–C10은 실제 127개 전구간 적분·그림·독립 검토에 대응한다.
이론 검산과 source 검토가 끝나면 실제 실행으로 진행한다.

결과의 과학적 범위는 지정된 T/UV와 retained-process 원자망 아래의
non-tilted LRS H–Li preliminary sweep이다. 전역 분해능 수렴, isotope-specific
rate correction, CI/CX/분자/열핵반응, 완전한 thermal/radiative Q^a closure는
각각 별도 확장 의무다. 실제 완료·검증·게시·백업 상태는 DAG와 delivery의
각 증거로 판정하고, 이 문서의 모형 정의로 실행 완료를 대신하지 않는다.

## 원전

- https://www.pa.uky.edu/~verner/photo.html
- https://www.pa.uky.edu/~verner/rec.html
- https://amdpp.phys.strath.ac.uk/tamoc/DATA/RR/
- https://amdpp.phys.strath.ac.uk/tamoc/DATA/DR/
- https://arxiv.org/abs/2011.06518
- https://nucldata.tunl.duke.edu/nucldata/HTML/A%3D6/06Li_2002.shtml

원 계수, 라이선스, Git blob/commit, 실제 SciSpace·Exa 조회와 Wolfram
검산의 provenance는 동봉한 source와 intake/evidence에 연결되어 있다.
