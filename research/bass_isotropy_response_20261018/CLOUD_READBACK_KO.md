# S9/S10 원8개 archive — Google Drive 배송 복구 완료

**Google Drive 플러그인의 승인된 재시도로 원8ZIP의 이중 백업과 전체 원격 readback을 완료했다.** Dropbox에서 복구한 봉인 원본과 Drive에서 받은 전체 bytes가 일치했다. SHA256·ZIP CRC·manifest의 크기/해시/Git blob과 각 archive의 원 publication commit/tree를 확인했다.

총8ZIP, 4,189,549 bytes, 317개 manifest payload 항목이며 317에는 checkpoint 사이 중복이 포함된다.

| 단계 | ZIP | Drive object | Dropbox object | payload |
|---|---|---|---|---:|
| S9 | `BASS_S9_ACTUAL_RESULTS_20261020_a4031179.zip` | [1vAUNZCHQkNfbROH6AZU4nH1Cw80bR2Z1](https://drive.google.com/file/d/1vAUNZCHQkNfbROH6AZU4nH1Cw80bR2Z1/view) | `id:BSpOijBcT10AAAAAAD_SMg` | 123 |
| C1 | `BASS_S10_C1_20261020_62d6bc14.zip` | [1RRUiR453swSQ5xCHGNomGHR6K_mhRSSh](https://drive.google.com/file/d/1RRUiR453swSQ5xCHGNomGHR6K_mhRSSh/view) | `id:BSpOijBcT10AAAAAAD_SNA` | 11 |
| R2_C2 | `BASS_S10_R2_C2_20261020_8138a014.zip` | [1PcWfhIIoMXlzAUCdutJIATWNMz1INqVb](https://drive.google.com/file/d/1PcWfhIIoMXlzAUCdutJIATWNMz1INqVb/view) | `id:BSpOijBcT10AAAAAAD_SNg` | 35 |
| C3_C5 | `BASS_S10_C3_C5_20261020_d5a17364.zip` | [1NKH1ilaob3gRYWOoOyvjUGsyYLK0JONf](https://drive.google.com/file/d/1NKH1ilaob3gRYWOoOyvjUGsyYLK0JONf/view) | `id:BSpOijBcT10AAAAAAD_SOA` | 30 |
| C6 | `BASS_S10_C6_20261020_477eca7d.zip` | [16yszEKMWu6y7VpTVbbG-3RcePGuOd6kF](https://drive.google.com/file/d/16yszEKMWu6y7VpTVbbG-3RcePGuOd6kF/view) | `id:BSpOijBcT10AAAAAAD_SPQ` | 15 |
| C7_C8 | `BASS_S10_C7_C8_20261020_26e9e1ba.zip` | [1JE-BXoppOnQlsfSri82sD2V8sLcmuvXZ](https://drive.google.com/file/d/1JE-BXoppOnQlsfSri82sD2V8sLcmuvXZ/view) | `id:BSpOijBcT10AAAAAAD_SQw` | 70 |
| C9 | `BASS_S10_C9_20261020_0771f061.zip` | [1ouKuQECPz1JnnxzjMi303nbO_r582Uvg](https://drive.google.com/file/d/1ouKuQECPz1JnnxzjMi303nbO_r582Uvg/view) | `id:BSpOijBcT10AAAAAAD_SRQ` | 16 |
| C10 | `BASS_S10_C10_20261020_a8560530.zip` | [1-9tol8BUxdd-6CD3NUQVY6mBzOjAgHL2](https://drive.google.com/file/d/1-9tol8BUxdd-6CD3NUQVY6mBzOjAgHL2/view) | `id:BSpOijBcT10AAAAAAD_SRg` | 17 |

원본 SHA256·bytes·publication identity와 provider별 receipt는 [통합 index](delivery/s10/CLOUD_CHECKPOINT_INDEX.json)를 읽는다. [Drive 독립 전체 readback](delivery/s10/drive_recovery_20261020/EIGHT_ARCHIVE_DRIVE_READBACK.json)과 [Dropbox 실제 복구 readback](delivery/s10/dropbox_restore_20261020/EIGHT_ARCHIVE_RESTORE_READBACK.json)을 구분해 보존했다.

## 복구 범위와 역사적 실패

과거 connector 무응답은 당시 receipt 그대로 보존한다. 사용자의 명시적 브라우저 승인 뒤에도 보안 로그인 요청과 브라우저 runtime 상태 조회는 시간 초과로 끝났고, 브라우저 인증 성공이나 업로드는 관측하지 않았다. 이후 사용자가 Google Drive 플러그인 재시도를 명시했고 이번 업로드·원격 검증이 성공했다. 현재 원8ZIP의 Drive blocker는 해소됐다. 빈 Doc/Sheet나 실패 receipt를 백업으로 세지 않았다.

과학 source `d5a173644f5c7c0dbe9eb8757dfc4ccad6c4f4c8`, original REI owner `0e25846433170d0f420c4cda44a0bedbf02cd177`, 원 C10 판정 metadata `a85605302bb0317022eb06b498eb05b9d621de6a`를 보존했다. 이번 복구의 build/test/ODE/benchmark 재실행은0회다. 다음 물리 연구는 pending이며 REI production/full EoR/merge는 승인하지 않는다.

이 문서가 포함된 복구 metadata 자체의 commit/tree와 별도 postcommit 보충 ZIP/마지막 readback은 최신 PR174 배송 댓글이 소유한다. 원8ZIP의 완료를 아직 만들지 않은 보충 ZIP의 성공으로 확대하지 않는다.

---

## 아래는 원 C10 metadata 시점의 역사적 cloud 기록

다음의 blocked/pending/승인대기 표현은 당시 관측이다. 현재 상태는 위의 실제 성공 receipt를 따른다.

# Cloud readback — S9/S10 현재 배송 상태

## 2026-10-20 C10 마감 시점

**아래7개 이전 단계 archive는 Dropbox 전체 원격 bytes·SHA256·CRC·payload manifest/Git blob readback을 완료했다. Drive 새 복사는 미완료다.** [기계 판독 index](delivery/s10/CLOUD_CHECKPOINT_INDEX.json)는 stage별 commit/tree·객체·원 receipt를 연결한다. 원격 임시 download URL은 공개하지 않는다.

| 단계 | Commit | ZIP bytes | SHA256 | Dropbox ID | payload수 |
|---|---|---:|---|---|---:|
| S9_ACTUAL | `a4031179` | 1,724,949 | `1d7993575b796f6d5bf2d78e7775d11a7a22bb7c3457e8aec1c2f0304241aea3` | `id:BSpOijBcT10AAAAAAD_SMg` | 123 |
| S10_C1 | `62d6bc14` | 108,190 | `e95e2492e9d58aef410518e04224a0e8b12b1218c31d30e0c16635e5e4fb4a15` | `id:BSpOijBcT10AAAAAAD_SNA` | 11 |
| S10_R2_C2 | `8138a014` | 428,337 | `743601cd092cc1bbb01756e79c53f7a8476e8f3fd143ca6b9baeb75e9e9aff15` | `id:BSpOijBcT10AAAAAAD_SNg` | 35 |
| S10_C3_C5 | `d5a17364` | 130,693 | `bbbf95c63d88d24b7b7478faa7344e43d3787de16a307382a7cebf9f40618f9e` | `id:BSpOijBcT10AAAAAAD_SOA` | 30 |
| S10_C6 | `477eca7d` | 60,506 | `1cd0453971fdc94206d6589e727cac0a1df4a77bc67291fffb7e8104b9108711` | `id:BSpOijBcT10AAAAAAD_SPQ` | 15 |
| S10_C7_C8 | `26e9e1ba` | 1,460,006 | `ec8cef6194abfe93c0309129bd546e1bc14389859796599720ef77ea35979219` | `id:BSpOijBcT10AAAAAAD_SQw` | 70 |
| S10_C9 | `0771f061` | 146,597 | `0cce35c86caad58ca0270ffa232978bc8a8d66bf9720c48fad66d92e72c1cd2b` | `id:BSpOijBcT10AAAAAAD_SRQ` | 16 |

Payload 합계는300개이며 여러 checkpoint의 중복파일을 포함한다. 고유 과학 결과300개라는 의미가 아니다. 현재 최종 C10 metadata ZIP은 containing commit을 만든 뒤 포장하므로 자기 hash를 이 표에 미리 넣지 않는다. **그 마지막8번째 archive의 실제 commit/tree/hash/Dropbox readback은 PR174 최종 배송 댓글과 postcommit receipt를 읽는다.** 이전7개와 마지막1개를 함께 복구하면 이번 세션의 전체 배송 묶음이다.

Drive `/BASS_BACKUPS` folder `1fFxb-qgExWbEomt3EbbOjGKcslFpGv3y`에 대한 초기 업로드와 한 번의 diagnostic retry는 provider response/operation ID 없이 무응답이었다. 별도 staging-copy 진단도 무응답으로 controller가 중단했다. 응답의 “aborted by user”는 root controller가 대기를 중단한 상황이며 실제 사용자 취소 지시나 provider가 반환한 오류라고 해석하지 않는다. files.update의 content 쓰기는 시도하지 않았다. 기존 backup은 수정·삭제하지 않았다.

마지막 [읽기 전용 대조](delivery/s10/FINAL_DRIVE_READONLY_RECONCILIATION.json)는06:22:12.355UTC에 직접항목48개, 그 시점의 관련7파일명 일치0개를 확인했다. 해당7개는 S9actual와 S10C1/R2C2/C3C5/C6/C7C8, 당시staging 이름이며 이후 C9/C10 쓰기는 애초 시도하지 않았다. 따라서 지연생성 object를 성공으로 재사용할 증거도 없었다. 반복 mutation은 중단했고 브라우저는 사용하지 않았다.

Browser fallback은 연결 서비스의 반복 오류 후 사용자 승인을 요구하는 브라우저 도구 지침 때문에 별도 승인이 필요하다. 승인되면 이미 봉인한 ZIP bytes를 그대로 Drive에 올리고 원격 전체 bytes/SHA256/CRC/manifest를 확인하는 배송 복구만 수행한다. 새과학실행·사용자ZIP다운로드·파일첨부·사전명령을 요구하지 않는다. 과거의 완성된 두provider백업·복구와 빈Doc/Sheet·실패영수증은 각각 원래 범위를 유지한다.

## 역사적 intake와 이전 단계 검증

아래는 S9 실행 전에 완료한 storage 대조 및 그 이전 scope의 증거다. 아래 시점 표현과 예전 pending 상태를 위의 새 결과 배송 상태로 혼동하지 않는다.

# Cloud readback — S9 source 재확인과 실제 결과 배송

## 2026-10-20 현재 intake와 실행 전 gate

사용자가 제공한 `3694d6e1` 이후에 S6·S7·S8 결과와 S9 source/preregistration의 게시·이중 백업이 이미 있었다. S9 실행 전 intake에서 확인한 GitHub PR174 source HEAD `4b30957cb008aad8019bb1a673937fc67bd017e8`, tree `8e4abf3820d06bae6cbec307e4f69de74195d14b`와 마지막 [S9 prereg 배송 댓글](https://github.com/cosmosapjw-quantum/bass/pull/174#issuecomment-6269099795)을 실제로 읽어 두 클라우드의 최신 결과와 대조했다.

Google Drive `/BASS_BACKUPS` 직접 항목 48개와 Dropbox `/BASS_BACKUPS` 33개를 조사했다. Drive는 top_k1000 요청에서 후속 pagination을 노출하지 않았고 Dropbox는 has_more=false였다. 이 확인 범위에서 최신 S9 객체는 미실행 source/preregistration ZIP이었으므로, 이미 끝난 S6–S8을 재실행하지 않고 그 고정 S9 여덟 이력만 실행했다.

현재 intake에서 Drive의 S6·S7 final·S8 final·S9 prereg 네 ZIP 전체 bytes를 받아 원 SHA256/CRC와 manifest 86/22/43/140개 항목을 확인했다. Git blob identity가 있는 항목은 각각 86/21/42/139개다. Dropbox는 네 객체의 fresh provider content_hash와 size를 Drive의 검증된 bytes로 계산한 값과 대조했고, S9의 remote extracted manifest 140개도 일치했다. 이 과거 객체들의 Dropbox 독립 raw ZIP 다운로드를 수행한 것으로 표시하지 않는다.

| S9 실행 전에 재확인한 항목 | 실제 identity |
|---|---|
| Archive | `BASS_S9_PREREG_VIGILODE_RUST_20261019_4b30957c.zip` |
| Bytes / SHA256 | 604752 / `adaa646269168365738bb6c6e7ec67538da0b6109b5d9cb8cac5e4a886a2d9c1` |
| Drive | `1zZsKKoAmR3as89JIVMWjpTlbQWRN15LL` |
| Dropbox | `id:BSpOijBcT10AAAAAAD_Q5g` |
| Dropbox provider hash | `03ee5cdc7f80cf43e9075f8512b25762e23b486f6fecf1109ec9fcf79fbb5010` |
| Preregistration SHA256 | `7e615ea1820e95b6fb61d7a360d13bf0fb560b6f25883e17ed487e8a3505f507` |
| Current source gate SHA256 | `3682dce97d7f89dd4e178a4bae16a6d7e328db197bae31ec2fdca78134df4717` |

공개 근거는 [현재 intake](evidence_s9/resume_20261020/CURRENT_CLOUD_INTAKE.json), [manifest 검증](evidence_s9/resume_20261020/manifest_verification.json), [provider readback](evidence_s9/resume_20261020/cloud_readback_validation.json), [실행 전 source gate](evidence_s9/SOURCE_PUBLICATION_GATE.json)에 있다. 현재 Git tree에 일치하는 cloud payload만 재사용했고, 오래된 metadata 19개는 현재 파일을 덮어쓰는 데 쓰지 않았다.

## S9 실제 결과의 후속 배송

고정 여덟 이력은 현재 샌드박스에서 실제 완료됐고 원 gate assertion 140개가 통과했다. [결과 보고서](S9_RESULTS_KO.md)와 원자료·독립 검토·최종 그림을 함께 게시한다. 이 문서의 최초 결과 commit 시점에는 해당 결과의 post-commit ZIP 업로드/readback이 아직 진행 중이며, 성공을 선기록하지 않는다. 확인한 commit/tree와 실제 cloud 객체/hash를 후속 마감 문서와 PR174 배송 댓글에 기록한다. 과거 content-write 실패와 빈 Docs/Sheets는 성공한 ZIP 백업으로 바꾸어 세지 않는다.

## S8의 기존 배송 근거

S8는 각 과학 실행 전에 source/preregistration을 게시하고 양쪽 provider에서 확인했다. 최종 결과·그림·handoff의 게시와 마지막 백업도 완료했다.

| 단계 | archive bytes | SHA256 | Drive object |
|---|---:|---|---|
| S8 intake/theory | 62109 | 9e27c3cb170d61b70acf84674c2ff32a2ce9b08ee42f88c296dde6a773a83fec | 1zk2wSTt4VNOtOzeXTFgXtss2tHtWUY2U |
| S8 source/prereg | 123122 | ae0ccedaaccc25044f77fa28129b9b1cfc9dd699674aa4dc204c6454dabcae71 | 1VS_Z1G2VeWgtWLrmmS6yV1CPeZNXdrpw |
| S8 native results + tangent recovery prereg | 1435308 | de7b33947029ff5cd17fd38560a0665a6209e73e97ab0fa80dd7db949d00c0e4 | 1U82SIahJaMmJQnAe40GkdXw48mVIHYou |
| S8 final results/figures/handoff | 916060 | cf4cc9b03b243afb6f055469e57193def5db01fc2610b14c537bd8968ffc3efc | 1z8ovrEJWOLJla5rbRCOvCYmh2AKcld3e |

최종 source/publication commit은 `276172ca6cac9cf6b38561fdf9ba0103e1beb9cf`, tree는 `b021e10a8d4776fdcbede3c03885e08995dd6d48`이다. [PR comment6268573867](https://github.com/cosmosapjw-quantum/bass/pull/174#issuecomment-6268573867)의 본문도 readback했다. Dropbox 최종 object는 `id:BSpOijBcT10AAAAAAD_Q3w`, provider content_hash는 `961c9d99769d03afb6881423018c1971f300a73145cc0c4bb7c95ee9565cd6fc`다.

Google Drive는 독립 connector로 전체 raw ZIP을 읽어 byte 동일성/SHA256/CRC/manifest/Git blob을 검증했다. Manifest는 차례대로10/35/39/43개다. Dropbox는 fresh object의 전체 provider content_hash와 size를 검증했다. Dropbox raw ZIP 다운로드와 구분된 증거다.

고정 근거는 `delivery/s8/S8_STAGE0_CLOUD_READBACK.json`부터 `S8_STAGE3_CLOUD_READBACK.json`, `S8_STAGE3_GIT_READBACK.json`, `S8_FINAL_PR_READBACK.json`이다. 최종 post-upload receipt를 이번 S9 source checkpoint에도 포함하여 이전 archive 밖의 마감 근거를 보존한다.

## S9 source/preregistration의 역사적 준비 기록

원 S9 prereg SHA는 `7e615ea1820e95b6fb61d7a360d13bf0fb560b6f25883e17ed487e8a3505f507`다. 2026-10-19 source 문서의 pending/NOTRUN 표현은 당시 준비 상태이며, source `4b30957c`의 후속 게시·이중 백업과 이번 실제 실행은 위의 새 receipt가 소유한다.

Intake의 공개 근거는 `evidence_s9/intake/PUBLIC_RELATED_INTAKE.json`(399337B, SHA `9bfb913a76b27949108b7e825053989f1c6f053872bb2bb256565ac2144e3c73`)이다. 확인한 관련 roots·결과 시점·공개에 필요한 과학적 source와 결과를 기록한다. 이 문서는 새 S9 source의 백업이 이미 끝났다는 뜻으로 사용하지 않는다.
