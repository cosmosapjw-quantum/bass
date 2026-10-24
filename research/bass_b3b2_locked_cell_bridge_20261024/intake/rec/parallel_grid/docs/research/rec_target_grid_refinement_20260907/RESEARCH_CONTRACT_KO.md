# REC target-grid refinement — fixed reference measure, weak source and JVP

WORK_UNIT=REC_TARGET_GRID_REFINEMENT_WITH_FIXED_REFERENCE_MEASURE
STATUS=DERIVED_AND_SOURCE_AUTHORED; EXECUTION_PENDING

## 1. 선행 결과와 이번 한 단계

수용된 보충 결과는 59dafbd34bc21b1b885c716b7b8cc899636bbd60 / tree
c0d6a862567e111cfe92a6fd5a3c30051180e38e다. PR80의 주 대화 수용 댓글
5567434296을 이번에 다시 읽었다. 기존 PR79의7개/84방향과 새 보충4개/16방향은
완료된 별도 근거다. 이를 재실행하지 않는다. 과거 PR79 raw artifact/원래 PNG
수령 미완료는 그대로 두며 다음 연구의 불필요한 선행조건으로 만들지 않는다.

이번 질문: 같은 연속 photon state/perturbation, 같은 원자 population,
같은 원자 표와 reference measure에서 target-grid만 세분화하면 무엇이
수렴하는가? 원자 base/hires 표의 차이와 target-grid 오차를 분리한다.

현재 main container와 Python은 각각 실제 호출에서 process 시작 전
ClientError였다. 따라서 새 syntax/수치/CAS/그림/독립 review는0회다.
여기에는 직접 유도와 source 작성/같은 작성자 경로 검토만 있다. 계획된
검사와 생성될 파일을 관측 결과라고 쓰지 않는다. Actions는 사용하지 않는다.

## 2. 범위·단위·새 제조 입력

같은 수소 정지계, (-,+,+,+), scalar unpolarized 2s 두 광자 한 채널,
g=1, 양의 x_u,x_g,f, 고정 source-bin 에너지와 a_b [s^-1]를 사용한다.
광자 에너지는 E=E21*u, E21=10.198714553953742 eV이며 기존 모듈의
1 eV=1.602176634e-19 J, h_P=6.62607015e-34 J s 변환을 재사용한다.
자연단위 전환은 없다. Hubble-time/log-state RHS가 아닌 물리시간 source를
검사한다. d/d(alpha)의 방향변수 alpha는 무차원이며 이동 grid/event는 없다.

고정 원본 HyRec base140/hires408개의 normalized 2s rate만 이번 비교에
사용한다. raw 계수/정규화 정보는 loader의 provenance로 보존하고 중복
구적 가중치, source-bin 폭, 두 광자 계수를 곱하지 않는다. 각 사건의 두
leg를 COM에 한 번씩 전달한다. 원본 C/history 또는 다른 채널은 실행하지 않는다.

새 제조 reference measure를 명시적으로 선택한다:

    dmu = mu_* (1+u^2) du, mu_*=8 m^-3,
    u in [epsilon,1-epsilon], epsilon=2^-30,
    n_H=8 m^-3, x_u+x_g=9/16.

이는 물리 photon phase-space measure, actual BASS cell 또는 finite-volume
권위를 선언한 것이 아니다. PR79의 mu=(2,4,8,4,2)를 복제한 것도 아니다.
격자는 PR79의5개 u node에서 각 구간을 이분해 N=5,9,17,33,65,129로 만든다.
모든 격자에서 endpoint가 같고 coarse nodes가 fine nodes에 포함된다.

연속 chi=ln(1+1/f)를 세 가지 고정 함수로 선택한다:

    affine_balance: chi=1/2+u, eta=0;
    curved: chi=1/2+u+u(1-u)/8, eta=-1/8;
    odd_null: chi=1/2+u+u(1-u)(2u-1)/8, eta=0.
    x_u/x_g=exp(eta-2).

세 함수 모두 chi>=1/2다. 따라서 f와 Bose 응답 도함수에 격자와 무관한
상한이 있다. affine_balance는 양의 offset을 가진 제조 상세균형이지
Planck IR 극한 실험이 아니다. PR79의 chi=2u/그림/반례 eta와 새 입력을
동일한 상태로 표현하거나 이번 결과를 이전 결과의 정확도 개선으로 비교하지 않는다.

두 고정 방향은 공통 delta_chi=1/16+5u/32-u^2/8이고,
photon 방향은 원자/밀도 변화0, mixed 방향은 추가로
(delta_xu,delta_xg,delta_rate_scale,delta_nH)=(1/64,-1/32,1/8,2 m^-3)다.
같은 함수와 같은 원자 population을 모든 표/격자/읽기에 사용한다. 결과를
본 후 상태/eta를 재선택하거나 격자마다 f를 재정규화하지 않는다.

## 3. 연속 측도를 고정하는 nodal 질량 — 직접 유도

phi_i를 연속 piecewise-linear hat으로 두고

    mu_i^(N)=integral phi_i dmu,
    B_is=phi_i(u_s), D_ib=B_i,tb+B_i,cb

로 정의한다. B는 nonnegative, sum_i B_is=1, sum_i u_i B_is=u_s다.
격자 내부 source만 허용하며 외삽/사후 보정은 하지 않는다. 구간 [a,b],
h=b-a의 두 endpoint hat 기여는 정확히

    left = mu_* h [(1+a^2)/2 + a h/3 + h^2/12],
    right= mu_* h [(1+a^2)/2 + 2a h/3 + h^2/4].

합은 고정 dmu 적분이고, 각 mu_i>0다. 코드에는 이 닫힌식을 쓰고 검사에서는
cubic integrand에 정확한 별도2점 Gauss 구적으로 대조한다. 고정 함수 f의
상태 적분 Q0=sum mu_i f_i, Q1=sum mu_i u_i f_i도 독립 mpmath 적분과 비교한다.
Q1의 물리 에너지 밀도는 E21*Q1이다. 유한 격자 Q0/Q1을 억지로 같게 만들지 않는다.

중요한 비식별성: C_i=n_H/mu_i sum_b D_ib Gamma_b이므로 모든 weak source
moment에서 mu_i가 상쇄된다. 다른 양의 mu'_i를 넣고 C'_i를 일관되게 다시
계산하면 모든 weak moment가 같을 수 있다. 따라서 source moment 성공만으로
reference measure의 올바름을 인증할 수 없다. mu 공식과 상태 적분을 별도
검사하는 이유다. 이 검사가 인증하는 것은 선언된 제조 measure의 구현이다.

## 4. 고정 원자 표에서의 reference — 직접 유도

각 표에서 연속 f(u)를 실제 source-bin 에너지에 직접 평가한 rate를
Gamma_b^*=a_b[x_u(1+f_t)(1+f_c)-x_g f_t f_c]라 쓴다. 실제 direct() 경로는
원본 paired API를 사용하되 target interpolation을 하지 않는다. 따라서
이는 target-grid 오차의 reference이며 원본 paired API 자체의 독립 oracle도,
원자 구적의 연속체 참값도 아니다. 별도 고정밀 nonlinear primal이 구현 미분을
검증하는 두 번째 역할을 맡는다.

고정된 유한 원자 표의 signed photon source measure는

    nu_*=sum_b Gamma_b^* (delta_{u_t,b}+delta_{u_c,b}).

이다. 현재 point-deposition 계약 아래에서는 delta source의 약형 극한을
비교해야 한다. mu_i가 O(h)이고 사건이 node 주변에 국소화되면 C_i가 O(1/h)로
커질 수 있다. 이는 그 자체로 발산하는 물리 source를 뜻하지 않는다. 크기가
다른 C_i 배열의 단순차나 nodal infinity norm을 strong convergence 기준으로
사용하지 않는다. 양의/음의 rate의 상쇄 가능성도 있어 이 scaling을 모든
node의 필연적 성장으로 해석하지 않는다.

psi=(1,u,u^2,u^4)의 weak moments를 사용한다:

    M_psi^(N)=1/n_H sum_i mu_i psi(u_i) C_i
             =sum_b Gamma_b^(N) Psi_b^(N),
    Psi_b^(N)=(I_N psi)(u_t,b)+(I_N psi)(u_c,b),
    M_psi^*=sum_b Gamma_b^* Psi_b^*,
    Psi_b^*=psi(u_t,b)+psi(u_c,b).

psi는 무차원이고 모든 M은 수소 원자당 [s^-1]다. 에너지 source는 E21*M_u다.
psi=1,u의 분배 오차는 정확히0이므로 이 두 보존식만으로 수렴을 선언하지 않는다.

## 5. read / scatter / cross의 정확한 분해

Delta_Gamma=Gamma_N-Gamma_*, Delta_Psi=Psi_N-Psi_*이면

    M_N-M_* = sum Delta_Gamma Psi_*
              +sum Gamma_* Delta_Psi
              +sum Delta_Gamma Delta_Psi.

세 항은 각각 read, scatter, cross다. code는 실제 COM output으로 계산한
좌변과 source-side 세 항을 대조한다. 모든 항을 signed 값으로 보존하여
오차 상쇄를 숨기지 않는다. 고정 source 에너지와 grid에서 방향미분도
동일한 식의 Gamma를 delta_Gamma로 바꾸면 된다. mu/nH로 변환한 count-JVP에는
반드시 beta*(dC-C*dnH/nH)가 들어간다.

정확한 quadratic witness: [a,b]에서

    (I_N u^2)(u)-u^2=(u-a)(b-u)>=0.

a=1/4,b=1/2,u=3/8이면 defect=1/64다. 새 curved chi는 이차항이 -u^2/8이므로

    I_N chi-chi=-(u-a)(b-u)/8=-1/512

다. 이는 실제 원자 표의 특정 bin이라고 주장하지 않는 별도 유리수 witness다.
코드는 실제 모든 source-bin 위치에서도 위 defect 식을 대조한다.

## 6. 조건부 O(h^2)와 JVP bound — 직접 유도

h=max mesh gap, chi와 delta_chi가 C^2이고 chi>=1/2일 때,
linear interpolation의 Peano remainder 또는 Rolle 정리에서

    ||I_N z-z||_infty <= h^2 ||z''||_infty/8

를 얻는다. g(chi)=1/expm1(chi), F=1/expm1(1/2),
L1=F(1+F), L2=L1(1+2F)를 두면

    e_f <= L1 Hchi h^2/8,
    e_df <= (L1 Hdelta + L2 Hchi D0)h^2/8,
    Hchi>=||chi''||, Hdelta>=||delta_chi''||, D0>=||delta_chi||.

이 fixture에서 각 계수 상한은 polynomial 계수의 절댓값 합으로 코드에서
계산한다. 데이터에 맞춘 상수가 아니다. K=xu(1+F)+xg F,
P=xu(1+F)^2+xg F^2, A=sum a_b, KD=|dxu|(1+F)+|dxg|F라 두면

    E_Gamma := sum_b |Gamma_N-Gamma_*| <= 2 A K e_f,
    E_dGamma <= A [2 |ds| K e_f + 2 KD e_f + 2 K e_df
                    + 2 |xu-xg| L1 D0 e_f],
    sum_b |dGamma_*| <= A [|ds|P + |dxu|(1+F)^2 + |dxg| F^2
                           + 2 K L1 D0].

도함수 차이 bound는 bilinear rate의 occupation 미분 두 개를 따로 분해하면
따른다. 모든 psi의 sup norm<=1, Hpsi=(0,0,2,12)이므로

    |M_N-M_*| <= 2 E_Gamma + A P Hpsi h^2/4,
    |dM_N-dM_*| <= 2 E_dGamma + (sum |dGamma_*|) Hpsi h^2/4.

이는 chi 읽기의 조건부 consistency bound다. raw floating arithmetic의
보편적 error certificate, 실제 시간진화의 전역 수렴정리 또는 모든 photon
스펙트럼의 정리는 아니다. 검사는 기존4096*epsilon의 roundoff allowance를
별도로 둔다. log_control은 ln(u)에서 ln(f)를 선형 보간하므로 해당 좌표의
mesh/regularity 조건을 따로 다뤄야 한다. 작은 epsilon의 첫 구간을 가진
현재6개 격자에서 log 대조에 동일한 h^2 slope를 강제하지 않는다.

state moment bound는 Q=integral I_N z dmu에 위 interpolation bound를
적용한다. z=f,uf의 두 번째 도함수 상한은 각각
L2||chi'||^2+L1||chi''|| 및 그 값+2L1||chi'||다.

## 7. 두 해상도 축의 분리

각 표는 자기 direct-bin reference를 가진다. 같은 grid/state에서

    M_hires,N-M_base,N
    = (M_hires,*-M_base,*) + (error_hires,N-error_base,N).

오른쪽 첫 항은 atomic-table difference, 둘째는 target-grid 오차 차이다.
ATOMIC_TABLE_CONTRAST.csv에 primal/JVP 모두 기록한다. 두 원자 표 중 하나를
증거 없이 물리 참값으로 택하지 않는다. finite-grid 기울기가 정확히2가
아니라고 fixture를 조정하지 않는다. 원자 bin의 knot 위치, 상쇄와 roundoff가
개별 ratio에 영향을 준다. conditional bound와 실제 finite-grid 관측을 구분한다.

대칭 N=2m+1의 단일 transition은 적어도 m+2개의 좌보존량을 가진다.
또한 rank V<=min(m+1,number_of_active_bins)이므로 finite atomic table를
고정한 채 grid를 늘리면 추가 null directions가 생길 수 있다. 이번 목적은
그 rank를 재감사하는 것이 아니라, 이런 구조 아래 적절한 weak convergence를
측정하는 것이다. 전체 collision physics의 열평형 구조로 일반화하지 않는다.

## 8. 구현 경로와 검증 범위

refinement.py:
원래 study.load_tables/weights -> 새 nested hats/mu -> 같은 연속 함수 샘플 ->
원래 PhysicalTwoPhotonRamanBin.paired_rates/net_action/jvp ->
원래 COMSourceDepositionPlan.apply/jvp -> nodal moment/entropy/count 방향.
원래 study.compose는5-node 전용이므로 monkey-patch하거나 변경하지 않는다.
새 composition은 이 연구 디렉터리에만 있고 production hook은 없다.

별도 independent()는 고정 binary64 B/L/a를 lift한 nonlinear primal만
구현한다. 입력 polynomial/메타데이터는 공유하지만 paired/COM 함수와 analytic
JVP는 호출하지 않는다. 80/120자리 중앙차분 h=2^-32 및2^-36으로16개 선택된
새 구성(N=9,65; 두 표/두 읽기/두 방향)을 비교한다. 이는 grid-convergence
오차와 별개의 implementation derivative error다.

6개 unittest 그룹: measure/nesting, exact quadratic witness, equilibria/entropy,
weak split+조건부 bound+state integral, independent JVP, measure-blindness 및
companion 삭제 진단. 계획된 데이터는 weak576행, state18행, JVP16행,
bin sample2192행, table-contrast288행이다. 이 수는 실행 전 설계 census다.
검사 개수를 physics completeness로 환산하지 않는다.

run_refinement.py는 실제 child process와 result/exit/TestID/source를 분리한다.
plot_refinement.py는 저장된 CSV만 읽으며 네 내용의90/180mm PNG8개를 생성하도록
작성됐다. 현재 생성 그림0개/시각검토0회다. 실제 부호와0을 유지하는 symlog
축의 선형영역은±1e-14 s^-1이며 이는 data floor나 허용오차가 아니다.

## 9. 같은 작성자의 두 관점 검토 및 미완료

수학: 단위/두 leg counting, 새 measure와 옛mu의 구분, chi positivity,
constant/linear exactness, quadratic signed witness, moment/JVP 분해와
Gronwall 없는 순간 source bound를 직접 검토했다. 구현: 원본 API를 실제
호출하는 경로, independent reference의 API 비호출, density 변환, signed
CSV, 별도 process exit와 saved-data renderer를 소스 수준에서 검토했다.
이는 새 제3자 검토나 실행 검증이 아니다. runtime/syntax/그림상 관측 결함은
현재 미평가다. 새6개가 PASS하더라도 전 solver/time convergence로 승격하지 않는다.

위험과 detector: (P1) weak source가 measure를 식별 못함 -> measure/state
integral 및 음성대조; (P1) conservation을 consistency로 오인 -> u^2/u^4
split과 quadratic witness; (P1) table 차이와 grid 차이 혼합 -> table contrast;
(P1) 같은 연속 perturbation을 잃음 -> fixed polynomial와 independent JVP;
(P1) log 대조에 잘못된 기울기 강제 -> 별도 좌표 및 bound 적용 제외;
(P2) figure를 생성만 하고 신뢰 -> 저장된 CSV와 실제 PNG 후속검토 대기.

## 10. 문헌과 출처 역할

SciSpace의 weak-form/conservative collision 검색은 주로 classical Boltzmann,
Landau 관련 방법론을 반환했다. 이를 이번 Bose two-photon의 직접 근거로
치환하지 않는다. 웹에서 확인한 원 연구의 초록/메타데이터:

- P. A. Markowich and L. Pareschi, Fast conservative and entropic numerical
  methods for the Boson Boltzmann equation, Numerische Mathematik99(2005)509-532,
  doi:10.1007/s00211-004-0570-5; https://arxiv.org/abs/1009.2748
  (arXiv 게시2010과 journal2005를 구분). 보존/entropy/BE stationary 구조를
  따로 다루는 방법론 배경이며 이번 source/table/map의 인증이 아니다.
- L. Pareschi and T. Rey, Moment preserving Fourier-Galerkin spectral methods
  and application to the Boltzmann equation; https://arxiv.org/abs/2105.13158
  conservation과 consistency/stability를 별도로 검증하는 비교 배경이다.
  이 논문의 spectral theorem을 현재 piecewise-linear scheme에 적용하지 않는다.

여기서 새로 사용한 measure, fixed functions, weak decomposition, O(h^2)
project-specific bound와 구현은 위 본문의 직접 유도/연구 선택이다.
논문 PDF 전문이나 사용자의 전체 BASS 수식 SSOT를 이번에 검토한 것으로
표시하지 않는다. 그 SSOT를 REC microphysics 권위로 승격하지 않는다.

## 11. 완료 경계

현재 완료는 유도와 검사/실행/그림 코드 작성이다. 구현 검증은 미완료다.
다음 한 행동은 새6개 검사와 saved-data 그림의 실제 로컬 실행/범위 내 수리/
해석/Git 반환이다. 이후 무엇을 할지는 그 관측값으로 결정한다. 새 grid나
더 큰 프로그램을 자동으로 추가하지 않는다.

NO_PASS_REC_PHYSICAL_SPLIT; physical_source_authenticated=false;
provider_admitted=false. 이전 source/evidence, workflows, main/PR79/80,
공식 Jira dependency, provider/merge/ready는 변경하지 않는다.
