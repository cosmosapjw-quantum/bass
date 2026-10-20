# Cloud readback — S9 source 재확인과 실제 결과 배송

## 2026-10-20 현재 intake와 실행 전 gate

사용자가 제공한 `3694d6e1` 이후에 S6·S7·S8 결과와 S9 source/preregistration의 게시·이중 백업이 이미 있었다. 현재 GitHub PR174의 source HEAD `4b30957cb008aad8019bb1a673937fc67bd017e8`, tree `8e4abf3820d06bae6cbec307e4f69de74195d14b`와 마지막 [S9 prereg 배송 댓글](https://github.com/cosmosapjw-quantum/bass/pull/174#issuecomment-6269099795)을 실제로 읽어 두 클라우드의 최신 결과와 대조했다.

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
