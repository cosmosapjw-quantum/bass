# ACCEL01 — 완료한 split729를 재사용하는 C15 계산 경로 최적화

2026-10-21 KST. BASS PR176 / REI PR213 완료 결과에서 이어지는 별도 구현 단위다.
원 결과와 source는 research/rei_sigma_pi_pilot_20261021에 그대로 보존한다.

## 완료 기준

1. 최신 branch/PR/대화/백업의 유효 근거를 조사하고 source identity·물리 lane을 구분한다.
2. 동일한 (x,b)와 고정된 per-case quadrature에서 원 massive_source_3moments 결과만 재사용한다.
3. 완료729를 case 단위로 인식하는 계획을 만들고 새거나 미완료인 입력만 가용 자원에 배분한다.
4. 원 이산화·reduction 순서·closure·허용오차·matter/radiation 분리를 유지하고 변경 의존성만 검증한다.
5. 상세 timing benchmark 없이 실제 검산·독립 검토·DAG·게시·백업·두 handoff를 완결한다.

## 현재 scope

non-tilted LRS Bianchi I, a=0.1999→0.2, warm conditional C15 physics, massive nonbaryonic Vlasov matter와 gamma+massless-nu+UV radiation. Half-contraction norm과 signed 좌표를 함께 보존한다. 원 pilot의 729 trajectories / 243 groups / 47,385 rows는 재실행하지 않는다. 비교 검증에 필요한 새 kernel 평가와 최소 short-step 검산은 새 최적화의 의존성 검증이다.

BASS baseline HEAD 26f4a89a54462c4e7c5705f281f187f33f45166a, REI baseline HEAD d32cd99fa19c65aa1ca63dbc8aab8741834270e8, 실행 source82372ed8db68085868603d4267a630ed9cde6abb, 물리 owner80825585f9fe31d2ee0d5af545ada3fa1f52be72.

## 구현·검증 결과

- `cached_context.py`: 원 C15 finite-mass 구적의 exact-bit per-model cache. 불변 배열 값과 dtype/shape/strides/layout binding을 검사한다.
- `work_plan.py`: 완료729를 pinned 과학 결과로 재사용하고 새 입력만 계획한다. 실제 기본 CLI는 completed729/pending0/jobs0이다.
- `batch_worker.py`: 원 `shared_executor` manifest, group당 준비 한 번, case별 atomic receipt와 partial-failure resume, 동시 요청 잠금.
- 최종25 tests PASS, C9 한 차례29 guard probes PASS, baseline112 파일 불변. 새 custom case 하나의2-step 연결 검산도 원8gates PASS다.
- 상세benchmark와 기존729 full-trajectory 재실행은0이다. 실제 call reuse를 speedup 배율로 바꾸어 주장하지 않는다.

결과·유도·원전·자원·검증은 [REPORT_KO.md](REPORT_KO.md)와 [THEORY.md](THEORY.md), 실제 상태는 [DAG.json](DAG.json), [delivery/](delivery/)에 있다. 다음 실행은 [CODEX_HANDOFF.md](CODEX_HANDOFF.md), 다음 대화는 [NEXT_THREAD_HANDOFF.md](NEXT_THREAD_HANDOFF.md)를 사용한다.

## 채택한 결정

- S10 exact-bit cache와 RUN19 prepared context의 실제 패턴을 현재 C15 의존성에 맞춰 적용한다.
- Numpy reduction 재결합·새 interpolation table·새 solver·LRS40→8 다른 모델의 축소는 이번 구현에 도입하지 않는다.
- REI PR198의 z20→4 collisionless625+606과 C21L은 별도 결과로 관리한다.
- NCP64CPU/128GiB는 target이다. 현재 측정값과 과거 NCP 관측은 evidence에서 분리한다. 타 작업이 있다는 이유로 중지하지 않고 새 작업 admission만 live headroom에 맞춘다.

진척·실제 검증·저장 상태는 DAG.json과 delivery/에 기록한다.
