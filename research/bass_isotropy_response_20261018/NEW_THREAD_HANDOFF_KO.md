# 새 ChatGPT 대화용 handoff — S10 결과 재사용과 남은 물리 연구

아래 단일 블록을 새 연구 대화에 복사한다. 고정 과학 source·실제 결과·독립 검토를 보존하며, 이 파일이 포함된 최종 metadata commit은 PR174 최종 배송 댓글과 Git ref/readback에서 확인한다.

```text
$physmath-research-loop를 사용해 BASS의 현재 완료 증거를 재사용하고 사용자가 선택한 다음 물리 연구만 이어라. 과거 대화·ZIP 다운로드·파일 첨부·사전 명령 실행을 사용자에게 요청하지 마라. 새 자동 최적화 주기를 열거나 완료한 실행을 반복하지 마라.

[고정 위치와 identity]
Repo: https://github.com/cosmosapjw-quantum/bass
Draft PR174: https://github.com/cosmosapjw-quantum/bass/pull/174
Branch: research/bass-isotropy-checkpoint-recovery-20261018
Lane: research/bass_isotropy_response_20261018/
S9 불변 실행 source: 4b30957cb008aad8019bb1a673937fc67bd017e8
S9 결과 게시: a40311796f9aac5ea5e0e58c630bee2a78443353
S10 불변 실행 source: d5a173644f5c7c0dbe9eb8757dfc4ccad6c4f4c8
S10 source tree: 95785be65c196c68d61b79dafb32f4cedfd7702d
Source/input manifest SHA256: 4ac631dced7e1d4fdc8ce63d076dfe15bb38bde7040029644e2c34f30b1ebc17
C6 검증 checkpoint: 477eca7d13bba4f69e063ad9b024225ee06cc395
C7/C8 결과 commit: 26e9e1ba8f39788d98ec33c60f6e9fd2605f8b8a
C7/C8 tree: 925f3cf75683b83c8b292cea4ce596059b36265d
C9 검토 commit: 0771f0610987eb9f900674e83063912150733255
C9 tree: 1c93fb37dce78cbd54691d072aaf35209a94894c
고정 VigilODE: a21d573980f66fe02891bd216153443b5352f921
고정 original REI spectral owner: 0e25846433170d0f420c4cda44a0bedbf02cd177
부모 PR173: 4e2d1fa820d6f7baae1069b615fb82a08d53403b
SourceID: MD14_Z002_FESC_BB50K_13P6_100_V1
최종 metadata HEAD: 이 파일이 포함된 HEAD는 PR174 최종 배송 댓글/Git ref 및 postcommit readback을 대조하라. 위 source/result/review 고정값과 혼동하지 마라.

[첫 행동과 읽을 파일]
현재 GitHub ref/commit/full tree 및 PR 최신 배송 댓글을 읽고 Dropbox /BASS_BACKUPS와 Drive /BASS_BACKUPS의 저장 결과를 read-only로 대조한다. Drive folder ID=1fFxb-qgExWbEomt3EbbOjGKcslFpGv3y. PR 요약 HEAD가 늦게 갱신된 원 관측은 보존하고 Git Data ref/commit/tree의 실제 검증을 따른다.
README_KO.md, DAG.json, RETURN_TO_CHATGPT.json, PUBLICATION_CLOSEOUT.json, CLOUD_READBACK_KO.md, S10_OPTIMIZATION_KO.md, S10_THEORY_KO.md, S10_RESULTS_KO.md를 읽는다.
고정 입력/실행 gate는 s10_optimization/SOURCE_MANIFEST.json, evidence_s10/c4/BENCHMARK_PROTOCOL.json, evidence_s10/run_20261020_r1/EXPERIMENT_POSTCHECK.json을 확인한다.
실제 검토는 evidence_s10/c9_review_r1/C9_REVIEW_RECEIPT.json, C9_REVIEW_KO.md, INDEPENDENT_RECOMPUTATION.json, C9_CLOSEOUT.json을 읽는다. C9 receipt SHA256=1b63d46ebe2b576acacd828b77ac5fdf85e3461de84991305f708b2ea5513c29.
S9_RESULTS_KO.md 및 evidence_s9/run_20261020_r1/CAMPAIGN_RETURN.json, evidence_s9/resume_20261020/science_review/DUAL_REVIEW_RECEIPT.json도 연결해 S9 완료 근거를 재사용한다. S6–S8는 기존 결과/실패 receipt를 재사용한다.

[실제 완료 범위]
S9 고정8 history가 8/8완료·140 gate assertion PASS다. 140은 독립 실험 수가 아니다. 이 S9 matrix의 NCP 재실행 의무는 없다.
S10은 원 문제·gate·birth/P24·stock·owner·solver를 유지한 isolated opt-in crate다. stream/prepared/exact-cache/SIMD/독립 history 병렬화를 비교했다. 원 S9/VigilODE 기본 경로를 교체하지 않았다.
C6 targeted11/11, kernel strict proof108/108, 네 입력×여섯 mode의 대표RAW24/24 scientific bytes 동일, serial/parallel digest 동일, science68/68을 통과했다. Benchmark history496회는 기존 네 입력의 성능 반복이며 새 물리 사례496개가 아니다.
C9 단일 독립 pass는155/155 checks와 science68/68 PASS_SCOPED다. 문서 표현 finding1건을 같은 pass에서 닫았다. 준비 데이터는 immutable mu²와 weight이고 1-z는 평가 중 계산한다. code/tolerance 변경·ODE/benchmark 재실행은 없었다. 별도 host/compiler 재현은 아니다.
MF simd_cache의 paired median 가속비는 closed2.973배, FLRW4.115배다. closed small/clock4는1.055배, Q1–Q3=0.957–1.243으로 일관된 이득을 승인하지 않는다. changing-state n16/cohort2 simd_cache0.949817은 성능 회귀로 보존한다.
별도 allocation binary에서 최적화 다섯 mode의 평가 구간은 allocation/reallocation0회·0bytes였다. setup/caller clone/whole-history 전체 할당 또는 peak RAM이0이라는 뜻은 아니다. IQR은 신뢰구간이 아니며 다른 CPU/입력으로 portable speedup을 주장하지 않는다.
현재 완료 증거를 확인하기 위한 build/test/history/timing 재연은 필요 없다. 현재 범위의 NCP 실행 의무도 없다.

[보존할 입력·물리 gate]
Non-tilted axisymmetric Bianchi I, (-,+,+,+), a_perp=a exp(-b), a_parallel=a exp(2b), s=dot b, Sigma=sqrt(3)|s|/H를 유지한다.
새 명시적 등방 birth angular quadrature만 보정한다. 기존 광자장·physical anisotropic stock·birth weights를 초기화하거나 재가중하지 않는다. 양의 weights, reflection parity, source frame, 고정 spectral owner와 balance owner를 유지한다.
원 gate: exact normalization/P2/P4=3/10^15, fine reference absolute1e-9, Hamiltonian/cohort energy relative1e-11, event energy1e-13, donor endpoint3e-14, clock absolute1e-12. Feasibility/precision 실패를 음수 weight나 gate 완화로 우회하지 않는다.
P2/P4 일치만으로 continuum 또는 full native finite-bin 보존을 승인하지 않는다. 새 문제의 input/gate는 필요한 과학적 의존성을 먼저 정의한 뒤 별도 사전등록한다.

[배송 상태와 제한]
오늘 S9 결과와 S10 C1/R2·C2/C3·C5/C6/C7·C8의 Dropbox 전체 ZIP bytes·SHA256·CRC·manifest 검증은 완료됐다. C9를 포함한 최종 provider 상태와 object ID는 PUBLICATION_CLOSEOUT.json, CLOUD_READBACK_KO.md가 연결하는 최종 delivery index 및 각 단계 CLOUD_READBACK.json을 우선한다. 이 인계는 최종 C10 자기 commit 또는 미확인 cloud ID를 만들어 넣지 않는다.
새 Drive 내용 쓰기는 provider 무응답으로 blocked다. 2026-10-20 06:22 UTC metadata listing의 직접 항목48개에서 당시 관련 archive6개와 staging copy1개의 exact 이름 일치는0개였다. 이 관측을 계정 전체 검색/전체 파일 부재의 증명으로 확대하지 않는다. 과거 source/prereg 및 S6–S8의 Drive 검증 성공은 별도 역사적 사실이다.
무응답이 확인된 같은 upload/copy 경로를 반복하지 않는다. 현재는 검증된 대체 쓰기 경로가 없어 mutation을 중단한 상태다. 브라우저 fallback은 브라우저 도구 지침에 따른 명시적 사용자 승인 후에만 진행한다. 실패 receipt와 빈 Docs/Sheets를 완료 백업으로 세지 않는다. Dropbox 완료와 Drive 미완료를 분리하며 이중백업 완료를 주장하지 않는다.

[진짜 남은 연구와 재개 원칙]
새 자동 최적화 cycle을 열지 말고, 사용자가 선택한 후속 물리 의무를 최소 계산 가능한 계약으로 구체화한다:
1) 실제 MD14 source의 시간/physical·comoving volume/방출·흡수/에너지 공급·응력 정규화와 native Einstein/shear feedback의 동일 Q 연결.
2) 아직 구현하지 않은 P6 제약 알고리즘.
3) evolving reactive absorption/chemistry와 full finite-bin spectral-history photon/energy 보존·수렴.
4) S8 b0=.9,n64,P24 STRICT_INTERIOR의 INNER_P2_PRECISION_LIMIT 원 실패.
5) 더 넓은 finite-d continuum/angular accuracy와 고차 moment 범위.
6) 새 Rust client의 full birth-memory parameter tangent.
S6의5.369926725506957e-12 source-deposition 잔차 설명과 기존 rank1/finite-d/cohort 증거는 재사용하되 full spectral history 완료로 확대하지 않는다. S6 rate38/344 실패·P4악화44/238, S7 원 실패, S8 낮은 해상도8미달·precision1실패를 보존한다.
가능한 유도·코드·경량 gate는 여기서 완성한다. 새 NCP 작업이 실제로 필요할 때만 source·입력·gate·게시/backup 상태를 먼저 준비해 compile/작은 호환 수정/등록 실행만 남긴다.
기존 owner 작업과 사용자 변경을 보존한다. 추가workers≤16, RAM≤16GiB, disk≤4GiB, 개별job≤1800초. 현재 관측 환경은8CPU/8GiB이며 build2, 독립history 권장2workers다. 새 환경의 실제 자원은 별도로 확인한다.
실행·게시·provider별 backup/readback·DAG 상태를 구분해 기록하고 실제 결과·실패 종류·남은 의무·source/result/review/PR·두 handoff를 반환한다. REI production/full EoR/merge로 확대하지 않는다.
```
