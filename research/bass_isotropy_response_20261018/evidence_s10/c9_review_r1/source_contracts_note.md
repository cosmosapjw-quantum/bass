# S10 C9 source contract specialist note

**판정: `PASS_SCOPED_SOURCE_REVIEW` — 검토한 변경 범위에서 구체적인 계약 위반을 발견하지 않았다.**

이 문서는 부모 `/root/science_reuse_and_review`의 한 번의 C9 검토 안에서 수행한 좁은 source 검토다. 별도 연구 주기나 review-of-review가 아니다. 부모가 전달한 고정 source commit은 `d5a173644f5c7c0dbe9eb8757dfc4ccad6c4f4c8`이다. 이 담당자는 로컬 source의 내용과 freeze manifest의 SHA256을 대조했으며 원격 commit/readback, 실제 timing 통계와 과학 RAW의 독립 재계산은 부모 담당이다.

새 compile, test 실행, benchmark, ODE 적분, 외부 검색, repo/source 수정은 **0회**다. 파일 읽기, 문자열·SHA256 대조와 이 note 작성만 수행했다. 기존 `tests_r1.log`의 release 11/11 통과 기록은 읽었으나 다시 실행하지 않았다.

## 직접 확인한 원본 관계

`s9_vigilode/src/lib.rs`의 현재 bytes는 보존한 `s10_optimization/provenance/S9_LIB_ORIGINAL.rs`와 완전히 같다. 양쪽 SHA256은 `204d3fa9dd4a5ed8400410ff1035c4771e11d6ff50d5267a3756a740cf9b731b`다.

`RUNNER_COPY_PROVENANCE.json`에 기록된 원본의 `projected_birth`, `validate_input`, `observe`, `run_and_run_inner` 네 구간을 실제 원본 bytes에서 다시 추출해 SHA256을 비교했고 네 개 모두 일치했다. `S9_RUNNER_EXTRACT.rs`에 선언된 **다섯 개의 문자열 치환만** 적용한 텍스트가 실제 `src/runner.rs` 전체와 정확히 같았다. 치환은 candidate entry point/mode 인자 전달 세 개와 MF/Small callback construction 두 개다.

따라서 P24 owner 호출, exact birth gate, 기존 stock 검증, 양의 donor transfer, event 연속성, right-bank output 교체, observation, segment/counter receipt, solver 설정과 실패 처리의 나머지 코드는 원본대로 보존되어 있다. `lib.rs::run_with_mode`의 `baseline`은 복사 runner 대신 원 `bass_s9_vigilode::run`을 직접 호출한다.

## Kernel과 cache

- `kernel.rs::OrderedSum::push/finish`는 원 S9 `sum`의 비교 분기, 보정항 덧셈과 마지막 `sum+correction` 순서를 그대로 쓴다. 채널 사이 실행을 interleave하지만 각 채널의 node 순서와 cohort 순서는 바뀌지 않는다.
- `scalar_terms`의 `a`, `c`, `r`, `n`, `dd` 및 `[w*r,w*n/r,w*dd]`는 원 `Cohort::moments`와 같은 괄호·곱셈/나눗셈 결합 순서다. prepared data는 불변 μ의 `m*m` 및 원 weight 복사다.
- cohort factor는 원 `energy_birth * exp(-4*(x-u))`를 유지한다. 이를 별도 `exp(-4x)*exp(4u)`로 분해하지 않았다. `FrozenBank`의 donor, RHS, Jacobian 및 explicit partial_t도 같은 식과 연산 순서다.
- `Evaluator`의 bank와 prepared fields는 private이며 bank를 소유한 immutable `Arc` lifetime에 묶여 있다. public constructor는 bank ownership을 취하고, crate 내부 `from_arc`는 fresh segment에서 사용된다. mutable bank reference는 노출하지 않는다.
- `Key`는 x/h/b/y의 네 `to_bits()` 값을 모두 보관한다. RHS와 JVP slot은 각각 최대 한 entry다. 각 조회는 정확한 key를 확인한 뒤 evaluation을 복제한다. 새 방향의 Jv는 매 호출 원 순서의 3-term Neumaier dot product로 계산하고 Jv 결과를 cache하지 않는다.
- `jvp`는 원본과 동일하게 invalid direction을 먼저 거부하고 point domain을 다음에 검사한다. `eval`은 cache lookup 전에 finite x/state와 h>0을 확인한다. 실패 evaluation은 `?`로 반환되어 store되지 않는다. 두 slot의 mutex는 별도 lock scope여서 역순 중첩 lock이 없다.
- 새 event segment는 새로운 bank clone, adapter 및 evaluator를 구성한다. 이전 evaluator의 slots가 다음 bank로 전달되는 경로가 없다.

## SIMD와 adapter

`moments`는 두 prepared 배열의 유효 길이 중 작은 값으로 bound를 정한다. `index+4<=count`일 때만 unaligned four-lane load를 하고, lane 0→3을 원 순서로 누적한 뒤 scalar tail을 처리한다. 이는 원 zip의 길이 의미도 보존한다.

실제 vector 함수는 AVX packed f64 add/sub/mul/div/sqrt를 사용하고 FMA 또는 approximate reciprocal/sqrt intrinsic을 사용하지 않는다. `avx2_terms`를 호출하는 backend는 x86_64에서 runtime AVX2 guard를 통과한 경우에만 선택된다. AVX2 guard가 실제 AVX instruction 요구보다 보수적이라는 comment도 정확하다. 다른 target 또는 강제 fallback에서는 scalar 경로다. 저장된 binary inspection은 해당 symbol에서 packed sqrt/div와 FMA mnemonic 부재를 보고한다. 이 사실을 vendor/upstream binary 전체의 FMA 부재로 넓히지 않는다.

`adapter.rs`는 원 state dimension/error conversion, MF RHS/JVP/Ft callback signature를 보존한다. `ClockProblem`은 `[h,b,y,x]`, x′=1, Jacobian의 네 번째 column=partial_t, 실패 시 NaN 출력이라는 원 동작을 그대로 유지한다.

`lib.rs::run_independent`는 새 local pool에서 independent input jobs만 처리한다. 입력 Vec의 indexed parallel iterator 결과를 Vec로 수집하며 inner angular reduction은 병렬화하지 않는다. `scientific_value`는 top-level `elapsed_seconds`만 제거한다. 과학 field를 삭제해 equality를 맞추는 경로는 없다.

## 재확인한 source 식별자

다음 8개 로컬 파일의 SHA256이 `SOURCE_MANIFEST.json`의 해당 항목과 일치했다.

| 파일 | SHA256 |
|---|---|
| `src/kernel.rs` | `fdfaa29c19e026bfec8d7a1852b0cb918f3c6e0a63ec3584b0c61d481ae7dd2e` |
| `src/adapter.rs` | `e03cbc6fabf98fcef27ea494f6fb5148030f5c054d0d4b29a4bb2cf550fa6cc7` |
| `src/runner.rs` | `93205a1912e4f8d63a175280ddb6e633e5a894d3776c226a53877d04929a1f80` |
| `src/lib.rs` | `e05e73b640cc04919c5bac6c40d8d1564a4a3bcae125f6f146eb05fae6397bb7` |
| `provenance/S9_LIB_ORIGINAL.rs` | `204d3fa9dd4a5ed8400410ff1035c4771e11d6ff50d5267a3756a740cf9b731b` |
| `provenance/S9_RUNNER_EXTRACT.rs` | `88c304b0d252e0ecb6034ba50815af45bb7cbd7e3aea8a56af98f3884556640e` |
| `provenance/RUNNER_CALLBACK_DIFF.patch` | `97c7d38997902f17d0dce3164d61cbdbbdb6cad78391790580e59d0275e5a5f1` |
| `tests/targeted.rs` | `654bd70b41514f355088dd41264ba7c377b38d852c2dcb757d6854346db11407` |

## 한계와 독립성

정적 source 검토와 현재 manifest 대조는 임의 compiler·hardware·입력 전체에 대한 bit identity 정리가 아니다. 실제 등록 workload와 C6 범위에서의 bit equality, timing binary/environment binding, 68개 science gate와 통계는 부모가 원 RAW에서 독립 확인해야 한다. 이 note는 성능 배율이나 새 물리 closure의 완료를 승인하지 않는다. 원 S9의 broader evidence는 재사용하며 continuum angular, P6, full native finite-bin/spectral history, 실제 owner feedback, REI production/full EoR/merge로 확대하지 않는다.

`physmath-research-loop` 1.3.0의 부모가 읽은 CODING_LOOP C9와 POLICY_INTEGRATION의 finite-review/최소검증 context를 상속하여 적용했다. 이번 검토는 그 한 pass의 source 전문 분담이며, 새로운 child나 검토 cycle을 만들지 않았다.
