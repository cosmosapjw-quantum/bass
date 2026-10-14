# FA03-R7 중단 복구와 동시 R7 결과 연결

2026-10-14, Asia/Seoul. 이 문서는 완료된 R7의 복구·교차연결 증보다. 새 R8 실행, 독립 외부심사 또는 chemistry/CAS producer 재실행이 아니다.

## 복원한 두 과학 산출물

본 스레드 PR147 원 과학 commit은 `d37554d19a08d22e8f6e7675efaf14d5d73602ff`, archive SHA256은 `551ca3cd2f8679fcf5bbe4b0885176147c77e232def6c5606622a6364ea987f6`다. 1,631,909 bytes,135members/134payloads. 이번에는 Google Drive object `1_PhopBCHNxk6yhr9gLDjWsS4brqJXUqg`에서 실제 복원해 SHA256·CRC·저장된2304셀 residual의 exact assembly를 확인했다. 이전 작업의 Dropbox 복원성공과 이번 Drive 복원성공은 별도의 사건이다.

동시 스레드 PR146은 `3e612547a5e54f48aa930a16778b6b656f4671ad`, archive SHA256 `5fbdc60f4d614e7c71378b043081469aced34d713cd33108f34b96f26ed99fc1`이다.523,577bytes,124members/123payloads. 중단 이전에 materialize된 원본이 현재 runtime에 남아 있었고, 이번에 SHA256·CRC와 저장된36ray/24component interval의 exact assembly를 확인했다. 이 복구에서 해당 science를 다시 적분한 것은 아니다.

두 원본 archive는 변경하지 않았다. 공통 parent R6 SHA256은 `c040514105fa856b05a8792a628e441a2ad73c991cc253b94b7646425d8bb0e8`이다. 같은 source,IC,clock,observer(chi=1/125,psi=1/100),delta=1/50,exactGL3x12 양의36ray detector와 continuous energy moment를 사용한다. 원 b453 family와 source-clock/abundance lock을 유지한다. Bytes가 같은 결과가 아니고 같은 수학적 관측량을 서로 다른 근사/상계로 계산한 결과다.

## 실제 exact-rational 교차확인

PR147은64-step 고정cubic의 whole-cell residual과 contractive six-state cascade로 계수오차를 감쌌다. PR146은32-step20차 intervalTaylor+Cauchy tail로 정확해의24성분 구간을 감쌌다. PR146의4성분(F11,F22,ReF12,ImF12)을 PR147의Stokes(I,Q,U,V)로 변환할 때 I=F11+F22,Q=F11-F22,U=2ReF12,V=-2ImF12를 쓴다.

`compare_r7_enclosures.py`의24성분 변환과6trace-ball 포함관계는 모두 exact Fraction 비교로 충족됐다. 즉 PR146의 전체 component box가 PR147의 각 forward-error ball 안에 들어온다. 표본 중심값만 비교한 것이 아니다. 이 계산은 저장된 두certificate의 정합성을 확인하며, 두certificate에 공통인 물리전제나 interval라이브러리를 외부 독립적으로 인증하지 않는다.

PR146의 보존된 enclosure를 재사용하면 PR147의 **그대로인** 고정reference polynomial에 대한 coefficient error를 추가로 제한할 수 있다. E0,E1,E2를 이 reference와 peerbox의 trace-norm 거리상계라 하면, exact-rational로

    E0 + .1 E1 + .005 E2 < 7.361e-12,
    E0 + .1 E1 + .005 E2 + 926402349807/1953125000000000000
        < 4.75e-7.

직접 계산한 마지막 유리수의 decimal display는4.743253633745658e-7이다. 분자·분모는 `PEER_COMPATIBILITY.json`에 보존했다. 원PR147의 자체 residual기반9.313e-9/4.84e-7 결과는 그대로 유지한다. 더 작은 bound는 **PR146 enclosure를 추가로 소비한 결과**이며 새 독립certificate나 PR147이 처음부터 낸 값으로 소급하지 않는다. PR146의exact midpoint와 PR147의기존RK4 reference도 교체하지 않는다.

양쪽 모두 continuous cap quadrature error,observer-derivative numerical enclosure,empirical atomic/calibration error는 null이다. 위4.75e-7은 fixed36ray exact model의 opacity-only |epsilon|<=.1에 대한 결과다. 물리intensity에는 원 `c t_o E_*^2 j_*(e_+-e_-)`를 적용한다.

## REI 인계에서의 상보성

PR147의 `milestones.py`는 주어진 continuous error envelope에서 first-passage bracket을 제공한다. 완료된ZERO의실제312238행을읽어0.1/0.5/0.9의참조crossing을추출한근거도원capsule에보존돼있다. PR146의 `pl_metrics.py`는 같은ln(a) PLreference의merged-knot sup/L1/L2_squared를 계산한다. 서로 다른 도구이며 한쪽을 다른 쪽의trueODE오차로 부르지 않는다.

21:06:11KST의실제read에서ZERO는owner-scoped완료,MINUS는accepted-step resource-stop의partial review완료,HALF_PLUS는실제PID970521이실행중이었다. 기존observerPID811686도살아있었다. AX11/T1과AX12variant준비는이미owner가완료했으며실제실행은pending이다. 기존supervisor를재시작하거나HALF_MINUS/refinement를중복실행하지않았다. 이후상태는최종영수증의별도timestamp만권위가있다.

## 다음 실행점

다음 선택은FA03-R8이며미실행이다. 두R7의동일target/서로다른certificate와위compatibility를읽어단일claim registry에서범위에맞게판정한다. 완료한R5/R6/R7 producer를다시돌리지않는다. 현재milestone/helper준비가canonicalAX11의실제signed-family/refinement입력을만들지는않는다.

재현: 두원archive를같은부모디렉터리에풀고이closeout폴더를그옆에둔뒤 `python closeout/compare_r7_enclosures.py`를실행한다. 과학솔버나네트워크를사용하지않는다. 원capsule검증은각README의read-only명령을쓴다.
