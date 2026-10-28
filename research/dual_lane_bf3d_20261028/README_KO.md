# BF3-D: 정적 비균질 lapse의 국소 source와 편광 충돌 수송

COMPLETE_SCOPED_STATIC_LAPSE_INVERSE_FIELD_COLLISIONS. 통합 PR223의 고정 parent5461d50b3f187b4736b62e0f9ecb3e85e413aaee 위에서 실제 package module bianchi.nonperturbative.lapse_field를 추가했다. 코드/테스트 commit b93731b94cb9a66a5face69c4164243aebff1100 이후 최종 변경은 보고서·계약·DAG·영수증뿐이다. 상위 DAG8/15, BF3 PARTIAL이며 production_ready=false다. Main/owner/integration parent와 기존 함수를 바꾸거나 merge하지 않았다.

## 정의와 정확한 변수변환

서명(-+++), ds2=-N(x)^2 c^2dt2+Lstar2 dx_i2, N=exp(epsilon cos x)>0. x는2pi 주기, y/z 의존성은 없다. 시간u=t/Tstar, cbar=cTstar/Lstar. Normal proper time=Ndt, 코드 opacity nu_star=n_e_star sigma_T c*Tstar는 전자 proper-density rate다. Coordinate collision rate=N*nu_star. Bath는 normal observer에 정지한 cold elastic Thomson이고 기하학은 prescribed다. Epsilon/편광 진폭을 섭동 전개하지 않지만 전체 Einstein feedback을 푼 것은 아니다.

mu=n_x, phi는x축 주위 방위각, meridional screen e_theta=(-sqrt(1-mu2),mu cosphi,mu sinphi), e_phi=(0,-sinphi,cosphi)를 사용한다. W는2x2 real P8(S+A) carrier이며 물리적 Hermitian은S+iA다. Y=N^4 W로 두면 redshift가 정확히 제거된다:

    Y_u+cbar N mu Y_x-cbar N'(1-mu2)Y_mu
       =N nu_star(K[Y]-Y).

Physical Cartesian J=N^-4 EYE^T. E는3x2 screen이지 E-mode 계수가 아니다. M(x)=int J(x,n)dOmega는 각 최종 위치의 최종 물리 방향에서 구적한다. BF3-C global coupled phase Jacobian은 local angular weight가 아니다. Raw GL/phi weight를 정규화하지 않고 signed fluctuation을 clipping하지 않는다.

## 실제 구현과 독립 비교

Integrated TetradHistory를 각 final(x,mu)에서 -h까지 적분해 departure x/mu와 screen을 구한다. 이 metric에서 phi는 일정하다. Source를 옮기는 대신 전체 field를 departure에서 Fourier(x)/barycentric(mu) 평가하고 실제 inverse screen의 R^T Y R로 복원한다. Physics source는 final-x 방향에서만 구한다.

DirectHistory는 Fourier/Legendre collocation derivative와 DOP853, split 경로는 exact local P8 collision(h/2), inverse transport(h), collision(h/2)의 Strang 순서다. 두 경로는 서로의 radiation history를 호출하지 않는다. 같은 continuum 문제지만 finite interpolation과 collocation exponential이 동일하다고 전제하지 않는다. Time/space/angular error를 각각 측정한다. 고차 보간의 일반 positivity 보증은 없다. 주요 fixture는 매끄러운 축대칭 full-IQUV이며 phi8 고정이다.

독립 Hamiltonian inverse ray는 tetrad RHS를 호출하지 않는다. 비교한 x/n/r 최대차1.21e-13/3.57e-14/1.30e-13. Integrated lapse와 P8 source는 그대로다. Numerical constructor에서 explicit backend='python_oracle'을 요구하며 native fallback은 없다.

## 물리적 검산과 결과

등방 constant Y는 J proportional to N^-4의 정확한 정지해다. 공간적으로 변하는 opacity를 포함한 equilibrium physical-carrier error2.34e-13,RHS6.07e-15. 그러나 equilibrium collision은0이므로 clock 오류 검증에는 별도 비평형이 필요하다.

Constant N=e^.4,nu_star=.7,u=.6에서 초기 intensity2+.3P2(mu)의 Legendre coefficient c2는 .3[6 exp(-chi)+exp(-.3chi)]/7,chi=.6265663730093335다. 계산.17293635572608768 대 정확값.17293635572609092,오차3.25e-15. N을 빼는 대조군 오차.0338020. 이 c2는 normalized spherical I20이 아니다.

rho=int trJ dOmega,q=int n trJ dOmega=energy_flux/c. 연속식은 partial_u(Nrho)+cbar partial_x(N2 q_x)=0. Y의 weight는N^-3이며 div(N^-3 v)=0. CAS에서 N4변환,weighted divergence,conservative equivalence,I/E exact solution 및 초기조건 residual이 모두0이다. CAS는 독립모델심사가 아니다.

주 시험: epsilon=.55,u in[0,.4],nx33,nmu18,nphi8,nu_star=1.1+.3sinx,cbar1. Y의 초기 I=2+.2cosx+.12mu sin2x+.1P2 cosx,Q=.08(1-mu2)cosx,U=.06(1-mu2)sin2x,V=.04mu cosx. 실제 J에는N^-4가 곱해진다.

Strang8/16/32/64 steps의 source endpoint 차이는1.65891e-4/4.14758e-5/1.03691e-5/2.59229e-6,physical carrier 차이는5.42843e-5/1.35718e-5/3.39302e-6/8.48269e-7. Source observed orders1.999895/1.999974/1.999994. 사전 fine-time gate2e-4와order>=1.7를 바꾸지 않았다.

공간13/21/33 대49점의 source 차이5.29860e-4/4.22135e-7/1.79625e-10. Mu6/10/18 대26 source 차이1.34704e-7/2.01106e-12/3.97904e-13. Fine reference도 exact continuum이 아니며 phi cutoff/infinite tail certificate는 없다. ODE tightening source5.83e-13/carrier1.48e-12. Free analytic initial evaluation at inverse departures 대 direct source2.60e-11/carrier9.92e-10.

주기적 Killing energy relative defect는direct<=2.22e-16,split<=2.89e-15. Local conservative residual은1.24514e-9,raw collision-energy residual1.28362e-13로 별개다. 보존을 사후 projection하지 않았다. 이 global 작은 오차를 일반 interpolation conservation theorem으로 확대하지 않는다.

초기 Y intensity difference=.1cosx P4(mu)는 source<=1.02245e-14지만 u=.4,x0에서 direct Mxx=-.00038576312932216334,split64=-.00038577438250431964로 돌아온다. Endpoint 전체 source 차이1.07350e-7. Signed-response 검사이며 새 positive-pair campaign은 아니다. P4는 Legendre amplitude이고 canonical I40이 아니다. Global phase Jacobian을 local weight에 곱하면 source 차이1.27507947; mixed fixture에서 lapse clock을 누락하면.1038746332. 두 오류를 실제로 검출했다.

## 실행·출처와 패키지 검증

12 unique tests PASS. RED missing-module exit2,firstGREEN,finalGREEN을 보존했다. 한 번의 science campaign:direct11,split7,inverse-ray6,Hamiltonian1. Current/historical science replay0. 최종 검토에서 진단 이름I20을Legendre_c2로 정정하고 tail basis를 명시했다. PRE_LABEL JSON/driver를 보존했고 모든 숫자와 rows는 같으며 수치 재실행은0이다. 기존 DAG의 stale current/next pointer는 별도 보존한 뒤 BF3-D로 갱신했으며 의존성은 그대로다.

Actual full repository CI40659768531/job122719576069 SUCCESS:12tests passed, 별도 wheel 설치 후 numerical equilibrium PASS. Native Rust와 전체 repo suite는NOT_RUN. Core blob912ab549ab71ee19a3717f7afd71800274eb0106/test4957f3cf62c115d7171a8d7c49ed9e771542e32a는 실제 실행한 바이트와 일치한다. Local runtime는 selected numerical package projection, full package assurance는 CI의 별도 증거다. Native subagent/independent-model review NOT_RUN.

## 재현·보존·다음

실제 checkout에서 OPENBLAS_NUM_THREADS=1 python -m pytest tests/nonperturbative/test_lapse_field.py -q. API는 from bianchi.nonperturbative.lapse_field import FieldGrid,LapseField,PeriodicLapse,stationary; LapseField(...,backend='python_oracle'). Old model/Strang/native routes는 교체하지 않는다.

PRESERVATION.json의42-file immutable ZIP에는 전체 Korean derivation/report/handoff,detailed DAG/contracts,all raw rows,complete science/saved validators,CAS,logs,figure,selected exact numerical source projection이 있다. Git의 현재 보고서는 요약이며 full archive byte identity를 주장하지 않는다. Science driver를 source inspection만을 위해 replay하지 않는다.

다음 BF3-E는 같은 lapse의 inverse transfer와 coordinate opacity를 유지하는 independent retarded local-source memory다. Finite collocation/interpolation과 continuum transfer를 동일시하지 않고 전체 초기 carrier를 보존한다. BF3-E는 이번에 실행하지 않았다. Generic metric/tilt,spectral validity,material/EFE feedback,native production,universal positivity/tail/long-time theorem은 별도 남은 의무다.
