# S10 C3 — 원 과학 receipt를 보존하는 제한된 callback 최적화

## 선택과 완료 경계

이번 설계와 구현은 `physmath-research-loop` 1.3.0의 C3/C5다. 원 과학 source는 BASS `4b30957cb008aad8019bb1a673937fc67bd017e8`, 원 결과는 `a40311796f9aac5ea5e0e58c630bee2a78443353`이며, VigilODE `a21d573980f66fe02891bd216153443b5352f921`, REI owner `0e25846433170d0f420c4cda44a0bedbf02cd177`를 유지한다. C2의 식·비용·license 조사와 원 S9의 8개 실행을 재사용한다.

`skill_context_used`: `/root/.codex/plugins/cache/created-by-me-remote/physmath-research-loop/1.3.0/skills/physmath-research-loop/` 아래 `SKILL.md`, `STAGE_SELECTION.md`, `references/POLICY_INTEGRATION.md`, `references/CODING_LOOP.md` C3/C5 계약, `references/SUBAGENT_MODE.md`. 실제 읽은 파일의 SHA256은 함께 쓰는 `SKILL_CONTEXT_USED.json`에 고정한다. 연속식·폐쇄·이산화와 구현을 연결하고, scalar arithmetic 순서와 state/bank identity를 보존한 runnable feature를 만든다. compile, test, benchmark 실행은 source/prereg 게시 뒤 parent의 별도 실행 지시까지 **NOT_RUN**이다.

수정 범위는 lane의 신규 `s10_optimization/` crate다. 원 `s9_vigilode`, `balance_p24.rs`, 고정 upstream은 읽기 전용이다. 원 loop 중 필요한 부분만 명시적 provenance와 exact diff를 남겨 복사한다. baseline variant는 원 crate의 실제 `run(input)`을 호출한다.

## 식과 연산 순서

`Cohort::moments`의 원 식을 그대로 사용한다. `z=mu*mu`, `a=exp(2*d)*(1-z)`, `c=exp(-4*d)*z`, `r=sqrt(a+c)`, `n=c-a/2`, `dd=(-4*c-a)/r+((2*n)*n)/((r*r)*r)`, 세 term은 `w*r`, `(w*n)/r`, `w*dd`다. `factor=energy_birth*exp(-4*(x-u))`도 원 괄호를 보존한다. `exp(-4*x)*exp(4*u)` 같은 재인수분해를 하지 않는다.

RHS/J/Ft 식, Jacobian-vector product의 원 3항 Neumaier 순서, 단위·time variable, donor closure, birth schedule, source frame과 spectral owner는 변경하지 않는다. Wolfram이 확인한 다른 동치 Pi_b 식은 이 구현에 넣지 않는다.

원 moment 구현의 ray별 임시 triple Vec와 bank의 cohort triple Vec를 각각 세 scalar Neumaier accumulator로 대체한다. 각 채널에 들어가는 term의 bit pattern과 ray/cohort 순서를 유지한다. 이것은 discretization이나 solver tolerance 변경이 아니다. 기준은 우선 BYTE 동일성이다. SIMD도 별도 gate를 가지며 통과 전 수치 동등성을 승인하지 않는다.

## 여섯 variant

| Mode | 적용 |
|---|---|
| `baseline` | 원 S9 `FrozenBank::eval/jvp/run` |
| `stream` | 원 mu/alpha에서 계산, ordered streaming ray/bank sums |
| `prepared` | stream + immutable `mu²`/alpha SoA; 같은 `mu*mu`를 준비 시 한 번 수행 |
| `cache` | prepared + 별도 RHS와 JVP-base bounded slots |
| `simd` | prepared + AVX2 lane arithmetic, cache 없음 |
| `simd_cache` | simd + 동일 cache 계약 |

SIMD는 parent가 승인한 stable `std::arch`를 사용한다. conservative AVX2 runtime detection으로 dispatch하고 모든 다른 target에서 scalar fallback한다. 256-bit 4×f64 lanes에서 원 순서의 add/sub/mul/div/sqrt만 쓴다. FMA, reciprocal approximation, approximate exp, parallel reduction을 사용하지 않는다. 계산한 각 lane의 세 term은 원 index 순서대로 scalar Neumaier에 넣는다. tail은 scalar 원 식으로 계산한다. CPU feature는 prepared evaluator당 한 번 결정하고 공개 `backend()`로 기록 가능하게 한다.

## 소유권과 cache

`Evaluator`는 외부에서 변경할 수 없는 `Arc<FrozenBank>`를 소유한다. 준비된 데이터는 내부 private 배열이며 원 mu/alpha와 stock metadata를 보존한다. 동일 bank를 공유하는 안전한 Rust `Arc`에는 mutable alias가 생길 수 없으며, 원 source와 prepared data를 외부에 mutable reference로 내주지 않는다.

key는 `x,h,b,y` 각각의 `f64::to_bits()`를 담는 4원소 배열이다. `+0/-0`은 구별한다. 유효성 검사를 통과한 성공 Evaluation만 cache한다. RHS/partial_t slot과 JVP-base slot은 독립이며 각각 최대 한 항목이다. JVP miss에서 같은 key의 RHS 성공값을 재사용할 수 있고, 그 뒤 stage RHS가 바뀌어도 JVP base는 보존된다. 매 direction에 대해 원 순서의 matrix-vector product를 다시 계산한다. direction의 NaN/Inf 오류는 원 S9처럼 base eval 전에 판정한다.

각 segment callback은 새 Evaluator/cache를 만든다. bank가 달라지는 birth 전후의 state bit가 같아도 cache는 공유하지 않는다. source bank에는 interior mutability가 없으며 cache는 Mutex로만 보호한다. cache entry는 불변 physical bank를 나타내는 evaluator 내부에 한정되어 별도 전역 key로 유출하지 않는다. 진단 counters는 opt-in이며 기본 timing 경로에서는 atomic increment를 하지 않는다.

## 최소 integration copy

원 S9 `validate_input`, `observe`, `projected_birth`, `run`, `run_inner`의 필요한 부분을 `runner.rs`로 복사한다. 원 `projected_birth`가 private이므로 정확한 failure/pending-candidate receipt 보존을 위해 이 작은 helper도 복사하고, 변하지 않은 owner `balance_p24.rs`를 같은 방식으로 참조한다. `Cohort`, `Input`, `MomentCertificate`, `RunReceipt`, `birth_support`, `exact_moment_certificate`, `failure_kind`는 원 crate에서 재사용한다.

candidate loop의 변경은 mode 전달과 두 callback adapter 생성부다. Birth/P24/BigRational certificate, digest 검사, before/after/event/observation, fresh driver와 original solver counter 기록은 그대로다. administrative `observe`와 birth pre/post eval은 원 bank의 eval을 사용한다. 따라서 이번 첫 최적화 표면은 **solver callbacks**이며, 모든 administrative eval까지 최적화했다고 보고하지 않는다. 원 전체 파일 SHA와 source snapshot, exact unified diff 및 발췌 범위를 기록한다.

`scientific_value(receipt)`는 `elapsed_seconds`만 제거한다. input, observations, events, segments와 counters, final_cohorts, failures, pending_birth 등 다른 field는 제거하지 않는다. baseline과 candidate 비교는 이 완전한 내용으로 수행할 수 있다. mode/backend/외부 timing은 과학 receipt 외부의 command 또는 harness metadata로 기록한다.

## API와 CLI

crate 이름은 `bass-s10-optimization`이다. `Mode`는 `FromStr`/serde를 지원한다. `Evaluator::new(bank,mode)`, `with_diagnostics(bank,mode)`, `eval(x,state)`, `jvp(x,state,direction)`, `counters()`, `backend()`를 공개한다. `run_with_mode(Input,Mode)->RunReceipt`, `run_independent(Vec<Input>,Mode,workers)->Result<Vec<RunReceipt>,String>`를 제공한다.

CLI는 `run MODE INPUT OUTPUT`, `callbacks MODE INPUT OUTPUT`, `batch MODE WORKERS INPUTS_JSON OUTPUT_JSON`이다. root timing harness는 library API로 parse/serialize/phase 비용을 분리할 수 있다. 이 CLI에는 임의 time loop나 benchmark 자동 실행을 넣지 않는다.

`run_independent`는 Rayon1.12.0의 명시적 local pool과 indexed ordered collect를 사용한다. 허용 workers는1/2/4, 각 history 내부 reduction은 직렬이다. 서로 다른 history 사이 cache와 mutable bank를 공유하지 않는다. 기존 vendor/lock에 있는 Rayon을 재사용하고 nested inner pool을 만들지 않는다. compile jobs2, worker≤4, 실제 cgroup8CPU/8GiB와 총 추가 disk4GiB/job1800초를 유지한다.

## 작은 targeted test를 작성할 범위

- n16/64/256 × cohort2/16/64의 mirrored positive source-valid kernel bank에서 scalar stream/prepared/cache와 원 eval/JVP의 bit 비교.
- SIMD의 ordinary values 및 scalar fallback/tail 동등성. lane 내 operation order와 scalar ordered reduction을 비교한다.
- `+0/-0`, nonfinite x/state/direction, zero/negative h와 원 error string, large matching x/u, d가 ±2를 포함하는 범위.
- 같은 bank/state의 반복·alternating direction, RHS stage가 JVP base를 밀지 않음, 신규 bank의 같은 state가 이전 cache를 읽지 않음, 오류를 성공 cache로 저장하지 않음.
- 원 callback/whole-run scientific receipt의 compare helper. 작은 no-birth/짧은 birth fixture만 targeted test로 작성하고 실행은 별도 지시까지 보류한다. 실제 사전등록 whole-history matrix는 root C4 harness가 소유한다.
- 독립 history workers1/2/4의 입력 순서와 각 receipt의 원 baseline 대응, 잘못된 worker 수 거부.

원 사전등록 gate를 그대로 유지한다. P24 workspace, 다른 optimizer, P6, full physical source/REI production/full EoR/merge는 이번 첫 artifact 범위에 넣지 않는다. source-only 완료는 compile/test PASS가 아니며, 실측 없는 speedup은 보고하지 않는다.
