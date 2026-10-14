# BASS FA03-R7 / REI exact-reference-norm 인계

먼저 자신의 실제 HEAD, STATE, runtime receipt와 process/job 상태를 읽는다. 이 capsule의 최신 REI source snapshot은2026-10-14T11:44:19Z이고, STATE 안의 process 서술은20:21:17KST의 더 오래된 관찰이다. 읽은 시각과 process 관찰 시각을 혼동하지 않는다. 기존 supervisor/queue를 재시작하거나 science job을 중복 실행하지 않는다.

## BASS 이론 다음 작업

`manuscripts/R7_VALIDATION_KO.md`, `evidence/CERTIFICATE.json`, `contracts/DECISION.json`, `contracts/NEXT_LOOP.json`을 읽고 `python code/verify.py`로 저장된 evidence와 identity를 확인한다. 이것은 read-only이며36ray science를 다시 적분하지 않는다.

R7은 exact-decimal chi=.008,psi=.01,delta=.02의 GL3×12 finite detector에서24component 시간·반올림 오차를 닫았다. Parent R6 opacity-only remainder와 결합해 실제 archived RK4 polynomial도 |epsilon|<=.1에서 error<4.75e-7이다. Exact rational midpoint와 출력용 rounded decimal을 구분한다. Continuous cap error, observer derivative enclosure, empirical opacity error는 새로 인증하지 않았다.

다음 선택은 FA03-R8 결과 판정이다. 완료 R5/R6 및 새R7를 재생산하지 말고 finite-detector scope, exact midpoint 사용, 원 mathematical/numerical evidence를 연결해 채택/보류 claim을 판정한다. 원 I–VII,21/21,D9.1,SOURCE_CLOCKS,ABUNDANCE_MODEL을 변경하지 않는다. 새로운과학 문제는 명시적으로 선택되기 전 자동 시작하지 않는다.

## REI AX11 담당자

Owner의 `AX11_NEXT_RUN_CONTRACT.json`과 `next_run_001/RUN_BINDING.json`은 이미T1와4096MiB allocation을 준비했다. 이를 다시 만들지 않는다. 기존execution_authorized_now=false,baseline5완료/sharedslot/remote-staging 조건과 prepared output policy를 보존한다. 이 공급은 solver launch 허가가 아니다.

`manuscripts/REI_SUPPLIER_KO.md`와 `code/pl_metrics.py`를 소비한다. 기존1001점 통계는 유지하면서 원acceptedrows의 동일한ln(a) PL참조에 대해 추가 exact reference sup/L1/L2_squared를 계산할 수 있다. Adapter가 binary64 log(a)를 쓴다면각knot를Fraction.from_float로올리고좌표를LN_A_BINARY64로명시한다. PLina로대체하지않는다.

먼저HH68의 실제pair-bound source identity/semantic relation guard,HE51의source-specificnormalization·stitching 계약을 적용한다. Genericmetrichelper 자체는이scientificsourceadmission을대신하지않는다. Private raw outputs는publicGit에올리지않는다. `code/check_bridge.py`는parent의과거24행을읽는bounded예제이지최신fullhistoryconsumer가아니다.

UnknowntrueODEerror는null로남기고,3level/component/refinement/보간오차를source와coordinate별로분리한다. 합집합knotnorm은지정PL함수의연속sup를계산하지만참해의오차나physicalshear검출을인증하지않는다. CR/RCT/HH OFF 및 optionaltau-tail비차단을유지한다. CanonicalAX11완료·입력readiness는owner가실제결과로판정한다.
