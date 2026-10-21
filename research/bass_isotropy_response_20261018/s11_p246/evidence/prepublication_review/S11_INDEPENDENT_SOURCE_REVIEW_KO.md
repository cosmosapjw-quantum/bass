# S11 P246 독립 소스·수식 검토

검토자: `p6_theory` 독립 이론 작업자. 날짜: 2026-10-20.

이 검토는 새 `s11_p246/` 구현과 검증기에 한정된다. 검토자가 solver,
기존 S8/S9/S10 history, build, benchmark, ODE 또는 NCP를 실행한 횟수는
이번 소스 검토에서 모두 0회다. 앞서 runtime interruption으로 사라진 새 S11
독립 유리수 수학 단위만 1회 복구 실행했으며, 이는 별도 `RECOVERY_RECEIPT.json`에
원본 소실·정확 바이트 복원·새 측정 시간을 구분하여 기록했다.

## 1. 판정과 증거의 범위

수식과 정확 인증 경로에는 현재 검토 범위의 물리적 반례를 발견하지 못했다.
초기 독립 인증 함수의 두 실제 false-PASS 반례와 검증기의 실패 판정 누락을
보고했고, 검토 중 갱신된 Python·runner 소스에서 핵심 수정 내용을 확인했다.
이는 **실행 결과 PASS가 아니라 소스 검토 결과**다. 새 고정 입력 검증은
게시한 소스 identity와 연결한 뒤 담당 실행자가 수행해야 한다.

검토 snapshot의 정확한 파일 집합, 바이트 수와 SHA256은
`S11_INDEPENDENT_SOURCE_REVIEW_R1.json`에 있다. 주요 snapshot은 다음과 같다.

| 파일 | 검토 snapshot SHA256 |
|---|---|
| `projector.py` | `1ddb802e2b82744527681182669c6586c3df7be286eee560859aeb8b1763cd1b` |
| `run_validation.py` | `39fcdbee06776c223b40460fc02c53c321fd30e17b9a5eb45f1e0ec42e752462` |
| `rust/projector.rs` | `a14817cd39f903d7ca8e258965dd5e100b64a8181e26301481f2f2c85b2dc510` |
| `rust/cli.rs` | `e1e6c1ad82611b0df92b7531fae5d8a195463d8f86d42749f49d9fe75fe66c2b` |
| `CONTRACT.json` | `2ea6c721a50290af84457b26520bafbdc5ca84e470c9b729b644eaed0e8b4de7` |

Rust 구현자는 이 snapshot 이후 최소 ray 수와 중복 방향 거부를 수정했다고
보고했다. 해당 후속 바이트와 추가 계약 수정은 다음 검토 revision에서 따로
확인해야 한다. 아직 읽지 않은 후속 소스까지 이 표의 판정에 포함하지 않는다.

## 2. 발견한 문제와 수정 확인

| ID | 문제 | 검토 시점의 처리 |
|---|---|---|
| S11-C9-01 | 독립 `exact_certificate`에 `order=0`을 주면 모멘트 검사 목록이 비어 PASS 가능 | `type(order) is int`와 `order in (4,6)`를 먼저 요구하도록 수정 확인 |
| S11-C9-02 | 독립 인증이 비물리적 `abs(mu)>1`을 거부하지 않아 낮은 모멘트만 맞춘 자료를 PASS 가능 | 유한성·범위·정렬·길이를 모멘트 계산 전에 검사하도록 수정 확인 |
| S11-C9-03 | domain control이 모든 Rust 비정상 종료를 올바른 거부로 집계 | case별 JSON 상태·정확한 종료 코드·stderr 검사로 수정 확인 |
| S11-C9-04 | Rust 종료 0과 `weights` key만 있으면 오류 상태의 JSON도 성공으로 간주 | 성공 상태 `PROJECTED_NEEDS_EXACT_CERTIFICATE`와 요청 차수 일치를 추가한 수정 확인 |
| S11-C9-05 | timeout, 실행 파일 오류, JSON 구조 오류, 빠진 input 등이 최종 receipt 이전에 중단 | 호출별 원시 기록, timeout/launch 분류, 최상위 실패 receipt 확인 |
| S11-C9-06 | `--source-commit`은 형식만 확인하므로 임의 commit에 결과를 귀속 가능 | 게시 파일 manifest의 집합·바이트·SHA256·Git blob 일치 검사 추가. 외부 GitHub readback 증거는 별도 보존 필요 |
| S11-C9-07 | P8/P10 계수 차이의 절대 `1e-12` 진단 기준이 계약에 명시되지 않음 | 사전등록에 독립 진단 기준으로 명시하도록 요청. 기존 모멘트 gate와 분리 |
| S11-C9-08 | Rust가 중복 방향을 허용하지만 Python은 거부. 기존 중복 control은 rank 부족으로도 거부되어 원인을 구분 못함 | Rust strict ordering 수정과 full-rank 중복 control을 요청. 후속 구현자 수정 보고 수신 |

첫 두 반례는 `PROJECTOR_PRE_FIX_FINDINGS.json`에 당시 소스 identity와 실제
반환값을 남겼다. 특히 범위 반례는 다음의 비음수 방향과 orbit masses를 썼다.

\[
\mu_{\ge0}=(0,1/2,3/4,5/4),\qquad
\beta=(8797/23625,388/3675,2404/4725,244/18375).
\]

0 이외의 질량을 반씩 나누어 반사쌍에 배치하면 초기 인증 함수는
`max_abs_residual = 2.7755575615628914e-17`로 PASS했다. 원인은 허용 오차가
아니라 `mu`의 물리적 정의역 검사가 빠진 것이었다. 수정은 gate 변경 없이
이 입력을 거부한다.

Python의 새 birth 선언도 임의의 truthy 객체가 아니라 boolean `True`를
요구하도록 바뀌었다. 기존 photon stock의 의미를 이 독립 수학 API가 자동으로
판별하는 것은 아니다. 실제 호출부는 새로 명시한 등방 birth만 전달해야 한다.

## 3. 실패한 실행과 빠진 쌍이 PASS로 남는가

초기 runner에서도 정확히 feasible한 입력의 Python 또는 Rust 성공이 빠지면
`_executed` 검사가 false가 됐다. 이후 angular response loop가 해당 Python
실패 행을 건너뛰어도 최종 실패 목록에 그 false가 남는다. 따라서 현재 소스의
이 skip 자체가 전체 PASS를 만드는 경로는 아니다.

반면 초기 domain 검사는 `rust_exit != 0`만으로 통과했으므로 signal crash도
정상 입력 거부처럼 집계할 수 있었다. 수정한 runner는 다음의 서로 다른
상태를 구분한다.

| 입력 종류 | Python 예상 상태 | Rust 예상 상태 / exit |
|---|---|---|
| 등방 birth 선언 없음 | `NOT_ISOTROPIC_BIRTH` | 같은 상태 / 2 |
| 유한성·범위·양의 prior·반사·정렬·차수 위반 | 구체적인 Python domain 상태 | `INVALID_INPUT` / 3 |
| 두 ray의 P246 rank 부족 | `INFEASIBLE_AFFINE_SUPPORT` | `FEASIBILITY_UNRESOLVED` / 3 |
| 정확히 음수 facet인 등록 support | `INFEASIBLE_SUPPORT` | 같은 상태 / 3 |
| feasible한 성공 | `PROJECTED` | `PROJECTED_NEEDS_EXACT_CERTIFICATE` / 0, 이후 별도 exact gate |

Python exact rank 판정과 보수적인 Rust rank 미해결 상태는 동일 문구일 필요가
없다. 서로 다른 의미를 등록한 예상 상태로 검사하는 것이 맞다. 정상 solver
출력에는 stderr가 필요하지 않으므로 현재 CLI 계약에서 빈 stderr 요구도
일관된다. 이것은 운영 환경 전체에 대한 일반 규칙이 아니라 이 CLI의 계약이다.

수정한 runner는 등록 support 예상값을 독립 목록으로 확인한다. 동적으로
계산한 support 상태를 그대로 정답으로 삼아 양쪽 실패를 정당화하지 않는다.
현재 runner에는 `P24_only_support_P6`와 `b9_n64_P6` 두 음성 사례가 명시되어
있다. 후자의 정확한 저장 input bytes와 facet 증거는 이번 snapshot에 없으므로
검토자가 그 음수 slack 수치를 재계산했다고 주장하지 않는다. 해당 고정 input
증거가 뒷받침하면 계획상 14개 쌍 중 12개 projection, 두 예상 infeasibility,
12×55=660개 response 행이 나온다. 이 수치는 **예상 cardinality이며 실행 실적이 아니다**.

다음 control은 solver를 재실행할 필요 없이 runner 판정 함수의 작은 mock
입출력으로 추가할 수 있다. 본 검토에서는 추천만 남기고 실행하지 않았다.

- 정상적인 weight 목록과 함께 오류 status, 다른 order, 또는 JSON list를
  반환하는 fake CLI가 성공으로 인정되지 않아야 한다.
- `exit=-11`, timeout, 실행 파일 누락은 domain rejection PASS가 되면 안 된다.
- 한 feasible pair에서 Python 또는 Rust 결과를 빼면 최종 결과가 FAIL이어야 한다.
- full-rank를 유지하는 중복 방향
  `[-1,-.75,-.5,-.5,0,.5,.5,.75,1]`는 rank 검사 이전 domain 거부여야 한다.
- 게시 manifest의 한 바이트, 한 파일 집합 또는 Git blob 불일치는 compile
  전에 `SOURCE_BINDING_FAILED`여야 한다.

실제 새 고정 진단 실행에서는 모든 실패를 그대로 보존하면 충분하다. 이 검토를
이유로 완료된 캠페인이나 전체 검증 자동 주기를 재시작할 의무는 생기지 않는다.

## 4. 정확 gate와 양의 KL 구성

독립 인증은 입력 float의 정확한 유리수 값을 사용한다. 제곱도
`Fraction(binary64_mu)**2`로 계산하여 먼저 반올림한 `mu*mu`를 정확한 값처럼
인증하지 않는다. 출력 weight 합으로 재정규화하지 않은 상태에서

\[
\left|\sum_i w_i-1\right|\le 3/10^{15},\qquad
\left|\sum_iw_i P_\ell(\mu_i)\right|\le3/10^{15},
\quad \ell=2,4,6
\]

를 확인하고, 모든 저장 weight의 엄격한 양수성과 정확한 반사 parity를 추가로
요구한다. 이전 P2/P4 gate를 느슨하게 만든 지점은 발견하지 못했다.

정확 support 판정은 이 유한한 출력 허용 오차와 다르다. 연속 방정식의 정확한
target이 moment hull 내부인지 판단하며, Rust outward interval은 확실히 양인
facet만 내부로 승인한다. 0을 포함한 interval을 억지로 양수로 바꾸거나 음수
weight로 통과시키는 경로를 도입하지 않는다.

Python reference는

\[
w_i(\lambda)=\frac{q_i e^{\lambda\cdot(P_2,P_4,P_6)(\mu_i)}}
 {\sum_j q_j e^{\lambda\cdot(P_2,P_4,P_6)(\mu_j)}}
\]

의 동시 dual Newton 문제를 푼다. gradient는 모멘트, Hessian은 centered
covariance다. strict feasible full-rank support에서는 KL 최소점이 유일하고
양수다. 실제 원시 ray prior와 reflection orbit prior 사이의 factor 2는
중앙 0 ray를 제외한 반사쌍의 두 prior 합에서 나온다. 이는 기존 birth 또는
물리적 anisotropic stock의 재가중을 허용하는 근거가 아니다.

정확 moment certificate는 모멘트·양수성·parity 인증이며, 그 자체만으로 KL
최적성의 임의 정확도까지 인증하지 않는다. KL 구성의 타당성은 위 exponential
family, 수렴한 reference gradient, 두 구현의 고정 cross-weight 비교와 별도의
수학 증거로 뒷받침한다. 엄격히 feasible하다는 사실도 임의 binary64 문제의
좋은 conditioning이나 모든 finite support의 성공을 뜻하지 않는다.

## 5. Bianchi I angular reference와 Taylor 방법

사용한 부호와 source frame에서

\[
R(d,\mu)=\sqrt{e^{2d}(1-\mu^2)+e^{-4d}\mu^2},\quad
D=-\tfrac12\partial_dR,\quad \mathcal A=\langle D\rangle/\langle R\rangle.
\]

continuum reference의 \(k=e^{-6d}-1\), \(r=\sqrt{1+k}\)라 놓으면

\[
J=\int_0^1\frac{d\mu}{\sqrt{1+k\mu^2}},\quad
K_2=\frac{r-J}{2k},
\]

\[
F=e^d(r+J)/2,\qquad
G=e^d[-J/2+(3/2+k)K_2].
\]

\(k>0\)에서 \(J=\operatorname{asinh}(\sqrt k)/\sqrt k\),
\(-1<k<0\)에서 \(J=\arcsin(\sqrt{-k})/\sqrt{-k}\)다.
코드의 `atan(s/r)`는 두 번째 branch에서 올바른 \(\arcsin s\)를 준다.
`d=0`은 별도 정확한 \((F,G,\mathcal A)=(1,0,0)\) 처리다. 등록한
\([-0.6,0.6]\)와 작은 세 양·음 strain은 이 정의역 안에 있다.

`response_taylor`는 실제 저장 weight를 쓴 \(R^2\)의 유리수 급수 recurrence,
\(G=-F'/2\), 그리고 \(G/F\) 급수 나눗셈으로 계수를 계산한다. 따라서
허용된 낮은 모멘트 잔차와 실제 normalization이 보존된다. 소량의 비영
P2/P4/P6을 0으로 간주한 공식으로 작은 strain 데이터를 잘못 판정하지 않는다.

정확한 P246 조건 아래의 다음 두 bias 계수는

\[
[d^3](\mathcal A-\mathcal A_{iso})=\frac{288}{143}M_8,
\]

\[
[d^4](\mathcal A-\mathcal A_{iso})
=-\frac{7200}{2717}M_8+\frac{136080}{46189}M_{10}.
\]

runner는 실제 유리수 저차 bias를 먼저 제거한 다음 작은 양의 strain
`1e-3, 5e-4, 2.5e-4`의 계수를 비교한다. 음의 세 점은 진단값을 저장하지만
현재 asymptotic PASS 검사는 양의 세 점에만 적용한다. 최종 설명도 이 범위를
지켜야 한다. 2% 계수 진단은 원래 `3e-15` 모멘트 gate와 다른 새 진단이다.
P8/P10의 단순 공식과 실제 저장 weight 계수 사이의 `1e-12` 비교도 별도의
등록 진단으로 명시해야 한다. 전체 angular continuum 정확도 gate로 사용하면
안 된다.

## 6. 남는 과학적 의무

P246 구성과 위 factorized collisionless 응답으로 실제 MD14 정규화·native
Einstein/shear shared-Q 결합, evolving reactive full finite-bin spectral
history, Rust full birth-memory parameter tangent을 완료했다고 판정할 수 없다.
새 pointwise projector가 저장된 S8 입력에서 성공하더라도 기존 S8
`INNER_P2_PRECISION_LIMIT` 실행과 history receipt는 그대로 남는다.

유한 strain과 높은 angular moment에서는 이득이 단조적일 필요가 없다.
P2/P4/P6 일치는 더 넓은 continuum 또는 모든 native finite-bin 보존을 보장하지
않는다. S10의 `5.369926725506957e-12` source-deposition 잔차는 그 제한된
맥락을 유지해야 한다. 완료된 S9/S10 성능 수치와 알려진 성능 회귀 역시 새
각도 projector의 결과로 교체하지 않는다.

이론 세부 증명과 25개 정확 수학 검사는
`P246_THEORY_AND_ALGORITHM_REVIEW_REVISED.md`, `exact_p246_derivation.py`,
`EXACT_DERIVATION_CHECKS.json`, `EXACT_DERIVATION_CHECKS_RECOVERY_R1.json`에 있다.
원본 복구 바이트와 문구 교정본은 구분해 보존한다. 본 검토는 새 no-go 주장이나
production/full EoR/merge 승인이 아니다.
