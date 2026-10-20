# S10 C9 실제 독립 검토

## 판정

**현재 고정 source와 등록 workload의 code·과학 결과·성능 통계 및 수정된 보고서는 `PASS_SCOPED`다.** 변경 source에서 현재 수치 계약을 위반하는 구체적인 결함은 발견하지 않았다. 부모의 분석 함수를 호출하지 않고 저장 RAW에서 수행한 155개 검사는 모두 통과했고, 원 과학 gate 68/68도 직접 재계산했다. 보고서 표현 finding 한 건은 같은 검토 안에서 수정 내용을 직접 확인하여 닫았다.

문서 finding `C9-DOC-01`(부모 ID `F1_PREPARED_REPRESENTATION`)은 `S10_RESULTS_KO.md` §3의 prepared 행이다. 수정 전에는 “immutable mu², 1-mu², weight를 SoA로 준비”라고 썼지만 실제 `PreparedCohort`에는 `z=mu²`와 `alpha=weight`만 있다. `1-z`는 ray 평가 중 계산한다. 부모가 C7/C8 publication `26e9e1ba8f39788d98ec33c60f6e9fd2605f8b8a` 뒤 **“immutable mu², weight를 SoA로 준비; 1-z는 평가 시 계산”**으로 수정했다. 이 reviewer가 실제 문구, 이전 문구 부재와 수정 후 SHA256 `9229dc6d9763dfb12a48cd2766172e5fc0518d68b09006727e9c629ec9ec6873`을 직접 확인했다. 따라서 `CLOSED_VERIFIED_SAME_PASS`다. code·tolerance 변경이나 ODE/benchmark 재실행은 없었다.

이 C9는 한 번의 범위가 고정된 검토다. source 계약 전문 분담과 원자료 계산을 병렬로 나눴으며 새 검토 주기를 열지 않았다. C4 사전등록을 담당했던 reviewer가 별도 Python 계산을 작성하고, 최적화 구현에 참여하지 않은 source 전문 담당자가 변경 코드를 검토했다. 이는 계산·source 검토의 독립성이고, 별도의 실험실·compiler·hardware에서 재현했다는 뜻은 아니다.

## 식별과 확인 범위

| 항목 | 식별자 |
|---|---|
| 최적화 source | `d5a173644f5c7c0dbe9eb8757dfc4ccad6c4f4c8` |
| source tree | `95785be65c196c68d61b79dafb32f4cedfd7702d` |
| source/input manifest SHA256 | `4ac631dced7e1d4fdc8ce63d076dfe15bb38bde7040029644e2c34f30b1ebc17` |
| 원 S9 source | `4b30957cb008aad8019bb1a673937fc67bd017e8` |
| 고정 spectral owner | `0e25846433170d0f420c4cda44a0bedbf02cd177` |
| 실제 VigilODE | `a21d573980f66fe02891bd216153443b5352f921` |
| timing binary SHA256 | `375d95ae4dfdd96fef96c8b96a17fa966e0cd6b14063b14a79d867c2233f8265` |
| allocation binary SHA256 | `4ab9bf3013f0ef599a9bd06b5e6458f04ca697c727250e58bc8750ca6f8474b3` |

manifest의 37개 파일을 직접 읽어 bytes·SHA256·Git blob을 재계산했다. 원 S9 사전등록의 13개 source hash도 일치한다. 실제 build runtime의 S9/S10 Rust source·Cargo manifest/lock와 `balance_p24.rs`를 repo source와 직접 대조했다. 원 lock의 97개 package record는 새 lock 안에서 그대로 보존된다. 저장된 Git Data readback의 commit/tree/ref와 각 process의 source manifest·Git receipt·log·binary hash를 확인했다. 이 검토가 원격 Git 조회를 새로 실행한 것은 아니다.

build, targeted tests, micro, serial history, parallel, allocation build, allocation은 모두 `r1`, exit0, source `d5a173...`로 기록되어 있다. 기록된 build/test compile 구간과 실제 timing 구간은 겹치지 않는다. release targeted tests 11/11 통과 log를 읽었고 다시 실행하지 않았다. timing binary는 allocation feature 없이 보존된 별도 binary다.

## PHYS-MATH: 보존한 문제와 직접 검산

Non-tilted axisymmetric Bianchi I, signature `(-,+,+,+)`, \(a_\perp=a e^{-b}\), \(a_\parallel=a e^{2b}\), \(s=\dot b\), \(\Sigma=\sqrt3|s|/H\)를 유지한다. 원 donor closure·birth schedule·P24 admission·spectral owner는 변경되지 않았다. 기존 anisotropic/isotropic stock을 새 source처럼 재가중하는 경로가 없다.

검토 코드는 네 release baseline의 **612개 저장 관측**에서 다음을 직접 계산했다.

- \(C=h^2-y^2-E_d-E_r-\Lambda\)와 해당 scale, \(\Sigma\), raw field의 일치.
- immutable cohort들의 닫힌식 \(E_i=E_{i,b}\exp[-4(x-u_i)]\langle R(b-b_{i,b})\rangle\)와 stress를 `math.fsum`으로 합성한 독립 관측값.
- 저장 point에서만 complex-step 방향미분을 계산하여 \(E_r'+4E_r+2(y/h)\Pi=0\) 확인. ODE 적분은 없다.
- 두 closed 입력의 **64개 birth**를 `Fraction`의 exact binary64 유리수로 다시 평가한 normalization·P2·P4와 원 certificate의 완전 일치.
- 양의 energy/weights, 정확한 reflection, old-stock bytes/digests, birth digests, state/energy/birth-b 결속, zero state jump와 right-bank event 출력.
- closed case당 32 births/33 fresh segments, FLRW당 0 births/1 segment, 각 입력의 153 output times, 실제 JVP/Ft 또는 direct/clock counters.
- 저장 S8 reference 및 analytic FLRW에 대한 h/b/y 차이, donor endpoint와 clock gate.

동일한 네 입력에 적용한 원 gate 68개가 모두 통과한다. 68은 검사항목 수이고 독립 과학 실험 수가 아니다. 대표 RAW가 여섯 mode에서 완전히 같으므로 같은 관측을 24번의 새로운 과학 검증으로 다시 세지 않았다.

| 입력 | 최대 h/b/y reference 절대차 | Hamiltonian 상대오차 | 독립 fsum complex-step energy 상대오차 | clock 절대차 |
|---|---:|---:|---:|---:|
| closed MF | 1.4327428132787645e-13 | 3.941328494994859e-13 | 1.034074613179427e-15 | 0 |
| closed small/clock4 | 1.7108536809473662e-13 | 4.706398368875746e-13 | 9.598184557643717e-16 | 1.3322676295501878e-15 |
| FLRW MF | 3.35231842285566e-13 | 7.87756038618741e-13 | 8.765746211363714e-16 | 0 |
| FLRW small/clock4 | 3.681499549657019e-13 | 8.730986626880304e-13 | 8.765746211363714e-16 | 9.992007221626409e-16 |

최대 event energy 상대오차는 `2.1805516491514178e-16`, donor endpoint 상대차는 0이다. 독립 real-energy 재계산과 원 관측값의 최대 상대차는 `2.1001018840442804e-16`, stress 최대 절대차는 `1.3010426069826053e-18`이다. constraint와 event-energy raw field는 직접 재계산과 정확히 일치했다.

원 분석의 energy identity 최대값 `2.8503909994791273e-15`를 지우거나 이 독립 계산의 더 작은 수치로 대체하지 않는다. 두 계산은 미분 항의 합산 방식을 달리하므로 rounding 잔차의 최대값도 다르다. 두 결과가 모두 기존 `1e-11` gate를 통과한다는 것이 현재 결론이다. derivative·operator 또는 과학 허용오차를 바꾼 것이 아니다.

## PHYS-MATH-CODE: 바뀐 경로

[source 전문 검토](source_contracts_note.md)는 원본의 네 extraction 구간과 실제 candidate runner를 대조했다. runner 전체는 원 excerpt에 선언된 다섯 callback/mode 치환만 적용한 결과와 정확히 같다. birth/P24, exact gate, positive donor transfer, observation, event right-bank 교체, counters와 failure 처리의 나머지는 보존된다. baseline은 원 S9 `run`을 직접 호출한다.

`OrderedSum`은 원 Neumaier update 분기·괄호·마지막 보정합을 유지한다. channel을 interleave하지만 각 channel에 들어가는 node/cohort 순서는 같다. scalar term과 SIMD term의 곱셈·나눗셈 parenthesization도 원 source와 같다. prepared data는 μ²와 weight뿐이며 x−u나 b−b_birth의 지수 차이를 별도 exp 곱으로 분해하지 않는다.

bank는 evaluator가 소유한 private immutable Arc다. cache key는 x/h/b/y 네 `to_bits`이고 RHS/JVP slot은 각각 최대 한 entry다. 새 Jv 방향은 매번 원 3-term ordered dot product로 계산한다. invalid direction이 invalid point보다 먼저 반환되는 원 error 우선순위를 보존하고, 실패 evaluation을 cache에 저장하지 않는다. event 이후에는 새 evaluator와 cache를 만든다.

SIMD는 in-bounds four-lane load 뒤 lane0→3 순서로 누적하고 scalar tail을 처리한다. 실제 원소 연산은 AVX packed f64이며 AVX2 runtime guard가 보수적으로 적용된다. 현재 micro proof는 SIMD modes에서 `Avx2`가 실제 선택되었음을 기록한다. 저장 disassembly에서 해당 symbol의 `vsqrtpd`, `vdivpd`와 FMA mnemonic 부재를 독립 확인했다. 이 검토는 vendor/upstream binary 전체가 FMA를 쓰지 않는다고 주장하지 않는다.

`scientific_value`는 top-level `elapsed_seconds`만 제거한다. 이력의 숫자 lexeme를 그대로 보존해 canonical JSON SHA256을 독립 재구성했고 24개 대표 RAW 모두 실제 warmup digest와 일치했다. signed zero를 포함한 모든 scientific float bits도 같은 release의 baseline과 같다. 네 baseline은 저장 S9 debug RAW와도 timing 필드 외 전체 과학 값이 실제로 같았다. 이 사실을 다른 compiler·hardware·입력으로 확대하지 않는다.

## 실제 표본과 통계

| 항목 | 저장 원자료에서 확인한 수 |
|---|---:|
| kernel timed batches | 1,260 |
| kernel proof records | 108 × 64 queries |
| 별도 diagnostic records | 108 × 64 calls |
| history timed / warmup records | 280 / 24 |
| parallel timed / warmup batches | 42 / 6 |
| preparation timed samples | 378 |
| allocation rows | 108 |

모든 micro/history pair의 후보 rotation·실제 AB/BA 순서, round0–6, 인접 baseline, 고정 calls를 원 JSONL 순서에서 검증했다. preparation mode rotation과 parallel 순서도 그대로 일치했다. 280개 timed history digest는 대표 RAW에, 42개 parallel batch의 네 digest는 입력 index 순서의 serial 대표에 모두 일치한다. micro proof 18조건에서 여섯 mode의 output-bit digest가 같다.

90개 micro paired 통계군, 20개 history paired 통계군, 6개 parallel latency/throughput 통계군, 54개 preparation 통계군을 직접 재계산했다. median·Q1·Q3·IQR·원 7표본·paired ratio는 부모 분석과 일치한다. 요약값 계산의 수 ulp 이내 반올림 비교는 통계 표현에만 적용했으며 scientific output bit equality를 완화한 것이 아니다.

| history의 `simd_cache` | paired median | Q1–Q3 | 해석 |
|---|---:|---:|---|
| closed MF | 2.9733520597566536 | 2.69010799897751–3.1533799035904444 | 현재 workload에서 이득 관측 |
| closed small/clock4 | 1.0551887909522575 | 0.9572132242316267–1.2425557671751304 | 일관된 이득을 승인하지 않음 |
| FLRW MF | 4.114511379999065 | 3.6590591506345236–4.659804932593214 | 현재 workload에서 이득 관측 |
| FLRW small/clock4 | 1.5320070843534945 | 1.4110331424291012–1.5465587280835074 | 현재 workload에서 이득 관측 |

changing-state n16/cohort2 `simd_cache` 중앙비 `0.9498173837599284`는 실제 성능 회귀로 남긴다. JVP reuse trace는 한 base point당 16회 호출하는 특별한 조건이다. diagnostic의 64회 JVP에서 exact-cache modes의 full evaluation은 4회, hit는 60회이며 다른 modes는 64회다. 이를 전체 history 시간 점유율이나 자동적인 16배 가속으로 환산하지 않는다.

allocation 108 rows는 모두 등록한 64회 평가다. baseline의 allocation/reallocation 횟수는 `64*(cohorts+1)`와 맞고 다섯 후보의 평가 구간은 0회다. 이 계측은 별도 binary이며 setup·caller clone·whole-history 전체 할당 또는 peak memory를 뜻하지 않는다.

parallel `simd_cache`의 pool 포함 median batch는 workers1/2/4에서 각각 135.934766ms, 65.453537ms, 63.336020ms다. workers2와4의 차이는 작고 네 job의 길이도 다르다. worker block이 별도 시점에 측정되었으므로 인접 causal pair나 초선형 scalability의 증거로 표현하지 않는다. shared container의 IQR은 confidence interval이 아니다. 준비 표본의 sub-µs 해상도, 짧은 cache micro 표본, fixed sample 수를 유지한다.

## 보고서·자원·출판 범위

새 `S10_RESULTS_KO.md`의 주요 성능 수치, 회귀·불확실성, callback counters, 과학 최대 오차와 scope를 원자료와 대조했다. `C9-DOC-01` 외에 구체적인 수치·범위 위반은 발견하지 않았다. 세 그림은 부모가 실제 시각 검토한 `VISUAL_AUDIT.json`을 재사용하며 이 reviewer가 다시 렌더링하거나 시각 검토한 것으로 표시하지 않는다.

`EXPERIMENT_POSTCHECK.json`은 runtime+execution의 일반 파일 logical bytes `1,563,541,784`, 전체 workspace 일반 파일 logical bytes `2,176,546,393`, OOM/OOM-kill 0을 기록한다. 이를 snapshot으로 읽었다. process-lifetime peak, filesystem allocated blocks 또는 task-exclusive memory로 확대하지 않는다. shared cgroup의 memory `max` event가 0이라고 주장하지 않으며 RSS의 최대 개별 child 수치도 동시 process-tree 합산 peak가 아니다. 원 user caps와 현재 실제 8CPU/8GiB 환경, workers1/2/4·build jobs2의 범위를 유지한다.

C9의 `RESULT_VALIDITY`와 고정 실행의 `PROVENANCE_VALIDITY`, 수정된 보고서 representation은 현재 범위에서 통과한다. C9 Git publication·cloud readback은 부모의 다음 checkpoint이며 이 문서가 완료를 선언하지 않는다. 특히 Drive blocked를 이중 백업 성공으로 바꾸지 않는다.

원 S9 broader evidence는 그대로 재사용한다. P6 제약, 넓은 finite-d continuum angular 보증, 전체 reactive finite-bin/spectral history 수렴, 실제 owner 공급부/Einstein feedback의 남은 과학 의무는 이 최적화 결과로 닫히지 않는다. REI production·full EoR·merge 또는 새 연구 주기를 승인하지 않는다.

## 재계산 산출물

- [INDEPENDENT_REVIEW.py](INDEPENDENT_REVIEW.py): 외부 import된 BASS analyzer·subprocess·network·solver 호출 없이 저장 데이터만 계산.
- [INDEPENDENT_RECOMPUTATION.json](INDEPENDENT_RECOMPUTATION.json): 155 checks, 원자료 hash, 24개 재구성 digest, 68개 science gate, 64개 exact certificate, 전체 재계산 통계.
- [source_contracts_note.md](source_contracts_note.md): source 전문 분담의 실제 diff·연산·cache·SIMD 검토.
- [C9_REVIEW_RECEIPT.json](C9_REVIEW_RECEIPT.json): 식별자, 실행 범위, 단일 문서 finding과 같은 pass의 수정 확인.

검토 중 새 compile, unit/integration test, ODE, benchmark, 외부 문헌 검색, repo/source 수정은 모두 0회다. 실제 실행한 것은 기존 RAW에 대한 독립 Python 계산 한 번과 문서/receipt 작성이다.
