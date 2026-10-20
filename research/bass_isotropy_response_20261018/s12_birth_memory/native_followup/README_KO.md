# S12: S8의 한 수치 실패에 대한 native 후속 코드

**코드 준비 상태이며 실제 native history는 아직 실행하지 않았다.** 현 NCP 연결은 월 사용 한도 때문에 차단되어 있다. 이 디렉터리의 존재, source manifest, compile-only 통과는 실행 receipt 또는 과학 통과를 대신하지 않는다. 실제 새 실행의 source commit은 상위 S12 게시 receipt와 ready-job batch가 전달한다.

대상은 `b9_n64_P2P4` 한 행이다. 기존 18행 campaign의 17개 완료 사례는 호출하지 않는다. 기존 실패 raw에 complete prefix bank가 없으므로 초기 상태부터 진행하는 한 번의 새 수선 시도이며 checkpoint resume가 아니다. 고정된 dispatch는 birth0–10 `legacy_P24`, birth11–15 `S11_P24`다. 완료되지 않았던 suffix에만 simultaneous P24를 연결한다. 각 birth가 만들어진 뒤에는 weights와 native state를 그대로 동결한다.

## 입력과 코드 권위

- [CONTRACT.json](CONTRACT.json): 한 case, exact moment gate, 기존 native gates, 자원 상한 및 비주장 범위.
- [native_followup.rs](native_followup.rs): 원 S8 probe의 작은 변경본. [PATCH_FROM_S8.diff](PATCH_FROM_S8.diff)에 전체 차이를 남겼다. 기존 테스트 모듈은 새 작업에 가져오지 않았으며 옛 검사를 다시 실행하지 않는다.
- `balance.rs`, `balance_p24.rs`, `native_adapter.rs`: 고정 원본 bytes. Prefix와 native source owner의 수치 연산은 수정하지 않았다.
- [s11_projector.rs](s11_projector.rs): source `7fb9b83cba01d37ce4cabbc4772527710601cd96`에서 사용된 완료 S11 projector의 그대로인 사본. order4와 명시적 새 isotropic birth 선언만 호출한다.
- [native_owner_manifest.json](native_owner_manifest.json): original REI owner `0e25846433170d0f420c4cda44a0bedbf02cd177`의 57개 소스, 합계614,313 bytes. 원 owner를 고치거나 다른 branch로 대체하지 않는다.
- [ORIGINAL_S8_FAILURE.json](inputs/ORIGINAL_S8_FAILURE.json): 그대로 보존한 원 실패 입력. [BASELINE_IDENTITY.json](inputs/BASELINE_IDENTITY.json)은 이미 완료된 S8 `b9_n64_prior`의 old32 관측값과 spectral digest를 read-only로 추출한 작은 입력이다. 원 gzip/전체 raw SHA256를 함께 기록했다.
- [SOURCE_MANIFEST.json](SOURCE_MANIFEST.json): 실행에 필요한 모든 파일의 bytes/SHA256/Git blob. manifest 자체의 신원은 containing Git source commit과 실행 receipt가 제공한다.

## 실행과 검증 경로

[run.py](run.py)는 Python 표준 라이브러리만 사용한다. Root의 게시된 NCP ready job이 실제 고정 `--source-commit`과 새 `--out`을 인자로 전달한다. 사용자가 과거 파일이나 사전 명령을 제공할 필요가 없다.

Runner는 source manifest와 모든 runtime 파일을 해당 Git commit의 전체 원격 bytes와 대조한 후, 고정 REI owner를 자동으로 materialize한다. owner의 파일별 크기·SHA256·Git blob을 검사하며 archive를 다운로드하거나 기존 owner 작업을 덮어쓰지 않는다. 이미 검증 가능한 owner source가 있으면 `--owner-root`를 통해 읽기 전용으로 재사용할 수 있다. 그 다음 pinned owner rlib와 새 probe를 `rustc --edition=2021 -O -C codegen-units=1`로 빌드하고, 생성한 정확히 한 행의 CASES.csv만 실행한다.

`--verify-only`는 source/input 확인만, `--compile-only`는 새 probe까지 compile만 수행한다. 두 모드는 `native_histories_executed=0`과 각각의 상태를 남긴다. 실제 case 실행은 raw·stdout/stderr·명령·exit code·source binding·compiled SHA256·owner 재검증·RSS·disk·elapsed를 create-only receipt에 묶는다. numerical failure row 뒤에 binary completion marker가 있어도 과학 성공으로 취급하지 않는다. 분석 실패·source 변경·nonzero exit는 wrapper nonzero로 끝난다.

[validate.py](validate.py)는 projector나 history를 호출하지 않는 별도 observer다. 저장된 binary64의 Fraction norm/P2/P4 잔차를 원 gate `3/10^15`와 비교하고, 각 birth의 source frame·prior Jacobian·positivity·reflection·source amount·native inventories·old32 전체 bit digest를 확인한다. 원 native ledger `1e-11`, R/D kernel `3e-14`, per-H continuity `1e-11`도 유지한다. GL128/256 비교는 기존의 제한된 angular reference control이며, 새 표준 라이브러리 observer의 recurrence로 계산한다. 이는 evolving reactive/full spectral convergence 증거가 아니다.

`A=DeltaP_new/U_new`의 continuum 오차 `1e-6` 목표는 별도 diagnostic이다. Native integrity가 통과하고 n64 angular target이 실패하면 그 두 사실을 함께 기록한다. 원 n256 finest-grid admission을 다시 발급하지 않는다. 기존 anisotropic old32 block과 새64 block은 분리해 보존하며 remesh·초기화·기존 weights 재가중은 없다.

## 자원 및 재개 경계

한 native process, owner 다운로드 최대4 worker, 모든 내부 수치 thread1을 사용한다. runner는 실제 affinity/cgroup·가용 메모리를 확인하고 child address-space를 최대4 GiB로 제한한다. task disk4 GiB, hard wall limit1800초 안에서 1740초 guard를 사용한다. 상위 NCP scheduler가 전체 batch의 RAM/CPU 예약을 담당하며 기존 owner process를 종료하거나 바꾸지 않는다. 실패·timeout에서 자동으로 같은 과학 작업을 반복하지 않는다.

Wrapper가 SIGTERM 또는 SIGINT를 받으면 자신이 만든 현재 child process group에만 TERM을 보내고 최대0.75초 기다린 뒤 KILL을 보낸다. 마지막 reap 대기는 최대0.15초다. 중단의 실제 signal·명령·소유 child group·cleanup 결과를 `INTERRUPTION.json`에 먼저 보존하며, 정상적인 unwind가 가능하면 최종 receipt에도 `INTERRUPTED`와 exit code를 남긴다. 외부 scheduler의2초 grace 또는 강제 종료 때문에 최종 receipt가 없어도 별도 중단 기록은 과학 완료로 해석하지 않는다.

이 후속이 실행되어 native 16 births와 ledger를 통과하더라도 actual MD14 normalization/native Einstein shared-Q, evolving reactive finite-bin spectral history, full EoR 또는 production 완료로 확대하지 않는다. 원 실패와 완료 증거는 그대로 남는다.
