# 현재 후속 단계: S12

2026-10-21 KST. [S12 계약·진척](s12_birth_memory/README_KO.md)과 [고정 계약](s12_birth_memory/CONTRACT.json)을 먼저 읽는다. S11 최종 게시 복구는 [댓글6301060073](https://github.com/cosmosapjw-quantum/bass/pull/174#issuecomment-6301060073)에 있다. 아래 S11 결과와 기존 실패는 그대로 보존한다.

---

# BASS — S11 양의 P246와 유한 전단 응답

**새 P246 birth 알고리즘과 등록한 물리·수학 검증을 완료했다.** 새 Python/Rust projector는 기존 source frame과 방향 support를 유지하며 엄격히 양의 reflection weights를 돌려준다. 저장된 S8 입력의 새 pointwise P24는 원 gate를 통과했고, 같은 n64 support의 P246은 양의 해가 없어 정확히 거부했다. 고정 7-ray의 유한-d 최대 오차가 P24보다 약 1.549배 커진 반례도 보존한다.

[전체 S11 결과](s11_p246/RESULTS_KO.md) · [기계 판독 ledger](s11_p246/RESULT_LEDGER.json) · [이론](s11_p246/THEORY.md) · [DAG](DAG.json) · [현재 closeout](PUBLICATION_CLOSEOUT.json)

**신규 S11 배송은 GitHub와 Dropbox에서 보존됐고, 새 Google Drive 복사는 미완료다.** C1/C2–C5/C6–C9 세 ZIP은 Dropbox 전체 원격 bytes·SHA256·provider hash·CRC·manifest/Git readback을 통과했다. Drive upload 두 번과 별도 copy 요청 한 번은 응답 없이 중단됐고 확인한 새 ID가 없다. 후속 C10 metadata의 정확한 containing HEAD/tree, 마지막 ZIP·JSON과 readback은 [PR174 최신 배송 댓글](https://github.com/cosmosapjw-quantum/bass/pull/174)이 소유한다. 아직 확인하지 않은 배송 성공을 기입하지 않는다. [새 cloud index](delivery/s11/CLOUD_CHECKPOINT_INDEX.json), [C10 판정](delivery/s11/C10_DECISION.json), [cloud 상세](CLOUD_READBACK_KO.md).

## S11 실제 결과

| 항목 | 판정과 범위 |
|---|---|
| Main 새 고정 검증 | 101/101; 14입력·차수 쌍 중 12양의 결과와 2예상 P6 infeasibility |
| Exact gate | 원 normalization/P2/P4 `3/10^15` 유지; P6도 같은 기준. Rust 최대 실제 exact 잔차 `1.0280045769226785e-16` |
| 구현 대조 | Python/Rust 저장 weight 최대 차이 `6.938893903907228e-17` |
| S8 pointwise | 원 b9/n64 birth11 입력에서 새 동시 P24 해법 PASS. 원 failed native history는 변경·재실행하지 않음 |
| P246 support | b9/n64의 `z_max≈0.619510<5/7`; exact 음수 facet. 음의 weights나 tolerance 완화로 우회하지 않음 |
| 응답 | 기존 S3 P8 cubic 재사용, 새 P8/P10 quartic 유도. 국소 bias 차수 P24≈2, P246≈3, cubic 제거 후≈4 |
| 유한 d 반례 | 고정49점 `[-0.6,0.6]`에서 dyadic P24 최대bias `0.02204259946`, P246 `0.03414707019`, 비율 `1.54913989382294` |
| 새 수학 단위 | 별도 recovery25/25; 사라진 새 단위의 원 evidence와 재측정 receipt를 구분 |
| C9 | 독립 수학·응답235/235, provenance152/152. 서로 겹치는 검사 집합이며 합산하지 않음 |

P246의 모멘트 일치와 작은 d의 차수 개선은 모든 support/strain의 angular 정확도나 full native finite-bin 보존을 보증하지 않는다. 49점 최대값은 연속구간 supremum이 아니다. 기존 S8 `INNER_P2_PRECISION_LIMIT` 실패와 낮은 해상도/angular 실패를 유지한다.

![S11 고정 support와 유한 strain 결과](s11_p246/evidence/figure/S11_P246_RESPONSE.png)

[PNG](s11_p246/evidence/figure/S11_P246_RESPONSE.png) · [PDF](s11_p246/evidence/figure/S11_P246_RESPONSE.pdf) · [SVG](s11_p246/evidence/figure/S11_P246_RESPONSE.svg) · [고정49점 CSV](s11_p246/evidence/figure/ANGULAR_RESPONSE_GRID.csv)

## 고정 identity와 증거

| 역할 | Commit |
|---|---|
| S11 계약·read-only intake | `e9f8eccc8d86764ebebe9bb98cc68ecb9aad09d8` |
| S11 실행 전 source/input | `7fb9b83cba01d37ce4cabbc4772527710601cd96` |
| S11 실제 결과·독립 검토 | `85d5833b4486d14855b84a9d967f5819788d05e5` |
| 완료한 S10 배송 metadata | `d0c0313d6c063037fd8e067744aee66235df1a58` |
| S10 실행 source / 결과 / C9 | `d5a173644f5c7c0dbe9eb8757dfc4ccad6c4f4c8` / `26e9e1ba8f39788d98ec33c60f6e9fd2605f8b8a` / `0771f0610987eb9f900674e83063912150733255` |
| 고정 original REI owner | `0e25846433170d0f420c4cda44a0bedbf02cd177` |

S11 source tree는 `963a43f26df1f9c6f462b9df9a2c34cf99f525c9`, 결과 tree는 `fd3e994212059228501e26f7bf3d3b96462ba1d5`다. 실행 source는 main 전에 게시했고 18개 source/input의 bytes·SHA256·Git blob을 연결했다. [Main receipt](s11_p246/evidence/run_r1/PROCESS_RECEIPT.json), [원시 호출](s11_p246/evidence/run_r1/EXECUTIONS.json), [물리 C9](s11_p246/evidence/c9_physics/C9_REVIEW_RESULTS_KO.md), [provenance C9](s11_p246/evidence/c9_provenance/AUDIT_REPORT_KO.md)를 읽는다. 후자는 Rust 작성자의 감사이므로 독립 범위는 root runner/provenance이며 단독 Rust 승인이 아니다. 다른 검토자가 frozen Rust core를 별도로 읽었다.

## 완료된 S9/S10은 재사용한다

2026-10-20의 **원8ZIP+복구보충1ZIP=9ZIP·4,399,983bytes·중복 포함383payload**, 최종 JSON24,280bytes의 양쪽 전체 검증은 완료 상태 그대로다. 초기 intake는 양쪽 최종 JSON bytes/SHA256과 기존9ZIP metadata identity를 대조했다. 원 ZIP CRC/manifest 증거를 재사용했고 이전 캠페인을 다시 돌리지 않았다. [원 최종 배송 댓글](https://github.com/cosmosapjw-quantum/bass/pull/174#issuecomment-6289844952), [현재 read-only intake](s11_p246/CLOUD_INTAKE.json).

S9 고정8history, S10 targeted11/11·kernel108/108·대표RAW24/24 scientific identity·science68/68·원C9 155/155를 보존한다. MF closed2.973배·FLRW4.115배는 원 고정 workload 결과다. Closed small/clock4의1.055배(IQR0.957–1.243)는 일관된 이득을 승인하지 않고 changing n16/cohort2 `0.9498173837599284`배 성능 회귀를 유지한다. [S10 전체 결과](S10_RESULTS_KO.md).

## 물리 계약과 남은 의무

Non-tilted axisymmetric Bianchi I, `(-,+,+,+)`, `a_perp=a exp(-b)`, `a_parallel=a exp(2b)`, `s=dot b`, `Sigma=sqrt(3)|s|/H`를 유지한다. 새 명시적 isotropic birth quadrature만 보정하며 기존 photons·physical anisotropic stock·birth weights·source frame·reflection·양수성·고정 owner를 보존한다.

실제 MD14 정규화/donor closure와 native Einstein/shear shared-Q 결합, evolving reactive full finite-bin spectral history, 더 넓은 finite-d/angular 고차 moment, 새 Rust client의 full birth-memory parameter tangent는 계속 미완료다. 확인한 [PR175](https://github.com/cosmosapjw-quantum/bass/pull/175)의 normalizer/event adapter는 재사용 대상으로 기록했으며 native 물리 완료로 세지 않는다. `5.369926725506957e-12`의 제한된 source-deposition 설명을 전체 spectral-history 수렴으로 바꾸지 않는다.

[새 연구 대화 인계](NEW_THREAD_HANDOFF_KO.md) · [Codex/NCP 인계](CODEX_HANDOFF_KO.md) · [현재 반환 JSON](RETURN_TO_CHATGPT.json).

현재 NCP 재실행 의무는 없다. 추가worker≤16/RAM≤16GiB/disk≤4GiB/개별job≤1800초를 지켰다. 실제환경8CPU/8GiB, main science process1, 기록된 main wall2.37586초·최대 개별child RSS238364KiB, 관측 task allocated disk약1.28GiB다. Runtime refresh로 잃은 초기 smoke raw는 PASS 근거에서 제외했고, 복구 후 게시 source에 결박된 main receipt를 사용한다. [자원 및 복구 기록](s11_p246/evidence/runtime_recovery/RESOURCE_CLOSEOUT.json).

과거 campaign·native history·ODE·benchmark·NCP 재실행과 새 자동 최적화 cycle은0회다. Draft를 유지하며 REIproduction/fullEoR/merge로 확대하지 않는다.
