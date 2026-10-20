# 새 ChatGPT 대화용 handoff — S9 결과 재사용 후 실제 owner 결합 연구

아래 내용을 새 연구 대화에 그대로 전달할 수 있다.

---

`$physmath-research-loop`를 사용해 BASS 연구를 이어라. 사용자에게 과거 대화·ZIP 다운로드·파일 첨부·사전 명령 실행을 요청하지 말고 현재 repo와 연결된 백업에서 직접 복원하라.

```text
Repository: https://github.com/cosmosapjw-quantum/bass
Draft PR174: https://github.com/cosmosapjw-quantum/bass/pull/174
Branch: research/bass-isotropy-checkpoint-recovery-20261018
Lane: research/bass_isotropy_response_20261018/
실제로 실행한 S9 source: 4b30957cb008aad8019bb1a673937fc67bd017e8
Source tree: 8e4abf3820d06bae6cbec307e4f69de74195d14b
S9 preregistration SHA256: 7e615ea1820e95b6fb61d7a360d13bf0fb560b6f25883e17ed487e8a3505f507
VigilODE 구현: a21d573980f66fe02891bd216153443b5352f921
VigilODE 결과 게시: ac1cd2a4738c2441c92e5fdae5f70aba35e53544 (PR71)
REI 고정 spectral owner: 0e25846433170d0f420c4cda44a0bedbf02cd177
SourceID: MD14_Z002_FESC_BB50K_13P6_100_V1
부모 PR173: 4e2d1fa820d6f7baae1069b615fb82a08d53403b
S8 결과 게시: 276172ca6cac9cf6b38561fdf9ba0103e1beb9cf
현재 S9 결과 publication: 이 문서의 containing commit; 최종 배송 receipt/PR 댓글에서 실제 hash 확인
현재 결과 ZIP의 cloud readback: PENDING — 실제 배송 후 최종 receipt로 갱신
Dropbox: /BASS_BACKUPS
Drive folder: 1fFxb-qgExWbEomt3EbbOjGKcslFpGv3y
```

## 재개 전에 읽고 대조할 것

현재 GitHub HEAD/PR 최신 댓글과 두 BASS_BACKUPS의 새 실행결과를 먼저 대조하라. `README_KO.md`, `DAG.json`, `RETURN_TO_CHATGPT.json`, `PUBLICATION_CLOSEOUT.json`, `CLOUD_READBACK_KO.md`, `S9_RESULTS_KO.md`, `S9_THEORY_KO.md`, `S9_THEORY_PACKAGE_REVIEW_KO.md`를 읽고 실제 build·campaign·독립 검토 receipt를 확인하라. S6–S8의 이론·결과는 연결된 `S6_RESULTS_KO.md`, `S7_COUPLED_RESULTS_KO.md`, `S8_RESULTS_KO.md`와 현재 재사용 ledger를 읽는다. 새 evidence의 identity와 가정이 맞으면 이를 우선 채택하고 동일 캠페인을 반복하지 마라.

현재 build는 `evidence_s9/resume_20261020/runtime/PREPARATION_RETURN.json`의 `fresh_build`, 실제 실행은 `evidence_s9/run_20261020_r1/CAMPAIGN_RETURN.json`이다. 각 case의 RAW/PROCESS/ASSESSMENT와 `evidence_s9/RESULT_SUMMARY_20261020.json`을 연결한다. [현재 cloud intake](evidence_s9/resume_20261020/CURRENT_CLOUD_INTAKE.json), [독립 dual receipt](evidence_s9/resume_20261020/science_review/DUAL_REVIEW_RECEIPT.json), [독립 검토 보고](evidence_s9/resume_20261020/science_review/INDEPENDENT_S9_ACTUAL_REVIEW_KO.md)를 직접 읽는다. 과거 `verified_prior_build`와 source/prereg NOT_RUN 문서는 해당 시점의 기록이며 현재 상태를 대체하지 않는다. Source·입력·gate는 실행 전에 `evidence_s9/SOURCE_PUBLICATION_GATE.json`으로 확인했다.

## 완료된 현재 범위

2026-10-20 실제 S9 8개 history를 한 번 실행해 8/8 완료, 140개 gate assertion 통과를 얻었다. 140은 독립 테스트 수가 아니라 사례별 판정 항목 합계다. 독립 이론·수치 검토와 구현·기록 검토는 각각 PASS_SCOPED다. S9를 NCP에서 다시 실행해야 할 의무는 없다.

두 arm은 actual mf_into_ls와 SmallProblem<4>이고, closed history 6개와 analytic FLRW control 2개다. 각 closed history에서 양의 P24 birth 32개가 admission을 통과했다. 기존 photon stock/birth weights를 보존하고 현재 해의 b(u)에서만 새 birth를 만든다. Fine 상태 (h,b,y)의 최대 절대오차은 MF 1.4327428132787645e-13, Small+clock 1.7108536809473662e-13이다. 각 arm에서 rtol 1e-8과 1e-10의 observation 배열은 동일한 plateau이며 형식적인 수렴차수 또는 portable speedup을 주장하지 않았다. S8 수치 참조 153개 출력은 ODE를 다시 풀지 않고 재사용했다.

S6 finite-d certificate, Python exact rank1 certificate, source-deposition spectral 잔차 설명, 처방 기하 source-age 합성은 재사용한다. G5 rate 38/344 실패, P4 제약 44/238 악화는 보존한다. S7 coupled/native의 제한 결과와 실패, S8 tangent 10/10 gate PASS, native 18 attempt/17 measured/n256의 6 PASS/낮은 해상도 8 FAIL/STRICT_INTERIOR precision 1 FAIL을 구분한다. P6 알고리즘과 full spectral/history 수렴이 끝났다고 가정하지 마라.

## 이제 수행할 연구

S9 manufactured donor의 결과를 기반으로 실제 MD14 source 공급부의 시간·체적·에너지·응력 대응을 정식화하고 native Einstein/shear feedback으로 연결하라. 고정 owner가 반환하는 방출/흡수와 source-age data의 단위, physical/comoving volume, cosmic/proper time 및 x, 에너지 공급 소유권과 stress 정규화를 먼저 대응시켜라. 실제 owner 호출과 source-age cohort 합성·보존식 사이의 작은 계산 가능한 bridge를 코드로 구현하고 새 입력·고정 gate로 경량 검증하라. 완료한 기존 캠페인에 새 의미를 부여하지 말고 변경된 의존성만 검증하라.

별도 남은 의무는 P6 제약 알고리즘, continuum angular accuracy의 새 범위, 실제 reactive transport/absorption/history spectral 수렴, native finite-bin photon/energy 보존, 새 client의 full birth-memory parameter tangent이다. 필요성이 명확한 것부터 DAG 의존성 순서로 수행한다. 원전·직접 유도·수치 확인·구현 확인·미완료를 구분하고 새로운 실패의 원인을 분류한다.

Non-tilted axisymmetric Bianchi I, (-,+,+,+), a_perp=a exp(-b), a_parallel=a exp(2b), s=dot b, Sigma=sqrt(3)|s|/H를 유지한다. 새 명시적 등방 source의 angular quadrature만 보정한다. 기존 광자장·physical anisotropic source를 초기화하거나 재가중하지 않으며 birth weights·양성·reflection·source frame·고정 spectral owner를 유지한다. Feasibility와 precision 실패를 음수 weights나 허용오차 완화로 우회하지 않는다.

가능한 유도·구현·경량 검증은 현재 환경에서 완성하고, 새 NCP 실행이 필요하면 source·입력·gate를 먼저 게시·검증해 컴파일·작은 호환 수정·실행만 남겨라. 기존 owner 작업과 실행 중 job을 보존하고 추가 worker16/RAM16GiB/disk4GiB/개별job1800초 상한을 적용한다. 매 완료 단위에서 실행·게시·이중백업/readback·DAG 상태를 따로 남기고 최종 결과와 남은 의무, source/commit/PR, cloud readback 및 갱신한 두 handoff를 본문에 제공하라. REI production/full EoR/merge로 자동 확대하지 않는다.
