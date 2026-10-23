# G1A 결과: 양의 운동론 측도와 일반 Bianchi 배경의 실제 결합

2026-10-23 KST. 부모는 BASS PR182 df2f5c78d49ea27b3d48fd2aaebb4add9f2d7f6e다.
이번에는 게시 복구가 아니라 새로운 유도, 구현, 유한 계산을 수행했다.
판정은 **FINITE_COLLISIONLESS_G1A_SCOPED**다. 일반 smooth-distribution 수렴,
충돌/방출/원자망 에너지 교환, production 승인은 별도 의무다.

## 무엇이 추가됐는가

기존 core.py는 그대로 두고, 기하학에서 개별 운동량과 양의 가중치를 진화시키고
그 모멘트가 다시 기하학에 작용하는 CoupledPackets를 구현했다. 각 sector의
rho, flux, pressure, pi를 따로 보존한다. 상태는 기존 24변수 core와 두 sector의
12packet 운동량36개, logweight12개를 합친72차원이다. 전체 비대각 전단과 n을
유지하고 회전프레임을 지원한다. H로 나누지 않는다.

핵심 유도는 THEORY.md에 있다. E=sqrt(m^2+k^2), prime=d/d(ct/L)에서

    k' = -h k - sigma k + R cross k
         + ((a.k)k - a k^2 - k cross(n k))/E,
    (log w)' = -3h + 2a.k/E.

여기서 a는 Class-B 공간 구조벡터이지 법선 congruence의 가속도가 아니다.
Class B에서 마지막 가중치 항을 빼면 에너지·운동량 moment 보존이 틀린다.
Wolfram에서 momentum divergence, 에너지 moment, 운동량 moment의 정확한
상징 잔차 {0,0,{0,0,0}}을 실제 얻었다. 이것은 해당 국소 항등식의 검산이지
전역 Einstein-Vlasov 정칙성이나 연속분포 오차의 증명이 아니다.

## 실제 계산과 수치

| 항목 | 실제 근거 |
|---|---|
| 새 pytest | 최초8그룹 PASS; donor-domain 보강 후 영향2그룹 PASS. 고유9그룹 |
| 초기 RED | implementation 파일이 없는 collection error; 행동 반례와 별도로 보존 |
| 독립 형태의 Koszul 계산 | 8기하 배위, 동일 저자의 별도 전개 |
| moment 보존 | 16무작위 ensemble, massive/massless 혼합 |
| local boost | beta=0,1e-8,.3,.8, tensor 변환/역변환 및 weight-Jacobian mutation |
| 원 freestream 직접 호출 | 6개 같은-node 상태의 rho/p/pi 비교 |
| 추가 실제 FD96 순간 검사 | 55296nodes씩6배위, 최대 scaled 보존 잔차1.887379141862766e-15 |
| 새 IVP | 12family nominal +3tight +1rotating +1IX turnaround +1wrong-weight =18 |
| 정상 물리 이력 | 17개, 각각101저장시각 |
| intentional negative control | 잘못된 Class-B 가중치1개 |
| 완료된 과거 캠페인 재실행 | 0 |
| 새 그림 | 저장 데이터에서 PNG/SVG3쌍 및 실제 CSV |

정상17이력의 최대 scaled core constraint는1.0746284409072745e-10,
packet moment로 재계산한 constraint는6.062824783526302e-11,
독립 rho/flux와 packet moment 차이는6.493404013806587e-10이다.
동결 기준은 모두2e-8이다. 마지막 수치는 원시 상대오차가 아니라
|difference|/(1+|packet moment|)의 최대다.

V/VIII/exceptional VI의 default/tight 전체 상태 비교는 각각
1.6795017688898806e-11,1.5306858559824444e-11,2.5585868072273764e-11이다.
회전하는 V와 별도 비회전 tight 이력을 시간의존 SO(3)로 대조한 최대 차이는
9.707538521980071e-14다. 기본 DOP853 rtol=2e-10,atol=2e-12,max_step=.05;
tight는2e-12,2e-14다. 시간창은 tau=[0,1.5]다.

새로운 닫힌 massive+massless 무충돌 혼합물은 h=.2에서 시작해
h=-5.945148961127839로 끝났고101점 중81점이 수축 구간이다. 이전 완전유체
turnaround 계산을 재실행한 것이 아니다. 6방향 초기 모멘트의 등방성과 분포
전체의 SO(3) 등방성도 동일시하지 않는다.

18적분 전체 측정시간5.473123s는 이번 공유 sandbox/작은 finite model의
실행시간 기록이다. 통제된 speedup/55k-node IVP 성능/production 처리량이 아니다.

## 가장 중요한 반례: constraint만 통과해도 kinetic closure가 틀릴 수 있다

일부러 (logw)'=-3h로 바꾼 V 대조군에서

- core constraint 최대4.890066884465813e-12;
- packet-derived constraint 최대0.007950929928365411;
- packet/core rho·flux 불일치 최대0.013635715827791783.

core는 자신의 rho와 flux를 보존식으로 따로 적분하므로, 외부 p/pi와 함께
Einstein constraint를 유지하면서도 microscopic carrier와 어긋날 수 있다.
이것을 core 자체의 오류로 분류하지 않았다. **constraint gate와
kinetic-to-ledger identity gate를 함께 유지해야 한다**는 구체적 반례다.
figures/closure_mismatch.png는 이 차이를 직접 보여준다.

## donor 재사용과 최신 병렬 결과

부모 core와 원 freestream은 각각 exact SHA256/Git blob 일치로 재사용했다.
PR168의 finite-source 정규화 및 diagonal initialization domain을 유지하고,
PR170의 LRS source-age 경로를 일반 방출 closure로 승격하지 않았다.
이번에 발견한 HE37 PR90과 REC LINE01 PR128은 각각 전자 STF rate와 detached
line injection의 범위로만 조사했다. 그 코드를 새 물리 closure에 합치지 않았다.

이번 조사는 기존 census를 재사용한 제한된 최신 PR 변화 조사다. 모든 branch,
대화 전문, 모든 provider 파일을 새로 전수 읽었다고 주장하지 않는다.

FD96 원본은 실제 첨부 archive의 파일을 live Git blob과 대조해 복구했다.
55296node의 source moment와 국소 derivative를 검증했지만, 이번18이력은
12packet의 별도 finite-measure 모형이다. 이를 FD96 smooth-source cosmological
convergence나 관측 CMB 예측으로 바꾸지 않는다. 질량0 FD source도 실제 Planck
photon spectrum과 별개다.

## 감사, 실패와 남은 범위

PHYS-MATH 검토 후 PHYS-MATH-CODE 검토를 직렬 수행했고 실제 세 그림을 읽었다.
새 독립 subagent reviewer는 NOT_RUN이다. Wolfram CAS와 explicit Koszul 경로는
서로 다른 계산 검산이지만 독립 모델 저자의 심사로 세지 않는다.
원 collection RED, 렌더 전 directory PermissionError, 잘못 옮긴 upload poll token
오류를 별도 보존했다. directory만 수리했으며 물리식/허용오차 변경은 없다.
초기 그림 실패는 생성된 그림0개이며, 수리 후 실제 성공 render는1회/3쌍이다.

양의 압력·우세에너지 부등식은 finite positive sum에서 직접 유도된다. 전역
정칙성, 부드러운 분포의 구적오차, beta->1의 conditioning, 충돌/방출 연산자,
thermal/gas/emitter four-force, production/restart는 미완료다.

다음은 G1B: positive smooth-source quadrature를 고정하고 radial/angular/time
refinement를 서로 분리한 curved Bianchi control이다. 먼저 IVP가 아닌 frozen-state
shell과 source-tail 계약을 고정하고, 새 요구만 계산한다. 이번18이력과 부모
캠페인을 다시 돌리는 것은 다음 단계가 아니다.
