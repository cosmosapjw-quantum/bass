# CE1-B: pressure 구적과 재구성 시간경로의 기하학 오차 예산

Status: COMPLETE_SCOPED_ANALYTIC_SOURCE_TIME_BUDGET. 상위 CE-1은 PARTIAL, DAG9/15, production_ready=false, merge_ready=false. 별도 child PR232. 원격 부모4eccdbb6af46eed54ca8bf1b0baa8bb8378b7f0a와 첨부 CE1-A17e8ce86은 서로 다른 구현/fixture다. 첨부 원본은 별도로 보존했고 덮어쓰거나 byte-identical이라고 선언하지 않았다.

실제 module은 bianchi.nonperturbative.einstein_error_budget이고 명시적 python_oracle만 허용한다. 수치 core commit9bd7a1839ef07b4056f38bc69d4d93f750c280d4의 계산 내용은 변경하지 않았다. 테스트-only 강화 후 commit0bfc3d45e9427901755238172b53a9db11ed3c34에서 actual repository CI와 installed-wheel 검증을 마쳤다. 이 보고서를 추가하는 후속 commit은 문서·결과·영수증만 추가한다.

## 물리·입력 계약

Signature(-,+,+,+), u=t/Tstar, ell=ln a, h=Tstar H, E,P=8piG Tstar^2/c^2 times energy density/pressure. Radiance 입력이라면 먼저 c로 나눈다. Lambda0, collisionless massless diagonal reflection-symmetric Bianchi I. ell'=h, h'=-theta h+P(ell). 초기 shear로 Hamiltonian constraint를 정하고 진화 중 projection/weight normalization/clipping을 하지 않는다. 모든 초기 h_i>=0인 expanding 영역에만 오차 비교를 적용한다.

F0=E0/(4pi)[1+c2 P2(qz)+ct(qx^2-qy^2)+c4 P4(qz)]라는 알려진4차 continuum 다항식이다. 구면전체 positivity를 z^2에 대한 quadratic minimum으로 검사한다. 임의의 샘플을 이 클래스라고 추정하지 않는다. Main E0=.9,coefficients(.6,.25,.2),shear(.2,-.13,-.07),u<=1,16x32angular/64RK4steps. 작은 진폭 전개나 물리적 multipole closure가 아니다.

## Pressure 구적 상계

b_i=exp(-2ell_i),V=exp(sum ell),r^2=sum b_i q_i^2이고 P_i=V^-1 integral F0*b_i*q_i^2/r dOmega다. m=(bmax+bmin)/2,z=1-r^2/m이면 |z|<=rho=tanh(maxell-minell)<1.

(1-z)^(-1/2)=sum_(k=0)^K c_k z^k+R_K,c_k=binom(2k,k)/4^k. 계수는 양수·감소하므로 |R_K|<=c_(K+1)rho^(K+1)/(1-rho).

F0 degree d=4이면 pressure 다항식 부분의 degree는 d+2+2K. 이것이2ntheta-1 이하이고 nphi보다 작으면 ideal GL×periodic-phi rule은 정확하다. 양의 적분과 구적합 각각에서 F0 q_i²의 mass는 P_i0이므로

|P_i-P_i,Q|<=2 P_i0 b_i/(V sqrt(m))*c_(K+1)rho^(K+1)/(1-rho).

경로 전체 ell box[L,U]에서는 rho<=tanh(maxU-minL),m>=.5(exp(-2maxU)+exp(-2minU)),b_i/V<=exp(-2L_i-sumL)을 사용한다. Fine-grid 차이나 표본 최대값으로 상계를 정의하지 않는다. GL4에서 P4가 node마다0이어도 알려진 continuum degree4를 버리지 않는다.

이는 Gauss 정확도와 binomial series를 이용해 직접 유도한 bound다. 기본 참고: NIST DLMF3.5 https://dlmf.nist.gov/3.5 ,4.6 https://dlmf.nist.gov/4.6 . 이 문헌이 이번 전체 계산의 machine certificate를 제공한다고 인용하지 않는다.

## 재구성 시간경로의 defect

RK4 states와 실제 endpoint RHS slopes에서 cubic Hermite 경로를 구성한다. Bernstein convex hull로 구간 전체 ell,h>=0와1~3차 derivative cap을 검사한다. r_ell=ell_tilde'-h_tilde,r_h=h_tilde'+theta_tilde*h_tilde-P_Q(ell_tilde). 각 panel을8개 subcell로 나누고 residual Taylor3차까지 계산한 뒤 analytic fourth-derivative remainder를 더해 모든 시각을 감싼다. Endpoint residual이나 sample maximum을 supremum이라고 부르지 않는다.

Pressure integrand exp(-sumell-2ell_i)*(sum q_j²exp(-2ell_j))^-1/2의 product/chain derivative bounds와 cubic의4차 미분0을 이용한다. 전체 계수와 증명은 불변 ZIP의 REPORT_KO.md에 있다. External CAS는 inverse-root4차 derivative 계수와 forced comparison ODE를 residual0으로 확인했다.

실제8step reconstructed path에서는 knot residual1.11e-16이지만 interior residual4.24655e-4다. Node에서만 검사하면 시간 defect를 놓친다. Endpoint 실제오차는 약4차이나 cubic reconstruction의 absolute residual envelope는 약3차로 감소하며 이를 숨기지 않는다.

## Source와 time의 분리 전파

x=||Delta ell||inf,y=||Delta h||inf에 대해 D+x<=y+dell,D+y<=4E0*x+eta_quad+dh. Source geometry derivative row absolute sum은4P_i<=4E0이고 expansion block log norm=max_i(h_i-theta)<=0이므로 성립한다. 각 panel의 positive2x2 affine comparison을 해석적으로 전파하고 (0,eta_quad),(dell,dh) contributions를 따로 합한다.

정확산술 부등식과 float64 평가는 별개다. GL node/weight, exp/tanh, polynomial range, Taylor coefficient의 rounding을 outward enclosure하지 않았다. 따라서 floating_point_certificate=false. 24x48의 source-only envelope가2.24e-18이어도 총 계산 정밀도가 그 값이라는 뜻은 아니다. Contracting sector와 임의 sampled distribution에는 적용하지 않는다.

## 실제 수치 결과

16x32에서8/16/32/64steps의 endpoint rate errors는2.70028836e-6/1.59787994e-7/9.67703190e-9/5.94841953e-10. Corresponding time rate envelopes는5.11104915e-4/6.15034672e-5/7.54789414e-6/9.35136833e-7. Fine source rate envelope2.39189486e-12,total9.35139225e-7. Fine ell error1.07700610e-9,total ell envelope4.78056401e-7. 상계는보수적이다.

64steps의 ntheta4/6/8/12/16/24 source rate envelopes는.0321130/.000293766/5.18675e-6/2.99142e-9/2.39189e-12/2.24047e-18. Time contribution은약9.35e-7이므로 각도만늘리면budget개선이멈춘다. Controller자체는아직구현하지않았다.

독립65digit source reference는 angular quadrature가 아니라 exact spherical monomial integral+36차 binomial series다. 세 시각에서15개pressure comparison을 수행했고 최대analytic tail1.66e-29. t=1의 coarse4x8pressure difference2.71767e-5,bound.0204842;16x32difference1.249e-16,bound1.30883e-11. 이고정밀경로도interval인증은아니다.

14unique tests PASS. 과학1회:9RK4 histories,2referenceIVPs,3high-precision source evaluations;time4/angular6행중16x32/64행은공유. Current/historicalscience replay0. 수치reference48x96DOP853는exactcontinuumtrajectory가아니다. Finalconstraint약7.90e-9이며이를강제로0으로만들지않았다.

## 검증·보존·제한

Actual CI40689344240/job122819847070 SUCCESS:14tests,parent AngularRadiation moment compatibility,installed-wheel numerical budget PASS. Core blobdd1f3a1aee3ce9ec6c2461f3e856322818795b1e,test98fc890eb3c520e986ed907902bae9ed3e028285는실행본과원격이일치한다. 기존full-repositoryRF00run40689017677은portablefailure/nativecancelled이며원인은이번에재조사하지않았다. 예상hash나policytest를바꾸지않는다.

단일검토에서interior-domain테스트가다른초기gate에서먼저실패할수있는약점을발견해validinitial/positiveendpoints/negativeinteriorfixture로교체했다. 수치core/results/gates는불변,science replay0. 문서writer의quoteparse실패도문자열만수정했고과학재실행은없다. 원기록보존.

S0/S1/S2와첨부원본은Drive전체byte readback,Dropboxproviderhash/size확인;DropboxfullbyteNOT_RUN. Git는actualcore/tests/workflow와요약dossier. Final ZIP은fullreport,validators,allrawrows/panelbudgets/patharrays,CAS,logs,figures,original/updatedDAG와selectedpackageprojection이며전체repo/wheel이아니다.

Reproduce scoped package tests: OPENBLAS_NUM_THREADS=1 python -m pytest tests/nonperturbative/test_einstein_error_budget.py -q. 저장검사는ZIP의validate_saved.py만사용하며verify_ce1b.py를임의replay하지않는다. NativeCE1B미구현,subagent/독립모델심사NOT_RUN. 다음은CE1-C의동일입력roundoff-awaretargetbudget만이며자동실행하지않는다.
