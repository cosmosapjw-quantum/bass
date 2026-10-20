# BASS PR174 cloud intake — 2026-10-20

## 판정

사용자 재개문 이후 S6, S7, S8 실행 결과와 S9의 고정 source/사전등록 백업이 양쪽 저장처에 존재한다. 최신 게시 source는 `4b30957cb008aad8019bb1a673937fc67bd017e8`, tree는 `8e4abf3820d06bae6cbec307e4f69de74195d14b`이다. S9의 실제 8개 history는 최신 source 내 반환 기록에서 `NOT_RUN`이다. S6부터 같은 캠페인을 다시 실행하지 않고 이 근거를 재사용한다.

## 현재 readback

Drive는 각 ZIP 전체 bytes를 현재 connector raw 응답으로 받아 로컬 복원한 뒤 SHA256, CRC, 파일별 size/SHA256/Git blob을 확인했다. Dropbox는 같은 네 객체의 provider whole-object content hash가 Drive에서 확보한 원 bytes로 계산한 Dropbox hash와 일치했다. 최신 S9 ZIP의 원격 추출 manifest도 140개 항목 전체가 Drive manifest와 같았다. Dropbox 원 ZIP bytes의 로컬 다운로드는 수행하지 않았으며 해당 검증 강도를 구별한다.

| 백업 | ZIP bytes | SHA256 | manifest 항목 | Git blob 검사 |
|---|---:|---|---:|---:|
| S6 | 927047 | `93ae03207b9c1fcccba56b4ec6cd22408f9f03fb7a86e5dec72fe62793915ea1` | 86 | 86 |
| S7 final | 197742 | `840cec2663ae048ae2cd8d6c6830cc75a2ffaf4affeaf30a08e46227e006dca0` | 22 | 21 |
| S8 final | 916060 | `cf4cc9b03b243afb6f055469e57193def5db01fc2610b14c537bd8968ffc3efc` | 43 | 42 |
| S9 prereg | 604752 | `adaa646269168365738bb6c6e7ec67538da0b6109b5d9cb8cac5e4a886a2d9c1` | 140 | 139 |

모든 위 검사는 mismatch 0. 마지막 세 ZIP은 `GIT_READBACK.json` 한 항목이 Git payload 밖에 있어 manifest 수와 Git blob 수가 1씩 다르다.

Drive 직접 하위목록 48개, Dropbox 직접 하위목록 33개(`has_more=false`)를 확인했다. 양쪽 최신 객체는 `BASS_S9_PREREG_VIGILODE_RUST_20261019_4b30957c.zip`; 이보다 나중의 S9 실제 실행 archive는 이 scope에서 발견되지 않았다. Drive 목록 인터페이스에는 pagination 상태가 노출되지 않았고 top_k=1000으로 요청해 48개가 반환됐다.

## 보존할 과학 상태

S6 finite-d certificate는 제한 통과, 원 G5 refinement gate 38/344 실패와 held-out 통과를 구분한다. P4 제약 44/238 악화도 보존한다. Exact rank1은 Python 인증 경로에 한정된다. Spectral 잔차는 Simpson-32 기준 절단 오차와 1 ulp 변동으로 설명됐으며 source deposition 범위다. S7 coupled/native와 S8 tangent/native refinement 실제 결과는 새 archive에서 확보됐다. S9는 source·callback·개발 검증까지만 완료이며 실제 history는 아직 실행하지 않았다.

## 파일

`CURRENT_CLOUD_INTAKE.json`이 intake의 집계 기록이다. `manifest_verification.json`, `cloud_readback_validation.json`, `*_download_receipt.json`은 현재 검산 영수증이다. `drive_s6/`, `drive_s7_final/`, `drive_s8_final/`, `drive_s9_prereg/`는 각각 독립적인 immutable archive의 추출 디렉터리이며 서로 덮어쓰지 않았다. 외부 mutation은 하지 않았다.
