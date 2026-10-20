# Codex / NCP handoff — S9 재실행 없이 다음 native bridge 준비

이 인계는 local/Codex/NCP에서 다음 구현·실행 단위를 준비하기 위한 것이다. 새 ChatGPT 연구 대화는 [NEW_THREAD_HANDOFF_KO.md](NEW_THREAD_HANDOFF_KO.md)를 사용한다.

## source와 완료 상태

```text
Repository: https://github.com/cosmosapjw-quantum/bass
Draft PR174: https://github.com/cosmosapjw-quantum/bass/pull/174
Branch: research/bass-isotropy-checkpoint-recovery-20261018
Lane: research/bass_isotropy_response_20261018/
S9 실행 source: 4b30957cb008aad8019bb1a673937fc67bd017e8
S9 source tree: 8e4abf3820d06bae6cbec307e4f69de74195d14b
S9 prereg SHA256: 7e615ea1820e95b6fb61d7a360d13bf0fb560b6f25883e17ed487e8a3505f507
VigilODE 구현: a21d573980f66fe02891bd216153443b5352f921
REI spectral owner: 0e25846433170d0f420c4cda44a0bedbf02cd177
SourceID: MD14_Z002_FESC_BB50K_13P6_100_V1
부모 PR173: 4e2d1fa820d6f7baae1069b615fb82a08d53403b
현재 S9 결과 publication: a40311796f9aac5ea5e0e58c630bee2a78443353; 원격 tree/blob readback 완료
현재 결과 ZIP의 Drive·Dropbox readback: PENDING — 최종 배송 영수증에서 실제 완료 상태 확인
```

S9는 2026-10-20 현재 Rust 1.94.1로 새 locked build를 성공한 뒤 고정 8개 history를 한 번 실행해 8/8 완료, 140개 gate assertion PASS를 얻었다. 독립 이론·수치/구현·기록 검토는 각각 PASS_SCOPED다. 140은 독립 테스트 수가 아니다. **이 S9 matrix의 NCP 재실행 의무는 없다.** 과거 NOT_RUN과 verified_prior_build는 역사 기록이다. [Dual receipt](evidence_s9/resume_20261020/science_review/DUAL_REVIEW_RECEIPT.json)와 [독립 검토 보고](evidence_s9/resume_20261020/science_review/INDEPENDENT_S9_ACTUAL_REVIEW_KO.md)를 직접 확인한다.

현재 build receipt는 `evidence_s9/resume_20261020/runtime/PREPARATION_RETURN.json`이며 mode=fresh_build, new_compilation_performed=true다. 새 binary SHA256은 `69de3e8739488524cdbe53f9e4bd71f8125717138bf06085b5f51a082060582f`다. 실제 결과는 `evidence_s9/run_20261020_r1/CAMPAIGN_RETURN.json`, 각 case의 `RAW.json`/`PROCESS.json`/`ASSESSMENT.json`, `evidence_s9/RESULT_SUMMARY_20261020.json`, `S9_RESULTS_KO.md`에 있다. Resource 측정 범위는 `evidence_s9/resume_20261020/CURRENT_EXECUTION_RESOURCE_CLARIFICATION.json`을 읽는다. 관측된 /proc RSS를 전체 compiler peak로 해석하지 않는다.

## 실행자가 먼저 할 일

현재 branch/PR 최신 댓글과 두 BASS_BACKUPS의 새 결과를 확인해 위 source와 실제 raw receipt를 대조한다. 사용자의 과거 대화·첨부·ZIP 다운로드·사전 명령을 요구하지 않는다. `README_KO.md`, `DAG.json`, `RETURN_TO_CHATGPT.json`, `PUBLICATION_CLOSEOUT.json`, `CLOUD_READBACK_KO.md`, `S9_RESULTS_KO.md`, [현재 cloud intake](evidence_s9/resume_20261020/CURRENT_CLOUD_INTAKE.json) 및 실제 독립 검토 receipt를 읽는다. 새 실행환경의 compiler·Python·자원은 현재 실행으로 확인하고 과거 runtime 실패를 현재 blocker로 승계하지 않는다.

S6–S8 완료 evidence와 실패를 재사용한다. S6 rate 38/344 FAIL·P4 제약 44/238 악화, S7 support/exact-moment 실패, S8 native 18 attempt/17 measured/낮은 해상도 8 FAIL/STRICT_INTERIOR precision 1 FAIL을 지우지 않는다. S8 tangent 10/10 gate PASS와 n256의 6 target PASS도 각각의 범위로 보존한다. r0/r1 observation과 step count가 같았던 S9 plateau에서 수렴차수·portable speedup을 추정하지 않는다.

## 다음 개발 단위

다음 대상은 실제 MD14 공급부의 source time·stress·energy bridge와 native Einstein/shear feedback이다. 고정 REI owner의 실제 반환을 읽어 physical/comoving volume, 시간 변수, 방출·흡수·에너지 공급 소유권과 응력 정규화의 대응을 먼저 완성한다. 새 bridge가 기존 immutable birth cohort와 결합할 입력·출력 계약, 계산식, negative control, 보존식 gate를 구현한다. 기존 S9 manufactured donor의 성공을 실제 astrophysical source coupling의 완료로 바꾸지 않는다.

새 NCP 캠페인이 필요한 경우 ChatGPT/샌드박스에서 가능한 코드·입력·사전 gate를 먼저 완성한다. 새 source와 prereg를 게시하고 원격 hash 및 이중백업/readback을 확보한 뒤 NCP에는 현재 자원 확인, locked compile, 작고 구체적인 호환 수정, 등록된 실제 native 실행만 맡긴다. 새 campaign 명령은 그 실행 계약이 완성된 뒤 해당 새 단위에 기록한다. [S9 HOWTO](s9_vigilode/HOWTO_KO.md)의 과거8개 명령은 명시적 재현 연구를 위한 기록이며 다음 작업 지시가 아니다.

P6 제약 알고리즘은 아직 구현하지 않았다. Full reactive transport/absorption/history spectral 수렴, native finite-bin photon/energy 보존, continuum angular accuracy의 추가 범위, 새 client의 full parameter tangent는 미완료다. 새 변경에 의존하는 검사만 실행하고 source가 같은 S8·S9 또는 AD/adapter/runner 개발 검증을 관성적으로 반복하지 않는다.

## 고정 물리·실행 계약

Non-tilted axisymmetric Bianchi I; (-,+,+,+); a_perp=a exp(-b); a_parallel=a exp(2b); s=dot b; Sigma=sqrt(3)|s|/H. 새 등방 birth angular quadrature만 보정하며 기존 photon stock·physical anisotropic source·birth weights를 초기화하거나 재가중하지 않는다. 양의 weights, reflection parity, source frame, 고정 spectral owner와 원 balance owner를 유지한다. 지지 feasibility와 numerical precision을 구분하고 음수 weights·허용오차 완화·oracle birth b로 실패를 우회하지 않는다.

기존 owner 작업·사용자 변경·실행 중 job을 보존한다. 추가 worker≤16, RAM≤16GiB, disk≤4GiB, 개별 job≤1800초; 기본 새 build2/campaign1을 유지한다. 결과 경로를 덮어쓰지 않고 raw와 원 failure를 보존한다. 이론/수치/구현/환경/권한/입력 의존성 실패를 구분하며 timeout·잘린 raw·observer 실패도 실제 과정과 함께 반환한다.

각 완료 단위에서 실행·게시·백업/readback·DAG 상태를 따로 기록한다. 최종 반환에는 실제 명령·exit code·source/tree/binary/input hash·gate·자원 측정 범위·실패 유형·미실행 의무·GitHub PR/commit·cloud readback을 포함한다. REI production/full EoR/merge는 별도의 충분한 검증과 사용자 범위에 따라 다룬다.
