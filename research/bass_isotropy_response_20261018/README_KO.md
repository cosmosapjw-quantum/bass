# BASS S3와 native 새 source 보정: 실제 실행 완료

2026-10-19. **P2 birth isotropy와 이후 collisionless shear response는 서로 다른 조건**임을
직접 유도·검산했다. 양의 P2/P4 Python/Rust 보정, 분리된 angular 캠페인 및 고정 REI
owner에 연결한 실제 native 새 source adapter의 제한 검증을 마쳤다.

| 결과 | 근거 |
|---|---|
| D의 0~3차 Legendre 미분, 양의 반례, exact support1023개 | [S3_THEORY_KO.md](S3_THEORY_KO.md) |
| Python14, Rust16, CLI valid1/negative7, 동일 입력43, reuse guards13 PASS | [S3_RESULTS_KO.md](S3_RESULTS_KO.md) |
| 165 rule 중146 측정,1606 response points,19 구체적 지지 실패 | [S3 캠페인 receipt](evidence_s3/campaign/RETURN_S3_CAMPAIGN.json) |
| 원 native owner compile, 새 native tests7,20 측정행, runner regressions6 PASS | [NATIVE_ADAPTER_KO.md](NATIVE_ADAPTER_KO.md) |
| Python 두 review finding 수정·종결, Rust와 native adapter 별도 독립 검토 | [Python 검토](evidence_s3/INDEPENDENT_PYTHON_REVIEW.json), [native 검토](evidence_native_s3/INDEPENDENT_ADAPTER_REVIEW.json) |

`F=<R>`, `G=<D>`, `A=G/F`, `M_l=<P_l>`로 쓰면
`M2=0 => A'(0)=-8/5+(36/35)M4`이고,
`M2=M4=0 => A''(0)=16/7+(216/77)M6`다.
P4를 맞춰도 고차 moments와 유한-d angular error는 남는다.

기존 `balance.rs`의 작성된5개 테스트는 원본 무변경으로 실제 실행해 통과했다.
S2 게시 commit은 `87149cdb673c250ccbb36dda5d43a38f0f7dd7b7`, S3 게시 commit은
`a7938ad51ad0fa324c5cb680dddb5fbfc7ed218e`다. 기존 Python15 및 PR173 native58/
negative5는 원본 증거를 재사용했고 새 실행으로 세지 않는다.
실제 native source 게시 commit은 `b30a2044be1ae04a68d8319f47d15a5bed751668`,
tree는 `bf3a57343140fda867bae9ea94932d9c1475f53b`다.

## Native 결과의 범위

원 owner `cosmosapjw-quantum/rei_bianchi@0e25846433170d0f420c4cda44a0bedbf02cd177`의
57개 원 파일을 그대로 컴파일했다. 새 source를 빈 임시 state에 주입하고 그 birth에만
양의 angular 배율을 적용한 후 기존 state에 transactionally 더한다. 기존 anisotropic stock,
spectral integrals, bin 및 source frame은 유지한다. Caller는 새 locally isotropic emission과
non-tilted local orthonormal frame을 명시해야 한다.

20개 native 사례에서 old-stock photon/energy transfer ledger의 최대 상대 잔차는
각각 `8.62786e-14`, `1.43679e-13`이었다. 기존 parent ledger gate `1e-11`을 유지했다.
Measured native derivative와 실제 energy-moment 식의 차이는 최대 `1.30149e-10`이었다.
이 native quantity는 birth energy로 나눈 `G'(0)`이다. A의 현재 energy 정규화와 구별한다.

Native energy와 고정 source-cell 평균의 최대 상대 차이 `5.36993e-12`는 그대로 남긴
진단값이다. 24/96-bin 비교만으로 spectral convergence를 인증하지 않는다.
Native job은 Rust1.94.1로14.96초, 관측된 child peak RSS339804KiB,
생성 disk16409633bytes였다. NCP는 실행하지 않았고 현재 native 범위의 미실행 의무는 없다.

## 고정 조건과 재개

Non-tilted axisymmetric Bianchi I, signature `(-,+,+,+)`, `a_perp=a exp(-b)`,
`a_parallel=a exp(2b)`, `s=dot b`, `Sigma=sqrt(3)|s|/H`를 유지한다.
새 명시적 등방 source의 angular quadrature만 보정하며 existing photons와 물리적
anisotropic source는 초기화하지 않는다. Strict positivity/reflection parity와 고정
spectral owner를 유지하고 feasibility 실패를 음의 weights나 tolerance 완화로 우회하지 않는다.

현재 상태는 [DAG.json](DAG.json), [RETURN_TO_CHATGPT.json](RETURN_TO_CHATGPT.json),
[PUBLICATION_CLOSEOUT.json](PUBLICATION_CLOSEOUT.json)을 따른다. 과거 문서는 history/에
보존한다. [Codex handoff](CODEX_HANDOFF_KO.md), [새 대화 handoff](NEW_THREAD_HANDOFF_KO.md)는
이미 완료된 캠페인을 반복하지 않고 새 백업·PR 결과를 먼저 대조하도록 한다.

남은 연구는 finite-d continuum error/고차 moment, exact rank1 실행 certificate,
고정 owner spectral refinement/잔차 설명, source-age 합성과 coupled shear feedback이다.
현재 P2/P4 일치나 제한 native ledger 통과를 continuum, 전체 finite-bin 보존,
REI production 또는 full EoR 승인으로 확대하지 않는다. Draft PR174는 merge하지 않는다.

## 최종 게시·백업 확인

2026-10-19 마감 시 Google Drive의 raw ZIP/Docs/Sheets 내용 쓰기가 응답하지 않았고 새 백업 readback은 미완료다. 생성된 빈 Doc/Sheet를 성공으로 세지 말고, 재조회로 원격 effect부터 확인하라. 상세 receipt는 delivery/DRIVE_FINAL_READBACK.json이다. Dropbox 세 단계는 provider hash와 remote manifest 범위에서 확인됐다.

상세 객체·hash·readback 범위는 [CLOUD_READBACK_KO.md](CLOUD_READBACK_KO.md)와
[PUBLICATION_CLOSEOUT.json](PUBLICATION_CLOSEOUT.json)을 따른다.
