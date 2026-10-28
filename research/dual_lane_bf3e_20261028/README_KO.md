# BF3-E: 정적 비균질 lapse의 독립 국소 source-memory

## 결과와 범위

COMPLETE_SCOPED_STATIC_LAPSE_SOURCE_MEMORY. 검증된 수치 코드 commit은60c1ebbb5ef68f8072bc689764f362d6c4df1e4d, 부모는 BF3-D PR226/aca22f4b7287b642d65caf2c820b681b76ab1309다. 실제 bianchi.nonperturbative.lapse_memory에 독립 source solver를 추가했다. 이 closeout은 문서·영수증만 추가하며 수치 코드, 테스트, tolerance, 부모 default/native 경로는 바꾸지 않는다. Merge하지 않는다.

서명(-,+,+,+), ds²=-N(x)²c²dt²+Lstar²dx_i², N=exp(epsilon cos x)>0, x는2pi주기, u=t/Tstar,cbar=cTstar/Lstar. 전자는 normal-rest cold Thomson bath, nu_star=n_e_star sigma_T c Tstar, coordinate rate kappa=N nu_star. 기하학과 opacity는 정적 prescribed 입력이므로 복사 문제는 선형이며, 작은 전단·lapse·복사 진폭 전개를 하지 않았다는 것과 비선형 Einstein 계를 풀었다는 것을 구별한다.

## 구성

Y=N^4 W, physical J=N^-4 EYE^T, scaled source S=N^4 M=L Y=int EYE^T dOmega. Local final-x source는 final-angle raw quadrature이며 global phase Jacobian을 곱하지 않는다. 부모와 동일한 Fourier/Legendre collocation에서

    A=-vx D_x-vmu D_mu-diag(kappa),
    vx=cbar N mu, vmu=-cbar N'(1-mu²),
    B S=(3kappa/8pi) E^T S E,
    Y'=A Y+B S,
    S(u)=L exp(uA)Y_initial+int_0^u L exp((u-s)A)B S(s) ds.

A에는 radiation source/history가 들어가지 않는다. B,L도 직접 screen/구적으로 구성하며 solver는 부모 radiation rhs/direct/split/gain을 호출하지 않는다. 초기 전체 carrier와 source-null 성분을 유지한다. Physical-source kernel에는 좌우 N^4 변환이 필요하다.

시간 panel의 source를0,1/2,1에서 이차 보간하고 h int exp[hA(r-v)]L_j(v)dv를 augmented block exponential로 정확히 계산한다. A^-1 또는 cumulative fundamental inverse를 쓰지 않는다. 두 미지 source에 대한18nx 실수 선형계를 풀며 전체 carrier/endpoints는 저장한다. Dense reference이고 메모리·속도 우위나9상태Markov closure가 아니다.

Continuum inverse-ray attenuation/remap과 finite collocation exponential은 같다고 가정하지 않았다. 별도 inverse-ray kernel action에서 retarded x,mu,screen과 경로 opacity를 사용해 격자별 차이를 측정했다. Static 계수의 time-lag convolution 구조를 시변 metric에 외삽하지 않는다.

## 실제 과학 검증

주 fixture: epsilon=.55,cbar1,u<=.4,nx17,nmu10,nphi8,nu_star=1.1+.3sinx. 매끄러운 meridional IQUV field. Panels8/16/32/64의 physical-source endpoint 차이는2.6214104221e-9,1.6356627164e-10,1.0218714763e-11,6.3948846218e-13. Physical-carrier 차이는1.4713714691e-9,9.2081564596e-11,5.7527316244e-12,3.5560443479e-13. 처음 두 source 차수4.0023961/4.0005896. 최대panel condition1.06528. Same-grid agreement는 continuum 오차상계가 아니다.

별도640x640 full-generator exponential과 memory source 차이2.91323e-13. 이 full matrix는 부모 RHS basis로 구성했으므로 독립 시간표현이지 독립 물리모델 심사는 아니다. 부모Strang64/direct source차이2.71426e-6은 별도2차 remap/time 오차로 기록한다. Stationary Y error1.19904e-14; constant nonunit lapse collision error4.44e-15; wrong clock차이.0138848.

Continuum inverse-ray kernel action의 joint(nx,nmu)=(7,6),(13,10),(21,14) 차이1.34542e-3,1.54640e-5,1.22146e-8. 잘못된globalJacobian은 fine에서도.0501900 차이를 만든다. 이는 joint refinement의 kernel-action 검사이지 전체해 인증이 아니다. Spatial solution 비교는 x=0에서만 기록했고 angular 비교는 별도다.

초기 scaled intensity .1cosx P4(mu)의 physical source는1.68e-16이하. u=.4,x0의direct/memory Mxx는-.00038573529502942115/-.00038573529502525944. Initial-.00031772248377597196,gain-.00006801281124928747. Signed-response 검사이며 두 양의 초기장의 별도 paired evolution은 실행하지 않았다.

Global Killing 상대변화1.55431e-14와 달리 주격자의 국소 energy residual은3.39199e-5다. 전역 상쇄를 국소정확도로 승격하지 않는다. Off-grid reconstructed source2.79599e-12와 source polynomial2.58667e-9도 구별한다. Clipping/재정규화 없이 기록했다.

과학캠페인1회,memory15,direct3,Strang1,640행렬지수1,실제inverse-rayIVP4(추가kernel3+Strang내부1). Current/historical science replay0. 테스트·자동CI 실행은 별도다. CAS는 scalar panel의h4까지 일치와 weight/divergence 항등식을 확인했으며 독립모델심사가 아니다.

## 테스트와 저장소 CI를 구별

신규13개 고유 테스트는 로컬과 hosted CI40667431443/job122745367879에서 통과했다. 별도 설치 wheel의 source-memory 평형 수치검사도 PASS. Core blob5ff27159e919a8ef7327bc6c8c7a75b7ec87db93와 test blob271d8459884683a68c5af598c8c66d6c61632636은 실행본과 원격 readback이 같다.

그러나 별도 기존 RF00 run40667473221은 FAILURE다. Portable62pass/2skip/1fail은 부모부터 존재한 root runtime export와 exact __all__ 기대값 충돌이다. Native job은 기존Rust134tests,fmt/clippy,wheel build/install을 통과했으나 Pythonpolicy86pass/1fail이며 runtime_plan_warm_construct의 registered digest가 실제 repeatable output과 다르다. 후자의 root cause는 미해결이다. REPOSITORY_CI_STATUS.json에 보존했으며 expectedhash/정책/부모코드를 바꾸지 않았다. 새BF3E native는 구현·실행하지 않았고 전체repo CI PASS 또는 merge-ready를 주장하지 않는다.

## 진행·재현·보존

BF3-C/D/E가 선택된 static periodic lapse의 characteristic/local collision/independent memory 비교를 닫았다. BF-3는 이 범위에서 COMPLETE_SCOPED, upper9/15로 집계한다. 원래15nodes/edges는 유지하고S0/S1/S2를 새노드로 세지 않는다. Generic metric,fullfrequency,비축대칭수렴,Einstein/material feedback,native,positivity/tail 정리는 미완료다. Native subagent/독립모델심사NOT_RUN,production_ready=false.

    OPENBLAS_NUM_THREADS=1 python -m pytest tests/nonperturbative/test_lapse_memory.py -q

전체 불변 ZIP에서는 PYTHONPATH=package python -m pytest tests/test_lapse_memory.py -q 및 python validate_saved.py를 사용한다. verify_bf3e.py는 새 과학캠페인이므로 저장증거 확인만을 위해 실행하지 않는다. ZIP의 source projection은 전체repo/wheel 대체물이 아니다. Git은 핵심 실행코드·테스트·요약문서, ZIP은 상세유도·검증기·모든행·CAS·로그·그림·상세DAG를 보존한다.

PRESERVATION.json의 final fc095394 archive가 현재 authority다. 초기5a81613e seal도 보존하되, 최종판은 추가로 확인된 기존CI실패와 semantic-only CI excerpt를 명시한다. 과학 원시값·core·tests·gate는 바이트가 같다.

다음은CE1-A 후보만 유지한다: collisionless homogeneousBianchi-I massless radiation의 constraint-admissible initialdata와source-to-geometry오차전파를 먼저 구성한 뒤 그 범위의 최소coupled pilot. CE-1/BF-4는 미완료이며 자동실행하지 않는다. 기존 repository/native 정책실패는 별도owner범위의 통합의무로 남는다.
