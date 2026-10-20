# S10 최적화 연구 — 현재 계약과 단계 기록

## 선택한 범위와 기준

2026-10-20 사용자 추가 요청에 따라 BASS의 현재 S9 Rust cohort/ODE client를 대상으로 외부 문헌·코드 재사용(R2), 코드·수식 대응(C2), 알고리즘/병렬화 설계(C3/C4), 실제 최적화 구현과 검증(C5–C9), 단계별 배송과 실행 인계(C10)를 수행한다. C1은 아래 baseline/수용 조건이다. 기존 물리 이론의 R1–R10 전체를 새로 반복하지 않는다. 이번 명시적 요청으로 한 최적화 연구 주기를 열며, 끝난 뒤 다음 주기를 자동 시작하지 않는다.

기준 실행 source는 `4b30957cb008aad8019bb1a673937fc67bd017e8`, 결과 publication은 `a40311796f9aac5ea5e0e58c630bee2a78443353`다. 기존 S9 실제 8/8 이력·140 gate 판정·독립 검토는 재사용한다. 새 성능 비교를 위한 반복 측정은 목적·입력·반복 수가 다른 사전등록 benchmark로 구분하며, 예전 완료 캠페인을 확인 목적으로 반복하지 않는다.

## 고정하는 과학 계약

- Non-tilted axisymmetric Bianchi I, (-,+,+,+), a_perp=a exp(-b), a_parallel=a exp(2b), s=dot b, Sigma=sqrt(3)|s|/H.
- Fixed spectral owner `0e25846433170d0f420c4cda44a0bedbf02cd177`; actual VigilODE `a21d573980f66fe02891bd216153443b5352f921`.
- 기존 광자장·physical anisotropic stock 및 모든 birth data는 immutable. 새 명시적 isotropic birth만 양의 P24 admission을 적용한다. Reflection/source frame/정확한 moment gate `3/10^15`는 유지한다.
- Hamiltonian 1e-11, cohort energy 1e-11, birth energy 1e-13, donor endpoint 3e-14, fine reference abs1e-9, clock abs1e-12의 기존 과학 gate는 완화하지 않는다.
- 최적화는 같은 수학적 문제의 구현/스케줄 변경이다. 근사·reassociation·SIMD reduction이 roundoff를 바꾸면 byte identity와 numerical/scientific equivalence를 구별해 판정한다. Fast-math나 음수 weights로 gate를 우회하지 않는다.

## C1 목표와 수용

먼저 allocations·cohort kernel·같은 (x,state,bank)의 반복 evaluation·출력/직렬화·birth exact arithmetic 비용을 구분한다. 후보는 allocation 제거, algebraic common subexpression, immutable prepared data/SoA, deterministic SIMD/chunking, bank-local cache, 독립 job 병렬화다. 측정 결과에 따라 적절한 후보만 채택하며 모든 방법의 speedup을 미리 주장하지 않는다.

속도는 release build의 동일 입력·동일 정확도에서 warmup과 반복 표본을 고정해 비교한다. 초기 compile 비용과 scientific kernel/whole-history 시간을 분리한다. 공유 container의 단회 관측을 portable speedup으로 일반화하지 않는다. 측정된 allocation/작업량/출력 크기/메모리 관측과 throughput/latency를 각각 기록한다.

추가 worker<=16, RAM16GiB, 추가 disk4GiB, 개별job1800초. 현재 실제 cgroup은8 CPU·8GiB이므로 그보다 큰 병렬 실행을 요청하지 않는다. 기본 build jobs2, 중첩 threading 억제, 기존 owner 작업 보존. 이미 취득한 Rust1.94.1, pinned source, locked vendor와 기존 target을 재사용한다.

## 단계별 현재 상태

| 단계 | objective 상태 | 게시 | 이중 백업/readback |
|---|---|---|---|
| C1 목표·baseline | 계약 작성 완료; 현재 source/results identity 재사용 | 진행 중 | 진행 중 |
| R2 외부 문헌·코드 재사용 | 조사 시작 | 미완료 | 미완료 |
| C2 코드·수식·비용 대응 | 조사 시작 | 미완료 | 미완료 |
| C3 알고리즘·수치 설계 | 대기 | 미완료 | 미완료 |
| C4 병렬화·실행 DAG | 대기 | 미완료 | 미완료 |
| C5 구현 | 대기 | 미완료 | 미완료 |
| C6 구현 검증 | 대기 | 미완료 | 미완료 |
| C7 과학 검증 | 대기 | 미완료 | 미완료 |
| C8 정확도 대비 성능 | 대기 | 미완료 | 미완료 |
| C9 독립 검토 | 대기 | 미완료 | 미완료 |
| C10 판정·인계 | 대기 | 미완료 | 미완료 |

실제 MD14 공급부/응력 closure와 native Einstein feedback, P6 제약, 전체 reactive finite-bin spectral history 및 넓은 continuum angular 보증은 기존의 미완료 과학 의무로 유지한다. 이번 사용자의 최적화 우선순위는 그 의무들을 완료했다는 의미가 아니다.
