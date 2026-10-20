# BASS — S9 실제 이력과 S10 최적화 결과

**S10의 연구·구현·정확도·성능·독립 검토와 두 인계를 완료했다.** 원 과학 출력을 유지한 matrix-free history에서 SIMD+exact-cache의 중앙 가속비2.973/4.115를 관측했다. Closed small/clock4는1.055(IQR0.957–1.243)로 일관된 이득을 인정하지 않고, 작은 changing-state kernel의0.950 회귀를 보존했다. [전체 결과와 모든 후보 표](S10_RESULTS_KO.md), [C10 판정](evidence_s10/C10_DECISION.json)을 먼저 읽는다.

오늘의 이전7개 archive는 GitHub 게시·Dropbox 전체 원격 bytes/SHA256/CRC/manifest 검증을 마쳤다. **Drive 새 두 번째 복사는 connector 무응답으로 blocked**다. 이 파일을 포함한 최종 C10 metadata archive의 정확한 commit/tree/hash와 마지막 Dropbox readback은 [PR174 최종 배송 댓글](https://github.com/cosmosapjw-quantum/bass/pull/174)이 소유한다. 이 문서 안에서 자기 commit/hash 또는 이중백업 성공을 선기록하지 않는다.

## 현재 검증 범위

| 범위 | 실제 결과 |
|---|---|
| S9 처음 실행한 고정 캠페인 | 8/8완료,140/140 quality 판정,1224관측,192exact birth instance; 독립 검토 PASS_SCOPED |
| S10 targeted 구현 검증 | release11/11; 정상short run23·예상input failure7 |
| S10 kernel proof | 108records×64queries, 여섯mode bit identity |
| S10 전체 과학 출력 | 대표24RAW와 모든 반복의 timing제외 scientific fields 동일, 기존68gate PASS |
| S10 성능 반복 | micro1260timed,prep378,serial304호출+parallel192호출; 고유 물리입력4개 |
| S10 별도 할당 계측 | 108rows; 다섯최적화 mode의 등록 evaluation 구간 allocation0, 준비비용 별도 |
| S10 C9 독립 검토 | 155/155,612관측·64birth 직접 계산; code/science finding0, 문서finding1수정확인 |
| Delivery | 이전7archive Dropbox fullbytes PASS; Drive blocked; 최종 C10 postcommit receipt는 PR174참조 |

## 정확한 source 역할

| 역할 | Commit |
|---|---|
| 원 S9 과학 source | `4b30957cb008aad8019bb1a673937fc67bd017e8` |
| S9 실제 결과 | `a40311796f9aac5ea5e0e58c630bee2a78443353` |
| S10 실행 구현·사전등록 | `d5a173644f5c7c0dbe9eb8757dfc4ccad6c4f4c8` |
| S10 실제 원표본·분석 | `26e9e1ba8f39788d98ec33c60f6e9fd2605f8b8a` |
| S10 독립 검토·문서수정 | `0771f0610987eb9f900674e83063912150733255` |
| 원 REI spectral owner | `0e25846433170d0f420c4cda44a0bedbf02cd177` |
| 실제 VigilODE | `a21d573980f66fe02891bd216153443b5352f921` |

현재 C10 metadata는 위 실행 source를 바꾸지 않는다. Frozen manifest SHA256은 `4ac631dced7e1d4fdc8ce63d076dfe15bb38bde7040029644e2c34f30b1ebc17`이다. PR은 Draft이며 base PR173 `4e2d1fa820d6f7baae1069b615fb82a08d53403b`를 유지한다.

## 읽는 순서와 실행 재사용

1. [현재 반환 metadata](RETURN_TO_CHATGPT.json), [DAG](DAG.json), [출판 마감](PUBLICATION_CLOSEOUT.json), [cloud readback](CLOUD_READBACK_KO.md).
2. [S10 최적화 계약/단계](S10_OPTIMIZATION_KO.md), [유도](S10_THEORY_KO.md), [결과](S10_RESULTS_KO.md), [고정 protocol](evidence_s10/c4/BENCHMARK_PROTOCOL.json).
3. [실제 실행 receipt](evidence_s10/run_20261020_r1/EXPERIMENT_POSTCHECK.json), [독립 검토](evidence_s10/c9_review_r1/C9_REVIEW_RECEIPT.json), [C10 판정](evidence_s10/C10_DECISION.json).
4. [새 연구 대화용 인계](NEW_THREAD_HANDOFF_KO.md), [Codex/NCP 인계](CODEX_HANDOFF_KO.md).

S9/S10의 완료 source·입력·gate가 맞는 증거를 재사용한다. Cloud 복구나 metadata 확인을 이유로 완료한 과학 캠페인을 반복하지 않는다. 현재 범위는 샌드박스에서 끝났고 추가 NCP 실행 의무가 없다. 같은 source의 재현이 별도로 필요할 때만 기존 pinned/offline runtime와 execute wrapper의 gate를 따른다. Frozen source의 README/PREREG/NOT_RUN은 사전등록 시점 기록이므로 실제 결과를 덮어씌워 고치지 않는다.

## 물리 계약과 남은 연구

Non-tilted axisymmetric Bianchi I,(-,+,+,+),a_perp=a exp(-b),a_parallel=a exp(2b),s=dot b,Sigma=sqrt(3)|s|/H. 기존 photons·physical anisotropic stock·birth data·source frame·reflection·양의 weights·고정spectral owner는 불변이다. 새 명시적 isotropic birth만 원 admission을 통과한다. 허용오차 완화·음수weights·재가중으로 실패를 우회하지 않는다.

S6 finite-d/rank1/source-deposition 설명의 제한된 완료는 재사용한다. P2/P4 일치나 S10 bit identity가 continuum/full native finite-bin 보증을 뜻하지 않는다. P6 알고리즘, 넓은 angular 범위, 실제 MD14 공급부의 에너지·시간·응력 closure와 native Einstein feedback, full reactive finite-bin spectral history, 이 Rust client의 full parameter tangent는 남아 있다. S6 rate38/344FAIL, above-noise P4악화44/238, S7 angular FAIL2rows, S8 낮은해상도8fails와 INNER_P2_PRECISION_LIMIT를 보존한다.

추가worker16/RAM16GiB/추가disk4GiB/개별job1800초 상한. 실제환경8CPU/8GiB, build2, 독립이력1/2/4를 측정했고 이번4job묶음의 후속우선선택은2workers다. REIproduction/fullEoR/merge 또는 CI PASS를 승인하지 않는다.
