# S8 cloud readback

S8는 각 과학실행 전에 해당source/preregistration을 GitHub에게시하고두provider에백업했다. 아래세receipt의archiveidentity와scope를재사용한다.

| 단계 | archive bytes | SHA256 | Drive object |
|---|---:|---|---|
| Intake/theory | 62109 | 9e27c3cb170d61b70acf84674c2ff32a2ce9b08ee42f88c296dde6a773a83fec | 1zk2wSTt4VNOtOzeXTFgXtss2tHtWUY2U |
| Source/prereg | 123122 | ae0ccedaaccc25044f77fa28129b9b1cfc9dd699674aa4dc204c6454dabcae71 | 1VS_Z1G2VeWgtWLrmmS6yV1CPeZNXdrpw |
| Native results + tangent recovery prereg | 1435308 | de7b33947029ff5cd17fd38560a0665a6209e73e97ab0fa80dd7db949d00c0e4 | 1U82SIahJaMmJQnAe40GkdXw48mVIHYou |

GoogleDrive는독립connector로전체rawZIP을다시읽어원byte동일성/SHA256/CRC/각manifest/Gitblob을검증했다. Manifest수는10/35/39다. Dropbox는각원격파일의freshsize와provider전체content_hash를검증했다. DropboxrawZIPdownload완료주장은없다.

정확한증거는delivery/s8/S8_STAGE0_CLOUD_READBACK.json, S8_STAGE1_CLOUD_READBACK.json, S8_STAGE2_CLOUD_READBACK.json에있다. 과거S7백업은history/20261019_PRE_S8_FINAL_CLOUD_READBACK_KO.md 및delivery/s7에보존한다.

FinalS8결과/그림/handoffarchive는이문서의containingcommit게시후생성한다. 그post-uploadidentity/readback은PR174해당comment와다음S9checkpoint에넣는다. 이기록은과학계산을재실행하지않고backup의identity만판정한다. 최종archive는앞의세immutablearchive에이어지는incrementalsupplement다.
