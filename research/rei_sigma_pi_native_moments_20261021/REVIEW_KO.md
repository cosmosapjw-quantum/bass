# ACCEL02 독립 C9 심사

**판정: PASS — 동결 범위의 국소 수치적 동등성과 native 통합을 승인한다. 차단 결함이나 수정 요구는 없다.**

새 독립 심사자가 실제 C++/Python 소스, 기존 exact cache와 worker 연결부, 원시 수치 결과 및 실행 영수증을 한 차례 검토했다. 구현 코드는 수정하지 않았으며 컴파일·solver·검증 suite를 재실행하지 않았다. 요청된 심사 모델은 `gpt-6-astra`이고 실제 런타임 모델 telemetry는 제공되지 않아 관측값은 null로 기록했다.

## 승인 근거

- **동일 구적법:** 원래 96×32 점의 반사쌍마다 커널이 동일하다. 실제 `mu`, `mu²`, P2, 각도 가중치와 전체 분포 가중치의 대칭을 검사하고 원래 두 가중치를 한 번 더한다. 16점짜리 새 구적법으로 바꾸지 않았다.
- **수치 계산:** 세 모멘트의 Neumaier 보상합과 마지막 `s+c`가 올바르게 구현되었다. 컴파일 옵션은 fast-math와 FP contraction을 끈다. ctypes와 C ABI 형식도 일치한다. exact `(x,b)` cache는 native miss evaluator와 명시적으로 합성되며 모델별 입력 복사·불변 binding을 유지한다.
- **물리 부호·단위:** 고정 가중치에 대해 `∂x J0 = −3J0−J1`, `∂b J0 = −2J2`가 성립한다. LRS 수축은 `2sD`이며 `H³/κ_t` 단위의 일은 `2ΣΠ`이다. 실제 정규화 코드는 성분의 부호 있는 합과 단위 변환을 보존한다.
- **원시 결과 재계산:** 지정된 140점 집합이 정확히 일치하고 최대 에너지 기준 오차는 `3.0017696087628955e-16`으로 한계 `1.4210854715202004e-14` 이내다. 세 미분 잔차의 최대값은 `3.730718793634552e-12`로 `2e-9` 이내다. 5쌍×2 step의 초기·history·최종 20개 비교행 모두 기준을 통과했으며, 10개 trajectory의 기존 8개 gate도 원시 자료에서 다시 확인했다. 최대 signed Π_total 차이는 `1.1777890328403265e-20`, 정규화된 전체 tensor-work 차이는 `3.268686181550334e-24`다.
- **실행 연결:** 실제 소스 hash가 구현 실행 기록과 일치한다. worker manifest의 43개 파일 binding, 현재 library와 build receipt, 독립 재구성한 backend namespace가 모두 일치한다. 첫 worker는 한 case를 계산했고 두 번째 실행은 같은 receipt/result를 재사용했다. 기존 worker 9개 test는 저장된 로그에서 모두 통과했다.
- **기본 경로와 NCP 준비:** 완료 729건의 pending=0 분기는 build 검사·library load·job 생성 전에 no-work receipt를 만든다. 기본 exact-cache 경로와 native namespace는 구별된다. 문서의 target-local compile 및 plan/prepare/executor 명령은 실제 CLI와 일치하며, 기존 executor가 현재 가용 자원과 thread=1 정책을 적용한다.

## 승인 한계와 다음 실행

이번 승인은 지정된 유한 시험집합과 warm 2-step 연결 검사에 한정한다. 전역 반올림 오차한계, 시간·격자 수렴, 원래 64-step 729건의 대체, 성능 향상, NCP 실측 실행을 주장하지 않는다. 비-LRS·tilt·odd 분포·full EoR·full Qᵃ 역시 범위 밖이다. target에서의 새 build는 환경별 receipt와 namespace를 만들 수 있으며 이는 보수적 checkpoint 구분이지 물리 실패가 아니다.

**다음 단계는 Stage C 게시·백업과 NCP용 컴파일/실행 인계다. 추가 수정이나 심사 확장은 필요 없다.** 상세 판정, 검토한 소스 SHA256 및 근거 파일 SHA256은 `evidence/INDEPENDENT_REVIEW.json`에 기록했다.
