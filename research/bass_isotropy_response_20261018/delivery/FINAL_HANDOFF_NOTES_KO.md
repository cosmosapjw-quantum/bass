# 최종 handoff 보충: 완료 증거 재사용과 다음 미완료 의무

이 문서는 최종 Codex/새 대화 handoff에 붙일 보충본이다. Stage 2 게시 기준은
`a7938ad51ad0fa324c5cb680dddb5fbfc7ed218e`이며, 최종 HEAD·PR 댓글·cloud
readback의 확정 식별은 이후 작성되는 최신 `RETURN_TO_CHATGPT.json`과
`PUBLICATION_CLOSEOUT.json`을 따른다. 아래 완료 상태를 과거 handoff의
미실행 표시로 되돌리지 않는다.

## 먼저 재사용할 완료 증거: 이유 없이 재실행하지 않는다

| 완료 항목 | 확정된 범위·개수 | 읽을 증거 |
|---|---|---|
| PR173 원 native SourceLedger | 58행 + negative controls 5개 완료; 원본 재사용 | `../../bass_sourceledger_20261018/` 및 기존 intake/return |
| PR174 P2-only Python | 기존 15개 완료; 정확한 source identity로 재사용 | `../history/20261018_RETURN_TO_CHATGPT.json`, `../evidence_s2_rust/RETURN_RUST.json` |
| 기존 `balance.rs` | 미실행이었던 5개가 실제 실행되어 **5 PASS**; 원 파일 무변경 | `../evidence_s2_rust/RETURN_RUST.json` |
| S3 직접 유도·독립 검산 | D의 0~3차 Legendre 전개, 양의 반례, 80-digit Decimal, exact rational support 1023개 검산 완료 | `../evidence_s3/theory_independent.json` |
| 새 Python S3 | **14 PASS** | `../evidence_s3/campaign/TEST_S3.log` |
| 새 std-only Rust P24 | **16 PASS**; CLI valid 1 + negative controls 7 완료 | `../evidence_s3/rust_p24_execution.json`, `../evidence_s3/rust_p24_cli_artifacts/RETURN.json` |
| Python/Rust 같은 입력 | **43 PASS** | `../evidence_s3/campaign/RETURN_RUST_PARITY.json` |
| Angular 측정 | 165 rule 시도, 146 성공, 19 구체적 지지 실패, 1606 response points 저장 | `../evidence_s3/campaign/ANGULAR_CAMPAIGN.json`, `../evidence_s3/campaign/RETURN_S3_CAMPAIGN.json` |
| 저장 측정 reuse guard | 최종 **13 PASS**; F1/F2 수정·독립 재검토 완료 | `../evidence_s3/reuse_guard_validation_r2/RETURN_REUSE_GUARD.json`, `../evidence_s3/INDEPENDENT_PYTHON_REVIEW.json` |
| 새 native adapter | **7 native tests PASS + 20 측정행 + 6 Python runner regressions PASS** | `../evidence_native_s3/run01/RETURN_NATIVE_ADAPTER.json`, `../evidence_native_s3/run01/PYTHON_RUNNER_REGRESSIONS.json` |
| 새 adapter 초기 P2 preflight | 별도 1건 완료; historical `P24=NOT_RUN_PENDING_MODULE`은 당시 상태 그대로 보존 | `../evidence_native_s3/p2_preflight/RETURN_PREFLIGHT.json` |

개수가 서로 다른 tests, controls, support proofs, measurement rows를 하나의
총 테스트 수로 합산하지 않는다. Figure의 첫 mathtext 실패는 저장 측정으로
복구했고, 이후 reuse-guard 수정은 물리·optimizer를 바꾸지 않았다. 최초
measurement producer, 실행된 report producer, 최종 reuse-guard source SHA를
서로 구별한다. 이미 완료한 optimizer/native 캠페인을 단순 보고서 재생성이나
마감 확인 때문에 반복하지 않는다.

## 다음 미완료 연구 의무

1. **Finite-d continuum angular error와 고차 moments.** P2=0은 birth isotropy를,
   P4=0은 첫 collisionless response coefficient를 제어한다. P6와 더 높은
   moments는 여전히 남는다. 저장된 동일 `(birth b, n_mu, d)` 비교를 먼저
   재사용하고, 연구할 d 범위와 오차 지표를 정한 뒤 추가 유도·certificate 또는
   필요한 새 점만 측정한다. Angular refinement와 새 moment constraint를
   계속 독립된 축으로 비교한다. P6 제약 알고리즘이 이미 구현되었다고 가정하지 않는다.
2. **Exact rank1의 실행 certificate.** 양의 rank1 해가 존재하는 지지와 그
   수학적 판정은 검산했다. 현재 f64 코드의 affine-compatible 입력은
   `FEASIBILITY_UNRESOLVED_RANK1`로 남는다. Exact 입력 표현과 양의 해를
   보장하는 실행 경로를 별도로 설계해야 하며, unresolved를 infeasible 또는
   PASS로 바꾸지 않는다.
3. **고정 native spectral owner의 잔차·refinement.** 새 adapter의 20행에서
   nonempty-stock transfer ledger와 실제 energy moments/전단 tangent를
   검증했다. 고정 source-cell mean energy 대비 최대 상대 차이
   `5.369926725506957e-12`는 남은 진단값이다. Spectral panel refinement와
   finite-bin refinement를 angular constraint 변화와 분리해 원인을 조사한다.
   이 20행을 일반적인 native finite-bin 수렴·보존 승인으로 확대하지 않는다.
4. **Source-age 합성과 coupled shear feedback.** Source-age 선도항의 이론적
   유도와 실제 history convolution 실행은 구별한다. 각 cohort의 birth weights를
   고정하고 source-age 합성, reactive coupling, Einstein feedback을 차례로
   검증해야 한다. 단일 birth의 고정-a kinematic family를 실제 cosmological
   history 실행으로 부르지 않는다.

## 이어서 작업할 때의 고정 조건

Non-tilted axisymmetric Bianchi I와 `(-,+,+,+)`,
`a_perp=a exp(-b)`, `a_parallel=a exp(2b)`, `s=dot b`,
`Sigma=sqrt(3)|s|/H`를 유지한다. 원 owner는 REI
`0e25846433170d0f420c4cda44a0bedbf02cd177`이다. 새로 선언된 locally isotropic
source의 angular quadrature만 보정하고 old photon stock, 물리적으로
anisotropic source, source frame 및 spectral owner를 보존한다.

새 실행이 필요한 구체적인 미완료 질문이 생기면 이미 준비된 runner로 정확한
owner를 취득·검증하고 컴파일·작은 수정·실행만 이어 간다. NCP에서 기존
native 20행을 기본 의무로 반복하지 않는다. 추가 workers 16 / RAM 16GiB /
disk 4GiB / 개별 job 1800초 상한과 기존 owner 작업을 보존한다. 음의 weights,
허용오차 확대, 지지 삭제로 실패를 우회하지 않는다.

재개 시 Dropbox와 Google Drive의 `/BASS_BACKUPS`에서 새 receipt를 먼저
읽고 현재 GitHub HEAD 및 PR174 최신 댓글과 대조한다. 새 결과가 있으면
완료 증거에 우선 반영한다. 사용자에게 과거 대화, ZIP, 파일 첨부 또는 사전
명령 실행을 요청하지 않는다. REI production, full EoR 및 merge는 충분한
검증과 해당 gate 없이 자동 확대하지 않는다.
