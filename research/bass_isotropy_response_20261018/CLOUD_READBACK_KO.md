# S7 cloud readback — 2026-10-19

연구 전 새 S6 source/결과를 양쪽 `/BASS_BACKUPS`와 GitHub HEAD/PR 댓글에서 먼저 확인했다. S6 science04a3a851, closeouta9704c6f를 재사용했고 캠페인을 반복하지 않았다. 이번 Drive S6 raw ZIP927047bytes/SHA256/CRC/manifest86/86 및 Gitblob을 검증했다. Dropbox는 freshmetadata와 기존 커밋의 이전 rawreadback receipt를 대조했다. 근거: [intake](delivery/s6_intake_20261019/INTAKE.json), [원S6receipt](delivery/S6_CLOUD_READBACK.json).

## 이번 S7의 서로 다른 readback 범위

**Google Drive:** 각 archive를 업로드한 뒤 별도 connector로 raw bytes를 다시 받아 로컬 ZIP과 전체 byte동일성, SHA256, ZIPCRC, manifest의 모든 size/SHA256/Gitblob을 검증했다. Parentfolder는 `1fFxb-qgExWbEomt3EbbOjGKcslFpGv3y`다. 업로드는 사용자가 승인한 Browser 전환으로 수행했다.

**Dropbox:** 각 새 object의 metadata, 전체 object에 대한 Dropbox content hash와 size가 로컬 archive와 일치했다. Stage1의 single-use URL rawGET은 URLError(no HTTPstatus)로 완료되지 않았다. 이후 단계는 같은 경로를 반복하지 않고 fresh providerhash로 확인했다. 이번에 Dropbox raw ZIP을 내려받아 검증했다고 주장하지 않는다. 이전 S6의 rawreadback receipt와도 구별한다.

| S7 단계 | Source commit | ZIP bytes | Drive manifest | Drive ID | Dropbox ID |
|---|---|---:|---:|---|---|
| 1 | `2865f60bf0a247eaab4997c222ad82ae22a4c8fa` | 172,803 | 51/51 | `1eSm2DdXvmXx9osM6sIT2weU03Cz_kwHC` | `id:BSpOijBcT10AAAAAAD_Quw` |
| 2 | `c689dcf151a9b3a6ba830d2a7f4fe8cc6a68385a` | 2,195,973 | 93/93 | `1Jxy4AaqY2VUqTItza4-qtF3du3XhU1D8` | `id:BSpOijBcT10AAAAAAD_Qvw` |
| 3 | `f993bf7121af7bb6d69698244089201e28868ebc` | 1,811,170 | 68/68 | `1Y2d3SkoaJr4nfB9zHzX9yoMzymlhD2XU` | `id:BSpOijBcT10AAAAAAD_QxA` |

## Archive identity

### Stage 1

- Name: `BASS_S7_PREREG_COUPLED_NATIVE_20261019_2865f60b.zip`
- SHA256: `7398aa6268e4d345419652c2f41efe67305b1d049f3d12f1cc7308b699084672`
- Dropbox content hash: `a1fc1e0b6d8af26d221d236d131c1e4a0998b6feb6b2d9c6a46d5bff2c1bfa74`
- Receipt: [S7_STAGE1_CLOUD_READBACK.json](delivery/s7/S7_STAGE1_CLOUD_READBACK.json)

### Stage 2

- Name: `BASS_S7_EXECUTION_R2_VALIDATOR_20261019_c689dcf1.zip`
- SHA256: `0a9ec0a199e1a0a96aebf534e95b5812f84bb7d39067eda38ece02c5feabe050`
- Dropbox content hash: `d8855b16dc4b20b598a77148937996fee68e5f36cf8b0cef85766b7705c43897`
- Receipt: [S7_STAGE2_CLOUD_READBACK.json](delivery/s7/S7_STAGE2_CLOUD_READBACK.json)

### Stage 3

- Name: `BASS_S7_EXACT_RESULTS_R3_PREREG_20261019_f993bf71.zip`
- SHA256: `a2e230c60ca5bb9bb04df9abe23b875cab69f769c98cf192728ff82f665fd6e1`
- Dropbox content hash: `6cf0070bf7312e6a776735543329331358887561430afa210e977c77ea7a4bfa`
- Receipt: [S7_STAGE3_CLOUD_READBACK.json](delivery/s7/S7_STAGE3_CLOUD_READBACK.json)

## 최종 metadata supplement

최종 Stage4는 실제 R3 결과, 종합보고서, DAG/RETURN/인계와 Stage3 cloudreceipt를 담는 **incremental supplement**다. 앞의 세 S7 archive와 고정 Git commit을 함께 참조한다. 최종 source는 f993bf7121af7bb6d69698244089201e28868ebc이고 scientific source는 마지막 metadata 작성에서 변경하지 않았다.

최종 metadata commit을 publish하고 ref/tree를 독립 검증한 후 한 archive를 만든다. 그 ZIP의 `GIT_READBACK.json`과 `MANIFEST.json`이 정확한 commit/파일 identity를 담는다. 업로드 뒤 마지막 cloudreadback은 자기 archive 내부에 자기 hash를 쓰는 순환 없이 **PR174 최종 S7 closeout comment**에 기록한다. 최신 finalproof가 이 문서의 containingcommit과 일치하는지 확인한다.

[PR174](https://github.com/cosmosapjw-quantum/bass/pull/174), [DAG](DAG.json), [PUBLICATION_CLOSEOUT](PUBLICATION_CLOSEOUT.json)을 함께 확인한다. Backup identity 검증은 물리적 정확도나 production승인이 아니다.

## 이전 S2/S3/S5 복구 이력

아래 기록은 S7 이전 archive에 대한 역사적 readback이다. 현재 S7의 raw/providerhash 범위와 혼동하지 않는다.

# 실제 클라우드 readback과 복구 완료 범위

2026-10-19 08:07 UTC / 17:07 KST. 사용자 승인 후 cloud Browser로 네 원본 ZIP의 Google Drive 저장을 복구했다.
업로드 UI와 별도 connector readback을 구분했으며, 다음은 실제 원격 바이트에서 확인한 결과다.

| 단계 | 원본 ZIP | bytes | Drive 객체 ID | manifest 항목 |
|---|---|---:|---|---:|
| S2_RUST | `BASS_S2_RUST_EXECUTED_20261019_87149cdb.zip` | 34578 | `1TfPwVyfgsGJ1wqjtWLq9aze28cSxOMsi` | 24/24 |
| S3_RESPONSE | `BASS_S3_P24_RESPONSE_20261019_a7938ad5.zip` | 554697 | `1qRR2sQbKewphYdlFI5068ajO8FdYwaZ9` | 79/79 |
| S5_NATIVE | `BASS_NATIVE_ADAPTER_20261019_b30a2044.zip` | 853265 | `1crznW0ckVSumZCf34W75mx3g5ws6dYiJ` | 114/114 |
| PREVIOUS_FINAL_METADATA | `BASS_PR174_S3_NATIVE_CLOSEOUT_20261019_b69c7791.zip` | 95901 | `1-Pjuh0hq8gGA2bxJRZoXhXSVuCzTwhs1` | 35/35 |

## 원격 검증 방법

Google Drive: 업로드 후 독립된 connector로 완전한 raw ZIP bytes를 다시 읽었다. 원본과 전체 bytes가 같고,
SHA256·크기·ZIP CRC 및 원격 root manifest의 모든 payload SHA256가 일치했다. 네 archive의 manifest 항목
합계252개에는 단계 사이 중복 보관된 파일도 포함된다. Rust·바이너리·중첩 ZIP도 확인했으며 추출 텍스트에 의존하지 않는다.
네 파일은 모두 지정 폴더에 각각 하나씩 존재한다. 각 payload 결과는 delivery/drive_recovery/에 보존했다.

Dropbox: 네 원본의 실제 remote metadata 크기/provider content hash가 원 ZIP bytes로 계산한 Dropbox block hash와
일치했고 원격 root manifest 및 제공되는 추출 텍스트도 비교했다. Dropbox의 raw ZIP을 독립 다운로드한 결과는 아니다.
이 검증 범위와 이전 Rust 빈 추출·중첩 binary 미제공·owner JSON 추출 encoding artifact는 그대로 보존한다.

| 단계 | 원본 ZIP SHA256 | Dropbox 객체 ID |
|---|---|---|
| S2_RUST | `c624a140000066cb278b0f1dbd946932f8f2069ce48f752c1710ced1879b28ef` | `id:BSpOijBcT10AAAAAAD_Ppg` |
| S3_RESPONSE | `7d040f80cc4edee2a32c490938f59c2526c934f543ae64c4acd548bf1b8958d3` | `id:BSpOijBcT10AAAAAAD_PrA` |
| S5_NATIVE | `f262e35974fb8b741fb7a37fd14bc17054a8966f992ecf778368e28f9706dc98` | `id:BSpOijBcT10AAAAAAD_PrQ` |
| PREVIOUS_FINAL_METADATA | `45731aff760569ca4340a4ab2dde36620ef7d6757932cacb6c733b97c121284d` | `id:BSpOijBcT10AAAAAAD_Prg` |

## 이전 실패의 처리

Raw ZIP connector upload, Docs 두 크기 쓰기, Sheets 소량 쓰기는 당시 ack 없이 정지했다.
실패 상세는 delivery/DRIVE_FINAL_READBACK.json, 이전 마감은 b69c7791b71064fd4b82fd7b2b3706860d84a29e에
보존한다. 새 복구는 그 실패를 소급해서 성공으로 변경하지 않는다. connector 쓰기 경로 자체를 수리했다고 주장하지 않는다.
승인된 cloud Browser의 기존 로그인 세션과 문서화된 file chooser를 이용했다. 새 공유 권한을 부여하지 않았다.
빈 Doc/Sheet 또는 그 파일 이름을 백업으로 세지 않았고, Base64 문서 carrier는 사용하지 않았다.

## 게시·과학 범위

검증된 native source는 `b30a2044be1ae04a68d8319f47d15a5bed751668`이며 원 owner는
`cosmosapjw-quantum/rei_bianchi@0e25846433170d0f420c4cda44a0bedbf02cd177`로 고정돼 있다.
S2/S3/native 과학 코드와 측정은 다시 실행하지 않았다. 기존 tracked Python/Rust32개는 검증된 source와 같다.
S7 및 R10/C10은 위 네 archive의 이중 백업 범위에서 완료다. 현재 metadata의 exact commit/tree와 새 복구 보충본은
그 commit을 만든 뒤 한 번 패키징하고 두 provider에서 readback한 후 PR174 최신 댓글에 기록한다.
파일이 자기 commit/ZIP hash를 포함하게 만드는 무한 게시 순환은 만들지 않는다.
S6(유한-d continuum angular error, exact rank1 실행 certificate, spectral refinement, source-age/coupled feedback)는
pending이다. P2/P4 일치를 전체 continuum/native spectral 보존 또는 production/full EoR/merge 승인으로 확대하지 않는다.
