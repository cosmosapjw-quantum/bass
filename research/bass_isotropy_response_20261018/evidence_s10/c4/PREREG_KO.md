# S10 C4 — 정확한 수치 계약을 보존하는 최적화 benchmark 사전등록

## 상태와 목적

**C4 설계 완료. 실행 source binding, compile, C6, benchmark와 C9 실제 독립 검토는 아직 이 문서의 결과가 아니다.** 이 단계는 부모가 작성한 `s10_optimization/src/bin/s10-benchmark.rs`, 신규 crate의 공개 API와 `tests/targeted.rs`를 읽어 사전등록을 구체화했다. 이 담당자는 구현 source를 수정하거나 compile·benchmark·과학 적분을 실행하지 않았다.

기계 판독 계약은 [BENCHMARK_PROTOCOL.json](BENCHMARK_PROTOCOL.json)이다. source가 아직 freeze되지 않았으므로 JSON의 `read_source_snapshots`는 읽은 설계 시점의 식별자다. 부모의 실제 실행 binding이 최종 source·입력·binary·환경을 결속해야 한다. 이번 출력은 기존 GitHub repo의 연구 산출물이며 부모가 단계별 게시와 이중 백업/readback에 포함한다. 현재 미완료인 게시나 cloud readback을 완료로 표시하지 않는다.

이번 질문은 **같은 S9 물리 입력과 같은 release 빌드에서 계산 순서·출력·gate를 보존하면서 어떤 비용을 줄일 수 있는가**이다. 기존 완료 8이력을 재확인하려는 캠페인을 만들지 않는다. 네 기존 입력의 성능 반복 측정과 새 kernel 비용 측정을 등록하며, 반복 호출 수를 새로운 독립 과학 사례 수로 세지 않는다.

## 고정 source와 물리 계약

기준 과학 source는 `4b30957cb008aad8019bb1a673937fc67bd017e8`, 기존 S9 결과 publication은 `a40311796f9aac5ea5e0e58c630bee2a78443353`이다. 원 S9 `src/lib.rs` SHA256은 `204d3fa9dd4a5ed8400410ff1035c4771e11d6ff50d5267a3756a740cf9b731b`다. 실제 VigilODE source는 `a21d573980f66fe02891bd216153443b5352f921`, 고정 original REI spectral owner는 `0e25846433170d0f420c4cda44a0bedbf02cd177`를 유지한다.

Non-tilted axisymmetric Bianchi I, signature `(-,+,+,+)`, \(a_\perp=a\exp(-b)\), \(a_\parallel=a\exp(2b)\), \(s=\dot b\), \(\Sigma=\sqrt3|s|/H\)를 유지한다. 기존 광자장·physical anisotropic stock·기존 birth data는 불변이다. 새 명시적 등방 birth만 기존 양의 P24 admission과 정확한 moment bound \(3/10^{15}\)를 통과한다. source frame, reflection parity, birth weights, event transfer와 fresh driver/bank restart를 바꾸지 않는다.

solver tolerance, output schedule, P24 owner, spectral bins, FMA/reassociation/fast-math 또는 근사 exp/sqrt/div를 바꾸지 않는다. Wolfram에서 검토한 dd 항등변형은 이번 실행에 적용하지 않는다. 기존 science gate는 Hamiltonian/cohort energy 각각 `1e-11`, event energy `1e-13`, donor endpoint `3e-14`, fine reference 절대차 `1e-9`, clock 절대차 `1e-12`다. 이 기준의 원본은 `s9_vigilode/PREREGISTRATION.json`이며 JSON에 원본과 각 입력/RAW/assessment/process의 SHA256을 기재했다.

## 여섯 구현과 수용 기준

| mode | 변경 대상 | 이번 수용 기준 |
|---|---|---|
| `baseline` | 원 `bass_s9_vigilode::run`와 원 evaluation | 비교 기준 |
| `stream` | 임시 Vec 제거, 원 순서의 Neumaier 누적 | kernel bit와 전체 scientific receipt 동일 |
| `prepared` | immutable μ²/weight prepared data 추가 | 같은 기준 |
| `cache` | bank-local exact-key RHS/Jacobian cache | 같은 기준; 새 방향은 새 Jv |
| `simd` | stable `std::arch` packed f64 원소 연산과 ordered scalar reduction | 같은 기준; guard와 scalar fallback |
| `simd_cache` | SIMD와 exact cache 결합 | 같은 기준 |

**같은 release에서 여섯 mode 모두 strict equality를 요구한다.** kernel은 모든 `Evaluation` 성분과 Jv를 `f64::to_bits`로 비교한다. 이력은 원 `RunReceipt`에서 `elapsed_seconds`만 제외하고 canonical scientific bytes/SHA256을 비교한다. 입력, signed zero, 상태·실패, 관측, event, exact certificate, cohort, old-stock digest, segment와 solver counters는 모두 남는다. 불일치는 `FAILED_CANDIDATE`이며 science tolerance 안이라는 이유로 허용하지 않는다. 비교 helper가 timing만 무시하고 signed zero/status 변경을 검출하는 작은 C6 control도 보존한다.

기존 저장 S9 debug RAW와 새 release baseline 사이에는 기존 science gate를 적용한다. 서로 다른 빌드의 bit identity를 근거 없이 요구하지 않는다. 같은 release 후보의 완전 동일성과 baseline의 과학 gate 통과를 각각 확인해야 최적화 결과를 수용한다.

LLVM 공식 문서는 elementwise vectorization과 floating reduction 재결합의 조건을 구분한다. 따라서 vector lane 결과를 원 node/cohort 순서로 scalar Neumaier에 넣고 reduction tree를 바꾸지 않는다. Rust의 `_mm256_sqrt_pd`·`_mm256_div_pd`는 AVX intrinsics이며, 구현이 더 보수적으로 AVX2 runtime guard를 사용하면 그 차이를 기록한다. Pulp 0.22.3은 조사한 대안이고 이번 채택 패키지가 아니다. Rayon 1.12.0은 기존 lock/vendor에서 독립 이력에 사용한다. [LLVM](https://llvm.org/docs/Vectorizers.html), [Rust std::arch](https://doc.rust-lang.org/1.94.1/std/arch/), [sqrt intrinsic](https://doc.rust-lang.org/1.94.1/core/arch/x86_64/fn._mm256_sqrt_pd.html), [div intrinsic](https://doc.rust-lang.org/1.94.1/core/arch/x86_64/fn._mm256_div_pd.html), [Rayon upstream](https://raw.githubusercontent.com/rayon-rs/rayon/v1.12.0/src/iter/mod.rs).

## Kernel workload와 고정 표본 수

node 수 `16/64/256` × cohort 수 `2/16/64`의 9개 grid를 쓴다. 각 grid에 `changing` eval trace와 `jvp_reuse` trace를 적용하므로 timing 조건은 18개다. 실제 harness의 `bank`는 μᵢ=(2i+1)/n−1, αᵢ=1/n의 양의 dyadic 반사 대칭 frozen stock이다. cohort u, birth b, energy와 bank 상수는 JSON에 식 그대로 등록했다. 이 bank는 새 isotropic P24 source나 continuum angular refinement가 아니다. C6의 별도 `fixtures::synthetic_bank`와 provenance를 섞지 않는다.

`changing`은 `p=i%32`, `jvp_reuse`는 정수 나눗셈으로 `p=(i/16)%32`를 쓴다. x/state는 p에 따라 변하고 Jv 방향은 i에 따라 변한다. 반복 base point에서 방향을 바꿔 Jacobian의 재사용과 Jv 재계산을 동시에 점검한다. query와 연산 순서는 frozen Rust source 및 JSON의 수식에 결속한다.

batch 호출 수는 측정 전에 다음과 같이 고정한다.

\[
N_{\rm calls}=\max\left(64,\min\left(8192,\left\lfloor\frac{1048576}{nK}\right\rfloor\right)\right).
\]

| nodes | cohorts 2 | cohorts 16 | cohorts 64 |
|---:|---:|---:|---:|
| 16 | 8192 | 4096 | 1024 |
| 64 | 8192 | 1024 | 256 |
| 256 | 2048 | 256 | 64 |

짧게 측정되어도 반복 수를 늘리지 않는다. `SHORT_BATCH`/timer-resolution 한계를 기록한다. wall-clock을 보고 workload나 solver tolerance를 조정하지 않는다.

각 mode/grid/trace에서 timing 밖의 64-query strict comparison을 먼저 실행한다. 총 6,912개 비교이며 baseline과 해당 mode를 각각 호출하므로 실제 callback 호출은 13,824회다. 그 뒤 mode마다 정확히 한 batch를 warmup한다. warmup은 총 108 batches이며 이미 correctness query를 거친 evaluator를 사용하므로 cold-cache 시험이 아니다.

timed round는 정확히 7회다. 매 round 다섯 후보 각각에 인접한 baseline을 배치한다. `candidate=1+(ci+round)%5`, pair 순서는 `(ci+round)%2`에 따라 baseline→candidate 또는 반대다. 총 **1,260 timed batches**이며 grid와 trace의 외부 순서는 harness의 고정 순서를 따른다. 비교·hash·serialization·file I/O와 diagnostics는 timing 밖이다. query 생성과 `black_box`, eval/Jv 호출은 timing 안이다.

새 diagnostic evaluator에서 각 조건당 64회 호출한 counters는 108 batches/6,912 calls로 별도 기록한다. cache hit 또는 kernel evaluation 감소를 elapsed-time speedup으로 해석하지 않는다.

## 준비 비용과 allocation 계측

`Evaluator::new(owned_bank,mode)`의 준비시간은 9 grid×6 modes마다 1회 warmup, 7회 측정한다. **54 warmups와 378 `PREPARE_SAMPLES`**다. round마다 mode 순서를 회전한다. caller bank clone과 evaluator drop·serialization은 timer 밖이다. 이 단일 준비 표본은 특히 baseline에서 sub-µs timer 잡음에 지배될 수 있으므로 별도 median/IQR와 caution을 기록한다. 준비비용의 break-even은 해당 workload에 대한 참고 계산으로만 해석한다.

allocation은 `allocation-probe` feature로 만든 **별도 binary에서 한 번** 실행한다. timing binary에는 GlobalAlloc 계측이 compile out되어야 한다. 9 grid×6 modes×2 traces, 총 108 rows에 각각 64회 호출한다. 별도로 54개의 `Evaluator::new` setup 영역을 계측한다. 각 trace는 fresh evaluator로 시작한다. 이 실행에는 whole-history를 추가하지 않는다.

보고값은 `alloc/alloc_zeroed/realloc` 합계 호출 수와 요청 bytes 누적이다. setup 밖 caller clone, free balance, 실제 live bytes, peak RSS나 시간 점유율을 뜻하지 않는다. 계측 binary의 시간으로 speedup을 계산하지 않는다.

## Whole-history와 독립 job 병렬화

다음 네 입력의 원본 bytes를 그대로 사용한다. 각 입력은 기존 저장 RAW에서 153 observations를 갖는다.

| 입력 | 역할 | 기존 birth/segment 수 |
|---|---|---:|
| `closed_mf_into_ls_r2` | fine MF + analytic JVP/Ft | 32 / 33 |
| `closed_small_clock4_r2` | fine direct + clock augmentation | 32 / 33 |
| `flrw_mf_into_ls_fine` | analytic FLRW control | 0 / 1 |
| `flrw_small_clock4_fine` | analytic FLRW + clock control | 0 / 1 |

각 case×mode에 한 번의 warmup을 실행하고 그 **24개 전체 RAW**를 보존한다. 이후 4 cases×7 rounds×5 candidates×2 paired samples = 280 timed 호출을 수행한다. serial history 전체는 **304회**다. 반복은 전체 scientific SHA256, status, exact 판정, pair 순서와 timing을 보존하며 동일한 전체 RAW를 계속 복제하지 않는다.

outer timer는 `run_with_mode` 한 호출을 감싼다. caller input clone은 시작 전, receipt hash/직렬화와 drop은 elapsed 취득 뒤다. 함수 안의 실제 receipt construction, 내부 clone, birth/P24/certificate, callback과 준비 비용은 실제 end-to-end 비용에 포함된다. 원 `elapsed_seconds`도 diagnostic으로 남기되 outer 시간과 혼동하지 않는다.

parallel은 `baseline`과 `simd_cache`, workers `1/2/4`, 고정 네 입력 batch를 사용한다. 각 mode/worker에 1 warmup +7 timed batches를 수행한다. 총 48 batches, **192 history 호출**이다. round마다 mode의 AB/BA 순서를 교대한다. 입력 index 순서로 수집한 모든 출력이 serial 대표 hash와 같아야 한다.

`run_independent`는 매 호출 local Rayon pool을 생성하므로 **pool construction을 포함한 전체 batch 시간**이다. API 반환 전에 수행되는 teardown도 실제 timer 범위에 포함된다. caller Vec clone·hash·serialization·drop은 밖이다. kernel 내부 병렬 reduction이나 global pool·중첩 threading은 하지 않는다. explicit pool 구성은 [Rayon ThreadPoolBuilder](https://docs.rs/rayon/1.12.0/rayon/struct.ThreadPoolBuilder.html)에 근거한다.

따라서 성능 harness는 **304+192=496 history 호출**, 고유 기존 물리 입력은 **4개**다. 별도 C6 `targeted.rs`에는 현재 **30회 run 호출**이 있다. 짧은 no/one-birth 14회, input-failure 7회, parallel order 8회, scientific comparator control 1회이며 예상 정상 적분은 23회, 적분 전 예상 실패는 7회다. 둘을 합치면 현재 설계는 526회 run 호출이고, 이 수치를 526개 독립 과학 사례로 표현하지 않는다. C6 test/input이 바뀌면 실행 전에 count와 source binding을 함께 갱신한다.

## C6와 과학 gate의 범위

현재 11개 targeted tests가 변경된 위험을 담당한다. node/cohort 순서의 bit equality, SIMD fallback/tail, 큰 같은 x와 birth u의 차를 별도 exp로 분해하지 않는 조건, RHS/JVP cache slot 분리, x/h/b/y 각 coordinate의 1-bit 변화, signed zero, 같은 point의 새 bank, caller clone 변경에도 원 evaluator 불변, invalid domain/direction의 error 우선순위와 valid recovery, 짧은 birth/no-birth receipt, input-failure receipt, worker cap·순서, scientific comparator다. 기존 전체 S9 test/campaign을 확인 목적으로 다시 수행하지 않는다. 별도 FMA solver/control 변형은 추가하지 않는다.

cache는 동일 bank의 정확한 `to_bits` point만 재사용한다. 새 방향은 원 순서의 Jv를 새로 계산하고, 새 bank/event는 이전 cache lifetime을 끝낸다. 다른 점의 approximate Jacobian reuse는 방법의 order 조건에 대한 별도 검토가 필요한 변경이므로 이번 범위에 넣지 않는다. [EPIRK primary paper](https://arxiv.org/html/1701.06528).

저장한 새 release 대표 RAW로 기존 S9의 네 입력에 해당하는 68개 quality-gate 판정을 적용한다. positive background, output schedule, immutable old-stock/births, 정확한 P24 certificate, energy/Hamiltonian/clock/reference, right-bank event 관측, fresh segment와 실제 JVP/Ft/direct work를 검사한다. 동일 release 후보의 counters·관측·cohort·event가 모두 같다는 조건은 별도로 유지한다. S8 153-row reference는 재사용하며 S8 적분을 실행하지 않는다. compensation만으로 다른 summation 순서의 reproducibility가 보장된다고 가정하지 않는다. [Collange et al. primary paper](https://hal.science/hal-00949355v3/file/superaccumulator.pdf).

## 통계와 허용되는 주장

각 grid/trace/candidate와 case/candidate에 대해 원 7개 paired samples, latency median, Q1/Q3/IQR, pair별 `baseline_time/candidate_time`를 기록한다. quantile은 `(N−1)p` 선형보간이며 N=7에서 Q1은 정렬된 index1·2의 평균, Q3은 index4·5의 평균이다. baseline은 해당 인접 pair의 값을 사용한다. 여러 후보의 baseline을 임의로 섞지 않는다.

kernel은 seconds/calls도 보고하되 cache가 실제로 생략한 ray 연산을 모두 실행했다고 가정한 처리량을 만들지 않는다. 18 kernel 조건과 네 history의 회귀·무효과도 모두 제시한다. 사전등록하지 않은 가중 평균 speedup, best-run 선택 또는 사후 추가 round는 없다.

parallel은 pool 포함 batch latency와 `4/seconds` throughput을 보고한다. workers1 대비 workers2/4 비율과 efficiency는 다른 worker block에서 얻은 descriptive scaling이다. worker별 같은 round index를 비교하더라도 시간적으로 인접한 paired 인과 비교로 표현하지 않는다. shared container의 7개 표본으로 portable speedup·population confidence나 power law를 주장하지 않는다.

## 실행 DAG, 자원, 실패와 다음 단계

1. 부모가 최종 source/tests/harness, 두 C4 문서, Cargo lock/vendor, 네 입력·reference, deterministic bank/query 정의, Rust/target/profile/features, 두 binary와 명령을 결속한다. 실제 publication/readback 상태도 그대로 기록한다.
2. 같은 release timing binary와 별도 allocation binary를 준비한다. compile 시간은 benchmark에서 분리한다. 이후 timing과 build를 동시에 실행하지 않는다.
3. 범위가 고정된 C6를 실행하고 raw/exit/failure를 보존한다.
4. micro(준비 표본 포함), serial history, parallel batch, 별도 allocation을 순차 실행한다. 고정 표본 수와 live strict-equality gate를 적용한다.
5. 대표 RAW의 science gates와 저장 pair 통계를 분석한다. 그 뒤 부모가 요청하는 **한 번의 C9 독립 검토**에서 물리 계약, 변경 source, execution binding, raw gate와 요약 통계를 읽는다. 이 담당자의 C4 설계는 C9 결과를 대신하지 않는다.
6. 결과·실패 후보·남은 의무를 게시하고 GitHub 및 두 backup/readback 상태와 두 handoff를 갱신한다. 이 작업은 부모 담당이다.

사용자 상한은 추가 workers16, RAM16GiB, disk4GiB, 개별 job1800초다. 현재 관측한 8 CPU/8GiB 환경보다 크게 요청하지 않고 build jobs2, timing process1, parallel workers1/2/4를 사용한다. 기존 owner 작업을 보존한다. sparse `/proc` RSS는 관측 하한으로만 보고하며 전체 process tree/lifetime을 포괄하지 않은 값을 peak라고 부르지 않는다.

실패는 source binding, build/I/O, domain 예상 실패, strict identity, science gate, timeout/resource, incomplete samples, timer 해상도, cloud readback pending을 구분한다. 원 실패·partial JSONL·exit를 보존하고 기존 run directory를 덮어쓰지 않는다. 같은 실패 작업은 초기 시도와 한 번의 diagnostic retry까지만 허용한다. 실제 원인에 따른 source 수정은 한 번의 범위가 고정된 repair episode에서 영향받은 검증만 실행하고 새 결속을 남긴다. timeout 뒤 7쌍이 안 된 조건은 `INCOMPLETE`이며 빠진 표본을 숨겨 PASS로 만들지 않는다.

이번 범위가 통과해도 continuum angular 보증, P6 제약 알고리즘, 실제 REI/MD14 owner feedback, 전체 reactive finite-bin 보존·spectral history 수렴, REI production, full EoR 또는 merge를 승인하지 않는다. `RESULT_VALIDITY`, `PROVENANCE_VALIDITY`, `PACKAGING_VALIDITY`를 구분하여 완료한 근거를 재사용하고 남은 의무만 이어간다.

## Skill context

사용자가 선택한 `physmath-research-loop` 1.3.0의 SKILL, STAGE_SELECTION, POLICY_INTEGRATION, SUBAGENT_MODE, STAGE_GUIDE_KO 및 CODING_LOOP를 적용했다. 실제 경로와 SHA256은 JSON의 `skill_context_used`에 있다. C4의 bounded DAG·자원·checkpoint를 설계했고, unchanged core policy와 R2의 검증된 primary source를 재사용했다. C4 완료를 계기로 추가 연구 주기·compile·독립 검토를 이 담당자가 자동 실행하지 않는다.
