# BASS CE1-F 구현 병렬분기 조정 및 수학적 보증 결함 수정

## 판정

**CE1-F-RECON = COMPLETE_SCOPED_PROOF_PRECONDITION_REPAIR_AND_SAME_INPUT_COMPARISON**. 상위 CE-1은 `PARTIAL`, 원래 상위 DAG는 **9/15** 그대로다. 이 결과는 CE1-G의 물리/시간오차 연구를 수행하거나, 기존 구현 브랜치 두 개를 병합한 결과가 아니다. `production_ready=false`, `merge_ready=false`.

### Source authority

- 대조 대상 A: PR #239 (`research/bass-ce1f-tabulated-angular-certificate-20261029`), inspected HEAD `9de0f37955f259b5e9172ce406d1353bf7cc3695`, source Git blob `e1f5e11baada25858f8fb03321f071ed759b6f99`. 이쪽은 기존 독립 C9 review를 거쳤고 정확한 이산 E0 상한을 이미 사용한다.
- 대조 대상 B: PR #238 (`research/bass-ce1f-tabulated-meanray-implementation-20261029`), parent HEAD `0286dd0a97f512a2dc6f431e462e64bd65267047`, 원본 code Git blob `6bc2787ea07d03e4c739cb53e43f9e21f9d6d842`.
- 현재 보정 코드는 B의 **격리된 자식 브랜치**에서만 변경했다. 수정 후 source blob `be835c9a56ac32781a235d3b89d493c3f8dc7902`, 신규 테스트 blob `d2af7f0cc3646e290d02ee36fdde1a5b9e22faaf`. A, B 부모, 진행 중인 PR #240/CE1-G와 main·owner를 수정·병합하지 않았다.
- A의 문서 `research/ce1f_20261029/RECONCILIATION_KO.md`에서 문제를 먼저 지적했다. 현재 턴에서는 그 반례를 **독립 Python/Decimal105 경로로 재현**하고 실제 코드 수정을 수행했다.

## 증명 전제 결함: exact-real stored energy를 과소 평가

연속계 초기 에너지는 \(E_{0,C}=\sum_C w_C\), 실제 저장 이산 source의 정확한 실수 에너지는 \(E_{0,Q}=\sum_C \hat w_C\sqrt{\sum_i\hat n_{Ci}^{2}\)이다. B의 기존 구현은 \(E_\max=\max(E_{0,C}, \mathrm{float64}(E_{0,Q}))\)를 사용했다. 이는 부동소수점으로 평가된 에너지이지 정확한 저장-source의 상한이라는 보장이 없다.

단일 양의 구면 전 octant cell \(w=9/10\)에서 저장 광선의 정확한 노름제곱은 \(81129638414606703496731723412443/81129638414606681695789005144064>1\). Decimal105 독립 평가에서

\[
E_{0,Q}=0.9000000000000001431272750758168544229966\ldots,
\qquad E_\max^\mathrm{old}=0.9000000000000000222044604925\ldots
\]

이므로 \(E_{0,Q}-E_\max^\mathrm{old}=1.209228145833137236\ldots\times10^{-16}>0\). 이 경우 B의 source-to-geometry 비교부등식에서 요구되는 \(E_{0,Q}\le E_\max\) 전제가 성립하지 않는다. **최종 기하학 값 자체가 이 상계를 위반했다는 반례는 아니며, 물리 방정식의 반례도 아니다.**

## 최소 보정과 증명

`certified_tabulated_energy`가 계산한 \(\Delta_E^+\ge |E_{0,Q}-E_{0,C}|\)는 정확한 저장 이진값과 MPFR 외향연산을 통해 얻은 상한이다. 따라서

\[
E_{0,Q}\le E_{0,C}+\Delta_E^+,\qquad
\boxed{E_\max^+=\max\{E_{0,C}^+, (E_{0,C}+\Delta_E^+)^+\}}.
\]

실제로 code에서는 이 양을 `E_Q_upper`, `Emax`로 사용하고 `energy_max_upper` 반환값을 명시했다. 각도 대표광선 제곱 \(X_i=\hat n_i^2\)의 upper cap도 최근접 반올림 `float(X_i)` 대신 `_iv_fraction(X_i).upper`를 사용해 증명상 상한 조건을 명시했다. 물리적 RHS, 원본 cell 값, numerical time solver, acceptance tolerance, raw weight 및 projection은 수정하지 않았다.

## 동등성 교차검증: 정확히 같은 물리 입력

두 branch는 API 입력 형태가 다르다. A에는 binary64 float, B에는 그 float의 **정확한 이진 유리수 문자열**을 전달해 동일한 piecewise-constant continuum 물리분포를 구성했다. \(\mu=(0,1/2,1)\), 첫 octant 방위각 좌표 \(t=(0,1/4,3/4,1)\), 에너지 행렬 \((0.1,0.25,0.05);(0.2,0.15,0.15)\)를 사용했다. 다른 초기자료에서 얻은 \(10^{-5}\) 목표 판정과 교차 비교하지 않았다.

| refine | rays | 압력 최대 차이 | 결합 상태 최대 차이 | PR239 h 상계 | 보정 B h 상계 |
|---:|---:|---:|---:|---:|---:|
| 1 | 6 | 5.551e-17 | 1.110e-16 | 0.000706345786932 | 0.000706345786932 |
| 2 | 24 | 1.110e-16 | 5.551e-17 | 0.000183165801598 | 0.000183165801598 |
| 4 | 96 | 1.110e-16 | 1.110e-16 | 4.60258856547e-05 | 4.60258856547e-05 |
| 8 | 384 | 1.110e-16 | 1.110e-16 | 1.14875028708e-05 | 1.14875028707e-05 |


최대 압력차 \( 1.110e-16 \), 최대 6상태 IVP 차 \( 1.110e-16 \). 본문 비교는 물리적 부동소수점 동등성의 수치적 근거이며 모든 입력에 대한 수학적 동등성 증명은 아니다. 두 source 모두 별도의 원본-cell GL32 기준에 대해 오차가 각자가 보고한 upper 내부였고, 최대 측정오차/상계 비율 \( 0.08930\)였다. 실제 비교는 GitHub Actions **40792700025**에서 step 종료 코드0으로 확인했고 JSON과 log artifact **12862327693**을 다운로드해 원본 포함 ZIP에 보존했다. \(u\in[0,.08]\), refinement1/2/4/8, 16개 seeded random log-scale states +3 fixed, 4 paired DOP853 IVPs.

## TDD·검증·재현성

- 수정 전 신규 단위 테스트: **5 FAIL + 1 PASS** (반례 자체는 PASS, 필수 `energy_max_upper` 계약 불충족). 원래 47개 baseline PASS.
- 수정 후 신규 6 PASS, 부모 47 PASS, 합계 **53 PASS** 로컬; CI는 재실행 후 53 PASS. 별도 설치 wheel의 단일-cell 정확 저장 E 상계 smoke PASS.
- 초기 workflow #40792407814는 `python compare_variants.py | tee`의 Python import 오류가 pipeline 종료 코드에 가려져 거짓 전체 SUCCESS가 됐다. 이를 **검증 미수행으로 판정**한 후 `set -euo pipefail`과 `PYTHONPATH=.`을 적용. 후속 CI #40792700025에서 비교 프로그램·53 pytest·wheel 모두 SUCCESS 확인. 초기에 발생한 false-green 로그도 원시 provenance로 보존한다.
- Native subagent, Rust 생산 implementation 및 독립 형식검증은 `NOT_RUN`. 메모리+Python 숫자 검증은 완전한 컴파일러/MPFR 바인딩의 형식적 증명이 아니다.

## 연구 결과 및 다음 선택

이번 조정의 결론은 **동일 입력에 대한 상태·source 수치결과는 일치하지만 바이트와 API는 다르고, B의 Emax 증명 전제는 보정 전까지 미충족**이었다는 것이다. A(검토된 PR239)를 source authority 후보로 추천한다. B는 보정 PR로 과학적 교차참조를 보존하고 자동 병합하지 않는다. PR238의 직접 source/pressure 결과를 전부 폐기하는 것은 부적절하다.

최신 PR240이 CE1-G whole-panel time-defect 연구를 별도로 진행 중이었다. 이 연구를 자동 재실행·병합하지 않고 그 HEAD·CI를 다음 스레드에서 확인한 뒤, 동일 모델에 대한 source+time 결합 인증으로 넘어갈지 판단한다. 원래 15 top-level DAG 노드·edges를 유지하고 CE-1은 PARTIAL, **9/15**로 기록한다.
