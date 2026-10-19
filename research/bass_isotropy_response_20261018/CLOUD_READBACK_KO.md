# Cloud readback — S8 완료, S9 source 백업 준비

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

## S9 source/preregistration

현재 S9 prereg SHA는 `7e615ea1820e95b6fb61d7a360d13bf0fb560b6f25883e17ed487e8a3505f507`이다. GitHub source 게시와 양쪽 cloud backup/readback은 이 문서 작성 시점에 pending이며, 실제 history8개도 NOTRUN이다. Source publication은 이 문서를 담은 commit을 게시 후 확인한다. 해당 실제 identity와 readback을 가진 `evidence_s9/SOURCE_PUBLICATION_GATE.json`을 만든 다음 고정 캠페인을 실행한다.

Intake의 공개 근거는 `evidence_s9/intake/PUBLIC_RELATED_INTAKE.json`(399337B, SHA `9bfb913a76b27949108b7e825053989f1c6f053872bb2bb256565ac2144e3c73`)이다. 확인한 관련 roots·결과 시점·공개에 필요한 과학적 source와 결과를 기록한다. 이 문서는 새 S9 source의 백업이 이미 끝났다는 뜻으로 사용하지 않는다.
