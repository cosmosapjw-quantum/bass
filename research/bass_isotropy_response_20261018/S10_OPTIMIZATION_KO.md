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
| C1 목표·baseline | 완료 | `62d6bc14` full tree readback 완료 | Dropbox 전체 bytes·CRC·11 payload 일치; Drive connector 무응답으로 미완료 |
| R2 외부 문헌·코드 재사용 | SciSpace 2 + Exa 3 검색, primary 9묶음 관련 절 검토 완료 | `8138a014` full tree readback | Dropbox 전체 bytes·35 payload 일치; Drive 미완료 |
| C2 코드·수식·비용 대응 | 원 source/counter 대응 완료; 실제 시간 점유율 주장 없음 | `8138a014` full tree readback | Dropbox 전체 bytes·35 payload 일치; Drive 미완료 |
| C3 알고리즘·수치 설계 | 수치·소유권·cache 계약 완료 | 대기 | 대기 |
| C4 병렬화·실행 DAG | 고정 7회 paired benchmark 사전등록 완료 | 대기 | 대기 |
| C5 구현 | 신규 crate 구현 완료; compile/test/benchmark 미실행 | 대기 | 대기 |
| C6 구현 검증 | release build 및 targeted11/11 PASS | 현재 checkpoint | Dropbox 대기; Drive 미완료 |
| C7 과학 검증 | 대기 | 대기 | 대기 |
| C8 정확도 대비 성능 | 대기 | 대기 | 대기 |
| C9 독립 검토 | 대기 | 대기 | 대기 |
| C10 판정·인계 | 대기 | 대기 | 대기 |

실제 MD14 공급부/응력 closure와 native Einstein feedback, P6 제약, 전체 reactive finite-bin spectral history 및 넓은 continuum angular 보증은 기존의 미완료 과학 의무로 유지한다. 이번 사용자의 최적화 우선순위는 그 의무들을 완료했다는 의미가 아니다.

## R2/C2에서 선택한 구현

[R2 재사용 조사](evidence_s10/r2/R2_REUSE_KO.md), [C2 비용 지도](evidence_s10/c2/CODE_COST_MAP_KO.md)를 보존했다. 원8이력의 counter와 읽은 code를 대응한 정적 합계는 full eval 62,025회, angular node 방문 29,732,096회, moment 관련 Vec 구성 요청 1,138,493회다. P24는 distribution 평가 487,258회다. 이 값은 실제 malloc 계측·시간 점유율·RSS가 아니다.

실제 SIMD 후보는 stable std::arch의 runtime feature guard + scalar fallback이다. 확인한 Pulp0.22.3은 대안이며 이번 직접 채택으로 표시하지 않는다. Rayon1.12.0의 이미 잠긴 vendor를 독립 작업용으로 재사용한다. 기존 callback source·P24 owner·exact certificate는 수정하지 않고 별도 opt-in crate를 만든다. 모든 variant는 이력 관측·event·cohort·solver counter의 동일성을 검증한다. 성능 이득은 아직 측정 전이다.

## C3/C4/C5 실행 전 checkpoint

[C3 설계](evidence_s10/c3/C3_DESIGN_KO.md), [C4 사전등록](evidence_s10/c4/PREREG_KO.md), [machine protocol](evidence_s10/c4/BENCHMARK_PROTOCOL.json), [격리 crate](s10_optimization/README_KO.md)를 게시한다. 여섯 variant와 11개 targeted test는 작성되었으며 아직 실행 전이다. Kernel 1,260 paired timing samples와 preparation378, benchmark history496회(고유 물리 입력4개), 별도C6 run30회(예상적분23·예상입력실패7)를 고정했다. 원 완료 캠페인의 과학표본 수를 늘렸다고 보고하지 않는다.

읽기 전용 runtime preflight에서 새 sibling crate가 기존 vendor config를 상속하지 않는 점과 embedded test input 누락을 발견했다. execute.py는 명시 --config와 검증된 원 fixture의 create-only materialization을 사용한다. compile 실패나 과학 실패가 아니라 실행 전 준비 수정이다. 모든 실행은 원 repo execute.py에서 시작하며 새 source manifest·성공 build receipt·binary hash·C6 gate를 확인한다.

## C6 실제 구현 검증

Rust1.94.1 release/offline/locked/jobs2 빌드1회가 164.782401714초, exit0으로 끝났다. Timing binary SHA256은 `375d95ae4dfdd96fef96c8b96a17fa966e0cd6b14063b14a79d867c2233f8265`이며 allocation-probe feature는 꺼져 있다. 원고정VigilODE의 dead-code 경고4개는 보존했고 신규 compile failure는 없다.

Targeted test는 `--test-threads=1`로 11/11 PASS. signed-zero와 전체 cache key, 새 bank/same point, 변하는 JVP 방향, 원 오류 우선순위, scalar fallback/tail, 큰 공통 x/u, 짧은 history와 전체 과학 receipt identity, worker cap/order를 확인했다. 테스트 코드에서 실행된 run30회는 정상23회와 예상 input failure7회이며 performance 표본과 구분한다. AVX2 term symbol의 실제 binary에는 packed sqrt/div가 있으며 FMA instruction은 없었다. 이 검사는 해당 symbol 범위이고 upstream 전체 binary의 FMA 사용을 금지했다는 의미가 아니다.

원source37파일 hash와 owner repo/runtime bytes가 유지됨을 확인했다. 아직 고정 performance timing은 수행하지 않았다.
