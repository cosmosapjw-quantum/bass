# 새 연구 대화 handoff — S11 완료 증거 재사용

원문은 history/20261020_BEFORE_S11_NEW_THREAD_HANDOFF_KO.md에 정확히 보존했다.

```text
$physmath-research-loop를 사용해 BASS의 완료된 S9/S10/S11 증거를 재사용하고 후속 물리 연구만 이어라. 과거 대화·ZIP 다운로드·첨부·사전 명령을 요청하지 마라. 완료 캠페인·solver·자동 최적화 주기를 반복하지 마라.

[고정 위치와 게시 identity]
Repo: https://github.com/cosmosapjw-quantum/bass
Draft PR174: https://github.com/cosmosapjw-quantum/bass/pull/174
Branch: research/bass-isotropy-checkpoint-recovery-20261018
Lane: research/bass_isotropy_response_20261018/
S11 단위: s11_p246/
Stage 1 계약/intake: e9f8eccc8d86764ebebe9bb98cc68ecb9aad09d8
S11 실행 source: 7fb9b83cba01d37ce4cabbc4772527710601cd96
Source tree: 963a43f26df1f9c6f462b9df9a2c34cf99f525c9
S11 결과+독립 검토: 85d5833b4486d14855b84a9d967f5819788d05e5
Result tree: fd3e994212059228501e26f7bf3d3b96462ba1d5
진행 댓글: https://github.com/cosmosapjw-quantum/bass/pull/174#issuecomment-6298011330
최종 containing metadata commit/tree·cloud ID는 이후 최종 PR 배송 댓글·Git ref/readback을 따른다. 자기 hash를 꾸미거나 source/result와 혼동하지 마라.

[먼저 읽기]
현재 GitHub ref/commit/full tree·최신 PR 댓글과 Dropbox·Drive /BASS_BACKUPS를 read-only로 대조한다. Drive folder ID=1fFxb-qgExWbEomt3EbbOjGKcslFpGv3y.
README_KO.md, DAG.json, RETURN_TO_CHATGPT.json, PUBLICATION_CLOSEOUT.json, CLOUD_READBACK_KO.md와 이 handoff 전체를 읽는다.
s11_p246/의 RESULTS_KO.md, RESULT_LEDGER.json, CONTRACT.json, CONTRACT_ADDENDUM.json, THEORY.md를 읽는다. 그 아래 evidence/run_r1/의 RETURN.json·PROCESS_RECEIPT.json·EXECUTIONS.json, evidence/c9_physics/의 RETURN.json·C9_REVIEW_RESULTS_KO.md·C9_PROCESS_R1.json, evidence/c9_provenance/의 AUDIT_R1.json·AUDIT_REPORT_KO.md·AUDIT_R1_PROCESS_RECEIPT.json, evidence/figure/FIGURE_STATS.json을 확인한다.
원 S10_RESULTS_KO.md와 evidence_s10/c9_review_r1/C9_REVIEW_RECEIPT.json, S9_RESULTS_KO.md도 재사용한다. 과거 NOT_RUN·미구현 P6·Drive pending 문장을 현재 판정으로 승계하지 않는다.

[S11에서 실제로 완료한 범위]
고정 reflection support의 양의 P24/P246 KL projector 구현·검토 완료: Python Decimal 동시 Newton+Fraction certificate, 독립 Rust 동시 Newton. 기존 P24/owner/history에 자동 연결하지 않았다.
Main 101/101 PASS_SCOPED, exit0·빈 stderr·wall2.376초. 14쌍 중12양의 성공/2예상 infeasible·24exact certificate·660angular response.
Physics C9 235/235·provenance C9 152/152는 별도 검토다. 152 검토자는 Rust 작성자이므로 Rust의 단독 독립 승인이 아니다. 별도 physics source 검토·저장 결과 재계산을 함께 읽는다. Solver/history 재실행은 없다.
정확 norm/P2/P4 gate 3/10^15를 유지하고 P6에도 적용했다. 음수 weights·tolerance 완화는 없다.
S8 저장 b9_n64/birth11 입력에서 P24 점별 계산을 복구했다. 원 INNER_P2_PRECISION_LIMIT receipt/history는 보존하며 전체 S8 재실행 성공으로 바꾸지 않는다. 같은 support의 P6는 실제 infeasible이다. P24_only의 P6도 min facet slack=-1/42로 실패한다.
S3 cubic/P8 재사용, quartic/P8/P10 추가 검토. 고정 d=k/40, k=-24..24의 49점에서 dyadic uniform 최대 각응답 오차는 P24 0.02204259946, P246 0.03414707019로 1.54913989382294배 악화했다. 이는 구간 supremum이나 history 오차가 아니다. P6가 모든 finite-d에서 개선된다고 주장하지 않는다.
Runtime reset으로 소실된 smoke raw receipt는 TRANSCRIPT_ONLY_NOT_DURABLE, PASS에서 제외한다. 새 S11 수학 복구25/25의 실제 receipt는 evidence/theory/RECOVERY_RECEIPT.json이며 복구 범위는 evidence/runtime_recovery/ROOT_RECOVERY.json을 따른다.

[원 S9/S10과 배송 완료 유지]
원 S10 metadata HEAD=d0c0313d6c063037fd8e067744aee66235df1a58
Tree=e62a42c3227114a5657538a75e034af5a5823703
S10 source=d5a173644f5c7c0dbe9eb8757dfc4ccad6c4f4c8
Result=26e9e1ba8f39788d98ec33c60f6e9fd2605f8b8a
Review=0771f0610987eb9f900674e83063912150733255
원 최종 배송 댓글: https://github.com/cosmosapjw-quantum/bass/pull/174#issuecomment-6289844952
2026-10-20 원8ZIP+복구1ZIP=9ZIP·4,399,983bytes·중복 포함 payload383항목. 양쪽 전체 bytes/SHA256/CRC/manifest와 최종 JSON 전체 바이트·내용 검증 PASS다. 신규 Drive 문제로 원 완료를 취소하지 않는다.
S9 고정8history 완료, S10 targeted11/11·kernel108/108·대표 RAW24/24 scientific identity·science68/68·원 C9 155/155를 재사용한다.
MF 가속비 closed2.973·FLRW4.115는 원 고정 workload 결과다. Closed small 1.055(IQR0.957–1.243)의 이득 불확실성과 changing n16/cohort2의 0.949817배 회귀를 보존한다. 기존 배송 복구에서 과학/build/test/ODE/benchmark/NCP 재실행은 0회다.

[신규 S11 cloud 상태: C10 이중 완료 아님]
작성 시 Dropbox stage1/2/3 전체 readback PASS, stage3=id:BSpOijBcT10AAAAAAD_aCQ. Drive 신규 upload2회+copy_file1회는 무응답·서버 결과 미확정이다. copy344.6초 무응답, 18:23 UTC read-only reconcile은 pending/최종 이름 미관측. update_file 미호출이다.
최종 객체·hash·provider별 검증은 이후 최종 댓글/closeout의 실제 관측을 따른다. 요청·객체 존재·전체 readback을 구분하며 신규 이중 완료를 선포하지 않는다. 원 S10은 완료다.

[보존할 물리와 남은 의무]
Non-tilted axisymmetric Bianchi I, (-,+,+,+), a_perp=a exp(-b), a_parallel=a exp(2b), s=dot b, Sigma=sqrt(3)|s|/H.
고정 original REI owner=0e25846433170d0f420c4cda44a0bedbf02cd177.
새 명시적 등방 birth angular quadrature만 보정한다. 기존 광자장·physical anisotropic stock·birth weights를 초기화·재가중하지 않는다. 양의 weights·reflection parity·source frame·고정 owner를 유지한다. Feasibility/rank/boundary/precision 실패를 분리하며 음수 weight나 gate 완화로 우회하지 않는다.
원 fine reference abs1e-9, Hamiltonian/cohort energy rel1e-11, event1e-13, donor endpoint3e-14, clock abs1e-12를 유지한다. P2/P4/P6 일치만으로 continuum/full native finite-bin 보존을 승인하지 않는다.
남은 의무: 실제 MD14 정규화·donor closure/native Einstein·shear shared-Q; evolving reactive full finite-bin spectral history; 원 S8 precision/history; 더 넓은 finite-d/angular 고차 moment; 새 Rust client full birth-memory parameter tangent. PR175 adapter 검토는 실제 MD14/native feedback 완료가 아니다.
5.369926725506957e-12는 제한된 source-deposition 설명이다. Full spectral-history 수렴 완료가 아니다. S6 rate38/344 실패·P4악화44/238, S7 실패, S8 낮은 해상도8미달·precision1실패를 보존한다.
현재 NCP 재실행 의무는 없다. 후속 물리 의존성만 별도 계약·고정 gate로 진행한다. 추가worker≤16/RAM≤16GiB/disk≤4GiB/개별job≤1800초. 기존 owner 작업·사용자 변경·원 RAW, 단계별 DAG·게시·provider별 backup/readback을 보존한다. REI production/full EoR/merge로 확대하지 마라.
```
