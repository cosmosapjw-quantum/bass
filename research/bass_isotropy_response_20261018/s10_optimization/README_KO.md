# S10 opt-in callback 최적화 crate

현재 상태는 **source 작성 완료, compile/test/benchmark NOT_RUN**이다. 원 S9의 scientific result를 새 성능 결과로 사용하지 않는다. source/prereg 게시와 cloud readback 뒤 parent가 실행을 지시한다.

이 crate는 BASS S9 source `4b30957cb008aad8019bb1a673937fc67bd017e8`와 결과 `a40311796f9aac5ea5e0e58c630bee2a78443353`를 기준으로 한다. 고정 VigilODE `a21d573980f66fe02891bd216153443b5352f921`, REI owner `0e25846433170d0f420c4cda44a0bedbf02cd177` 및 원 P24 owner를 수정하지 않는다.

## 모드와 API

| Mode 문자열 | solver callback 경로 |
|---|---|
| `baseline` | 원 S9 `FrozenBank::eval`, `FrozenBank::jvp`, `run(input)` 직접 호출 |
| `stream` | 원 term 식과 ray/cohort 순서의 세 Neumaier accumulator |
| `prepared` | stream + immutable `mu²`/alpha SoA |
| `cache` | prepared + RHS/Ft slot과 JVP-base slot을 분리한 bounded cache |
| `simd` | prepared + AVX2 lane arithmetic, cache 없음 |
| `simd_cache` | simd + 동일 bounded cache |

`Evaluator::new(FrozenBank,Mode)`는 diagnostics가 꺼진 evaluator다. `with_diagnostics`는 counter를 켜며 `counters()`로 읽는다. `with_scalar_fallback`은 SIMD 모드도 scalar fallback에서 확인할 수 있게 한다. `backend()`는 `Scalar` 또는 `Avx2`다.

```rust
let evaluator = Evaluator::new(bank, Mode::Cache);
let evaluation = evaluator.eval(x, [h, b, y])?;
let jvp = evaluator.jvp(x, [h, b, y], direction)?;
let receipt = run_with_mode(input, Mode::Cache);
```

`run_independent(Vec<Input>,Mode,workers)`는 workers1/2/4만 허용한다. 명시적 local Rayon pool과 ordered collect를 사용하며 각 history의 bank/cache는 독립이다. history 내부 ray/cohort reduction을 병렬화하지 않는다.

`scientific_value(&RunReceipt)`는 `elapsed_seconds`만 제거한다. `scientific_bytes`는 이를 canonical JSON bytes로 직렬화한다. input, observations, events, segments/driver counters, final_cohorts, failure/pending_birth는 모두 비교에 남는다. signed zero도 byte 비교에 남는다.

## 정확한 변경 표면

후보의 full run은 원 `run_inner`에서 두 callback adapter 생성부만 바꾼 최소 복사본이다. mode 전달을 포함하여 exact diff에는5개 변경만 있다. 원 private helper `projected_birth`도 failure/pending-candidate 증거를 유지하기 위해 그대로 발췌했다. `provenance/S9_LIB_ORIGINAL.rs`, `S9_RUNNER_EXTRACT.rs`, `RUNNER_CALLBACK_DIFF.patch`, `RUNNER_COPY_PROVENANCE.json`에서 원 SHA와 발췌 범위를 확인한다.

**administrative observe와 birth pre/post eval은 원 S9 경로**를 유지한다. 모든 eval을 최적화한 구현으로 보고하지 않는다. P24 workspace/optimizer, source closure, birth rule, exact BigRational certificate와 admission tolerance, input/output stop, solver policy와 counters는 변경하지 않는다.

SIMD는 stable `std::arch`의 add/sub/mul/div/sqrt만 쓴다. 각 lane의 `(2*n)*n`, `(r*r)*r`, `(w*n)/r` 등의 원 괄호를 유지하고, lane 결과는 scalar Neumaier에 원 순서로 넣는다. exp는 원 scalar 구현, FMA와 reciprocal approximation은 사용하지 않는다. 실제 intrinsic은 AVX 부류지만 conservative AVX2 runtime detection을 적용했다. fallback과 tail을 포함하여 **전 모드 strict bitwise gate**를 적용한다.

Cache key는 `(x,h,b,y).to_bits()`이고 `+0/-0`을 구별한다. 성공한 Evaluation만 저장하며 매 direction에 대해 새 Jv를 만든다. JVP base는 RHS stage가 바뀌어도 보존된다. cache를 소유하는 bank는 immutable Arc이고 매 segment 새 evaluator를 만든다. 같은 state에서 다른 bank나 birth 전후의 cache를 공유하지 않는다.

## CLI와 runtime 배치

```text
bass-s10-optimization run MODE INPUT.json OUTPUT.json
bass-s10-optimization callbacks MODE INPUT.json OUTPUT.json
bass-s10-optimization batch MODE WORKERS INPUTS.json OUTPUT.json
```

출력은 원 receipt/callback shape를 유지한다. batch의 입력·출력은 배열이며 입력 순서를 보존한다. mode/backend/timing은 command 또는 별도 benchmark receipt에 둔다. 실패도 parse 가능한 JSON으로 남는다.

기존 검증된 S9 runtime의 sibling layout에 새 crate만 넣는다. 상대 path dependency는 다음 구조를 전제로 한다.

```text
build/client/s9_vigilode/
build/client/s10_optimization/
build/client/balance_p24.rs
build/vigilode -> 고정되고 검증된 upstream directory
```

기존 offline vendor와 Rust1.94.1을 재사용한다. `Cargo.lock`은 원 S9 lock의 registry/upstream entry를 그대로 두고 신규 local root package만 추가했다. Rayon1.12.0와 sha2 0.10.9는 기존 locked package다. Cargo 재해석/compile은 아직 수행하지 않았으므로 `--locked --offline` 빌드가 후속 gate다.

`src/bin/s10-benchmark.rs`는 parent 소유 harness다. binary autodiscovery를 유지한다. `allocation-probe` feature는 별도 allocation 계측 binary용이며 uninstrumented timing binary와 구별한다. benchmark 명령·반복·input hash는 별도 C4 사전등록이 정한다.

## 작성한 targeted tests

`tests/targeted.rs`에는11개 test가 있다. n16/64/256 × cohort2/16/64의 원 kernel bit 비교, scalar fallback과 SIMD tail, d=±2와 매우 큰 matching x/u, 분리 cache와 alternating direction, 모든 key 좌표의1ULP와 signed zero, 새 bank 분리, NaN/domain/error precedence와 회복, 작은 no-birth/one-birth full receipt, 입력 실패 receipt, workers1/2/4의 ordered receipt, elapsed만 제외한 비교기를 다룬다.

`fixtures::synthetic_bank`는 양의 dyadic mirrored midpoint를 사용하는 **frozen kernel bank**다. 새 isotropic P24 birth fixture로 부르지 않는다. 작은 integration test는 원 S9 input의 원 stock과 coordinate grid를 사용하며, 새 birth에는 기존 P24와 exact certificate 경로를 적용한다. 원8개 캠페인을 이 test 파일에 재실행용으로 복제하지 않는다.

지시 뒤 사용할 검증 명령의 형태는 `cargo test --locked --offline --release --test targeted -- --test-threads=1`다. 현재 이 명령을 실행하지 않았다. test harness는 직렬로 실행하여 workers1/2/4 테스트의 local Rayon pool이 다른 test와 겹치지 않게 한다. compile jobs2, benchmark workers≤4, 실제 cgroup8CPU/8GiB, 추가 disk4GiB/개별 job1800초를 유지한다.

P2/P4만으로 continuum이나 native finite-bin 보존을 승인하지 않는다. P6, physical source/stress closure, spectral convergence, production/full EoR/merge는 별도 의무다.
