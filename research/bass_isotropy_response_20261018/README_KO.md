# BASS 등방 source 보정: 중단 복구와 게시 체크포인트

이 패키지는 2026-10-18 사용자 요청에 따라 새 연구를 멈추고 S1/S2를 보존·게시하기 위한 것이다. 원본 코드의 과학적 동작이나 허용오차는 바꾸지 않았다. 연구 경로는 `research/bass_isotropy_response_20261018/`이며, 기준은 BASS PR173 `4e2d1fa820d6f7baae1069b615fb82a08d53403b`다.

## 새로 확인된 이전 실행

Google Drive BASS_BACKUPS에 새로 올라온 PR173 복구본을 먼저 읽었다. 전체 archive SHA256은 `3a4f24fc529f71b3fff4c6df39be47943cee5d76ac5679f7c29b9a78fbc59885`이며 실제 원본 native SourceLedger 58행과 negative input 5개의 exit3를 포함한다. 실행 host는 사용자 Ubuntu `cosmosapjw`(24 logical CPUs)였다. 이 결과는 이론·Python 예측만 있던 이전 PR172의 native NOT_RUN을 대체하지만, 새 등방성 보정 코드가 실행됐다는 의미가 아니다. Native 원시 결과와 영수증을 복구 ZIP의 `native_pr173_evidence/`에 정확한 bytes로 보존했다. Git에서는 부모 PR173의 `research/bass_sourceledger_20261018/evidence_native_20261018/`를 재사용한다. 193MB 전체 legacy archive를 다시 public Git에 넣지는 않았다.

## 이번에 보존한 코드

- `angular_balance.py`: reflection-even 양의 source prior의 KL 최소변경으로 sum(alpha)=1, sum(alpha P2)=0을 맞추는 P2-only 연구 함수.
- `balance.rs`: 동일 목표의 std-only standalone Rust 후보. 5개 테스트를 작성했지만 이 복구에서 컴파일·실행하지 않았다.
- `test_balance.py`, `test_properties.py`: 복구된 원본 소스에 대해 15/15 재실행 PASS. 그중 고차 moment가 남는다는 부정 제어도 있다.
- `THEORY_KO.md`: 과거 해석과 당시 상태 그대로다. 과거의 native 미확인 문장은 PR173 측정으로 상태가 갱신된다. 원문을 지우지 않았다. 원본 S1/S2 아카이브와 역사적 실패 로그는 최종 복구 ZIP에 함께 있다.

`python -m pip install -r requirements.txt` 후 `python -m unittest -v test_balance test_properties`로 재실행한다. Git-only checkout에 별도 ZIP, /mnt/data 또는 비공개 reference 파일이 필요 없다. NCP는 이 15개 Python 테스트를 위해 필요하지 않다.

## 정확한 경계

보정 대상은 새로 방출되는 등방 source의 각도 구적뿐이다. 이미 자유수송한 광자 stock 또는 물리적으로 비등방인 source에 이를 적용해서는 안 된다. P2=0은 모든 고차 moment가 0이거나, 이후 전단 응답·스펙트럼·native finite-bin deposition이 정확하다는 증거가 아니다. PR173은 원래 `inject`의 결과이며 보정된 새 연산자의 승인은 아니다.

중단 직전의 다음 아이디어는 즉시 P4를 보정하는 것이 아니라, exact photon kernel의 미분을 Legendre 다항식으로 분해해 P2-only 보정 후 응답 오차가 남는지 검산하는 것이었다. 이 후속 S3의 기호 검산·캠페인·P4 구현은 아직 실행하지 않았다. 여기서 제공하는 것은 완성된 S2 체크포인트다.

## 인계와 보존

`CODEX_HANDOFF_KO.md`는 기존 Rust 후보의 작은 compile/test만 요청한다. `NEW_THREAD_HANDOFF_KO.md`는 다음 ChatGPT 대화에서 BASS LRS 연구를 이어가기 위한 지시다. 두 문서는 source-only PR173 완료와 새 보정 native NOT_RUN을 구별한다. 기존 REI production 코드와 checkpoint를 수정하거나 PR을 자동 병합하지 않는다.

복구 ZIP `BASS_ISOTROPY_RECOVERY_20261018T1407Z.zip`는 77758 bytes, SHA256 `8d71c52d7709b6d1867c14fe21af0a6a592eaf86c3099c2d2151c4aecb22c92e`이다. Dropbox와 Google Drive에서 각각 실제 다운로드하여 ZIP 및 28개 manifest payload의 동일성을 확인했다. ZIP은 연구 하위트리와 기존 stage/native 증거이며 전체 Git clone이 아니다. 최종 Git identity와 게시 정보는 별도 publication receipt로 보존한다.
