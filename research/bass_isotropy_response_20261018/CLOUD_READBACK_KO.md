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
