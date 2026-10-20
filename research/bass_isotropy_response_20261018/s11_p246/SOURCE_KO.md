# S11 실행 소스: 새 등방 birth의 양의 P246 보정

## 고정 범위

Non-tilted axisymmetric Bianchi I, signature `(-,+,+,+)`, `a_perp=a exp(-b)`, `a_parallel=a exp(2b)`, `s=dot b`, `Sigma=sqrt(3)|s|/H`를 유지한다. 이 코드는 source-frame의 새 명시적 등방 birth에만 독립적인 새 weights를 반환한다. 기존 photon stock, physical anisotropic stock, 기존 birth weights, spectral owner, default P24 경로에는 쓰지 않는다.

## 방법

고정된 μ와 양의 reflection prior에서 KL 최소화의 simultaneous dual Newton 방정식을 푼다. P24는 M2=M4=0, P246는 M2=M4=M6=0을 요구한다. 모든 imposed moment와 정규화는 실제 저장 binary64 값의 Fraction exact gate `3/10^15`를 만족해야 한다. 출력 weights를 다시 정규화하거나 음수를 절단하는 단계는 없다.

Python은 80-digit Decimal reference, Rust는 std-only compensated binary64 구현이다. Python은 exact moment-curve facet을, Rust는 outward interval로 엄격한 내부임이 증명되는 facet만 사용한다. 음의 facet은 INFEASIBLE_SUPPORT, 모호한 interval 또는 낮은 rank는 Rust에서 FEASIBILITY_UNRESOLVED다. 후자는 성공으로 치환하지 않는다. Rust 성공 status는 PROJECTED_NEEDS_EXACT_CERTIFICATE이며 그 자체로 물리 승인되지 않는다.

`THEORY.md`는 정확한 지지 조건과 KL 존재·유일성, S3에서 재사용한 P8의 cubic 응답 및 새 P10/quartic 항을 전개한다. 고차 moment로 유한한 d 전 구간이나 full native finite-bin 보존을 승인하지 않는다. `CONTRACT_ADDENDUM.json`은 소스 검토에서 추가한 domain controls와 새로운 진단 수치 기준을 메인 실행 전에 고정한다.

## 입력과 실행 귀속

`extract_archived_inputs.py`는 기존 S8 raw gzip의 bytes/SHA256/Git blob을 대조한 뒤 birth index11의 μ/prior만 읽는다. `inputs/INPUT_EXTRACTION.json`은 원 numeric tokens와 binary64 bits를 저장된 prior/P2 rows 및 원 실패 support와 대조한다. 기존 S8 이력은 실행하지 않는다.

`run_validation.py`는 메인 실행 전에 게시된 전체 rooted Git tree에서 만든 외부 manifest를 요구한다. 모든 관련 `.py`, `.rs`, `.json` source/input을 bytes/SHA256/Git blob으로 맞추고, 실행 후 재대조한다. 14개 고정 pair 중 12개 양의 해와 2개 exact 지지 불가능이 사전 예상이다. 49개 유한 d와 6개 작은 부호 있는 d에 대한 660개 angular-response 값은 별도의 continuum 허용오차를 승인하지 않는 진단이다.

실행은 새 output directory만 사용한다. 모든 Rust 실제 호출의 stdin/stdout/stderr/exit 또는 timeout/launch failure가 호출 직후 보존된다. crash는 정상 입력 거부로 집계되지 않는다. 독립 검토에서 확인된 certificate order/domain 누락과 Rust duplicate 허용의 원 관측 및 수정 내역은 `evidence/prepublication_review/`와 runtime recovery receipt에 남는다.

## 기존 완료·실패 재사용

S9 고정8history, S10 targeted11/11·kernel108/108·대표 RAW24/24·science68/68·C9 155/155는 고정 원 증거를 재사용한다. MF closed2.973배·FLRW4.115배는 원 고정 workload 결과이며 closed small 불확실성과 changing n16/cohort2의0.9498173837599284배 회귀를 유지한다.

S8 원 INNER_P2_PRECISION_LIMIT는 보존한다. 같은 저장 input에서 새 P24 알고리즘이 통과하더라도 이 특정 pointwise 수치 문제의 해소에 한정된다. PR175의 shared-Q normalizer/event adapter는 읽어 재사용하되 실제 MD14 donor closure·native Einstein/shear 결합과 measured paired-event 입력을 완료한 것으로 취급하지 않는다. Evolving reactive full finite-bin spectral history, 새 Rust client의 full birth-memory parameter tangent, 더 넓은 finite-d/angular 검증도 별도 의무다. `5.369926725506957e-12`는 기존의 제한된 source-deposition 설명으로 유지한다.

추가 worker≤16·RAM≤16GiB·disk≤4GiB·개별 job≤1800초 범위를 따른다. 실제 환경은8CPU quota·8GiB cgroup이다. NCP·REI production·full EoR·merge·완료된 캠페인 재실행·자동 최적화 주기는 이 단위에 포함하지 않는다.
