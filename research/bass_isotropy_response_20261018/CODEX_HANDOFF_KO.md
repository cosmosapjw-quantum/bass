# Codex handoff — S11 P246를 재사용하는 후속 구현

원문은 history/20261020_BEFORE_S11_CODEX_HANDOFF_KO.md에 정확히 보존했다.

```text
$physmath-research-loop로 완료된 BASS S9/S10/S11을 재사용하고 후속 물리 구현만 이어라. 과거 대화·ZIP 다운로드·첨부·사전 명령을 요청하지 마라. 완료 캠페인·자동 최적화 cycle·solver를 반복하지 마라.

[고정 repository/identity]
Repo=https://github.com/cosmosapjw-quantum/bass
Draft PR174=https://github.com/cosmosapjw-quantum/bass/pull/174
Branch=research/bass-isotropy-checkpoint-recovery-20261018
Lane=research/bass_isotropy_response_20261018/
S11 unit=s11_p246/
Stage1 계약/intake=e9f8eccc8d86764ebebe9bb98cc68ecb9aad09d8
S11 실행 source=7fb9b83cba01d37ce4cabbc4772527710601cd96
Source tree=963a43f26df1f9c6f462b9df9a2c34cf99f525c9
S11 결과+검토=85d5833b4486d14855b84a9d967f5819788d05e5
Result tree=fd3e994212059228501e26f7bf3d3b96462ba1d5
진행 댓글=https://github.com/cosmosapjw-quantum/bass/pull/174#issuecomment-6298011330
최종 containing metadata commit/tree·cloud ID는 이후 최종 PR 배송 댓글·Git ref/readback을 따른다. 자기 hash를 꾸미거나 source/result와 혼동하지 않는다.

[첫 행동: read-only]
GitHub ref/commit/full tree·최신 댓글과 Dropbox·Drive /BASS_BACKUPS를 대조한다. Drive folder ID=1fFxb-qgExWbEomt3EbbOjGKcslFpGv3y.
Lane README_KO.md, DAG.json, RETURN_TO_CHATGPT.json, PUBLICATION_CLOSEOUT.json, CLOUD_READBACK_KO.md, NEW_THREAD_HANDOFF_KO.md 전체를 읽는다.
S11 unit의 RESULTS_KO.md, RESULT_LEDGER.json, CONTRACT.json, CONTRACT_ADDENDUM.json, THEORY.md, SOURCE_KO.md를 읽는다. Unit 아래 evidence/run_r1/{RETURN,PROCESS_RECEIPT,EXECUTIONS}.json, evidence/c9_physics/RETURN.json·C9_REVIEW_RESULTS_KO.md, evidence/c9_provenance/AUDIT_R1.json·AUDIT_REPORT_KO.md와 두 C9 process receipt, evidence/figure/FIGURE_STATS.json을 확인한다.
S9_RESULTS_KO.md, S10_RESULTS_KO.md, evidence_s10/c9_review_r1/C9_REVIEW_RECEIPT.json 및 원 S6–S8 receipt도 재사용한다. 역사적 NOT_RUN·미구현 P6·배송 pending을 현재 상태로 승계하지 않는다.

[재사용할 구현·검토]
P24/P246 fixed-support positive KL projector 구현·검토 완료: Python Decimal 동시 Newton+Fraction certificate, Rust 동시 Newton+outward interval preflight. 새 등방 birth 전용이며 기존 P24/stock/owner/history에는 자동 연결하지 않았다.
Norm/P2/P4 exact gate=3/10^15를 유지하고 P6에도 적용한다. 입력 f64의 정확한 Fraction, |mu|≤1, 정렬·중복 거부·명시적 birth 선언을 유지한다. Rust PROJECTED_NEEDS_EXACT_CERTIFICATE만으로 승인하지 않으며 interval·rank·boundary·precision 미확정을 성공으로 바꾸지 않는다.
Main 101/101 PASS_SCOPED, exit0·빈 stderr·wall2.376초. 14쌍 중12양의 성공/2예상 infeasible·24exact certificate·660angular response.
Physics C9 235/235·provenance C9 152/152는 별도 검토다. 152 작성자는 Rust 구현자이므로 Rust의 단독 독립 승인이 아니다. 별도 source 검토·저장 결과 재계산을 함께 읽는다. Solver/history 재실행은 없다.
S8 원 b9_n64/birth11 입력의 P24 점별 precision을 복구했다. 원 INNER_P2_PRECISION_LIMIT와 전체 history 판정은 그대로다. b9_n64의 P6 support는 실제 infeasible이며 P24_only P6도 min slack=-1/42로 실패한다. 입력·기존 weights 변경이나 음수 weights·gate 완화로 우회하지 않는다.
S3 cubic/P8을 재사용하고 quartic/P8/P10을 검토했다. d=k/40, k=-24..24 고정49점에서 dyadic uniform 최대오차는 P24 0.02204259946→P246 0.03414707019, 1.54913989382294배 악화했다. 보편적 finite-d 개선·구간 supremum·full-history 수렴 인증이 아니다.
소실된 smoke raw receipt는 TRANSCRIPT_ONLY_NOT_DURABLE, PASS에서 제외한다. 새 S11 수학 복구25/25의 실제 receipt와 범위는 evidence/theory/RECOVERY_RECEIPT.json·evidence/runtime_recovery/ROOT_RECOVERY.json을 따른다.

[원 S9/S10 완료]
S10 metadata=d0c0313d6c063037fd8e067744aee66235df1a58
Tree=e62a42c3227114a5657538a75e034af5a5823703
Source=d5a173644f5c7c0dbe9eb8757dfc4ccad6c4f4c8
Result=26e9e1ba8f39788d98ec33c60f6e9fd2605f8b8a
Review=0771f0610987eb9f900674e83063912150733255
원 배송 댓글=https://github.com/cosmosapjw-quantum/bass/pull/174#issuecomment-6289844952
2026-10-20 원8ZIP+복구1ZIP=9ZIP·4,399,983bytes·중복 포함 payload383항목. 양쪽 bytes/SHA256/CRC/manifest와 최종 JSON 전체 바이트·내용 검증 PASS다. 신규 Drive 문제로 되돌리지 않는다.
S9 고정8history, S10 targeted11/11·kernel108/108·대표 RAW24/24 scientific identity·science68/68·원 C9 155/155를 재사용한다.
MF closed2.973배·FLRW4.115배는 원 고정 workload 한정이다. Closed small1.055(IQR0.957–1.243)의 이득 불확실성, changing n16/cohort2의0.949817배 회귀를 보존한다. 원 배송 복구의 과학/build/test/ODE/benchmark/NCP 재실행은0회다.

[신규 배송은 별도 미완료]
작성 시 Dropbox stage1/2/3 전체 readback PASS, stage3=id:BSpOijBcT10AAAAAAD_aCQ. Drive 신규 upload2회+copy_file1회는 무응답·서버 결과 미확정. copy344.6초 무응답, 18:23 UTC read-only reconcile은 pending/최종 이름 미관측. update_file 미호출이다.
신규 C10 이중 완료라고 쓰지 않는다. 최종 객체/hash/provider별 readback은 실제 관측 후 최종 댓글·closeout에 기록한다. 요청·객체 존재·전체 readback을 구분한다. 원 S10은 완료다.

[물리 계약·후속 의무]
Non-tilted axisymmetric Bianchi I, (-,+,+,+), a_perp=a exp(-b), a_parallel=a exp(2b), s=dot b, Sigma=sqrt(3)|s|/H.
Original REI owner=0e25846433170d0f420c4cda44a0bedbf02cd177.
새 명시적 등방 birth quadrature만 보정한다. 기존 photon field·physical anisotropic stock·birth weights는 초기화·재가중하지 않는다. 양의 weights·reflection parity·source frame·고정 owner를 유지한다.
원 fine reference abs1e-9, Hamiltonian/cohort energy rel1e-11, event1e-13, donor endpoint3e-14, clock abs1e-12를 유지한다. P2/P4/P6 일치로 continuum/full native finite-bin 보존을 승인하지 않는다.
남은 구현: 실제 MD14 정규화·donor closure/native Einstein·shear shared-Q, evolving reactive full finite-bin spectral history, 원 S8 precision/history, 더 넓은 finite-d/angular 고차 moment, 새 Rust client full birth-memory parameter tangent. PR175 adapter 검토는 실제 MD14/native feedback 완료가 아니다.
5.369926725506957e-12는 제한된 source-deposition 설명이며 full spectral-history 수렴 완료가 아니다. S6 rate38/344 실패·P4악화44/238, S7 실패, S8 낮은 해상도8미달·precision1실패를 보존한다.
현재 NCP 재실행 의무는 없다. 후속 물리 의존성만 계약·입력·고정 gate로 진행한다. 추가worker≤16/RAM≤16GiB/disk≤4GiB/개별job≤1800초. 기존 owner 작업·사용자 변경·원 RAW와 단계별 DAG·게시·provider별 백업/readback·source/result/review/metadata·실패를 보존한다. REI production/full EoR/merge로 확대하지 마라.
```
