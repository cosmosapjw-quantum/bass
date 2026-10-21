# NCP SSH 계약 수정 — 2026-10-21 KST

[NCP_ACCESS_CONTRACT.json](NCP_ACCESS_CONTRACT.json)과 두 전체 handoff를 사용자 지정 SSH로 갱신했다. 이번 수정은 문서·메타데이터만이며 SSH/compile/science/ODE/benchmark/NCP 실행0회다. 현재 접속 상태는 `SSH_AUTHORIZED_NOT_TESTED`, 실제 job은 `NOT_RUN`이다. Desktop Commander의 기존 quota 이력은 보존하며 SSH 승인과 구분한다.

기존 S12 최종 배송은 [댓글6303812301](https://github.com/cosmosapjw-quantum/bass/pull/174#issuecomment-6303812301)에서 **Dropbox8ZIP·4,450,082bytes·중복 포함930payload·946entries+final JSON 전체 readback PASS**로 확정됐다. 마지막 metadata ZIP은 `BASS_S12_C10_METADATA_20261021_57184994.zip`,252,521bytes,SHA256 `93a9b88d3afc4b95d6d31f2a137e012671143ce5d45735b508f623a5aa8f3646`,Dropbox `id:BSpOijBcT10AAAAAAD_aQQ`다. Final JSON은 `BASS_S12_FINAL_DELIVERY_20261021_57184994.json`,60,121bytes,SHA256 `6f78d553712649ddf4557249b7962986285b16e5d24a70829e74d1feb6e5bec9`,Dropbox `id:BSpOijBcT10AAAAAAD_agg`다.

이번 작은 계약 수정의 commit/ZIP/readback은 별도 PR174 amendment 댓글이 소유한다. 기존 S12 ZIP/JSON을 다시 만들지 않는다. **새 Drive는 계속 pending**이며 이번 SSH 지정은 Drive 쓰기/재시도 승인으로 확대하지 않는다. 아래7ZIP 표와 이전 상태는 metadata57184994에 포함됐던 봉인 전 snapshot 원문으로 보존한다.

---

# S12 현재 백업/readback 상태

현재까지 검증된 S12 Dropbox는 7ZIP·4,197,561bytes·중복 포함 payload907항목이다. 아래 각 ZIP은 전체 원격 bytes/SHA256/provider hash/CRC/manifest/Git blob 검증 PASS다.

| 단계 | 고정 ZIP | bytes | payload | SHA256 |
|---|---|---:|---:|---|
| stage1 | BASS_S12_C1_20261021_e48e0d56.zip | 52352 | 8 | `432a3aa206cbf6a803db47e23eeb928a4b6030f043363d97c920a713d9422bb1` |
| stage2 | BASS_S12_C2_C5_20261021_f4cd0d53.zip | 264364 | 63 | `14a1d01d0693cf81db16b8c3b816a160981b6e98cfe2a35a8cdfe067f9387536` |
| stage2_repair | BASS_S12_C6_REPAIR_20261021_4e3615dd.zip | 130367 | 35 | `9398776be5981feea8b907933bda2d930442a09cda63c1af87beada9e378b5d8` |
| stage3_inputs | BASS_S12_C7_INPUTS_20261021_094971e5.zip | 264552 | 97 | `3419bd00431f31455522a599306daa8f640774a5d1c35f2537098ff822b60d06` |
| stage3_support | BASS_S12_C7_SUPPORT_20261021_be773dbf.zip | 172381 | 44 | `1c8e7fa1d8470f5acab9d22952e89fa2bd44538dcdbb5be70d4e88ae2e8ea5fa` |
| stage4_c8_source | BASS_S12_C8_SOURCE_20261021_8247645d.zip | 432014 | 50 | `d97b57d760664e1214ce5556b7802982e0e10c80603b28b8839e7ddcdbc28d67` |
| stage5_results | BASS_S12_C6_C9_RESULTS_20261021_fd8a9aaf.zip | 2881531 | 610 | `7b88604747a28a1d9ae1ec800061bb0b6b8c64a91a3874ef78f16dc9fa482f54` |

각 provider ID와 원문 receipt는 [S12 cloud index](s12_birth_memory/delivery/CLOUD_CHECKPOINT_INDEX.json)에 있다. 최종 containing metadata HEAD/tree와 마지막 finite ZIP/JSON은 게시 뒤의 실제 readback 및 최종 PR174 배송 댓글이 소유한다. 이 파일 안에 자기 hash를 만들지 않는다.

**새 S11/S12 Google Drive 배송은 미완료다.** 이전 write는 응답·ID가 없고 서버 결과가 불확정이다. 이번 단계들의 추가 Drive write는0회이며 더 이상 재시도/우회를 하지 않는다. 새 객체가 독립적인 read-only 대조에서 보이면 full bytes로 확인하기 전까지 PASS로 올리지 않는다. 원 S10의 양쪽9ZIP·4,399,983bytes·payload383항목+최종 JSON 완료는 그대로 유지한다.

NCP의 첫 config 호출은 월 quota와 명시적 no-retry/reconnect를 반환했다. 실제 새 NCP process0회, current64/128 hardware 미관측이다. 배송/metadata 처리 중 과학/build/test/ODE/benchmark/NCP 재실행0회다. 아래는 이전 단계의 역사적 기록이며 현재 S12 판단은 위 index와 최신 최종 댓글을 따른다.

<!-- S12_CLOUD_CURRENT_END -->

# S11 신규 배송 — GitHub·Dropbox 보존, 새 Drive 복사 미완료

**S11 C1/C2–C5/C6–C9 세 ZIP은 Dropbox의 전체 원격 bytes·SHA256·provider hash·CRC·manifest/Git 검증을 완료했다. 새 Drive 복사는 확인되지 않아 이중 배송 완료를 선언하지 않는다.** 기존 S10의 원9ZIP·최종JSON 이중 배송은 이미 완료됐으며 이 새 장애 때문에 되돌리지 않는다.

| S11 단계 | 봉인 ZIP bytes | SHA256 | Dropbox ID | payload |
|---|---:|---|---|---:|
| C1 | 40,857 | `73653cbbd5e8b01b10f4e95513514bb8d8db6f5415a80724fa79d0e58185e028` | `id:BSpOijBcT10AAAAAAD_aBg` | 6 |
| C2–C5 | 157,012 | `978d030a8cf4f7db583ed74c14413566cfca93d1b886e5d5feb22a2857d118c8` | `id:BSpOijBcT10AAAAAAD_aBw` | 44 |
| C6–C9 | 2,581,659 | `399e036594bf809ad29f9450a2f4c2549522ab4228a60224fab571ccb2939099` | `id:BSpOijBcT10AAAAAAD_aCQ` | 121 |

합계2,779,528bytes·171payload entries이며 단계 사이 중복을 포함한다. 결과 ZIP의121은 게시된120Git파일과 별도 보존한 실행binary1개다. Binary를 source로 주장하지 않는다. [현재 index](delivery/s11/CLOUD_CHECKPOINT_INDEX.json), [C10 판정](delivery/s11/C10_DECISION.json), 단계별 [C1](delivery/s11/stage1/DROPBOX_FULL_READBACK.json)·[C2–C5](delivery/s11/stage2/DROPBOX_FULL_READBACK.json)·[C6–C9](delivery/s11/stage3/DROPBOX_FULL_READBACK.json) 원격 검증을 읽는다.

실행 source `7fb9b83cba01d37ce4cabbc4772527710601cd96`, 결과/검토 `85d5833b4486d14855b84a9d967f5819788d05e5`를 구별한다. 이 문서가 포함된 C10 metadata의 정확한HEAD/tree·마지막ZIP/JSON·postcommit readback은 [PR174 최신 배송 댓글](https://github.com/cosmosapjw-quantum/bass/pull/174)이 소유한다. 자기hash나 아직 수행하지 않은 최종 전송 성공을 선기록하지 않는다.

## 새 Drive 장애의 실제 범위

C1 `upload_file` 두 호출은 provider 응답/새ID/operationID 없이1604.0초·1197.8초 뒤 root가 중단했다. 별도 `copy_file` endpoint로 새 pending copy를 만드는 시도도344.6초 뒤 응답 없이 중단했다. 새copyID가 없었으므로 `update_file`은0회다. 원본S10파일을 수정하는 호출은 없었다. Tool의 `aborted by user` 원문은 **root assistant가 대기를 중단한 것**이며 사용자 취소로 해석하지 않는다.

18:23:53UTC의 read-only 검색에서 `/BASS_BACKUPS`의 C1 최종명과 `BASS_S11_C1_PENDING_CONTENT_20261020_e9f8eccc.zip`은 관측되지 않았다. 이것은 지연된 서버 작업의 사후 완료까지 배제하지 않으므로 재시도 전 exact-name/ID 대조가 필요하다. 반복 쓰기는 중단했다. Read-only Drive와 Dropbox 전송은 정상 응답했지만 새 Drive write의 구체적인 내부 원인은 확정하지 않았다. [업로드 중단](delivery/s11/UPLOAD_INTERRUPTION_RECEIPT.json), [별도copy 중단](delivery/s11/DRIVE_ALTERNATE_INTERRUPTED_COPY.json), [마지막 이름 대조](delivery/s11/DRIVE_ALTERNATE_NAME_LOOKUP.json).

과학·build/test·ODE·benchmark·NCP를 재실행해서 해결할 장애가 아니다. 배송에 필요한 ZIP·source/result/Git readback·manifest는 그대로 보존됐다. 연결 Browser plugin의 문서화된 초기 접속은 originating browser context가 필요하다는 응답으로 사용할 수 없었다. 페이지 조회·로그인·업로드는0회다. [브라우저 경계](delivery/s11/BROWSER_DELIVERY_BOUNDARY.json)에 실제 응답을 보존했다. Cloud Browser로 대체하려면 연결 서비스 도구의 반복 오류 후 fallback에 별도 사용자 승인을 요구하는 브라우저 도구 지침을 따라야 한다. 이 승인은 아직 요청하지 않았으며, 이미 허용된 GitHub·Dropbox 배송은 계속 마친다.

## 재사용한 원 S10 최종 배송

[2026-10-20 최종 댓글6289844952](https://github.com/cosmosapjw-quantum/bass/pull/174#issuecomment-6289844952)의 원8ZIP+복구보충1개는 양쪽 전체bytes/SHA256/CRC/manifest PASS,9ZIP·4,399,983bytes·중복포함383payload다. 최종JSON24,280bytes SHA256`98a88ff10828d9d6d0794237da87db76fb68875db38457c7fb18c04aedcfdb3c`의 양쪽 전체bytes도 초기read-only intake에서 다시 일치했다. [S11 intake](s11_p246/CLOUD_INTAKE.json)는 원ZIP전체재다운로드 대신 완료한과거CRC/manifest증거를 재사용했음을 명시한다.

---

## 아래는 S10 및 이전 시점의 보존된 역사적 기록

아래8ZIP/보충ZIP생성전/Drivepending 등의 표현은 각 문서 작성 시점이다. 현재 원S10완료와 새S11Drive미완료는 위 구분을 따른다.

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
