# S3 Python 및 실제 측정 결과의 독립 검토

상태: **`PASS_SCOPED` — 실제 측정 검산 통과, 재사용 경로의 두 발견 사항 보완 및 검증 완료**.

이 검토자는 `angular_p24.py`, `shear_response.py`, `run_s3_campaign.py`, `test_s3.py`를 작성하지 않았다. 별도로 작성한 유리수 다항식 유도와 80자리 Decimal 적분을 기준으로 코드를 읽고, `s3_campaign_run_02`의 실제 저장값을 검산했다. 이 검토 중 165개 projection을 다시 실행하지 않았다. 이전 실행의 완료된 측정을 재사용한다는 원칙을 유지했다. 검토 파일의 정확한 SHA256과 수치 결과는 같은 이름의 JSON에 기록한다.

## 1. 승인되는 범위

검토 결과는 고정된 source-frame ray 집합에서 수행한 양의 P2/P4 KL projection과, 그 출생 weights를 고정한 collisionless 응답의 유한 수치 캠페인을 지지한다. 다음 범위를 승인하지 않는다.

- 연속체 각도 오차의 전 영역 상한 또는 수렴 증명.
- native finite-bin photon/energy 보존 및 보정된 source의 production 채택.
- Einstein 방정식과 결합한 전단 진화 또는 full EoR.

실제 실행 receipt도 `continuum_accuracy_admission=false`, `native_finite_bin_admission=false`, `coupled_shear_evolution=NOT_RUN`을 기록한다. 이번 검토는 native adapter 검토와 별개다.

## 2. 알고리즘 및 고정 source frame

`angular_p24.py`의 목적함수와 두 제약은 양의 prior를 기준으로 한 표준 유한 KL projection이다. 먼저 고정된 λ4에서 P2 평균을 0으로 만드는 λ2를 scalar bisection으로 구하고, 그 해 위에서 P4 평균을 0으로 만든다. 반환 직전에 양의 weights와 양쪽 직접 다항식 moment를 확인한다. 허용오차 범위는 `1e-16 <= atol <= 3e-15`이며, inner target은 `atol/8`이다. 최종 P2/P4 gate는 계속 `3e-15`다. bracket, precision, support-loss 실패를 성공으로 변환하지 않는다.

양의 해의 존재 조건과 수치 해법의 종료 조건은 분리되어 있다. 64 epsilon guard는 hull 경계 판정에 쓰이며 moment 허용오차를 늘리는 용도가 아니다. 수학적으로 가능한 2-z rank-one support를 일괄 불가능으로 분류하지 않는다. 그 경우의 근접한 f64 일치는 `FEASIBILITY_UNRESOLVED_RANK1`로 남긴다.

원래 `angular_balance.py`는 변경되지 않았다. 그 기존 API가 더 큰 명시적 `atol`도 받는다는 사실과 별개로, 이 캠페인의 P2 호출은 기본 `3e-15`를 사용하고 저장값에도 같은 gate를 적용한다. 이번 P24 API는 `3e-15`보다 느슨한 허용오차를 받지 않는다.

캠페인은 각 `(b(u), n_mu)`에 대해 `lrs_rule`로 source-frame 방향과 prior를 한 번 구성한다. constraint mode가 바뀔 때 방향과 prior는 동일하다. P2/P24 projection은 d sweep 밖에서 한 번 수행된다. `shear_response.py`는 그 후 d마다 고정된 방향과 weights로 R,D를 평가하며 입력을 수정하지 않는다. 검토한 146개 성공 row에서 같은 support를 쓰는 prior/P2/P24 간 μ와 prior가 동일함을 실제 저장값으로 확인했다. 현재 photon stock, 스펙트럼 또는 물리적으로 anisotropic인 source를 이 Python 캠페인이 초기화하는 경로는 없다. Native의 source 종류 선언과 spectral owner 연결은 별도 검토 사항이다.

## 3. 응답식과 독립 검산

R과 D는 사용자가 지정한 source-frame 정의 및 부호와 일치한다. `F=<R>`, `G=<D>`, 관측하는 정규화된 압력차는 `A=G/F`다. 단위 없는 d의 미분이며 `R'=-2D`이다. 출생시 `F(0)=1`, `G(0)=M2`이므로

\[
\mathcal A'(0)=G'(0)+2M_2^2,
\qquad
\mathcal A''(0)=G''(0)+6M_2G'(0)+8M_2^3.
\]

코드의 diagnostic은 이 일반식을 포함한다. M2가 0인 경우만을 가정해서 prior의 normalized response를 G와 혼동하지 않는다. 독립 유도한

\[
D'(0)=-\frac85 P_0-\frac{10}{7}P_2+\frac{36}{35}P_4
\]

및 D'' 전개와 일치한다. 따라서 P2만 없애면 잔류 P4가 선형 응답을 바꾸고, P2/P4를 모두 없애도 잔류 P6가 이차 응답을 바꾼다는 결론을 코드와 실제 데이터가 구별한다.

저장된 f64 μ와 weights를 `Fraction`으로 정확히 읽어 moment를 다시 합산했다. 이를 통해 recurrence 반올림과 projection 내부의 자체 보고에 의존하지 않는 제약 검사를 수행했다. 모든 1,606개 응답점도 검토 대상 함수를 import하지 않고

\[
R=e^d\sqrt{1+(e^{-6d}-1)\mu^2},\qquad
\mu_x=\mu e^{-2d}/R,\qquad D=R P_2(\mu_x)
\]

로 검산했다. 원래 구현과의 최대 F/G/A 차이는 `3.3306690738754696e-16`이다. Fraction moment에서 재구성한 A'와 A''의 저장값 차이는 각각 `4.440892098500626e-16`, `2.6645352591003757e-15` 이하였다.

적분 reference는 `lrs_rule`이나 projection 결과를 이용하지 않고 μ in [0,1]의 연속체를 별도로 적분한다. GL256 reference는 source mesh와 별개의 rule이고, Decimal80 reference는 독립적으로 유도한 적분식이다. 두 reference 간 실제 일치는 유용한 교차검산이며 연속체 오차의 보편적 상한은 아니다. Decimal 유도를 작성한 검토자가 이 항목도 확인하므로, 독립성은 root Python source/solver와 다른 유도 및 계산 경로라는 의미다.

## 4. 실제 측정의 readback

실제 JSON의 row는 최초 실행 `s3_campaign_run_01`의 저장된 row와 값 수준에서 완전히 동일하다. grid의 유일한 `(b,n,mode)` key 집합과 각 성공 row의 11개 d 값이 실행 receipt와 정확히 일치한다.

| 항목 | 독립 readback 결과 |
|---|---:|
| 시도한 rule | 165 |
| 측정 성공 / 지지 불가능 | 146 / 19 |
| prior 성공 | 55 |
| P2 성공 / 지지 불가능 | 48 / 7 |
| P24 성공 / mean 밖 / upper hull 밖 | 43 / 7 / 5 |
| 실제 응답점 | 1,606 |
| P2 mode의 정확한 binary-input M2 최대 | `2.9391197195792192e-15` |
| P24 mode의 정확한 binary-input M2 최대 | `1.9113380953429277e-15` |
| P24 mode의 정확한 binary-input M4 최대 | `2.8557850242805446e-15` |
| 최대 normalization defect | `1.1102230246251565e-16` |
| 최소 weight | `6.14251849056058e-06` |
| 최대 weight reflection defect | `0` |
| GL256 대 adaptive quad의 최대 A 차이 | `5.551115123125783e-16` |
| Decimal80 대 adaptive quad의 최대 A 차이 | `5.551115123125783e-17` |

55개 support 모두에 대해 저장된 binary μ를 유리수로 취급해 `z=mu^2`, 목표 `(E[z],E[z^2])=(1/3,1/5)`의 hull 조건을 독립 판정했다. 정확한 결과는 43 strict interior, 7 mean 밖, 5 upper hull 밖이다. P24 결과와 하나도 어긋나지 않는다. 성공 support의 mean/lower/upper 경계까지 최소 margin은 `0.013494465708051672` (`b=1,n=64`)여서 64 epsilon의 모호 경계와도 충분히 떨어져 있다. P2에서 거절한 7개도 정확한 mean bracket 실패다. 이 캠페인에서 저장된 19개 실패를 numerical nonconvergence로 오인하지 않는다.

`b(u)=0.3`, 8 rays라는 같은 support에서 P2-only는 `M4=-0.05946222340038122`, `A'(0)=-1.6611611440689655`다. P24는 A'를 약 -1.6으로 맞추지만 `M6=-0.1984198108084396`이 남아 `A''(0)=1.729108063186708`이며 연속체 `16/7`과 다르다. d=0.01에서 저장된 A 오차는 P2 `-6.178581420255985e-4`, P24 `-2.750669336356454e-5`다. 이는 P4 제약이 해결한 조건과 남은 조건을 구체적으로 드러낸다.

기존 실제 `TEST_S3.log`는 신규 14 tests가 실행되어 `OK`, exit 0임을 기록한다. 검토자가 그 전체 test suite를 다시 돌리지는 않았다. 테스트에는 별도 `scipy.optimize.root` 해와 weights 비교, manufactured KL 조건, sharp P2/P24 feasibility 차이, 경계/rank-one 미해결 분류, parity/positivity/입력 불변성, 정규화 미분, `R'=-2D`가 포함된다. 별도 root solver의 reference 비교 tolerance는 production projection의 `3e-15` gate를 대체하지 않는다.

## 5. 실패 이력 및 재사용 경로의 발견 사항

최초 실행은 측정 저장 후 Matplotlib의 괄호 없는 `\\mathcal A`를 그리는 단계에서 exit 1이 되었다. 오류 기록과 producer source가 보존되어 있다. 이후 괄호를 수정한 report producer가 기존 측정을 재사용했다. 예전 producer에 있던 추가 recurrence assertion `3.5e-15`는 최종 report producer에서 `3e-15`로 좁혀졌다. 실제 projection의 직접 제약 gate는 이전에도 `3e-15`였다. 저장된 recurrence M2의 최대 `2.9585708882784445e-15` 및 위 독립 exact-binary 검사가 현재의 엄격한 조건을 통과하므로 허용오차 완화로 과학적 결과를 구제한 사례가 아니다.

**F1 — 재사용 입력 검증의 누락, `CLOSED`.** 검토한 report producer는 dependency hash와 row 수는 검사했으나 동일한 수의 grid 치환, 중복 key, d vector 변경을 충분히 거절하지 않았다. P2-only의 재사용 검사도 저장된 diagnostic M2에 의존했다. 현재 run02 파일은 위 독립 readback으로 문제가 없음을 확인했다. 최종 source는 exact unique grid/d, 원래 source-frame 방향/prior의 정확한 재구성, 배열 domain/parity/normalization, 직접 P2/P4, 실제 support certificate, deterministic diagnostic 및 응답을 검사한다. 거절 row도 실제 support 실패로 다시 확인한다. 첫 보완의 12개 실제 targeted tests와 source snapshot이 보존되어 있다.

**F2 — 유한 값인 continuum cache의 일관성, `CLOSED`.** 첫 보완은 cached continuum 값을 finite인지 확인했지만 해당 적분과 비교하지 않았다. 검토자는 d=-0.2의 cached A에 0.125를 더하고 그 d의 저장된 A_error만 일관되게 바꾼 입력이 165 rows로 승인되는 사례를 실제로 재현했다. 이는 이후 report가 새 reference와 과거 error를 함께 쓸 수 있는 복구 경로의 결함이었다. 최종 source는 11개 cached F/G/A를 독립적으로 다시 평가한 `continuum(d)`와 정확히 비교한다. 검토자는 같은 변조 입력을 다시 넣어 `MEASUREMENT_REFERENCE_CHANGED`로 거절됨을 확인했다. 두 호출 모두 optimizer를 호출하면 실패하는 mock을 두었으며 optimizer 실행은 0회다.

최종 `test_campaign_reuse.py`는 원래의 12개에 coordinated reference/error 변경을 거절하는 검사를 추가했다. 실제 `reuse_guard_validation_r2/TEST_RECOVERY_GUARD.log`는 **13 tests, OK, exit 0**을 기록한다. 정상 저장값 검사는 두 optimizer를 금지한 채 165 rows 및 146 measured rows를 승인한다. 이 검토자는 해당 source diff, test 내용, receipt와 snapshot SHA256을 직접 읽었으며 전체 test suite나 과학적 campaign을 다시 실행하지 않았다. `r2` receipt가 첫 guard receipt를 대체하지만 과거 기록은 삭제하지 않는다.

보고서 그림을 실제로 열어 확인했다. 같은 8 rays에서 제약을 바꾸는 패널과 고정 d에서 각도 ray 수를 늘리는 패널이 분리되어 있으며 source birth와 고정 weights를 명시한다. `1e-16` 표시 floor와 한 plot-reference 지점의 quad roundoff warning은 receipt에 남아 있다. 해당 warning은 과학적 grid의 feasibility/moment gate를 완화하지 않는다.

## 6. identity와 남은 의무

run02의 measurement producer, report producer, 최종 재사용 검증 보완 source의 identity를 구분해서 확인했다. 뒤의 검증 patch를 run02를 생성한 source라고 소급 표시하지 않는다.

| source 역할 | SHA256 |
|---|---|
| 최초 측정 producer | `76ce92ac1482430f9d85268688c388248f2adccf4e86fcbde72bcd38ca208843` |
| 실제 run02 report producer | `8e171badca059edee5f9e7d8dee0d0e8dcfbfe885d498ecd7895095bd95b7ff1` |
| 최종 재사용 guard가 있는 `run_s3_campaign.py` | `28160640be0db83e8f539898cae765ff689f1a09e0974d8a7a12739f7c042caa` |
| 최종 `test_campaign_reuse.py` | `7ed485b5915fa481cd1923b47ab986386914ca94b00a900fabe6ad233c819e5c` |

최종 guard 보완 뒤에도 원래 run02 `ANGULAR_CAMPAIGN.json`과 `RETURN_S3_CAMPAIGN.json`의 SHA256은 바뀌지 않았다. 저장소의 `evidence_s3/campaign` 복사본도 원래 실행 파일과 동일한 SHA256임을 직접 확인했다. 이 로컬 readback은 별도로 수행해야 하는 클라우드 독립 readback을 대체하지 않는다.

남은 물리·구현 의무는 더 높은 angular moments와 유한 d의 수렴 연구, 결합 전단 진화, 그리고 실제 native source owner의 finite-bin 보존·주입 검증이다. P2/P4가 맞는다는 사실만으로 그 의무를 닫을 수 없다. 이번 검토가 만든 파일 외에는 수정하거나 게시하지 않았다.
