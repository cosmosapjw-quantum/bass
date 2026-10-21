# ACCEL02 — LRS massive moment의 반사쌍·융합 계산

작성일: 2026-10-21, Asia/Seoul. 과학 판정:
**PASS_SCOPED_LOCAL_NUMERICAL_EQUIVALENCE**.

## 1. 이번에 끝낸 일

완료된 warm C15 729-case pilot과 ACCEL01을 재사용하고, massive Vlasov
모멘트의 cache miss 계산을 C++17로 연결했어. 원래 96×32 quadrature의
각도 노드 32개를 16개 반사쌍으로 묶으며, 세 모멘트를 한 순회에서 계산해.
실제 128 GiB NCP용 새 scheduler를 만들 필요 없이 기존 pending-case
executor의 자원 관측·부분 완료·재개 기능을 그대로 사용해.

실행 가능한 코드는 이미 다음 Stage B commit에 있어.

| 저장소 | 게시 위치 | 실행 소스 commit |
|---|---|---|
| BASS | https://github.com/cosmosapjw-quantum/bass/pull/178 | `7fe0e25a28c0e48110c522378e203ffb934cc504` |
| rei_bianchi | https://github.com/cosmosapjw-quantum/rei_bianchi/pull/215 | `231df3ab717dbc112f63b77953f64def08e9bcb5` |

Branch는 `research/rei-sigma-pi-native-moments-20261021`, 새 경로는
`research/rei_sigma_pi_native_moments_20261021`이야. 뒤따르는 Stage C
commit은 심사·보고·인계·delivery 기록을 보충하며 검증된 실행 코드는
바꾸지 않아. 두 PR은 draft이고 merge는 하지 않았어.

이번 판정은 고정된 유한 검증점과 짧은 warm 궤적의 수치적 동등성이야.
NCP 실측 속도, 전체 729 native 재실행, 전역 오차 한계나 수렴을 뜻하지 않아.
정확한 주장 범위는 SCOPED_DECISION.json에 고정했어.

## 2. 연구 전에 확인한 새 결과

접근 가능한 4개 저장소의 branch 목록 871 refs를 이전 866과 전수 비교했어.
864개는 같은 head, 2개 변경, 5개 추가였어. 관련 대화 검색 단서 7개,
선별 Git 원문 28개(213,392 B), 실제 새 백업 2개 및 첨부 20개의 목록도
확인했어. 모든 branch의 모든 파일이나 접근하지 못한 비공개 대화를
읽었다는 뜻은 아니야. 정확한 coverage와 근거는 intake/에 있어.

| 새 근거 | 확인 결과 | 이번 단위의 사용 |
|---|---|---|
| BASS177/REI214 | 문서·delivery만 8파일 변경. 실행 관련 11 Python 파일 및 원 pilot subtree 동일 | 최신 문서 상태를 수용하고 검증된 코드·완료 729 재사용 |
| BASS_CR92 | 새 NCP 98/98 완료, 이전 26+center 1을 합친 125좌표 분석 | PR147 collisionless z=20→4 별도 결과. C15 warm 수치 검증과 혼합하지 않음 |
| C21M 백업 | 98 raw seal/RESULT/history 결속 일치. 두 설명 문서의 run identity만 다름 | 실제 raw identity에 결속. 설명 문서 수정은 원 작업의 후속 의무 |
| C21M 분석 CSV | 126 B 및 SHA 차이가 정확히 LF↔CRLF로 설명됨 | 포장 차이로 기록, 물리적 실패로 해석하지 않음 |
| REI199 | 현재 Git은 joint 175 중 35 재사용, 140 nominal+3 refined 미실행과 237 연장 계약 | 237 완료라는 대화 단서를 실행 완료로 채택하지 않음 |
| HE82 | canonical 40 보고와 현재 raw 27/13 복구 중을 구별. C15는 기존 512행 재표현 | 새 warm sweep으로 세지 않음 |
| HH128/129, VigilODE | 저장 자료 벡터화·불변 연산자 등의 참고 구현 | C15에 성립하지 않는 collisionless 8→3 축약/FVM/Schur를 이식하지 않음 |

따라서 이번에 확인한 범위에서는 ACCEL01 이후 새 warm C15 sweep이 없었어.
이미 끝난 729 case/243 PASS/누락 0/history 47,385행을 그대로 기준으로 삼았어.
원래 a=0.1999→0.2의 조건부 warm 범위도 유지했어.

ACCEL01 Drive A는 후속 반환 ID `1GK5AjCvmbnVdDwDMRmz-_OhVReBE5sxn`와
248,613 B를 이번 직접 metadata로 확인했어. 원 중단된 제출의 완료·중복
여부와 full-byte 검증은 별개야. 이전의 미확인 상태를 과장 없이 갱신했어.

## 3. 왜 이 계산을 골랐나

ACCEL01은 같은 모델의 같은 binary64 (x,b)가 다시 요청될 때 원 계산값을
정확히 재사용해. 그러나 새로운 geometry의 모멘트 산술은 그대로 남아
있었어. 원 코드에서 32개 각도 노드는 ±mu 쌍이고, 현재 분포와 세 kernel은
mu²에만 의존해. 이 중복은 소스에서 직접 확인할 수 있었어.

반면 seed_for는 두 번의 작은 스칼라 초기조건 변환이어서 그곳을 큰
비용 원인으로 선택할 근거가 없었어. source/rate 준비, chemistry 또는
ODE의 시간 비중은 benchmark하지 않았어. 그 비중을 추정한 성능 배수도
제시하지 않아.

외부 지식은 실제 적용했어. SciSpace에서 Higham 1993 및
Ogita–Rump–Oishi 2005 원논문을 찾고, Exa로 저자 원문을 확보한 뒤
primary PDF를 읽었어. 부호가 바뀌는 모멘트에는 논문의 Neumaier
보상합 방식을 적용했어. 큰 새 solver dependency는 추가하지 않았고,
문헌의 다른 환경에서 측정한 속도 향상률을 이 코드에 전용하지 않았어.
[Higham 1993](https://nhigham.com/wp-content/uploads/2023/10/high93s.pdf),
[Ogita–Rump–Oishi 2005](https://www.tuhh.de/ti3/paper/rump/OgRuOi05.pdf).

## 4. 구성적 유도와 물리 해석

서명은 (-+++), 물리상수는 기존 차원 규약을 유지해. x=ln(a/a0), r=exp(-x),
u=mu²일 때

    R² = exp(2b)(1-u)+exp(-4b)u,
    p² = r²q²R²,
    E = sqrt(m²+p²),   v²=p²/E²,
    u_phys = exp(-4b)u/R².

원래 저장된 가중치 W에는 독립적인 matter seed (1+alpha_m P2(mu))가 들어가.

    J0 = r³ sum W E,
    J1 = r³ sum W E v²,
    J2 = r³ sum W E v²(3u_phys-1)/2.

반사된 노드의 kernel은 같으므로 원래 32개 항을

    sum(j=0..15) [W_j+W_(31-j)] K_j

로 묶을 수 있어. 원 32개 노드와 가중치가 모두 남아 있고, leggauss(16)으로
새 quadrature를 만드는 방식이 아니야. 실제 배열의 mu/mu²/P2/가중치
대칭성을 검사하고, 조건을 만족하지 않는 native 요청은 명시적으로 거절해.

같은 유한합을 직접 미분하면

    ∂x J0 = -3J0-J1,       ∂b J0 = -2J2

가 나와. dx/dt=H, db/dt=s를 넣으면 massive 성분의 에너지 보존식에서
anisotropic work가 -2sD_m로 나타나. 실제 LRS tensor를
sigma=diag(-s,-s,2s), pi_A=diag(-D_A/3,-D_A/3,2D_A/3)로 쓰면
sigma_ab pi_A^ab=2sD_A와 일치해.

기본 norm은 sqrt(A_ab A^ab/2)이고, 부호 있는
Sigma=sqrt(3)s/H, Pi_A=kappa_t D_A/(sqrt(3)H²),
kappa_t=8piG/c²를 사용해. 따라서 work/(H³/kappa_t)=2SigmaPi_A야.
Matter와 radiation의 D를 먼저 더한 뒤 total norm을 취하는 원 규약을 보존해.
작은 상쇄 잔차를 0으로 잘라내지 않아.

Wolfram 실제 평가기에서 세 parity residual과 두 미분 residual이 정확히 0,
tensor contraction이 2ds, positivity 범위가 -1≤alpha_m≤2로 나왔어.
양의 가중치에서 0≤J1≤J0, -J1/2≤J2≤J1도 유한합 자체의 진단 조건이야.
이 결과는 해당 성분의 quadrature와 work 부호를 확인하며 full Q^a closure를
새로 제공하지는 않아. 자세한 유도와 실제 CAS 코드는 THEORY.md 및
evidence/WOLFRAM_CHECK.json에 있어.

## 5. 실제 구현

| 파일 | 역할 |
|---|---|
| moments.cpp | 원 96×32 구적법을 96×16 반사쌍으로 평가, 세 모멘트 융합·Neumaier 보상합 |
| build_native.py | C++17 명시적 빌드, compiler/flags/source/binary/platform 기록 |
| native_context.py | 실제 parity·배열 조건 확인, ctypes 연결, 모델별 immutable folded 입력과 기존 exact cache 조합 |
| native_worker.py | native 선택을 plan/prepare/run-group에 연결 |
| ACCEL01 batch_worker.py | 선택적 BackendSpec만 추가. 기본 Python exact cache 경로 유지 |
| verify_native.py, verify_worker.py | 고정된 작은 수치 검증과 실제 worker 재사용 증거 생성 |

원 pilot, cached_context.py, work_plan.py, shared_executor.py 및 원 물리 gate는
수정하지 않았어. C++ 옵션은 -O3 -std=c++17 -fPIC -shared -fno-fast-math
-ffp-contract=off야. 보상합의 연산이 재배열되지 않도록 했고, GPU·OpenMP·MPI
또는 새 Python 패키지를 요구하지 않아. NCP에서 한 번 compile하는 binary는
해당 host의 실제 library hash와 함께 별도 backend identity에 들어가.

3072→1536은 miss당 에너지/sqrt 평가 지점 수야. full 96×32 중간 배열을 매번
만들지 않고 각도 16개의 factor를 공유해. 대신 모델마다 folded weight 등의 작은
준비 배열이 추가돼. 전체 메모리가 절반이 된다는 주장이나 전체 walltime 2배 가속,
SIMD 생성 보장은 하지 않아. 엄격한 보상합은 자동 벡터화를 제한할 수 있어.

## 6. 고정 기준과 실제 관측

허용 기준은 새 native 결과를 보기 전에 FROZEN_CONTRACT.md에 고정했어.
J2 또는 Pi_total≈0에서 relative error로 판정하지 않고, J0 기준 절대오차와
각 signed 관측량의 절대차를 사용했어. 기준을 넓히는 수정은 없었어.

| 검증 | 실제 관측 | 고정 기준/판정 |
|---|---:|---|
| 140 kernel점 max abs(deltaJ)/J0 | 3.0017696087628955e-16 | ≤1.4210854715202004e-14, PASS |
| 3 미분점 max 정규화 잔차 | 3.730718793634552e-12 | ≤2e-9, PASS |
| 5 original/native 쌍, 각 2 step | 10궤적의 원 8 gate 모두 PASS | 원 기준 그대로 |
| signed Sigma 최대차 | 4.400213117869973e-23 | ≤5e-14 |
| signed Pi_m 최대차 | 1.1777890328282316e-20 | ≤5e-14 |
| signed Pi_r 최대차 | 5.169878828456423e-26 | ≤5e-14 |
| signed Pi_total 최대차 | 1.1777890328403265e-20 | ≤5e-14 |
| 정규화 total work 최대차 | 3.268686181550334e-24 | ≤5e-14 |
| H, Tgas, ionization 비교 | 저장된 비교에서는 차이 0 | 각 고정 기준 PASS |
| 기존 worker unit 검사 | 9개 PASS | 변경된 dispatcher의 영향 검사 |
| 실제 native worker | 1 case 계산, 다음 실행은 같은 case 재사용 | 결과·receipt 동일 |
| 기본 729 plan | 완료 729, pending 0, jobs 0 | native build/load 없이 종료 |

compiler 호출은 1회, 새 solver 실행은 original 5+native 직접 5+worker 1이었어.
두 번째 worker는 case를 다시 풀지 않았어. 상세 benchmark와 완료 729 재실행은 0이야.
warm 비교는 전체 729의 64 step 결과를 대체하지 않는 2 step 연결 검산이야.

독립 Astra 심사는 저장된 raw 값으로 140점/3점/20비교행과 10궤적의 gate를
재계산하고, source/binary/43개 worker binding을 대조했어. 새 solver나
suite를 실행하지 않았고, 차단 결함 0·수정 0·심사 1회로 끝났어.
evidence/INDEPENDENT_REVIEW.json과 REVIEW_KO.md에 정확한 근거가 있어.

## 7. 자원과 동시 작업

샌드박스 관측값은 affinity 9 logical CPU이나 cgroup quota가 8 CPU,
memory.max가 8 GiB였어. 실제 가용한 한도에 맞춰 최대 2 worker와 수치 thread 1로
작은 검증을 수행했어. 원 729 pilot도 8 CPU/8 GiB 실행이라는 기록을 유지해.

NCP target은 64 CPU/128 GiB야. 이번 대화에서는 remote 서비스 제한 때문에
현재 live 여유량을 직접 관측하지 못했어. 새 C21M의 19:50:11 KST 실행 receipt는
64 affinity CPU, 61 worker, 약 80.20 GiB available/125.78 GiB total을 기록하지만
그것은 그 시점 그 작업의 관측값이야.

새 native 경로는 기존 executor가 launch 때 실제 자원을 다시 표본화하게 해.
production의 --max-workers 64는 상한이고 예약 수량이 아니야. 다른 세션이
있으면 여유 자원에 맞춰 batch를 줄여 진행해. 중첩 thread pool을 만들거나
다른 프로세스를 종료하지 않아. 공유 checkout의 tracked 파일을 바꾸지 않고
검증된 Git 객체의 세 research 경로를 고유 실행 폴더로 export하는 명령을
CODEX_HANDOFF.md에 제공했어.

## 8. 단계별 게시·백업·DAG

| 단계 | 실제 남긴 것 | 확인 기록 |
|---|---|---|
| Stage A: R1–R6, C1–C4 | 최신 조사, 구성적 유도, CAS, 고정 계약. 18파일 양 repo 게시, 75,934 B Dropbox 객체 확인 | delivery/STAGEA_PUBLICATION.json, STAGEA_BACKUP.json |
| Stage B: C5–C8, R7–R9 | 코드·raw 검증·재사용. 73파일 양 repo 게시, 226,801 B Dropbox 객체 확인 | delivery/STAGEB_PUBLICATION.json, STAGEB_BACKUP.json |
| Stage C: C9, C10, R10 | 독립 판정, 보고, 실행·다음 대화 인계, 세 lane 복구 패키지 | delivery/최종 게시·패키지·full GET 영수증 |

DAG.json과 LOOP_RECORD.json의 각 R/C node에는 증거, 게시/백업 checkpoint,
다음 실행 전이를 함께 남겨. Stage A/B는 provider 객체·size를 확인했고,
Stage C 복구본은 실제 전체 GET로 SHA256·size·ZIP CRC·member를 확인하는
별도 영수증을 사용해. 이 문서는 Stage C 과학·인계 본문이며, 최종 외부 작업의
실제 상태는 delivery/FINAL_PUBLICATION.json과 STAGEC_BACKUP_VERIFIED.json이
정확한 기준이야. 패키지 자신의 hash를 자기 ZIP에 넣는 순환 요구는 만들지 않아.

복구본은 원 pilot 112파일, ACCEL01, 새 native 소스·작은 raw 검증을 함께 보존해.
원 47,385행/70,618,848 B history 전체는 이번에 다시 받지 않았어. 원 Stage 5
index와 hash/locator를 유지하며, history가 새 ZIP에 있다고 표현하지 않아.
원 preliminary component/cancellation 및 parameter-slice 그림은 그대로 재사용해.

## 9. 남은 실행과 연구 범위

NCP에서는 기존 NumPy/SciPy 환경에서 C++을 한 번 compile하고, 제공한 작은
5 case 2 step 입력 또는 사용자가 정한 새 pending 입력을 실행하면 돼. 기본 입력은
이미 끝난 729이므로 no-work가 정상 동작이야. 샌드박스 절대 경로를 담은
옛 manifest를 NCP에서 재사용하지 말고 native plan/prepare로 새로 만들어.

새 grid의 expected-case 집계·plot 일반화는 별도 단위로 남아 있어. 원 729용
aggregator에 2 step custom 결과를 넣어 64 step 그림인 것처럼 표시하면 안 돼.
전체 EoR, 일반 non-LRS, full Q^a, 시간·각도·radial 수렴은 계속 남아 있고,
다음 연구 범위가 정해지면 이번 backend를 그 새 pending 실행에 사용할 수 있어.

복사해서 NCP에 전달할 문서는 CODEX_HANDOFF.md, 새 대화 재개문은
NEXT_THREAD_HANDOFF.md야. 완료 데이터를 재사용하고 다음 과학 의무에
집중하도록 작성했어.


## Final delivery status / 최종 전달 상태

ACCEL02의 과학·구현·검토·인계는 `SCOPED_COMPLETE`다. Stage C 본문은
BASS `f94bad85fc913a5be7478251bc85457e6fafdb98`,
REI `369fd5007f7236e2bbb22e1bbe8ff0f1ceee2d5c` content commit에 게시됐다.
기존 Stage B code pin과 고정 과학 계약은 그대로 유지한다.

Dropbox의 5,514,078-byte Stage C ZIP을 **한 번의 전체 GET**으로 내려받아
size·SHA256·Dropbox block hash·ZIP CRC·263개 exact member를 모두 확인했다.
실제 영수증은 `delivery/STAGEC_PUBLICATION.json`, `STAGEC_BACKUP.json`,
`STAGEC_BACKUP_VERIFIED.json`, `FINAL_PUBLICATION.json`에 있다.
Stage A/B는 각각 provider object·size 확인이며, 전체 GET 검증은 Stage C에
한 번 수행한 것으로 구분한다.

불변 ZIP은 자체 provider ACK보다 먼저 만들어졌다. 최종 영수증과 이 상태
보충은 뒤따르는 Git closeout commit에 기록한다. ZIP을 재생성하거나 자기
hash를 재귀적으로 넣지 않는다. 최종 영수증의 Git commit은 이 파일을 포함하는 commit으로 확인한다.
위 content commit은 과학·인계 본문의 게시점이며 실행 코드 pin과 구분한다.

남은 NCP target-local compile·자원 확인·명시된 pending 실행은 별도 후속
작업이다. 이번 단위의 실패나 미완료 과학 검증으로 계산하지 않는다.
