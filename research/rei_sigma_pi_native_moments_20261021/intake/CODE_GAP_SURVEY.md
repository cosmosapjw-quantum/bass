# ACC02 read-only code-gap survey

작성일: 2026-10-21 UTC. 담당 범위는 현재 ACCEL01 코드·계약과 첨부 프로토콜의 읽기 및 의존성 연결이다. 이 문서의 후보는 coordinator의 최신 repo/backup/conversation delta 합류 뒤 연구 단위를 선택하는 입력이다. Production 수정, 새로운 이론 유도, 과학 실행, benchmark 및 기존 suite 재실행은 수행하지 않았다.

## 1. 핵심 결과

**다음 계산 개선을 검토할 위치는 cache miss의 massive three-moment kernel이다.** 현재 split_sweep.seed_for는 두 번의 스칼라 초기조건 변환이며 quadrature나 ODE를 호출하지 않는다. 이 함수를 큰 비용 원인으로 선정할 코드 근거는 없다. 준비 연산은 sweep.PreparedContext의 source/rate/grid 구성과 prototype 초기화에 있다. 시간 비중은 측정하지 않았다. [S1–S3]

ACCEL01은 동일 모델의 동일 binary64 (x,b) 요청을 원 함수 결과로 대체하는 exact cache, 완료729 재사용, pending-only worker 및 atomic case store를 완성했다. 새로운 geometry에 대한 kernel 산술은 그대로 실행한다. 원 데이터는 기본 plan에서 pending 0이다. [S4–S6]

Coordinator가 제시한 **기존 96×32 quadrature의 \(\mu\leftrightarrow-\mu\) pair folding + fused C++17 three-moment kernel**에는 구체적인 source seam이 있다. 현재 source는 \(\mu^2\), \(P_2\), even angular weight만 사용한다. 기존 32개 노드를 16쌍으로 접는 설계이며 새 16점 Gauss rule로 바꾸는 설계와 구별해야 한다. Compensated reduction은 원 np.sum의 rounding 계약을 바꾸므로 opt-in backend와 별도 수치 수용 기준이 필요하다. 여기서는 parity 조건과 연결 위치만 식별하며 신규 동등성 증명·컴파일·수치 판정을 수행하지 않았다. [S7, S8, S12]

새 parameter grid에서 그림을 만들 때는 **expected-case 집계 계약**이 별도 필요하다. 현재 worker는 custom case를 실행할 수 있으나 aggregate/plot은 원729 좌표·64-step 설명·고정 slice에 결합돼 있다. Kernel 개선과 독립적으로 작업할 수 있는 출력 경로의 공백이다. [S1, S6, S9]

## 2. 현재 근거와 재사용 범위

중앙 delivery/FINAL_PUBLICATION.json의 ACCEL01 상태는 SCOPED_COMPLETE_WITH_DRIVE_DELIVERY_LIMITATION이다. 세 production 파일의 실제 SHA256을 그 receipt와 대조했으며 모두 일치했다. 기존 25 targeted tests, C9 한 pass의 29 guard probes, custom case 하나의 2-step worker 연결 근거를 재사용한다. 그 검사를 다시 실행하지 않았다. 원729 full-trajectory rerun과 상세 benchmark는 이번 intake에서도 0이다. [S10]

고정 계약은 non-tilted LRS Bianchi I, \(a=0.1999\to0.2\), \(L=8\), source grid 8X8, massive fraction 0.1, mass/T=30이다. Matter는 massive Vlasov, radiation은 gamma+massless nu+UV이며 \(\alpha_m,\alpha_r\)는 독립이다. \(\alpha_r\)는 gamma와 nu에 공통으로 사용된다. 기본 norm은 half contraction이고 부호 있는 응력 합 이후 norm을 취한다. Full EoR/non-LRS/full donor-escape \(Q^a\)/수렴은 기존 open 범위를 유지한다. [S1, S2]

원 StageC ZIP은 endpoints/plots/source와 history locator를 보존한다. 원 47,385행 history를 현재 로컬 raw data로 간주하지 않는다. Endpoint-only 소비와 raw-history 복원은 서로 다른 입력 계약이다. 이번에 해당 history를 다운로드하지 않았다. [S10]

## 3. 실제 식–코드–실행 경로

| 경로 | 실제 함수와 위치 | 관찰된 역할 |
|---|---|---|
| 요청 좌표 검증 | work_plan.normalize_case/validate_cases, 65–100행 | signed 좌표·입력 범위·중복 label/coordinate 검사 |
| 완료 데이터 소비 | load_completed_registry/build_plan, 110–184행 | pinned729의64step 재사용; pending이 생길 때만 context 생성 |
| 초기 불변량→seed | split_sweep.seed_for, 89–107행 → sigma_pi_map.initial_seed, 29–63행 | \(H=H_{\rm base}/\sqrt{1-\Sigma_h^2/3}\), 각 signed \(D_A\), \(\alpha_A\)의 scalar 계산 |
| 고정 입력 준비 | sweep.PreparedContext, 99–124행 → coupled.EinsteinBoltzmann, 166–201행 | CSV/rate PCHIP/96×32 grid/operators 생성, prototype initial로 calibration |
| 개별 모델 | split_sweep.PreparedContext.model, 46–62행 → cached_context.PreparedContext.model, 113–120행 | 새 params/weights/state/counters와 immutable cache binding |
| Massive 응력 | coupled._physical, 254–306행 → massive_source_3moments, 231–252행 | 실제 (x,b)에서 \(J_{00},J_{01},J_{20}\); \(E_m=\rho_{\rm ref}J_{00}\), \(D_m=\rho_{\rm ref}J_{20}\) |
| Geometry/hierarchy | rhs/_geom, 308–336행 | 현재 \(H\), signed stress, massless hierarchy를 사용하는 DOP853 |
| Gas/UV feedback | _chem/step, 356–430행 | source injection, chemistry, compression, 두 번 predictor-corrector, 원 number/energy gates |
| 저장·재개 | batch_worker.case_from_store/run_group, 192–279행 | backend source별 case lock, strict owner 검증, 부분 성공 checkpoint |
| Normalized 출력 | split_sweep.normalize_row, 110–145행 | \(D_r=D_\gamma+D_\nu+D_{\rm UV}\), \(D_t=D_m+D_r\), signed/half/Frobenius/work |
| 집계·그림 | split_sweep.aggregate, 280–342행; split_plot | 원729 expected grid·fixed interval/labels와 실제 endpoint/history |

_physical 전체에는 massive-only key를 사용할 수 없다. 같은 x,b라도 \(s,J,\) gas/UV proxy에 따라 \(H\), radiation stress와 Thomson rate가 달라진다. 이 경계는 기존 THEORY의 dependency table에 보존돼 있다. [S7, S11]

## 4. Seed mapping과 이미 확보된 affine 구조

Seed_for는 matter/radiation에 initial_seed를 각각 한 번 호출한다. 동일 \(\Sigma_h\)의 H,s를 두 번 계산하지만 각 호출은 scalar validation·sqrt·곱셈/나눗셈·작은 dict 생성이다. Context는 grid/PCHIP를 만들고 initial 및 massive moments를 평가한다. 새 pending plan, prepare 검증, worker process에 context 준비가 존재하며 worker group 내에서는 공유된다. 이 source 조사로 비용 비율을 알 수는 없다. **다음 후보에서 seed_for를 최적화 대상으로 택하지 않는다.** [S1–S3, S5, S6]

고정 geometry에서의
\[
J(x,b;\alpha_m)=J_0(x,b)+\alpha_m J_2(x,b)
\]
는 ACCEL01 THEORY.md 95–106행과 REPORT_KO.md 130–142행에 이미 도출·기록된 결과다. 새 유도로 다시 주장하지 않는다. 실제 massive_weight=(rw/norm)·[w_mu(1+alpha_m P2)]가 이 seed 의존성을 보여준다. [S1, S7, S8, S11]

다음 사용처는 같은 geometry에서 여러 alpha_m를 평가하거나 kernel 민감도를 계산하는 것이다. 완전 결합 궤적마다 b(x), H, gamma/nu, gas/UV가 달라지므로 한 궤적을 다른 seed의 전체 solution으로 바꾸는 근거는 아니다. 두 basis sum의 결합도 원 summation과 rounding이 달라진다. Exact cache와 별도 numeric contract가 필요하다. [S7, S11]

## 5. Massive kernel과 reflection-folding 조건

### 원 kernel에서 남은 산술

Massive_q2와 massive_weight는 모델 생성 시 계산된다. Source/rate/angular operators도 prepared group에서 공유한다. Cache miss에서는 rr=exp(-x), perp=exp(2b), parallel=exp(-4b), R2, 96×32 p2/energy/v2/weighted와 세 np.sum을 수행한다. Weighted*v2는 j1과 j2 표현에 각각 나타난다. [S7]

동일 weighted*v2 중간값을 재사용하는 것은 작은 arithmetic-reuse 후보다. Subexpression과 원 reduction 순서를 유지한다면 원 tuple byte 비교를 수용 기준으로 삼을 수 있다. Energy*v2를 p2/energy로 재배열하는 것은 다른 산술 순서이므로 같은 분류에 넣지 않는다. 이 intake에서 어느 변경도 구현하지 않았다. [S7, S11]

### Pair parity의 출처와 필요한 입력 검사

Vendor_pr140_massive_radial.MassiveRadialGrid 41–56행은 각도에 leggauss(nmu), wmu*=.5, mu2=mu**2, p2=(3*mu2-1)/2를 사용한다. C15는 MassiveRadialGrid(mass,96,32)를 생성한다. 설치된 NumPy2.3.5의 실제 leggauss source에도 w=(w+w[::-1])/2와 x=(x-x[::-1])/2의 대칭화가 있다. [S7, S8, S12]

현재 세 integrand는 \(\mu^2\), transformed \(\mu_{\rm phys}^2\), \(P_2\), even seed weights만 사용한다. Signed alpha_m도 P2 seed의 reflection parity를 바꾸지 않는다. Source inspection과 별도로 실제 전달 배열에서 다음을 확인해야 한다.

- nmu=32가 짝수이고 node/weight pairing이 명확하다.
- \(\mu_i=-\mu_{31-i}\), \(\mu_i^2=\mu_{31-i}^2\), \(w_i=w_{31-i}\), \(P_{2,i}=P_{2,31-i}\)가 요구한 binary64 표현에서 성립한다.
- 실제 96×32 massive_weight의 paired 열이 같고 finite/nonnegative이다.
- Mass/q²/weights/mu²의 값·dtype·shape·strides·layout이 native/cache lifetime 동안 고정된다.
- 원32-node measure를 pair로 합친다. 새16-node quadrature, angular cutoff 감소, odd/tilted distribution은 다른 계약이다.

위 source 조건에 따라 중복된 각도 geometry를 pair마다 한 번 평가하는 seam을 확인했다. 동등성 명제와 compensated reduction의 수치 기준은 다음 연구 단위가 확정한다. 96×32와96×16은 원 quadrature 노드 수와 distinct pair 계산 수의 구별이며 wall-time 배수를 뜻하지 않는다.

### 기존 batch 코드와 재사용 한계

MassiveRadialGrid.batch 83–108행은 chunked NumPy로 여러 (x,b)의 j0/j2/j4 tower를 계산한다. 현재 owner는 scalar three-moment method를 호출한다. Batch를 즉시 교체품으로 사용하기 전에 다음 차이를 해결해야 한다. [S8]

- Math.exp와 np.exp, (rr*rr)*q²와 (r*q)^2, reduction axis가 다르다.
- 세 return float 대신 i-index tower를 계산한다.
- 여러 adaptive trajectory가 같은 stage/geometry에 있다는 실행 보장이 없다.
- Batch의 직접 guard는 shape/chunk 중심이며 scalar moments의 x/b/A/imax 검사를 호출하지 않는다.

읽은 current warm-lane tree에는 해당 massive three-moment 경로의 C/C++/Rust 또는 reflection-folded 구현이 없었다. 첨부 Rust README/Cargo의 노출 기능은 ray/optical/chart/background이다. 다른 최신 repo의 kernel 존재 여부는 coordinator의 별도 source inventory와 합류해야 한다. 전 repo의 부재를 주장하지 않는다. [A10, A17]

## 6. Cancellation-safe reduction과 response/derivative 의무

J2는 positive weight에 부호가 바뀌는 P2를 곱해 합한다. 그 바깥에서 D_m와 D_r가 상쇄한다. 양의 energy/pressure moment 검사와 signed stress의 작은 차 검사는 구별해야 한다. 원 normalization은 total을0으로 clip하지 않고 invariant \(3\times10^{-13}\) 아래 orientation을 unresolved로 표시한다. [S1, S7]

Compensated native reduction의 판별량은 각 J, 각 component \(D_A,\widetilde\Pi_A\), signed total 및 work sum의 **absolute** 차이다. Total≈0에서 relative error 하나로 판정하지 않는다. 숫자 tolerance는 root가 source-normalization과 원 gates에 맞춰 고정하며 기존 기준을 편의상 넓히지 않는다. _physical.Pi_total_source와 normalize_row.D_total_Pa는 덧셈 grouping도 다르므로 한쪽을 조용히 바꾸지 않는다. [S1, S7, S11]

| Response 후보 | 실제 연결 위치 | 먼저 정할 의무 |
|---|---|---|
| 고정 geometry kernel 민감도 | massive_source_3moments, 기존 affine identity | x/b/alpha별 derivative 정의·정규화·reference |
| 완전 결합 signed-shear response | rhs/_physical/_chem/step | 초기 parameter derivative와 gas/UV/Thomson, predictor-corrector 의존성 |
| Endpoint norm response | normalize_row | abs at zero와 orientation classifier의 비매끈함; signed variable 우선 |
| Compression 포함 민감도 | coalesce.reduce_age_cohorts | event/heat budget으로 달라지는 admitted/merged branch와 smooth ODE tangent 구별 |

기존 THEORY의 초기 cancellation에서 stress1차/shear2차 성장 해석은 재사용할 근거다. 여기서는 새로운 tangent equation, 근사 surrogate 또는 no-go를 도출하지 않았다. [S7, S11, S13]

## 7. Opt-in native backend 연결 지점

아래는 구현 전 seam map이다. 현재 CLI가 native mode를 지원한다는 뜻은 아니다.

| 현재 지점 | 필요한 연결 | 유지할 계약 |
|---|---|---|
| cached_context._model_class,97–100행 | owner와 cache 사이에 backend별 miss evaluator; cache의 super dispatch가 native body로 연결 | exact-bit(x,b), tuple, capacity/domain/binding guards |
| PreparedContext.model,113–120행 | 실제 even arrays 검증 및 folded read-only representation | fresh params/proxy/state, source-owned nodes/weights |
| work_plan.build_plan,185–188행 | backend를 명시적으로 전달; 현재 main CLI에는 native selector 없음 | science와 resources 분리, completed729 no-work |
| batch_worker.PRODUCTION_FILES/backend_binding,24,61–67행 | loader/C++source/build recipe와 실제 library bytes/compiler/flags를 binding | path/group/workers 독립 source ID, stale library 거부 |
| batch_worker.prepare,116–161행 | backend 선택을 manifest/input에 결합 | pending0 no-work; compiler/native load를 eager 실행하지 않기 |
| batch_worker.run_group,240–279행 | input의 backend context를 명시적으로 생성 | split.run_case, strict validate_result, 원 physics/gates |
| case_from_store,192–237행 | 새 backend namespace와 실제 backend/build receipt | 원 label provenance, atomic store, partial-group resume |

Native reduction에는 기존 exact-cache-v1 source ID를 재사용하지 않는다. **Native 모델 내부에서 동일 입력의 결과 tuple을 캐시하는 것은 계속 exact reuse**다. 원 scientific parameters와 quadrature를 유지한다면 기존 scientific/backend identity 분리를 활용하되 numeric acceptance contract도 backend identity에 묶는다.

Native 선택 상태에서 load/build 실패를 명시적으로 기록한다. Fallback을 설계한다면 실제 Python backend로 기록하고 native 성공으로 표시하지 않는다. Numerical thread는 worker당1, 병렬화는 기존 pending shared executor에서 수행한다. 새 scheduler나 Rust 설치는 이 seam의 필수 의존성이 아니다.

## 8. 후보별 최소 수용검사

아래 검사는 설계만 했으며 실행하지 않았다. 서로 다른 후보를 모두 동시에 구현하라는 목록이 아니다.

| 후보 단위 | 실제 기여 | 최소 의미 있는 수용 근거 |
|---|---|---|
| Reflection-folded fused native kernel | cache miss의 중복 angular arithmetic/temporary 감소 | 실제 parity/domain guard; 원 scalar 대비 component별 absolute error와 원 gates; alpha 경계·0/±b·isotropic/cancellation 대표점; build/source invalidation |
| 동일 산술 common subexpression | weighted*v2 등 중복 산술 재사용 | 원 tuple byte 비교·관련 binding 검사·변경된 owner 연결 |
| 고정-geometry affine basis | 같은 geometry의 여러 seed/민감도 계산 | 원 quadrature 대비 signed component 절대오차; alpha=-1,0,2/상쇄 부근; full trajectory와 구별 |
| Expected-case endpoint aggregate/plot | 실제 custom grid 결과 소비 | expected science IDs; 중복/실패/source/nsteps mismatch 거부; missing=PARTIAL; grouping/label 변경에 values 불변 |
| Analytic derivative | kernel/이후 tangent response의 출발점 | 실제 식의 독립 대입·검산, signed zero 근방, feedback/compression 의존성 |

새 검사는 새 dependency에 집중한다. 기존729 재실행이나 benchmark sweep을 요구하지 않는다. 원144-point kernel test의 입력 설계는 새 kernel 비교에 재사용할 수 있으나 원 PASS를 native PASS로 적을 수는 없다. Warm 연결 검산이 필요하면 root가 고정한 소수의 새 input/short interval을 사용한다. Acceptance 숫자와 정확한 명령은 다음 계약이 확정한다. [S4, S10]

## 9. Custom aggregate/plot의 정확한 공백

Split_sweep.aggregate301행은 signed_grid()의 원 label/좌표를 expected로 삼는다. 334–335행은 8X8/L8/warm interval을 고정한다. Split_plot의 CONTRACT도 원파일이고 footer84행은64step, slices는0/±.004, ticks도 고정이다. Custom nsteps=2 worker smoke를 이 경로에 넣으면 설명/입력 계약이 맞지 않는다. [S1, S9]

별도 expected-case contract는 plan science IDs와 per-case provenance를 입력으로 삼아야 한다. Label/grouping 변화는 원 values를 바꾸지 않는다. 같은 좌표라도 nsteps/physics/source/toolchain이 다르면 구별한다. Archived endpoints와 새 pending results를 한 plot에서 소비할 때는 record별 origin과 과학적 호환성을 명시한다.

Endpoint만 필요한 경우 raw history를 먼저 복원할 필요는 없다. History panel에는 실제 history만 사용한다. Control-subtracted response는 동일 initial signed Sigma의 zero-initial-stress control이 있을 때만 계산하며 없으면 missing으로 표시한다. Full rectangular grid가 아니면 gaps를 mask하거나 actual-point scatter를 사용하고 새로운 interpolation을 암묵적으로 넣지 않는다. [S9]

## 10. 첨부 정책 적용

ATTACHMENT_INTAKE.json은 visible attachment20개를 size/SHA256로 고정한다. 내용 읽기 범위는 protocol5개 전문, archive index7개, selected text member8개, report PDF metadata+앞2page이다. 나머지는 byte inventory이며 설치·실행·원문 방정식 검증을 했다는 뜻이 아니다.

| 첨부 | 현재 채택할 부분/범위 |
|---|---|
| 01 final-code audit | 실제 code path, solver/output/statistics 구별, same-physics 근거. Warm LRS 의존성만 조사 |
| 04 adaptive protocol | contract→source→최소 patch→판별. 1.0의 changed-dependency 검증; fixed quotas와 일괄감사 요구는 범위별 적용 |
| 05 DAG executor | 현재 node·선행 근거·다음 의무. 완료729/ACCEL01 재사용, 문서 조사에 새 solver plot 강제 안 함 |
| 07/08 figure pass | 새/변경 figure의 의미·단위·legibility·caption/actual point 대응 |
| 10/17 Rust core | ray/optical/background API와 differential-test 접근 참고. Historical speedup 숫자를 warm pilot으로 전용하지 않음 |
| 11 Rust patch kit | source/build provenance 참고. PATCH80R Rust gate 규칙은 해당 lane의 기록 |
| 12 old high-l harness | historical source/state 보존. 과거 OD0 gate로 현재 승인된 intake를 다시 막지 않음 |
| 14 JAX/diffrax bundle | 다른 background family/normalization의 참고. README/report constants를 warm 결과로 채택하지 않음 |
| 18/19 literature,20 report | 정확한 원문 위치 후보. 이번 index/metadata 읽기만으로 새 방정식·성능 결론을 채택하지 않음 |

이전 규칙·위치, 교정 근거, 대체 적용 및 영향은 JSON policy_adaptation에 기록했다. 현재 사용자 지시와 physmath1.0을 우선하며 실제 환경 접근권한을 그대로 지킨다. Rust가 첨부됐다는 사실은 설치 필요성이나 backend 변경의 근거가 아니다.

## 11. DAG·게시·백업 상태와 합류점

| 대상 | 실제 상태 |
|---|---|
| Local source/protocol intake(R1/R2/C1/C2) | 이 문서와 byte inventory로 완료 |
| 최신 repo/backup/conversation delta 합류 | root가 새 warm C15 execution/source 변화 없음 확인을 통보함; 상세 delta 근거는 root의 다른 intake 기록 |
| 다음 numeric contract/theory-to-code unit | root가 native reflected three-moment unit을 선택; numeric acceptance는 root가 고정 |
| 신규 유도·production implementation·과학 실행 | 이 intake에서 시작하지 않음 |
| ACCEL01 게시/백업 | 중앙 FINAL_PUBLICATION 상태 재사용, Drive 제한 보존 |
| ACC02 intake 게시/백업 | 이 agent가 제출하지 않음; root가 실제 receipt/DAG에 합류 |

다음 입력은 native folding의 parity/normalization/reduction 계약, 위 seam map, root가 고정할 absolute-error 기준이다. 별도 output 작업을 택하면 expected-case endpoint aggregate를 최소 단위로 사용할 수 있다.

## Source map

함수·숫자·정책의 근거는 실제 읽은 아래 파일이다. 바이트 size/SHA256은 ATTACHMENT_INTAKE.json에 있다.

| ID | 경로 또는 읽은 자료 |
|---|---|
| S1 | research/rei_sigma_pi_pilot_20261021/split_sweep.py, SPLIT_CONTRACT.json |
| S2 | 같은 pilot lane sigma_pi_map.py |
| S3 | 같은 pilot lane sweep.py |
| S4 | research/rei_sigma_pi_acceleration_20261021/cached_context.py, test_cached_context.py |
| S5 | 같은 ACCEL01 lane work_plan.py |
| S6 | 같은 ACCEL01 lane batch_worker.py |
| S7 | pilot vendor/rei_c15/research/rei_c15_sigma_pi_feedback_20261015/coupled.py |
| S8 | 같은 owner directory vendor_pr140_massive_radial.py |
| S9 | pilot split_plot.py |
| S10 | ACCEL01 delivery/FINAL_PUBLICATION.json, DAG.json, CODEX_HANDOFF.md, evidence/VERIFICATION.json |
| S11 | ACCEL01 THEORY.md, REPORT_KO.md 관련 구간 |
| S12 | 현재 runtime numpy/polynomial/legendre.py::leggauss 실제 source |
| S13 | vendor short_interval.py, coalesce.py, rate_table.py 관련 함수 |
| A10/A17 | project_sources/10 Rust README; 17 Rust index/Cargo |


### Coordinator 합류 결과

이 조사 종료 시 root는 최신 intake에서 새 warm C15 execution/source 변화가 없음을 확인하고 native reflected three-moment 단위를 선택했다. 위 조건·seam·수용검사 설계가 그 계약의 입력이다. 실제 구현과 수치 판정은 이 read-only intake 이후 별도 담당자가 수행한다.
