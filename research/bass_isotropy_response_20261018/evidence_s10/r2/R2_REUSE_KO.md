# S10 최적화 R2 — 문헌·공식 코드 재사용

**권고 순서는 원래 순서의 streaming Neumaier, immutable prepared data, 동일 point의 exact cache, ray별 SIMD, 독립 이력 단위 병렬화다.** 앞의 세 후보는 작은 kernel에서 할당과 중복 계산을 줄이는 직접적인 방법이다. SIMD와 병렬화는 그 이후에 비용을 분리해 비교한다. 이 순서는 현재 구조에 대한 재사용 판단이며, 아직 측정된 speedup은 아니다.

이 문서는 부모가 지정한 R2 범위의 완료 산출물이다. 물리·출생·source 계약은 [S10_OPTIMIZATION_KO.md](../../../bass/research/bass_isotropy_response_20261018/S10_OPTIMIZATION_KO.md)를 따른다. 기존 S9 과학 결과와 고정 소스를 재사용했고, 여기서는 ODE 적분·과거 검사·코드 수정·의존성 설치·외부 쓰기를 수행하지 않았다. 선택한 알고리즘의 구현과 새 benchmark는 부모의 C3–C8 작업으로 연결한다.

## 1. 실제 조사와 근거의 범위

SciSpace의 자연어 질문 두 개로 재현 가능한 parallel summation과 ODE/Jacobian 평가 재사용 문헌을 조사했다. Exa는 LLVM/Rust 공식 문서, Rust upstream package, 원 저자 summation 논문이라는 서로 다른 세 방향을 검색했다. 모든 외부 query는 일반적인 공개 과학·소프트웨어 질문이며 프로젝트의 비공개 source, 입력, 결과 또는 사용자 대화문을 전송하지 않았다.

| 기록 | 실제 수 | 의미 |
|---|---:|---|
| 서로 다른 검색 | 5 | SciSpace 2회, Exa 3회 |
| SciSpace 반환 후보 | 20 | 초록·서지 후보이며 검증 원문 수가 아님 |
| Exa `numResults` 합 | 21 | 요청한 후보 slot 수 |
| Exa 반환 URL | 21 | 정확히 같은 URL 기준 중복 0개; 동일 프로젝트·논문의 다른 URL은 포함 |
| primary URL fetch | 25회 | 반복·다른 버전 URL 포함 |
| 내용 수신 | 23회, 고유 URL 22개 | Exa의 clean content 수신; 원 PDF 또는 Git blob bytes의 readback 주장이 아님 |
| 실제 관련 절을 검토한 source 묶음 | 9 | 아래 세 논문과 여섯 공식 문서·package 묶음 |

`numResults` 합을 완독 수로 표시하지 않는다. 길이 상한에 걸린 문서에서는 관련 알고리즘·API·제약 부분만 검토했다. 논문 전체 완독을 주장하지 않는다. 상세 URL, 확인한 절, 버전 차이, API, 재사용 조건은 [REUSE_SOURCES.json](REUSE_SOURCES.json), 원 검색·fetch 응답은 `raw/`, 그 파일들의 SHA256은 [RAW_RECEIPTS_MANIFEST.json](RAW_RECEIPTS_MANIFEST.json)에 있다.

## 2. 원 논문의 직접 재사용

### P1. 재현 가능한 합산의 두 층

Collange 등의 *Numerical Reproducibility for the Parallel Reduction on Multi- and Many-Core Architectures*에서 §2.1의 TwoSum과 §3.1의 expansion accumulation은 빠른 부동소수점 처리와 남은 오차의 정확한 축적을 구분한다. Algorithm 1은 round-to-nearest 아래 덧셈 결과와 반올림 잔차를 분리하고, Algorithm 2는 고정 길이 expansion에 남는 잔차를 superaccumulator로 넘긴다. 해당 논문은 이 전체 구성과 마지막 반올림을 통해 합산 순서가 달라도 같은 정확한 합의 반올림값을 목표로 한다. [HAL v3 원문](https://hal.science/hal-00949355v3/file/superaccumulator.pdf)

현재 문제에 재사용할 핵심은 **ray별 연산을 병렬로 계산하는 것과 결과를 어떤 순서로 합치는 것이 서로 다른 선택**이라는 점이다. 기존 Neumaier 합산을 벡터 lane별 합산 또는 병렬 tree reduction으로 교체하면 같은 실수 수식을 계산하더라도 부동소수점 연산 그래프가 달라진다. 문헌의 exact accumulator까지 도입하지 않은 채 그 재현성 결론을 가져올 수 없다.

이 논문의 큰 배열에서의 처리량은 16-ray cohort 비용의 speedup 추정치로 사용할 수 없다. 당장은 기존 보정합의 입력 순서를 유지하는 구현을 우선하고, 여러 scheduler·CPU에서 합산 순서와 무관한 bitwise 결과가 실제 요구가 되는 경우에만 expansion/superaccumulator를 별도 후보로 둔다. 고정 overhead와 작은 배열의 비용을 그때 직접 비교한다.

### P2. 보정합의 정확도와 저장 비용

He–Ding은 민감한 기후 모형의 global summation에서 self-compensated summation과 double-double arithmetic을 비교하고, 부분합과 오차를 함께 다루는 MPI 합산을 설명한다. 확인한 부분은 self/doubly compensated summation, 합산 순서 민감도, double-double 및 병렬 조합이다. [기관 저장소 원문](https://escholarship.org/content/qt5wm5z58d/qt5wm5z58d.pdf?t=p21mk2)

현재 구현에 필요한 연결은 보정합이 소수의 accumulator 값으로 동작한다는 점이다. `Vec<[f64; 3]>`를 만든 뒤 세 번 합산하는 구조를 세 개의 `(sum, correction)` 상태에 차례로 공급하는 구조로 바꿀 수 있다. 각 성분에 들어가는 값의 bits와 순서, 보정 갱신의 괄호·덧셈·뺄셈 순서를 그대로 보존하면, 서로 독립인 세 accumulator의 갱신을 한 loop에 교차 배치해도 각 성분의 연산 의존 관계는 같다. 이는 현재 코드에 적용하는 연산 그래프 판단이다.

문헌의 관측은 보정합이 모든 입력 순서에서 같은 bits를 준다는 보장이 아니다. 기존 Neumaier를 일반 `sum`으로 바꾸거나, cohort별 correction을 버린 부분합만 임의 순서로 결합하는 근거로 사용하지 않는다. SciSpace의 2001년 journal DOI와 이번에 받은 2000년 기관 archive 표기는 별도 edition identity로 남겼다.

### P3. 정확한 memoization과 근사 Jacobian 재사용

Narayanamurthi 등의 *EPIRK-W and EPIRK-K time discretization methods*는 Jacobian 근사를 허용하는 적분법을 구성하면서 추가 order conditions를 유도한다. 서론의 Rosenbrock/ROW 설명, 식 (11), EPIRK-W order-condition 절, Theorem 3.2와 Table 3을 확인했다. [저자 preprint](https://arxiv.org/html/1701.06528)

이 문헌은 현재 VigilODE의 solver를 바꾸는 근거가 아니라, **다른 point에서의 Jacobian 재사용에는 별도 수치해석이 필요하다**는 범위 판단에 사용한다. 동일한 `(x, state, immutable bank)`에서 이미 계산한 값 또는 Jacobian 계수를 읽는 exact cache는 함수 평가를 재사용하는 구현 변경이다. 반면 state가 조금 바뀌었는데 이전 Jacobian을 사용하거나 Krylov 종료 조건을 바꾸는 것은 오차·차수 조건을 다시 다뤄야 한다. EPIRK의 정리를 현재 client에 자동 적용하지 않는다.

## 3. 공식 Rust·LLVM·package 확인

| ID / 원 source | 확인한 기능·버전 | 정확도·재현성 조건 | 현재 채택 판단 |
|---|---|---|---|
| D1 [LLVM vectorizer](https://llvm.org/docs/Vectorizers.html) | `Reductions`, 함수 호출 vectorization, Loop/SLP 설명 | 대부분 target의 floating reduction은 reassociation 관련 조건이 필요하다. 일부 target의 ordered reduction은 별도 경로다. | 독립 ray 연산과 합산을 분리한다. fast-math를 켜는 변경은 현재 후보에서 제외한다. |
| D2 [Rust 1.94.1 std::arch](https://doc.rust-lang.org/1.94.1/std/arch/) | stable vendor intrinsics, runtime feature detection, scalar fallback | 올바른 architecture와 CPU feature를 보장해야 한다. 현재 FP 환경·NaN semantics도 유지한다. | 추가 crate 없이 구현할 수 있는 우선 SIMD 후보다. |
| D3 [Rust 1.94.1 std::simd](https://doc.rust-lang.org/1.94.1/std/simd/) | `portable_simd`는 nightly-only experimental API | 현재 고정 stable toolchain에 그대로 사용할 API가 아니다. | toolchain을 바꾸지 않고 `std::arch` 또는 pinned stable wrapper를 비교한다. |
| C1 [Rayon 1.12.0 source](https://raw.githubusercontent.com/rayon-rs/rayon/v1.12.0/src/iter/mod.rs) | `ParallelIterator::reduce`, `sum`; [ThreadPoolBuilder](https://docs.rs/rayon/1.12.0/rayon/struct.ThreadPoolBuilder.html) | reduction 결합 순서를 지정하지 않는다. floating-point 결과는 완전히 deterministic하지 않다. | 독립 이력·독립 benchmark batch 수준에서 제한된 worker로 사용 가능하다. |
| C2 [Pulp 0.22.3 API](https://docs.rs/pulp/0.22.3/pulp/trait.Simd.html) | `Arch::new().dispatch`, `WithSimd`; `sqrt_f64s`, `div_f64s`, `mul_f64s` | `mul_add_f64s`, `reduce_sum_f64s`, relaxed-SIMD feature를 원 연산과 같은 것으로 가정하지 않는다. | runtime dispatch가 필요한 wrapper 후보다. 16개 lane에서 dispatch·의존성 비용을 비교한다. |
| C3 [Wide 1.7.1 f64x4](https://docs.rs/wide/1.7.1/wide/struct.f64x4.html) | `sqrt`, `Div`, `reduce_add`, `mul_add`, `exp`의 서로 다른 정확도 설명 | `reduce_add`의 순서는 고정되지 않는다. `mul_add`의 반올림 수는 hardware에 따라 다르다. [README](https://github.com/Lokathor/wide)는 compile-time SIMD 선택만 지원한다고 명시한다. | build target을 고정한 비교 후보이며 runtime dispatch의 대체물로 사용하지 않는다. |

Rust의 [`_mm256_sqrt_pd`](https://doc.rust-lang.org/1.94.1/core/arch/x86_64/fn._mm256_sqrt_pd.html)와 [`_mm256_div_pd`](https://doc.rust-lang.org/1.94.1/core/arch/x86_64/fn._mm256_div_pd.html)는 AVX의 packed double 연산이다. 이 두 연산 자체에 필요한 feature와 AVX2를 구분한다. 전체 SIMD 함수에 추가로 사용한 instruction이 있으면 그 요구 feature를 함께 기록해야 한다.

Wide 문서는 sqrt와 기본 나눗셈의 정밀한 결과를 명시하지만, `exp` 등 transcendental 함수의 precision과 `reduce_add` 순서는 따로 설명한다. 따라서 sqrt/div가 필요하다는 이유로 원래 scalar `exp`까지 한꺼번에 교체하지 않는다. 작은 SIMD block에서 ray별 값을 계산한 뒤 scalar lane을 원래 순서로 Neumaier에 공급하는 후보가 이 차이를 분리한다.

### 확인된 package identity와 license

| Package | 확인한 published/API version | License | 별도 identity 사항 |
|---|---:|---|---|
| [Rayon registry](https://crates.io/crates/rayon) | 1.12.0 | MIT OR Apache-2.0 | 공식 v1.12.0 source도 읽었다. 확인한 MSRV는 1.80이다. |
| [Pulp registry](https://crates.io/crates/pulp) | 0.22.3 | MIT | [upstream main manifest](https://raw.githubusercontent.com/sarah-quinones/pulp/main/pulp/Cargo.toml)는 0.23.0이다. published API와 같은 source라고 묶지 않는다. |
| [Wide registry](https://crates.io/crates/wide) | 1.7.1 | Zlib OR Apache-2.0 OR MIT | [manifest](https://raw.githubusercontent.com/Lokathor/wide/main/Cargo.toml)에서 version·license·MSRV 1.89를 확인했다. moving main과 published crate bytes가 같다는 주장은 하지 않는다. |

이 조사는 package의 설치나 source vendoring을 포함하지 않는다. 실제 채택할 때는 선택한 published version, archive checksum, feature와 Cargo.lock을 묶어야 한다. Registry/API 문서와 moving main의 version string만으로 byte identity를 인정하지 않는다. 논문은 개념과 알고리즘의 근거로 사용했고 논문 속 구현을 복제하지 않았다.

## 4. 현재 kernel에 연결할 구체적 조건

### 4.1 Streaming accumulator

`Cohort.moments`의 ray 배열과 `FrozenBank.eval`의 cohort 배열에서 임시 결과 `Vec`를 제거하되, F/G/Q 각 성분의 값 계산과 보정합 갱신 순서를 유지한다. 최종 `sum + correction`까지 같은 위치에서 수행한다. 이 후보는 allocation 횟수, 생성 원소 수, 순회 횟수를 줄이는 구조 변경이다. 효과의 크기는 새 kernel benchmark가 결정한다.

### 4.2 Immutable prepared data / SoA

출생 후 바뀌지 않는 ray geometry에서 매번 반복하는 `mu * mu`, `1 - mu²` 같은 값은 같은 binary64 연산으로 한 번 준비할 수 있다. 원 birth weights·reflection·source frame과 old isotropic/physical anisotropic stock은 그대로 둔다. 준비 배열은 기존 데이터의 표현이며 새로운 projection이나 재가중이 아니다.

공통 부분식 제거와 대수적 식 변형도 구분한다. `exp(2 * (b - birth_b))`를 `exp(2*b) * exp(-2*birth_b)`로 바꾸면 실수 항등식은 성립하지만 반올림과 overflow/underflow 경로가 달라진다. 그런 후보는 원 연산 순서 보존 후보와 분리해 gate를 적용한다.

### 4.3 동일 point의 bank-local cache

캐시 key에는 저장하는 값에 영향을 주는 모든 입력을 넣는다. 가장 보수적인 시작점은 `x`와 state 각 성분의 `to_bits()` 및 immutable bank generation이다. birth event로 새 bank를 만들면 이전 bank의 값은 사용하지 않는다. 근접한 state를 같다고 판정하는 tolerance는 추가하지 않는다.

RHS, explicit F_t, JVP가 공유하는 energy/pressure 또는 Jacobian 계수는 같은 point에서 재사용할 수 있다. Jacobian 계수 J를 캐시하면 각 direction v에 대해 새로 Jv를 계산한다. **이미 계산한 Jv 자체를 캐시한다면 v도 key의 일부**다. 비공유 cache는 worker별 bank에 둬서 mutable state와 다른 이력의 callback이 섞이지 않게 한다. cache hit/miss와 실제 kernel 호출 수를 기록하면 시간을 줄인 원인이 관측 가능하다.

### 4.4 Elementwise SIMD와 coarse parallelism

SIMD는 준비된 SoA에서 독립적인 ray 값을 계산하는 부분에 적용한다. lane별 sqrt/div, 곱셈·덧셈 순서, 나머지 scalar tail, 원순서 reduction을 각각 명시한다. 별도 검증을 하지 않은 FMA, reciprocal approximation, horizontal sum을 묵시적으로 섞지 않는다. scalar fallback과 실제 실행 target feature를 결과에 남긴다.

병렬화는 독립적인 history 또는 benchmark case를 단위로 시작한다. 각 solver의 event 순서와 immutable bank는 내부적으로 순차 관계를 유지한다. worker 개수는 현재 실제 8 CPU·8 GiB와 사용자 상한 이내로 고정하며, build·outer jobs·library pool이 중첩되어 한도를 넘지 않게 한다. 병렬 throughput과 단일 history latency는 서로 다른 측정으로 보고한다.

## 5. 선택에 사용할 근거와 남은 일

| 후보 | 지금 확보한 근거 | 다음 단계의 관측·판정 |
|---|---|---|
| Streaming Neumaier | 작은 accumulator로 보정합 가능; 기존 per-component 연산 그래프 보존 가능 | 할당 수·kernel 시간·bit 또는 수치 identity |
| Prepared SoA | immutable geometry의 공통 계산을 이동할 수 있음 | 준비 비용과 반복 평가 비용, old/birth data identity |
| Exact point cache | 같은 순수 함수 입력과 bank에 대한 계산 재사용 | hit/miss, JVP·RHS·F_t별 호출 수, event invalidation |
| SIMD sqrt/div | stable 공식 intrinsic/API가 존재; reduction과 분리 가능 | scalar/SIMD 비교, CPU feature, fallback/tail, 과학 gate |
| 독립 job 병렬화 | 공식 bounded pool API와 독립 작업 분할 | 고정 worker에서 throughput·메모리·출력 identity |
| Superaccumulator / approximate Jacobian | 별도 문헌과 수치 계약이 필요함을 확인 | 현재 우선 구현으로 채택하지 않음; 필요가 생기면 다른 후보로 평가 |

SUNDIALS의 이전 `SIM.html` 경로와 anchor 변형은 `CRAWL_NOT_FOUND`를 반환했다. 두 응답을 보존하고 이 경로를 근거에서 제외했다. ODE 근사 재사용의 범위 구분은 실제 받은 EPIRK 원문으로 뒷받침했다. 추가 재시도나 검색은 하지 않았다.

**R2의 반환 지점은 위 후보 중 구현할 연산·캐시 계약을 부모가 선택하는 곳이다.** 현재 자료로 kernel speedup, portable speedup, 새로운 continuum 정확도, physical MD14 feedback 또는 production/full EoR/merge를 승인하지 않는다. 기존 gate와 과학 의무는 [S10 계약](../../../bass/research/bass_isotropy_response_20261018/S10_OPTIMIZATION_KO.md)에 고정되어 있다.

## Skill context used

PhysMath Research Loop **1.3.0**의 `SKILL.md`, `STAGE_SELECTION.md`, `references/POLICY_INTEGRATION.md`, `references/SUBAGENT_MODE.md`, `references/STAGE_GUIDE_KO.md`의 R2 정의 및 `references/THEORY_LOOP.md`의 R2 완료 조건을 실제 읽었다. Exa Search의 `SKILL.md`, `references/searching.md`와 code/paper/source-quality 지침을 읽었다. 절대 경로와 hash는 [CHECKPOINT.json](CHECKPOINT.json)에 기록했다.

적용 결과는 R2에 한정한 source별 재사용 연결, 검색 수와 실제 검토 수의 구분, 원 source/version 보존, 한 번의 bounded 조사, 실패 경로 종료, 과학·구현 미실행의 정확한 기록이다. 이 하위 작업에서 후속 연구 단계나 재검토 agent를 시작하지 않았다.
