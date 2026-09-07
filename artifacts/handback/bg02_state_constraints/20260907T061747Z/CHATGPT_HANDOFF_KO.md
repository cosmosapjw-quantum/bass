# BG02 state-to-constraint map 실행·수리 반환

STATUS: `PASS_RESEARCH_COMPONENT_ONLY`.
Repo: `cosmosapjw-quantum/bass`.
Branch: `evidence/bg02-state-constraints-20260907T061747Z`.

실제 첫 실행과 수리를 완료했다. 원본 15 Success / 4 Failure / 미평가 0,
`INVALID_RESEARCH_RUN`, actual exit 2를 보존했다. 수리 후 같은 19개 SC 검사는
19 Success / 0 Failure / 미평가 0, actual exit 0이다. 모든 TestID가 실제
TestEvaluated 사건으로 관측되었고 actual_messages 및 RuntimeFailures는 모두
`{}`, stderr는 두 target 모두 0 bytes다.

| 대상 | Success | Failure | 미평가 | actual exit | elapsed s |
|---|---:|---:|---:|---:|---:|
| Original SC | 15 | 4 | 0 | 2 | 6.423564 |
| repair1 SC | 19 | 0 | 0 | 0 | 8.830702 |
| Shape 회귀 RED (원본 mapper) | 3 | 2 | 0 | 1 | 7.164470 |
| Shape 회귀 GREEN (수정 mapper) | 5 | 0 | 0 | 0 | 5.171518 |

## Source/code identity

- 전달 commit: `9f85ba7c4cbeec9223a21a6bcab730b6d2d62aef` / tree `2bbc755f963a238d0bf62e2dfe2303fb57828b0f`.
- 검증한 수정 code commit: `b074e206fd6fe640b6eecb703befcb9bd72467cf` / tree `9fc96c7c7f4d2f3aa9b581d8d28f1c579b96e3ba`.
- Dependency 원 candidate: `e404f914c0817b4c2ab3a0ff4632a8457e026fde` / tree `e2fc64860631e781082cceb3bef5b24fb8a06084`.
- Dependency publication: `2e1b6e2f12cc766c8ffe1160d6371a88730064a8`의 여섯 파일 snapshot.
- 실제 BASS_REPO: `/mnt/sn850x2t/local_ai_foundry/70_experiments/bg02-state-constraints-20260907T061747Z/checkout/artifacts/handback/bg02_repaired_aux_comparison/20260907T052727Z/source`.

전달 branch의 historical root kernel은 실행 source로 쓰지 않았다. 지정한
여섯 파일의 Git blob 모두를 대조했고 원래 위치의 snapshot을 읽기 전용으로
사용했다. 이 작업은 source-subset 실행이다. 네 새 code 파일과 여섯 dependency의
host-side before/after SHA-256은 두 target에서 kernel의 기록과 모두 일치한다.
Dependency는 0개 수정했다. 테스트·runner·plotter도 전달본 그대로다.
Code 상단의 PREPARED_UNEXECUTED 주석은 전달 시점의 작성 상태이며, 이번 실제
실행 상태는 이 반환과 raw 결과로 별도 기록한다.

## 관측 결함과 최소 수리

원본은 SC05, SC06, SC09, SC19가 Failure였다. 직접 진단에서
`Dimensions[Sqrt[14/3]]`가 `{2}`를 반환하고 mapper가 `Failure[StateShape]`를
내는 것을 관측했다. 이는 compound exact scalar의 표현식 인자 수를 배열 모양으로
오인한 구현 오류다. 별도 회귀는 symbolic scalar 출력에서도 같은 종류의
`Dimensions` 오판을 분리했다. 다른 15개 SC 기대식은 원본에서도 통과했다.

`StateConstraints.wl` 한 파일에서 모양 검사만 실제 중첩 `List` 구조로 바꿨다.
입력, 생성된 tensor, constraint 출력에 같은 검사를 적용해 radical/symbolic
스칼라를 허용하면서 list-as-scalar와 ragged tensor는 계속 거부한다. 수학적
connection contraction, owner/projection 호출, exact-real·positive kappa·symmetry·STF·Jacobi
판정, 입력 반환과 expected identity는 바꾸지 않았다. 새 generator나 owner
계수 복사, projection/clamp를 추가하지 않았다.

원본은 TestReport 19행이 실제로 존재하므로 19 미평가나 parser 실패가 아니다.
SC05/06/09는 mapper Failure에서 필요한 값을 얻지 못했고 SC19는 진단값 생성이
실패했다. runner가 diagnostic_rows를 비우면서 최종 code를 2로 두었다.
원본 raw `INVALID_RESEARCH_RUN` 및 네 Failure를 그대로 보존하며 이를 물리
반례나 수정 후 PASS로 덮어쓰지 않는다.

[수리 patch](mapper-repair.patch), [원본 code](original_code/),
[직접 진단](regressions/scalar-shape-red/stdout.log),
[회귀 RED](regressions/list-shape/red.stdout),
[회귀 GREEN](regressions/list-shape/green.stdout)를 함께 반환한다.

| TestID | Original actual | repair1 actual |
|---|---|---|
| SC01_FLAT_BASELINE | Success | Success |
| SC02_BIANCHI_V_MOMENTUM | Success | Success |
| SC03_BIANCHI_II_CURVATURE | Success | Success |
| SC04_H_ZERO_REGULAR | Success | Success |
| SC05_EXCEPTIONAL_CONSTRAINT_STATE | Failure | Success |
| SC06_OFFDIAGONAL_DELETION | Failure | Success |
| SC07_FULL_TRANSVERSE_FLUX | Success | Success |
| SC08_PROPER_FRAME_COVARIANCE | Success | Success |
| SC09_INPUT_UNCHANGED | Failure | Success |
| SC10_MISSING_INPUT | Success | Success |
| SC11_REJECT_DERIVED_OVERRIDE | Success | Success |
| SC12_REJECT_NONSYMMETRIC_N | Success | Success |
| SC13_REJECT_TRACEFUL_SHEAR | Success | Success |
| SC14_REJECT_JACOBI_VIOLATION | Success | Success |
| SC15_REJECT_INEXACT | Success | Success |
| SC16_REJECT_NONREAL | Success | Success |
| SC17_REJECT_SHAPE | Success | Success |
| SC18_OWNER_GENERAL_SLOTS | Success | Success |
| SC19_DIAGNOSTIC_ROWS_CONSISTENCY | Failure | Success |

수정 후 관측은 내부 tensor norm/divergence 생성, exceptional full-shear의
Hres=M=0, 같은 Hgeom에서 shear deletion에 따른 Hres=u^2/ell^2 및 M 유지,
full-transverse 비영점 flux와 proper-frame covariance, Hgeom=0 regularity,
키/override/shape/STF/Jacobi/inexact/nonreal 거부를 이 고정 검사 범위에서 지지한다.
SC18은 owner gradient 슬롯 산술 검사이며 homogeneous geometry의 일반 gradient
검증이라고 쓰지 않는다. 같은 작성자의 source/result 검토이며 독립 감사가 아니다.

## 실제 진단값과 그림

| u | actual Hfull | actual Hdeleted | actual sigma2 |
|---:|---:|---:|---:|
| -2 | -3 | 1 | 8 |
| -1 | 0 | 1 | 2 |
| 0 | 1 | 1 | 0 |
| 1 | 0 | 1 | 2 |
| 2 | -3 | 1 | 8 |

값은 다섯 입력의 full/deleted mapper 호출(총 10회)에서 반환된 JSON에서 왔다. SC19가 이를 별도로 검사했다.
제공된 plotter는 원본 non-PASS stdout을 보존하고 그림을 만들지 않았다.
수정 후 actual stdout으로 다시 호출해 PNG/SVG 두 종류의 그림을 생성했다.
BASS venv에는 matplotlib가 없었지만 기존 `/usr/bin/python3`의 matplotlib 3.10.8을
사용할 수 있어 설치 없이 완료했다. Wolfram을 plotting 때문에 재실행하지 않았다.

- [Constraint vs shear PNG](plots-repair1/constraint_vs_shear.png) / [SVG](plots-repair1/constraint_vs_shear.svg)
- [Deletion response PNG](plots-repair1/deletion_response.png) / [SVG](plots-repair1/deletion_response.svg)
- [실제 diagnostic rows](diagnostic_rows.json), [추출된 원본 JSON](plots-repair1/STATE_CONSTRAINT_RESULT.json), [시각 검사](VISUAL_INSPECTION.md)

두 PNG를 직접 열어 축·수식·범례·겹침·잘림을 확인했다. u=0의 marker 겹침은
실제 동일값이며, 별도 layout 수리가 필요하지 않았다. 연결선은 다섯 algebraic
입력 사이의 안내선이다. 시간 궤적이나 입력 사이에서 계산한 값이 아니다.

## 실행 기록과 경계

Original SC: `2026-09-07T06:19:47.926601+00:00` → `2026-09-07T06:19:54.352092+00:00`.
repair1 SC: `2026-09-07T06:24:28.431695+00:00` → `2026-09-07T06:24:37.264164+00:00`.
기존 actual Wolfram 15.0.0 kernel을 `wolframscript -local <kernel> -file <runner>`로
직접 호출했다. 모든 Wolfram 호출은 inner 120초 / outer 150초 / TERM 후 10초 kill
및 기존 자원 제한을 유지했다. SC target 2회, 진단 1회, 작은 회귀 2회로 총 5개
Wolfram process, 합산 wall 32.462472초다. 상세 argv,
current-process environment, actual exit와 before/after 기록은
[ATTEMPT_ACCOUNTING.json](ATTEMPT_ACCOUNTING.json)과 execution/에 있다.

AUX/native17/capture6/ownerWLT6 호출은 모두 0회다. 과거 증거·실패·예산을 재사용해
새 SC PASS로 세지 않았다. 원본 dirty checkout, main, PR131 historical head,
후보 dependency와 이전 evidence를 보존한다. 새 commit은 모두 `[skip ci]`이며
workflow 파일·Actions 도구·dispatch·merge·force push·새 PR을 사용하지 않는다.
원격 본문 확인 후 PR131에 링크 댓글만 append한다.

최종 의미는 이 정확한 연구 component map의 `PASS_RESEARCH_COMPONENT_ONLY`다.
Caller의 일관된 symbolic assumptions와 단위 계약은 남아 있다. Numerical RHS,
all-family solver, arbitrary-ell transport, native xTensor four-projection proof,
generic gradient geometry, serialized production ingestion, finite-time stability,
provider/likelihood/RF04 admission은 아니다. BASS init.wl에 설치하지 않았다.
원본과 수정 evidence가 충분하여 추가 scientific 실행·반복 review 없이 반환한다.
