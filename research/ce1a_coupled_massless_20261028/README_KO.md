# CE1-A: 무충돌 복사와 대각 Bianchi-I의 자기일관적 결합

COMPLETE_SCOPED_CONSTRAINT_AND_NONLINEAR_ERROR_COUPLED_PILOT. 실제 package는 bianchi.nonperturbative.einstein_vlasov이며 backend='python_oracle'를 명시한다. 검증된 코드 commit465cf9daaa8c720038d6d4cbf3e7ceea68d0ec33 이후의 이 closeout은 문서·증거 요약만 추가한다. 상위 CE-1은 PARTIAL, DAG9/15 유지다. Main/owner/부모 branch와 native-default는 변경하지 않는다.

## 물리 범위와 정규화

Signature(-,+,+,+), ds²=-c²dt²+Lstar² sum_i a_i² dx_i², Lambda=0. u=t/Tstar,ell_i=ln(a_i/a_i0),h_i=Tstar H_i,a_i0=1. rho는 에너지밀도이며 E=8piG*Tstar²*rho/c², P_i=8piG*Tstar²*p_i/c²이다. Conventional radiance는 먼저 c로 나누어 angular energy density로 바꾼다. 무충돌 질량 없는 입자, 좌표별 반사대칭인 양의 초기 angular energy measure dW를 사용한다. 전단/복사 진폭의 섭동 전개는 없지만 유한 angular quadrature와 ODE 오차는 남는다. Initial direct carrier는 무편광이다.

Canonical momentum 보존으로 p_i=e^-ell_i n0_i,r=|p|,V=exp(sum ell)에 대해
E=V^-1 integral r dW, P_i=V^-1 integral p_i²/r dW.
질량 없는 radial energy integral은 초기 dW에 정확히 포함된다. 여섯 metric 변수로 적분해도 전체 초기 dW가 source 평가에 남으므로 finite multipole/fluid closure가 아니다. 반사대칭은 모든 시각의 flux와 off-diagonal stress를0으로 만드는 충분조건이며 임의의 비대각 분포를 수용하지 않는다.

## 제약을 만족하는 초기자료와 전파

Tracefree shear s를 입력하면 hbar0=sqrt((E0+sum s²/2)/3),h_i0=hbar0+s_i다. 초기자료에서만 이 조건을 맞춘다.
Evolution: ell_i'=h_i, h_i'=-theta*h_i+P_i, theta=sum h_i.
C=sum_i<j h_i*h_j-E에 대해 dE/dell_j=-(E+P_j)로부터 C'=-2theta C, 즉 V²C=C(0)를 얻는다. 매 스텝 Hamiltonian projection, density/weight renormalization, clipping을 하지 않는다. 별도 spatial Einstein residual과 massless Ricci trace도 검사했다.

압력에만 진단 eta_i를 넣으면 C'=-2theta C+sum_i(theta-h_i)eta_i다. eta=10^-3 exp(-u)(1,-.4,-.6)를 넣은 실험에서 u=.8의 raw C=-2.9454742904666542e-5. V²C의 변화=-.0002120056660780211은 독립48점 시간구적=-.00021200566642776413과3.50e-13 차이다. 세 시각 최대 차이는5.46e-12. 이 압력 주입은 물리적 matter 모델이 아니라 검출용 오류다.

## 비선형 source-to-geometry 상계

R_ij=V^-1 integral p_i²p_j²/r³ dW라 하면 sum_j R_ij=P_i이고
partial_j P_i=-P_i-2delta_ij P_i+R_ij, sum_j|partial_j P_i|=4P_i.
초기 h_i>=0인 팽창 옥탄트에서 ell>=0,E<=E0,0<=h_i<=B=max(max h_i0,sqrt(E0))는 invariant region이다. h_i=0에서 P_i>=0, h_i=B에서 h_i'<=-B²+E0<=0이다.

d[-theta h]/dh=-theta I-h 1^T의 infinity logarithmic norm은 max_i(h_i-theta)<=0이다. 두 해의 오차 e_l=||delta ell||inf,e_h=||delta h||inf는 D+e_l<=e_h,D+e_h<=4Emax e_l+eta를 만족한다. 같은 초기 geometry, source mismatch upper bound eta, k=2sqrt(Emax)에 대해
e_l<=eta(cosh(ku)-1)/k², e_h<=eta*sinh(ku)/k.
이는 비선형 해 사이의 비교 부등식이지 진화의 선형화가 아니다. Kasner contraction control에는 이 영역의 정리를 적용하지 않는다.

두 positive initial angular measures의 TV가 알려지면 ell>=0에서 source mismatch<=TV다. Main 분포에 .08P4/(4pi)를 더한 경우 TV=.02284657925465665,u=.8의 실제(e_l,e_h)=(8.31420368e-6,2.04115508e-5),새 상계=(.00900991677,.02713680076). 단순 six-state Gronwall 상계6.80818463보다 작지만 여전히 보수적이다. .02/.04/.08의 모든 검사시각에서 만족했다. Fine-grid gap을 인증된 source bound로 쓰지 않으며 continuous/discrete singular measures의 TV가 작아진다고 가정하지 않는다. Floating-point IVP의 interval certificate는 아니다.

## 두 실제 결합 경로와 결과

CoupledHistory는 전체 초기 canonical-momentum 분포를 현재 metric에서 적분한다. DirectHistory는 기존 P8의 direction_rate/tensor_rate를 호출하며 방향,log angular Jacobian,physical3x3 carrier,Einstein geometry를 함께 진화한다. Direct가 reduced source를 호출하면 실패하도록 막은 테스트도 통과했다. 두 경로는 geometry equations,초기조건,구적,SciPy integrator를 공유하므로 독립모델심사로 세지 않는다.

주 분포 I0=[1+.65P2(n_z)+.4P4(n_z)+.25(n_x²-n_y²)]/(4pi),E0=1,shear(.16,-.04,-.12),u0..8,main grid12x24,17output times.
최대 metric-state 차이4.43e-12,energy7.96e-12,pressure4.22e-12,reduced constraint2.91e-12,direct constraint1.26e-11,flux1.20e-16,offdiag1.10e-17. 정확한 radiation-FLRW state 차이2.49e-12,Kasner vacuum2.20e-12. Tight ODE endpoint direct/reduced 차이3.05e-15.

20x40 angular reference 대비6x12/8x16/12x24 endpoint state 차이7.11e-8/1.06e-10/7.22e-16. 이는 empirical refinement이며20x40을 continuum exact라고 선언하지 않는다.

두 positive 분포1/(4pi)와[1+.6P4]/(4pi)는 초기 E/P/q와 초기 metric이 같다. u=.8의 delta h=(.000109774001952945,.0000675068752019614,-.000181913825384794). 최대1.81914e-4의 차이가 생긴다. 초기 stress만으로 전체 kinetic 초기자료를 대체할 수 없다는 사례다. Spatial averaging backreaction은 이번에 계산하지 않았다. P_i를 E/3로 강제한 control은 state를.02567575 바꾸고 C=-.00139689를 만들었다.

## 실제 검증, 비용, 남은 통합 문제

15 local targeted tests,actual repository CI40676017862/job122774500345,installed-wheel coupled numerical check PASS. Core/test Git blobs는 실행본과 일치한다. Science1회:reduced coupled IVP14,direct P8 IVP2,independent constraint quadrature3. Tests/CI는 별도. Current/old science replay0. Six exact CAS identities는0이며 CAS는 독립심사가 아니다.

현재 별도 RF00 workflow40676128349와 RF-BENCH40676128240는FAILURE다. 이 단위에서 근본원인을 재감사하지 않았으므로 부모의 실패 원인과 같다고 단정하지 않는다. Expected hash와 기존 policy는 변경하지 않았다. Native CE1-A미구현,native subagent/독립모델심사NOT_RUN,production_ready=false,merge_ready=false.

S1 Dropbox 최초 업로드FETCH_FAILED 후 destination NOT_FOUND를 확인했고,동일SHA의 fresh source를 한 번 재전달해 완료했다. 수치계산은 재실행하지 않았다. 현재 container/private Python probe 실패는 서비스 오류였지만 available Python runtime/subprocess로 계속했다.

## 보존과 재현

S0/S1/S2는 PRESERVATION.json에 기록했다. Git에는 실제 core/tests/workflow와 이 요약 dossier가 있다. 전체 한국어 보고서,상세 원본DAG와 변경본,source map,science driver,validate_saved.py,모든 raw rows,CAS,로그,두 그림,선택 numerical package projection은40파일 ZIP에 있다. ZIP은 전체 BASS repo나 wheel의 대체물이 아니다.

Repository: OPENBLAS_NUM_THREADS=1 python -m pytest tests/nonperturbative/test_einstein_vlasov.py -q
Archive: python validate_saved.py는 저장증거만 확인한다. verify_ce1a.py는 이미 raw output이 있으면 implicit replay를 거절한다.

문헌 배경은 Heinzle–Uggla gr-qc/0512031과 Lee–Nungesser–Tod1911.04937의 Bianchi-I Einstein–Vlasov construction이다. 후자의 small-anisotropy late-time 정리를 이번 finite-amplitude 전역 결과로 사용하지 않았다. Source derivatives/오차식/수치는 현재 유도·실행 결과이며 신규성 주장은 없다.

다음CE1-B_ONLY는 동일 채널의 continuous angular source 오차를 controlled bound와 연결해 source/time error budget을 분리한다. CE-1 원 의존관계를 보존하고 불필요한 atomic/cohort 입력을 collisionless 채널에 붙이지 않는다. 다음단위는 실행하지 않았다.
