# BASS–REI electron-density / Thomson boundary 연구

근거 상태: 아래 식은 정의와 국소 공변 운동학에서 **derived**다. BASS의 기존 `frame.rs`, `visibility.rs`와 REI `hhe_events.rs`를 실제 읽어 구현 의미와 대조했다. 현재 문서 자체는 수치 실행이나 전체 Bianchi/CMB 검증의 증거가 아니다. 실행 판정은 별도 coding/evidence receipt가 소유한다.

## 1. 선택한 경계와 상태 의미

이번 bounded 목적은 REI의 검증된 H/He snapshot을 BASS의 기존 `ElectronState` 및 고정입력 Thomson visibility로 연결하는 것이다. 새 원자율·ionization history·collision engine을 만들지 않는다. 실제 `HHeModel::electron_density`는 공개된 full model/state 검증을 포함한다. `Ft03Model.gas` 역시 이 density 경계에 사용할 수 있다. 온도 의존 FT03 RHS를 계산하는 작업과 전자밀도만 계산하는 작업을 구별한다. 후자에만 필요한 값은 proper 핵밀도와 species fractions이므로 FT03의 rate-temperature guard를 이 경계의 독립 조건으로 추가하지 않는다.

공통 물질 rest frame에서

\[
x=\frac{n_{\rm HII}}{n_{\rm H}},\qquad
y_1=\frac{n_{\rm HeII}}{n_{\rm He}},\qquad
y_2=\frac{n_{\rm HeIII}}{n_{\rm He}},
\]

이며 REI 배열 순서는 `[x, y1, y2]`다. 제약은 \(0\le x\le1\), \(y_1,y_2\ge0\), \(y_1+y_2\le1\)이다. 전하중성과 H/He만의 조성이라는 현재 모형 아래

\[
n_e^*=n_{\rm H}x+n_{\rm He}(y_1+2y_2). \tag{1}
\]

별표는 물질 rest-frame proper density다. \(x_e=n_e^*/n_{\rm H}\)는 별도의 H-normalized electron fraction이며 helium 때문에 1을 넘을 수 있다. 이것을 \(x=x_{\rm HII}\)의 [0,1] 범위로 잘라서는 안 된다. 핵종이 전혀 없는 경우 그 분율의 물리적 의미는 없지만, 현재 upstream 허용·거절 정책은 그대로 따른다. 특히 upstream `HHeModel`은 두 핵밀도가 모두 0인 모형을 거절한다. BASS `ElectronState`가 진공을 표현할 수 있다는 이유로 REI 입력 검증을 우회하지 않는다.

REI는 cm\(^{-3}\), BASS는 m\(^{-3}\)를 사용한다.

\[
n_{s,\mathrm{SI}}=10^6 n_{s,\mathrm{cgs}}. \tag{2}
\]

이는 단위 변환일 뿐 팽창·Lorentz contraction·부피평균을 포함하지 않는다. BASS rate는 `C_M_S=299792458`와 `SIGMA_T_M2=6.6524587e-29`라는 기존 고정 profile을 따른다. 이 작업은 상수의 정밀도를 재평가하지 않는다. REI의 `model.c_cm_s`를 density 변환에 사용하지 않으므로, 임의 synthetic light-speed를 가진 chemistry run을 실제 SI 시간력과 동일시하려면 후속 run contract에서 constants profile을 확인해야 한다.

## 2. number current와 chemistry clock

Signature는 \((-+++ )\). Dimensionless unit timelike vector를 \(u_m^a u_{ma}=-1\), dimensional 4-velocity를 \(U_m^a=c u_m^a\)로 둔다. Free-electron current와 source는

\[
J_e^a=n_e^* U_m^a,\qquad
\nabla_aJ_e^a=S_e,
\]
\[
\frac{d n_e^*}{d\tau_m}+\theta_m n_e^*=S_e,
\qquad \theta_m=\nabla_aU_m^a. \tag{3}
\]

\(S_e\) 단위는 m\(^{-3}\)s\(^{-1}\), \(\theta_m\)는 s\(^{-1}\)다. 두 원자핵 current가 보존되고 같은 속도를 가진다는 전제 아래

\[
\frac{dn_{\rm H}}{d\tau_m}+\theta_m n_{\rm H}=0,
\qquad
\frac{dn_{\rm He}}{d\tau_m}+\theta_m n_{\rm He}=0,
\]

을 (1)에 대입하면

\[
S_e=n_{\rm H}\frac{dx}{d\tau_m}
 +n_{\rm He}\left(\frac{dy_1}{d\tau_m}
 +2\frac{dy_2}{d\tau_m}\right). \tag{4}
\]

분율 방정식에서는 공통 부피희석항이 정확히 소거된다. 비기울어진 homogeneous Bianchi에서 \(\theta=3H_V\)와 \(a_V=({V}/{V_0})^{1/3}\)를 정의하면 \(n_s\propto a_V^{-3}\)다. 이 관계는 shear=0을 가정하지 않는다. FLRW 극한에서만 이를 통상적인 scale factor \(a\)와 동일시한다.

He RCT의 종별 변화 \((\dot n_{\rm HI},\dot n_{\rm HII},\dot n_{\rm HeII},\dot n_{\rm HeIII})=(-R,+R,+R,-R)\)는

\[
S_e^{\rm RCT}=R+R-2R=0. \tag{5}
\]

따라서 RCT는 같은 순간 직접 Thomson opacity를 생성하지 않는다. 이후 온도·종분율·다른 반응을 변화시켜 \(n_e\) 궤적에 간접 영향을 줄 수 있다. 기존 scalar RCT rate만으로 그 궤적 영향이나 방출 photon spectrum을 확정할 수 없다.

## 3. photon ray clock과 정확히 한 번의 Doppler factor

Bianchi normal unit observer를 \(n^a\), 그 관측자의 광자 전파방향을 \(e^a\)라 두며 \(n\cdot e=0\), \(e\cdot e=1\)이다. 여기서 \(e\)는 **광자가 미래로 전파하는 방향**이다. 하늘에서 관측자가 보는 반대 방향을 넣으면 부호가 바뀐다.

\[
u_m^a=\gamma(n^a+\beta^a),\qquad
p^a=\frac{E_n}{c}(n^a+e^a),
\qquad \gamma=(1-\beta^2)^{-1/2}.
\]

따라서 물질계 광자에너지는

\[
E_m=-c\,u_m\cdot p=D E_n,\qquad
D=\gamma(1-\boldsymbol\beta\cdot\mathbf e)>0. \tag{6}
\]

Ray를 따라 normal-clock 간격 \(dt_n\)에 대한 변위는 \(dx^a=c(n^a+e^a)dt_n\). 물질계가 측정하는 광자 경로길이는

\[
d\ell_m=-u_{ma}dx^a=cD\,dt_n.
\]

Cold Thomson approximation에서 optical-depth increment는

\[
d\tau_T=\sigma_T n_e^*d\ell_m,
\qquad
q_n\equiv\frac{d\tau_{\rm forward}}{dt_n}
=c\sigma_T n_e^*D. \tag{7}
\]

\([c\sigma_T n_e^*]=(\mathrm{m/s})\mathrm{m^2}\mathrm{m^{-3}}=\mathrm{s^{-1}}\). Normal observer가 측정하는 전자밀도를 \(n_{e,n}=\gamma n_e^*\)라 쓰면 동등한 식은 \(q_n=c\sigma_T n_{e,n}(1-\beta\cdot e)\)다. 여기에 다시 \(\gamma\)를 넣으면 안 된다.

BASS `ElectronState::scattering_rate_per_normal_second`가 (6)의 \(D\)를 내부에서 한 번 적용한다. 따라서 adapter에는 proper density만 넘기며 미리 \(D\) 또는 \(\gamma\)로 밀도를 변형하지 않는다. `MaterialFrame::atomic_normal_time_source`의 \(1/\gamma\)는 물질 worldline의 \(d\tau_m/dt_n\)이고, 광선 위의 \(D\)와 다른 관계다. Fixed-input tilted photon rate를 계산했다고 tilted chemistry trajectory를 진화시킨 것은 아니다.

\(\beta=0\)이면 \(D=1\)이라 국소 Thomson rate는 방향 독립적이다. 이는 Bianchi의 방향 의존 redshift, ray direction, screen transport 또는 전 하늘 radiation이 등방이라는 뜻이 아니다. 이 요소들은 기존 geometry/transport lane이 소유한다.

## 4. FLRW clock 복원

FLRW에서 proper time \(t\), 초 단위 conformal time \(\eta_s\), 길이 단위 conformal coordinate \(\chi=c\eta_s\)를 구별한다.

\[
dt=a\,d\eta_s,\qquad
q_t=c\sigma_T n_e,\qquad
q_{\eta_s}=a c\sigma_T n_e,\qquad
q_\chi=a\sigma_T n_e. \tag{8}
\]

각 rate와 clock의 곱은 같은 dimensionless \(d\tau_T\)다. m 단위 \(\chi\)를 Mpc로 바꾸면 rate에는 m/Mpc 변환상수를 곱해야 한다. CAMB의 공변 시간은 길이 단위 convention이므로 그 `opacity=a*n_e*sigma_T`와 초 단위 BASS rate를 수치 그대로 비교해서는 안 된다. 이 문서에서 conformal mapping은 **derived contract**이며 새 conformal runtime API를 구현했다는 뜻이 아니다.

Comoving density \(N_e=a^3n_e\)를 쓰면

\[
q_t=c\sigma_T N_e/a^3,\qquad
q_{\eta_s}=c\sigma_T N_e/a^2. \tag{9}
\]

정상 expanding FLRW에서 \(dt/dz=-[(1+z)H(z)]^{-1}\). 현재부터 과거 redshift \(z\)까지의 backward optical depth는

\[
\tau(z)=\int_0^z\frac{c\sigma_T n_e(z')}{(1+z')H(z')}dz'. \tag{10}
\]

균일하고 \(x_e\)가 일정한 Einstein–de Sitter analytic fixture, \(n_e(z)=N_e(1+z)^3\), \(H=H_0(1+z)^{3/2}\), 에서는

\[
\tau(z)=\frac{2c\sigma_TN_e}{3H_0}
 \left[(1+z)^{3/2}-1\right]. \tag{11}
\]

이는 clock/power/sign 검산식이며 실제 재이온화 history의 예측식이 아니다.

## 5. finite-interval visibility와 left-endpoint rule

\(t_0<\cdots<t_N\)은 미래 방향 normal-clock grid이며 입력은 **각 cell의 left endpoint snapshot**이다. \(q_i=q(t_i)\)를 \([t_i,t_{i+1})\)에서 고정하면

\[
\Delta\tau_i=q_i\Delta t_i,\qquad
\tau_i=\tau_{\rm tail}+\sum_{j=i}^{N-1}\Delta\tau_j,
\qquad S_i=e^{-\tau_i}. \tag{12}
\]

\(\tau_{\rm tail}\ge0\)는 마지막 edge에서 관측자까지의 추가 optical depth다. 연속형으로 \(\tau_b(t)=\tau_{\rm tail}+\int_t^{t_N}q(s)ds\), \(\dot\tau_b=-q\), \(\dot S=qS\), \(g_t=q e^{-\tau_b}\ge0\). 따라서 cell 내 마지막 산란 확률은

\[
P_i=S_{i+1}-S_i
=S_{i+1}\left[-\operatorname{expm1}(-\Delta\tau_i)\right]. \tag{13}
\]

얇은 cell에서 \(1-e^{-x}=x-x^2/2+x^3/6+O(x^4)\)이므로 `1-exp(-x)`의 cancellation을 피하는 existing `expm1` 경로를 그대로 쓴다. \(q_i=0\)이면 \(P_i=0\); 매우 두꺼운 cell에서는 floating-point survival이 0으로 underflow할 수 있으나 이를 음수나 unit-renormalized mass로 고치지 않는다.

망원합으로

\[
\boxed{\sum_iP_i+S_0=e^{-\tau_{\rm tail}}}. \tag{14}
\]

\(\tau_{\rm tail}=0\)일 때만 우변이 1이다. 비영 tail에서는 \(1-e^{-\tau_{\rm tail}}\)가 마지막 grid 이후 산란할 확률이고, \(S_0\)는 전체 경로에서 무산란으로 살아남는 질량이다. 유한 interval \(P_i\)만 합을 1로 정규화하면 이 의미를 잃는다. 이 backward tail sum은 미래 방향 grid 위 확률 적분이며 kinetic equation을 음의 timestep으로 진화시키는 기능이 아니다.

이 규칙은 고정된 piecewise-constant \(q\)에 대해 정확하다. 매끈한 실제 \(q(t)\)의 left-endpoint 근사는 일반적으로 전역 1차다. Cell에서 \(|q'|\le L_i\)라면

\[
\int_{t_i}^{t_{i+1}}|q(t)-q_i|dt\le\tfrac12L_i\Delta t_i^2. \tag{15}
\]

반응 적분기의 endpoint 정확도와 visibility quadrature 정확도를 구별한다. `ft03_adaptive_step`의 local error control이 (15)의 \(L_i\) bound나 전체 시간력 visibility convergence를 자동 인증하지 않는다.

## 6. 원자 스레드 오차를 transport하는 최소 계약

같은 ray/frame, grid, observer tail에 놓인 두 입력 \(q,q_{\rm ref}\)에 대해

\[
E_i=\sum_{j=i}^{N-1}|q_j-q_{{\rm ref},j}|\Delta t_j,
\qquad |\tau_i-\tau_{{\rm ref},i}|\le E_i. \tag{16}
\]

비음수 두 depth \(a,b\)에 대해 \(|e^{-a}-e^{-b}|=e^{-\min(a,b)}(1-e^{-|a-b|})\le1-e^{-E}\). 따라서

\[
|S_i-S_{{\rm ref},i}|\le1-e^{-E_i},
\]
\[
|P_i-P_{{\rm ref},i}|\le (1-e^{-E_i})+(1-e^{-E_{i+1}}). \tag{17}
\]

이 bound는 BASS `compare_opacity`의 기존 의미와 같다. 공통 tail이 양수이면 추가 \(e^{-\tau_{\rm tail}}\) 인자로 더 좁힐 수 있으나 현재 API의 더 보수적인 bound를 변경할 필요는 없다. 이 식은 peak 위치·높이, \(C_\ell\), anisotropy 또는 polarization operator norm의 bound가 아니다.

같은 proper 핵밀도와 frame이면

\[
|\delta q_i|\le c\sigma_TD_i
\{n_{{\rm H},i}|\delta x_i|
+n_{{\rm He},i}(|\delta y_{1,i}|+2|\delta y_{2,i}|)\}. \tag{18}
\]

Chemistry endpoint error, density/geometry interpolation error, left-endpoint quadrature error를 서로 다른 입력 오차로 보존한 뒤 (16)에 전달한다. 예를 들어 같은 exact clock에서 \(E_{\rm total}\le E_{\rm chemistry}+E_{\rm frame/density}+E_{\rm quadrature}\)라는 triangle bound를 사용할 수 있다. KF96와 GM25의 17배 scalar-rate 차이는 아직 \(\delta n_e\) bound가 아니며 (18)에 곧바로 넣을 수 없다. `compare_opacity`의 성공은 upstream chemistry source 불확실성의 증명이 아니다.

## 7. filling factor를 species fraction으로 대체할 수 없는 이유

Density \(n_H=\bar n_H\Delta_H\), local ionization \(x\)에 대해 \(\langle n_e\rangle_H=\bar n_H\langle\Delta_H x\rangle\)다. 완전히 이온화/중성인 두 상이라 \(x=I_{\rm ion}\)이어도 \(Q_V=\langle I_{\rm ion}\rangle\)와 \(Q_M=\langle\Delta_HI_{\rm ion}\rangle\)는 일반적으로 다르다.

같은 부피의 두 영역에 \(n_H=(3n_0,n_0)\), \(x=(1,0)\)이면 \(\bar n_H=2n_0\), \(Q_V=1/2\), \(Q_M=3/4\), 실제 \(\langle n_e\rangle=3n_0/2\)다. \(\bar n_HQ_V=n_0\)라는 단순 대입은 틀리다. 적절한 density-weighted x를 사용하여 평균 \(n_e\)를 맞춰도 nonlinear recombination/opacity와 평균 연산의 교환이 따라오지 않는다. 따라서 이번 typed seam은 local H/He fractions만 받고 Q-to-x closure를 제공하지 않는다.

## 8. 구현 완료와 물리 admission의 경계

광자 에너지와 전자 열운동을 무시하는 cold Thomson approximation의 scalar rate/visibility를 시험하는 작업이다. 기존 `ELECTRON-THOMSON-VALIDITY-CONTRACT.md`의 spectrum·event·temperature 조건을 승격하지 않는다. 특히 \(T_e>0\)에서 Maxwellian tail이 무한하므로 thermal diagnostic만으로 exact-cold certificate를 얻지 못한다. Vacuum opacity=0은 collision-off이고 Thomson domain의 적극적 증명은 아니다. Static bounded FT03 chemistry trajectory의 snapshot을 fixed-grid opacity에 연결하는 실행은 팽창·tilted chemistry·full polarized Boltzmann coupling·관측 가능한 CMB history를 검증하지 않는다.

## 출처와 직접 유도의 범위

1. BASS pinned source `14e0cf0486dc834234122f8bd990fe479f593675`, `_rustcore/src/microphysics/{rei,frame,visibility}.rs` 및 `docs/ELECTRON-THOMSON-VALIDITY-CONTRACT.md`: 실제 host API와 현재 gate의 authority. [저장소](https://github.com/cosmosapjw-quantum/bass/tree/14e0cf0486dc834234122f8bd990fe479f593675).
2. REI native `41e4592aa494b48929dcd23fc8504c169a98a908`, `HHeModel`·`HHeState`: proper cgs density, species order, 기존 RCT number ledger. [저장소](https://github.com/cosmosapjw-quantum/rei_bianchi/tree/41e4592aa494b48929dcd23fc8504c169a98a908). 실제 소비 dependency pin은 이번 root intake/구현 receipt가 소유한다.
3. CAMB 공식 [symbolic source](https://camb.readthedocs.io/en/stable/_modules/camb/symbolic.html): opacity 정의, `d exp(-tau)/d eta = visibility`, collision damping 부호. [Lewis CAMB notes](https://cosmologist.info/notes/CAMB.pdf), 2026-07-17판 §I 및 §III, 식(3.1): conformal-length convention과 electron optical-depth 연결. 코드 재사용이나 CAMB parity 검증은 하지 않았다.
4. Pontzen–Challinor, [arXiv:0706.2075](https://arxiv.org/abs/0706.2075): nearly-FRW homogeneous Bianchi polarized transfer 연구의 맥락. 이번에는 abstract의 범위만 확인했으며 그 논문으로 arbitrary-anisotropy correctness를 주장하지 않는다.
5. Challinor, [astro-ph/9911481](https://arxiv.org/abs/astro-ph/9911481): 일반 시공간의 covariant polarized transfer라는 연구 맥락. 이번에는 abstract만 확인했다. (1)–(18)의 대수·clock·probability 결과는 여기서 명시한 가정으로 직접 유도한 결과다.
