# S10 C2 — BASS의 식·데이터·코드·비용 대응

## 판정과 범위

**C2 정적 대응을 완료했다.** 현재 코드에서 우선 계측할 표면은 (1) 같은 frozen bank/state의 전체 moment 재평가, 특히 MF JVP, (2) moment 임시 `Vec`, (3) P24 nested-distribution 작업 공간이다. 원 S9의 실제 counter가 이 표면의 호출 빈도를 제공한다. 실행 시간의 지배 항이나 가속 배수는 아직 판정하지 않았다.

이번 작업은 원 S9 과학 source `4b30957cb008aad8019bb1a673937fc67bd017e8`, 실제 결과 commit `a40311796f9aac5ea5e0e58c630bee2a78443353`에 묶었다. 고정 VigilODE는 `a21d573980f66fe02891bd216153443b5352f921`, spectral owner는 `0e25846433170d0f420c4cda44a0bedbf02cd177`다. 현재 GitHub HEAD를 이 값으로 덮어 해석하지 않는다.

`SOURCE_FINGERPRINTS.json`은 사전등록 source/input, P24 owner, 읽은 upstream 구현의 총 23개 파일과 8개 원 실행의 INPUT/RAW/PROCESS 지문을 보존한다. 기존 사전등록과 실제 실행 영수증의 SHA256, 관련 upstream Git blob이 일치했다. 원 RAW는 각 PROCESS의 SHA256/byte 수와 같고, RAW 안의 input도 INPUT과 같았다. 검사한 과학 source는 이번 읽기 전후 같았다. 새 compile, ODE/history, microbenchmark, 외부 쓰기와 source 수정은 모두 0이다.

`skill_context_used`: `physmath-research-loop` **1.3.0**의 `SKILL.md`, `STAGE_SELECTION.md`, `references/POLICY_INTEGRATION.md`, `references/CODING_LOOP.md`의 C2 계약, `references/SUBAGENT_MODE.md`를 적용했다. 절대 경로와 SHA256은 JSON에 있다. 선택 경계를 C2로 유지하고, source/authority 확인 → 식과 호출 경로 → 원 counter의 비용 대응으로 진행했다. C3 이후 구현·수치 검증 완료를 주장하지 않는다.

## 1. 물리량과 실제 함수

기준 파일은 lane의 `THEORY_KO.md`, `S9_THEORY_KO.md`, `s9_vigilode/src/lib.rs`, `s9_vigilode/PREREGISTRATION.json`이다. 여기의 행 번호는 점검 시 고정 source를 찾기 위한 위치다.

| 의미 | 식·입력·경계 | 구현 위치 |
|---|---|---|
| 기하와 시간 | non-tilted axisymmetric Bianchi I, `(-,+,+,+)`, \(a_\perp=a e^{-b},a_\parallel=a e^{2b}\); \(x=\ln(a/a_{ref})\) | `THEORY_KO.md` §1; `lib.rs` 1–5, 25–28 |
| 상태 | \(h=H/H_*, y=s/H_*\), state=`[h,b,y]`; \(\Sigma=\sqrt3|y|/h\) | `S9_THEORY_KO.md` §1; `lib.rs` 113–136, 307–312 |
| 단위와 정규화 | 입력은 이미 무차원 energy/donor/Λ다. Rust adapter는 물리적 luminosity·단위 변환이나 spectral integration을 수행하지 않는다. `energy_birth`가 각 cohort의 정규화된 amplitude다. | `Config`, `Cohort`, `INPUT_PROVENANCE.json` |
| 초기조건 | \(h_0=\sqrt{y_0^2+E_{d0}+E_{old,iso}+E_{old,aniso}+\Lambda_*}\); `b0,y0` 입력 | `lib.rs` 273–299, 349–366 |
| 초기 stock | 폐쇄 사례는 old isotropic 128 rays + old physical anisotropic 128 rays. 출생 frame은 모두 `u=0,b_birth=b0`. old energy·digest를 확인한다. | `validate_input`; 원 `INPUT.json` |
| 구간 closure | donor \(E_d=D_0 e^{-3x-\lambda\eta}\); exposure \(\eta\)는 한 구간에서 고정. source는 닫힌 manufactured donor의 이산 energy transfer다. | `FrozenBank::eval` 122; `run_inner` 407–438 |
| 출생 시점 | \(u_j=(j+1/2)\,birth\_end/K\), \(\Delta u=birth\_end/K\); `birth_end=0.8,K=32,x_end=1.2` | `lib.rs` 363–367; 원 input |
| 출생 에너지 | \(w=E_d^-[-\operatorname{expm1}(-\lambda\Delta u)]>0\); 현재 계산한 \(b(u_j)\)로 새 rule을 만든다. | `lib.rs` 407–418 |
| 경계·restart | 매 birth와 output time에 정확히 도달. `h,b,y` 연속, 새 cohort append, donor exposure 증가, fresh immutable bank와 fresh driver/workspace | `lib.rs` 369–438 |
| 관측 | \(C=h^2-y^2-E_d-E-\Lambda_*\), normalized \(|C|\), signed state와 \(\Sigma\) | `observe` 307–312 |
| 비교군 | MF는 3상태 analytic JVP + 명시적 \(F_x\). Small은 autonomous `[h,b,y,x]`, \(x'=1\), Jacobian column4=\(F_x\) | `ode_problem` 152–164; `ClockProblem` 166–183 |

이는 현재의 closed manufactured source-history 문제다. 실제 MD14 에너지 공급/응력 closure, physical native feedback나 전체 reactive finite-bin history를 대신하지 않는다. spectral owner는 provenance와 기존 입력에 고정되어 있지만 **이 S9 hot path가 REI owner를 매 callback에 직접 호출하는 것은 아니다.** 존재하지 않는 spectral loop를 최적화 대상으로 세면 비용 분석이 틀어진다.

### Cohort kernel

\[
d=b-b_u,\quad a=e^{2d}(1-\mu^2),\quad c=e^{-4d}\mu^2,
\quad R=\sqrt{a+c},\quad N=c-a/2,
\]
\[
D=N/R,\qquad D_b=(-4c-a)/R+2N^2/R^3.
\]
\[
(E_u,\Pi_u,Q_u)=L_u e^{-4(x-u)}
\sum_i\alpha_i(R_i,D_i,D_{b,i}),\qquad
(E,\Pi,Q)=\sum_u(E_u,\Pi_u,Q_u).
\]

`Cohort::moments` 75–89가 ray별 세 항을 만들고, `FrozenBank::eval` 113–136이 cohort 합을 만든다. 양쪽 합은 `sum` 30–38의 순서가 정해진 compensated summation이다. 기존 \(\mu,\alpha,u,b_u,L_u\)를 초기화하거나 재가중할 여지는 없다.

\[
F=\left((-h^2-2y^2-E_d/2-E+\Lambda_*)/h,\ y/h,\ -3y+\Pi/h\right).
\]

`eval`은 모든 호출에서 \(F\), 3×3 analytic Jacobian, \(F_x=((3E_d/2+4E)/h,0,-4\Pi/h)\)를 함께 계산한다. RHS만 필요한 호출도 \(Q=\Pi_b\)와 Jacobian을 계산한다. `jvp` 138–142는 `eval` 전체를 다시 호출한 뒤 3×3 matrix-vector product를 한다. 이 product는 9개 scalar product와 3개 짧은 compensated sum이며, 계산량이 커지는 항은 앞선 cohort 재평가다.

### 실제 최적화 목적함수

ODE 자체는 초기값 문제다. 내부의 constrained optimization은 **새 isotropic birth만** 받는 `balance_p24::project`다. 기준 prior \(q_i\)에 대한 KL 최소화의 exponential-family 해를

\[
\alpha_i\propto q_i\exp(\lambda_2P_2(\mu_i)+\lambda_4P_4(\mu_i))
\]

형태로 구하며, 정규화·P2·P4·positive support·reflection과 기하 feasibility를 확인한다. `solve_p2`는 각 \(\lambda_4\)에서 \(\lambda_2\)를 bracket/bisection하고, `project`는 바깥 \(\lambda_4\)를 bracket/bisection한다. receipt의 `projection.evaluations`는 **중첩 분포 평가 수**다. Newton iteration 수나 birth 수가 아니다. `p2,p4,logq`는 이미 birth당 한 번 만들어 내부 평가에서 재사용하므로 이 배열을 매 iteration 다시 만든다고 잘못 세지 않았다.

## 2. 원 S9 counter로 고정한 작업량

다음 RHS/Ft/JVP/Jacobian 수는 저장된 원 RAW의 segment counter를 합친 **관측값**이다. `eval 수`는 해당 callback이 각각 `eval`을 한 번 호출한다는 고정 source와 counter를 대응한 **정적 유도값**이다. 실행 시간을 새로 측정하지 않았다. r0/r1은 각각 `rtol=1e-8,1e-10`, r2/fine은 `1e-12`다.

| 사례 | accepted | RHS | Ft | JVP | Jacobian | solver 안 eval | P24 분포 평가 |
|---|---:|---:|---:|---:|---:|---:|---:|
| closed MF r0 | 218 | 1,744 | 218 | 10,246 | 0 | 12,208 | 81,023 |
| closed MF r1 | 218 | 1,744 | 218 | 10,246 | 0 | 12,208 | 81,023 |
| closed MF r2 | 305 | 2,440 | 305 | 14,335 | 0 | 17,080 | 81,260 |
| closed Small r0 | 218 | 1,744 | 0 | 0 | 218 | 1,962 | 81,151 |
| closed Small r1 | 218 | 1,744 | 0 | 0 | 218 | 1,962 | 81,151 |
| closed Small r2 | 305 | 2,440 | 0 | 0 | 305 | 2,745 | 81,650 |
| FLRW MF fine | 238 | 1,904 | 238 | 7,830 | 0 | 9,972 | 0 |
| FLRW Small fine | 232 | 1,856 | 0 | 0 | 232 | 2,088 | 0 |

모든 원 사례의 reject, `state_reuses`/`jacobian_reuses`는 0이었다. 이는 저장된 해당 캠페인의 사실이며 새 문제의 reuse 상한이 아니다. closed MF에서는 step당 RHS8 + Ft1 + JVP47 = full eval56이다. Small은 RHS8 + Jacobian1 =9이다. MF의 `jvp_calls`에는 diagnostic residual matvec도 포함되어 있으므로 `linear_matvecs`를 다시 더하지 않는다. `problem.rs`의 실제 counter charging과 `linearize_matrix_free`를 확인했다.

관측·event 처리의 추가 `eval`은 closed당 249회, FLRW당153회다. 식은 `최종 observation 수 + 3 × birth 수`다. 출생 직전/직후 평가와 오른쪽 bank로의 observation 교체를 포함하며, 최종 JSON의 observation 153개만 세면 이 비용을 놓친다.

### Moment 임시 배열의 정적 비용

cohort 수를 \(C\), 총 ray 수를 \(N=\sum_u n_u\)라 하면, `eval` 하나는 source 수준에서 \(3C+1\)개의 `exp` 식과 \(N\)개의 `sqrt` 식, **\(C+1\)개 `Vec` 구성**을 가진다. numeric payload 요청량은 \(24(N+C)\) bytes다. 각 cohort의 임시 ray 배열은 함수 반환 때 사라지므로 이 요청량의 합은 peak memory가 아니다. 동시에 살아 있는 이 부분의 payload 형태는 \(24(C+\max n_u)\) bytes이며 allocator capacity·메타데이터·다른 출력 자료는 별도다.

closed 사례의 bank는 \(C=2\to34\), \(N=256\to768\)로 커진다. 마지막 bank의 eval 하나는 source 수준으로 Vec35개, 총 요청 payload19,248bytes, 위 임시 live payload3,888bytes다.

| 원 사례 | admin 포함 eval | ray 방문 = sqrt 식 | Vec 구성 요청 | 누적 payload 요청 bytes |
|---|---:|---:|---:|---:|
| closed MF r0/r1 각각 | 12,457 | 6,961,664 | 273,163 | 173,336,880 |
| closed MF r2 | 17,329 | 10,029,568 | 401,571 | 249,931,440 |
| closed Small r0/r1 각각 | 2,211 | 1,234,432 | 48,409 | 30,735,120 |
| closed Small r2 | 2,994 | 1,727,488 | 69,046 | 43,044,960 |
| FLRW MF fine | 10,125 | 1,296,000 | 20,250 | 31,347,000 |
| FLRW Small fine | 2,241 | 286,848 | 4,482 | 6,938,136 |
| 전체 8개 | 62,025 | 29,732,096 | 1,138,493 | 739,405,536 |

이것은 원 counter에서 소스의 `Vec` 구성을 센 값이다. compiler의 allocation elision, capacity rounding, 실제 malloc 호출, cache miss, cycles를 측정한 값이 아니다. 원 debug timing으로 이 항목의 비율을 추정하지 않았다.

## 3. 중복 계산과 cache의 정확한 경계

`rodas5p_matrix_free_fast.rs` 2600–2636은 base `(t,y)`의 RHS와 Ft를 만든 뒤 그 state를 고정한 JVP operator를 만든다. `problem.rs` 829 이후의 closure는 동일 base state를 보관하고 여러 방향 vector에 대해 JVP를 호출한다. 기존 upstream의 state reuse가 0이어도 **같은 한 step 안의 JVP base는 반복된다.** 현재 BASS callback은 그 반복마다 전체 cohort moments를 다시 만든다.

후속 설계에서 공유할 수 있는 것은 성공한 동일 bank의 동일 bit-pattern `(x,h,b,y)`에서 얻은 evaluation 또는 Jacobian 계수다. 방향 vector는 JVP 결과에 영향을 주지만 base Jacobian에는 영향을 주지 않는다. 같은 state의 RHS/Ft/JVP 사이 공유와 JVP끼리의 공유를 구별해야 한다. RHS의 stage state가 JVP의 base state와 교대로 호출되므로 단순한 한 항목 cache는 stage마다 base entry를 밀어낼 수 있다. base-JVP 영역과 마지막 RHS 영역의 경계를 먼저 설계하고 hit/miss를 기록해야 한다.

같은 step의 full eval56회를 서로 다른 stage state 기준으로 줄일 수 있다는 **작업량 가설**은 성립한다. upstream의 RHS8회는 base1+stage7이고 base derivative를 유지할 수 있다. 따라서 이상적인 정확한 cache의 후보 예산은 step당 full kernel8회다. 이것은 7배 속도 향상 예측이 아니다. P24, solver, locking, output, memory 비용은 그대로 남고 실제 callback key reuse는 계측해야 한다. Small은 같은 base에서 Jacobian과 첫 RHS가 각각 `eval`을 하므로 후보가 9→8로 훨씬 작다.

**birth에서 cache는 반드시 새 세대다.** `h,b,y,x`가 같아도 cohort bank와 donor exposure가 바뀌어 RHS/Ft/Jacobian이 달라진다. `S9_THEORY_KO.md`의 이상적 정규화 식은 \(\Delta F_h=-w/(2h)\), \(\Delta(F_x)_h=5w/(2h)\), \(\Delta J_{yb}=-8w/(5h)\)다. 실제 binary64 rule의 작은 norm/moment residual도 보존해야 한다. `Arc`로 소유한 immutable bank의 수명 또는 명시적 generation을 key에 포함하고, 오류 평가를 cache 성공으로 기록하지 않아야 한다. 전역 `(x,state)`만의 cache, 시간 반올림 key, birth 전후 공유는 불가하다.

`Cohort::moments`의 ray별 세 항은 서로 독립이지만, compensated sum은 순차 reduction이다. 별도의 세 accumulator를 사용해 기존 각 채널의 순서를 유지하는 것은 임시 `Vec` 제거 후보다. SIMD 계산 결과를 정해진 ray 순서로 reduction하는 선택과 pair-fold/parallel reduction으로 합산 순서를 바꾸는 선택은 검증 계약이 다르다. 원 stock 배열은 그대로 두고 derived `mu²`, `1-mu²`를 추가 보관하는 prepared data도 후보가 된다. birth frame·가중치·원 배열 digest를 대신 쓰거나 수정하지 않는다.

## 4. Birth, exact certificate, clone, serialization

| 표면 | 현재 실제 코드와 정적 빈도 | 후속 판단에 필요한 것 |
|---|---|---|
| P24 workspace | `balance_p24.rs::evaluated` 88–116에서 매 분포 `logs`와 `weights` Vec2개. 전체487,258분포 → Vec974,516개, ray exp 식7,796,128개. geometry/q/p2/p4/logq의 고정 overhead는 별도다. | workspace 재사용이 bracket의 lower/upper/current ownership을 보존하는지 확인. 평가 수가 줄어드는 algorithm 변경은 다른 변경으로 분리. |
| coordinate transform | `birth_support`가 pending receipt 준비와 `projected_birth`에서 birth당2회 호출. 각 호출에서 방향·prior를 만든다. closed당64회, 전체384회. | 유효한 prepared `(mu,q)`를 같은 birth에서 한 번 만들고 실패 시 pending 증거를 보존할 수 있는지. exp는 source에서 loop 안에 있으나 compiler hoisting 여부는 미측정. |
| exact certificate | `exact_moment_certificate` 199–216는 **admission당1회**, 전체192회. node별 `BigRational::from_float`2회 → 전체6,144회. exact P2/P4/norm을 `3/10^15`와 비교. | phase 시간과 integer allocation을 먼저 계측. 분포 평가와 같은 487k회라고 세면 안 된다. SIMD f64로 대체하거나 gate를 생략할 수 없다. |
| rational 크기 | closed MF fine의 저장 certificate에서 norm denominator 최대57bits, P2 172bits, P4 288bits. 이것은 출력 rational 크기다. | 중간 BigInt/GCD 비용은 이 출력 크기만으로 결정되지 않는다. dyadic 특수화는 별도 exact equivalence가 필요. |
| bank/receipt clone | segment마다 `Arc::new(bank.clone())`, birth마다 `receipt.final_cohorts=bank.cohorts.clone()`, 시작 시 input/stock clone. closed당 mu+alpha clone payload548,864bytes의 정적 계산. | immutable shared storage 후보. 실패 시 partial cohort evidence가 유지되는지 검토. 원 자료 digest 비교를 없애서 비용을 줄이지 않는다. |
| stock digest | segment 전/후, birth 후, final에 실제 배열 SHA256을 확인. `role,u,b_birth,energy_birth,mu,alpha`를 포함한다. | derived-data cache를 신뢰성 proof로 혼동하지 않는다. hash 제거는 과학 stock 계약 변경이 될 수 있다. |
| event JSON | `pending_birth`를 두 차례 Value로 만들고 overwrite, event에도 certificate·projection·pre/post state를 기록한다. | 복사/구조 비용을 계측하되 실패 종류와 pending candidate 증거 보존. |
| final JSON | `main.rs`는 RunReceipt→`serde_json::Value`→pretty String→file 경로. 원8개 RAW 합계2,033,201bytes. | struct를 writer로 직접 보낼 때 object key 순서/byte hash는 달라질 수 있다. parsed data/schema, binary64 roundtrip, 실패 receipt를 먼저 수용 계약으로 정한다. |

`run.elapsed_seconds`는 `run()` 안의 시작부터 마지막 receipt 상태 갱신까지다. input parsing, 반환 뒤 `to_value`, 최종 pretty string 생성과 file write는 포함하지 않는다. PROCESS wall은 startup/I/O까지 포함한다. 따라서 두 시간을 단순히 비교해서 serialization의 순수 시간을 얻거나 solver kernel 속도를 주장할 수 없다. 현 debug build는 `opt-level=1,debug=0,codegen-units=1`이다. 향후 release 비교는 baseline과 candidate에 같은 profile·input·accuracy를 적용해야 한다.

## 5. 이미 잠겨 있는 SIMD/thread 패키지와 라이선스

다음은 인터넷의 최신 version 탐색이 아니라 **현재 locked vendor와 실제 기존 build feature 영수증**을 읽은 결과다. 전체 Cargo metadata·checksum·license 파일 지문은 `REUSABLE_PACKAGE_INVENTORY.json`에 있다.

| package | 고정 version / local license 선언 | 실제 사용 가능성 및 경계 |
|---|---|---|
| `pulp` | 0.22.3 / MIT | runtime dispatch와 scalar fallback, vector `sqrt` 등. 기존 feature는 `std,x86-v3`; `x86-v4`, `macro`, `relaxed-simd`는 현재 build에 없다. 안정된 현재 의존성을 통해 ray arithmetic 후보를 검토할 수 있다. 벡터 exp의 정확도나 대체 구현을 자동 제공한다고 가정하지 않는다. |
| `rayon`, `rayon-core` | 1.12.0 / 1.13.0, MIT OR Apache-2.0 | 이미 upstream integrators의 직접 의존성. 제한된 local `ThreadPoolBuilder` 또는 독립 case scheduling 후보. 존재만으로 현재 BASS callback이 병렬 실행된다는 뜻은 아니다. |
| `crossbeam-deque/epoch/utils` | 0.8.7 / 0.9.20 / 0.8.22, MIT OR Apache-2.0 | 기존 Rayon 기반 내부 요소. 별도 저수준 scheduler를 새로 만들 근거는 아직 없다. |
| `faer` | 0.24.4 / manifest MIT | 실제 활성 feature는 `std,linalg,sparse,sparse-linalg`; Rayon feature는 비활성이다. package에 Eigen MPL2, LAPACK/SuiteSparse BSD notice도 있으므로 코드를 복사하면 해당 파일 notice를 확인한다. 현재3/4상태 문제를 큰 GEMM으로 바꾸는 효과는 미증명. |
| `gemm`, `gemm-common` | 0.19.0 / MIT | 실제 `std` 중심 build이며 Rayon/x86-v4는 비활성. 기존 faer 기반 자산; nonlinear ray kernel의 직접 대체물이 아니다. |
| `private-gemm-x86`, `nano-gemm` | 0.1.20 / 0.2.2, MIT | 이미 lock에 있는 특화 선형대수. 작은 BASS state에 유리한지는 별도 계측 문제. |
| `bytemuck` | 1.25.2 / Zlib OR Apache-2.0 OR MIT | 필요한 경우 POD/view 표현에 재사용. alignment와 aliasing 계약은 유지. 자체 SIMD 알고리즘은 아니다. |
| `raw-cpuid`, `cpufeatures` | 11.6.0 MIT / 0.2.17 MIT OR Apache-2.0 | 기존 capability dispatch 자산. 현재 머신 feature를 portable target의 보장으로 바꾸지 않는다. |
| `num-rational`, `num-bigint`, `num-traits` | 0.4.2 / 0.4.6 / 0.2.19, MIT OR Apache-2.0 | exact birth gate의 이미 검증된 기반. f64 shortcut보다 우선 보존. |

패키지 존재와 BASS crate의 직접 dependency는 다르다. BASS `Cargo.toml`은 현재 Rayon/Pulp를 직접 선언하지 않는다. 직접 사용을 선택하면 명시적 dependency/features 변화와 offline lock 검증이 후속 C5/C6 표면이다. 이 C2에서는 manifest/lock을 수정하지 않았다. 이것은 local package notice 조사이며 법적 판정은 아니다.

## 6. 현재 CPU와 실행 배치의 제약

2026-10-20 05:39:57 UTC의 읽기 관측은 x86_64, `AMD EPYC 9V74 80-Core Processor`, visible/affinity9 logical CPUs다. 공통 노출 flag에 AVX2/FMA와 AVX512F/DQ/BW/VL 등이 있다. 실제 SIMD 명령 시험, 성능/주파수 시험은 하지 않았다. 기존 `pulp` build는 x86-v3까지만 활성화되어 있으므로 AVX512 flag만 보고 기존 binary가 AVX512를 쓴다고 말할 수 없다.

실제 cgroup `cpu.max=800000 100000`은 8 CPU quota, `memory.max=8589934592`는8GiB다. 이 task의 user cap workers16/RAM16GiB/disk4GiB/job1800s보다 현재 컨테이너 cap이 작다. C2 관측의 `memory.current=7,687,479,296`에는 file7,074,328,576bytes, anon162,189,312bytes, kernel449,777,664bytes 등이 포함된다. 이를 모두 비회수 active RSS라고 판정하지 않는다. `memory.peak`는 공유 컨테이너 lifetime counter이며 이 build/history의 peak가 아니다. host cache 설정은 변경하지 않았다.

한 birth history 안의 각 segment는 직전 state와 새 birth bank에 의존한다. 따라서 segment32개를 독립적으로 병렬 실행할 수 없다. 가능한 병렬 경계는 독립 사례, 한 evaluation 안의 충분히 큰 ray/cohort 묶음, 또는 검증된 upstream의 독립 stage 구조다. 현재 n16·최대N768에서 매 callback에 Rayon pool 생성/동기화를 하면 비용이 증가할 수 있으므로 이득은 미측정이다. 작은 kernel은 SIMD/중복 제거부터 측정할 합리적 후보이며, coarse case parallelism과 inner thread pool을 동시에 최대화하지 않는다. 향후 기본 build jobs2와 명시적 전체 worker 예산을 유지한다.

## 7. 후속 구현의 수용 항목과 미측정 항목

이 문서는 C3/C5 구현 지시를 대신하지 않는다. 다음 표는 변경을 선택할 때 필요한 등가성과 검증 표면이다.

| 후보 | 보존해야 할 의미 | 필요한 identity/측정 |
|---|---|---|
| stream compensated accumulators, 준비된 `mu²` | ray/channel의 기존 연산·합산 순서, immutable stock | BYTE callback 동등성을 우선 시도; compiler 차이/재결합이 있으면 명시적 NUMERICAL 판정 |
| JVP/base-state cache | exact bits·bank generation, explicit Ft, 오류 무효화, birth restart | 같은 callback 결과의 CONTENT/NUMERICAL 동등성 + cache hit/miss; stale-birth negative control |
| P24 workspace | geometry와 bracket 순서, positivity·reflection·잔차·실패 분류 | 기존 owner algorithm 유지 시 weights/certificate 비교; algorithm 변경과 workspace 변경 분리 |
| SIMD ray arithmetic | 기존 source frame/weights; 보상합과 정확도 | scalar fallback, 여러 길이/tail, 고정 gate에서 NUMERICAL/SCIENTIFIC_EQUIVALENCE; fast-math 금지 |
| deterministic cohort/case parallelism | history 의존성, output 순서, immutable bank | thread-count별 결과/failed receipt; launch overhead와 CPU quota 측정 |
| JSON writer·receipt sharing | 모든 과학 수치/원자료/실패 증거 | parsed CONTENT/STRUCTURAL 동등성; 원 RAW는 지문과 함께 계속 보존 |

Hamiltonian1e-11, cohort energy1e-11, event energy1e-13, donor endpoint3e-14, fine reference absolute1e-9, clock absolute1e-12를 바꾸지 않는다. P24 내부 tolerance1e-15와 exact moment/norm gate `3/10^15`, 정확한 reflection, 양의 weights를 유지한다. P2/P4 일치로 continuum이나 전체 native finite-bin 보존을 승인하지 않는다. P6, actual physical source closure, spectral convergence의 미완료 의무도 유지한다.

향후 필요한 계측은 phase별 release wall/CPU 시간, allocation 요청·실제 peak RSS, cache hit/miss, P24/BigRational/ODE/JSON의 분리 시간, thread-count/dispatch별 같은 정확도 결과, warmup과 반복의 분산이다. compile 시간은 kernel/history 시간과 분리한다. 원 debug 캠페인 시간과 공유 컨테이너 단회값으로 portable speedup을 주장하지 않는다.

## 근거와 재현 방법

`CODE_COST_MAP.json`은 사례별 원 counter와 segment별 cohort/node 수, static-cost 계산 결과를 가진다. `COLLECT_C2.py`는 저장된 소스와 JSON만 읽으며 solver나 package command를 실행하지 않는다. 재현 명령은 `python intake/optimization/c2/COLLECT_C2.py`다. 실행하면 현재 CPU 관측 시각은 갱신되지만 원 scientific receipt는 변하지 않는다.

- BASS source: `research/bass_isotropy_response_20261018/s9_vigilode/src/lib.rs`, `src/main.rs`, `Cargo.toml`, `Cargo.lock`, `PREREGISTRATION.json`; lane `balance_p24.rs`.
- 실제 결과: `evidence_s9/run_20261020_r1/*/RAW.json`, 대응 INPUT/PROCESS 및 CURRENT_EXECUTION. 이 보고서의 집계는 이 원본들을 재사용한다.
- upstream counter/cache: pinned `crates/rodas5p-integrators/src/problem.rs`, `rodas5p_matrix_free_fast.rs`, `rodas5p_fast_small.rs`.
- package: 고정 runtime `vendor/*/Cargo.toml`, license/COPYING 파일과 기존 build의 실제 feature receipt.
- 상세 지문: `SOURCE_FINGERPRINTS.json`; CPU 관측: `CPU_CAPABILITIES.json`; package 목록: `REUSABLE_PACKAGE_INVENTORY.json`.

이번 단계의 완료 의미는 **source와 물리 계약에 연결된 비용 지도를 확보한 것**이다. 성능 향상 구현, 새 과학 실행, 또는 production/full EoR/merge 승인은 포함하지 않는다.
